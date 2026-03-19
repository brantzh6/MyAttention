from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String as SqlString, cast, or_, select
from sqlalchemy.orm import joinedload

from config import get_settings
from db.models import FeedItem as FeedItemModel
from db.models import Source as SourceModel
from feeds.fetcher import PROXY_DOMAINS, get_feed_fetcher, FeedSource as _FeedSource, FeedEntry, reload_feed_fetcher, map_category, reload_feed_fetcher
from feeds.authority import get_authority_classifier
from feeds.persistence import (
    build_import_feed_extra,
    build_import_source_url,
    persist_import_feed_item,
    resolve_source_for_import,
)
from feeds.proxy_config import load_proxy_settings, normalize_proxy_mode, should_use_proxy
from feeds.raw_ingest import persist_import_item_raw
from db import get_db, AsyncSession

router = APIRouter()


# ── Response models ──────────────────────────────────

class SourceType(str, Enum):
    RSS = "rss"
    WEB = "web"
    API = "api"


class SourceStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class ProxyMode(str, Enum):
    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"


class Source(BaseModel):
    id: str
    name: str
    type: SourceType
    url: str
    category: str
    tags: List[str] = []
    enabled: bool = True
    status: SourceStatus = SourceStatus.OK
    last_fetched: Optional[datetime] = None
    success_rate: float = 100.0
    proxy_mode: ProxyMode = ProxyMode.AUTO
    proxy_effective: bool = False
    proxy_reason: str = "direct"


class SourceCreate(BaseModel):
    name: str
    type: SourceType = SourceType.RSS
    url: str
    category: str
    tags: List[str] = []
    enabled: bool = True
    proxy_mode: ProxyMode = ProxyMode.AUTO


class SourceProxyUpdate(BaseModel):
    proxy_mode: ProxyMode


class FeedItem(BaseModel):
    id: str
    title: str
    summary: str
    source: str
    source_id: str
    source_type: SourceType
    url: str
    published_at: datetime
    category: str
    importance: float
    is_read: bool = False
    is_favorite: bool = False


class FeedsReadBackend(str, Enum):
    CACHE = "cache"
    DB = "db"
    HYBRID = "hybrid"


# ── Import models ────────────────────────────────────

class ImportItem(BaseModel):
    """Single item from info-processor output."""
    id: str
    title: str
    link: str = ""
    summary: str = ""
    content: str = ""
    source: str = ""
    source_name: str = ""
    source_type: str = "rss"
    category: str = ""
    category_name: str = ""
    secondary_tags: List[str] = []
    urgency: float = 0.5
    urgency_factors: Dict[str, Any] = {}
    language: str = "zh"
    published_at: Optional[str] = None
    processed_at: Optional[str] = None
    metadata: Dict[str, Any] = {}


class FeedsImportRequest(BaseModel):
    """Batch import request from info-processor."""
    items: List[ImportItem]
    stats: Dict[str, Any] = {}


class FeedsImportResponse(BaseModel):
    """Import result summary."""
    status: str
    imported: int = 0
    persisted: int = 0
    duplicates: int = 0
    errors: int = 0
    items: List[str] = Field(default_factory=list, description="IDs of imported items")


# ── Endpoints ────────────────────────────────────────

def _source_to_api_model(source: _FeedSource) -> Source:
    proxy_settings = load_proxy_settings()
    proxy_mode = normalize_proxy_mode(getattr(source, "proxy_mode", None), getattr(source, "use_proxy", False))
    proxy_effective, proxy_reason = should_use_proxy(
        source.url,
        proxy_mode,
        proxy_settings,
        PROXY_DOMAINS,
    )
    return Source(
        id=source.id,
        name=source.name,
        type=SourceType.RSS,
        url=source.url,
        category=source.category,
        tags=source.tags,
        enabled=source.enabled,
        proxy_mode=ProxyMode(proxy_mode),
        proxy_effective=proxy_effective,
        proxy_reason=proxy_reason,
    )


def _feed_source_public_id(source: SourceModel, extra: dict[str, Any]) -> str:
    source_key = extra.get("source_key")
    if source_key:
        return str(source_key)
    config = source.config or {}
    configured_key = config.get("source_key")
    if configured_key:
        return str(configured_key)
    return str(source.id)


def _db_feed_to_api_model(item: FeedItemModel) -> FeedItem:
    source = item.source
    extra = item.extra or {}
    source_type = source.type.value if hasattr(source.type, "value") else str(source.type or "rss")
    category = source.category or extra.get("category_name") or extra.get("raw_category") or ""
    return FeedItem(
        id=item.external_id or str(item.id),
        title=item.title,
        summary=item.summary or "",
        source=source.name if source else (extra.get("source_name") or ""),
        source_id=_feed_source_public_id(source, extra) if source else str(item.source_id),
        source_type=SourceType(source_type),
        url=item.url or "",
        published_at=item.published_at or item.fetched_at,
        category=category,
        importance=item.importance or 0.5,
        is_read=False,
        is_favorite=False,
    )


async def _get_db_feeds(
    db: AsyncSession,
    *,
    source_id: Optional[str],
    category: Optional[str],
    limit: int,
) -> list[FeedItem]:
    stmt = (
        select(FeedItemModel)
        .options(joinedload(FeedItemModel.source))
        .join(FeedItemModel.source)
    )

    if source_id:
        stmt = stmt.where(
            or_(
                cast(SourceModel.id, SqlString) == source_id,
                SourceModel.config.op("->>")("source_key") == source_id,
                SourceModel.url == build_import_source_url(source_id),
            )
        )

    if category:
        stmt = stmt.where(SourceModel.category == category)

    stmt = stmt.order_by(
        FeedItemModel.published_at.desc().nullslast(),
        FeedItemModel.fetched_at.desc(),
        FeedItemModel.created_at.desc(),
    ).limit(limit)

    result = await db.execute(stmt)
    return [_db_feed_to_api_model(item) for item in result.scalars().all()]


async def _get_cache_feeds(
    *,
    source_id: Optional[str],
    category: Optional[str],
    limit: int,
) -> list[FeedItem]:
    fetcher = get_feed_fetcher()

    if source_id:
        entries = await fetcher.fetch_by_source(source_id)
    else:
        entries = await fetcher.fetch_all()

    if category:
        entries = [e for e in entries if map_category(e.category) == category or _match_category(e.category, category)]

    entries = entries[:limit]
    return [
        FeedItem(
            id=e.id,
            title=e.title,
            summary=e.summary,
            source=e.source_name,
            source_id=e.source_id,
            source_type=SourceType.RSS,
            url=e.url,
            published_at=e.published_at,
            category=e.category,
            importance=e.importance,
            is_read=e.is_read,
            is_favorite=e.is_favorite,
        )
        for e in entries
    ]


def _merge_feed_results(db_items: list[FeedItem], cache_items: list[FeedItem], limit: int) -> list[FeedItem]:
    merged: list[FeedItem] = []
    seen: set[str] = set()

    for item in db_items + cache_items:
        dedupe_key = item.url or item.id
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        merged.append(item)

    merged.sort(key=lambda item: item.published_at, reverse=True)
    return merged[:limit]


@router.get("/feeds", response_model=List[FeedItem])
async def get_feeds(
    source_id: Optional[str] = Query(None, description="?????"),
    category: Optional[str] = Query(None, description="?????"),
    limit: int = Query(200, ge=1, le=500),
    backend: Optional[FeedsReadBackend] = Query(None, description="?????cache/db/hybrid"),
    db: AsyncSession = Depends(get_db),
):
    """???????? cache / db / hybrid ???"""
    settings = get_settings()
    configured_backend = getattr(settings, "feeds_read_backend", "hybrid")
    active_backend = (backend.value if backend else configured_backend or "hybrid").strip().lower()

    if active_backend == FeedsReadBackend.CACHE.value:
        return await _get_cache_feeds(source_id=source_id, category=category, limit=limit)

    db_items = await _get_db_feeds(db, source_id=source_id, category=category, limit=limit)
    if active_backend == FeedsReadBackend.DB.value:
        return db_items

    cache_items = await _get_cache_feeds(source_id=source_id, category=category, limit=limit)
    return _merge_feed_results(db_items, cache_items, limit)


@router.get("/feeds/health")
async def get_feed_collection_health(db: AsyncSession = Depends(get_db)):
    """Return durable collection health for the feed pipeline."""
    from feeds.collection_health import collect_collection_health_snapshot

    return await collect_collection_health_snapshot(db)


@router.post("/feeds/refresh")
async def refresh_feeds():
    """强制刷新所有信息源（清除缓存）"""
    fetcher = get_feed_fetcher()
    fetcher._cache.clear()
    entries = await fetcher.fetch_all()
    return {"status": "ok", "count": len(entries)}


@router.get("/sources", response_model=List[Source])
async def get_sources():
    """获取所有信息源配置"""
    fetcher = get_feed_fetcher()
    sources = fetcher.get_sources()
    return [_source_to_api_model(s) for s in sources]


@router.post("/sources", response_model=Source)
async def create_source(body: SourceCreate):
    """添加新信息源"""
    fetcher = get_feed_fetcher()
    source_id = body.name.lower().replace(" ", "_")
    new = _FeedSource(
        id=source_id,
        name=body.name,
        url=body.url,
        category=body.category,
        tags=body.tags,
        enabled=body.enabled,
        proxy_mode=body.proxy_mode.value,
        use_proxy=body.proxy_mode == ProxyMode.ALWAYS,
    )
    fetcher.add_source(new)
    return _source_to_api_model(new)


@router.delete("/sources/{source_id}")
async def delete_source(source_id: str):
    """删除信息源"""
    fetcher = get_feed_fetcher()
    removed = fetcher.remove_source(source_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"status": "deleted"}


@router.post("/sources/{source_id}/toggle")
async def toggle_source(source_id: str):
    """切换信息源启用/禁用"""
    fetcher = get_feed_fetcher()
    new_state = fetcher.toggle_source(source_id)
    if new_state is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"source_id": source_id, "enabled": new_state}


@router.put("/sources/{source_id}/proxy", response_model=Source)
async def update_source_proxy(source_id: str, body: SourceProxyUpdate):
    fetcher = get_feed_fetcher()
    source = fetcher.update_source_proxy_mode(source_id, body.proxy_mode.value)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return _source_to_api_model(source)


@router.post("/sources/{source_id}/refresh")
async def refresh_source(source_id: str):
    """手动刷新指定信息源"""
    fetcher = get_feed_fetcher()
    # 清除该源缓存
    fetcher._cache.pop(source_id, None)
    entries = await fetcher.fetch_by_source(source_id)
    return {"status": "ok", "source_id": source_id, "count": len(entries)}


@router.post("/sources/reload")
async def reload_sources():
    """重新加载所有信息源配置"""
    fetcher = reload_feed_fetcher()
    return {
        "status": "ok",
        "message": "Sources reloaded",
        "count": len(fetcher.sources)
    }


# ── Import endpoint ──────────────────────────────────

def _parse_import_datetime(dt_str: Optional[str]) -> datetime:
    """Parse ISO datetime string, fallback to now."""
    if not dt_str:
        return datetime.now(timezone.utc)
    try:
        # Handle various ISO formats
        dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


# Category mapping from info-processor to MyAttention categories
_CATEGORY_MAP = {
    "TECH": "科技",
    "WORLD": "国际",
    "CHINA": "国内",
    "FINANCE_CN": "财经",
    "FINANCE_INTL": "海外财经",
    "SOCIAL": "社交",
}

# Also map lowercase variants from gatherer
_CATEGORY_MAP.update({k.lower(): v for k, v in _CATEGORY_MAP.items()})
_CATEGORY_MAP.update({
    "tech": "科技",
    "world": "国际",
    "china": "国内",
    "finance_cn": "财经",
    "finance_intl": "海外财经",
    "social": "社交",
})

# Reverse mapping for filtering (Chinese -> English keys)
_CATEGORY_REVERSE_MAP = {v: k for k, v in _CATEGORY_MAP.items()}


def _match_category(entry_category: str, filter_category: str) -> bool:
    """Check if entry's category matches the filter using mapping."""
    if not filter_category:
        return True

    # Import mapping from fetcher
    from feeds.fetcher import CATEGORY_MAPPING

    # Get standard category for entry
    entry_standard = CATEGORY_MAPPING.get(entry_category, entry_category)

    # Direct match with standard category
    return entry_standard == filter_category


@router.post("/feeds/import", response_model=FeedsImportResponse)
async def import_feeds(body: FeedsImportRequest, db: AsyncSession = Depends(get_db)):
    """
    批量导入 info-processor 处理后的信息项。
    
    Phase 1 先做双落点：
    1. 原始导入内容进入对象存储 + raw_ingest 元数据
    2. 继续注入 FeedFetcher 内存缓存，保持现有 /api/feeds 可用
    """
    fetcher = get_feed_fetcher()
    
    imported_ids = []
    persisted_count = 0
    duplicates = 0
    errors = 0
    
    # Collect existing IDs for dedup
    existing_ids = set()
    for _, (_, entries) in fetcher._cache.items():
        for e in entries:
            existing_ids.add(e.id)
    
    # Group imported items by source
    by_source: Dict[str, list] = {}
    
    for item in body.items:
        try:
            payload = item.model_dump() if hasattr(item, "model_dump") else item.dict()
            source_key = item.source or "_imported"
            registered_source = next((src for src in fetcher.get_sources() if src.id == source_key), None)
            resolved_source_name = item.source_name or (registered_source.name if registered_source else source_key)
            resolved_source_url = registered_source.url if registered_source else ""
            resolved_category = _CATEGORY_MAP.get(
                item.category,
                item.category_name or (registered_source.category if registered_source else item.category),
            )
            resolved_tags = item.secondary_tags or (registered_source.tags if registered_source else [])
            fetched_at = _parse_import_datetime(item.processed_at or item.published_at)

            raw_result = await persist_import_item_raw(
                db,
                source_key=source_key,
                external_id=item.id,
                payload=payload,
                fetched_at=fetched_at,
            )

            try:
                async with db.begin_nested():
                    source = await resolve_source_for_import(
                        db,
                        source_key=source_key,
                        source_name=resolved_source_name,
                        source_type=item.source_type,
                        source_url=resolved_source_url,
                        category=resolved_category,
                        tags=resolved_tags,
                    )

                    persisted = await persist_import_feed_item(
                        db,
                        source=source,
                        external_id=item.id,
                        title=item.title,
                        summary=item.summary,
                        content=item.content or item.summary,
                        url=item.link,
                        importance=item.urgency,
                        published_at=_parse_import_datetime(item.published_at),
                        fetched_at=fetched_at,
                        extra=build_import_feed_extra(
                            raw_ingest_id=str(raw_result.record.id) if raw_result.record.id else None,
                            source_key=source_key,
                            source_name=resolved_source_name,
                            source_type=item.source_type,
                            category=item.category,
                            category_name=item.category_name,
                            metadata=item.metadata,
                            urgency_factors=item.urgency_factors,
                            secondary_tags=item.secondary_tags,
                            language=item.language,
                        ),
                    )
            except Exception as exc:
                raw_result.record.parse_status = "error"
                raw_result.record.error_message = str(exc)[:1000]
                response_meta = dict(raw_result.record.response_meta or {})
                response_meta.update(
                    {
                        "persist_error": str(exc)[:500],
                        "source_key": source_key,
                    }
                )
                raw_result.record.response_meta = response_meta
                await db.flush()
                errors += 1
                continue

            raw_result.record.parse_status = "persisted" if persisted.created else "duplicate"
            response_meta = dict(raw_result.record.response_meta or {})
            response_meta.update(
                {
                    "source_id": str(source.id) if source.id else None,
                    "feed_item_id": str(persisted.record.id) if persisted.record.id else None,
                    "feed_item_created": persisted.created,
                }
            )
            raw_result.record.response_meta = response_meta
            raw_result.record.error_message = None
            await db.flush()

            if item.id in existing_ids or not persisted.created:
                duplicates += 1
                continue
            persisted_count += 1

            category = _CATEGORY_MAP.get(item.category, item.category_name or item.category)
            entry = FeedEntry(
                id=item.id,
                title=item.title,
                summary=item.summary[:200] + "..." if len(item.summary) > 200 else item.summary,
                source_name=resolved_source_name,
                source_id=source_key,
                url=item.link,
                published_at=_parse_import_datetime(item.published_at),
                category=category,
                importance=item.urgency,
            )

            if source_key not in by_source:
                by_source[source_key] = []
            by_source[source_key].append(entry)

            imported_ids.append(item.id)
            existing_ids.add(item.id)

        except Exception:
            errors += 1
    
    # Inject into FeedFetcher cache
    import time as _time
    for source_key, entries in by_source.items():
        cached = fetcher._cache.get(source_key)
        if cached:
            # Merge with existing cache entries
            existing_entries = list(cached[1])
            existing_entries.extend(entries)
            # Sort by published time and dedup
            existing_entries.sort(key=lambda e: e.published_at, reverse=True)
            fetcher._cache[source_key] = (_time.time(), existing_entries)
        else:
            entries.sort(key=lambda e: e.published_at, reverse=True)
            fetcher._cache[source_key] = (_time.time(), entries)
    
    return FeedsImportResponse(
        status="ok" if imported_ids else "empty",
        imported=len(imported_ids),
        persisted=persisted_count,
        duplicates=duplicates,
        errors=errors,
        items=imported_ids[:50],  # Limit returned IDs
    )


# ── 一键转知识库 ───────────────────────────────────────

class ToKnowledgeBaseRequest(BaseModel):
    """转入知识库请求"""
    kb_id: str = Field(..., description="目标知识库ID")
    notes: Optional[str] = Field(None, description="可选备注")
    extract_deep: bool = Field(False, description="是否进行深度提取(L3)")


class ToKnowledgeBaseResponse(BaseModel):
    """转入知识库响应"""
    success: bool
    knowledge_link_id: Optional[str] = None
    document_id: Optional[str] = None
    message: str


@router.post("/feeds/{item_id}/to-knowledge-base", response_model=ToKnowledgeBaseResponse)
async def feed_to_knowledge_base(
    item_id: str,
    body: ToKnowledgeBaseRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    将信息流条目转入指定知识库

    实现信息闭环：信息 -> 知识
    """
    from knowledge import get_kb_manager, Document as KbDocument
    from knowledge import Document as KbDocument

    try:
        # 1. 尝试从内存缓存中获取 FeedEntry
        fetcher = get_feed_fetcher()
        feed_entry = None
        source_name = "未知来源"

        # 搜索所有缓存的 feed 条目
        for source_key, (_, entries) in fetcher._cache.items():
            for entry in entries:
                if entry.id == item_id:
                    feed_entry = entry
                    source_name = entry.source_name
                    break
            if feed_entry:
                break

        content = ""
        title = ""
        url = ""
        category = ""
        importance = 0.5

        if feed_entry:
            # 使用内存条目
            content = feed_entry.summary or ""
            title = feed_entry.title
            url = feed_entry.url
            category = feed_entry.category
            importance = feed_entry.importance
        else:
            # 尝试从数据库获取
            from db.models import FeedItem
            from sqlalchemy import select
            result = await db.execute(
                select(FeedItem).where(FeedItem.id == item_id)
            )
            db_item = result.scalar_one_or_none()

            if not db_item:
                return ToKnowledgeBaseResponse(
                    success=False,
                    message="信息条目不存在"
                )

            # 使用数据库条目
            content = db_item.content or db_item.summary or ""
            title = db_item.title
            url = db_item.url or ""
            category = db_item.category or ""
            importance = db_item.importance or 0.5
            source_name = "未知来源"

        # 2. 获取内容（如果需要深度提取）
        if body.extract_deep and content:
            from feeds.depth_fetcher import get_depth_fetcher
            depth_fetcher = get_depth_fetcher()
            try:
                depth_content = await depth_fetcher.fetch_depth_3(
                    content=content,
                    title=title,
                    category=category,
                    llm_client=None
                )
                if depth_content.extracted_data and "error" not in depth_content.extracted_data:
                    content = f"{content}\n\n## 深度分析\n"
                    for key, value in depth_content.extracted_data.items():
                        if key != "置信度":
                            content += f"- {key}: {value}\n"
            except Exception as e:
                pass  # 深度提取失败不影响主流程

        # 3. 调用知识库管理器添加文档
        kb_manager = get_kb_manager()

        # 确保知识库存在
        kb = await kb_manager.get_knowledge_base(body.kb_id)
        if not kb:
            # 创建知识库
            kb = await kb_manager.create_knowledge_base(
                name=f"KB {body.kb_id[:8]}",
                description="从信息流转入"
            )

        # 创建文档并添加到知识库
        kb_doc = KbDocument(
            id=item_id,
            content=content,
            title=title,
            source=url,
            url=url,
            source_type="feed",
            kb_id=body.kb_id,
            metadata={
                "feed_item_id": item_id,
                "source": source_name,
                "category": category,
                "importance": importance,
                "imported_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        try:
            chunk_ids = await kb_manager.add_document(kb_doc, body.kb_id)
            document_id = item_id
        except Exception as e:
            return ToKnowledgeBaseResponse(
                success=False,
                message=f"添加到知识库失败: {str(e)}"
            )

        # 4. 创建关联记录（如果数据库连接可用）
        try:
            from db.models import KnowledgeLink
            from sqlalchemy import select

            # 检查数据库中是否有对应的 feed_item (通过 external_id 或其他方式)
            # 这里我们跳过数据库记录，因为 feed items 主要在内存中
            link_id = None
        except Exception:
            link_id = None  # 数据库记录失败不影响主流程

        return ToKnowledgeBaseResponse(
            success=True,
            knowledge_link_id=link_id,
            document_id=document_id,
            message="已成功转入知识库"
        )

    except Exception as e:
        return ToKnowledgeBaseResponse(
            success=False,
            message=f"转入知识库失败: {str(e)}"
        )


@router.get("/feeds/{item_id}/knowledge-links", response_model=List[Dict])
async def get_feed_knowledge_links(item_id: str, db: AsyncSession = Depends(get_db)):
    """获取信息条目关联的知识库列表"""
    from db.models import KnowledgeLink
    from sqlalchemy import select

    result = await db.execute(
        select(KnowledgeLink).where(KnowledgeLink.feed_item_id == item_id)
    )
    links = result.scalars().all()

    return [
        {
            "id": str(link.id),
            "kb_id": link.knowledge_base_id,
            "status": link.status,
            "linked_at": link.linked_at.isoformat() if link.linked_at else None,
            "notes": link.notes
        }
        for link in links
    ]

"""
知识图谱模块 (Knowledge Graph)

核心功能：
1. 实体提取 - 从文本中自动提取实体（人物、组织、概念、技术）
2. 关系抽取 - 建立实体之间的关联关系
3. 知识推理 - 基于已有知识推断新关系
4. 分类体系 - 层次化的知识分类
"""

import logging
import json
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    KnowledgeEntity, KnowledgeRelation, KnowledgeCategory, KnowledgeMetrics,
    KnowledgeLink, FeedItem
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ExtractedEntity:
    """提取的实体"""
    name: str
    entity_type: str  # person, org, concept, tech, event, location
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class ExtractedRelation:
    """提取的关系"""
    source_name: str
    target_name: str
    relation_type: str  # related_to, part_of, caused_by, owns, etc.
    evidence: str = ""
    weight: float = 1.0


@dataclass
class GraphQueryResult:
    """知识图谱查询结果"""
    entities: List[KnowledgeEntity]
    relations: List[KnowledgeRelation]
    path: List[str] = field(default_factory=list)  # 推理路径


# ═══════════════════════════════════════════════════════════════════════════
# 实体提取器
# ═══════════════════════════════════════════════════════════════════════════

class EntityExtractor:
    """实体提取器 - 从文本中提取实体"""

    # 实体类型
    ENTITY_TYPES = [
        "person",     # 人物
        "org",        # 组织/公司
        "concept",    # 概念
        "tech",       # 技术
        "event",      # 事件
        "location",   # 地点
        "product",    # 产品
    ]

    # 关系类型
    RELATION_TYPES = [
        "related_to",
        "part_of",
        "caused_by",
        "owns",
        "developed_by",
        "competes_with",
        "partners_with",
        "uses",
        "based_in",
        "founded_by",
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_entities(
        self,
        text: str,
        category: str = "",
        llm_client=None
    ) -> List[ExtractedEntity]:
        """
        从文本中提取实体

        Args:
            text: 待处理的文本
            category: 文本所属领域（用于提示 LLM）
            llm_client: LLM 客户端，如果提供则使用 AI 提取

        Returns:
            提取的实体列表
        """
        if llm_client:
            return await self._extract_with_llm(text, category, llm_client)

        # 使用规则提取（简化版）
        return await self._extract_with_rules(text)

    async def _extract_with_llm(
        self,
        text: str,
        category: str,
        llm_client
    ) -> List[ExtractedEntity]:
        """使用 LLM 提取实体"""
        prompt = f"""从以下{category}领域文章中提取所有实体。

要求：
1. 识别人物、组织、概念、技术、事件、地点、产品
2. 只返回确实在文中明确提到的实体
3. 每个实体给出类型和简要描述

文本内容：
{text[:3000]}

请以JSON格式返回，格式如下：
{{
    "entities": [
        {{"name": "实体名", "type": "person/org/concept/tech/event/location/product", "description": "简要描述"}}
    ]
}}

只返回JSON，不要其他内容。"""

        try:
            response = await llm_client.chat([{"role": "user", "content": prompt}])

            # 解析 JSON
            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text.strip())
            entities = []

            for e in data.get("entities", []):
                entities.append(ExtractedEntity(
                    name=e.get("name", ""),
                    entity_type=e.get("type", "concept"),
                    description=e.get("description", "")
                ))

            return entities

        except Exception as e:
            logger.warning(f"LLM entity extraction failed: {e}")
            return await self._extract_with_rules(text)

    async def _extract_with_rules(self, text: str) -> List[ExtractedEntity]:
        """使用规则提取实体（简化版）"""
        entities = []
        seen = set()

        # 简单规则：识别常见的实体模式
        # 1. 识别技术/产品（带版本号的）
        tech_pattern = r'([A-Z][a-zA-Z0-9]*(?:\s+v?\d+\.\d+(?:\.\d+)?))'
        for match in re.finditer(tech_pattern, text):
            name = match.group(1).strip()
            if name and name not in seen:
                entities.append(ExtractedEntity(
                    name=name,
                    entity_type="tech",
                    description="识别到的技术/产品"
                ))
                seen.add(name)

        # 2. 识别中文公司名
        org_pattern = r'([\u4e00-\u9fa5]{2,}(公司|集团|企业|机构|组织))'
        for match in re.finditer(org_pattern, text):
            name = match.group(1).strip()
            if name and name not in seen:
                entities.append(ExtractedEntity(
                    name=name,
                    entity_type="org",
                    description="识别到的组织"
                ))
                seen.add(name)

        return entities

    async def save_entities(
        self,
        entities: List[ExtractedEntity],
        kb_id: str = ""
    ) -> List[KnowledgeEntity]:
        """保存实体到数据库"""
        saved = []

        for entity in entities:
            # 检查是否已存在
            result = await self.db.execute(
                select(KnowledgeEntity).where(
                    or_(
                        KnowledgeEntity.name == entity.name,
                        KnowledgeEntity.aliases.any(entity.name)
                    )
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # 更新属性
                existing.properties = {**existing.properties, **entity.properties}
                existing.updated_at = datetime.now(timezone.utc)
                saved.append(existing)
            else:
                # 创建新实体
                new_entity = KnowledgeEntity(
                    id=uuid4(),
                    name=entity.name,
                    entity_type=entity.entity_type,
                    description=entity.description,
                    kb_id=kb_id,
                    aliases=entity.aliases,
                    properties=entity.properties
                )
                self.db.add(new_entity)
                saved.append(new_entity)

        await self.db.commit()

        # 刷新获取 ID
        for entity in saved:
            await self.db.refresh(entity)

        return saved


# ═══════════════════════════════════════════════════════════════════════════
# 关系抽取器
# ═══════════════════════════════════════════════════════════════════════════

class RelationExtractor:
    """关系抽取器 - 提取实体间的关系"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_relations(
        self,
        text: str,
        entities: List[ExtractedEntity],
        llm_client=None
    ) -> List[ExtractedRelation]:
        """从文本中提取关系"""
        if llm_client and entities:
            return await self._extract_with_llm(text, entities, llm_client)

        # 简化版：基于共现
        return await self._extract_by_cooccurrence(text, entities)

    async def _extract_with_llm(
        self,
        text: str,
        entities: List[ExtractedEntity],
        llm_client
    ) -> List[ExtractedRelation]:
        """使用 LLM 提取关系"""
        entity_names = [e.name for e in entities]

        prompt = f"""从以下文本中提取{entity_names}之间的关系。

关系类型：related_to, part_of, caused_by, owns, developed_by, competes_with, partners_with, uses, based_in, founded_by

文本内容：
{text[:3000]}

请以JSON格式返回：
{{
    "relations": [
        {{"source": "实体1", "target": "实体2", "type": "关系类型", "evidence": "证据句子"}}
    ]
}}

只返回JSON，不要其他内容。"""

        try:
            response = await llm_client.chat([{"role": "user", "content": prompt}])

            text = response.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text.strip())
            relations = []

            for r in data.get("relations", []):
                relations.append(ExtractedRelation(
                    source_name=r.get("source", ""),
                    target_name=r.get("target", ""),
                    relation_type=r.get("type", "related_to"),
                    evidence=r.get("evidence", "")
                ))

            return relations

        except Exception as e:
            logger.warning(f"LLM relation extraction failed: {e}")
            return await self._extract_by_cooccurrence(text, entities)

    async def _extract_by_cooccurrence(
        self,
        text: str,
        entities: List[ExtractedEntity]
    ) -> List[ExtractedRelation]:
        """基于共现关系（简化版）"""
        relations = []

        # 简单的共现关系
        for i, e1 in enumerate(entities):
            for e2 in entities[i+1:]:
                # 检查两个实体是否在同一句子中出现
                pattern = f"{re.escape(e1.name)}.*?{re.escape(e2.name)}"
                if re.search(pattern, text) or re.search(f"{re.escape(e2.name)}.*?{re.escape(e1.name)}", text):
                    relations.append(ExtractedRelation(
                        source_name=e1.name,
                        target_name=e2.name,
                        relation_type="related_to",
                        weight=0.5
                    ))

        return relations

    async def save_relations(
        self,
        relations: List[ExtractedRelation]
    ) -> List[KnowledgeRelation]:
        """保存关系到数据库"""
        saved = []

        for rel in relations:
            # 查找源实体
            source_result = await self.db.execute(
                select(KnowledgeEntity).where(KnowledgeEntity.name == rel.source_name)
            )
            source = source_result.scalar_one_or_none()

            # 查找目标实体
            target_result = await self.db.execute(
                select(KnowledgeEntity).where(KnowledgeEntity.name == rel.target_name)
            )
            target = target_result.scalar_one_or_none()

            if not source or not target:
                continue

            # 检查是否已存在关系
            result = await self.db.execute(
                select(KnowledgeRelation).where(
                    and_(
                        KnowledgeRelation.source_id == source.id,
                        KnowledgeRelation.target_id == target.id,
                        KnowledgeRelation.relation_type == rel.relation_type
                    )
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # 更新权重
                existing.weight = (existing.weight + rel.weight) / 2
                saved.append(existing)
            else:
                # 创建新关系
                new_rel = KnowledgeRelation(
                    id=uuid4(),
                    source_id=source.id,
                    target_id=target.id,
                    relation_type=rel.relation_type,
                    weight=rel.weight,
                    evidence=rel.evidence
                )
                self.db.add(new_rel)
                saved.append(new_rel)

        await self.db.commit()

        for rel in saved:
            await self.db.refresh(rel)

        return saved


# ═══════════════════════════════════════════════════════════════════════════
# 推理引擎
# ═══════════════════════════════════════════════════════════════════════════

class ReasoningEngine:
    """知识推理引擎 - 基于已有知识推断新关系"""

    MAX_DEPTH = 3  # 最大推理深度

    def __init__(self, db: AsyncSession):
        self.db = db

    async def query(
        self,
        entity_name: str,
        relation_type: str = None,
        max_results: int = 20
    ) -> GraphQueryResult:
        """查询实体及其关系"""
        # 查找实体
        result = await self.db.execute(
            select(KnowledgeEntity).where(
                or_(
                    KnowledgeEntity.name == entity_name,
                    KnowledgeEntity.aliases.any(entity_name)
                )
            )
        )
        entity = result.scalar_one_or_none()

        if not entity:
            return GraphQueryResult(entities=[], relations=[])

        # 查找直接关系
        rel_result = await self.db.execute(
            select(KnowledgeRelation).where(
                or_(
                    KnowledgeRelation.source_id == entity.id,
                    KnowledgeRelation.target_id == entity.id
                )
            ).limit(max_results)
        )
        relations = rel_result.scalars().all()

        # 查找相关实体
        entity_ids = set([entity.id])
        for rel in relations:
            entity_ids.add(rel.source_id)
            entity_ids.add(rel.target_id)

        entity_result = await self.db.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.id.in_(entity_ids))
        )
        entities = entity_result.scalars().all()

        return GraphQueryResult(
            entities=list(entities),
            relations=relations,
            path=[entity_name]
        )

    async def reason(
        self,
        entity_name: str,
        target_type: str = None,
        max_depth: int = None
    ) -> List[str]:
        """
        推理路径

        例如：从 "OpenAI" 推理到 "AI" 领域
        """
        if max_depth is None:
            max_depth = self.MAX_DEPTH

        # 查找实体
        result = await self.db.execute(
            select(KnowledgeEntity).where(KnowledgeEntity.name == entity_name)
        )
        entity = result.scalar_one_or_none()

        if not entity:
            return []

        # BFS 遍历
        visited = {entity.id}
        queue = [(entity.id, [entity_name])]

        results = []

        while queue and len(results) < 10:
            current_id, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            # 如果目标是指定类型
            if target_type:
                current_result = await self.db.execute(
                    select(KnowledgeEntity).where(KnowledgeEntity.id == current_id)
                )
                current_entity = current_result.scalar_one_or_none()
                if current_entity and current_entity.entity_type == target_type:
                    results.append(" -> ".join(path + [current_entity.name]))
                    continue

            # 查找下一层关系
            rel_result = await self.db.execute(
                select(KnowledgeRelation).where(
                    or_(
                        KnowledgeRelation.source_id == current_id,
                        KnowledgeRelation.target_id == current_id
                    )
                )
            )
            relations = rel_result.scalars().all()

            for rel in relations:
                next_id = rel.target_id if rel.source_id == current_id else rel.source_id

                if next_id in visited:
                    continue

                visited.add(next_id)

                # 获取下一实体名
                next_result = await self.db.execute(
                    select(KnowledgeEntity).where(KnowledgeEntity.id == next_id)
                )
                next_entity = next_result.scalar_one_or_none()

                if next_entity:
                    queue.append((next_id, path + [next_entity.name]))

        return results


# ═══════════════════════════════════════════════════════════════════════════
# 分类管理器
# ═══════════════════════════════════════════════════════════════════════════

class CategoryManager:
    """知识分类管理器 - 层次化分类体系"""

    DEFAULT_CATEGORIES = [
        {"name": "人工智能", "children": ["大模型", "机器学习", "计算机视觉", "自然语言处理"]},
        {"name": "科技", "children": ["硬件", "软件", "互联网", "移动互联网"]},
        {"name": "财经", "children": ["投资", "加密货币", "宏观经济", "公司财报"]},
        {"name": "商业", "children": ["创业", "公司", "行业", "市场"]},
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def init_default_categories(self):
        """初始化默认分类"""
        for cat in self.DEFAULT_CATEGORIES:
            await self._create_category(cat["name"], None)
            if "children" in cat:
                for child in cat["children"]:
                    # 先查找父分类
                    parent_result = await self.db.execute(
                        select(KnowledgeCategory).where(KnowledgeCategory.name == cat["name"])
                    )
                    parent = parent_result.scalar_one_or_none()
                    if parent:
                        await self._create_category(child, parent.id)

    async def _create_category(self, name: str, parent_id: str = None) -> KnowledgeCategory:
        """创建分类"""
        # 检查是否已存在
        result = await self.db.execute(
            select(KnowledgeCategory).where(
                and_(
                    KnowledgeCategory.name == name,
                    KnowledgeCategory.parent_id == parent_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        category = KnowledgeCategory(
            id=uuid4(),
            name=name,
            parent_id=parent_id
        )
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def get_category_tree(self, parent_id: str = None) -> List[Dict]:
        """获取分类树"""
        result = await self.db.execute(
            select(KnowledgeCategory).where(KnowledgeCategory.parent_id == parent_id)
        )
        categories = result.scalars().all()

        tree = []
        for cat in categories:
            children = await self.get_category_tree(str(cat.id))
            tree.append({
                "id": str(cat.id),
                "name": cat.name,
                "description": cat.description,
                "entity_count": cat.entity_count,
                "children": children
            })

        return tree

    async def assign_entity_to_category(
        self,
        entity_id: str,
        category_id: str
    ):
        """将实体分配到分类"""
        # 这里可以扩展实现
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 知识图谱管理器（主入口）
# ═══════════════════════════════════════════════════════════════════════════

class KnowledgeGraphManager:
    """知识图谱管理器 - 统一入口"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.entity_extractor = EntityExtractor(db)
        self.relation_extractor = RelationExtractor(db)
        self.reasoning_engine = ReasoningEngine(db)
        self.category_manager = CategoryManager(db)

    async def process_text(
        self,
        text: str,
        title: str = "",
        category: str = "",
        kb_id: str = "",
        llm_client=None
    ) -> Dict[str, Any]:
        """
        处理文本，构建知识图谱

        流程：实体提取 -> 关系抽取 -> 保存到数据库
        """
        # 1. 提取实体
        entities = await self.entity_extractor.extract_entities(
            text, category, llm_client
        )

        if not entities:
            return {"status": "no_entities", "entities": [], "relations": []}

        # 2. 保存实体
        saved_entities = await self.entity_extractor.save_entities(entities, kb_id)

        # 3. 提取关系
        relations = await self.relation_extractor.extract_relations(
            text, entities, llm_client
        )

        # 4. 保存关系
        saved_relations = await self.relation_extractor.save_relations(relations)

        return {
            "status": "success",
            "entities": [{"id": str(e.id), "name": e.name, "type": e.entity_type}
                        for e in saved_entities],
            "relations": [{"source": r.source_id, "target": r.target_id, "type": r.relation_type}
                         for r in saved_relations]
        }

    async def search(self, query: str, max_results: int = 20) -> GraphQueryResult:
        """搜索知识图谱"""
        return await self.reasoning_engine.query(query, max_results=max_results)

    async def reason(self, entity: str, target_type: str = None) -> List[str]:
        """知识推理"""
        return await self.reasoning_engine.reason(entity, target_type)

    async def get_categories(self) -> List[Dict]:
        """获取分类树"""
        return await self.category_manager.get_category_tree()

    async def add_feed_to_graph(
        self,
        feed_item_id: str,
        llm_client=None
    ) -> Dict[str, Any]:
        """将信息流条目添加到知识图谱"""
        # 获取 feed 内容
        result = await self.db.execute(
            select(FeedItem).where(FeedItem.id == feed_item_id)
        )
        feed = result.scalar_one_or_none()

        if not feed:
            return {"status": "error", "message": "Feed not found"}

        # 处理内容
        text = f"{feed.title}\n{feed.content or feed.summary or ''}"
        result = await self.process_text(
            text=text,
            title=feed.title,
            category=feed.category or "",
            kb_id=feed.category,
            llm_client=llm_client
        )

        # 标记已提取知识
        feed.is_knowledge_extracted = True
        await self.db.commit()

        return result


# 辅助函数
_kg_manager: Optional[KnowledgeGraphManager] = None


async def get_knowledge_graph(db: AsyncSession) -> KnowledgeGraphManager:
    """获取知识图谱管理器实例"""
    global _kg_manager
    if _kg_manager is None:
        _kg_manager = KnowledgeGraphManager(db)
    else:
        _kg_manager.db = db
    return _kg_manager
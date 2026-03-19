"""
Memories Router - Memory management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db, MemoryFact, FactType
from memory import get_memory_engine

router = APIRouter()

# Default user ID (will be replaced with auth later)
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"


# Request/Response Models
class MemoryCreate(BaseModel):
    content: str
    fact_type: str  # preference, fact, decision, insight
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    confidence: float = 0.8


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    fact_type: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    confidence: Optional[float] = None


class MemoryResponse(BaseModel):
    memory_id: str
    content: str
    fact_type: str
    category: Optional[str]
    tags: List[str]
    confidence: float
    access_count: int
    created_at: str
    source_conversation_id: Optional[str] = None

    class Config:
        from_attributes = True


class MemoryListResponse(BaseModel):
    memories: List[MemoryResponse]
    total: int
    page: int
    page_size: int


class MemoryStatsResponse(BaseModel):
    total_memories: int
    type_distribution: dict
    collection_status: str


@router.post("", response_model=MemoryResponse)
async def create_memory(
    data: MemoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Manually create a new memory"""
    # Validate fact_type
    if data.fact_type not in ["preference", "fact", "decision", "insight"]:
        raise HTTPException(status_code=400, detail="Invalid fact_type")
    
    memory_engine = get_memory_engine()
    
    # Add to vector store
    memory_id = await memory_engine.add_memory(
        user_id=DEFAULT_USER_ID,
        content=data.content,
        memory_type=data.fact_type,
        category=data.category,
        tags=data.tags,
        confidence=data.confidence,
    )
    
    # Also save to PostgreSQL for structured queries
    fact_type_enum = FactType(data.fact_type)
    db_memory = MemoryFact(
        id=UUID(memory_id),
        user_id=UUID(DEFAULT_USER_ID),
        fact_type=fact_type_enum,
        content=data.content,
        category=data.category,
        tags=data.tags or [],
        confidence=data.confidence,
        embedding_id=memory_id,
    )
    db.add(db_memory)
    await db.commit()
    
    return MemoryResponse(
        memory_id=memory_id,
        content=data.content,
        fact_type=data.fact_type,
        category=data.category,
        tags=data.tags or [],
        confidence=data.confidence,
        access_count=0,
        created_at=datetime.utcnow().isoformat(),
    )


@router.get("", response_model=MemoryListResponse)
async def list_memories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fact_type: Optional[str] = None,
    category: Optional[str] = None,
):
    """List all memories for the current user"""
    memory_engine = get_memory_engine()
    
    offset = (page - 1) * page_size
    memories, total = await memory_engine.list_memories(
        user_id=DEFAULT_USER_ID,
        memory_type=fact_type,
        limit=page_size,
        offset=offset,
    )
    
    return MemoryListResponse(
        memories=[
            MemoryResponse(
                memory_id=m["memory_id"],
                content=m["content"],
                fact_type=m["memory_type"],
                category=m.get("category"),
                tags=m.get("tags", []),
                confidence=m.get("confidence", 0.8),
                access_count=m.get("access_count", 0),
                created_at=m.get("created_at", ""),
                source_conversation_id=m.get("source_conversation_id"),
            )
            for m in memories
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats():
    """Get memory statistics for the current user"""
    memory_engine = get_memory_engine()
    stats = await memory_engine.get_stats(user_id=DEFAULT_USER_ID)
    
    return MemoryStatsResponse(
        total_memories=stats["total_memories"],
        type_distribution=stats["type_distribution"],
        collection_status=stats["collection_status"],
    )


@router.get("/search")
async def search_memories(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    fact_type: Optional[str] = None,
):
    """Search memories by semantic similarity"""
    memory_engine = get_memory_engine()
    
    results = await memory_engine.search_memories(
        query=query,
        user_id=DEFAULT_USER_ID,
        limit=limit,
        memory_type=fact_type,
    )
    
    return {
        "results": [
            {
                "memory_id": r.memory_id,
                "content": r.content,
                "fact_type": r.memory_type,
                "category": r.category,
                "tags": r.tags,
                "confidence": r.confidence,
                "score": r.score,
                "access_count": r.access_count,
            }
            for r in results
        ],
        "total": len(results),
    }


@router.get("/profile")
async def get_user_profile():
    """Get user profile summary from memories"""
    memory_engine = get_memory_engine()
    
    profile_memories = await memory_engine.get_user_profile(
        user_id=DEFAULT_USER_ID,
        limit=20,
    )
    
    # Group by type
    preferences = []
    facts = []
    
    for mem in profile_memories:
        item = {
            "memory_id": mem.memory_id,
            "content": mem.content,
            "category": mem.category,
            "confidence": mem.confidence,
        }
        if mem.memory_type == "preference":
            preferences.append(item)
        elif mem.memory_type == "fact":
            facts.append(item)
    
    return {
        "preferences": preferences,
        "facts": facts,
        "total_preferences": len(preferences),
        "total_facts": len(facts),
    }


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str):
    """Get a specific memory by ID"""
    memory_engine = get_memory_engine()
    
    # Search for specific memory
    memories, _ = await memory_engine.list_memories(
        user_id=DEFAULT_USER_ID,
        limit=100,
    )
    
    for m in memories:
        if m["memory_id"] == memory_id:
            return MemoryResponse(
                memory_id=m["memory_id"],
                content=m["content"],
                fact_type=m["memory_type"],
                category=m.get("category"),
                tags=m.get("tags", []),
                confidence=m.get("confidence", 0.8),
                access_count=m.get("access_count", 0),
                created_at=m.get("created_at", ""),
                source_conversation_id=m.get("source_conversation_id"),
            )
    
    raise HTTPException(status_code=404, detail="Memory not found")


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    data: MemoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a memory"""
    memory_engine = get_memory_engine()
    
    # Get existing memory
    memories, _ = await memory_engine.list_memories(
        user_id=DEFAULT_USER_ID,
        limit=100,
    )
    
    existing = None
    for m in memories:
        if m["memory_id"] == memory_id:
            existing = m
            break
    
    if not existing:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Delete old and create new (Qdrant doesn't support partial updates well)
    await memory_engine.delete_memory(memory_id, DEFAULT_USER_ID)
    
    new_content = data.content if data.content is not None else existing["content"]
    new_type = data.fact_type if data.fact_type is not None else existing["memory_type"]
    new_category = data.category if data.category is not None else existing.get("category")
    new_tags = data.tags if data.tags is not None else existing.get("tags", [])
    new_confidence = data.confidence if data.confidence is not None else existing.get("confidence", 0.8)
    
    # Create updated memory
    new_memory_id = await memory_engine.add_memory(
        user_id=DEFAULT_USER_ID,
        content=new_content,
        memory_type=new_type,
        memory_id=memory_id,  # Keep same ID
        category=new_category,
        tags=new_tags,
        confidence=new_confidence,
    )
    
    # Update PostgreSQL record if exists
    try:
        await db.execute(
            update(MemoryFact)
            .where(MemoryFact.id == UUID(memory_id))
            .values(
                content=new_content,
                fact_type=FactType(new_type),
                category=new_category,
                tags=new_tags,
                confidence=new_confidence,
            )
        )
        await db.commit()
    except Exception:
        pass  # PostgreSQL record may not exist
    
    return MemoryResponse(
        memory_id=new_memory_id,
        content=new_content,
        fact_type=new_type,
        category=new_category,
        tags=new_tags,
        confidence=new_confidence,
        access_count=existing.get("access_count", 0),
        created_at=existing.get("created_at", datetime.utcnow().isoformat()),
    )


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a memory (soft delete by setting valid_until)"""
    memory_engine = get_memory_engine()
    
    # Delete from Qdrant
    await memory_engine.delete_memory(memory_id, DEFAULT_USER_ID)
    
    # Delete from PostgreSQL if exists
    try:
        await db.execute(
            delete(MemoryFact).where(MemoryFact.id == UUID(memory_id))
        )
        await db.commit()
    except Exception:
        pass
    
    return {"message": "Memory deleted", "memory_id": memory_id}

"""
Memory Engine - Long-term memory storage and retrieval using Qdrant
"""

import hashlib
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from qdrant_client.http import models as qdrant_models
from sentence_transformers import SentenceTransformer

from config import create_qdrant_client, get_settings


@dataclass
class MemorySearchResult:
    """Search result from memory retrieval"""
    memory_id: str
    content: str
    memory_type: str
    category: Optional[str]
    tags: List[str]
    confidence: float
    score: float
    access_count: int
    created_at: str


class MemoryEngine:
    """Long-term memory management engine using Qdrant"""
    
    COLLECTION_NAME = "myattention_memories"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384
    
    def __init__(self):
        settings = get_settings()
        self.client = create_qdrant_client(settings)
        self._encoder: Optional[SentenceTransformer] = None
        self._ensure_collection()
    
    @property
    def encoder(self) -> SentenceTransformer:
        """Lazy load the embedding model"""
        if self._encoder is None:
            self._encoder = SentenceTransformer(self.EMBEDDING_MODEL)
        return self._encoder
    
    def _ensure_collection(self):
        """Ensure the memories collection exists"""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.COLLECTION_NAME for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=qdrant_models.VectorParams(
                    size=self.EMBEDDING_DIM,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )
            # Create payload indexes for filtering
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="user_id",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name="memory_type",
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )
    
    def _generate_point_id(self, content: str, user_id: str) -> str:
        """Generate deterministic point ID from content hash"""
        hash_input = f"{user_id}:{content[:200]}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    async def add_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str,
        memory_id: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        confidence: float = 0.8,
        source_conversation_id: Optional[str] = None,
        source_message_ids: Optional[List[str]] = None,
        valid_until: Optional[datetime] = None,
    ) -> str:
        """Add a new memory to the vector store"""
        # Generate embedding
        embedding = self.encoder.encode(content).tolist()
        
        # Generate IDs
        if memory_id is None:
            memory_id = str(uuid4())
        point_id = self._generate_point_id(content, user_id)
        
        # Build payload
        payload = {
            "memory_id": memory_id,
            "user_id": user_id,
            "content": content,
            "memory_type": memory_type,
            "category": category or "",
            "tags": tags or [],
            "confidence": confidence,
            "access_count": 0,
            "source_conversation_id": source_conversation_id or "",
            "source_message_ids": source_message_ids or [],
            "created_at": datetime.utcnow().isoformat(),
            "valid_until": valid_until.isoformat() if valid_until else None,
        }
        
        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                qdrant_models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )
        
        return memory_id
    
    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
        score_threshold: float = 0.5,
        memory_type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[MemorySearchResult]:
        """Search memories by semantic similarity"""
        # Generate query embedding
        query_embedding = self.encoder.encode(query).tolist()
        
        # Build filter
        must_conditions = [
            qdrant_models.FieldCondition(
                key="user_id",
                match=qdrant_models.MatchValue(value=user_id),
            )
        ]
        
        if memory_type:
            must_conditions.append(
                qdrant_models.FieldCondition(
                    key="memory_type",
                    match=qdrant_models.MatchValue(value=memory_type),
                )
            )
        
        if category:
            must_conditions.append(
                qdrant_models.FieldCondition(
                    key="category",
                    match=qdrant_models.MatchValue(value=category),
                )
            )
        
        # Search
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_embedding,
            query_filter=qdrant_models.Filter(must=must_conditions),
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )
        
        # Convert to results
        memories = []
        for point in results.points:
            payload = point.payload
            memories.append(MemorySearchResult(
                memory_id=payload.get("memory_id", ""),
                content=payload.get("content", ""),
                memory_type=payload.get("memory_type", ""),
                category=payload.get("category"),
                tags=payload.get("tags", []),
                confidence=payload.get("confidence", 0.8),
                score=point.score,
                access_count=payload.get("access_count", 0),
                created_at=payload.get("created_at", ""),
            ))
        
        return memories
    
    async def get_user_profile(
        self,
        user_id: str,
        limit: int = 10,
    ) -> List[MemorySearchResult]:
        """Get user's preference and fact memories for profile"""
        # Get preference memories
        filter_condition = qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="user_id",
                    match=qdrant_models.MatchValue(value=user_id),
                ),
            ],
            should=[
                qdrant_models.FieldCondition(
                    key="memory_type",
                    match=qdrant_models.MatchValue(value="preference"),
                ),
                qdrant_models.FieldCondition(
                    key="memory_type",
                    match=qdrant_models.MatchValue(value="fact"),
                ),
            ],
        )
        
        results = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            scroll_filter=filter_condition,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        
        memories = []
        for point in results[0]:
            payload = point.payload
            memories.append(MemorySearchResult(
                memory_id=payload.get("memory_id", ""),
                content=payload.get("content", ""),
                memory_type=payload.get("memory_type", ""),
                category=payload.get("category"),
                tags=payload.get("tags", []),
                confidence=payload.get("confidence", 0.8),
                score=1.0,  # No score for scroll
                access_count=payload.get("access_count", 0),
                created_at=payload.get("created_at", ""),
            ))
        
        return memories
    
    async def update_access_stats(self, memory_id: str, user_id: str):
        """Update access count and last accessed time for a memory"""
        # Find the point by memory_id
        filter_condition = qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="memory_id",
                    match=qdrant_models.MatchValue(value=memory_id),
                ),
                qdrant_models.FieldCondition(
                    key="user_id",
                    match=qdrant_models.MatchValue(value=user_id),
                ),
            ]
        )
        
        results = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            scroll_filter=filter_condition,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )
        
        if results[0]:
            point = results[0][0]
            new_access_count = point.payload.get("access_count", 0) + 1
            
            self.client.set_payload(
                collection_name=self.COLLECTION_NAME,
                payload={
                    "access_count": new_access_count,
                    "last_accessed_at": datetime.utcnow().isoformat(),
                },
                points=[point.id],
            )
    
    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Delete a memory by ID"""
        filter_condition = qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="memory_id",
                    match=qdrant_models.MatchValue(value=memory_id),
                ),
                qdrant_models.FieldCondition(
                    key="user_id",
                    match=qdrant_models.MatchValue(value=user_id),
                ),
            ]
        )
        
        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=qdrant_models.FilterSelector(filter=filter_condition),
        )
        
        return True
    
    async def list_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Dict[str, Any]], int]:
        """List all memories for a user with pagination"""
        must_conditions = [
            qdrant_models.FieldCondition(
                key="user_id",
                match=qdrant_models.MatchValue(value=user_id),
            )
        ]
        
        if memory_type:
            must_conditions.append(
                qdrant_models.FieldCondition(
                    key="memory_type",
                    match=qdrant_models.MatchValue(value=memory_type),
                )
            )
        
        filter_condition = qdrant_models.Filter(must=must_conditions)
        
        # Count total
        count_result = self.client.count(
            collection_name=self.COLLECTION_NAME,
            count_filter=filter_condition,
        )
        total = count_result.count
        
        # Get paginated results
        results = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            scroll_filter=filter_condition,
            limit=limit,
            offset=offset if offset else None,
            with_payload=True,
            with_vectors=False,
        )
        
        memories = []
        for point in results[0]:
            payload = point.payload
            memories.append({
                "memory_id": payload.get("memory_id", ""),
                "content": payload.get("content", ""),
                "memory_type": payload.get("memory_type", ""),
                "category": payload.get("category"),
                "tags": payload.get("tags", []),
                "confidence": payload.get("confidence", 0.8),
                "access_count": payload.get("access_count", 0),
                "created_at": payload.get("created_at", ""),
                "source_conversation_id": payload.get("source_conversation_id", ""),
            })
        
        return memories, total
    
    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a user"""
        filter_condition = qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="user_id",
                    match=qdrant_models.MatchValue(value=user_id),
                )
            ]
        )
        
        count_result = self.client.count(
            collection_name=self.COLLECTION_NAME,
            count_filter=filter_condition,
        )
        
        # Get type distribution
        type_counts = {}
        for memory_type in ["preference", "fact", "decision", "insight"]:
            type_filter = qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="user_id",
                        match=qdrant_models.MatchValue(value=user_id),
                    ),
                    qdrant_models.FieldCondition(
                        key="memory_type",
                        match=qdrant_models.MatchValue(value=memory_type),
                    ),
                ]
            )
            type_count = self.client.count(
                collection_name=self.COLLECTION_NAME,
                count_filter=type_filter,
            )
            type_counts[memory_type] = type_count.count
        
        return {
            "total_memories": count_result.count,
            "type_distribution": type_counts,
            "collection_status": "green",
        }


# Singleton instance
_memory_engine: Optional[MemoryEngine] = None


def get_memory_engine() -> MemoryEngine:
    """Get or create the singleton MemoryEngine instance"""
    global _memory_engine
    if _memory_engine is None:
        _memory_engine = MemoryEngine()
    return _memory_engine

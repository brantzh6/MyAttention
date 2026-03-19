"""
RAG Engine - Retrieval Augmented Generation

Provides semantic search capabilities using:
- Qdrant for vector storage and retrieval
- Sentence Transformers for text embedding
- Context augmentation for LLM queries
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import uuid

from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer

from config import create_qdrant_client, get_settings


@dataclass
class Document:
    """A document with its metadata"""
    id: str
    content: str
    title: str = ""
    source: str = ""
    source_type: str = ""
    url: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchResult:
    """A search result with relevance score"""
    document: Document
    score: float
    

class RAGEngine:
    """
    RAG Engine for semantic document retrieval
    
    Features:
    - Document chunking and embedding
    - Semantic similarity search
    - Context augmentation for LLM
    - Source tracking and citation
    """
    
    COLLECTION_NAME = "myattention_docs"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and efficient
    EMBEDDING_DIM = 384
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    def __init__(self):
        settings = get_settings()
        self.client = create_qdrant_client(settings)
        self._encoder = None
        self._ensure_collection()
    
    @property
    def encoder(self) -> SentenceTransformer:
        """Lazy load the embedding model"""
        if self._encoder is None:
            self._encoder = SentenceTransformer(self.EMBEDDING_MODEL)
        return self._encoder
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.COLLECTION_NAME for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=qmodels.VectorParams(
                    size=self.EMBEDDING_DIM,
                    distance=qmodels.Distance.COSINE,
                ),
            )
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.CHUNK_SIZE:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.CHUNK_SIZE
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('。')
                if last_period == -1:
                    last_period = chunk.rfind('. ')
                if last_period > self.CHUNK_SIZE // 2:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk.strip())
            start = end - self.CHUNK_OVERLAP
        
        return [c for c in chunks if c]
    
    def _generate_id(self, content: str, source: str) -> str:
        """Generate deterministic ID from content hash"""
        hash_input = f"{source}:{content[:200]}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    async def add_document(self, doc: Document) -> List[str]:
        """
        Add a document to the vector store
        
        Returns list of chunk IDs
        """
        chunks = self._chunk_text(doc.content)
        chunk_ids = []
        
        points = []
        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_id(chunk, doc.source)
            chunk_ids.append(chunk_id)
            
            # Generate embedding
            embedding = self.encoder.encode(chunk).tolist()
            
            # Create point
            points.append(qmodels.PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "content": chunk,
                    "title": doc.title,
                    "source": doc.source,
                    "source_type": doc.source_type,
                    "url": doc.url,
                    "doc_id": doc.id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    **doc.metadata,
                },
            ))
        
        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )
        
        return chunk_ids
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.5,
        filter_source: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            limit: Maximum results to return
            score_threshold: Minimum similarity score
            filter_source: Optional source filter
            
        Returns:
            List of SearchResult ordered by relevance
        """
        # Generate query embedding
        query_embedding = self.encoder.encode(query).tolist()
        
        # Build filter if needed
        query_filter = None
        if filter_source:
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="source",
                        match=qmodels.MatchValue(value=filter_source),
                    )
                ]
            )
        
        # Search using query_points (qdrant-client 1.17+)
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        
        # Convert to SearchResult
        search_results = []
        for hit in results.points:
            payload = hit.payload
            doc = Document(
                id=payload.get("doc_id", ""),
                content=payload.get("content", ""),
                title=payload.get("title", ""),
                source=payload.get("source", ""),
                source_type=payload.get("source_type", ""),
                url=payload.get("url", ""),
                metadata={
                    k: v for k, v in payload.items()
                    if k not in ["content", "title", "source", "source_type", "url", "doc_id"]
                },
            )
            search_results.append(SearchResult(document=doc, score=hit.score))
        
        return search_results
    
    async def build_context(
        self,
        query: str,
        max_tokens: int = 2000,
        limit: int = 5,
    ) -> tuple[str, List[Dict[str, str]]]:
        """
        Build context for LLM from relevant documents
        
        Args:
            query: User's question
            max_tokens: Approximate max context length
            limit: Max documents to retrieve
            
        Returns:
            Tuple of (context_string, sources_list)
        """
        results = await self.search(query, limit=limit)
        
        if not results:
            return "", []
        
        # Filter out low-relevance results
        results = [r for r in results if r.score >= 0.5]
        
        if not results:
            return "", []
        
        context_parts = []
        sources = []
        total_length = 0
        
        for result in results:
            doc = result.document
            content = doc.content
            
            # Estimate tokens (rough: 1 token ≈ 4 chars for Chinese)
            content_tokens = len(content) // 2
            
            if total_length + content_tokens > max_tokens:
                # Truncate if needed
                remaining = (max_tokens - total_length) * 2
                if remaining > 100:
                    content = content[:remaining] + "..."
                else:
                    break
            
            context_parts.append(f"【来源: {doc.source}】\n{content}")
            sources.append({
                "title": doc.title or doc.source,
                "url": doc.url,
                "source": doc.source,
                "score": round(result.score, 3),
            })
            
            total_length += content_tokens
        
        context = "\n\n---\n\n".join(context_parts)
        return context, sources
    
    async def delete_by_source(self, source: str) -> int:
        """Delete all documents from a specific source"""
        result = self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="source",
                            match=qmodels.MatchValue(value=source),
                        )
                    ]
                )
            ),
        )
        return result.status
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        info = self.client.get_collection(self.COLLECTION_NAME)
        return {
            "total_documents": info.points_count,
            "status": str(info.status),
        }

    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents, deduplicated by doc_id"""
        all_docs: Dict[str, Dict[str, Any]] = {}
        offset = None

        while True:
            result = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            points, next_offset = result

            for point in points:
                p = point.payload
                doc_id = p.get("doc_id", "")
                if doc_id not in all_docs:
                    all_docs[doc_id] = {
                        "doc_id": doc_id,
                        "title": p.get("title", ""),
                        "source": p.get("source", ""),
                        "source_type": p.get("source_type", ""),
                        "url": p.get("url", ""),
                        "chunk_count": 0,
                        "preview": "",
                    }
                all_docs[doc_id]["chunk_count"] += 1
                if not all_docs[doc_id]["preview"] and p.get("content"):
                    all_docs[doc_id]["preview"] = p["content"][:150]

            if next_offset is None:
                break
            offset = next_offset

        return list(all_docs.values())

    async def list_sources(self) -> List[Dict[str, Any]]:
        """List all sources with document counts"""
        source_map: Dict[str, int] = {}
        offset = None

        while True:
            result = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                limit=100,
                offset=offset,
                with_payload=["source", "doc_id"],
                with_vectors=False,
            )

            points, next_offset = result
            doc_ids_seen: Dict[str, set] = {}

            for point in points:
                source = point.payload.get("source", "unknown")
                doc_id = point.payload.get("doc_id", "")
                if source not in doc_ids_seen:
                    doc_ids_seen[source] = set()
                doc_ids_seen[source].add(doc_id)

            for source, ids in doc_ids_seen.items():
                source_map[source] = source_map.get(source, 0) + len(ids)

            if next_offset is None:
                break
            offset = next_offset

        return [
            {"name": name, "count": count}
            for name, count in sorted(source_map.items())
        ]

    async def delete_by_doc_id(self, doc_id: str) -> int:
        """Delete all chunks belonging to a specific document"""
        result = self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="doc_id",
                            match=qmodels.MatchValue(value=doc_id),
                        )
                    ]
                )
            ),
        )
        return result.status


# Singleton instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

"""
Context Builder - Assemble conversation context from multiple memory layers
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db import Message, Conversation
from rag import get_rag_engine
from .engine import MemoryEngine, get_memory_engine


@dataclass
class ContextSource:
    """A source used in context building"""
    type: str  # short_term, long_term, rag
    id: str
    content: str
    score: Optional[float] = None
    title: Optional[str] = None
    url: Optional[str] = None


class ContextBuilder:
    """
    Build conversation context from three memory layers:
    1. Short-term memory: Recent conversation messages
    2. Long-term memory: Extracted facts from past conversations
    3. RAG documents: External knowledge base
    """
    
    # Token allocation ratios (total ~5000 tokens)
    SHORT_TERM_RATIO = 0.4   # ~2000 tokens
    LONG_TERM_RATIO = 0.3    # ~1500 tokens
    RAG_RATIO = 0.3          # ~1500 tokens
    
    # Chars per token estimate (Chinese: ~2 chars/token)
    CHARS_PER_TOKEN = 2
    
    def __init__(self):
        self.memory_engine = get_memory_engine()
        self.rag_engine = get_rag_engine()
    
    async def build_context(
        self,
        query: str,
        user_id: str,
        conversation_id: Optional[str],
        db: AsyncSession,
        max_tokens: int = 5000,
        include_rag: bool = True,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Build complete context for LLM from all memory layers.
        
        Returns:
            Tuple of (system_prompt_extension, sources_list)
        """
        sources: List[Dict[str, Any]] = []
        context_parts = []
        
        # Calculate token budgets
        short_term_budget = int(max_tokens * self.SHORT_TERM_RATIO)
        long_term_budget = int(max_tokens * self.LONG_TERM_RATIO)
        rag_budget = int(max_tokens * self.RAG_RATIO) if include_rag else 0
        
        # 1. Get short-term context (recent messages)
        short_term_context, short_term_sources = await self._get_short_term_context(
            db=db,
            conversation_id=conversation_id,
            max_tokens=short_term_budget,
        )
        if short_term_context:
            context_parts.append(("历史对话", short_term_context))
            sources.extend(short_term_sources)
        
        # 2. Get long-term memory context
        long_term_context, long_term_sources = await self._get_long_term_context(
            query=query,
            user_id=user_id,
            max_tokens=long_term_budget,
        )
        if long_term_context:
            context_parts.append(("用户记忆", long_term_context))
            sources.extend(long_term_sources)
        
        # 3. Get RAG context
        if include_rag:
            rag_context, rag_sources = await self._get_rag_context(
                query=query,
                max_tokens=rag_budget,
            )
            if rag_context:
                context_parts.append(("知识库", rag_context))
                sources.extend(rag_sources)
        
        # Build the system prompt extension
        if not context_parts:
            return "", sources
        
        prompt_extension = "\n\n".join([
            f"## {title}\n{content}"
            for title, content in context_parts
        ])
        
        return prompt_extension, sources
    
    async def _get_short_term_context(
        self,
        db: AsyncSession,
        conversation_id: Optional[str],
        max_tokens: int,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Get recent messages from current conversation"""
        if not conversation_id:
            return "", []
        
        try:
            conv_uuid = UUID(conversation_id)
        except ValueError:
            return "", []
        
        # Get conversation settings
        conv_query = select(Conversation).where(Conversation.id == conv_uuid)
        conv_result = await db.execute(conv_query)
        conv = conv_result.scalar_one_or_none()
        
        if not conv:
            return "", []
        
        context_window = conv.context_window or 10
        
        # Get recent messages
        msg_query = (
            select(Message)
            .where(Message.conversation_id == conv_uuid)
            .order_by(desc(Message.created_at))
            .limit(context_window)
        )
        result = await db.execute(msg_query)
        messages = list(reversed(result.scalars().all()))
        
        if not messages:
            return "", []
        
        # Build context string with token budget
        max_chars = max_tokens * self.CHARS_PER_TOKEN
        context_parts = []
        total_chars = 0
        sources = []
        
        for msg in messages:
            role_label = "用户" if msg.role.value == "user" else "助手"
            msg_text = f"{role_label}: {msg.content}"
            
            if total_chars + len(msg_text) > max_chars:
                # Truncate if needed
                remaining = max_chars - total_chars
                if remaining > 50:
                    msg_text = msg_text[:remaining] + "..."
                    context_parts.append(msg_text)
                break
            
            context_parts.append(msg_text)
            total_chars += len(msg_text)
            
            sources.append({
                "type": "short_term",
                "id": str(msg.id),
                "title": f"对话消息",
                "source": "conversation",
            })
        
        return "\n".join(context_parts), sources
    
    async def _get_long_term_context(
        self,
        query: str,
        user_id: str,
        max_tokens: int,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Get relevant long-term memories"""
        # Search relevant memories
        memories = await self.memory_engine.search_memories(
            query=query,
            user_id=user_id,
            limit=10,
            score_threshold=0.5,
        )
        
        # Also get user profile (preferences and facts)
        profile_memories = await self.memory_engine.get_user_profile(
            user_id=user_id,
            limit=5,
        )
        
        # Combine and deduplicate
        all_memories = []
        seen_ids = set()
        
        for mem in memories + profile_memories:
            if mem.memory_id not in seen_ids:
                all_memories.append(mem)
                seen_ids.add(mem.memory_id)
        
        if not all_memories:
            return "", []
        
        # Build context with token budget
        max_chars = max_tokens * self.CHARS_PER_TOKEN
        context_parts = []
        total_chars = 0
        sources = []
        
        for mem in all_memories:
            type_label = {
                "preference": "偏好",
                "fact": "事实",
                "decision": "决策",
                "insight": "洞察",
            }.get(mem.memory_type, "记忆")
            
            mem_text = f"- [{type_label}] {mem.content}"
            
            if total_chars + len(mem_text) > max_chars:
                break
            
            context_parts.append(mem_text)
            total_chars += len(mem_text)
            
            sources.append({
                "type": "long_term",
                "id": mem.memory_id,
                "title": mem.content[:50],
                "source": "memory",
                "memory_type": mem.memory_type,
                "score": mem.score,
            })
            
            # Update access stats in background
            try:
                await self.memory_engine.update_access_stats(mem.memory_id, user_id)
            except Exception:
                pass  # Non-critical
        
        return "\n".join(context_parts), sources
    
    async def _get_rag_context(
        self,
        query: str,
        max_tokens: int,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Get relevant RAG documents"""
        try:
            context, rag_sources = await self.rag_engine.build_context(
                query=query,
                max_tokens=max_tokens,
                limit=5,
            )
            
            # Convert sources to standard format
            sources = [
                {
                    "type": "rag",
                    "id": s.get("doc_id", ""),
                    "title": s.get("title", ""),
                    "url": s.get("url", ""),
                    "source": s.get("source", ""),
                    "score": s.get("score", 0),
                }
                for s in rag_sources
            ]
            
            return context, sources
            
        except Exception as e:
            print(f"RAG context error: {e}")
            return "", []
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        return len(text) // self.CHARS_PER_TOKEN

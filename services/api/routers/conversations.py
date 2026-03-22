"""
Conversations Router - Conversation management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db, Conversation, Message, MessageRole

router = APIRouter()

# Default user ID (will be replaced with auth later)
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def _looks_corrupted_title(value: Optional[str]) -> bool:
    if not value:
        return False
    text = value.strip()
    if not text:
        return False
    question_marks = text.count("?")
    return "�" in text or (question_marks >= 3 and question_marks / max(len(text), 1) >= 0.3)


def _build_conversation_title(content: Optional[str]) -> str:
    if not content:
        return "新对话"
    title = " ".join(content.strip().split())
    if not title:
        return "新对话"
    if len(title) > 50:
        title = f"{title[:50].strip()}..."
    return title


async def _resolve_conversation_title(db: AsyncSession, conv: Conversation) -> str:
    if conv.title and not _looks_corrupted_title(conv.title):
        return conv.title

    query = (
        select(Message.content)
        .where(
            Message.conversation_id == conv.id,
            Message.role == MessageRole.USER,
        )
        .order_by(Message.created_at.asc())
        .limit(1)
    )
    result = await db.execute(query)
    first_message = result.scalar_one_or_none()
    fallback_title = _build_conversation_title(first_message)
    if _looks_corrupted_title(fallback_title):
        fallback_title = "新对话"
    conv.title = fallback_title
    return fallback_title


# Request/Response Models
class ConversationCreate(BaseModel):
    title: Optional[str] = None
    model: Optional[str] = None
    use_voting: bool = False


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    model: Optional[str] = None
    use_voting: Optional[bool] = None
    context_window: Optional[int] = None


class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    model: Optional[str]
    use_voting: bool
    summary: Optional[str]
    message_count: int
    context_window: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    model: Optional[str]
    tokens_used: Optional[int]
    sources: List[dict]
    voting_results: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    conv = Conversation(
        id=uuid4(),
        user_id=DEFAULT_USER_ID,
        title=data.title or "新对话",
        model=data.model,
        use_voting=data.use_voting,
        message_count=0,
        context_window=10,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    
    return ConversationResponse(
        id=str(conv.id),
        title=conv.title,
        model=conv.model,
        use_voting=conv.use_voting,
        summary=conv.summary,
        message_count=conv.message_count or 0,
        context_window=conv.context_window or 10,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all conversations for the current user"""
    # Count total
    count_query = select(func.count()).select_from(Conversation).where(
        Conversation.user_id == DEFAULT_USER_ID
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated list
    offset = (page - 1) * page_size
    query = (
        select(Conversation)
        .where(Conversation.user_id == DEFAULT_USER_ID)
        .order_by(desc(Conversation.last_message_at), desc(Conversation.created_at))
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    conversations = result.scalars().all()
    for conversation in conversations:
        original_title = conversation.title
        resolved_title = await _resolve_conversation_title(db, conversation)
        if resolved_title != original_title:
            conversation.title = resolved_title
    
    return ConversationListResponse(
        conversations=[
            ConversationResponse(
                id=str(c.id),
                title=c.title,
                model=c.model,
                use_voting=c.use_voting,
                summary=c.summary,
                message_count=c.message_count or 0,
                context_window=c.context_window or 10,
                last_message_at=c.last_message_at,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in conversations
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation"""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == DEFAULT_USER_ID
    )
    result = await db.execute(query)
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    original_title = conv.title
    resolved_title = await _resolve_conversation_title(db, conv)
    if resolved_title != original_title:
        conv.title = resolved_title
    
    return ConversationResponse(
        id=str(conv.id),
        title=resolved_title,
        model=conv.model,
        use_voting=conv.use_voting,
        summary=conv.summary,
        message_count=conv.message_count or 0,
        context_window=conv.context_window or 10,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    data: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a conversation"""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == DEFAULT_USER_ID
    )
    result = await db.execute(query)
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Update fields
    if data.title is not None:
        conv.title = data.title
    if data.model is not None:
        conv.model = data.model
    if data.use_voting is not None:
        conv.use_voting = data.use_voting
    if data.context_window is not None:
        conv.context_window = data.context_window
    
    await db.commit()
    await db.refresh(conv)
    
    return ConversationResponse(
        id=str(conv.id),
        title=conv.title,
        model=conv.model,
        use_voting=conv.use_voting,
        summary=conv.summary,
        message_count=conv.message_count or 0,
        context_window=conv.context_window or 10,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == DEFAULT_USER_ID
    )
    result = await db.execute(query)
    conv = result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.delete(conv)
    await db.commit()
    
    return {"message": "Conversation deleted", "id": str(conversation_id)}


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a specific conversation"""
    # Verify conversation exists and belongs to user
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == DEFAULT_USER_ID
    )
    conv_result = await db.execute(conv_query)
    if not conv_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=str(m.id),
            role=m.role.value,
            content=m.content,
            model=m.model,
            tokens_used=m.tokens_used,
            sources=m.sources or [],
            voting_results=m.voting_results,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.get("/{conversation_id}/context")
async def get_conversation_context(
    conversation_id: UUID,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get recent messages for context window"""
    # Verify and get conversation
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == DEFAULT_USER_ID
    )
    conv_result = await db.execute(conv_query)
    conv = conv_result.scalar_one_or_none()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Use conversation's context_window if limit not specified
    window_size = limit or conv.context_window or 10
    
    # Get recent messages
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .limit(window_size)
    )
    result = await db.execute(query)
    messages = list(reversed(result.scalars().all()))
    
    return {
        "conversation_id": str(conversation_id),
        "context_window": window_size,
        "messages": [
            {
                "role": m.role.value,
                "content": m.content,
            }
            for m in messages
        ]
    }

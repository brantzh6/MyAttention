"""
Chat Router - Conversation and AI Chat API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import time
import sys
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from brains.control_plane import build_execution_plan
from llm.adapter import LLMAdapter
from llm.voting import MultiModelVoting
from llm.router import TaskRouter, TaskType
from rag import get_rag_engine
from knowledge import get_kb_manager
from db import get_db, Conversation, Message, MessageRole

router = APIRouter()


import os
import logging

_chat_logger = logging.getLogger("myattention.chat")
_chat_logger.setLevel(logging.DEBUG)
if not _chat_logger.handlers:
    import sys as _sys
    _h = logging.StreamHandler(_sys.stdout)
    _h.setFormatter(logging.Formatter("[%(asctime)s] [chat] %(message)s", datefmt="%H:%M:%S"))
    _h.setLevel(logging.DEBUG)
    _chat_logger.addHandler(_h)
    _log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chat_debug.log")
    _fh = logging.FileHandler(_log_file, encoding="utf-8")
    _fh.setFormatter(logging.Formatter("[%(asctime)s] [chat] %(message)s", datefmt="%H:%M:%S"))
    _fh.setLevel(logging.DEBUG)
    _chat_logger.addHandler(_fh)


def log(msg: str):
    _chat_logger.info(msg)

# Default user ID (will be replaced with auth later)
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    use_voting: bool = False
    use_rag: bool = True  # Enable RAG by default
    enable_search: bool = False  # Enable web search for supported models
    enable_thinking: bool = False  # Enable thinking/reasoning mode
    provider: Optional[str] = None  # LLM provider (qwen, glm, kimi, etc.)
    model: Optional[str] = None  # Specific model to use
    voting_models: Optional[List[str]] = None  # Models for voting mode
    kb_ids: Optional[List[str]] = None  # Knowledge base IDs to search (None = all)


class ChatSource(BaseModel):
    title: str
    url: str
    source: str = ""
    score: float = 0.0


class ChatResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: List[ChatSource] = []
    voting_results: Optional[List[dict]] = None


async def get_or_create_conversation(
    db: AsyncSession, 
    conversation_id: Optional[str],
    use_voting: bool = False
) -> Conversation:
    """Get existing conversation or create a new one"""
    if conversation_id:
        try:
            conv_uuid = UUID(conversation_id)
            query = select(Conversation).where(
                Conversation.id == conv_uuid,
                Conversation.user_id == DEFAULT_USER_ID
            )
            result = await db.execute(query)
            conv = result.scalar_one_or_none()
            if conv:
                return conv
        except ValueError:
            pass  # Invalid UUID, create new
    
    # Create new conversation
    conv = Conversation(
        id=uuid4(),
        user_id=DEFAULT_USER_ID,
        title="新对话",
        use_voting=use_voting,
        message_count=0,
        context_window=10,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def save_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    model: Optional[str] = None,
    sources: Optional[List[dict]] = None,
    voting_results: Optional[dict] = None,
    tokens_used: Optional[int] = None,
    extra: Optional[dict] = None,
) -> Message:
    """Save a message to the database"""
    msg = Message(
        id=uuid4(),
        conversation_id=conversation_id,
        role=role,
        content=content,
        model=model,
        sources=sources or [],
        voting_results=voting_results,
        tokens_used=tokens_used,
        extra=extra or {},
    )
    db.add(msg)
    
    # Update conversation stats
    await db.execute(
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(
            message_count=Conversation.message_count + 1,
            last_message_at=datetime.utcnow(),
        )
    )
    
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_context_messages(
    db: AsyncSession,
    conversation_id: UUID,
    limit: int = 10
) -> List[dict]:
    """Get recent messages for context"""
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    messages = list(reversed(result.scalars().all()))
    
    return [
        {"role": m.role.value, "content": m.content}
        for m in messages
    ]


async def generate_conversation_title(content: str) -> str:
    """Generate a title from the first message"""
    title = content[:50].strip()
    if len(content) > 50:
        title += "..."
    return title


def _brain_plan_payload(plan) -> dict:
    return {
        "route_id": plan.route_id,
        "problem_type": plan.problem_type,
        "thinking_framework": plan.thinking_framework,
        "primary_brain": plan.primary_brain,
        "supporting_brains": plan.supporting_brains,
        "review_brain": plan.review_brain,
        "fallback_brain": plan.fallback_brain,
        "primary_models": plan.primary_models,
        "supporting_models": plan.supporting_models,
        "selected_models": plan.selected_models,
        "execution_mode": plan.execution_mode,
        "surface": plan.surface,
    }


@router.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Chat endpoint with RAG and optional multi-model voting.
    All blocking operations are inside generate() to enable real-time status updates.
    """
    adapter = LLMAdapter()
    task_router = TaskRouter()
    
    async def generate():
        t_start = time.time()
        full_response = ""
        sources = []
        model_used = None
        conversation_id = None
        context_messages = []
        voting_data = None  # Store voting individual results
        brain_plan = None
        
        try:
            # === Phase 1: Immediate connection confirmation ===
            yield f"data: {json.dumps({'status': '已连接后端服务'}, ensure_ascii=False)}\n\n"
            log(f"请求开始: message={request.message[:50]}..., model={request.model}, search={request.enable_search}, thinking={request.enable_thinking}, voting={request.use_voting}")
            
            # === Phase 2: Database - create/get conversation ===
            t_db = time.time()
            yield f"data: {json.dumps({'status': '正在准备会话...'}, ensure_ascii=False)}\n\n"
            
            conv = await get_or_create_conversation(db, request.conversation_id, request.use_voting)
            conversation_id = conv.id
            is_first_message = (conv.message_count or 0) == 0
            log(f"会话准备完成: conv_id={conversation_id}, 耗时={time.time()-t_db:.2f}s")
            
            # Send conversation_id immediately
            yield f"data: {json.dumps({'conversation_id': str(conversation_id), 'search_enabled': request.enable_search}, ensure_ascii=False)}\n\n"

            brain_plan = await build_execution_plan(
                db,
                problem_type="interactive_dialog",
                surface="chat",
                use_voting=request.use_voting,
                enable_search=request.enable_search,
                enable_thinking=request.enable_thinking,
                requested_model=request.model if request.provider and request.model else None,
            )
            yield f"data: {json.dumps({'brain_plan': _brain_plan_payload(brain_plan)}, ensure_ascii=False)}\n\n"
            
            # === Phase 3: Save user message ===
            t_save = time.time()
            await save_message(
                db=db,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=request.message,
            )
            log(f"用户消息保存完成: 耗时={time.time()-t_save:.2f}s")
            
            # Update title if first message
            if is_first_message:
                title = await generate_conversation_title(request.message)
                await db.execute(
                    update(Conversation)
                    .where(Conversation.id == conversation_id)
                    .values(title=title)
                )
                await db.commit()
            
            # Get conversation context
            context_messages = await get_context_messages(db, conversation_id, conv.context_window or 10)
            log(f"数据库操作总耗时: {time.time()-t_db:.2f}s, 上下文消息数: {len(context_messages)}")
            
            # === Phase 4: RAG retrieval using KBManager ===
            context = ""
            sources = []
            if request.use_rag:
                t_rag = time.time()
                kb_ids_to_search = request.kb_ids if request.kb_ids else None
                if kb_ids_to_search:
                    yield f"data: {json.dumps({'status': f'正在检索知识库: {len(kb_ids_to_search)} 个...'}, ensure_ascii=False)}\n\n"
                else:
                    yield f"data: {json.dumps({'status': '正在检索所有知识库...'}, ensure_ascii=False)}\n\n"
                try:
                    kb_manager = get_kb_manager()
                    log(f"KBManager获取完成: 耗时={time.time()-t_rag:.2f}s")

                    # Get all KBs if not specified
                    if kb_ids_to_search is None:
                        kbs = await kb_manager.list_knowledge_bases()
                        kb_ids_to_search = [kb.id for kb in kbs]

                    # Search each KB and collect results
                    all_results = []
                    for kb_id in kb_ids_to_search:
                        try:
                            # Lower score_threshold to 0.3 to get more results
                            results = await kb_manager.search(
                                query=request.message,
                                kb_id=kb_id,
                                limit=5,
                                score_threshold=0.3
                            )
                            if results:
                                log(f"KB {kb_id} 找到 {len(results)} 个结果")
                            all_results.extend(results)
                        except Exception as e:
                            log(f"搜索知识库 {kb_id} 失败: {e}")

                    # Sort by score and take top results
                    all_results.sort(key=lambda x: x.score, reverse=True)
                    top_results = all_results[:10]

                    log(f"KB检索完成: 耗时={time.time()-t_rag:.2f}s, 总结果={len(all_results)}, top={len(top_results)}")

                    # Build context from results
                    context_parts = []
                    for result in top_results:
                        doc = result.document
                        context_parts.append(f"【来源: {doc.source} (知识库: {doc.kb_id})】\n{doc.content[:500]}")
                        sources.append({
                            "title": doc.title or doc.source,
                            "url": doc.url,
                            "source": doc.source,
                            "score": round(result.score, 3),
                        })

                    if context_parts:
                        context = "\n\n---\n\n".join(context_parts)

                except Exception as e:
                    log(f"KB检索失败: {e}, 耗时={time.time()-t_rag:.2f}s")
                    context = ""
                    sources = []
            
            # Build system prompt with context
            system_prompt = "你是 MyAttention 智能助手，帮助用户获取、整理和分析信息，支持重大决策。"
            if context:
                system_prompt += f"\n\n以下是相关的知识库内容，请基于这些信息回答用户问题:\n\n{context}"
            
            log(f"准备阶段总耗时: {time.time()-t_start:.2f}s, 进入模型调用阶段")
            
            # === Phase 5: Model invocation ===
            if request.use_voting:
                voting_models = None
                if request.voting_models:
                    voting_models = request.voting_models
                elif brain_plan and brain_plan.selected_models:
                    voting_models = brain_plan.selected_models
                # Let MultiModelVoting handle model selection based on search/thinking capability
                
                voting = MultiModelVoting(
                    models=voting_models,
                    enable_search=request.enable_search,
                    enable_thinking=request.enable_thinking,
                )
                t_vote = time.time()
                async for event in voting.vote_stream(request.message, system_prompt=system_prompt):
                    event["sources"] = sources
                    event["search_enabled"] = request.enable_search
                    if event.get("type") == "voting_result":
                        full_response = event.get("consensus", "")
                        voting_data = {
                            "individual_results": event.get("individual_results", []),
                            "confidence": event.get("confidence", 0),
                            "summary": event.get("summary", {}),
                        }
                        log(f"投票完成: 耗时={time.time()-t_vote:.2f}s")
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            else:
                # Use user-specified provider/model or fall back to task router
                if request.provider and request.model:
                    use_provider = request.provider
                    use_model = request.model
                elif brain_plan and brain_plan.selected_models:
                    use_provider = "qwen"
                    use_model = brain_plan.selected_models[0]
                else:
                    task_type = task_router.classify_task(request.message)
                    model_config = task_router.get_model_config(task_type)
                    use_provider = model_config.provider
                    use_model = model_config.model
                
                model_used = use_model
                
                if use_provider == "voting":
                    voting = MultiModelVoting(
                        enable_search=request.enable_search,
                        enable_thinking=request.enable_thinking,
                    )
                    t_vote = time.time()
                    async for event in voting.vote_stream(request.message, system_prompt=system_prompt):
                        event["sources"] = sources
                        event["search_enabled"] = request.enable_search
                        if event.get("type") == "voting_result":
                            full_response = event.get("consensus", "")
                            voting_data = {
                                "individual_results": event.get("individual_results", []),
                                "confidence": event.get("confidence", 0),
                                "summary": event.get("summary", {}),
                            }
                            log(f"投票完成: 耗时={time.time()-t_vote:.2f}s")
                        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                else:
                    # Send model calling status with details
                    search_hint = " | 联网搜索" if request.enable_search else ""
                    thinking_hint = " | 深度思考" if request.enable_thinking else ""
                    yield f"data: {json.dumps({'status': f'正在调用 {use_model}{search_hint}{thinking_hint}...'}, ensure_ascii=False)}\n\n"
                    
                    t_model = time.time()
                    t_first_token = None
                    log(f"开始调用模型: provider={use_provider}, model={use_model}, search={request.enable_search}, thinking={request.enable_thinking}")
                    
                    first_chunk = True
                    async for chunk in adapter.stream_chat(
                        message=request.message,
                        provider=use_provider,
                        model=use_model,
                        system_prompt=system_prompt,
                        history=context_messages[:-1] if context_messages else [],
                        enable_search=request.enable_search,
                        enable_thinking=request.enable_thinking,
                    ):
                        if t_first_token is None:
                            t_first_token = time.time()
                            log(f"首token延迟: {t_first_token - t_model:.2f}s")
                        
                        # Separate thinking content from regular content
                        is_thinking = chunk.startswith("__THINKING__")
                        actual_chunk = chunk.replace("__THINKING__", "") if is_thinking else chunk
                        
                        if is_thinking:
                            # Only forward thinking content if user enabled thinking mode
                            if request.enable_thinking:
                                yield f"data: {json.dumps({'thinking': actual_chunk}, ensure_ascii=False)}\n\n"
                            # else: silently discard thinking chunks
                        else:
                            full_response += actual_chunk
                            if first_chunk and sources:
                                yield f"data: {json.dumps({'content': actual_chunk, 'sources': sources, 'model': use_model, 'search_enabled': request.enable_search, 'brain_plan': _brain_plan_payload(brain_plan) if brain_plan else None}, ensure_ascii=False)}\n\n"
                                first_chunk = False
                            else:
                                payload = {'content': actual_chunk}
                                if first_chunk and brain_plan:
                                    payload['brain_plan'] = _brain_plan_payload(brain_plan)
                                    payload['model'] = use_model
                                    payload['search_enabled'] = request.enable_search
                                    first_chunk = False
                                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    
                    log(f"模型调用完成: 耗时={time.time()-t_model:.2f}s, 响应长度={len(full_response)}")
            
            yield "data: [DONE]\n\n"
            log(f"请求总耗时: {time.time()-t_start:.2f}s")
            
        except Exception as e:
            log(f"错误: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            full_response = f"Error: {str(e)}"
        
        # Save assistant response
        if conversation_id:
            try:
                log(f"开始保存助手消息: conv_id={conversation_id}, content_len={len(full_response)}, voting={'yes' if voting_data else 'no'}")
                await save_message(
                    db=db,
                    conversation_id=conversation_id,
                    role=MessageRole.ASSISTANT,
                    content=full_response,
                    model=model_used or ("voting" if voting_data else None),
                    sources=[{"title": s.get("title", ""), "url": s.get("url", ""), "source": s.get("source", ""), "score": s.get("score", 0)} for s in sources] if sources else [],
                    voting_results=voting_data,
                    extra={
                        "brain_plan": _brain_plan_payload(brain_plan) if brain_plan else None,
                        "search_enabled": request.enable_search,
                        "thinking_enabled": request.enable_thinking,
                    },
                )
                log(f"助手消息保存成功")
            except Exception as e:
                log(f"保存助手消息失败: {e}")
                import traceback
                traceback.print_exc()
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

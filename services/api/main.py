# Windows 上设置事件循环策略，解决 Playwright subprocess 问题
import sys
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
import os
from pathlib import Path

from routers import brains, chat, feeds, models, settings, rag, conversations, memories, system, evolution, testing, feishu


def configure_runtime_logging() -> None:
    log_path = Path(__file__).resolve().parent / "api.log"
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not any(isinstance(handler, logging.FileHandler) and getattr(handler, "baseFilename", None) == str(log_path) for handler in root_logger.handlers):
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        if not any(isinstance(handler, logging.FileHandler) and getattr(handler, "baseFilename", None) == str(log_path) for handler in logger.handlers):
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)


configure_runtime_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - pre-warm expensive resources
    print("Starting MyAttention API...")

    # 预加载 RAG
    print("  Pre-loading RAG engine and embedding model...")
    try:
        from rag import get_rag_engine
        engine = get_rag_engine()
        # Force load the SentenceTransformer model (lazy property)
        _ = engine.encoder
        print("  RAG engine ready.")
    except Exception as e:
        print(f"  RAG engine pre-load failed (non-fatal): {e}")

    # 预加载 LLM
    print("  Pre-loading LLM adapter...")
    try:
        from llm.adapter import LLMAdapter
        adapter = LLMAdapter()  # Initialize singleton providers
        # Pre-warm the httpx client for Qwen (TLS handshake)
        qwen = adapter.providers.get("qwen")
        if qwen and hasattr(qwen, '_get_client'):
            qwen._get_client()
        print("  LLM adapter ready.")
    except Exception as e:
        print(f"  LLM adapter pre-load failed (non-fatal): {e}")

    # 启动自动进化系统
    print("  Starting Auto Evolution System...")
    try:
        from feeds.auto_evolution import start_auto_evolution
        from llm.adapter import LLMAdapter

        # 获取 LLM 客户端传给 AI 大脑
        adapter = LLMAdapter()
        llm_client = adapter.get_provider("qwen")  # 使用默认的 Qwen

        await start_auto_evolution(llm_client)
        print("  Auto Evolution System started.")
    except Exception as e:
        print(f"  Auto Evolution System failed (non-fatal): {e}")

    # Initialize notification manager from settings
    try:
        from notifications import get_notification_manager
        from config import get_settings
        settings = get_settings()
        manager = get_notification_manager()

        # 配置飞书 - 支持 Webhook 或 App API 模式
        if settings.feishu_app_id and settings.feishu_app_secret:
            # App API 模式（推荐，支持更多功能）
            manager.configure_feishu_app(
                app_id=settings.feishu_app_id,
                app_secret=settings.feishu_app_secret,
                default_target_id=settings.feishu_default_target_id
            )
            print("  Feishu notifications configured (App API mode).")
        elif settings.feishu_webhook_url:
            # Webhook 模式
            manager.configure_feishu(webhook_url=settings.feishu_webhook_url)
            print("  Feishu notifications configured (Webhook mode).")

        # 配置钉钉
        if settings.dingtalk_webhook_url:
            manager.configure_dingtalk(
                settings.dingtalk_webhook_url,
                settings.dingtalk_secret
            )
            print("  DingTalk notifications configured.")
    except Exception as e:
        print(f"  Notification setup failed (non-fatal): {e}")
    
    # Start pipeline scheduler as background task
    pipeline_task = None
    if os.environ.get("DISABLE_PIPELINE") != "1":
        try:
            from pipeline import PipelineScheduler
            api_port = os.environ.get("API_PORT", "8000")
            scheduler = PipelineScheduler(
                api_base=f"http://localhost:{api_port}",
                high_priority_interval=300,   # 5 min
                full_interval=1800,           # 30 min
            )
            pipeline_task = asyncio.create_task(scheduler.run())
            app.state.pipeline_scheduler = scheduler
            print("  Pipeline scheduler started.")
        except Exception as e:
            print(f"  Pipeline scheduler failed (non-fatal): {e}")
    else:
        print("  Pipeline scheduler disabled (DISABLE_PIPELINE=1).")

    print("MyAttention API ready.")
    yield
    # Shutdown
    print("Shutting down MyAttention API...")

    # 停止自动进化系统
    try:
        from feeds.auto_evolution import stop_auto_evolution
        await stop_auto_evolution()
        print("  Auto Evolution System stopped.")
    except Exception as e:
        print(f"  Failed to stop Auto Evolution: {e}")

    if pipeline_task:
        app.state.pipeline_scheduler.stop()
        pipeline_task.cancel()
        try:
            await pipeline_task
        except asyncio.CancelledError:
            pass
        print("  Pipeline scheduler stopped.")

app = FastAPI(
    title="MyAttention API",
    description="AI-driven intelligent decision support system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(feeds.router, prefix="/api", tags=["feeds"])
app.include_router(models.router, prefix="/api/llm", tags=["llm"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(memories.router, prefix="/api/memories", tags=["memories"])
app.include_router(system.router, prefix="/api", tags=["system"])
app.include_router(evolution.router, prefix="/api/evolution", tags=["self-evolution"])
app.include_router(testing.router, prefix="/api/testing", tags=["ai-testing"])
app.include_router(feishu.router, prefix="/api", tags=["feishu"])
app.include_router(brains.router, prefix="/api/brains", tags=["brains"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/api/pipeline/stats")
async def pipeline_stats():
    """Get pipeline scheduler status and statistics."""
    scheduler = getattr(app.state, "pipeline_scheduler", None)
    if not scheduler:
        return {"status": "disabled"}
    return {
        "status": "running" if scheduler._running else "stopped",
        **scheduler.stats,
    }


@app.post("/api/pipeline/trigger")
async def pipeline_trigger():
    """Manually trigger a pipeline run."""
    scheduler = getattr(app.state, "pipeline_scheduler", None)
    if not scheduler:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Pipeline scheduler not running")
    result = await scheduler.run_once(priority="all", push=True)
    return result


@app.post("/api/pipeline/digest")
async def trigger_digest(digest_type: str = "daily"):
    """Manually trigger a digest notification."""
    scheduler = getattr(app.state, "pipeline_scheduler", None)
    if not scheduler:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Pipeline scheduler not running")
    result = await scheduler._send_digest(digest_type)
    return result


@app.get("/")
async def root():
    return {"message": "MyAttention API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings
from qdrant_client import QdrantClient


_qdrant_clients: dict[str, QdrantClient] = {}


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://myattention:myattention@localhost:5432/myattention"
    redis_url: str = "redis://localhost:6379"
    qdrant_url: str = "http://localhost:6333"
    qdrant_local_path: str = "./data/qdrant"
    object_store_backend: str = "local"
    object_store_local_path: str = "./data/object_store"
    feeds_read_backend: str = "hybrid"
    
    # LLM API Keys
    qwen_api_key: str = ""
    qwen_base_url: str = ""
    glm_api_key: str = ""
    kimi_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    
    # Notifications - Feishu
    feishu_webhook_url: str = ""  # Webhook 模式
    feishu_app_id: str = ""  # 应用 API 模式
    feishu_app_secret: str = ""
    feishu_default_target_id: str = ""  # 默认推送目标（群 oc_xxx 或用户 ou_xxx）

    # Notifications - DingTalk
    dingtalk_webhook_url: str = ""
    dingtalk_secret: str = ""  # For HMAC signing
    
    # App settings
    debug: bool = True
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_effective_qwen_base_url(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    configured = (settings.qwen_base_url or "").strip()
    if configured:
        return configured.rstrip("/")

    api_key = (settings.qwen_api_key or "").strip()
    if api_key.startswith("sk-sp-"):
        return "https://coding.dashscope.aliyuncs.com/v1"

    return "https://dashscope.aliyuncs.com/compatible-mode/v1"


def get_effective_qwen_default_model(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    base_url = get_effective_qwen_base_url(settings)
    if "coding.dashscope.aliyuncs.com" in base_url:
        return "qwen3.6-plus"
    return "qwen-max"


def create_qdrant_client(settings: Settings | None = None) -> QdrantClient:
    """
    Build a Qdrant client that can use either an HTTP server or local storage.

    If `qdrant_url` is empty or starts with `local://`, Qdrant runs in embedded
    mode backed by `qdrant_local_path`.
    """
    settings = settings or get_settings()
    qdrant_url = (settings.qdrant_url or "").strip()

    if not qdrant_url or qdrant_url.startswith("local://"):
        qdrant_path = Path(settings.qdrant_local_path).expanduser().resolve()
        qdrant_path.mkdir(parents=True, exist_ok=True)
        client_key = f"path:{qdrant_path}"
        if client_key not in _qdrant_clients:
            _qdrant_clients[client_key] = QdrantClient(path=str(qdrant_path))
        return _qdrant_clients[client_key]

    client_key = f"url:{qdrant_url}"
    if client_key not in _qdrant_clients:
        _qdrant_clients[client_key] = QdrantClient(url=qdrant_url, check_compatibility=False)
    return _qdrant_clients[client_key]


def is_local_qdrant_mode(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    qdrant_url = (settings.qdrant_url or "").strip()
    return not qdrant_url or qdrant_url.startswith("local://")

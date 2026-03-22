from enum import Enum
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import get_settings

router = APIRouter()


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ModelCapability(str, Enum):
    WEB_SEARCH = "web_search"
    LONG_CONTEXT = "long_context"
    CODE_GEN = "code_gen"
    REASONING = "reasoning"
    VISION = "vision"
    TOOL_USE = "tool_use"


class LLMProviderBase(BaseModel):
    name: str
    provider: str
    model: str
    enabled: bool = True
    priority: Priority = Priority.MEDIUM


class LLMProvider(LLMProviderBase):
    id: str
    api_key_set: bool = False
    use_case: List[str] = []
    capabilities: List[ModelCapability] = []


class APIKeyUpdate(BaseModel):
    api_key: str


class VotingConfig(BaseModel):
    enabled: bool = True
    models: List[str] = []
    consensus_threshold: float = 0.67


def _build_providers() -> List[LLMProvider]:
    settings = get_settings()
    qwen_ready = bool((settings.qwen_api_key or "").strip())
    anthropic_ready = bool((settings.anthropic_api_key or "").strip())
    openai_ready = bool((settings.openai_api_key or "").strip())
    ollama_ready = bool((settings.ollama_base_url or "").strip())

    return [
        LLMProvider(
            id="1",
            name="通义千问 Max",
            provider="qwen",
            model="qwen-max",
            enabled=qwen_ready,
            api_key_set=qwen_ready,
            priority=Priority.HIGH,
            use_case=["摘要", "中文对话", "创意写作"],
            capabilities=[ModelCapability.WEB_SEARCH, ModelCapability.TOOL_USE, ModelCapability.REASONING],
        ),
        LLMProvider(
            id="2",
            name="Qwen 3.5 Plus",
            provider="qwen",
            model="qwen3.5-plus",
            enabled=qwen_ready,
            api_key_set=qwen_ready,
            priority=Priority.HIGH,
            use_case=["通用对话", "联网搜索"],
            capabilities=[ModelCapability.WEB_SEARCH, ModelCapability.REASONING],
        ),
        LLMProvider(
            id="3",
            name="MiniMax M2.5",
            provider="qwen",
            model="MiniMax-M2.5",
            enabled=qwen_ready,
            api_key_set=qwen_ready,
            priority=Priority.HIGH,
            use_case=["通用对话", "联网搜索"],
            capabilities=[ModelCapability.WEB_SEARCH, ModelCapability.LONG_CONTEXT],
        ),
        LLMProvider(
            id="4",
            name="DeepSeek V3.2",
            provider="qwen",
            model="deepseek-v3.2",
            enabled=qwen_ready,
            api_key_set=qwen_ready,
            priority=Priority.HIGH,
            use_case=["代码生成", "深度推理", "联网搜索"],
            capabilities=[ModelCapability.WEB_SEARCH, ModelCapability.CODE_GEN, ModelCapability.REASONING],
        ),
        LLMProvider(
            id="5",
            name="GLM-5",
            provider="qwen",
            model="glm-5",
            enabled=qwen_ready,
            api_key_set=qwen_ready,
            priority=Priority.MEDIUM,
            use_case=["简单问答", "快速响应"],
            capabilities=[ModelCapability.TOOL_USE],
        ),
        LLMProvider(
            id="6",
            name="Kimi K2.5",
            provider="qwen",
            model="kimi-k2.5",
            enabled=qwen_ready,
            api_key_set=qwen_ready,
            priority=Priority.MEDIUM,
            use_case=["长文本处理"],
            capabilities=[ModelCapability.LONG_CONTEXT],
        ),
        LLMProvider(
            id="7",
            name="Claude 3.5",
            provider="anthropic",
            model="claude-3-5-sonnet",
            enabled=anthropic_ready,
            api_key_set=anthropic_ready,
            priority=Priority.MEDIUM,
            use_case=["深度推理", "代码生成"],
            capabilities=[ModelCapability.REASONING, ModelCapability.CODE_GEN, ModelCapability.VISION, ModelCapability.TOOL_USE],
        ),
        LLMProvider(
            id="8",
            name="GPT-4o",
            provider="openai",
            model="gpt-4o",
            enabled=openai_ready,
            api_key_set=openai_ready,
            priority=Priority.MEDIUM,
            use_case=["综合任务"],
            capabilities=[ModelCapability.REASONING, ModelCapability.CODE_GEN, ModelCapability.VISION, ModelCapability.TOOL_USE],
        ),
        LLMProvider(
            id="9",
            name="Ollama 本地",
            provider="ollama",
            model="qwen2:7b",
            enabled=ollama_ready,
            api_key_set=True,
            priority=Priority.LOW,
            use_case=["离线使用", "隐私优先"],
            capabilities=[],
        ),
    ]


_voting_config = VotingConfig(
    enabled=True,
    models=["2", "3", "4"],
    consensus_threshold=0.67,
)


@router.get("/providers", response_model=List[LLMProvider])
async def get_providers():
    return _build_providers()


@router.put("/providers/{provider_id}/api-key")
async def update_api_key(provider_id: str, data: APIKeyUpdate):
    raise HTTPException(status_code=501, detail="API key updates must be made in server environment configuration")


@router.put("/providers/{provider_id}/toggle")
async def toggle_provider(provider_id: str):
    raise HTTPException(status_code=501, detail="Provider toggles are derived from server configuration in this runtime")


@router.get("/voting", response_model=VotingConfig)
async def get_voting_config():
    return _voting_config


@router.put("/voting")
async def update_voting_config(config: VotingConfig):
    global _voting_config
    _voting_config = config
    return {"status": "updated"}


@router.get("/routing")
async def get_routing_config():
    return {
        "simple_qa": {"model": "qwen-max", "fallback": "ollama:qwen2:7b"},
        "summarization": {"model": "qwen-max", "fallback": "ollama:qwen2:7b"},
        "deep_analysis": {"model": "claude-3-5-sonnet", "fallback": "qwen-max"},
        "long_context": {"model": "kimi-k2.5", "fallback": "qwen-max"},
        "code_generation": {"model": "deepseek-v3.2", "fallback": "qwen-max"},
        "critical_decision": {"mode": "voting", "models": _voting_config.models},
    }

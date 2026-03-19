from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

router = APIRouter()


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ModelCapability(str, Enum):
    """Model capabilities/features"""
    WEB_SEARCH = "web_search"       # Built-in web search
    LONG_CONTEXT = "long_context"   # 100K+ context
    CODE_GEN = "code_gen"           # Strong code generation
    REASONING = "reasoning"         # Deep reasoning
    VISION = "vision"               # Image understanding
    TOOL_USE = "tool_use"           # Function calling


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
    capabilities: List[ModelCapability] = []  # Model capabilities


class APIKeyUpdate(BaseModel):
    api_key: str


class VotingConfig(BaseModel):
    enabled: bool = True
    models: List[str] = []
    consensus_threshold: float = 0.67


# Mock data store
_providers: List[LLMProvider] = [
    LLMProvider(
        id="1",
        name="通义千问 Max",
        provider="qwen",
        model="qwen-max",
        enabled=True,
        api_key_set=True,
        priority=Priority.HIGH,
        use_case=["摘要", "中文对话", "创意写作"],
        capabilities=[ModelCapability.WEB_SEARCH, ModelCapability.TOOL_USE, ModelCapability.REASONING],
    ),
    LLMProvider(
        id="2",
        name="Qwen 3.5 Plus",
        provider="qwen",
        model="qwen3.5-plus",
        enabled=True,
        api_key_set=True,
        priority=Priority.HIGH,
        use_case=["通用对话", "联网搜索"],
        capabilities=[ModelCapability.WEB_SEARCH, ModelCapability.REASONING],
    ),
    LLMProvider(
        id="3",
        name="MiniMax M2.5",
        provider="qwen",
        model="minimax-m2.5",
        enabled=True,
        api_key_set=True,
        priority=Priority.HIGH,
        use_case=["通用对话", "联网搜索"],
        capabilities=[ModelCapability.WEB_SEARCH, ModelCapability.LONG_CONTEXT],
    ),
    LLMProvider(
        id="4",
        name="DeepSeek V3.2",
        provider="qwen",
        model="deepseek-v3.2",
        enabled=True,
        api_key_set=True,
        priority=Priority.HIGH,
        use_case=["代码生成", "深度推理", "联网搜索"],
        capabilities=[ModelCapability.WEB_SEARCH, ModelCapability.CODE_GEN, ModelCapability.REASONING],
    ),
    LLMProvider(
        id="5",
        name="GLM-5",
        provider="qwen",
        model="glm-5",
        enabled=True,
        api_key_set=True,
        priority=Priority.MEDIUM,
        use_case=["简单问答", "快速响应"],
        capabilities=[ModelCapability.TOOL_USE],
    ),
    LLMProvider(
        id="6",
        name="Kimi K2.5",
        provider="qwen",
        model="kimi-k2.5",
        enabled=True,
        api_key_set=True,
        priority=Priority.MEDIUM,
        use_case=["长文本处理"],
        capabilities=[ModelCapability.LONG_CONTEXT],
    ),
    LLMProvider(
        id="7",
        name="Claude 3.5",
        provider="anthropic",
        model="claude-3-5-sonnet",
        enabled=True,
        api_key_set=True,
        priority=Priority.MEDIUM,
        use_case=["深度推理", "代码生成"],
        capabilities=[ModelCapability.REASONING, ModelCapability.CODE_GEN, ModelCapability.VISION, ModelCapability.TOOL_USE],
    ),
    LLMProvider(
        id="8",
        name="GPT-4o",
        provider="openai",
        model="gpt-4o",
        enabled=False,
        api_key_set=False,
        priority=Priority.MEDIUM,
        use_case=["综合任务"],
        capabilities=[ModelCapability.REASONING, ModelCapability.CODE_GEN, ModelCapability.VISION, ModelCapability.TOOL_USE],
    ),
    LLMProvider(
        id="9",
        name="Ollama 本地",
        provider="ollama",
        model="qwen2:7b",
        enabled=False,
        api_key_set=True,
        priority=Priority.LOW,
        use_case=["离线使用", "隐私优先"],
        capabilities=[],
    ),
]

_voting_config = VotingConfig(
    enabled=True,
    models=["1", "4", "5"],
    consensus_threshold=0.67,
)


@router.get("/providers", response_model=List[LLMProvider])
async def get_providers():
    """
    Get all LLM providers
    """
    return _providers


@router.put("/providers/{provider_id}/api-key")
async def update_api_key(provider_id: str, data: APIKeyUpdate):
    """
    Update API key for a provider
    """
    for provider in _providers:
        if provider.id == provider_id:
            # In real implementation, save to secure storage
            provider.api_key_set = bool(data.api_key)
            return {"status": "updated"}
    raise HTTPException(status_code=404, detail="Provider not found")


@router.put("/providers/{provider_id}/toggle")
async def toggle_provider(provider_id: str):
    """
    Toggle provider enabled status
    """
    for provider in _providers:
        if provider.id == provider_id:
            provider.enabled = not provider.enabled
            return {"status": "toggled", "enabled": provider.enabled}
    raise HTTPException(status_code=404, detail="Provider not found")


@router.get("/voting", response_model=VotingConfig)
async def get_voting_config():
    """
    Get voting configuration
    """
    return _voting_config


@router.put("/voting")
async def update_voting_config(config: VotingConfig):
    """
    Update voting configuration
    """
    global _voting_config
    _voting_config = config
    return {"status": "updated"}


@router.get("/routing")
async def get_routing_config():
    """
    Get task-model routing configuration
    """
    return {
        "simple_qa": {"model": "qwen-turbo", "fallback": "glm-4-flash"},
        "summarization": {"model": "qwen-max", "fallback": "minimax"},
        "deep_analysis": {"model": "claude-3-5-sonnet", "fallback": "gpt-4o"},
        "long_context": {"model": "kimi", "fallback": "minimax"},
        "code_generation": {"model": "claude-3-5-sonnet", "fallback": "gpt-4o"},
        "critical_decision": {"mode": "voting", "models": _voting_config.models},
    }

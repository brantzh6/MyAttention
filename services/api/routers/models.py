from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import get_settings, write_local_secret

router = APIRouter()


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LLMProviderBase(BaseModel):
    name: str
    provider: str
    model: str
    enabled: bool = True
    priority: Priority = Priority.MEDIUM
    base_url: str = ""
    api: str = "openai-completions"
    key_env: Optional[str] = None
    reasoning: bool = False
    input: List[str] = Field(default_factory=list)
    context_window: int = 0
    max_tokens: int = 0
    cost_input: float = 0
    cost_output: float = 0


class LLMProvider(LLMProviderBase):
    id: str
    api_key_set: bool = False
    use_case: List[str] = Field(default_factory=list)


class APIKeyUpdate(BaseModel):
    api_key: str


class VotingConfig(BaseModel):
    enabled: bool = True
    models: List[str] = Field(default_factory=list)
    consensus_threshold: float = 0.67


class ModelCatalogEntry(BaseModel):
    id: str
    name: str
    reasoning: bool = False
    input: List[str] = Field(default_factory=list)
    cost_input: float = 0
    cost_output: float = 0
    context_window: int = 0
    max_tokens: int = 0


class ProviderCatalogEntry(BaseModel):
    provider: str
    name: str
    base_url: str
    api: str
    key_env: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    use_case: List[str] = Field(default_factory=list)
    models: List[ModelCatalogEntry] = Field(default_factory=list)


PROVIDER_CATALOG: List[ProviderCatalogEntry] = [
    ProviderCatalogEntry(
        provider="bailian-coding-plan",
        name="Bailian Coding Plan",
        base_url="https://coding.dashscope.aliyuncs.com/v1",
        api="openai-completions",
        key_env="BAILIAN_CODING_PLAN_API_KEY",
        priority=Priority.HIGH,
        use_case=["编码", "规划", "多模型投票"],
        models=[
            ModelCatalogEntry(
                id="qwen3.6-plus",
                name="qwen3.6-plus",
                reasoning=True,
                input=["text", "image"],
                cost_input=2,
                cost_output=12,
                context_window=1_000_000,
                max_tokens=65_536,
            ),
            ModelCatalogEntry(
                id="qwen3.5-plus",
                name="qwen3.5-plus",
                reasoning=True,
                input=["text", "image"],
                cost_input=0.8,
                cost_output=4.8,
                context_window=1_000_000,
                max_tokens=65_536,
            ),
            ModelCatalogEntry(
                id="qwen3-max-2026-01-23",
                name="qwen3-max-2026-01-23",
                reasoning=True,
                input=["text"],
                cost_input=2.5,
                cost_output=10,
                context_window=81_920,
                max_tokens=32_768,
            ),
            ModelCatalogEntry(
                id="qwen3-coder-next",
                name="qwen3-coder-next",
                reasoning=False,
                input=["text"],
                cost_input=0,
                cost_output=0,
                context_window=262_144,
                max_tokens=65_536,
            ),
            ModelCatalogEntry(
                id="qwen3-coder-plus",
                name="qwen3-coder-plus",
                reasoning=False,
                input=["text"],
                cost_input=4,
                cost_output=16,
                context_window=1_000_000,
                max_tokens=65_536,
            ),
            ModelCatalogEntry(
                id="MiniMax-M2.5",
                name="MiniMax-M2.5",
                reasoning=True,
                input=["text"],
                cost_input=2.1,
                cost_output=8.4,
                context_window=196_608,
                max_tokens=32_768,
            ),
            ModelCatalogEntry(
                id="glm-5",
                name="glm-5",
                reasoning=True,
                input=["text"],
                cost_input=4,
                cost_output=18,
                context_window=202_752,
                max_tokens=16_384,
            ),
            ModelCatalogEntry(
                id="glm-4.7",
                name="glm-4.7",
                reasoning=True,
                input=["text"],
                cost_input=3,
                cost_output=16,
                context_window=169_984,
                max_tokens=16_384,
            ),
            ModelCatalogEntry(
                id="kimi-k2.5",
                name="kimi-k2.5",
                reasoning=True,
                input=["text", "image"],
                cost_input=4,
                cost_output=21,
                context_window=262_144,
                max_tokens=262_144,
            ),
        ],
    ),
    ProviderCatalogEntry(
        provider="bailian",
        name="Bailian",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api="openai-completions",
        key_env="BAILIAN_API_KEY",
        priority=Priority.HIGH,
        use_case=["通用对话", "快速响应"],
        models=[
            ModelCatalogEntry(
                id="qwen3.6-plus",
                name="qwen3.6-plus",
                reasoning=True,
                input=["text", "image"],
                cost_input=2,
                cost_output=12,
                context_window=1_000_000,
                max_tokens=65_536,
            )
        ],
    ),
    ProviderCatalogEntry(
        provider="qwen",
        name="Qwen",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api="openai-completions",
        key_env="QWEN_API_KEY",
        priority=Priority.HIGH,
        use_case=["摘要", "对话", "创意写作"],
        models=[
            ModelCatalogEntry(
                id="qwen-max",
                name="qwen-max",
                reasoning=False,
                input=["text", "image"],
                cost_input=0,
                cost_output=0,
                context_window=131_072,
                max_tokens=32_768,
            ),
            ModelCatalogEntry(
                id="qwen3.5-plus",
                name="qwen3.5-plus",
                reasoning=False,
                input=["text", "image"],
                cost_input=0,
                cost_output=0,
                context_window=1_000_000,
                max_tokens=65_536,
            ),
            ModelCatalogEntry(
                id="MiniMax-M2.5",
                name="MiniMax-M2.5",
                reasoning=False,
                input=["text"],
                cost_input=0,
                cost_output=0,
                context_window=1_000_000,
                max_tokens=65_536,
            ),
            ModelCatalogEntry(
                id="deepseek-v3.2",
                name="deepseek-v3.2",
                reasoning=False,
                input=["text"],
                cost_input=0,
                cost_output=0,
                context_window=1_000_000,
                max_tokens=65_536,
            ),
            ModelCatalogEntry(
                id="glm-5",
                name="glm-5",
                reasoning=False,
                input=["text"],
                cost_input=0,
                cost_output=0,
                context_window=202_752,
                max_tokens=16_384,
            ),
            ModelCatalogEntry(
                id="kimi-k2.5",
                name="kimi-k2.5",
                reasoning=False,
                input=["text", "image"],
                cost_input=0,
                cost_output=0,
                context_window=262_144,
                max_tokens=32_768,
            ),
        ],
    ),
    ProviderCatalogEntry(
        provider="anthropic",
        name="Anthropic",
        base_url="https://api.anthropic.com/v1",
        api="anthropic",
        key_env="ANTHROPIC_API_KEY",
        priority=Priority.MEDIUM,
        use_case=["深度推理", "代码生成"],
        models=[
            ModelCatalogEntry(
                id="claude-3-5-sonnet-20241022",
                name="claude-3-5-sonnet-20241022",
                reasoning=True,
                input=["text", "image"],
                cost_input=0,
                cost_output=0,
                context_window=200_000,
                max_tokens=4_096,
            )
        ],
    ),
    ProviderCatalogEntry(
        provider="openai",
        name="OpenAI",
        base_url="https://api.openai.com/v1",
        api="openai",
        key_env="OPENAI_API_KEY",
        priority=Priority.MEDIUM,
        use_case=["综合任务"],
        models=[
            ModelCatalogEntry(
                id="gpt-4o",
                name="gpt-4o",
                reasoning=True,
                input=["text", "image"],
                cost_input=0,
                cost_output=0,
                context_window=128_000,
                max_tokens=4_096,
            )
        ],
    ),
    ProviderCatalogEntry(
        provider="ollama",
        name="Ollama Local",
        base_url="http://localhost:11434",
        api="ollama",
        key_env=None,
        priority=Priority.LOW,
        use_case=["离线使用", "隐私优先"],
        models=[
            ModelCatalogEntry(
                id="qwen2:7b",
                name="Qwen2-7B",
                reasoning=False,
                input=["text"],
                cost_input=0,
                cost_output=0,
                context_window=32_768,
                max_tokens=8_192,
            )
        ],
    ),
]

PROVIDER_ENV_KEYS = {
    "bailian-coding-plan": "BAILIAN_CODING_PLAN_API_KEY",
    "bailian": "BAILIAN_API_KEY",
    "qwen": "QWEN_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}


def _provider_is_ready(settings, provider_name: str) -> bool:
    if provider_name == "ollama":
        return bool((settings.ollama_base_url or "").strip())
    field_name = PROVIDER_ENV_KEYS.get(provider_name)
    if not field_name:
        return False
    value = getattr(settings, field_name.lower(), "")
    return bool((value or "").strip())


def _build_providers() -> List[LLMProvider]:
    settings = get_settings()
    providers: List[LLMProvider] = []

    for family in PROVIDER_CATALOG:
        family_ready = _provider_is_ready(settings, family.provider)
        for model in family.models:
            providers.append(
                LLMProvider(
                    id=f"{family.provider}/{model.id}",
                    name=model.name,
                    provider=family.provider,
                    model=model.id,
                    enabled=family_ready or family.provider == "ollama",
                    api_key_set=family_ready or family.provider == "ollama",
                    priority=family.priority,
                    base_url=family.base_url,
                    api=family.api,
                    key_env=family.key_env,
                    reasoning=model.reasoning,
                    input=list(model.input),
                    context_window=model.context_window,
                    max_tokens=model.max_tokens,
                    cost_input=model.cost_input,
                    cost_output=model.cost_output,
                    use_case=list(family.use_case),
                )
            )

    return providers


_voting_config = VotingConfig(
    enabled=True,
    models=["qwen3.5-plus", "MiniMax-M2.5", "deepseek-v3.2"],
    consensus_threshold=0.67,
)


@router.get("/providers", response_model=List[LLMProvider])
async def get_providers():
    return _build_providers()


@router.put("/providers/{provider_id}/api-key")
async def update_api_key(provider_id: str, data: APIKeyUpdate):
    api_key = (data.api_key or "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    providers = _build_providers()
    provider = next(
        (item for item in providers if item.id == provider_id or item.provider == provider_id),
        None,
    )
    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")

    env_key = PROVIDER_ENV_KEYS.get(provider.provider)
    if not env_key or provider.provider == "ollama":
        raise HTTPException(status_code=400, detail="This provider does not use a local API key")

    try:
        write_local_secret(env_key, api_key)
        get_settings.cache_clear()
        try:
            from llm.adapter import LLMAdapter

            LLMAdapter._providers = None
        except Exception:
            pass
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "updated",
        "provider": provider.provider,
        "api_key_set": True,
        "storage": "local_runtime_secret",
    }


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
        "deep_analysis": {"model": "claude-3-5-sonnet-20241022", "fallback": "qwen-max"},
        "long_context": {"model": "kimi-k2.5", "fallback": "qwen-max"},
        "code_generation": {"model": "deepseek-v3.2", "fallback": "qwen-max"},
        "critical_decision": {"mode": "voting", "models": _voting_config.models},
    }

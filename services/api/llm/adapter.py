"""
LLM Adapter - Unified interface for multiple LLM providers

Supports:
- Qwen (通义千问) - Primary choice for Chinese
- GLM (智谱) - Cost-effective
- Minimax - Long context
- Kimi (Moonshot) - 128K context
- Claude - Strong reasoning
- OpenAI GPT-4o - General purpose
- Ollama - Local models
"""

from typing import AsyncGenerator, Dict, Any, Optional, List
from abc import ABC, abstractmethod
import time
from datetime import datetime
import httpx
from config import get_settings


import os
import sys
import logging

_adapter_logger = logging.getLogger("myattention.llm")
_adapter_logger.setLevel(logging.DEBUG)
if not _adapter_logger.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[%(asctime)s] [llm] %(message)s", datefmt="%H:%M:%S"))
    _h.setLevel(logging.DEBUG)
    _adapter_logger.addHandler(_h)
    _log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chat_debug.log")
    _fh = logging.FileHandler(_log_file, encoding="utf-8")
    _fh.setFormatter(logging.Formatter("[%(asctime)s] [llm] %(message)s", datefmt="%H:%M:%S"))
    _fh.setLevel(logging.DEBUG)
    _adapter_logger.addHandler(_fh)


def log(msg: str):
    _adapter_logger.info(msg)


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str = "", base_url: str = ""):
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Synchronous chat completion"""
        pass
    
    @abstractmethod
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Streaming chat completion"""
        pass


class QwenProvider(BaseLLMProvider):
    """Qwen (通义千问) provider"""
    
    def __init__(self, api_key: str = ""):
        super().__init__(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        # Reuse httpx client for connection pooling (TLS + TCP reuse)
        self._client = None
    
    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=10.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client
    
    async def chat(self, messages: List[Dict[str, str]], model: str = "qwen-max", enable_search: bool = False, **kwargs) -> str:
        request_body = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        if enable_search:
            request_body["enable_search"] = True
        
        t0 = time.time()
        log(f"QwenProvider.chat 开始: model={model}, search={enable_search}")
        client = self._get_client()
        response = await client.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=request_body,
        )
        log(f"QwenProvider.chat 响应: status={response.status_code}, 耗时={time.time()-t0:.2f}s")
        if response.status_code != 200:
            error_text = response.text
            log(f"QwenProvider.chat 错误响应: {error_text[:500]}")
            raise Exception(f"API error {response.status_code}: {error_text[:200]}")
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            log(f"QwenProvider.chat 空choices: {str(data)[:300]}")
            raise Exception(f"API returned empty choices for model {model}")
        return choices[0]["message"]["content"]
    
    async def stream_chat(self, messages: List[Dict[str, str]], model: str = "qwen-max", enable_search: bool = False, enable_thinking: bool = False, **kwargs) -> AsyncGenerator[str, None]:
        request_body = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        if enable_search:
            request_body["enable_search"] = True
        if enable_thinking:
            request_body["enable_thinking"] = True
            request_body["stream_options"] = {"include_usage": True}
        
        t0 = time.time()
        log(f"QwenProvider.stream_chat 开始: model={model}, search={enable_search}, thinking={enable_thinking}")
        client = self._get_client()
        log(f"httpx client 获取完成: {time.time()-t0:.3f}s")
        async with client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=request_body,
        ) as response:
            log(f"HTTP 连接建立完成: {time.time()-t0:.3f}s, status={response.status_code}")
            first_line = True
            async for line in response.aiter_lines():
                if first_line:
                    log(f"收到第一行SSE数据: {time.time()-t0:.3f}s")
                    first_line = False
                if line.startswith("data: "):
                    data = line[6:]
                    if data != "[DONE]":
                        import json
                        chunk = json.loads(data)
                        choices = chunk.get("choices", [])
                        if not choices:
                            continue  # Skip chunks with empty choices (e.g., search metadata)
                        choice = choices[0]
                        # Check if model is trying to call tools (e.g., MiniMax search)
                        finish_reason = choice.get("finish_reason")
                        if finish_reason == "tool_calls":
                            log(f"模型 {model} 返回 tool_calls finish_reason，跳过")
                            continue
                        delta = choice.get("delta", {})
                        # Skip if delta contains tool_calls instead of content
                        if delta.get("tool_calls"):
                            log(f"模型 {model} 返回 tool_calls delta，跳过")
                            continue
                        reasoning = delta.get("reasoning_content")
                        if reasoning:
                            yield f"__THINKING__{reasoning}"
                        content = delta.get("content")
                        if content:
                            yield content


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str = ""):
        super().__init__(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1"
        )
    
    async def chat(self, messages: List[Dict[str, str]], model: str = "claude-3-5-sonnet-20241022", **kwargs) -> str:
        async with httpx.AsyncClient() as client:
            # Convert messages format for Claude API
            system = ""
            claude_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                else:
                    claude_messages.append(msg)
            
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 4096,
                    "system": system,
                    "messages": claude_messages,
                    **kwargs
                },
                timeout=60.0
            )
            data = response.json()
            return data["content"][0]["text"]
    
    async def stream_chat(self, messages: List[Dict[str, str]], model: str = "claude-3-5-sonnet-20241022", **kwargs) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient() as client:
            system = ""
            claude_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system = msg["content"]
                else:
                    claude_messages.append(msg)
            
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 4096,
                    "system": system,
                    "messages": claude_messages,
                    "stream": True,
                    **kwargs
                },
                timeout=60.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json
                        data = json.loads(line[6:])
                        if data["type"] == "content_block_delta":
                            yield data["delta"].get("text", "")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider"""
    
    def __init__(self, api_key: str = ""):
        super().__init__(
            api_key=api_key,
            base_url="https://api.openai.com/v1"
        )
    
    async def chat(self, messages: List[Dict[str, str]], model: str = "gpt-4o", **kwargs) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    **kwargs
                },
                timeout=60.0
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def stream_chat(self, messages: List[Dict[str, str]], model: str = "gpt-4o", **kwargs) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    **kwargs
                },
                timeout=60.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            import json
                            chunk = json.loads(data)
                            if chunk["choices"][0].get("delta", {}).get("content"):
                                yield chunk["choices"][0]["delta"]["content"]


class OllamaProvider(BaseLLMProvider):
    """Ollama local model provider"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(api_key="", base_url=base_url)
    
    async def chat(self, messages: List[Dict[str, str]], model: str = "qwen2:7b", **kwargs) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    **kwargs
                },
                timeout=120.0
            )
            data = response.json()
            return data["message"]["content"]
    
    async def stream_chat(self, messages: List[Dict[str, str]], model: str = "qwen2:7b", **kwargs) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    **kwargs
                },
                timeout=120.0
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if data.get("message", {}).get("content"):
                            yield data["message"]["content"]


class LLMAdapter:
    """
    Unified LLM adapter that routes requests to appropriate providers.
    Uses module-level singleton providers for connection reuse.
    """
    _providers = None
    
    @classmethod
    def _init_providers(cls):
        if cls._providers is None:
            settings = get_settings()
            cls._providers = {
                "qwen": QwenProvider(api_key=settings.qwen_api_key),
                "anthropic": ClaudeProvider(api_key=settings.anthropic_api_key),
                "openai": OpenAIProvider(api_key=settings.openai_api_key),
                "ollama": OllamaProvider(base_url=settings.ollama_base_url),
            }
    
    def __init__(self):
        LLMAdapter._init_providers()
        self.providers = LLMAdapter._providers
        self.default_provider = "qwen"
        self.default_model = "qwen-max"
    
    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        """Get provider by name"""
        return self.providers.get(provider_name, self.providers[self.default_provider])
    
    async def chat(
        self,
        message: str,
        provider: str = None,
        model: str = None,
        system_prompt: str = None,
        enable_search: bool = False,
    ) -> str:
        """
        Simple chat completion
        
        Args:
            enable_search: Enable web search for supported models (Qwen, GLM, Kimi)
        """
        provider = provider or self.default_provider
        model = model or self.default_model
        log(f"LLMAdapter.chat ENTRY: model={repr(model)}, provider={repr(provider)}, search={enable_search}")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        llm = self.get_provider(provider)
        
        # Pass enable_search to providers that support it
        if enable_search and provider in ["qwen", "glm", "kimi"]:
            return await llm.chat(messages, model=model, enable_search=True)
        else:
            return await llm.chat(messages, model=model)
    
    async def stream_chat(
        self,
        message: str,
        provider: str = None,
        model: str = None,
        system_prompt: str = None,
        history: List[Dict[str, str]] = None,
        enable_search: bool = False,
        enable_thinking: bool = False,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming chat completion
        
        Args:
            enable_search: Enable web search for supported models
            enable_thinking: Enable thinking/reasoning mode for supported models
        """
        provider = provider or self.default_provider
        model = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": message})
        
        llm = self.get_provider(provider)
        
        # Build kwargs for provider
        kwargs = {}
        if enable_search and provider in ["qwen", "glm", "kimi"]:
            kwargs["enable_search"] = True
        if enable_thinking and provider == "qwen":
            kwargs["enable_thinking"] = True
        
        log(f"LLMAdapter.stream_chat: provider={provider}, model={model}, kwargs={kwargs}")
        async for chunk in llm.stream_chat(messages, model=model, **kwargs):
            yield chunk

import httpx
from typing import Literal, AsyncGenerator
from pydantic import BaseModel
from .config import settings

class LLMProviderConfig(BaseModel):
    mode: Literal["local", "cloud", "remote"] = "local"
    base_url: str = "http://localhost:11434/v1"
    api_key: str | None = None
    model: str = "qwen2.5:7b"

class LLMClient:
    def __init__(self, config: LLMProviderConfig | None = None):
        self.config = config or LLMProviderConfig(
            mode=settings.llm_provider_mode,
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model
        )
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        self.client = httpx.AsyncClient(base_url=self.config.base_url, headers=headers, timeout=120.0)

    async def chat_stream(self, messages: list[dict], tools: list[dict] | None = None) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    import json
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        pass

    async def get_available_models(self) -> list[str]:
        """Fetch list of available models. If local Ollama, queries /api/tags."""
        if self.config.mode == "local" and "11434" in self.config.base_url:
            # Ollama specific API for listing models
            ollama_url = self.config.base_url.replace("/v1", "/api/tags")
            try:
                response = await self.client.get(ollama_url)
                response.raise_for_status()
                data = response.json()
                return [m.get("name") for m in data.get("models", [])]
            except Exception:
                return [self.config.model]
        else:
            return [self.config.model]

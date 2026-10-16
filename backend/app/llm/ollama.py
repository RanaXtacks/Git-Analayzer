import logging
import httpx
from app.llm.base import LLMProvider, LLMProviderError, LLMTimeoutError, LLMUnavailableError

logger = logging.getLogger("git_analyzer.llm.ollama")


class OllamaProvider(LLMProvider):
    """LLM Provider implementation for local Ollama instances."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:8b",
        timeout: float = 120.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                if response.status_code != 200:
                    raise LLMProviderError(
                        f"Ollama returned HTTP {response.status_code}: {response.text}"
                    )
                data = response.json()
                return data.get("response", "")
        except httpx.TimeoutException:
            raise LLMTimeoutError(f"Ollama generation timed out after {self.timeout}s.")
        except httpx.RequestError as e:
            raise LLMUnavailableError(
                f"Could not connect to Ollama server at {self.base_url}. Ensure 'ollama serve' is running and model '{self.model}' is pulled. ({e})"
            )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

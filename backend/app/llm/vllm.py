import logging
import httpx
from app.llm.base import LLMProvider, LLMProviderError, LLMTimeoutError, LLMUnavailableError

logger = logging.getLogger("git_analyzer.llm.vllm")


class VLLMProvider(LLMProvider):
    """LLM Provider implementation for high-throughput vLLM OpenAI-compatible server."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        model: str = "qwen3:8b",
        timeout: float = 120.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 4096,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                )
                if response.status_code != 200:
                    raise LLMProviderError(
                        f"vLLM returned HTTP {response.status_code}: {response.text}"
                    )
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    raise LLMProviderError("vLLM returned an empty choices list.")
                return choices[0].get("message", {}).get("content", "")
        except httpx.TimeoutException:
            raise LLMTimeoutError(f"vLLM generation timed out after {self.timeout}s.")
        except httpx.RequestError as e:
            raise LLMUnavailableError(
                f"Could not connect to vLLM server at {self.base_url}. Verify the vLLM container is running and healthy. ({e})"
            )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/health")
                if resp.status_code == 200:
                    return True
                # Fallback check
                resp_models = await client.get(f"{self.base_url}/v1/models")
                return resp_models.status_code == 200
        except Exception:
            return False

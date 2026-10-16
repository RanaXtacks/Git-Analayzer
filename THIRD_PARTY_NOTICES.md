# Third-Party Software Notices and Licenses

Git-Analyzer incorporates or interacts with open-source software and open-weight models. This document summarizes the licenses of key third-party components.

---

## 1. ContribCompass / Git-Analyzer Source Code
- **License**: Apache License 2.0
- **Copyright**: (c) Git-Analyzer Contributors

---

## 2. Backend Dependencies
- **FastAPI**: MIT License ([tiangolo/fastapi](https://github.com/tiangolo/fastapi))
- **Starlette**: BSD-3-Clause License ([encode/starlette](https://github.com/encode/starlette))
- **Pydantic**: MIT License ([pydantic/pydantic](https://github.com/pydantic/pydantic))
- **HTTPX**: BSD-3-Clause License ([encode/httpx](https://github.com/encode/httpx))
- **SQLAlchemy**: MIT License ([sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy))
- **Asyncpg**: Apache License 2.0 ([MagicStack/asyncpg](https://github.com/MagicStack/asyncpg))
- **aiosqlite**: MIT License ([omnilib/aiosqlite](https://github.com/omnilib/aiosqlite))
- **Redis (aioredis-py)**: MIT License ([redis/redis-py](https://github.com/redis/redis-py))
- **Uvicorn**: BSD-3-Clause License ([encode/uvicorn](https://github.com/encode/uvicorn))
- **SlowAPI**: MIT License ([laurentS/slowapi](https://github.com/laurentS/slowapi))
- **Pytest**: MIT License ([pytest-dev/pytest](https://github.com/pytest-dev/pytest))

---

## 3. Frontend Dependencies
- **React**: MIT License ([facebook/react](https://github.com/facebook/react))
- **Vite**: MIT License ([vitejs/vite](https://github.com/vitejs/vite))
- **Tailwind CSS**: MIT License ([tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss))
- **Lucide Icons**: ISC License ([lucide-icons/lucide](https://github.com/lucide-icons/lucide))
- **TanStack React Query**: MIT License ([TanStack/query](https://github.com/TanStack/query))

---

## 4. Inference Servers & Infrastructure
- **Ollama**: MIT License ([ollama/ollama](https://github.com/ollama/ollama))
- **vLLM**: Apache License 2.0 ([vllm-project/vllm](https://github.com/vllm-project/vllm))
- **PostgreSQL**: PostgreSQL License ([postgresql.org](https://www.postgresql.org/about/licence/))
- **Redis**: BSD-3-Clause / RSALv2 / SSPL (dependent on version; container uses open-source Redis)
- **Caddy**: Apache License 2.0 ([caddyserver/caddy](https://github.com/caddyserver/caddy))

---

## 5. Open-Weight Model Notice
- **Default Recommended Model**: `Qwen/Qwen3-8B` (or `qwen3:8b` via Ollama)
- **Model License**: Qwen open-weight model license (Apache 2.0 / Tongyi Qianwen License agreement depending on model release). Model weights are NOT bundled in the Git-Analyzer repository. Users and deployers should inspect and comply with the applicable terms for the specific model weights downloaded or served via Ollama / vLLM.

---

## 6. External APIs
- **GitHub REST API**: Proprietary service of GitHub, Inc. Usage is subject to the [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) and [GitHub API Acceptable Use Policy](https://docs.github.com/en/rest/overview/resources-in-the-rest-api).

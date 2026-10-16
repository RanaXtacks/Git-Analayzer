# Git-Analyzer

> **Find your way into any open-source project.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?logo=tailwind-css)](https://tailwindcss.com)
[![Model](https://img.shields.io/badge/LLM-Qwen3%3A8b-orange?logo=openai)](https://github.com/QwenLM)

**Git-Analyzer** is an open-source, self-hostable AI assistant that analyzes public GitHub repositories and generates evidence-backed onboarding guides for new contributors. It combines GitHub repository analysis, deterministic issue ranking, and open-weight LLM reasoning to help developers understand unfamiliar open-source projects and identify a practical first contribution.

---

## The Zero-Hallucination Principle

Most AI code assistants guess when they lack information. Git-Analyzer is built on a strict operational rule:

> **Inspect the repository first, reason over repository evidence second, and clearly communicate uncertainty when information is unavailable. Never fabricate repository information.**

Every recommendation produced by Git-Analyzer includes verifiable citations:
- **Source**: Manifest or document name (`package.json`, `README.md`, `Issue #101`)
- **Location**: AST key, section title, or label name (`scripts.dev`, `engines.node`, `labels`)
- **Detail**: The exact code excerpt or text from the repository

If a command or required version is not declared in the codebase, Git-Analyzer explicitly communicates that it could not be determined rather than guessing.

---

## Key Features

- **Project Summary & Core Purpose**: Plain-language overview explaining the problem the codebase solves.
- **Verified Prerequisites**: Only includes runtimes, engines, and dependencies actually specified in project manifests.
- **Local Setup & Run Commands**: Numbered, copyable shell commands detected from scripts, Makefiles, and Docker configurations.
- **Architecture & Directory Explorer**: Explains important folders and "Why a newcomer should care."
- **Deterministic Beginner Issue Ranking**: Scores open GitHub issues based on newcomer friendliness labels (`good first issue`, `help wanted`, `documentation`), comment volume, and scope size while penalizing architectural rewrites and vague descriptions.
- **Suggested First Contribution Spotlight**: Identifies a realistic, low-risk contribution (docs, small test addition, typo fix) with target files and rationale.
- **Contribution Workflow**: Prioritizes repository-specific `CONTRIBUTING.md` guidelines, clearly identifying generic GitHub PR flows when absent.
- **Evidence Inspection**: Interactive badges allow users to inspect the exact underlying repository citations.
- **Real-Time Progress Streaming**: Uses Server-Sent Events (SSE) to display stage-by-stage analysis progress.
- **100% Open Source & Zero Proprietary Dependencies**: Powered by open-weight models (`Qwen3:8b`) via Ollama or vLLM. No mandatory OpenAI, Anthropic, or proprietary inference API keys required.

---

## High-Level Architecture

```text
                           USER BROWSER
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  React + Tailwind v4 UI │
                   │  (SSE Progress & Guide) │
                   └────────────┬────────────┘
                                │ HTTP / SSE
                                ▼
                   ┌─────────────────────────┐
                   │    FastAPI Backend      │
                   └────────────┬────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌──────────────┐      ┌──────────────────┐      ┌──────────────┐
│  GitHub API  │      │ Repository       │      │ Redis Cache  │
│  Client      │      │ Analyzer         │      │ (1h TTL /    │
│  (httpx)     │      │ - Dependencies   │      │  SHA bound)  │
└──────┬───────┘      │ - Structure      │      └──────────────┘
       │              │ - Configuration  │
       ▼              │ - Issue Ranker   │
┌──────────────┐      └─────────┬────────┘
│ Context      │                │
│ Builder &    │◄───────────────┘
│ Sanitizer    │ (Scrubs secrets & truncates)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ LLM Provider Abstraction (LLMProvider ABC)   │
│   ├── Development: OllamaProvider            │
│   └── Production:  VLLMProvider              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
          ┌──────────────────────────┐
          │   Qwen3:8b Open-Weight   │
          └────────────┬─────────────┘
                       │ Structured JSON
                       ▼
          ┌──────────────────────────┐
          │  Pydantic Validation &   │
          │  Anti-Hallucination      │
          │  Evidence Verifier       │
          └────────────┬─────────────┘
                       │
                       ▼
                 Validated Guide
```

---

## Modes of Operation

### Mode A: Minimal Development Mode (Zero Docker required)
The backend can operate entirely in-memory with no PostgreSQL or Redis dependencies.

1. **Start Ollama** (with Qwen3):
   ```bash
   ollama pull qwen3:8b
   ollama serve
   ```

2. **Start Backend**:
   ```bash
   cd backend
   python -m venv .venv
   # Windows: .venv\Scripts\activate | Unix: source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

3. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:5173`.

---

### Mode B: Full Self-Hosted Development (Docker Compose)
Runs React, FastAPI, PostgreSQL, Redis, and connects to host Ollama:

```bash
cp .env.example .env
docker compose up --build
```

---

### Mode C: Production Cluster (vLLM + GPU + Caddy)
Production deployment orchestrating Caddy (automatic HTTPS), FastAPI, PostgreSQL, Redis, and high-throughput vLLM inference:

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## Environment Variables Reference

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `Git-Analyzer` | Application branding |
| `APP_ENV` | `development` | Environment mode (`development` or `production`) |
| `HOST` / `PORT` | `0.0.0.0` / `8000` | Backend bind address and port |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins for frontend |
| `GITHUB_TOKEN` | *(empty)* | Optional server-side PAT (boosts GitHub limit to 5000 req/hr) |
| `LLM_PROVIDER` | `ollama` | Inference engine (`ollama` for dev, `vllm` for prod) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service endpoint |
| `OLLAMA_MODEL` | `qwen3:8b` | Ollama model identifier |
| `VLLM_BASE_URL` | `http://localhost:8000` | vLLM service endpoint |
| `VLLM_MODEL` | `qwen3:8b` | vLLM model identifier |
| `DATABASE_ENABLED` | `false` | Enable PostgreSQL persistence (`true` in prod) |
| `DATABASE_URL` | `sqlite+aiosqlite:///...` | SQLAlchemy async connection string |
| `REDIS_ENABLED` | `false` | Enable Redis cache (`true` in prod) |
| `REDIS_URL` | `redis://localhost:6379/0`| Redis connection URI |
| `CACHE_TTL` | `3600` | Guide cache duration in seconds (1 hour) |
| `RATE_LIMIT_PER_MINUTE`| `5` | IP rate limit for `/api/analyze` |
| `MAX_TREE_ENTRIES` | `5000` | Maximum git tree entries processed |
| `MAX_FILE_SIZE` | `200000` | Maximum file character limit before truncation |
| `MAX_README_SIZE` | `100000` | Maximum README character limit |
| `MAX_ISSUES` | `30` | Maximum open issues retrieved for ranking |

---

## Testing & Verification

### Backend Tests
Execute the comprehensive automated test suite (25 tests covering URL validation, GitHub client, dependency parsers, structure analysis, deterministic issue ranking, secret sanitization, LLM parser, and API routes):

```bash
cd backend
python -m pytest tests -v
```

### Frontend Verification
```bash
cd frontend
# Run URL validation tests
node --experimental-strip-types src/tests/validation.test.ts

# Production bundle build test
npm run build
```

---

## GitHub API & Rate Limiting Strategy

- **Unauthenticated**: The GitHub REST API permits 60 requests per hour per IP.
- **Server-Side Token**: If a maintainer configures `GITHUB_TOKEN=ghp_...` in `.env`, the rate limit expands to 5,000 requests per hour. The token is stored strictly on the server and is **never** transmitted to client browsers.
- **Commit SHA Cache Invalidation**: Cached guides are tied directly to the default branch's HEAD commit SHA (`guide:owner/repo:commit_sha:model`). When new commits land in the repository, cached guides are automatically refreshed.
- **Request Deduplication**: If multiple concurrent requests arrive for the same repository, Git-Analyzer deduplicates them and serves the resulting guide once rather than executing redundant LLM inference calls.

---

## Hardware & GPU Sizing Guide

| Setup | Recommended Hardware | Compute Cost |
|---|---|---|
| **Development** (Ollama + Qwen3:8b) | Apple Silicon (M1/M2/M3) or NVIDIA GPU (>= 6GB VRAM) or modern multi-core CPU | Minimal / Local |
| **Production** (vLLM + Qwen3:8b) | 1x NVIDIA RTX 4090 (24GB) or A10G (24GB) or L4 (24GB) | ~$0.75 - $1.20 / hr |
| **Production High-Throughput** | 1x NVIDIA A100 (40GB/80GB) | ~$2.00 - $3.50 / hr |

> [!NOTE]
> **Important Open-Source Distinction**: Open-source software does not mean unlimited free hosting. While Git-Analyzer code and Qwen3 weights are open source and self-hostable, running a public hosted instance requires compute, network egress, and GPU hardware.

---

## Security & Privacy

- **No Secret Exposure**: All repository files, environment examples, and READMEs are passed through the `ContextSanitizer` before reaching the LLM, logs, or persistent databases. AWS keys (`AKIA...`), GitHub tokens (`ghp_...`), JWTs, and private keys (`-----BEGIN PRIVATE KEY-----`) are automatically scrubbed.
- **Sensitive File Exclusion**: Files like `.env`, `.env.local`, `*.pem`, `*.key`, and `id_rsa` are dropped from context selection completely.
- **No SSRF**: Git-Analyzer accepts only valid GitHub repository URLs matching `https://github.com/{owner}/{repo}`. Arbitrary URLs or internal IP addresses are strictly rejected.
- **Privacy Notice**: For public repositories, metadata is retrieved via GitHub's public API. For self-hosted instances, inference runs entirely on your own hardware.

---

## Third-Party Software & Model Notices

- **Git-Analyzer Code**: [Apache License 2.0](LICENSE)
- **FastAPI, React, Pydantic, HTTPX, SQLAlchemy**: MIT / BSD-3 licenses (see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md))
- **Model Weights**: `Qwen3:8b` weights are licensed under the Qwen open-weight model license. Model weights are referenced dynamically and are not stored in this repository.

---

## Roadmap

- [ ] Interactive contributor skill-matching (recommend issues based on your preferred language).
- [ ] Pull request history analysis (identify maintainer review turnaround times).
- [ ] AI contribution mentor mode (interactive Q&A grounded exclusively in repository files).
- [ ] Multi-repository architecture comparison.
- [ ] Visual dependency and component graph visualization.

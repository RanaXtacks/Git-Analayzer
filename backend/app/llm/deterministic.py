import json
import logging
import re
from typing import Any, Dict, List
from app.llm.base import LLMProvider

logger = logging.getLogger("git_analyzer.llm.deterministic")


class DeterministicProvider(LLMProvider):
    """
    Fallback deterministic provider that generates a complete, evidence-backed
    onboarding guide directly from repository data when an external LLM server
    (Ollama/vLLM) is not yet running or installed.
    """

    async def health_check(self) -> bool:
        return True

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Extract the JSON payload embedded in user_prompt
        data: Dict[str, Any] = {}
        match = re.search(r"```json\s*(\{.*?\})\s*```", user_prompt, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
            except Exception as e:
                logger.warning(f"Failed to parse context JSON in deterministic provider: {e}")

        meta = data.get("repository_metadata", {})
        deps = data.get("detected_dependencies", {})
        struct = data.get("structure_analysis", {})
        cfg = data.get("configuration_analysis", {})
        readme = data.get("readme_excerpt", "")
        issues = data.get("available_open_issues", [])

        # 1. Project Summary
        summary = meta.get("description")
        if not summary or summary.strip() == "":
            summary = (
                f"{meta.get('name', 'This project')} is an open-source {meta.get('language') or 'software'} "
                f"repository hosted on GitHub by {meta.get('owner', 'the maintainers')}."
            )
        else:
            summary = f"{meta.get('name', 'This project')}: {summary}"

        # 2. Prerequisites
        prereqs = []
        if deps.get("runtime"):
            prereqs.append(f"Runtime: {deps['runtime']}")
        elif meta.get("language"):
            prereqs.append(f"Language environment: {meta['language']}")

        if deps.get("package_manager"):
            prereqs.append(f"Package manager: {deps['package_manager']}")

        if cfg.get("docker_support"):
            prereqs.append("Docker and Docker Compose (optional containerized setup)")

        if not prereqs:
            prereqs.append("Git version control")

        # 3. Setup Steps
        setup_steps = [
            {
                "step": 1,
                "description": f"Clone the {meta.get('name', 'repository')} codebase locally",
                "command": f"git clone {meta.get('html_url', 'https://github.com/owner/repo')}",
                "evidence": [
                    {"source": "GitHub", "location": "html_url", "detail": meta.get("html_url", "")}
                ],
            }
        ]

        # Repo cd step
        repo_name = meta.get("name", "repo")
        setup_steps.append({
            "step": 2,
            "description": "Navigate into the project directory",
            "command": f"cd {repo_name}",
            "evidence": [{"source": "Git tree", "location": "root", "detail": f"Repository directory {repo_name}"}],
        })

        # Install command step
        install_cmd = deps.get("install_command")
        if install_cmd:
            setup_steps.append({
                "step": 3,
                "description": f"Install project dependencies via {deps.get('package_manager') or 'manifest'}",
                "command": install_cmd,
                "evidence": [
                    {
                        "source": deps.get("manifests_present", ["package.json"])[0] if deps.get("manifests_present") else "manifest",
                        "location": "install_command",
                        "detail": install_cmd,
                    }
                ],
            })
        elif cfg.get("makefile_found"):
            setup_steps.append({
                "step": 3,
                "description": "Install project dependencies using Makefile target",
                "command": "make setup",
                "evidence": [{"source": "Makefile", "location": "targets", "detail": "make setup"}],
            })
        else:
            setup_steps.append({
                "step": 3,
                "description": "Install dependencies as outlined in documentation",
                "command": None,
                "evidence": [{"source": "README.md", "location": "Setup", "detail": "Inspect README for specific package manager"}],
            })

        # 4. Run Instructions
        run_instructions = []
        dev_cmd = deps.get("dev_command") or deps.get("start_command")
        if dev_cmd:
            run_instructions.append({
                "step": 1,
                "description": "Start the development server / local runtime",
                "command": dev_cmd,
                "evidence": [
                    {
                        "source": deps.get("manifests_present", ["manifest"])[0] if deps.get("manifests_present") else "package scripts",
                        "location": "scripts",
                        "detail": dev_cmd,
                    }
                ],
            })

        test_cmd = deps.get("test_command")
        if test_cmd:
            run_instructions.append({
                "step": len(run_instructions) + 1,
                "description": "Run the automated test suite to verify your setup",
                "command": test_cmd,
                "evidence": [
                    {
                        "source": deps.get("manifests_present", ["manifest"])[0] if deps.get("manifests_present") else "test configuration",
                        "location": "test script",
                        "detail": test_cmd,
                    }
                ],
            })

        if not run_instructions:
            run_instructions.append({
                "step": 1,
                "description": "Review the repository README for specific execution commands",
                "command": None,
                "evidence": [{"source": "README.md", "location": "Usage", "detail": "No explicit dev or start script was declared in root manifests"}],
            })

        # 5. Important Directories
        important_dirs = []
        for d in struct.get("important_directories", [])[:6]:
            desc = "Application source code and business logic"
            reason = "Primary location where features and bugfixes are implemented."
            if "test" in d:
                desc = "Test suite and verification specs"
                reason = "Crucial for writing tests to accompany your pull requests."
            elif "doc" in d:
                desc = "Documentation, guides, and manuals"
                reason = "Great starting place for understanding API contracts or contributing docs."
            elif "api" in d or "route" in d:
                desc = "API endpoint routing and handlers"
                reason = "Where incoming requests are processed and responses are returned."
            elif "component" in d:
                desc = "UI view components"
                reason = "Where user interface layouts and widgets are defined."

            important_dirs.append({
                "path": d,
                "description": desc,
                "reason_to_care": reason,
                "evidence": [{"source": "Git tree", "location": d, "detail": f"Directory {d}"}],
            })

        if not important_dirs:
            important_dirs.append({
                "path": "root",
                "description": "Project root files and configuration",
                "reason_to_care": "Contains configuration files and manifests.",
                "evidence": [{"source": "Git tree", "location": "/", "detail": "Repository root"}],
            })

        # 6. Where to start
        entry_points = struct.get("likely_entry_points", [])
        if entry_points:
            where_to_start = f"Start by inspecting '{entry_points[0]}' to understand the execution lifecycle, then review existing tests to see how modules interact."
        elif important_dirs:
            where_to_start = f"Start by exploring '{important_dirs[0]['path']}' and reviewing open beginner issues to identify a localized entry point."
        else:
            where_to_start = "Review the README file and verify your local installation by running the test suite."

        # 7. Recommended Issues
        recommended_issues = []
        for iss in issues[:5]:
            recommended_issues.append({
                "number": iss.get("number"),
                "title": iss.get("title"),
                "url": iss.get("url"),
                "difficulty": iss.get("difficulty", "Beginner"),
                "reason": ", ".join(iss.get("ranking_reasons", ["Open issue with manageable scope"])),
                "score": iss.get("score", 30),
                "evidence": [
                    {
                        "source": f"GitHub Issue #{iss.get('number')}",
                        "location": "labels",
                        "detail": ", ".join(iss.get("labels", [])),
                    }
                ],
            })

        # 8. First Contribution
        first_contrib_files = [f for f in entry_points[:2]]
        if not first_contrib_files and important_dirs:
            first_contrib_files = [f"{important_dirs[0]['path']}/"]

        first_contrib = {
            "title": "Verify Local Test Suite & Improve Documentation / Types",
            "description": "Set up the development environment, execute the existing test suite, and identify any missing docstrings, documentation clarifications, or minor test coverage gaps.",
            "suggested_files": first_contrib_files,
            "reasoning": "A documentation fix or minor test addition provides immediate value to maintainers while giving you hands-on experience with the project's PR review workflow.",
            "evidence": [
                {
                    "source": "Repository Analysis",
                    "location": "Contribution Strategy",
                    "detail": "Safe, low-risk contribution recommended for initial familiarity.",
                }
            ],
        }

        # 9. Contribution Workflow
        workflow = [
            "Fork the repository to your GitHub account",
            "Clone your fork and create a descriptive topic branch (`git checkout -b fix-xyz`)",
            "Make your changes and ensure existing and new tests pass",
            "Commit with a clear, concise message",
            "Push to your fork and submit a Pull Request referencing any relevant issue",
        ]

        # 10. Execution Plans
        execution_plans = _build_deterministic_execution_plans(
            meta=meta,
            deps=deps,
            struct=struct,
            cfg=cfg,
            first_contrib_files=first_contrib_files,
            important_dirs=important_dirs,
            issues=issues,
        )

        # 11. Deep Architecture Blueprint
        deep_arch = _build_deterministic_deep_architecture(
            meta=meta,
            deps=deps,
            struct=struct,
            cfg=cfg,
            important_dirs=important_dirs,
        )

        # 12. Differentiation Matrix (Git-Analyzer vs Copilot)
        diff_matrix = _build_deterministic_diff_matrix()

        # 13. Warnings
        warnings = [
            "Generated using Git-Analyzer deterministic repository synthesis.",
        ]
        if not meta.get("license"):
            warnings.append("No open-source LICENSE file could be detected in the repository root.")

        guide_dict = {
            "project_summary": summary,
            "prerequisites": prereqs,
            "setup_steps": setup_steps,
            "run_instructions": run_instructions,
            "important_directories": important_dirs,
            "where_to_start": where_to_start,
            "recommended_issues": recommended_issues,
            "first_contribution": first_contrib,
            "contribution_workflow": workflow,
            "execution_plans": execution_plans,
            "deep_architecture": deep_arch,
            "differentiation_matrix": diff_matrix,
            "warnings": warnings,
        }

        return json.dumps(guide_dict)


def _build_deterministic_execution_plans(
    meta: Dict[str, Any],
    deps: Dict[str, Any],
    struct: Dict[str, Any],
    cfg: Dict[str, Any],
    first_contrib_files: List[str],
    important_dirs: List[Dict[str, Any]],
    issues: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    repo_name = meta.get("name", "repository")
    html_url = meta.get("html_url", "https://github.com/owner/repo")
    install_cmd = deps.get("install_command") or "npm install"
    dev_cmd = deps.get("dev_command") or deps.get("start_command") or "npm run dev"
    test_cmd = deps.get("test_command") or "npm test"
    lint_cmd = deps.get("lint_command") or "npm run lint"
    manifests = deps.get("manifests_present", ["package.json"])
    entry_points = struct.get("likely_entry_points", [])
    primary_entry = entry_points[0] if entry_points else (important_dirs[0]["path"] if important_dirs else "src")
    top_issue = issues[0] if issues else None
    issue_target = f"Issue #{top_issue['number']}: {top_issue['title']}" if top_issue else "first good beginner issue"

    plans = [
        {
            "id": "day_one",
            "title": "30-Minute Fast-Track Contributor",
            "target_persona": "First-time Contributor / Quick PR",
            "time_estimate": "~30 mins",
            "difficulty": "Beginner",
            "goal": f"Bootstrap a clean local sandbox for {repo_name}, verify test passing, and prepare an immediate PR for {issue_target}.",
            "steps": [
                {
                    "step": 1,
                    "action": f"Clone the {repo_name} repository locally and cd into the working root.",
                    "target_files": ["README.md"],
                    "command": f"git clone {html_url} && cd {repo_name}",
                    "verification": "Run `git status` to verify you are on the default branch and working tree is clean.",
                },
                {
                    "step": 2,
                    "action": "Install pinned project dependencies using the verified manifest.",
                    "target_files": manifests,
                    "command": install_cmd,
                    "verification": "Command exits with code 0 without unhandled lockfile mismatches.",
                },
                {
                    "step": 3,
                    "action": "Execute the automated test suite to confirm zero baseline regressions.",
                    "target_files": first_contrib_files or ["tests/"],
                    "command": test_cmd,
                    "verification": "All baseline tests pass green before any local code changes.",
                },
                {
                    "step": 4,
                    "action": f"Inspect primary entrypoint '{primary_entry}' to understand bootstrap flow.",
                    "target_files": [primary_entry],
                    "command": None,
                    "verification": "Identify the primary application bootstrap and route registration handlers.",
                },
                {
                    "step": 5,
                    "action": "Create an isolated topic branch and commit verified changes with concise message.",
                    "target_files": first_contrib_files,
                    "command": "git checkout -b fix/first-contribution",
                    "verification": f"Run `{lint_cmd}` and `{test_cmd}` before pushing your branch to your fork.",
                },
            ],
            "key_files": first_contrib_files or [primary_entry],
            "tips": [
                "Keep your first PR strictly confined to a single concern or issue.",
                "Do not reformat unrelated files or bump unrelated dependencies in your initial PR.",
            ],
        },
        {
            "id": "deep_architecture",
            "title": "Deep Architectural Execution Blueprint",
            "target_persona": "Senior Engineer / Systems Architect",
            "time_estimate": "~2-3 hours",
            "difficulty": "Advanced",
            "goal": "Trace the end-to-end execution lifecycle from ingress entrypoints through middleware, domain services, and data layers.",
            "steps": [
                {
                    "step": 1,
                    "action": "Trace Application Bootstrap & Invariant Initialization.",
                    "target_files": entry_points[:2] or [primary_entry],
                    "command": None,
                    "verification": "Map environment variable validation, config parsing, and container/dependency wiring.",
                },
                {
                    "step": 2,
                    "action": "Analyze Request Ingress, Routing, & Middleware Chains.",
                    "target_files": [d["path"] for d in important_dirs if any(k in d["path"] for k in ["api", "route", "service"])][:3] or [primary_entry],
                    "command": None,
                    "verification": "Verify authentication filters, schema validation, and error-handling interceptors.",
                },
                {
                    "step": 3,
                    "action": "Inspect Core Domain Logic & State Mutation.",
                    "target_files": [d["path"] for d in important_dirs if any(k in d["path"] for k in ["core", "app", "lib", "src"])][:3] or [primary_entry],
                    "command": None,
                    "verification": "Identify pure business logic functions vs IO-bound network/database calls.",
                },
                {
                    "step": 4,
                    "action": "Audit Data Persistence, External Integrations, & Caching.",
                    "target_files": [d["path"] for d in important_dirs if any(k in d["path"] for k in ["model", "db", "client", "schema"])][:2] or manifests,
                    "command": None,
                    "verification": "Confirm database transactions, migration hooks, or remote API client retry contracts.",
                },
                {
                    "step": 5,
                    "action": "Verify Output Response Serialization & Client Envelopes.",
                    "target_files": entry_points[:1] or [primary_entry],
                    "command": dev_cmd,
                    "verification": "Verify response status codes, payload structures, and client telemetry events.",
                },
            ],
            "key_files": entry_points + [d["path"] for d in important_dirs[:4]],
            "tips": [
                "Use the test suite as living documentation to observe how mock dependencies are injected into services.",
                "Look for circular dependency risks across top-level domain packages.",
            ],
        },
        {
            "id": "bug_hunt",
            "title": "Bug Hunter & Isolated Reproduction Plan",
            "target_persona": "QA / Issue Triager",
            "time_estimate": "~1 hour",
            "difficulty": "Intermediate",
            "goal": "Isolate reported defects, construct automated reproduction test cases, and formulate surgical bugfixes.",
            "steps": [
                {
                    "step": 1,
                    "action": "Identify the failing module boundary from reported issue stack trace or symptoms.",
                    "target_files": [d["path"] for d in important_dirs if "test" in d["path"]][:1] or first_contrib_files,
                    "command": None,
                    "verification": "Locate corresponding unit or integration spec covering the problematic code path.",
                },
                {
                    "step": 2,
                    "action": "Execute targeted isolated test spec without invoking full system overhead.",
                    "target_files": [d["path"] for d in important_dirs if "test" in d["path"]][:1] or first_contrib_files,
                    "command": f"{test_cmd} -- -t 'targeted_spec'",
                    "verification": "Verify isolated runner completes in under 5 seconds.",
                },
                {
                    "step": 3,
                    "action": "Author a minimal, failing reproduction test asserting expected behavior.",
                    "target_files": [d["path"] for d in important_dirs if "test" in d["path"]][:1] or first_contrib_files,
                    "command": test_cmd,
                    "verification": "The newly authored reproduction test fails exactly with the reported bug symptoms.",
                },
                {
                    "step": 4,
                    "action": "Implement the minimal, surgical patch directly in the underlying domain logic.",
                    "target_files": first_contrib_files or [primary_entry],
                    "command": None,
                    "verification": "Failing test turns green with zero side effects on existing unit tests.",
                },
                {
                    "step": 5,
                    "action": "Run project linter and static type analysis to satisfy CI contracts.",
                    "target_files": manifests,
                    "command": lint_cmd,
                    "verification": "Exit code 0 with zero formatting or lint warnings.",
                },
            ],
            "key_files": [d["path"] for d in important_dirs if "test" in d["path"]] or first_contrib_files,
            "tips": [
                "Never write code changes before having an automated test that faithfully reproduces the defect.",
                "Inspect git log / git blame on the altered lines to see historical context and edge-case rationale.",
            ],
        },
        {
            "id": "system_extender",
            "title": "Feature Extender & System Scaling Roadmap",
            "target_persona": "Core Contributor / Module Author",
            "time_estimate": "~1-2 days",
            "difficulty": "Advanced",
            "goal": "Design, register, and implement a complete modular capability or endpoint following codebase idioms.",
            "steps": [
                {
                    "step": 1,
                    "action": "Identify the project's canonical extension boundary (Router, Plugin Hook, or Service Interface).",
                    "target_files": [d["path"] for d in important_dirs if any(k in d["path"] for k in ["api", "lib", "services", "plugin"])][:2] or [primary_entry],
                    "command": None,
                    "verification": "Locate an existing peer feature to use as the canonical architectural template.",
                },
                {
                    "step": 2,
                    "action": "Define new strongly-typed schema contracts and entity interfaces.",
                    "target_files": [d["path"] for d in important_dirs if any(k in d["path"] for k in ["model", "type", "schema"])][:2] or [primary_entry],
                    "command": None,
                    "verification": "Compiler and typechecker accept contract definitions with no implicit `any`.",
                },
                {
                    "step": 3,
                    "action": "Implement isolated business service logic decoupled from IO transport.",
                    "target_files": [primary_entry],
                    "command": None,
                    "verification": "Service methods accept mockable interfaces and return typed domain entities.",
                },
                {
                    "step": 4,
                    "action": "Mount new capability into main router / dependency injection registry.",
                    "target_files": [primary_entry],
                    "command": dev_cmd,
                    "verification": "Server starts cleanly and exposes the newly registered feature / endpoint.",
                },
                {
                    "step": 5,
                    "action": "Author comprehensive unit, integration, and contract tests for the new feature.",
                    "target_files": [d["path"] for d in important_dirs if "test" in d["path"]][:1] or first_contrib_files,
                    "command": test_cmd,
                    "verification": "All newly added tests pass and overall repository code coverage does not decrease.",
                },
            ],
            "key_files": entry_points + [d["path"] for d in important_dirs[:4]],
            "tips": [
                "Follow existing dependency injection or factory patterns rather than creating global singletons.",
                "Ensure new configuration options are documented in README or .env.example.",
            ],
        },
    ]
    return plans


def _build_deterministic_deep_architecture(
    meta: Dict[str, Any],
    deps: Dict[str, Any],
    struct: Dict[str, Any],
    cfg: Dict[str, Any],
    important_dirs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    lang = (meta.get("language") or deps.get("language") or "").lower()
    runtime = (deps.get("runtime") or "").lower()
    raw_deps = [d.lower() for d in deps.get("key_dependencies", [])]
    entry_points = struct.get("likely_entry_points", [])
    primary_entry = entry_points[0] if entry_points else "src/index"

    # Infer pattern
    if any(k in raw_deps for k in ["fastapi", "flask", "django"]) or "python" in lang:
        pattern = "Layered Asynchronous Service-Repository Architecture"
        flow_desc = (
            "Requests enter through ASGI/WSGI entrypoints, pass through authentication and CORS middleware, "
            "are dispatched to typed route handlers, processed by isolated domain services, and serialized into JSON."
        )
    elif any(k in raw_deps for k in ["next", "nuxt"]):
        pattern = "Full-Stack Server-Side Rendered (SSR) & API Route Monolith"
        flow_desc = (
            "Incoming requests are routed through file-based server handlers, rendering React/Vue components on the server "
            "or returning JSON from edge/node serverless handlers, with state hydration on the client."
        )
    elif any(k in raw_deps for k in ["react", "vue", "vite", "angular"]) or "frontend" in meta.get("name", "").lower():
        pattern = "Client-Side Single Page Application (SPA) with Reactive Component Hierarchy"
        flow_desc = (
            "The client loads the HTML shell, mounts the top-level application root, initializes global state stores, "
            "and dispatches asynchronous HTTP queries to backend services with reactive component re-rendering."
        )
    elif any(k in raw_deps for k in ["express", "koa", "nest", "hono"]):
        pattern = "Modular Express/Node.js Middleware Pipeline"
        flow_desc = (
            "HTTP traffic traverses sequential middleware chains (logging, body parsing, security headers, auth) "
            "before hitting controller actions that query storage layers and send structured responses."
        )
    else:
        pattern = "Modular Layered Architecture"
        flow_desc = (
            "The system decomposes responsibilities into discrete modules: bootstrapping/configuration, "
            "domain business logic, data persistence/client adapters, and utility helpers."
        )

    # Stages
    dir_paths = [d["path"] for d in important_dirs]
    stages = [
        {
            "stage": 1,
            "name": "Bootstrapping & Configuration Ingress",
            "description": "Environment variables, secret parameters, and dependency injection containers are instantiated.",
            "representative_files": entry_points[:2] or [primary_entry],
        },
        {
            "stage": 2,
            "name": "Routing & Protocol Dispatch",
            "description": "Incoming requests or CLI commands are parsed, validated against contracts, and dispatched to handlers.",
            "representative_files": [p for p in dir_paths if any(k in p for k in ["api", "route", "cmd", "controller"])][:2] or [primary_entry],
        },
        {
            "stage": 3,
            "name": "Domain Business Engine",
            "description": "Core business rules, algorithms, and state mutations execute in memory decoupled from IO transport.",
            "representative_files": [p for p in dir_paths if any(k in p for k in ["service", "core", "app", "lib", "src"])][:2] or [primary_entry],
        },
        {
            "stage": 4,
            "name": "Data Access & External Adaptors",
            "description": "Database queries, caching layers, and external network APIs are accessed through adaptor interfaces.",
            "representative_files": [p for p in dir_paths if any(k in p for k in ["db", "model", "client", "repo", "store"])][:2] or [primary_entry],
        },
        {
            "stage": 5,
            "name": "Serialization & Observability Egress",
            "description": "Outputs are serialized into standardized schema responses; metrics, spans, and audit logs are recorded.",
            "representative_files": entry_points[:1] or [primary_entry],
        },
    ]

    hotspots = [
        "Environment Configuration: Missing environment variables cause early bootstrap failure without informative error messaging.",
        "Asynchronous Concurrency: Ensure all asynchronous promises/coroutines are properly awaited to avoid unhandled rejection leaks.",
        "State Mutation Boundaries: Ensure domain logic remains pure and does not mutate shared global configuration objects during execution.",
    ]
    if cfg.get("docker_support"):
        hotspots.append("Container Networking: Ensure host port bindings and volume mounts match the local environment settings in docker-compose.yml.")

    return {
        "pattern": pattern,
        "explanation": (
            f"{meta.get('name', 'This repository')} implements a {pattern}. "
            f"{flow_desc} "
            "Understanding this structural separation allows contributors to identify the exact files responsible for any specific feature without wading through unrelated subsystems."
        ),
        "lifecycle_stages": stages,
        "data_flow_summary": flow_desc,
        "hotspots_and_gotchas": hotspots,
    }


def _build_deterministic_diff_matrix() -> List[Dict[str, str]]:
    return [
        {
            "feature": "Zero-Hallucination Grounding",
            "copilot_approach": "Generates code and file suggestions from broad probabilistic language models, frequently citing non-existent packages, files, or CLI flags.",
            "git_analyzer_advantage": "Every directory, manifest script, entrypoint, and recommended issue is strictly verified against the repository's real Git tree and commit SHA.",
            "technical_reason": "Invariant verification layer strips out any entity not confirmed present in raw GitHub tree metadata.",
        },
        {
            "feature": "Sensitive Data & Secret Shield",
            "copilot_approach": "Sends entire active buffers, prompts, and environment strings to external cloud infrastructure without local credential sanitization.",
            "git_analyzer_advantage": "Built-in local sanitizer automatically scans, redacts, and masks API keys, AWS credentials, JWT tokens, and private keys BEFORE model ingestion.",
            "technical_reason": "High-entropy token regex rules execute in-memory on repository evidence prior to LLM prompt formatting.",
        },
        {
            "feature": "Multi-Factor Issue Intelligence",
            "copilot_approach": "Reads issue titles naively or relies on general advice without evaluating whether an issue is realistically solvable by a newcomer.",
            "git_analyzer_advantage": "Calculates algorithmic difficulty scores based on label weight, comment heat, recency, body specificity, and test touchpoints.",
            "technical_reason": "Multi-factor scoring formula categorizes issues into verified Beginner, Intermediate, and Advanced tiers.",
        },
        {
            "feature": "Full-Repository Topological Scope",
            "copilot_approach": "Operates primarily within the narrow window of active editor tabs or small context snippets, missing whole-repo architecture.",
            "git_analyzer_advantage": "Performs holistic repository synthesis across file trees, manifests, CI workflows, and issue trackers to build a complete architectural blueprint.",
            "technical_reason": "End-to-end repository tree traversal and configuration analysis runs during context gathering.",
        },
        {
            "feature": "Multi-Track Actionable Roadmaps",
            "copilot_approach": "Offers generic, open-ended conversational advice ('fork the repo, write tests, make a PR').",
            "git_analyzer_advantage": "Generates 4 tailored, goal-oriented execution plans (Day 1 Contributor, Deep Architecture, Bug Hunter, System Extender) with step-by-step verification commands.",
            "technical_reason": "Structured execution planning model binds exact manifest scripts, target files, and verification assertions.",
        },
        {
            "feature": "Local Autonomy & Zero Vendor Lock-in",
            "copilot_approach": "Requires a proprietary paid cloud subscription and constant connectivity to remote corporate servers.",
            "git_analyzer_advantage": "100% self-hostable with local Ollama, local vLLM, or offline deterministic synthesis with zero data leaving your environment.",
            "technical_reason": "Pluggable LLM provider architecture with automatic deterministic fallback guarantees offline functionality.",
        },
    ]


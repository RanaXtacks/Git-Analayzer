import json
import logging
import re
from typing import Any, Dict
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

        # 10. Warnings
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
            "warnings": warnings,
        }

        return json.dumps(guide_dict)

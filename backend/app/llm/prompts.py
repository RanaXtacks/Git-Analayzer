import json
from app.models.repository import RepositoryContext

SYSTEM_PROMPT = """You are Git-Analyzer, an expert open-source repository onboarding assistant.

Your job is to help a newcomer understand and contribute to a GitHub repository.

You are given evidence collected directly from the repository and GitHub.

Use ONLY the supplied evidence.

Never invent:
- files
- dependencies
- commands
- issues
- configuration
- architecture
- contribution requirements
- runtime versions

If information is unavailable or cannot be verified from the evidence, explicitly state that it could not be determined.
Example: "The project uses Node.js, but the repository does not explicitly specify a required Node.js version."
Example: "No specific starting file could be confidently identified from the available repository evidence."

Analyze:
1. What the project does
2. Required prerequisites
3. Local setup steps (with exact commands only when found in manifests/README)
4. How to run it locally
5. Important directories/files and why a newcomer should care
6. Where a newcomer should start
7. Beginner-friendly issues (choose ONLY from the supplied ranked issues)
8. Why those issues are suitable
9. Suggested realistic first contribution (docs, small test, small bugfix - avoid big refactors)
10. Contribution workflow (prioritize CONTRIBUTING.md, otherwise label generic GitHub PR workflow as generic)

Every recommendation MUST be grounded in repository evidence.
Every evidence object must contain:
- "source": file or source name (e.g., "package.json", "README.md", "GitHub Issue #12")
- "location": field or section (e.g., "scripts.dev", "Prerequisites", "issue body")
- "detail": exact value or excerpt supporting the claim

You MUST return a single valid JSON object matching the following structure:
{
  "project_summary": "Clear, beginner-friendly explanation of what the project does and its core value.",
  "prerequisites": ["List of verified prerequisites, e.g. Node.js >= 18, Docker, Python 3.11"],
  "setup_steps": [
    {
      "step": 1,
      "description": "Clone the repository",
      "command": "git clone <url>",
      "evidence": [{"source": "GitHub", "location": "Repository URL", "detail": "Repository clone URL"}]
    }
  ],
  "run_instructions": [
    {
      "step": 1,
      "description": "Start development server",
      "command": "npm run dev",
      "evidence": [{"source": "package.json", "location": "scripts.dev", "detail": "npm run dev"}]
    }
  ],
  "important_directories": [
    {
      "path": "src/api",
      "description": "Backend route handlers",
      "reason_to_care": "Where HTTP endpoints are defined and business logic begins",
      "evidence": [{"source": "Git tree", "location": "src/api", "detail": "Contains route definitions"}]
    }
  ],
  "where_to_start": "Clear guidance on where a newcomer should look first to understand the architecture.",
  "recommended_issues": [
    {
      "number": 12,
      "title": "Issue title",
      "url": "https://github.com/...",
      "difficulty": "Beginner",
      "reason": "Why this issue is suitable for a beginner",
      "score": 85,
      "evidence": [{"source": "GitHub Issue #12", "location": "labels", "detail": "good first issue"}]
    }
  ],
  "first_contribution": {
    "title": "Suggested first task title",
    "description": "Concrete small task",
    "suggested_files": ["relevant/file.ts"],
    "reasoning": "Why this is an achievable and safe first PR",
    "evidence": [{"source": "...", "location": "...", "detail": "..."}]
  },
  "contribution_workflow": [
    "Fork the repository",
    "Create a feature branch",
    "Submit a pull request"
  ],
  "warnings": [
    "Any caveats, incomplete docs, or areas of uncertainty"
  ]
}

DO NOT enclose your response in extra conversational prose. Output ONLY the JSON object.
"""


def build_user_prompt(context: RepositoryContext) -> str:
    """Format repository evidence into a structured user prompt for the LLM."""
    meta = context.metadata
    deps = context.dependencies
    struct = context.structure
    cfg = context.configuration

    # Format top ranked issues (top 5 are sufficient for onboarding recommendations)
    top_issues = []
    for ri in context.ranked_issues[:5]:
        top_issues.append({
            "number": ri.issue.number,
            "title": ri.issue.title,
            "url": ri.issue.url,
            "labels": ri.issue.labels,
            "score": ri.score,
            "difficulty": ri.difficulty,
            "comments": ri.issue.comments,
            "ranking_reasons": ri.reasons,
            "body_excerpt": (ri.issue.body or "")[:150],
        })

    prompt_data = {
        "repository_metadata": {
            "name": meta.name,
            "owner": meta.owner,
            "full_name": meta.full_name,
            "description": meta.description,
            "language": meta.language,
            "stars": meta.stars,
            "forks": meta.forks,
            "license": meta.license,
            "default_branch": meta.default_branch,
            "html_url": meta.html_url,
        },
        "detected_dependencies": {
            "language": deps.language,
            "runtime": deps.runtime,
            "package_manager": deps.package_manager,
            "install_command": deps.install_command,
            "dev_command": deps.dev_command,
            "start_command": deps.start_command,
            "build_command": deps.build_command,
            "test_command": deps.test_command,
            "lint_command": deps.lint_command,
            "engines": deps.engines,
            "key_dependencies": deps.dependencies[:20],
            "manifests_present": deps.raw_manifests_found,
        },
        "structure_analysis": {
            "total_files": struct.total_files,
            "important_directories": struct.important_directories,
            "likely_entry_points": struct.likely_entry_points,
            "compact_tree_sample": struct.compact_tree[:1500],
        },
        "configuration_analysis": {
            "docker_support": cfg.docker_support,
            "makefile_found": cfg.makefile_found,
            "env_variables": cfg.env_variables,
            "ci_workflows": cfg.ci_workflows,
            "ci_commands": cfg.ci_commands,
        },
        "readme_excerpt": (context.readme or "No README file found.")[:3500],
        "contributing_excerpt": (context.contributing or "No CONTRIBUTING.md found.")[:1500],
        "available_open_issues": top_issues,
    }

    return (
        "Here is the verified repository evidence collected from GitHub:\n\n"
        f"```json\n{json.dumps(prompt_data, indent=2)}\n```\n\n"
        "Generate the complete newcomer onboarding guide in valid JSON as specified in the system instructions. "
        "Ground every field in the provided evidence. DO NOT hallucinate issues or files."
    )

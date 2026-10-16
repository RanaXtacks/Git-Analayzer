import json
import logging
import re
from typing import Any, Dict, Optional
from pydantic import ValidationError

from app.models.guide import OnboardingGuide

logger = logging.getLogger("git_analyzer.llm.parser")


class GuideParseError(Exception):
    """Raised when LLM output cannot be parsed into a valid guide."""
    def __init__(self, message: str, raw_output: str):
        super().__init__(message)
        self.raw_output = raw_output


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extracts a JSON object from text, handling markdown fences or leading/trailing prose.
    """
    if not text or not isinstance(text, str):
        raise GuideParseError("Empty response received from LLM.", raw_output="")

    cleaned = text.strip()

    # 1. Direct parse attempt
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2. Markdown block extraction (```json ... ``` or ``` ... ```)
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # 3. First '{' to last '}' bracket extraction
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(candidate)
        except Exception:
            # Try removing common trailing commas before closing braces
            candidate_cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                return json.loads(candidate_cleaned)
            except Exception:
                pass

    raise GuideParseError("No valid JSON structure found in model output.", raw_output=text)


def parse_guide_response(text: str) -> OnboardingGuide:
    """
    Parses LLM response text into a validated OnboardingGuide model.
    Applies lenient normalization for minor model variations.
    """
    raw_dict = extract_json_from_text(text)

    # Lenient normalizations
    if "prerequisites" in raw_dict and isinstance(raw_dict["prerequisites"], str):
        raw_dict["prerequisites"] = [raw_dict["prerequisites"]]

    if "contribution_workflow" in raw_dict and isinstance(raw_dict["contribution_workflow"], str):
        raw_dict["contribution_workflow"] = [raw_dict["contribution_workflow"]]

    if "warnings" in raw_dict and isinstance(raw_dict["warnings"], str):
        raw_dict["warnings"] = [raw_dict["warnings"]]

    # Ensure first_contribution is a dict
    if "first_contribution" not in raw_dict or not isinstance(raw_dict["first_contribution"], dict):
        raw_dict["first_contribution"] = {
            "title": "Explore Documentation & Small Tests",
            "description": "Start by setting up the project locally and verifying the test suite.",
            "suggested_files": [],
            "reasoning": "Standard low-risk first contribution.",
            "evidence": [],
        }

    # Ensure differentiation_matrix is always present
    if "differentiation_matrix" not in raw_dict or not raw_dict["differentiation_matrix"]:
        from app.llm.deterministic import _build_deterministic_diff_matrix
        raw_dict["differentiation_matrix"] = _build_deterministic_diff_matrix()

    # Ensure execution_plans has at least fallback plans if model omitted it
    if "execution_plans" not in raw_dict or not raw_dict["execution_plans"]:
        from app.llm.deterministic import _build_deterministic_execution_plans
        raw_dict["execution_plans"] = _build_deterministic_execution_plans(
            meta={"name": "repository", "html_url": "https://github.com/repository"},
            deps={"install_command": None, "dev_command": None, "test_command": None, "manifests_present": []},
            struct={"likely_entry_points": []},
            cfg={},
            first_contrib_files=raw_dict.get("first_contribution", {}).get("suggested_files", []),
            important_dirs=raw_dict.get("important_directories", []),
            issues=raw_dict.get("recommended_issues", []),
        )

    # Ensure deep_architecture has at least fallback if omitted
    if "deep_architecture" not in raw_dict or not raw_dict["deep_architecture"]:
        from app.llm.deterministic import _build_deterministic_deep_architecture
        raw_dict["deep_architecture"] = _build_deterministic_deep_architecture(
            meta={"name": "repository"},
            deps={"key_dependencies": []},
            struct={"likely_entry_points": []},
            cfg={},
            important_dirs=raw_dict.get("important_directories", []),
        )

    try:
        return OnboardingGuide.model_validate(raw_dict)
    except ValidationError as e:
        logger.warning(f"Guide validation error: {e}")
        raise GuideParseError(f"Pydantic schema validation failed: {e}", raw_output=text)

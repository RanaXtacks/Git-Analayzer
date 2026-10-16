import logging
from typing import Optional
from app.llm.base import LLMProvider, LLMUnavailableError
from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.llm.parser import parse_guide_response, GuideParseError
from app.llm.deterministic import DeterministicProvider
from app.guide.verifier import EvidenceVerifier
from app.models.guide import OnboardingGuide
from app.models.repository import RepositoryContext
from app.config import get_settings

logger = logging.getLogger("git_analyzer.guide.generator")


class GuideGenerator:
    """Orchestrates LLM inference, schema parsing, retry correction, and evidence verification."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.verifier = EvidenceVerifier()

    async def generate_guide(self, context: RepositoryContext) -> OnboardingGuide:
        user_prompt = build_user_prompt(context)
        raw_output: str = ""

        try:
            raw_output = await self.llm.generate(SYSTEM_PROMPT, user_prompt)
        except (LLMUnavailableError, LLMProviderError, LLMTimeoutError) as e:
            settings = get_settings()
            if settings.AUTO_FALLBACK_TO_DETERMINISTIC:
                logger.warning(f"Inference error ({e}). Using deterministic evidence synthesis fallback.")
                fallback = DeterministicProvider()
                raw_output = await fallback.generate(SYSTEM_PROMPT, user_prompt)
            else:
                raise

        guide: Optional[OnboardingGuide] = None
        try:
            guide = parse_guide_response(raw_output)
        except GuideParseError as e:
            logger.warning(f"Initial LLM response failed validation: {e}. Retrying with correction prompt once...")
            correction_prompt = (
                f"Your previous output failed JSON validation with the following error:\n{str(e)}\n\n"
                f"Previous output snippet:\n{raw_output[:1000]}\n\n"
                "Please fix the error and output ONLY the valid JSON object according to the schema."
            )
            retry_output = await self.llm.generate(SYSTEM_PROMPT, correction_prompt)
            guide = parse_guide_response(retry_output)

        # Apply strict evidence verification
        verified_guide = self.verifier.verify_guide(guide, context)
        return verified_guide

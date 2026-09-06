from app.ai.llm import LLMProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.core.config import LLM_PROVIDER


def get_llm_provider() -> LLMProvider:
    """
    Returns the configured LLM provider.
    """

    if LLM_PROVIDER == "gemini":
        return GeminiProvider()

    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )
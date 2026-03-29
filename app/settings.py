import os
from typing import Literal, TypeAlias, cast

from dotenv import load_dotenv

ExtractorStrategySetting: TypeAlias = Literal["deterministic", "ai"]
DEFAULT_EXTRACTOR_STRATEGY: ExtractorStrategySetting = "deterministic"
DEFAULT_OPENAI_MODEL = "gpt-5-mini"

load_dotenv()


class InvalidExtractorStrategyError(ValueError):
    """Raised when EXTRACTOR_STRATEGY is set to an unsupported value."""


class OpenAIConfigurationError(RuntimeError):
    """Raised when required OpenAI configuration is missing."""


def get_extractor_strategy() -> ExtractorStrategySetting:
    configured_strategy = os.getenv(
        "EXTRACTOR_STRATEGY", DEFAULT_EXTRACTOR_STRATEGY
    ).strip()

    if configured_strategy in {"deterministic", "ai"}:
        return cast(ExtractorStrategySetting, configured_strategy)

    raise InvalidExtractorStrategyError(
        "EXTRACTOR_STRATEGY must be one of: deterministic, ai."
    )


def get_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    raise OpenAIConfigurationError(
        "OPENAI_API_KEY must be set to use the AI extractor."
    )


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

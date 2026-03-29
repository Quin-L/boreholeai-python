"""BoreholeAI Python SDK — digitise borehole logs programmatically."""

from boreholeai._types import FileResult, JobResult
from boreholeai._version import __version__
from boreholeai.client import BoreholeAI
from boreholeai.exceptions import (
    AuthenticationError,
    BoreholeAIError,
    InsufficientCreditsError,
    JobFailedError,
    RateLimitError,
    ServerError,
)

__all__ = [
    "BoreholeAI",
    "__version__",
    "AuthenticationError",
    "BoreholeAIError",
    "FileResult",
    "InsufficientCreditsError",
    "JobFailedError",
    "JobResult",
    "RateLimitError",
    "ServerError",
]

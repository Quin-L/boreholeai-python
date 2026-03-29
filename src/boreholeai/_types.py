"""Response types for the BoreholeAI SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileResult:
    """A single downloaded result file."""

    filename: str
    path: Path


@dataclass
class JobResult:
    """Result of processing a single job (one or more input files)."""

    job_id: str
    status: str
    num_pages: int
    credits_used: int
    files: list[FileResult] = field(default_factory=list)

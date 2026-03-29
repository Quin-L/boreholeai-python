"""Low-level HTTP calls to the BoreholeAI worker API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from boreholeai.exceptions import (
    AuthenticationError,
    BoreholeAIError,
    InsufficientCreditsError,
    RateLimitError,
    ServerError,
)

DEFAULT_BASE_URL = "https://boreholeai-worker-7b5nhwzhwq-uc.a.run.app"
DEFAULT_TIMEOUT = 120.0


class APIClient:
    """Thin wrapper around httpx for authenticated requests to the worker."""

    def __init__(self, api_key: str, base_url: str, timeout: float):
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def create_job(self, file_paths: list[Path]) -> dict[str, Any]:
        """POST /v1/jobs — upload files and create a job.

        Returns {"job_id": ..., "num_pages": ..., "credits_remaining": ...}.
        """
        files = [
            ("files", (p.name, p.read_bytes()))
            for p in file_paths
        ]
        resp = self._client.post("/v1/jobs", files=files)
        _raise_for_status(resp)
        return resp.json()

    def get_job(self, job_id: str) -> dict[str, Any]:
        """GET /v1/jobs/{id} — poll job status."""
        resp = self._client.get(f"/v1/jobs/{job_id}")
        _raise_for_status(resp)
        return resp.json()

    def get_results(self, job_id: str) -> dict[str, Any]:
        """GET /v1/jobs/{id}/results — signed download URLs."""
        resp = self._client.get(f"/v1/jobs/{job_id}/results")
        _raise_for_status(resp)
        return resp.json()

    def download_file(self, url: str) -> bytes:
        """Download a file from a signed URL."""
        resp = httpx.get(url, timeout=self._client.timeout)
        resp.raise_for_status()
        return resp.content


def _raise_for_status(resp: httpx.Response) -> None:
    """Convert HTTP errors to SDK exceptions."""
    if resp.is_success:
        return

    detail = ""
    try:
        detail = resp.json().get("detail", "")
    except Exception:
        detail = resp.text

    if resp.status_code == 401:
        raise AuthenticationError(detail or "Invalid API key", 401)
    if resp.status_code == 402:
        raise InsufficientCreditsError(detail or "Insufficient credits", 402)
    if resp.status_code == 429:
        raise RateLimitError(detail or "Rate limited", 429)
    if resp.status_code >= 500:
        raise ServerError(detail or "Server error", resp.status_code)
    raise BoreholeAIError(detail or f"HTTP {resp.status_code}", resp.status_code)

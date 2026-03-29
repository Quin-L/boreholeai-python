"""BoreholeAI Python SDK client."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from boreholeai._api import APIClient, DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from boreholeai._files import collect_files
from boreholeai._types import FileResult, JobResult
from boreholeai.exceptions import JobFailedError

# Polling configuration
_POLL_INITIAL_INTERVAL = 2.0   # seconds
_POLL_MAX_INTERVAL = 10.0      # seconds
_POLL_BACKOFF_FACTOR = 1.5

# Default output directory
_DEFAULT_OUTPUT_DIR = "./boreholeai_output"


class BoreholeAI:
    """Client for the BoreholeAI API.

    Usage::

        from boreholeai import BoreholeAI

        client = BoreholeAI(api_key="bhai_xxx")

        # Single file
        results = client.process_documents("borehole.pdf")

        # Folder — all PDFs + images processed together, merged output
        results = client.process_documents("./logs/", output_dir="./results")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        self._api = APIClient(api_key=api_key, base_url=base_url, timeout=timeout)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._api.close()

    def __enter__(self) -> BoreholeAI:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def process_documents(
        self,
        input_path: str | Path,
        *,
        output_dir: str | Path = _DEFAULT_OUTPUT_DIR,
    ) -> JobResult:
        """Upload files, process them, and download results.

        Args:
            input_path: Path to a single file or a directory of files.
                Supported formats: PDF, PNG, JPG, JPEG, TIF, TIFF, WebP.
            output_dir: Directory to save result files. Created if it doesn't exist.

        Returns:
            JobResult with job metadata and list of downloaded files.

        Raises:
            FileNotFoundError: If input_path doesn't exist.
            ValueError: If no supported files found.
            AuthenticationError: If API key is invalid.
            InsufficientCreditsError: If not enough credits.
            JobFailedError: If processing fails on the server.
        """
        files = collect_files(input_path)
        out = Path(output_dir).resolve()
        out.mkdir(parents=True, exist_ok=True)

        # Upload
        total_files = len(files)
        _print_status(f"Uploading {total_files} file(s)...")
        job_data = self._api.create_job(files)
        job_id = job_data["job_id"]
        num_pages = job_data["num_pages"]
        _print_status(
            f"Job {job_id[:8]}... created — "
            f"{num_pages} page(s), {total_files} file(s)"
        )

        # Poll
        result = self._poll_until_done(job_id)

        # Download results
        downloaded = self._download_results(job_id, out)

        return JobResult(
            job_id=job_id,
            status=result["status"],
            num_pages=num_pages,
            credits_used=num_pages,
            files=downloaded,
        )

    def _poll_until_done(self, job_id: str) -> dict:
        """Poll GET /v1/jobs/{id} until status is completed or failed."""
        interval = _POLL_INITIAL_INTERVAL

        while True:
            data = self._api.get_job(job_id)
            status = data["status"]

            if status == "completed":
                _print_status("Processing complete!")
                return data

            if status == "failed":
                error = data.get("error_message", "Unknown error")
                raise JobFailedError(f"Job {job_id} failed: {error}")

            # Show progress if available
            progress = data.get("progress") or {}
            pages_done = progress.get("pages_done", 0)
            pages_total = progress.get("pages_total", "?")
            _print_status(
                f"Processing... {pages_done}/{pages_total} pages "
                f"[{status}]"
            )

            time.sleep(interval)
            interval = min(interval * _POLL_BACKOFF_FACTOR, _POLL_MAX_INTERVAL)

    def _download_results(self, job_id: str, output_dir: Path) -> list[FileResult]:
        """Download all result files to output_dir."""
        results_data = self._api.get_results(job_id)
        downloaded: list[FileResult] = []

        for file_info in results_data.get("files", []):
            filename = file_info["filename"]
            url = file_info["url"]

            _print_status(f"Downloading {filename}...")
            content = self._api.download_file(url)

            dest = output_dir / filename
            dest.write_bytes(content)
            downloaded.append(FileResult(filename=filename, path=dest))

        _print_status(
            f"Downloaded {len(downloaded)} file(s) to {output_dir}"
        )
        return downloaded


def _print_status(message: str) -> None:
    """Print a status message to stderr (doesn't interfere with stdout piping)."""
    print(f"  {message}", file=sys.stderr, flush=True)

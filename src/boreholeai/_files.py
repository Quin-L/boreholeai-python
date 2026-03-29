"""File scanning and validation utilities."""

from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}


def collect_files(input_path: str | Path) -> list[Path]:
    """Collect valid files from a path (single file or directory).

    Returns a sorted list of Paths with supported extensions.
    Raises FileNotFoundError if the path doesn't exist.
    Raises ValueError if no supported files are found.
    """
    path = Path(input_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    if path.is_file():
        _validate_extension(path)
        return [path]

    if path.is_dir():
        files = sorted(
            f for f in path.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if not files:
            raise ValueError(
                f"No supported files found in {path}. "
                f"Accepted: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
        return files

    raise ValueError(f"Path is neither a file nor a directory: {path}")


def _validate_extension(path: Path) -> None:
    """Raise ValueError if the file extension is not supported."""
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {path.suffix}. "
            f"Accepted: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

# ABOUTME: Figure-store helpers for the web interface - directory paths, cleanup, name validation.
# ABOUTME: PNGs live under tmp_dev/web_figures/ and are served via the /figures/<name>.png endpoint.

import re
from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
FIGURES_DIR: Path = PROJECT_ROOT / "tmp_dev" / "web_figures"

_FIGURE_NAME_RE = re.compile(r"[0-9a-f]{32}\.png")


def clear_figures_dir() -> None:
    """Delete every file in FIGURES_DIR and ensure the directory exists.

    Tolerates a missing directory. Subdirectories (none expected) are skipped.
    """
    if FIGURES_DIR.exists():
        for entry in FIGURES_DIR.iterdir():
            if entry.is_file():
                entry.unlink()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def validate_figure_filename(name: str) -> bool:
    """Return True iff ``name`` is a lowercase 32-hex UUID followed by ``.png``.

    Only lowercase hex is accepted. Names with path separators, leading dots,
    traversal sequences, mixed case, or any other extension are rejected.
    """
    return _FIGURE_NAME_RE.fullmatch(name) is not None

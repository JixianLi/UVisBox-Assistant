# ABOUTME: Web entry point - `python -m uvisbox_assistant.web` launches uvicorn at 127.0.0.1:8000.
# ABOUTME: Activates FileRenderer before importing the FastAPI app so plot tools save PNGs to disk.

"""Launch the FastAPI web server with the FileRenderer active."""

from uvisbox_assistant.utils.renderer import FileRenderer, set_renderer

from .figures import FIGURES_DIR


def main() -> None:
    """Set the renderer, import the app, and run uvicorn on localhost:8000."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    set_renderer(FileRenderer(FIGURES_DIR))

    # Import uvicorn + app AFTER the renderer is set so any module-level
    # tool wiring picks up FileRenderer behavior (defensive - today nothing
    # at import time runs a tool, but this keeps the order explicit).
    import uvicorn
    from .server import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()

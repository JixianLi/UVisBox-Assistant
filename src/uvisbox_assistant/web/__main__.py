# ABOUTME: Web entry point - `python -m uvisbox_assistant.web` launches uvicorn at 127.0.0.1:8000.
# ABOUTME: Forces matplotlib Agg backend (thread-safe) and activates FileRenderer before importing the app.

"""Launch the FastAPI web server with the FileRenderer active."""

# Force Agg before any other matplotlib import. Plot tools run on a worker
# thread in web mode; GUI backends (MacOSX, TkAgg, Qt) cannot create figures
# off the main thread. Agg is non-interactive and thread-safe, which matches
# our use case: render and savefig, never display a window.
import matplotlib

matplotlib.use("Agg", force=True)

from uvisbox_assistant.utils.renderer import FileRenderer, set_renderer

from .figures import FIGURES_DIR


def main() -> None:
    """Set the renderer, import the app, and run uvicorn on localhost:8000."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    set_renderer(FileRenderer(FIGURES_DIR))

    import uvicorn
    from .server import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()

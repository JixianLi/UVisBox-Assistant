# Phase 05 — Production Build Wiring + Acceptance

## Scope

Wire the React `web/` build output into FastAPI as static assets so the
whole interface is served same-origin in production. Update project
documentation with run instructions for the web mode. Run the full
acceptance test suite and a manual end-to-end check of the prompt → plot
→ image workflow.

## Implementation

### Task 1 — Static-files mount in `server.py`

Modify `src/uvisbox_assistant/web/server.py`. Mount `web/dist/` at the
root path when the directory exists. Do not error out when it doesn't
(dev workflow uses the Vite proxy and ignores this path).

```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path

WEB_DIST = Path(__file__).resolve().parent.parent.parent.parent / "web" / "dist"

# ... existing endpoints ...

if WEB_DIST.exists():
    # Mount LAST so /ws and /figures take precedence
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
```

Place the mount *after* the WebSocket route and `/figures` route so
FastAPI matches those first. `html=True` makes StaticFiles fall back to
`index.html` for client-side routes (the React app has none today, but
this is a no-cost insurance against future single-page-app routes).

### Task 2 — Run the production build

In `web/`:

```bash
npm run build
```

Verify `web/dist/index.html` and `web/dist/assets/` exist. Confirm
`dist/index.html` references hashed asset filenames matching files
present in `dist/assets/`.

Add `web/dist/` to the project `.gitignore` if not already covered. The
production build is a build artifact, not source.

### Task 3 — README documentation

Append a new section to the project root `README.md` — keep it short.
Heading: `## Web Interface (preview)`. Cover:

- Dev workflow:
  ```bash
  # Terminal 1: Python server
  python -m uvisbox_assistant.web

  # Terminal 2: Vite dev server with HMR
  cd web && npm install && npm run dev
  # Open http://localhost:5173
  ```
- Production workflow:
  ```bash
  cd web && npm install && npm run build
  cd ..
  python -m uvisbox_assistant.web
  # Open http://127.0.0.1:8000
  ```
- One-line note: CLI REPL (`python -m uvisbox_assistant`) is unaffected
  and remains the primary interface.
- Link to `docs/plans/web-interface/design.md` for the architecture
  overview.

No new docs files. README addition only.

### Task 4 — Verify production mount

Run the production workflow from Task 3. Confirm:
- `GET http://127.0.0.1:8000/` returns the React app's `index.html`.
- Static assets under `/assets/<hash>.js` and `/assets/<hash>.css` load
  with 200.
- `/ws` upgrades to WebSocket (same as dev).
- `/figures/<id>.png` serves PNGs (same as dev).
- The full prompt → image workflow runs end-to-end in the browser at
  port 8000 (no port 5173, no Vite proxy).

### Task 5 — Acceptance test run

Execute the full project acceptance suite:

```bash
python tests/test.py --acceptance
```

This includes unit + uvisbox_interface + llm_integration + any E2E
tests. All must pass. Capture the summary line in the commit message.

### Task 6 — Manual acceptance checklist

End-to-end smoke (production build, single FastAPI process):

1. Start `python -m uvisbox_assistant.web`.
2. Open `http://127.0.0.1:8000`.
3. Prompt: "Generate 30 curves and plot functional boxplot".
   - Trace panel shows: `user → model` (prompt), `model → vis_tool`
     (tool_call for plot), `vis_tool → model` (tool_result).
   - Chat shows the rendered PNG inline.
4. Hybrid command: "median color blue".
   - Trace panel shows the hybrid acknowledgement and a re-render
     `tool_call` + `tool_result`.
   - Chat shows a new PNG with the updated median color.
5. Click the reset button. Both panels clear; input is re-enabled.
6. Issue a new prompt — confirms session is fresh.
7. Reload the browser — chat + trace are empty, server starts a new
   session.
8. CLI REPL parallel test: in a separate terminal,
   `python -m uvisbox_assistant`, generate data, plot — a window opens
   as before. (Confirms `WindowRenderer` default still applies when the
   web entry point isn't used.)

## Verification

Each manual step in Task 6 produces the expected result. Acceptance
suite green.

## Validation

- No regressions in any test category vs. Phase 04 baseline.
- `--acceptance` is the binding gate.

## Acceptance Criteria

- [ ] `server.py` mounts `web/dist/` at `/` when present, after the
      WebSocket and figures routes.
- [ ] `npm run build` in `web/` produces a working production bundle.
- [ ] `web/dist/` is git-ignored.
- [ ] README contains a "Web Interface" section covering dev and prod
      workflows.
- [ ] Production single-process workflow serves the React app on port
      8000 and runs the full prompt-to-image cycle.
- [ ] CLI REPL still opens windows and is unaffected by the web entry
      point.
- [ ] Manual acceptance checklist (Task 6) passes every step.
- [ ] `python tests/test.py --acceptance` passes.

## Git Commit

```
feat(web): serve React build same-origin; document run workflows

Mounts web/dist/ via FastAPI StaticFiles so the production interface
runs in a single Python process at http://127.0.0.1:8000. Updates
README with dev and production workflows. Acceptance suite passes.
```

Include: `src/uvisbox_assistant/web/server.py`, `README.md`,
`.gitignore` (if updated). Do not commit `web/dist/`.

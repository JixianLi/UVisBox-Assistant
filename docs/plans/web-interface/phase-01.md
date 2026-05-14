# Phase 01 — Renderer Abstraction + vis_tools Refactor

## Scope

Introduce the `Renderer` abstraction (Protocol + `WindowRenderer` +
`FileRenderer` + a `contextvars.ContextVar`) and refactor every plot
function in `vis_tools.py` to render through it. Default contextvar is
`WindowRenderer`, so the CLI REPL is byte-identical after this phase. No
web server yet.

Also add a `TOOL_REGISTRY: dict[str, Callable]` at the bottom of
`vis_tools.py` mapping `_tool_name` strings to the corresponding plot
function — used in Phase 03 for hybrid auto-rerender.

## Implementation

### Task 1 — Create `src/uvisbox_assistant/utils/renderer.py`

New file. Contents:

- `ABOUTME:` header (2 lines per project convention).
- `Renderer` Protocol with two methods:
  - `show_matplotlib(self, fig) -> Optional[str]`
  - `show_pyvista(self, plotter_factory: Callable[..., Plotter]) -> Optional[str]`
  Both return the PNG path when the renderer is file-based, `None` when
  it's window-based.
- `WindowRenderer` class:
  - `show_matplotlib(fig)`: `plt.show(block=False); plt.pause(0.1); return None`
  - `show_pyvista(plotter_factory)`: construct via
    `plotter_factory()` (factory uses its default, which for
    `BackgroundPlotter` opens a window); return `None`.
- `FileRenderer` class:
  - Constructor: `__init__(self, out_dir: Path)`. Creates `out_dir` if
    missing.
  - `show_matplotlib(fig)`: write to `out_dir / f"{uuid4().hex}.png"`
    via `fig.savefig(path, dpi=150, bbox_inches="tight")`, then
    `plt.close(fig)`. Return string path.
  - `show_pyvista(plotter_factory)`: call
    `plotter = plotter_factory(off_screen=True)`. (Tools will pass a
    factory that respects this kwarg — see Task 2.) After the caller
    has built the scene, the renderer screenshots to
    `out_dir / f"{uuid4().hex}.png"`, calls `plotter.close()`, returns
    the path.

There is one subtlety in the PyVista path: today, tools construct the
plotter, then add meshes/glyphs/text to it. With the renderer
abstraction, the plotter must be constructed by the renderer (so it can
choose `off_screen`), but the scene-building must still happen in the
tool. Solution: the tool passes both a `plotter_factory` (lambda that
calls `BackgroundPlotter(...)` or `pv.Plotter(off_screen=True, ...)`)
and a `build_scene(plotter)` callable. The renderer signature becomes:

```python
def show_pyvista(
    self,
    plotter_factory: Callable[..., Plotter],
    build_scene: Callable[[Plotter], None],
) -> Optional[str]: ...
```

`WindowRenderer` calls `plotter_factory()` (no off_screen kwarg —
defaults to `BackgroundPlotter()` which opens a window), then
`build_scene(plotter)`, returns `None`. `FileRenderer` calls
`plotter_factory(off_screen=True)`, then `build_scene(plotter)`, then
screenshots + closes.

- `current_renderer: ContextVar[Renderer] = ContextVar("renderer", default=WindowRenderer())`
- Helper: `set_renderer(renderer: Renderer) -> contextvars.Token` (thin
  wrapper around `current_renderer.set()` for clarity in entry points).

### Task 2 — Refactor `src/uvisbox_assistant/tools/vis_tools.py`

For every plot function (the file has 6 documented + helpers; refactor
**every** `plt.show(block=False)` callsite at lines 129, 270, 356, 466,
570, 672, 887 and every `BackgroundPlotter()` site at lines 751, 973,
1071, 1156 — verify the count after reading the file):

**Matplotlib pattern (today):**

```python
plt.show(block=False)
plt.pause(0.1)
return {"status": "success", "message": "...", "_vis_params": {...}}
```

**Matplotlib pattern (after):**

```python
from uvisbox_assistant.utils.renderer import current_renderer

renderer = current_renderer.get()
path = renderer.show_matplotlib(fig)
result = {"status": "success", "message": "...", "_vis_params": {...}}
if path is not None:
    result["_figure_path"] = path
return result
```

Note: `fig` must be the matplotlib `Figure` object. If the current code
uses `plt.subplots()` and only retains `ax`, capture `fig` too.

**PyVista pattern (today):**

```python
plotter = BackgroundPlotter()
squid_glyph_3D(positions=..., ensemble_vectors=..., ax=plotter)
plotter.add_text("...", position="upper_edge", ...)
return {"status": "success", ...}
```

**PyVista pattern (after):**

```python
from uvisbox_assistant.utils.renderer import current_renderer

def plotter_factory(**kwargs):
    if kwargs.get("off_screen"):
        return pv.Plotter(off_screen=True)
    return BackgroundPlotter()

def build_scene(plotter):
    squid_glyph_3D(positions=..., ensemble_vectors=..., ax=plotter)
    plotter.add_text("...", position="upper_edge", ...)

renderer = current_renderer.get()
path = renderer.show_pyvista(plotter_factory, build_scene)
result = {"status": "success", ...}
if path is not None:
    result["_figure_path"] = path
return result
```

Keep all existing behavior (text overlays, parameter formatting,
`_vis_params` content). The only changes are: (1) the rendering call and
(2) the optional `_figure_path` field.

### Task 3 — Add `TOOL_REGISTRY` to `vis_tools.py`

Append at the bottom of the file (after all function definitions):

```python
TOOL_REGISTRY: Dict[str, Callable[..., Dict]] = {
    "plot_functional_boxplot": plot_functional_boxplot,
    "plot_curve_boxplot": plot_curve_boxplot,
    "plot_contour_boxplot": plot_contour_boxplot,
    "plot_probabilistic_marching_squares": plot_probabilistic_marching_squares,
    "plot_uncertainty_lobes": plot_uncertainty_lobes,
    "plot_squid_glyph_2D": plot_squid_glyph_2D,
    # Include any 3D / additional plot_* functions present in the file.
    # The complete set must match the `_tool_name` values produced in
    # each function's `_vis_params` dict.
}
```

Verify by grepping `_tool_name` in `vis_tools.py` and ensuring every
distinct value has a registry entry. This dict is consumed by the
hybrid auto-rerender flow in Phase 03.

### Task 4 — Unit tests: `tests/unit/test_renderer.py`

New file. Cover:

- `WindowRenderer.show_matplotlib` returns `None`. Stub `plt.show` and
  `plt.pause` to no-ops so the test doesn't open windows in CI.
- `FileRenderer.show_matplotlib` writes a file and returns its path.
  Use a `tmp_path` pytest fixture and a real `matplotlib.figure.Figure`
  with a trivial plot.
- `FileRenderer` creates `out_dir` if it doesn't exist.
- `FileRenderer.show_pyvista` calls the factory with `off_screen=True`,
  runs `build_scene`, screenshots, closes, returns the path. Stub the
  plotter with a `MagicMock` that records calls; assert
  `factory.called_with(off_screen=True)`, `screenshot` called with the
  expected path, `close` called.
- `current_renderer.get()` returns `WindowRenderer` by default.
- Setting the contextvar to `FileRenderer` inside a `with` block
  scopes correctly (the default returns afterwards).

### Task 5 — Integration tests: `tests/uvisbox_interface/test_file_renderer.py`

New file. 0 LLM calls. For each plot function in `TOOL_REGISTRY`:

1. Generate minimal valid input data (reuse the existing data-generation
   helpers in `data_tools.py` if they exist, otherwise create small
   numpy arrays and save to a tmp `.npy`).
2. Activate `FileRenderer(tmp_path)` via `current_renderer.set()`.
3. Call the plot function.
4. Assert: `result["status"] == "success"`, `result["_figure_path"]`
   exists on disk, file is non-empty, file is a valid PNG (magic
   bytes `\x89PNG`).
5. Reset the contextvar.

PyVista tests: skip if `pv.Plotter(off_screen=True)` raises (CI without
OpenGL). Mark such tests with `pytest.mark.requires_opengl` so the
acceptance run can detect environment issues without aborting.

## Verification

After each task:

- **Task 1:** `python -c "from uvisbox_assistant.utils.renderer import current_renderer, WindowRenderer, FileRenderer"` runs without error.
- **Task 2:** Launch the REPL — `python -m uvisbox_assistant` — generate
  test data and produce a matplotlib plot. Window must open (proves
  `WindowRenderer` is the default and behavior is preserved).
- **Task 3:** `python -c "from uvisbox_assistant.tools.vis_tools import TOOL_REGISTRY; print(sorted(TOOL_REGISTRY))"` shows the full set.
- **Task 4–5:** `pytest tests/unit/test_renderer.py tests/uvisbox_interface/test_file_renderer.py -v` passes.

## Validation

- Run the project's pre-planning test suite:
  `python tests/test.py --pre-planning`. Zero regressions.
- Manual smoke: in the REPL, run one matplotlib plot and one PyVista
  plot. Both must open windows (REPL invariant).

## Acceptance Criteria

- [ ] `src/uvisbox_assistant/utils/renderer.py` exists with `Renderer`,
      `WindowRenderer`, `FileRenderer`, `current_renderer`.
- [ ] Every `plt.show(block=False)` and `BackgroundPlotter()` call in
      `vis_tools.py` is replaced with the renderer pattern.
- [ ] `TOOL_REGISTRY` exists at the bottom of `vis_tools.py` and covers
      every `_tool_name` value produced by the file.
- [ ] `tests/unit/test_renderer.py` passes (all cases).
- [ ] `tests/uvisbox_interface/test_file_renderer.py` passes for every
      matplotlib tool. PyVista tools either pass or are
      `requires_opengl`-skipped with a clear reason.
- [ ] `python tests/test.py --pre-planning` passes.
- [ ] Manual REPL smoke: a matplotlib plot and a PyVista plot both
      open windows as before.

## Git Commit

```
feat(renderer): add Renderer abstraction; refactor vis_tools

Introduces WindowRenderer (default) and FileRenderer selected via a
contextvar so REPL behavior is unchanged while web mode can write PNGs.
Refactors all vis_tools.py rendering callsites onto the abstraction and
adds TOOL_REGISTRY for hybrid auto-rerender in Phase 03.
```

Include: `src/uvisbox_assistant/utils/renderer.py`,
`src/uvisbox_assistant/tools/vis_tools.py`,
`tests/unit/test_renderer.py`,
`tests/uvisbox_interface/test_file_renderer.py`.

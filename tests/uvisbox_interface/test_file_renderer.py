# ABOUTME: Integration tests that activate FileRenderer and verify every TOOL_REGISTRY plot writes a PNG.
# ABOUTME: Matplotlib tools always run; PyVista tools skip when off-screen rendering is unavailable.
"""FileRenderer integration tests covering every entry in TOOL_REGISTRY.

For each plot function, activate FileRenderer via the contextvar, call the
function with minimal valid synthetic data, and assert the returned
``_figure_path`` points to a real PNG on disk. 0 LLM calls.
"""

import numpy as np
import pyvista as pv
import pytest

from uvisbox_assistant.tools.vis_tools import TOOL_REGISTRY
from uvisbox_assistant.utils.renderer import (
    FileRenderer,
    current_renderer,
    set_renderer,
)


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


# ============================================================================
# Synthetic data fixtures (copied / extended from test_tool_interfaces.py)
# ============================================================================


@pytest.fixture
def curves_2d_path(tmp_path):
    """2D curves: shape (n_curves, n_points)."""
    rng = np.random.default_rng(0)
    curves = rng.standard_normal((30, 100)).cumsum(axis=1)
    path = tmp_path / "curves_2d.npy"
    np.save(path, curves)
    return str(path)


@pytest.fixture
def curves_3d_path(tmp_path):
    """3D curves: shape (n_curves, n_points, 2)."""
    rng = np.random.default_rng(1)
    n_curves, n_points = 25, 50
    t = np.linspace(0, 2 * np.pi, n_points)
    curves = np.zeros((n_curves, n_points, 2))
    for i in range(n_curves):
        radius = 1.0 + rng.standard_normal() * 0.2
        curves[i, :, 0] = radius * np.cos(t) + rng.standard_normal(n_points) * 0.1
        curves[i, :, 1] = radius * np.sin(t) + rng.standard_normal(n_points) * 0.1
    path = tmp_path / "curves_3d.npy"
    np.save(path, curves)
    return str(path)


@pytest.fixture
def scalar_field_2d_ensemble_path(tmp_path):
    """2D scalar field ensemble: shape (nx, ny, n_ensemble)."""
    rng = np.random.default_rng(2)
    field = rng.standard_normal((30, 30, 10))
    path = tmp_path / "scalar_field_2d.npy"
    np.save(path, field)
    return str(path)


@pytest.fixture
def vectors_2d_paths(tmp_path):
    """2D ensemble vectors and positions for glyphs.

    Returns (vectors_path, positions_path).
    - positions: (n_positions, 2)
    - vectors:   (n_positions, n_ensemble, 2)
    """
    rng = np.random.default_rng(3)
    n_positions = 5
    n_ensemble = 20
    positions = rng.random((n_positions, 2)) * 10
    vectors = rng.standard_normal((n_positions, n_ensemble, 2))
    positions_path = tmp_path / "positions_2d.npy"
    vectors_path = tmp_path / "vectors_2d.npy"
    np.save(positions_path, positions)
    np.save(vectors_path, vectors)
    return str(vectors_path), str(positions_path)


@pytest.fixture
def triangle_mesh_paths(tmp_path):
    """Triangular mesh ensemble: field (n_points, n_ensemble), triangles (n_tris, 3), points (n_points, 2)."""
    rng = np.random.default_rng(4)
    # Build a small regular grid of points and triangulate.
    nx, ny = 8, 8
    xs, ys = np.meshgrid(np.linspace(0, 1, nx), np.linspace(0, 1, ny))
    points = np.column_stack([xs.ravel(), ys.ravel()]).astype(np.float64)

    triangles = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            v0 = j * nx + i
            v1 = v0 + 1
            v2 = v0 + nx
            v3 = v2 + 1
            triangles.append([v0, v1, v2])
            triangles.append([v1, v3, v2])
    triangles = np.asarray(triangles, dtype=np.int64)

    n_points = points.shape[0]
    n_ensemble = 10
    # Smooth scalar field plus noise so an isovalue ~0.5 gives a meaningful contour.
    base = np.sin(2 * np.pi * points[:, 0]) * np.cos(2 * np.pi * points[:, 1])
    field = base[:, None] + rng.standard_normal((n_points, n_ensemble)) * 0.1

    field_path = tmp_path / "tri_field.npy"
    points_path = tmp_path / "tri_points.npy"
    triangles_path = tmp_path / "tri_triangles.npy"
    np.save(field_path, field)
    np.save(points_path, points)
    np.save(triangles_path, triangles)
    return str(field_path), str(triangles_path), str(points_path)


@pytest.fixture
def vectors_3d_paths(tmp_path):
    """3D ensemble vectors and positions: (n_positions, 3) and (n_positions, n_ensemble, 3)."""
    rng = np.random.default_rng(5)
    n_positions = 4
    n_ensemble = 12
    positions = rng.random((n_positions, 3)) * 5
    vectors = rng.standard_normal((n_positions, n_ensemble, 3))
    positions_path = tmp_path / "positions_3d.npy"
    vectors_path = tmp_path / "vectors_3d.npy"
    np.save(positions_path, positions)
    np.save(vectors_path, vectors)
    return str(vectors_path), str(positions_path)


@pytest.fixture
def scalar_field_3d_ensemble_path(tmp_path):
    """3D scalar field ensemble: shape (nx, ny, nz, n_ensemble)."""
    rng = np.random.default_rng(6)
    # Keep volume small so marching cubes is quick.
    nx, ny, nz, n_ens = 10, 10, 10, 5
    xs, ys, zs = np.meshgrid(
        np.linspace(-1, 1, nx),
        np.linspace(-1, 1, ny),
        np.linspace(-1, 1, nz),
        indexing="ij",
    )
    base = xs**2 + ys**2 + zs**2  # spherical shell signal
    field = base[..., None] + rng.standard_normal((nx, ny, nz, n_ens)) * 0.05
    path = tmp_path / "scalar_field_3d.npy"
    np.save(path, field)
    return str(path)


@pytest.fixture
def tetrahedral_mesh_paths(tmp_path):
    """Tetrahedral mesh ensemble: field (n_verts, n_ens), positions (n_verts, 3), tets (n_tets, 4)."""
    rng = np.random.default_rng(7)
    # Build a small regular 3D grid and split each cell into 6 tetrahedra.
    nx, ny, nz = 4, 4, 4
    xs, ys, zs = np.meshgrid(
        np.linspace(0, 1, nx),
        np.linspace(0, 1, ny),
        np.linspace(0, 1, nz),
        indexing="ij",
    )
    positions = np.column_stack([xs.ravel(), ys.ravel(), zs.ravel()]).astype(np.float64)

    def vid(i, j, k):
        return i * ny * nz + j * nz + k

    tets = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            for k in range(nz - 1):
                v000 = vid(i, j, k)
                v100 = vid(i + 1, j, k)
                v010 = vid(i, j + 1, k)
                v110 = vid(i + 1, j + 1, k)
                v001 = vid(i, j, k + 1)
                v101 = vid(i + 1, j, k + 1)
                v011 = vid(i, j + 1, k + 1)
                v111 = vid(i + 1, j + 1, k + 1)
                # Standard 6-tetrahedron decomposition of a cube.
                tets.append([v000, v100, v110, v111])
                tets.append([v000, v100, v111, v101])
                tets.append([v000, v110, v010, v111])
                tets.append([v000, v010, v011, v111])
                tets.append([v000, v001, v101, v111])
                tets.append([v000, v011, v001, v111])
    tetrahedra = np.asarray(tets, dtype=np.int64)

    n_verts = positions.shape[0]
    n_ens = 8
    base = (positions - 0.5).sum(axis=1)
    field = base[:, None] + rng.standard_normal((n_verts, n_ens)) * 0.05

    field_path = tmp_path / "tet_field.npy"
    positions_path = tmp_path / "tet_positions.npy"
    tetrahedra_path = tmp_path / "tet_tetrahedra.npy"
    np.save(field_path, field)
    np.save(positions_path, positions)
    np.save(tetrahedra_path, tetrahedra)
    return str(field_path), str(positions_path), str(tetrahedra_path)


@pytest.fixture
def trajectories_path(tmp_path):
    """3D trajectory ensemble: shape (n_steps, n_starting_locations, n_ensemble, 3)."""
    rng = np.random.default_rng(8)
    n_steps = 20
    n_start = 3
    n_ens = 8
    t = np.linspace(0, 2 * np.pi, n_steps)
    trajectories = np.zeros((n_steps, n_start, n_ens, 3))
    for s in range(n_start):
        for e in range(n_ens):
            jitter = rng.standard_normal(3) * 0.05
            trajectories[:, s, e, 0] = np.cos(t) + s * 0.5 + jitter[0]
            trajectories[:, s, e, 1] = np.sin(t) + s * 0.5 + jitter[1]
            trajectories[:, s, e, 2] = t / (2 * np.pi) + jitter[2]
    path = tmp_path / "trajectories.npy"
    np.save(path, trajectories)
    return str(path)


# ============================================================================
# Helpers
# ============================================================================


def _assert_png(path_str: str) -> None:
    """Assert that ``path_str`` is a non-empty PNG file on disk."""
    from pathlib import Path

    p = Path(path_str)
    assert p.exists(), f"_figure_path does not exist on disk: {p}"
    assert p.stat().st_size > 0, f"_figure_path is empty: {p}"
    with open(p, "rb") as f:
        head = f.read(len(PNG_MAGIC))
    assert head == PNG_MAGIC, f"_figure_path is not a valid PNG (bad magic bytes): {p}"


def _run_with_file_renderer(tool_fn, out_dir, **kwargs):
    """Activate FileRenderer for the duration of one tool call. Returns the tool result."""
    token = set_renderer(FileRenderer(out_dir))
    try:
        return tool_fn(**kwargs)
    finally:
        current_renderer.reset(token)


def _assert_tool_success_and_png(result) -> None:
    assert result["status"] == "success", (
        f"Expected status=success but got status={result.get('status')!r} "
        f"message={result.get('message')!r}"
    )
    assert "_figure_path" in result, (
        f"Result missing _figure_path field. Result keys: {list(result)}, "
        f"message={result.get('message')!r}"
    )
    _assert_png(result["_figure_path"])


# ============================================================================
# Matplotlib tools
# ============================================================================


class TestFileRendererMatplotlib:
    """Calls each matplotlib plot tool with FileRenderer and verifies a PNG appears."""

    @pytest.mark.parametrize(
        "tool_name",
        [
            "plot_functional_boxplot",
            "plot_curve_boxplot",
            "plot_probabilistic_marching_squares",
            "plot_probabilistic_marching_triangles",
            "plot_uncertainty_lobes",
            "plot_squid_glyph_2D",
            "plot_contour_boxplot",
        ],
    )
    def test_writes_png(
        self,
        tool_name,
        tmp_path,
        curves_2d_path,
        curves_3d_path,
        scalar_field_2d_ensemble_path,
        triangle_mesh_paths,
        vectors_2d_paths,
    ):
        tool_fn = TOOL_REGISTRY[tool_name]
        out_dir = tmp_path / "renders"

        vectors_path, positions_path = vectors_2d_paths
        tri_field_path, tri_triangles_path, tri_points_path = triangle_mesh_paths

        kwargs_by_tool = {
            "plot_functional_boxplot": {
                "data_path": curves_2d_path,
            },
            "plot_curve_boxplot": {
                "data_path": curves_3d_path,
                "workers": 1,
            },
            "plot_probabilistic_marching_squares": {
                "data_path": scalar_field_2d_ensemble_path,
                "isovalue": 0.5,
            },
            "plot_probabilistic_marching_triangles": {
                "field_path": tri_field_path,
                "triangles_path": tri_triangles_path,
                "points_path": tri_points_path,
                "isovalue": 0.0,
            },
            "plot_uncertainty_lobes": {
                "vectors_path": vectors_path,
                "positions_path": positions_path,
            },
            "plot_squid_glyph_2D": {
                "vectors_path": vectors_path,
                "positions_path": positions_path,
            },
            "plot_contour_boxplot": {
                "data_path": scalar_field_2d_ensemble_path,
                "isovalue": 0.5,
                "workers": 1,
            },
        }

        kwargs = kwargs_by_tool[tool_name]
        result = _run_with_file_renderer(tool_fn, out_dir, **kwargs)
        _assert_tool_success_and_png(result)


# ============================================================================
# PyVista tools
# ============================================================================


def _pyvista_offscreen_available() -> tuple[bool, str]:
    """Probe whether ``pv.Plotter(off_screen=True)`` can render a trivial scene.

    Returns ``(ok, reason)``. ``reason`` is the exception text on failure,
    empty string on success.
    """
    try:
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(pv.Sphere())
        # Render to memory via screenshot=False+return_img to avoid touching disk;
        # if the GL backend is broken this will raise.
        plotter.show(auto_close=False, screenshot=False)
        plotter.close()
        return True, ""
    except Exception as exc:  # noqa: BLE001 - intentional broad catch for env probe
        return False, f"{type(exc).__name__}: {exc}"


class TestFileRendererPyVista:
    """Calls each PyVista plot tool with FileRenderer. Skips if off-screen unavailable."""

    @pytest.fixture(scope="class", autouse=True)
    def _require_offscreen(self):
        ok, reason = _pyvista_offscreen_available()
        if not ok:
            pytest.skip(
                "PyVista off-screen rendering not available in this environment: "
                f"{reason}"
            )

    @pytest.mark.parametrize(
        "tool_name",
        [
            "plot_squid_glyph_3D",
            "plot_probabilistic_marching_cubes",
            "plot_probabilistic_marching_tetrahedra",
            "plot_uncertainty_tubes",
        ],
    )
    def test_writes_png(
        self,
        tool_name,
        tmp_path,
        vectors_3d_paths,
        scalar_field_3d_ensemble_path,
        tetrahedral_mesh_paths,
        trajectories_path,
    ):
        tool_fn = TOOL_REGISTRY[tool_name]
        out_dir = tmp_path / "renders"

        vectors_path, positions_path = vectors_3d_paths
        tet_field_path, tet_positions_path, tet_tetrahedra_path = tetrahedral_mesh_paths

        kwargs_by_tool = {
            "plot_squid_glyph_3D": {
                "vectors_path": vectors_path,
                "positions_path": positions_path,
            },
            "plot_probabilistic_marching_cubes": {
                "data_path": scalar_field_3d_ensemble_path,
                "isovalue": 0.5,
            },
            "plot_probabilistic_marching_tetrahedra": {
                "field_path": tet_field_path,
                "positions_path": tet_positions_path,
                "tetrahedra_path": tet_tetrahedra_path,
                "isovalue": 0.0,
            },
            "plot_uncertainty_tubes": {
                "data_path": trajectories_path,
                "workers": 1,
            },
        }

        kwargs = kwargs_by_tool[tool_name]
        result = _run_with_file_renderer(tool_fn, out_dir, **kwargs)
        _assert_tool_success_and_png(result)

# UVisBox Interface Functions

This document specifies the interface functions available from the `uvisbox.Modules`.

## ContourBoxplot

### `contour_boxplot(binary_images, method='contour_bd', binary_images_depths=None, percentil=95, ax=None, show_median=True, show_outliers=True)`

Plot the contour boxplot including the band depth area between the top and bottom contours along with the median contour.

-   **binary_images**: `np.ndarray` - 3D array of shape (N, H, W) where N is the number of binary images and H, W are the height and width of each image.
-   **method**: `str` - The method to use for plotting. Options are 'contour_bd'. Default is 'contour_bd'.
-   **binary_images_depths**: `np.ndarray` - 1D array of band depths of shape (N,). If None, it will be computed.
-   **percentil**: `float` - Percentile for the band depth calculation. Default is 100.
-   **ax**: `matplotlib.axes.Axes` - Matplotlib Axes object to plot on. If None, a new figure and axes will be created.
-   **show_median**: `bool` - Whether to plot the median contour. Default is True.
-   **show_outliers**: `bool` - Whether to plot the outlier contours. Default is True.

## CurveBoxplot

### `curve_boxplot(curves, curve_depths=None, percentile=50, ax=None, color_map='viridis', median_color='red', alpha=1.0)`

Create a curve band depth plot using the provided curves and their depths.

-   **curves**: `numpy.ndarray` - 3D array of shape (n_curves, n_steps, n_dims) containing curve data.
-   **curve_depths**: `numpy.ndarray` - 1D array of shape (n_curves,) containing the depth of each curve.
-   **percentile**: `float` - The percentile for the band to be highlighted (default is 50).
-   **ax**: `matplotlib.axes.Axes` - The axes to plot on (default is None, which creates a new figure).
-   **color_map**: `str` - The colormap to use for the mesh (default is 'viridis').
-   **median_color**: `str` - The color to use for the median curve (default is 'red').
-   **alpha**: `float` - The transparency level for the mesh (default is 1.0).

## FunctionalBoxplot

### `functional_boxplot(curves, method='functional_bd', curves_depths=None, percentil=100, scale=1.0, ax=None, show_median=True, band_alpha=0.5)`

Plot the functional band depth area between the top and bottom curves along with the median curve.

-   **curves**: `np.ndarray` - 2D array of shape (N, D) where N is the number of samples and D is the number of features.
-   **method**: `str` - The method to use for plotting. Options are 'functional_bd' and 'modified_bd'. Default is 'functional_bd'.
-   **curves_depths**: `np.ndarray` - 1D array of band depths of shape (N,). If None, it will be computed.
-   **percentil**: `float` - Percentile for the band depth calculation. Default is 100.
-   **scale**: `float` - Scale factor for the depth area. Default is 1.0.
-   **ax**: `matplotlib.axes.Axes` - Matplotlib Axes object to plot on. If None, a new figure and axes will be created.
-   **show_median**: `bool` - Whether to plot the median curve. Default is True.
-   **band_alpha**: `float` - Alpha value for the band depth area. Default is 0.5.

## ProbabilisticMarchingCubes

### `probabilistic_marching_cubes(F, isovalue, cross_prob=None, opacity='linear', cmap='viridis', plotter=None)`

Visualize the probabilistic marching cubes result using PyVista.

-   **F**: `np.ndarray` - 4D array of shape (n_x, n_y, n_z, n_ens) representing the scalar field with ensemble members.
-   **isovalue**: `float` - The isovalue for which to compute the isosurface.
-   **cross_prob**: `np.ndarray` - 3D array of shape (n_x-1, n_y-1, n_z-1) with probabilities of isosurface presence in each cell. If None, it will be computed.
-   **opacity**: `str` or `list` - Opacity mapping for the volume rendering. Default is 'linear'.
-   **cmap**: `str` - Colormap for the volume rendering. Default is 'viridis'.
-   **plotter**: `pyvista.Plotter` - An existing PyVista plotter to add the volume rendering to. If None, a new plotter is created.

## ProbabilisticMarchingSquares

### `probabilistic_marching_squares(F, isovalue, prob_contour=None, cmap='viridis', ax=None)`

Visualize the probabilistic marching squares result using matplotlib.

-   **F**: `np.ndarray` - 3D array of shape (n, m, n_ens) representing the scalar field with ensemble members.
-   **isovalue**: `float` - The isovalue for which to compute the isocontour.
-   **prob_contour**: `np.ndarray` - 2D array of shape (n-1, m-1) with probabilities of contour presence in each cell. If None, it will be computed.
-   **cmap**: `str` - Colormap for the visualization. Default is 'viridis'.
-   **ax**: `matplotlib.axes.Axes` - The axis to draw on. If None, a new figure and axis will be created.

## ProbabilisticMarchingTetrahedra

### `probabilistic_marching_tetrahedra(points, F, tetrahedra, isovalue, cross_prob=None, opacity='linear', cmap='viridis', plotter=None)`

Visualize the probabilistic marching tetrahedra result using PyVista.

-   **points**: `np.ndarray` - 2D array of shape (n_points, 3) with point coordinates.
-   **F**: `np.ndarray` - 2D array of shape (n_points, n_ens) representing the scalar field with ensemble members.
-   **tetrahedra**: `np.ndarray` - 2D array of shape (n_tetrahedra, 4) representing the tetrahedralization of the points.
-   **isovalue**: `float` - The isovalue for which to compute the isosurface.
-   **cross_prob**: `np.ndarray` - 1D array with probabilities of isosurface presence in each tetrahedron. If None, it will be computed.
-   **opacity**: `str` or `list` - Opacity mapping for the volume rendering. Default is 'linear'.
-   **cmap**: `str` - Colormap for the volume rendering. Default is 'viridis'.
-   **plotter**: `pyvista.Plotter` - An existing PyVista plotter to add the volume rendering to. If None, a new plotter is created.

## ProbabilisticMarchingTriangles

### `probabilistic_marching_triangles(F, points, triangles, isovalue, prob_contour=None, cmap='viridis', ax=None)`

Visualize the probabilistic marching triangles result using matplotlib.

-   **F**: `np.ndarray` - 2D array of shape (n_points, n_ens) representing the scalar field with ensemble members.
-   **points**: `np.ndarray` - 2D array of shape (n_points, 2) with point coordinates.
-   **triangles**: `np.ndarray` - 2D array of shape (n_triangles, 3) with triangle indices.
-   **isovalue**: `float` - The isovalue for which to compute the isocontour.
-   **prob_contour**: `np.ndarray` - 1D array with probabilities of contour presence in each triangle. If None, it will be computed.
-   **cmap**: `str` - Colormap for the probability map. Default is 'viridis'.
-   **ax**: `matplotlib.axes.Axes` - The axis to draw on. If None, a new figure and axis will be created.

## SquidGlyphs

### `squid_glyph_3D(positions, ensemble_vectors, point_values=None, percentil=0.95, scale=0.5, show_edges=True, glyph_color='lightblue', ax=None)`

Draws uncertainty squid glyphs for the given positions and ensemble vectors in 3D.

-   **positions**: `numpy.ndarray` - Array of shape (n, 3) The positions of the squid glyphs.
-   **ensemble_vectors**: `numpy.ndarray` - Array of shape (n, m, 3) The ensemble vectors for each position in Cartesian coordinates.
-   **point_values**: `numpy.ndarray` - Array of shape (n,) The values associated with each position for coloring.
-   **percentil**: `float` - The first percentile for depth filtering.
-   **scale**: `float` - The scale factor for the glyphs. Default is 0.5.
-   **show_edges**: `bool` - Whether to show edges of the glyphs. Default is True.
-   **glyph_color**: `str` - The color of the glyphs. Default is 'lightblue'.
-   **ax**: `pyvista.Plotter` - The pyvista plotter to use. If None, a new plotter will be created.

### `squid_glyph_2D(positions, ensemble_vectors, percentil1, scale=0.2, ax=None)`

Draws uncertainty squid glyphs for the given positions and ensemble vectors in 2D.

-   **positions**: `numpy.ndarray` - Array of shape (n, 2) representing the positions of the squid glyphs.
-   **ensemble_vectors**: `numpy.ndarray` - Array of shape (n, m, 2) representing the ensemble vectors for each position.
-   **percentil1**: `float` - The first percentile for depth filtering.
-   **scale**: `float` - The scale factor for the glyphs.
-   **ax**: `matplotlib.axes.Axes` - The axis to draw on. If None, a new figure and axis will be created.

## UncertaintyLobes

### `uncertainty_lobes(positions, ensemble_vectors, percentil1, percentil2=None, scale=0.2, ax=None, show_median=True)`

Draws uncertainty lobe glyphs for the given positions and ensemble vectors.

-   **positions**: `numpy.ndarray` - Array of shape (n, 2) representing the positions of the lobe glyphs.
-   **ensemble_vectors**: `numpy.ndarray` - Array of shape (n, m, 2) representing the ensemble vectors for each position.
-   **percentil1**: `float` - The first percentile for depth filtering.
-   **percentil2**: `float` - The second percentile for depth filtering. If None, only one lobe is drawn.
-   **scale**: `float` - The scale factor for the glyphs.
-   **ax**: `matplotlib.axes.Axes` - The axis to draw on. If None, a new figure and axis will be created.
-   **show_median**: `bool` - Whether to show the median vector. Default is True.

## UncertaintyTube

### `uncertainty_tubes_2D(trajectories, axis=None)`

Generate and plot 2D uncertainty tubes from trajectories.

-   **trajectories**: `np.ndarray` - Array of shape (n_trajectories, n_time_steps, n_ensemble_members, 2) representing the 2D trajectories.
-   **axis**: `matplotlib.axes.Axes` - Axis to plot on. If None, creates a new figure and axis.

### `uncertainty_tubes_3D(trajectories, axis=None)`

Generate and plot 3D uncertainty tubes from trajectories.

-   **trajectories**: `np.ndarray` - Array of shape (n_trajectories, n_time_steps, n_ensemble_members, 3) representing the 3D trajectories.
-   **axis**: `matplotlib.axes.Axes` - Axis to plot on. If None, creates a new figure and axis.

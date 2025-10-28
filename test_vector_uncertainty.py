"""Simple test: Generate random vector field and plot uncertainty lobes"""
from pathlib import Path
import sys
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chatuvisbox.data_tools import generate_vector_field_ensemble
from chatuvisbox.vis_tools import plot_uncertainty_lobes


def main():
    """Generate a random vector field and visualize with uncertainty lobes"""
    print("Generating random vector field ensemble...")

    result = generate_vector_field_ensemble(
        x_res=8,
        y_res=8,
        n_instances=30,
        initial_direction=0.0,
        initial_magnitude=1.0,
        direction_variation_factor=0.3,
        magnitude_variation_factor=0.3
    )

    if result['status'] != 'success':
        print(f"✗ Generation failed: {result['message']}")
        return

    print(f"✓ Vector field generated: {result['positions_shape']}, {result['vectors_shape']}")

    print("\nPlotting uncertainty lobes...")

    viz_result = plot_uncertainty_lobes(
        vectors_path=result['vectors_path'],
        positions_path=result['positions_path'],
        percentile1=50,
        percentile2=90,
        scale=0.5
    )

    if viz_result['status'] != 'success':
        print(f"✗ Visualization failed: {viz_result['message']}")
        return

    print(f"✓ {viz_result['message']}")

    plt.show(block=True)


if __name__ == "__main__":
    main()

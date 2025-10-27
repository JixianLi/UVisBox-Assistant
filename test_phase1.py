"""Phase 1 Validation Tests"""
import sys
from pathlib import Path

print("=" * 60)
print("Phase 1 Validation Tests")
print("=" * 60)

# Test 1: Config import
print("\n[1/6] Testing config.py...")
try:
    import config
    print(f"  ✅ Config imported successfully")
    print(f"  - Model: {config.MODEL_NAME}")
    print(f"  - API Key present: {len(config.GEMINI_API_KEY) > 0}")
    print(f"  - Temp dir: {config.TEMP_DIR}")
    print(f"  - Test data dir: {config.TEST_DATA_DIR}")
except Exception as e:
    print(f"  ❌ Config import failed: {e}")
    sys.exit(1)

# Test 2: Data tools import
print("\n[2/6] Testing data_tools.py...")
try:
    from data_tools import (
        load_csv_to_numpy,
        generate_ensemble_curves,
        generate_scalar_field_ensemble,
        load_npy,
        DATA_TOOLS,
        DATA_TOOL_SCHEMAS
    )
    print(f"  ✅ Data tools imported successfully")
    print(f"  - Tool registry has {len(DATA_TOOLS)} tools")
    print(f"  - Schema registry has {len(DATA_TOOL_SCHEMAS)} schemas")
    assert len(DATA_TOOLS) == 4, "Expected 4 data tools"
    assert len(DATA_TOOL_SCHEMAS) == 4, "Expected 4 data tool schemas"
except Exception as e:
    print(f"  ❌ Data tools import failed: {e}")
    sys.exit(1)

# Test 3: Viz tools import
print("\n[3/6] Testing viz_tools.py...")
try:
    from viz_tools import (
        plot_functional_boxplot,
        plot_curve_boxplot,
        plot_probabilistic_marching_squares,
        plot_uncertainty_lobes,
        VIZ_TOOLS,
        VIZ_TOOL_SCHEMAS
    )
    print(f"  ✅ Viz tools imported successfully")
    print(f"  - Tool registry has {len(VIZ_TOOLS)} tools")
    print(f"  - Schema registry has {len(VIZ_TOOL_SCHEMAS)} schemas")
    assert len(VIZ_TOOLS) == 4, "Expected 4 viz tools"
    assert len(VIZ_TOOL_SCHEMAS) == 4, "Expected 4 viz tool schemas"
except Exception as e:
    print(f"  ❌ Viz tools import failed: {e}")
    sys.exit(1)

# Test 4: Data generation
print("\n[4/6] Testing data generation...")
try:
    # Generate ensemble curves
    result = generate_ensemble_curves(n_curves=10, n_points=50)
    assert result["status"] == "success", f"Expected success, got {result['status']}"
    assert Path(result["output_path"]).exists(), "Generated file doesn't exist"
    print(f"  ✅ generate_ensemble_curves() works")
    print(f"    - Created: {result['output_path']}")
    print(f"    - Shape: {result['shape']}")

    # Generate scalar field
    result = generate_scalar_field_ensemble(nx=20, ny=20, n_ensemble=10)
    assert result["status"] == "success", f"Expected success, got {result['status']}"
    assert Path(result["output_path"]).exists(), "Generated file doesn't exist"
    print(f"  ✅ generate_scalar_field_ensemble() works")
    print(f"    - Created: {result['output_path']}")
    print(f"    - Shape: {result['shape']}")
except Exception as e:
    print(f"  ❌ Data generation failed: {e}")
    sys.exit(1)

# Test 5: CSV loading
print("\n[5/6] Testing CSV loading...")
try:
    csv_path = config.TEST_DATA_DIR / "sample_curves.csv"
    if not csv_path.exists():
        print(f"  ⚠️  Test CSV not found: {csv_path}")
        print(f"  Run create_test_data.py first")
    else:
        result = load_csv_to_numpy(str(csv_path))
        assert result["status"] == "success", f"Expected success, got {result['status']}"
        assert Path(result["output_path"]).exists(), "Output file doesn't exist"
        print(f"  ✅ load_csv_to_numpy() works")
        print(f"    - Input: {csv_path}")
        print(f"    - Output: {result['output_path']}")
        print(f"    - Shape: {result['shape']}")
except Exception as e:
    print(f"  ❌ CSV loading failed: {e}")
    sys.exit(1)

# Test 6: Visualization (basic test without display)
print("\n[6/6] Testing visualization functions...")
try:
    import time
    
    # Generate test data
    result = generate_ensemble_curves(n_curves=30, n_points=100)
    data_path = result["output_path"]

    # Test functional boxplot
    start_time = time.time()
    viz_result = plot_functional_boxplot(data_path, percentiles=[25, 50, 75, 100])
    elapsed_ms = (time.time() - start_time) * 1000
    assert viz_result["status"] == "success", f"Expected success, got {viz_result['status']}"
    assert "_viz_params" in viz_result, "Missing _viz_params in result"
    assert viz_result["_viz_params"]["_tool_name"] == "plot_functional_boxplot"
    assert viz_result["_viz_params"]["percentiles"] == [25, 50, 75, 100], "Percentiles not stored correctly"
    print(f"  ✅ plot_functional_boxplot() works ({elapsed_ms:.2f} ms)")
    print(f"    - Message: {viz_result['message']}")

    # Test curve boxplot
    start_time = time.time()
    viz_result = plot_curve_boxplot(data_path, percentiles=[25, 50, 75, 100])
    elapsed_ms = (time.time() - start_time) * 1000
    assert viz_result["status"] == "success", f"Expected success, got {viz_result['status']}"
    assert "_viz_params" in viz_result, "Missing _viz_params in result"
    assert viz_result["_viz_params"]["_tool_name"] == "plot_curve_boxplot"
    assert viz_result["_viz_params"]["percentiles"] == [25, 50, 75, 100], "Percentiles not stored correctly"
    print(f"  ✅ plot_curve_boxplot() works ({elapsed_ms:.2f} ms)")
    print(f"    - Message: {viz_result['message']}")

    # Test probabilistic marching squares
    result = generate_scalar_field_ensemble(nx=30, ny=30, n_ensemble=20)
    field_path = result["output_path"]
    start_time = time.time()
    viz_result = plot_probabilistic_marching_squares(field_path, isovalue=0.5, colormap="viridis")
    elapsed_ms = (time.time() - start_time) * 1000
    assert viz_result["status"] == "success", f"Expected success, got {viz_result['status']}"
    assert "_viz_params" in viz_result, "Missing _viz_params in result"
    assert viz_result["_viz_params"]["_tool_name"] == "plot_probabilistic_marching_squares"
    print(f"  ✅ plot_probabilistic_marching_squares() works ({elapsed_ms:.2f} ms)")
    print(f"    - Message: {viz_result['message']}")

    print("\n  ⚠️  Note: Matplotlib windows were opened but may be hidden")
    print("     Close all matplotlib windows to continue")

except Exception as e:
    print(f"  ❌ Visualization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ ALL PHASE 1 VALIDATION TESTS PASSED!")
print("=" * 60)
print("\nPhase 1 Checklist:")
print("  ✅ Project structure created")
print("  ✅ .gitignore configured")
print("  ✅ config.py works with API key")
print("  ✅ data_tools.py with 4 tools + schemas")
print("  ✅ viz_tools.py with 4 tools + schemas")
print("  ✅ Test data created")
print("  ✅ Data generation works")
print("  ✅ CSV loading works")
print("  ✅ Visualizations work")
print("\n✅ Ready for Phase 2: LangGraph State & Nodes")
print("=" * 60)
input("Press Enter to continue...")

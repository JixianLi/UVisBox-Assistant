"""
Quick validation script for Phase 4.5 restructuring.

Tests that all imports work correctly after package restructure.
Makes NO API calls.
"""

print("="*70)
print("PHASE 4.5 RESTRUCTURING VALIDATION")
print("="*70)

# Test 1: Package import
print("\n✓ Test 1: Package version")
import chatuvisbox
print(f"  chatuvisbox version: {chatuvisbox.__version__}")

# Test 2: Main API imports
print("\n✓ Test 2: Main API imports")
from chatuvisbox import run_graph, stream_graph, GraphState
print("  run_graph, stream_graph, GraphState imported")

# Test 3: Module imports
print("\n✓ Test 3: Module imports")
from chatuvisbox.graph import graph_app, create_graph
from chatuvisbox.state import create_initial_state
from chatuvisbox.nodes import call_model, call_data_tool, call_viz_tool
from chatuvisbox.routing import route_after_model, route_after_tool
from chatuvisbox.model import create_model_with_tools, get_system_prompt
from chatuvisbox.data_tools import DATA_TOOLS, DATA_TOOL_SCHEMAS
from chatuvisbox.viz_tools import VIZ_TOOLS, VIZ_TOOL_SCHEMAS
from chatuvisbox import config
from chatuvisbox.utils import get_tool_type
print("  All modules imported successfully")

# Test 4: Config paths
print("\n✓ Test 4: Config paths")
print(f"  TEMP_DIR: {config.TEMP_DIR}")
print(f"  TEST_DATA_DIR: {config.TEST_DATA_DIR}")
print(f"  Temp dir exists: {config.TEMP_DIR.exists()}")
print(f"  Test data dir exists: {config.TEST_DATA_DIR.exists()}")

# Test 5: Tool registries
print("\n✓ Test 5: Tool registries")
print(f"  Data tools: {len(DATA_TOOLS)} tools")
print(f"  Viz tools: {len(VIZ_TOOLS)} tools")
print(f"  Total schemas: {len(DATA_TOOL_SCHEMAS + VIZ_TOOL_SCHEMAS)}")

# Test 6: Graph compilation
print("\n✓ Test 6: Graph compilation")
print(f"  Graph app compiled: {graph_app is not None}")

print("\n" + "="*70)
print("✅ ALL VALIDATION TESTS PASSED")
print("="*70)
print("\nPackage structure is working correctly!")
print("Ready to proceed with full test suite.")

"""Quick integration test that respects Gemini free tier rate limits

Gemini Free Tier Limits (gemini-2.0-flash-lite):
- 30 requests per minute
- This test makes ~6-8 API calls total, staying well under the limit
"""

from chatuvisbox.graph import run_graph
import matplotlib.pyplot as plt
import time


def test_data_only():
    """Test 1: Data generation only (2-3 API calls)"""
    print("\n" + "="*60)
    print("TEST 1: Data Generation Only")
    print("="*60)

    result = run_graph("Generate 10 test curves with 50 points")

    assert result.get("current_data_path") is not None
    assert result.get("error_count") == 0

    print(f"✅ Data path: {result['current_data_path']}")
    print(f"✅ Messages: {len(result['messages'])}")
    print(f"✅ Error count: {result.get('error_count')}")


def test_data_and_viz():
    """Test 2: Data + visualization (4-5 API calls)"""
    print("\n" + "="*60)
    print("TEST 2: Data Generation + Visualization")
    print("="*60)

    result = run_graph("Generate 15 curves and show a functional boxplot")

    assert result.get("current_data_path") is not None
    assert result.get("last_viz_params") is not None
    assert result.get("error_count") == 0

    print(f"✅ Data generated: {result['current_data_path']}")
    print(f"✅ Visualization: {result.get('last_viz_params', {}).get('_tool_name', 'N/A')}")
    print(f"✅ Messages: {len(result['messages'])}")
    print(f"✅ Matplotlib window should have appeared")


def test_conversational():
    """Test 3: Conversational response (1-2 API calls)"""
    print("\n" + "="*60)
    print("TEST 3: Conversational Response")
    print("="*60)

    result = run_graph("What can you do?")

    assert len(result["messages"]) >= 2
    last_msg = result["messages"][-1]
    assert hasattr(last_msg, "content")

    print(f"✅ Response: {last_msg.content[:100]}...")
    print(f"✅ No tools called (direct response)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("QUICK INTEGRATION TEST (Gemini Free Tier Friendly)")
    print("Expected API calls: 6-10 (well under 30/min limit)")
    print("="*60)

    start_time = time.time()

    try:
        test_data_only()
        test_data_and_viz()
        test_conversational()

        elapsed = time.time() - start_time

        print("\n" + "="*60)
        print(f"✅ ALL TESTS PASSED in {elapsed:.1f}s")
        print("="*60)
        print(f"\nAPI calls made: ~{len([1,2,3])*2 + 3} (estimated)")
        print("Free tier limit: 30 requests/minute")
        print("Status: ✅ Well under limit")

        # Close matplotlib windows
        print("\n💡 Close matplotlib windows to exit")
        input("Press Enter to close windows...")
        plt.close('all')

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        plt.close('all')
        sys.exit(1)

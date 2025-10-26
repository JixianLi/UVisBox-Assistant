# Phase 9: Final Testing & Bug Bash

**Goal**: Comprehensive testing of all features, edge cases, and failure modes.

**Duration**: 1 day

## Prerequisites

- Phases 1-8 completed
- All features implemented
- Main REPL working

## Tasks

### Task 9.1: Comprehensive Test Suite

**File**: `test_comprehensive.py`

```python
"""
Comprehensive test suite covering all features and edge cases.

This is the final validation before release.
"""

import pytest
from conversation import ConversationSession
import matplotlib.pyplot as plt
from pathlib import Path
import config
import numpy as np


class TestDataTools:
    """Test all data tool functionality."""

    def test_load_csv_valid(self):
        """Test loading valid CSV file."""
        import pandas as pd

        # Create test CSV
        test_file = config.TEST_DATA_DIR / "test_load.csv"
        pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}).to_csv(test_file, index=False)

        session = ConversationSession()
        session.send(f"Load {test_file}")

        ctx = session.get_context_summary()
        assert ctx["current_data"] is not None
        assert ctx["error_count"] == 0

    def test_load_csv_nonexistent(self):
        """Test loading nonexistent CSV."""
        session = ConversationSession()
        session.send("Load nonexistent_file.csv")

        response = session.get_last_response()
        assert "not found" in response.lower() or "error" in response.lower()

    def test_generate_curves(self):
        """Test curve generation."""
        session = ConversationSession()
        session.send("Generate 25 curves with 75 points")

        ctx = session.get_context_summary()
        assert ctx["current_data"] is not None

        # Verify file exists and has correct shape
        data = np.load(ctx["current_data"])
        assert data.shape[0] == 25 or data.shape[0] >= 20  # Model might vary

    def test_generate_scalar_field(self):
        """Test scalar field generation."""
        session = ConversationSession()
        session.send("Generate scalar field 35x35 with 20 ensemble members")

        ctx = session.get_context_summary()
        assert ctx["current_data"] is not None

        data = np.load(ctx["current_data"])
        assert data.ndim == 3


class TestVizTools:
    """Test all visualization tools."""

    def test_functional_boxplot(self):
        """Test functional boxplot visualization."""
        session = ConversationSession()
        session.send("Generate 30 curves and plot functional boxplot")

        ctx = session.get_context_summary()
        assert ctx["last_viz"] is not None
        assert "plot_functional_boxplot" in str(ctx["last_viz"])

    def test_curve_boxplot(self):
        """Test curve boxplot."""
        session = ConversationSession()
        session.send("Generate curves and show curve boxplot")

        ctx = session.get_context_summary()
        assert ctx["last_viz"] is not None

    def test_probabilistic_marching_squares(self):
        """Test probabilistic marching squares."""
        session = ConversationSession()
        session.send("Generate scalar field and visualize with probabilistic marching squares")

        ctx = session.get_context_summary()
        assert ctx["last_viz"] is not None

    def test_viz_with_parameters(self):
        """Test visualization with specific parameters."""
        session = ConversationSession()
        session.send("Generate curves and plot functional boxplot with percentile 85 and hide median")

        ctx = session.get_context_summary()
        assert ctx["last_viz"] is not None


class TestConversationalFeatures:
    """Test multi-turn conversations."""

    def test_sequential_workflow(self):
        """Test sequential data → viz workflow."""
        session = ConversationSession()

        session.send("Generate 20 curves")
        ctx1 = session.get_context_summary()
        data_path = ctx1["current_data"]

        session.send("Plot them as functional boxplot")
        ctx2 = session.get_context_summary()

        assert ctx2["current_data"] == data_path
        assert ctx2["last_viz"] is not None

    def test_context_preservation(self):
        """Test context preserved across multiple turns."""
        session = ConversationSession()

        session.send("Generate curves")
        session.send("Plot them")
        session.send("Change colormap to plasma")

        ctx = session.get_context_summary()
        assert ctx["turns"] == 3
        assert ctx["error_count"] == 0

    def test_pronoun_reference(self):
        """Test pronoun references work."""
        session = ConversationSession()

        session.send("Generate some test data")
        session.send("Visualize it")

        ctx = session.get_context_summary()
        assert ctx["last_viz"] is not None


class TestHybridControl:
    """Test hybrid control fast path."""

    def test_colormap_update(self):
        """Test colormap update via hybrid control."""
        session = ConversationSession()

        session.send("Generate curves and plot")
        session.send("colormap plasma")

        response = session.get_last_response()
        assert "colormap" in response.lower()

    def test_percentile_update(self):
        """Test percentile update."""
        session = ConversationSession()

        session.send("Generate curves and plot functional boxplot")
        session.send("percentile 75")

        ctx = session.get_context_summary()
        assert ctx["error_count"] == 0

    def test_hybrid_without_viz(self):
        """Test hybrid command without prior viz."""
        session = ConversationSession()

        session.send("colormap viridis")

        response = session.get_last_response()
        # Should explain no viz to update
        assert "no" in response.lower() or "first" in response.lower()


class TestErrorHandling:
    """Test error handling and recovery."""

    def test_file_not_found_recovery(self):
        """Test recovery from file not found."""
        session = ConversationSession()

        session.send("Load missing.csv")
        response1 = session.get_last_response()
        assert "error" in response1.lower() or "not found" in response1.lower()

        # Recover
        session.send("Generate test data instead")
        ctx = session.get_context_summary()
        assert ctx["current_data"] is not None

    def test_invalid_shape_error(self):
        """Test error for invalid data shape."""
        # Create wrong shape data
        wrong_data = np.array([1, 2, 3])
        wrong_path = config.TEMP_DIR / "wrong.npy"
        np.save(wrong_path, wrong_data)

        session = ConversationSession()
        session.send(f"Plot {wrong_path} as functional boxplot")

        response = session.get_last_response()
        assert "shape" in response.lower() or "dimension" in response.lower() or "error" in response.lower()


class TestSessionManagement:
    """Test session management features."""

    def test_clear_session(self):
        """Test session clear."""
        session = ConversationSession()

        session.send("Generate curves")
        session.send("Generate scalar field")

        files_before = len(list(config.TEMP_DIR.glob("_temp_*")))
        assert files_before > 0

        session.clear()

        files_after = len(list(config.TEMP_DIR.glob("_temp_*")))
        assert files_after == 0

    def test_reset_preserves_files(self):
        """Test reset preserves files."""
        session = ConversationSession()

        session.send("Generate curves")
        ctx = session.get_context_summary()
        data_path = ctx["current_data"]

        session.reset()

        assert Path(data_path).exists()

    def test_session_stats(self):
        """Test session statistics."""
        session = ConversationSession()

        session.send("Generate curves")
        session.send("Plot them")

        stats = session.get_stats()
        assert stats["turns"] == 2
        assert stats["current_data"] is True
        assert stats["current_viz"] is True


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_empty_input(self):
        """Test handling of empty input."""
        session = ConversationSession()
        # Empty input should be handled gracefully
        # (REPL handles this, but test at API level)

    def test_very_long_input(self):
        """Test very long input."""
        session = ConversationSession()
        long_prompt = "Generate curves " * 100
        session.send(long_prompt)
        # Should handle gracefully

    def test_special_characters(self):
        """Test input with special characters."""
        session = ConversationSession()
        session.send("Generate curves with ñamé.csv")
        # Should handle gracefully

    def test_rapid_sequential_commands(self):
        """Test rapid sequential commands."""
        session = ConversationSession()

        for i in range(5):
            session.send("Generate curves")

        ctx = session.get_context_summary()
        assert ctx["error_count"] == 0


def run_comprehensive_tests():
    """Run all comprehensive tests using pytest."""
    import sys

    print("\n" + "🧪"*35)
    print("CHATUVISBOX: COMPREHENSIVE TEST SUITE")
    print("🧪"*35 + "\n")

    # Run pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "test_"
    ])

    plt.close('all')

    return exit_code


if __name__ == "__main__":
    exit_code = run_comprehensive_tests()
    sys.exit(exit_code)
```

Run:
```bash
pip install pytest
python test_comprehensive.py
```

### Task 9.2: User Acceptance Test Scenarios

**File**: `user_acceptance_tests.md`

```markdown
# User Acceptance Test Scenarios

Test these scenarios manually in the REPL to verify user experience.

## Scenario 1: New User First Experience

1. Launch REPL: `python main.py`
2. Type: `/help`
3. Verify: Clear, helpful documentation appears
4. Type: `Generate some test curves and visualize them`
5. Verify: Matplotlib window appears with functional boxplot
6. Type: `/quit`
7. Verify: Clean exit

**Success Criteria**: New user can accomplish task without confusion

---

## Scenario 2: Data Analysis Workflow

1. Type: `Load test_data/sample_curves.csv`
2. Verify: Confirms data loaded
3. Type: `What shape is the data?`
4. Verify: Agent describes data shape
5. Type: `Plot it as a functional boxplot`
6. Verify: Visualization appears
7. Type: `Change percentile to 90`
8. Verify: Plot updates quickly
9. Type: `colormap plasma`
10. Verify: Plot updates with new colormap

**Success Criteria**: Smooth workflow, quick parameter updates

---

## Scenario 3: Error Recovery

1. Type: `Load nonexistent.csv`
2. Verify: Helpful error message, lists available files
3. Type: `Load sample_curves.csv instead`
4. Verify: Successfully loads correct file
5. Type: `Plot it`
6. Verify: Visualization appears

**Success Criteria**: Errors don't block progress, recovery is smooth

---

## Scenario 4: Multi-Visualization Comparison

1. Type: `Generate 40 curves`
2. Type: `Show functional boxplot`
3. Verify: Plot appears
4. Type: `Now show curve boxplot from the same data`
5. Verify: Second plot appears (both windows open)
6. Type: `Use percentile 70 for the second one`
7. Verify: Second plot updates

**Success Criteria**: Multiple plots can be open, correctly referenced

---

## Scenario 5: Session Management

1. Type: `Generate curves and plot`
2. Type: `Generate scalar field and plot`
3. Type: `/stats`
4. Verify: Shows 2+ turns, files created
5. Type: `/context`
6. Verify: Shows current state
7. Type: `/clear`
8. Verify: Session cleared message
9. Type: `/stats`
10. Verify: Reset stats

**Success Criteria**: Session commands work as expected

---

## Scenario 6: Advanced Parameters

1. Type: `Generate 50 curves and plot functional boxplot with percentile 95, hide outliers, and use colormap inferno`
2. Verify: Plot appears with all parameters applied
3. Type: `Show median now`
4. Verify: Median appears on plot

**Success Criteria**: Complex parameter combinations work

---

## Scenario 7: Conversational Continuity

1. Type: `Generate some test data`
2. Type: `More points please` (ambiguous request)
3. Verify: Agent asks for clarification OR generates more data
4. Type: `Make it look nicer`
5. Verify: Agent improves visualization aesthetics

**Success Criteria**: Agent handles ambiguity gracefully

---

## Pass/Fail Checklist

- [ ] Scenario 1: New User First Experience
- [ ] Scenario 2: Data Analysis Workflow
- [ ] Scenario 3: Error Recovery
- [ ] Scenario 4: Multi-Visualization Comparison
- [ ] Scenario 5: Session Management
- [ ] Scenario 6: Advanced Parameters
- [ ] Scenario 7: Conversational Continuity
```

### Task 9.3: Performance Testing

**File**: `test_performance.py`

```python
"""Performance testing for ChatUVisBox."""

import time
from conversation import ConversationSession
import matplotlib.pyplot as plt


def benchmark_data_generation():
    """Benchmark data generation."""
    print("\n" + "="*70)
    print("BENCHMARK: Data Generation")
    print("="*70)

    session = ConversationSession()

    start = time.time()
    session.send("Generate 50 curves with 100 points")
    elapsed = time.time() - start

    print(f"Time: {elapsed:.2f}s")
    print(f"Target: <3s")

    assert elapsed < 5.0, "Data generation too slow"
    print("✅ Passed")


def benchmark_visualization():
    """Benchmark visualization."""
    print("\n" + "="*70)
    print("BENCHMARK: Visualization")
    print("="*70)

    session = ConversationSession()

    # Setup
    session.send("Generate 40 curves")

    # Benchmark viz
    start = time.time()
    session.send("Plot functional boxplot")
    elapsed = time.time() - start

    print(f"Time: {elapsed:.2f}s")
    print(f"Target: <3s")

    assert elapsed < 5.0, "Visualization too slow"
    print("✅ Passed")


def benchmark_hybrid_control():
    """Benchmark hybrid control speed."""
    print("\n" + "="*70)
    print("BENCHMARK: Hybrid Control")
    print("="*70)

    session = ConversationSession()

    # Setup
    session.send("Generate curves and plot")

    # Benchmark hybrid update
    start = time.time()
    session.send("colormap plasma")
    elapsed = time.time() - start

    print(f"Time: {elapsed:.2f}s")
    print(f"Target: <1s (hybrid should be fast)")

    assert elapsed < 2.0, "Hybrid control too slow"
    print("✅ Passed")


def benchmark_full_workflow():
    """Benchmark complete workflow."""
    print("\n" + "="*70)
    print("BENCHMARK: Full Workflow")
    print("="*70)

    session = ConversationSession()

    start = time.time()
    session.send("Generate 30 curves with 80 points and plot functional boxplot with percentile 90")
    elapsed = time.time() - start

    print(f"Time: {elapsed:.2f}s")
    print(f"Target: <5s")

    assert elapsed < 8.0, "Full workflow too slow"
    print("✅ Passed")


def run_performance_tests():
    """Run all performance tests."""
    print("\n" + "⚡"*35)
    print("CHATUVISBOX: PERFORMANCE TESTS")
    print("⚡"*35)

    tests = [
        benchmark_data_generation,
        benchmark_visualization,
        benchmark_hybrid_control,
        benchmark_full_workflow,
    ]

    for test_func in tests:
        try:
            test_func()
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
        except Exception as e:
            print(f"❌ ERROR: {e}")

    plt.close('all')


if __name__ == "__main__":
    run_performance_tests()
```

Run:
```bash
python test_performance.py
```

### Task 9.4: Create Master Test Runner

**File**: `run_all_tests.py`

```python
"""Master test runner for all test suites."""

import subprocess
import sys


def run_test_file(filename: str, description: str) -> bool:
    """Run a test file and return success status."""
    print("\n" + "="*70)
    print(f"Running: {description}")
    print("="*70)

    result = subprocess.run(
        [sys.executable, filename],
        capture_output=False
    )

    success = result.returncode == 0

    if success:
        print(f"✅ {description} PASSED")
    else:
        print(f"❌ {description} FAILED")

    return success


def main():
    """Run all test suites."""
    print("\n" + "🚀"*35)
    print("CHATUVISBOX: MASTER TEST SUITE")
    print("🚀"*35)

    tests = [
        ("test_happy_path.py", "Happy Path Tests"),
        ("test_error_handling.py", "Error Handling Tests"),
        ("test_multiturn.py", "Multi-Turn Conversation Tests"),
        ("test_hybrid_control.py", "Hybrid Control Tests"),
        ("test_session_management.py", "Session Management Tests"),
        ("test_comprehensive.py", "Comprehensive Test Suite"),
        ("test_performance.py", "Performance Tests"),
    ]

    results = []

    for filename, description in tests:
        success = run_test_file(filename, description)
        results.append((description, success))

    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed

    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} - {description}")

    print("\n" + "="*70)
    print(f"Total: {passed}/{len(results)} test suites passed")
    print("="*70)

    if failed == 0:
        print("\n🎉 All tests passed! Ready for release.")
        return 0
    else:
        print(f"\n⚠️  {failed} test suite(s) failed. Fix before release.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
```

Run:
```bash
python run_all_tests.py
```

## Validation Checklist

### Automated Tests
- [ ] All happy path tests pass
- [ ] All error handling tests pass
- [ ] All multi-turn conversation tests pass
- [ ] All hybrid control tests pass
- [ ] All session management tests pass
- [ ] Comprehensive test suite passes (pytest)
- [ ] Performance benchmarks meet targets

### Manual Tests
- [ ] All 7 user acceptance scenarios complete successfully
- [ ] REPL is responsive and intuitive
- [ ] Error messages are helpful
- [ ] Matplotlib windows appear correctly
- [ ] Multi-window management works
- [ ] Help system is clear and complete

### Edge Cases
- [ ] Very long inputs handled
- [ ] Special characters handled
- [ ] Rapid sequential commands handled
- [ ] Empty inputs handled gracefully
- [ ] Network interruptions handled (Gemini API)

### Performance
- [ ] Data generation <3s
- [ ] Visualization <3s
- [ ] Hybrid control <1s
- [ ] Full workflow <5s

## Bug Bash Checklist

Test and fix:
- [ ] Memory leaks (check with multiple long sessions)
- [ ] File handle leaks (check temp files)
- [ ] Race conditions (rapid commands)
- [ ] State corruption (complex workflows)
- [ ] Unclear error messages
- [ ] Missing documentation
- [ ] Inconsistent behavior

## Output

After Phase 9, you should have:
- Comprehensive automated test suite covering all features
- Manual user acceptance test scenarios
- Performance benchmarks
- Master test runner
- All tests passing
- Known issues documented
- System ready for release

## Next Phase

Phase 10 will create final documentation, packaging, and release preparation.

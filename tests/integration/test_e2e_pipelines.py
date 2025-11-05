"""End-to-end pipeline integration tests.

These tests verify complete user workflows through the model, from natural
language input to final output. They ensure backward compatibility by testing
the full stack.

Layer 2: End-to-End Pipeline Tests
- Uses ConversationSession
- Natural language input
- Verifies complete workflows
"""

import pytest
import sys
import time
import matplotlib.pyplot as plt
from pathlib import Path

from uvisbox_assistant.session.conversation import ConversationSession
from uvisbox_assistant import config


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    sess = ConversationSession()
    yield sess
    # Cleanup
    sess.clear()
    plt.close('all')


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


# ============================================================================
# Happy Path: All Visualization Types
# ============================================================================

class TestFunctionalBoxplotPipeline:
    """Test data → functional_boxplot pipeline."""

    def test_generate_and_visualize(self, session):
        """Complete workflow: generate curves and plot functional boxplot."""
        wait_for_rate_limit()

        session.send("Generate 30 curves and plot functional boxplot")

        # Verify no errors
        stats = session.get_stats()
        assert stats["current_data"] is True, "Should have generated data"
        assert stats["current_vis"] is True, "Should have created visualization"

        # Verify response is informative
        response = session.get_last_response()
        assert len(response) > 0
        assert "boxplot" in response.lower() or "curve" in response.lower()


class TestCurveBoxplotPipeline:
    """Test data → curve_boxplot pipeline."""

    def test_generate_and_visualize(self, session):
        """Complete workflow: generate curves and plot curve boxplot."""
        wait_for_rate_limit()

        session.send("Generate 25 spatial curves and create curve boxplot")

        stats = session.get_stats()
        assert stats["current_data"] is True
        assert stats["current_vis"] is True


class TestProbabilisticMarchingSquaresPipeline:
    """Test data → probabilistic_marching_squares pipeline."""

    def test_generate_and_visualize(self, session):
        """Complete workflow: generate field and plot PMS."""
        wait_for_rate_limit()

        session.send(
            "Generate 20x20 scalar field ensemble with 15 members and visualize with probabilistic marching squares"
        )

        stats = session.get_stats()
        assert stats["current_data"] is True
        assert stats["current_vis"] is True


class TestUncertaintyLobesPipeline:
    """Test data → uncertainty_lobes pipeline."""

    def test_generate_and_visualize(self, session):
        """Complete workflow: generate vectors and plot uncertainty lobes."""
        wait_for_rate_limit()

        session.send(
            "Generate vector ensemble at 8 positions and show uncertainty lobes"
        )

        stats = session.get_stats()
        assert stats["current_data"] is True
        assert stats["current_vis"] is True


class TestSquidGlyphPipeline:
    """Test data → squid_glyph pipeline."""

    def test_generate_and_visualize(self, session):
        """Complete workflow: generate vectors and plot squid glyphs."""
        wait_for_rate_limit()

        session.send(
            "Generate vector ensemble at 6 positions and create 2D squid glyphs"
        )

        stats = session.get_stats()
        assert stats["current_data"] is True
        assert stats["current_vis"] is True


class TestContourBoxplotPipeline:
    """Test data → contour_boxplot pipeline."""

    def test_generate_and_visualize(self, session):
        """Complete workflow: generate field and plot contour boxplot."""
        wait_for_rate_limit()

        session.send(
            "Generate 25x25 scalar field ensemble with 12 members and create contour boxplot with isovalue 0.5"
        )

        stats = session.get_stats()
        assert stats["current_data"] is True
        assert stats["current_vis"] is True


# ============================================================================
# Full Analyzer Pipeline Tests
# ============================================================================

class TestAnalyzerPipelineInline:
    """Test data → vis → analyze (inline) pipeline."""

    def test_full_pipeline_one_sentence(self, session):
        """Complete workflow with inline (one-sentence) analysis."""
        wait_for_rate_limit()

        session.send(
            "Generate 30 curves, plot functional boxplot, give me a one-sentence summary"
        )

        # Get response after sending
        response = session.get_last_response()

        # Verify no KEY_NOT_FOUND or other errors
        assert "error" not in response.lower() or "Key" not in response

        # Verify response contains analysis text
        assert len(response) > 0

        # Verify it's concise (inline should be short)
        word_count = len(response.split())
        # Allow some flexibility, but should be brief
        assert word_count < 100, f"Inline summary too long: {word_count} words"

        # Verify mentions uncertainty/analysis concepts
        response_lower = response.lower()
        assert any(word in response_lower for word in [
            "uncertainty", "variation", "curve", "median", "band", "ensemble"
        ]), "Response should mention uncertainty analysis concepts"


class TestAnalyzerPipelineQuick:
    """Test data → vis → analyze (quick) pipeline."""

    def test_full_pipeline_short_summary(self, session):
        """Complete workflow with quick (short) analysis."""
        wait_for_rate_limit()

        session.send(
            "Generate 30 curves, plot functional boxplot, give me a short summary"
        )

        # Get response after sending
        response = session.get_last_response()

        # Verify no errors
        assert "error" not in response.lower() or "Key" not in response

        # Verify response has substance
        assert len(response) > 50, "Quick summary should have substance"

        # Verify mentions key components
        response_lower = response.lower()
        # Should mention at least 2 of these concepts
        concepts = ["median", "band", "percentile", "outlier", "uncertainty", "variation"]
        mentions = sum(1 for concept in concepts if concept in response_lower)
        assert mentions >= 2, f"Should mention multiple analysis concepts, found {mentions}"


class TestAnalyzerPipelineDetailed:
    """Test data → vis → analyze (detailed) pipeline.

    This is the critical test case Jesse mentioned:
    'generate curves, plot functional boxplot, create detailed report'
    This workflow revealed the KEY_NOT_FOUND bug.
    """

    def test_full_pipeline_detailed_report(self, session):
        """Complete workflow with detailed analysis.

        This test would have caught the KEY_NOT_FOUND bug.
        """
        wait_for_rate_limit()

        session.send(
            "Generate 30 curves, plot functional boxplot, create detailed report"
        )

        # Get response after sending
        response = session.get_last_response()

        # CRITICAL: Verify no KEY_NOT_FOUND error
        assert "KeyError" not in response
        assert "KEY_NOT_FOUND" not in response
        assert "key" not in response.lower() or "error" not in response.lower()

        # Verify response is substantial
        word_count = len(response.split())
        assert word_count >= 100, f"Detailed report should be substantial, got {word_count} words"

        # Verify comprehensive coverage
        response_lower = response.lower()
        assert "median" in response_lower, "Should discuss median curve"
        assert any(word in response_lower for word in ["band", "percentile"]), "Should discuss bands"
        assert "outlier" in response_lower, "Should discuss outliers"


# ============================================================================
# Multi-turn Workflow Tests
# ============================================================================

class TestSequentialVisualizationUpdates:
    """Test data → vis → update → update workflow."""

    def test_sequential_parameter_updates(self, session):
        """Multi-turn: create vis, then update parameters multiple times."""
        wait_for_rate_limit()

        # Step 1: Create initial visualization
        session.send("Generate 30 curves and plot functional boxplot")
        assert session.get_stats()["current_vis"] is True

        wait_for_rate_limit()

        # Step 2: Update percentile
        session.send("Change percentile to 75")
        response2 = session.get_last_response()
        assert "75" in response2 or "percentile" in response2.lower()

        wait_for_rate_limit()

        # Step 3: Show outliers
        session.send("Show outliers")
        response3 = session.get_last_response()
        assert "outlier" in response3.lower()

        # Verify session maintained state throughout
        stats = session.get_stats()
        assert stats["current_data"] is True
        assert stats["current_vis"] is True


class TestDataSwitchingWorkflow:
    """Test switching between different datasets."""

    def test_generate_multiple_datasets_and_switch(self, session):
        """Multi-turn: create multiple datasets and visualize each."""
        wait_for_rate_limit()

        # Generate dataset 1
        session.send("Generate 30 curves")
        stats1 = session.get_stats()
        assert stats1["current_data"] is True

        wait_for_rate_limit()

        # Generate dataset 2
        session.send("Generate scalar field 20x20")
        stats2 = session.get_stats()
        assert stats2["current_data"] is True

        wait_for_rate_limit()

        # Visualize dataset (should use most recent)
        session.send("Visualize this data")
        stats3 = session.get_stats()
        assert stats3["current_vis"] is True


class TestAnalysisAfterVisualization:
    """Test adding analysis to existing visualization."""

    def test_create_vis_then_analyze(self, session):
        """Multi-turn: create vis, then request analysis later."""
        wait_for_rate_limit()

        # Step 1: Create visualization
        session.send("Generate 30 curves and plot functional boxplot")
        assert session.get_stats()["current_vis"] is True

        wait_for_rate_limit()

        # Step 2: Request analysis of existing visualization
        session.send("Now give me a detailed analysis of this plot")

        # Get response after sending
        response = session.get_last_response()

        # Verify analysis was generated
        assert len(response) > 100, "Should provide detailed analysis"
        response_lower = response.lower()
        assert any(word in response_lower for word in [
            "median", "band", "uncertainty", "percentile"
        ])


class TestCompleteUserJourney:
    """Test realistic multi-step user journey."""

    def test_realistic_exploration_workflow(self, session):
        """Simulate realistic user exploration workflow."""
        wait_for_rate_limit()

        # Step 1: Generate and visualize
        session.send("Generate 40 curves and create functional boxplot")
        assert session.get_stats()["current_vis"] is True

        wait_for_rate_limit()

        # Step 2: Ask about the visualization
        session.send("What does this show?")
        response2 = session.get_last_response()
        assert len(response2) > 50

        wait_for_rate_limit()

        # Step 3: Adjust visualization
        session.send("Change percentile to 90")

        wait_for_rate_limit()

        # Step 4: Get detailed analysis
        session.send("Give me a detailed report")
        response4 = session.get_last_response()
        assert len(response4) > 100

        # Verify session maintained throughout
        stats = session.get_stats()
        assert stats["turns"] == 4
        assert stats["current_data"] is True
        assert stats["current_vis"] is True


# ============================================================================
# Backward Compatibility Verification
# ============================================================================

class TestBackwardCompatibility:
    """Tests that verify backward compatibility requirements."""

    def test_all_visualization_types_accessible(self, session):
        """Verify all 6 visualization types can be created.

        If this test passes, all visualization interfaces are working.
        """
        wait_for_rate_limit()

        test_cases = [
            "Generate 20 curves and plot functional boxplot",
            "Generate 20 curves and plot curve boxplot",
            "Generate 15x15 scalar field and show probabilistic marching squares",
            "Generate vectors at 5 positions and show uncertainty lobes",
            "Generate vectors at 5 positions and show squid glyphs",
            "Generate 15x15 scalar field and create contour boxplot with isovalue 0.5",
        ]

        for i, prompt in enumerate(test_cases):
            print(f"\n  Testing visualization {i+1}/6...")
            session.clear()  # Fresh session for each
            wait_for_rate_limit()

            session.send(prompt)
            stats = session.get_stats()

            assert stats["current_vis"] is True, f"Failed to create visualization for: {prompt}"

    def test_analyzer_pipeline_integrity(self, session):
        """Verify analyzer pipeline produces valid output.

        This test ensures the data→vis→analyze pipeline works end-to-end.
        Critical for catching interface changes.
        """
        wait_for_rate_limit()

        session.send(
            "Generate 30 curves, plot functional boxplot, give detailed analysis"
        )

        # Get response after sending
        response = session.get_last_response()

        # Should NOT contain errors
        assert "error" not in response.lower() or "successfully" in response.lower()
        assert "KeyError" not in response
        assert "traceback" not in response.lower()

        # Should contain analysis content
        assert len(response) > 100
        response_lower = response.lower()
        assert any(word in response_lower for word in ["median", "curve", "uncertainty"])


# ============================================================================
# Test Runner
# ============================================================================

def run_all_e2e_tests():
    """Run all end-to-end pipeline tests."""
    print("\n" + "🔄"*35)
    print("END-TO-END PIPELINE TESTS (Layer 2)")
    print("🔄"*35)
    print("\nTesting complete user workflows...")
    print("These tests verify backward compatibility.")
    print("⚠️  Tests make API calls - expect several minutes.\n")

    # Run pytest programmatically
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "test_"
    ])

    plt.close('all')

    return exit_code


if __name__ == "__main__":
    exit_code = run_all_e2e_tests()
    sys.exit(exit_code)

"""End-to-end tests for uncertainty analysis workflows (uses API calls)."""

import pytest
import time
import numpy as np
from unittest.mock import patch
from uvisbox_assistant.session.conversation import ConversationSession


@pytest.fixture
def test_data_path(tmp_path):
    """Create test data file."""
    n_curves, n_points = 30, 100
    x = np.linspace(0, 2*np.pi, n_points)
    curves = []
    for i in range(n_curves):
        amplitude = np.random.uniform(0.8, 1.2)
        phase = np.random.uniform(0, np.pi)
        noise = np.random.normal(0, 0.1, n_points)
        curve = amplitude * np.sin(x + phase) + noise
        curves.append(curve)
    data = np.array(curves)

    data_path = tmp_path / "e2e_test_curves.npy"
    np.save(data_path, data)
    return str(data_path)


@pytest.fixture
def mock_uvisbox_stats():
    """Mock UVisBox statistics output."""
    return {
        "depths": np.random.rand(30),
        "median": np.random.randn(100),
        "percentile_bands": {
            "50_percentile_band": (np.random.randn(100), np.random.randn(100)),
            "90_percentile_band": (np.random.randn(100), np.random.randn(100))
        },
        "outliers": np.random.randn(2, 100),
        "sorted_curves": np.random.randn(30, 100),
        "sorted_indices": np.arange(30)
    }


class TestPattern1VisualizationOnly:
    """Test Pattern 1: Visualization-only workflow (existing behavior)."""

    @pytest.mark.e2e
    def test_generate_and_plot_workflow(self):
        """Test existing data → vis workflow still works."""
        time.sleep(2)  # Rate limit

        session = ConversationSession()

        # Request data generation and visualization
        state = session.send("Generate 30 curves and plot functional boxplot")

        # Verify data was created
        assert state.get("current_data_path") is not None

        # Verify visualization was created
        assert state.get("last_vis_params") is not None
        assert state["last_vis_params"]["_tool_name"] == "plot_functional_boxplot"

        # Verify NO analysis was performed (backward compatibility)
        assert state.get("processed_statistics") is None
        assert state.get("analysis_report") is None


class TestPattern2TextAnalysisOnly:
    """Test Pattern 2: Text-only analysis workflow (new)."""

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_generate_and_analyze_workflow(self, mock_uvisbox, test_data_path, mock_uvisbox_stats):
        """Test new data → statistics → analyzer workflow."""
        time.sleep(3)  # Rate limit (multiple LLM calls)

        # Mock UVisBox statistics
        mock_uvisbox.return_value = mock_uvisbox_stats

        session = ConversationSession()

        # Request data and analysis (no visualization)
        state = session.send(f"Load {test_data_path} and create a quick uncertainty analysis")

        # Verify data was loaded
        assert state.get("current_data_path") is not None

        # Verify statistics were computed
        assert state.get("processed_statistics") is not None
        assert "median" in state["processed_statistics"]
        assert "bands" in state["processed_statistics"]

        # Verify analysis report was generated
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") == "quick"

        # Verify NO visualization was created
        assert state.get("last_vis_params") is None

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_inline_analysis_format(self, mock_uvisbox, test_data_path):
        """Test inline analysis format (1 sentence)."""
        time.sleep(3)

        mock_uvisbox.return_value = {
            "depths": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.array([]),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # Request inline analysis
        state = session.send(f"Load {test_data_path} and give me an inline uncertainty summary")

        # Verify inline report
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") == "inline"

        # Verify report is short
        word_count = len(state["analysis_report"].split())
        assert 10 <= word_count <= 40

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_detailed_analysis_format(self, mock_uvisbox, test_data_path):
        """Test detailed analysis format (full report)."""
        time.sleep(3)

        mock_uvisbox.return_value = {
            "depths": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100)),
                "90_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.random.randn(3, 100),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # Request detailed analysis
        state = session.send(f"Load {test_data_path} and create a detailed uncertainty report")

        # Verify detailed report
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") == "detailed"

        # Verify report is comprehensive
        word_count = len(state["analysis_report"].split())
        assert word_count >= 100

        # Verify mentions key sections
        report_lower = state["analysis_report"].lower()
        assert "median" in report_lower
        assert "band" in report_lower or "percentile" in report_lower
        assert "outlier" in report_lower


class TestPattern3CombinedWorkflow:
    """Test Pattern 3: Combined visualization + analysis workflow (new)."""

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_vis_and_analysis_workflow(self, mock_uvisbox, test_data_path):
        """Test data → vis → statistics → analyzer workflow."""
        time.sleep(4)  # Rate limit (multiple LLM calls + tools)

        mock_uvisbox.return_value = {
            "depths": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.array([]),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # Request both visualization and analysis
        state = session.send(
            f"Load {test_data_path}, plot functional boxplot, and create quick analysis"
        )

        # Verify data was loaded
        assert state.get("current_data_path") is not None

        # Verify visualization was created
        assert state.get("last_vis_params") is not None
        assert state["last_vis_params"]["_tool_name"] == "plot_functional_boxplot"

        # Verify statistics were computed
        assert state.get("processed_statistics") is not None

        # Verify analysis report was generated
        assert state.get("analysis_report") is not None


class TestMultiTurnAnalysisWorkflow:
    """Test multi-turn conversations with analysis."""

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_incremental_analysis_workflow(self, mock_uvisbox, test_data_path):
        """Test building up analysis over multiple turns."""
        mock_uvisbox.return_value = {
            "depths": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.array([]),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # Turn 1: Load data
        time.sleep(2)
        state = session.send(f"Load {test_data_path}")
        assert state.get("current_data_path") is not None
        assert state.get("processed_statistics") is None

        # Turn 2: Compute statistics
        time.sleep(2)
        state = session.send("Compute statistics for this data")
        assert state.get("processed_statistics") is not None
        assert state.get("analysis_report") is None

        # Turn 3: Generate report
        time.sleep(2)
        state = session.send("Now generate a quick analysis report")
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") == "quick"

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_analysis_then_visualization(self, mock_uvisbox, test_data_path):
        """Test doing analysis first, then visualization."""
        mock_uvisbox.return_value = {
            "depths": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.array([]),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # Turn 1: Load and analyze
        time.sleep(3)
        state = session.send(f"Load {test_data_path} and analyze uncertainty")
        assert state.get("processed_statistics") is not None
        assert state.get("analysis_report") is not None

        # Turn 2: Now visualize
        time.sleep(2)
        state = session.send("Now plot it as functional boxplot")
        assert state.get("last_vis_params") is not None
        # Statistics should still be there
        assert state.get("processed_statistics") is not None


class TestAnalysisContextMethods:
    """Test analysis context methods on ConversationSession."""

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_get_analysis_summary(self, mock_uvisbox, test_data_path):
        """Test get_analysis_summary() method."""
        time.sleep(3)

        mock_uvisbox.return_value = {
            "depths": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.random.randn(2, 100),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # Before analysis, should return None
        assert session.get_analysis_summary() is None

        # After analysis, should return summary
        state = session.send(f"Load {test_data_path} and create quick analysis")

        summary = session.get_analysis_summary()
        assert summary is not None
        assert "Analysis State:" in summary
        assert "Statistics computed:" in summary
        assert "Report generated:" in summary

    def test_get_context_summary_with_analysis(self):
        """Test get_context_summary() includes analysis fields."""
        session = ConversationSession()

        # Before any work
        ctx = session.get_context_summary()
        assert ctx["statistics"] is None
        assert ctx["analysis"] is None


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    import matplotlib.pyplot as plt
    sess = ConversationSession()
    yield sess
    sess.clear()
    plt.close('all')


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

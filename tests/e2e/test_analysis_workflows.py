"""End-to-end tests for uncertainty analysis workflows (uses API calls)."""

import pytest
import time
import numpy as np
from unittest.mock import patch
from uvisbox_assistant.conversation import ConversationSession


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

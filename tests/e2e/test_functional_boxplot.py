# ABOUTME: End-to-end tests for functional boxplot workflows.
# ABOUTME: Tests complete workflows from data generation to visualization (uses ~8 LLM calls).
"""End-to-end tests for functional boxplot workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_functional_boxplot


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    sess = ConversationSession()
    yield sess
    sess.clear()
    plt.close('all')


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


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

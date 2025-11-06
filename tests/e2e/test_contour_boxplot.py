"""End-to-end tests for contour boxplot workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_contour_boxplot


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

"""End-to-end tests for uncertainty lobes workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_uncertainty_lobes


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

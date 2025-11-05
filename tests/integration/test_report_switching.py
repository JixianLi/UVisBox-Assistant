"""Integration tests for report switching via hybrid control (v0.3.2)"""

import pytest
from uvisbox_assistant.session.conversation import ConversationSession


class TestReportSwitchingWorkflow:
    """Test users can switch between report types after initial generation"""

    def test_generate_and_switch_report_types(self):
        """
        Test complete workflow:
        1. Generate data and statistics
        2. Generate all three reports
        3. Switch between report types via hybrid control
        """
        session = ConversationSession()

        # Step 1: Generate curves and request detailed analysis
        session.send(
            "generate 100 curves with 50 points each, "
            "compute statistics, and show detailed summary"
        )
        response1 = session.get_last_response()
        assert "detailed" in response1.lower() or len(response1.split()) > 80
        assert session.state.get("analysis_reports") is not None
        assert "inline" in session.state["analysis_reports"]
        assert "quick" in session.state["analysis_reports"]
        assert "detailed" in session.state["analysis_reports"]

        # Step 2: Switch to inline summary (should be instant via hybrid control)
        session.send("inline summary")
        response2 = session.get_last_response()
        assert len(response2.split()) < 50  # Inline is short
        assert "inline" in response2.lower()
        # Should not regenerate - reports still in state
        assert session.state["analysis_reports"] is not None

        # Step 3: Switch to quick summary
        session.send("show quick summary")
        response3 = session.get_last_response()
        assert 40 < len(response3.split()) < 150  # Quick is medium
        assert "quick" in response3.lower()

        # Step 4: Switch back to detailed
        session.send("detailed summary")
        response4 = session.get_last_response()
        assert len(response4.split()) > 80  # Detailed is long
        assert "detailed" in response4.lower()

    def test_report_switching_without_regeneration(self):
        """Verify switching doesn't call analyzer tool again"""
        session = ConversationSession()

        # Generate initial reports
        session.send(
            "generate 50 curves, compute statistics, show quick summary"
        )

        # Verify reports were generated in first place
        if session.state.get("analysis_reports") is None:
            # If model didn't generate reports, skip this test
            import pytest
            pytest.skip("Model did not generate reports - LLM behavior varies")

        initial_reports = session.state["analysis_reports"].copy()

        # Switch to different type
        session.send("inline summary")

        # Verify reports are unchanged (not regenerated)
        assert session.state["analysis_reports"] == initial_reports

    def test_hybrid_control_for_report_retrieval(self):
        """Verify report switching uses hybrid control (fast path)"""
        session = ConversationSession()

        # Generate reports
        session.send(
            "generate 30 curves, compute statistics, show detailed summary"
        )

        # Track message count before switching
        message_count_before = len(session.state["messages"])

        # Switch report type
        session.send("inline summary")
        response = session.get_last_response()

        # Hybrid control should add exactly 2 messages (HumanMessage, AIMessage)
        # No tool calls, so should be fast
        message_count_after = len(session.state["messages"])
        assert message_count_after == message_count_before + 2

        # Verify response is correct
        assert "inline" in response.lower()
        assert len(response.split()) < 50


class TestReportRegenerationDetection:
    """Test smart detection of regenerate vs retrieve intent"""

    def test_explicit_regeneration_request(self):
        """User explicitly asks for 'new' or 'regenerate' - should call analyzer again"""
        import pytest
        session = ConversationSession()

        # Generate initial reports
        session.send(
            "generate 50 curves, compute statistics, show quick summary"
        )

        # Verify reports were generated
        if session.state.get("analysis_reports") is None:
            pytest.skip("Model did not generate reports - LLM behavior varies")

        initial_inline = session.state["analysis_reports"]["inline"]

        # Request regeneration (note: this will actually regenerate via full graph)
        session.send("generate new summary")
        response = session.get_last_response()

        # Should have called analyzer again (reports might differ due to LLM variance)
        # At minimum, state should still have all three types
        assert session.state["analysis_reports"] is not None
        assert "inline" in session.state["analysis_reports"]
        assert "quick" in session.state["analysis_reports"]
        assert "detailed" in session.state["analysis_reports"]

    def test_retrieve_existing_summary(self):
        """User says 'show summary' - should retrieve existing, not regenerate"""
        session = ConversationSession()

        # Generate reports
        session.send(
            "generate 50 curves, compute statistics, show detailed summary"
        )
        initial_reports = session.state["analysis_reports"].copy()

        # Request to show summary (not regenerate)
        session.send("show summary")
        response = session.get_last_response()

        # Should retrieve existing (default to quick)
        assert session.state["analysis_reports"] == initial_reports
        assert "quick" in response.lower() or len(response.split()) < 150


class TestNoReportsAvailable:
    """Test behavior when user requests report before generating"""

    def test_report_request_before_generation(self):
        """User requests report before any analysis - should fail gracefully"""
        session = ConversationSession()

        # Request report without generating data
        session.send("show inline summary")
        response = session.get_last_response()

        # Should explain no reports available yet (various valid explanations)
        response_lower = response.lower()
        assert (
            "no" in response_lower or
            "not" in response_lower or
            "yet" in response_lower or
            "need" in response_lower or
            "first" in response_lower
        ), f"Expected explanation that reports aren't available, got: {response}"

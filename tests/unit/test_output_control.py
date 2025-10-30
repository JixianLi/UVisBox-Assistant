"""Unit tests for verbose mode output control."""

import pytest
from chatuvisbox.output_control import vprint, is_verbose, set_session
from chatuvisbox.conversation import ConversationSession


def test_vprint_verbose_off(capsys):
    """vprint should not output when verbose is OFF."""
    session = ConversationSession()
    session.verbose_mode = False
    set_session(session)

    vprint("Test message")

    captured = capsys.readouterr()
    assert captured.out == ""


def test_vprint_verbose_on(capsys):
    """vprint should output when verbose is ON."""
    session = ConversationSession()
    session.verbose_mode = True
    set_session(session)

    vprint("Test message")

    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_vprint_force_always_prints(capsys):
    """vprint with force=True should always output."""
    session = ConversationSession()
    session.verbose_mode = False
    set_session(session)

    vprint("Forced message", force=True)

    captured = capsys.readouterr()
    assert "Forced message" in captured.out


def test_is_verbose_returns_correct_state():
    """is_verbose should return correct state."""
    session = ConversationSession()

    session.verbose_mode = False
    set_session(session)
    assert is_verbose() is False

    session.verbose_mode = True
    assert is_verbose() is True


def test_vprint_no_session(capsys):
    """vprint should not crash with no session set."""
    set_session(None)

    vprint("Message")  # Should not print, should not crash

    captured = capsys.readouterr()
    assert captured.out == ""

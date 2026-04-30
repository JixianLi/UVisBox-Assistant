# ABOUTME: LLM-package exports for the Ollama-based agent.
# ABOUTME: Re-exports get_system_prompt, create_model_with_tools, and prepare_messages_for_model from model.py.
"""LLM configuration and setup."""

from uvisbox_assistant.llm.model import get_system_prompt, create_model_with_tools, prepare_messages_for_model

__all__ = [
    "get_system_prompt",
    "create_model_with_tools",
    "prepare_messages_for_model",
]

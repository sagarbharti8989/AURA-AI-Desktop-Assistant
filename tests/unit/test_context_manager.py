"""
Unit tests for ContextManager reference resolution.
"""

import pytest
from intelligence.context_manager import context_manager


def test_context_resolution_for_close_it():
    context_manager.update_context("open_app", {"app_name": "chrome"})
    resolved = context_manager.resolve_reference("close it")
    assert resolved == "close chrome"


def test_context_clear():
    context_manager.update_context("open_app", {"app_name": "notepad"})
    context_manager.clear()
    resolved = context_manager.resolve_reference("close it")
    assert resolved == "close it"


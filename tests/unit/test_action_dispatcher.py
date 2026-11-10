"""
Unit tests for ActionDispatcher and verification.
"""

import pytest
from controllers.action_dispatcher import action_dispatcher
from security.request_validator import ActionRequest
from utils.helpers import generate_request_id


def test_dispatcher_handles_registered_action():
    req = ActionRequest(
        request_id=generate_request_id(),
        intent="check_battery",
        parameters={},
        source="voice",
    )
    resp = action_dispatcher.dispatch(req)
    assert resp.success
    assert resp.verified
    assert resp.intent == "check_battery"
    assert "battery" in resp.message.lower()


def test_dispatcher_handles_unregistered_action():
    req = ActionRequest(
        request_id=generate_request_id(),
        intent="unregistered_dummy_intent",
        parameters={},
        source="voice",
    )
    resp = action_dispatcher.dispatch(req)
    assert not resp.success
    assert not resp.verified


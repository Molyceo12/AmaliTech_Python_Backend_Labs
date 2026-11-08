"""Tests for the shared response shape on any status code."""

import json

import pytest
from rest_framework.response import Response

from url_shortener.renderers import EnvelopeJSONRenderer


def _render(data: object, status: int) -> bytes:
    """Render ``data`` as if a view returned it with ``status``."""
    response = Response(data, status=status)
    return EnvelopeJSONRenderer().render(data, renderer_context={"response": response})


@pytest.mark.parametrize(
    ("status", "message"),
    [(200, "OK"), (418, "I'm a Teapot"), (429, "Too Many Requests"), (460, "")],
)
def test_any_status_code_gets_the_shared_shape(status: int, message: str) -> None:
    """A new code needs no new code: the message is its HTTP reason, or empty."""
    assert json.loads(_render({"x": 1}, status)) == {
        "status_code": status,
        "message": message,
        "detail": {"x": 1},
    }


def test_no_content_stays_empty() -> None:
    """``204`` has no body, as HTTP requires."""
    assert _render(None, 204) == b""


def test_without_a_response_the_data_is_not_wrapped() -> None:
    """Rendering outside a view (no response) leaves the data as is."""
    assert json.loads(EnvelopeJSONRenderer().render({"x": 1})) == {"x": 1}


@pytest.mark.parametrize(
    ("detail", "message"),
    [
        ("Short code not found.", "Short code not found."),
        ({"original_url": ["Enter a valid URL."]}, "Enter a valid URL."),
        ({}, "Bad Request"),
    ],
)
def test_error_message_is_the_first_error_text(detail: object, message: str) -> None:
    """An error toast shows the error itself; no text → the HTTP reason."""
    assert json.loads(_render(detail, 400))["message"] == message

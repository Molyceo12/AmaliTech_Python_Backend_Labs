"""Small helpers for the shared response shape."""

from collections.abc import Mapping
from typing import Any


def first_text(detail: Any) -> str:
    """First error text in ``detail``, e.g. ``Enter a valid URL.``; else ``""``."""
    while isinstance(detail, (dict, list)) and detail:
        detail = next(iter(detail.values())) if isinstance(detail, dict) else detail[0]
    return detail if isinstance(detail, str) else ""


def success_message(context: Mapping[str, Any]) -> str:
    """The view's toast for this method, only for a success (below 400)."""
    request, response = context.get("request"), context["response"]
    if request is None or response.status_code >= 400:
        return ""
    messages = getattr(context.get("view"), "success_messages", {})
    return str(messages.get(request.method, ""))

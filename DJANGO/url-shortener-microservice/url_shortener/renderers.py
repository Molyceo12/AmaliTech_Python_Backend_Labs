"""One JSON shape for every API response: ``{status_code, message, detail}``.

``message`` is short text a client can show as a toast.
"""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from rest_framework.renderers import JSONRenderer


def _first_text(detail: Any) -> str:
    """First error text in ``detail``, e.g. ``Enter a valid URL.``; else ``""``."""
    while isinstance(detail, (dict, list)) and detail:
        detail = next(iter(detail.values())) if isinstance(detail, dict) else detail[0]
    return detail if isinstance(detail, str) else ""


def envelope(status_code: int, detail: Any, message: str = "") -> dict[str, Any]:
    """Wrap ``detail``. Message: the one given, else the error text, else the HTTP
    reason (e.g. ``Created``), else ``""`` for a code Python doesn't know."""
    if not message and status_code >= 400:
        message = _first_text(detail)
    if not message:
        try:
            message = HTTPStatus(status_code).phrase
        except ValueError:
            message = ""
    return {"status_code": status_code, "message": message, "detail": detail}


class EnvelopeJSONRenderer(JSONRenderer):
    """Wraps every DRF response, success or error, so no view has to.

    A view sets success toasts per method, e.g.
    ``success_messages = {"POST": "Short URL created."}``.
    """

    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: Mapping[str, Any] | None = None,
    ) -> bytes:
        """``204 No Content`` stays empty: HTTP forbids a body there."""
        context = renderer_context or {}
        response = context.get("response")
        if response is not None and response.status_code != 204:
            data = envelope(response.status_code, data, _success_message(context))
        body: bytes = super().render(data, accepted_media_type, renderer_context)
        return body


def _success_message(context: Mapping[str, Any]) -> str:
    """The view's toast for this method, only for a success (below 400)."""
    request, response = context.get("request"), context["response"]
    if request is None or response.status_code >= 400:
        return ""
    messages = getattr(context.get("view"), "success_messages", {})
    return str(messages.get(request.method, ""))

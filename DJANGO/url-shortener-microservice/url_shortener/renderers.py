"""One JSON shape for every API response: ``{status_code, message, detail}``."""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from rest_framework.renderers import JSONRenderer


def envelope(status_code: int, detail: Any) -> dict[str, Any]:
    """Wrap ``detail``; ``message`` is the HTTP reason, e.g. ``Created``."""
    try:
        message = HTTPStatus(status_code).phrase
    except ValueError:  # a code Python doesn't know, e.g. 460
        message = ""
    return {"status_code": status_code, "message": message, "detail": detail}


class EnvelopeJSONRenderer(JSONRenderer):
    """Wraps every DRF response, success or error, so no view has to."""

    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: Mapping[str, Any] | None = None,
    ) -> bytes:
        """``204 No Content`` stays empty: HTTP forbids a body there."""
        response = (renderer_context or {}).get("response")
        if response is not None and response.status_code != 204:
            data = envelope(response.status_code, data)
        body: bytes = super().render(data, accepted_media_type, renderer_context)
        return body

from schemathesis.models import Case
from schemathesis.hooks import HookContext
from requests.models import Response

from . import get_request_header, set_request_header


def add_invalid_request_content_type(context: HookContext, case: Case) -> Case:
    set_request_header(case, "Content-Type", "invalid/content/type")
    return case


def invalid_request_content_type(response: Response, case: Case) -> None:
    if (
        response.request.body
        and get_request_header(response.request, "Content-Type") == "invalid/content/type"
    ):
        assert (
            response.status_code == 415
        ), "415 status code must be used when the client sends a payload with a content-type not supported by the server."

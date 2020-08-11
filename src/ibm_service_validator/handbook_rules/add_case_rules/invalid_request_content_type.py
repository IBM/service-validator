from typing import Optional
from requests import Response

from schemathesis.models import Case
from schemathesis.hooks import HookContext

from . import get_request_header, original_case_successful, set_request_header


def add_invalid_request_content_type(
    context: HookContext, case: Case, response: Response
) -> Optional[Case]:
    if original_case_successful(response):
        set_request_header(case, "Content-Type", "invalid/content/type")
        return case
    else:
        return None


def invalid_request_content_type(response: Response, case: Case) -> Optional[bool]:
    if (
        response.request.body
        and get_request_header(response.request, "Content-Type") == "invalid/content/type"
    ):
        assert (
            response.status_code == 415
        ), "415 status code must be used when the client sends a payload with a content-type not supported by the server."
    else:
        # skips the check when it's not relevant
        return True
    return None

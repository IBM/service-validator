from typing import Optional
from requests import Response

from schemathesis.models import Case
from schemathesis.hooks import HookContext

from . import original_case_successful


def add_get_with_request_body(
    context: HookContext, case: Case, response: Response
) -> Optional[Case]:
    if original_case_successful(response) and case.method.upper() == "GET":
        # add request body if the original case received 2xx response
        case.body = {"requestBody": "request body passed with GET."}
        return case
    else:
        # otherwise, do not create an additional test case
        return None


def get_with_request_body(response: Response, case: Case) -> Optional[bool]:
    """Validates that request body is ignored for otherwise valid GET request.

    Assumes the constructed request is valid aside from the request body.
    """
    request = response.request
    if request.method == "GET" and request.body:
        assert (
            200 <= response.status_code < 300
        ), "Request body with a GET request must not cause an error."
    else:
        # skips the test when it's not relevant
        return True
    return None

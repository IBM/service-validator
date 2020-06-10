from schemathesis.models import Case
from schemathesis.hooks import HookContext
from schemathesis.models import Response


def add_get_with_request_body(context: HookContext, case: Case) -> Case:
    if case.method.upper() == "GET":
        case.body = {"requestBody": "request body passed with GET."}
    return case


def get_with_request_body(response: Response, case: Case) -> None:
    """Validates that request body is ignored for otherwise valid GET request.

    Assumes the constructed request is valid aside from the request body.
    """
    request = response.request
    if request.method == "GET" and request.body:
        assert (
            200 <= response.status_code < 300
        ), "Request body with a GET request must not cause an error."

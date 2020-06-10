from schemathesis.models import Case
from schemathesis.hooks import HookContext
from requests.models import Response

from . import get_request_header, set_request_header


def add_invalid_accept_header(context: HookContext, case: Case) -> Case:
    set_request_header(case, "Accept", "invalid/accept")
    return case


def invalid_accept_header(response: Response, case: Case) -> None:
    accept_header = get_request_header(response.request, "Accept")
    if accept_header == "invalid/accept":
        assert (
            response.status_code == 406
        ), "Requests including Accept header with only unsupported formats MUST be rejected with a 406 status code."

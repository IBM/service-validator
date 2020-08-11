from typing import Optional
from requests import Response

from schemathesis.models import Case
from schemathesis.hooks import HookContext

from . import get_request_header, original_case_successful, set_request_header


def add_invalid_accept_header(
    context: HookContext, case: Case, response: Response
) -> Optional[Case]:
    if original_case_successful(response):
        set_request_header(case, "Accept", "invalid/accept")
        return case
    else:
        return None


def invalid_accept_header(response: Response, case: Case) -> Optional[bool]:
    accept_header = get_request_header(response.request, "Accept")
    if accept_header == "invalid/accept":
        assert (
            response.status_code == 406
        ), "Requests including Accept header with only unsupported formats MUST be rejected with a 406 status code."
    else:
        # skips the check when it's not relevant
        return True
    return None

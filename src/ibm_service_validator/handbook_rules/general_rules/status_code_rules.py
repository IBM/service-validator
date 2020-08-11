from typing import Optional

from requests import Response
from schemathesis.models import Case


def no_422(response: Response, case: Case) -> Optional[bool]:
    assert (
        response.status_code != 422
    ), "422 code should not be used. Instead, 400 should be returned in response to invalid request payloads. https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-status-codes#client-errors-4xx"
    return None


def no_content_204(response: Response, case: Case) -> Optional[bool]:
    if response.status_code == 204:
        assert (
            not response.content
        ), "204 response must not include a response body. https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-status-codes#success-2xx"
    else:
        # skips the test when it's not relevant
        return True
    return None

from requests.models import Response
from schemathesis.models import Case


def no_422(response: Response, case: Case) -> None:
    assert (
        response.status_code != 422
    ), "422 code should not be used. Instead, 400 should be returned in response to invalid request payloads."


def no_content_204(response: Response, case: Case) -> None:
    if response.status_code == 204:
        assert not response.content, "204 response must not include a response body."

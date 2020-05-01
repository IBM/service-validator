from requests.models import Response
from schemathesis.models import Case


def default_response_content_type(response: Response, case: Case) -> None:
    api_def = case.endpoint.definition
    request = response.request
    request_headers = request.headers
    request_body_content_type = (
        request_headers["Content-Type"]
        if request_headers and "Content-Type" in request_headers
        else None
    )
    if request.body and (
        not request_body_content_type
        or (
            "requestBody" in api_def
            and "content" in api_def["requestBody"]
            and request_body_content_type not in api_def["requestBody"]["content"]
        )
    ):
        assert (
            response.status_code == 415
        ), "415 status code must be used when the client sends a payload with a content-type not supported by the server."


def no_422(response: Response, case: Case) -> None:
    assert (
        response.status_code != 422
    ), "422 code should not be used. Instead, 400 should be returned in response to invalid request payloads."


def no_content_204(response: Response, case: Case) -> None:
    if response.status_code == 204:
        assert not response.content, "204 response must not include a response body."

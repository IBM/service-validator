import schemathesis

from requests.models import Response
from schemathesis.models import Case


@schemathesis.register_check
def accept_header(response: Response, case: Case) -> None:
    request_headers = response.request.headers
    if response.content:
        if not request_headers or "Accept" not in request_headers:
            assert (
                response.headers
                and "Content-Type" in response.headers
                and response.headers["Content-Type"].startswith("application/json")
            ), "Accept header not provided in the request. Response must be JSON, and Content-Type header must start with application/json."


@schemathesis.register_check
def allow_header_in_405(response: Response, case: Case) -> None:
    if response.status_code == 405:
        assert (
            response.headers and "Allow" in response.headers
        ), "For 405 response, must provide the Allow header with the list of accepted request methods."


@schemathesis.register_check
def invalid_request_content_type(response: Response, case: Case) -> None:
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


@schemathesis.register_check
def location_201(response: Response, case: Case) -> None:
    if response.status_code == 201:
        assert (
            response.headers and "Location" in response.headers
        ), "For 201 response, must provide Location header with the URI of the created resource."


@schemathesis.register_check
def no_422(response: Response, case: Case) -> None:
    assert (
        response.status_code != 422
    ), "422 code should not be used. Instead, 400 should be returned in response to invalid request payloads."


@schemathesis.register_check
def no_content_204(response: Response, case: Case) -> None:
    if response.status_code == 204:
        assert not response.content, "204 response must not include a response body."


@schemathesis.register_check
def www_authenticate_401(response: Response, case: Case) -> None:
    if response.status_code == 401:
        assert (
            response.headers and "WWW-Authenticate" in response.headers
        ), "401 response must have WWW-Authenticate header."

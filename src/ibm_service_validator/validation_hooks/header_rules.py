from requests.models import Response
from schemathesis.models import Case


def allow_header_in_405(response: Response, case: Case) -> None:
    if response.status_code == 405:
        assert (
            response.headers and "Allow" in response.headers
        ), "For 405 response, must provide the Allow header with the list of accepted request methods."


def location_201(response: Response, case: Case) -> None:
    if response.status_code == 201:
        assert (
            response.headers and "Location" in response.headers
        ), "For 201 response, must provide Location header with the URI of the created resource."


def no_accept_header(response: Response, case: Case) -> None:
    request_headers = response.request.headers
    if response.content:
        if not request_headers or "Accept" not in request_headers:
            assert (
                response.headers
                and "Content-Type" in response.headers
                and response.headers["Content-Type"].startswith("application/json")
            ), "Accept header not provided in the request. Response must be JSON, and Content-Type header must start with application/json."


def www_authenticate_401(response: Response, case: Case) -> None:
    if response.status_code == 401:
        assert (
            response.headers and "WWW-Authenticate" in response.headers
        ), "401 response must have WWW-Authenticate header."

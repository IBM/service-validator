from requests.models import Response
from schemathesis.models import Case


def allow_header_in_405(response: Response, case: Case) -> None:
    if response.status_code == 405:
        assert (
            response.headers and "Allow" in response.headers
        ), "For 405 response, must provide the Allow header with the list of accepted request methods."


def content_location(response: Response, case: Case) -> None:
    if response.status_code == 200 and case.method.upper() in {"PUT", "PATCH"}:
        assert (
            response.headers and "Content-Location" in response.headers
        ), "For successful PUT or PATCH response, should provide Content-Location header with the URI of the resource."

        content_location_header = response.headers.get("Content-Location")
        relative_uri = case.formatted_path
        absolute_uri = case._get_base_url() + relative_uri
        assert content_location_header in {
            relative_uri,
            absolute_uri,
        }, f"Content-Location header should match the request URI. Content-Location: {content_location_header}, Absolute Request URI: {absolute_uri}, Relative Request URI: {relative_uri}"
    elif response.status_code == 201:
        assert (
            response.headers and "Content-Location" in response.headers
        ), "For 201 response, should provide Content-Location header with the URI of the created resource."

        content_location_header = response.headers.get("Content-Location")
        location = response.headers.get("Location")
        assert (
            content_location_header == location
        ), f"Content-Location header should match the value of the Location header. Content-Location: {content_location_header}, Location: {location}"
    elif response.status_code == 202 and case.method.upper() in {
        "DELETE",
        "PATCH",
        "POST",
        "PUT",
    }:
        assert (
            response.headers and "Content-Location" in response.headers
        ), "For 202 response from a DELETE, PATCH, POST, or PUT, should provide Content-Location header with the URI where resource may be obtained."


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
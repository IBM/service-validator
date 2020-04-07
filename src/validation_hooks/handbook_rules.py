from requests.models import Response

import schemathesis
from schemathesis.models import Case


@schemathesis.register_check
def body_no_content_type(response: Response, case: Case) -> None:
    apiDef = case.endpoint.definition
    request = response.request
    requestHeaders = request.headers
    requestBodyContentType = (
        requestHeaders["content-type"]
        if requestHeaders and "content-type" in requestHeaders
        else None
    )
    if request.body and (
        not requestBodyContentType
        or (
            "requestBody" in apiDef
            and "content" in apiDef["requestBody"]
            and requestBodyContentType not in apiDef["requestBody"]["content"]
        )
    ):
        assert response.status_code == 415


@schemathesis.register_check
def accept_header(response: Response, case: Case) -> None:
    requestHeaders = response.request.headers
    if not requestHeaders or "accept" not in requestHeaders:
        assert (
            response.headers
            and "Content-Type" in response.headers
            and response.headers["Content-Type"].startswith("application/json")
        )


@schemathesis.register_check
def location_201(response: Response, case: Case) -> None:
    if response.status_code == 201:
        assert response.headers and "Location" in response.headers


@schemathesis.register_check
def no_content_204(response: Response, case: Case) -> None:
    if response.status_code == 204:
        assert not response.text and not response.json


@schemathesis.register_check
def www_authenticate_401(response: Response, case: Case) -> None:
    if response.status_code == 401:
        assert response.headers and "WWW-Authenticate" in response.headers


@schemathesis.register_check
def allow_405(response: Response, case: Case) -> None:
    if response.status_code == 405:
        assert response.headers and "Allow" in response.headers


@schemathesis.register_check
def no_422(response: Response, case: Case) -> None:
    assert response.status_code != 422

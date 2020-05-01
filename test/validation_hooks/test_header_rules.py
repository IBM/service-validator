import pytest

import schemathesis

from test.validation_hooks import (
    mock_decorator,
    mock_objects,
    prepare_request,
    create_endpoint,
)

schemathesis.register_check = mock_decorator  # must occur before handbook rules imported

from src.ibm_service_validator.validation_hooks import header_rules as rules


def test_allow_header_in_405_positive():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 405
    mock_response.headers["Mock-Header"] = "mock/header"

    with pytest.raises(AssertionError, match="For 405 response, must provide the Allow"):
        rules.allow_header_in_405(mock_response, mock_case)


def test_allow_header_in_405_negative():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 405
    mock_response.headers["Allow"] = ["GET", "POST"]

    rules.allow_header_in_405(mock_response, mock_case)


def test_allow_header_in_405_negative_1():
    mock_case, mock_response = mock_objects()

    # not a 405 response
    mock_response.status_code = 200

    rules.allow_header_in_405(mock_response, mock_case)


def test_default_response_content_type_positive():
    mock_case, mock_response = mock_objects()

    request_body = {"foo": "request_body"}

    mock_response.request = prepare_request(
        headers={"Mock-Header": "mock/header"}, data=request_body, json=request_body
    )

    mock_response._content = {"foo": "response body"}
    # Content-Type should be application/json
    mock_response.headers["Content-Type"] = "text/plain"

    with pytest.raises(AssertionError, match="Accept header not provided"):
        rules.default_response_content_type(mock_response, mock_case)


def test_default_response_content_type_negative():
    mock_case, mock_response = mock_objects()

    mock_response.request = prepare_request(headers={"Mock-Header": "mock/header"})

    mock_response._content = {"foo": "response body"}
    mock_response.headers["Content-Type"] = "application/json"

    # Should not raise an error
    rules.default_response_content_type(mock_response, mock_case)


def test_default_response_content_type_negative_1():
    mock_case, mock_response = mock_objects()

    mock_response.request = prepare_request()

    # Should not raise an error
    rules.default_response_content_type(mock_response, mock_case)


def test_default_response_content_type_negative_2():
    mock_case, mock_response = mock_objects()

    # Request has a non application/json accept header
    mock_response.request = prepare_request(headers={"Accept": "text/plain"})

    mock_response._content = {"foo": "response body"}

    # accept is text/plain, so
    rules.default_response_content_type(mock_response, mock_case)


def test_location_201_positive():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 201
    # no location header, should raise an error
    with pytest.raises(AssertionError, match="For 201 response, must provide Location"):
        rules.location_201(mock_response, mock_case)


def test_location_201_negative():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 201
    mock_response.headers["Location"] = "http://fakeapi.com/created_resource"

    # this call to location_201 should not raise an exception
    rules.location_201(mock_response, mock_case)


def test_location_201_negative_1():
    mock_case, mock_response = mock_objects()

    # not a 201 status code
    mock_response.status_code = 200
    mock_response.headers["Location"] = "http://fakeapi.com/created_resource"

    # this call to location_201 should not raise an exception
    rules.location_201(mock_response, mock_case)


def test_www_authenticate_401_positive():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 401
    mock_response.headers["Mock-Header"] = "mock/header"
    with pytest.raises(
        AssertionError, match="401 response must have WWW-Authenticate header."
    ):
        rules.www_authenticate_401(mock_response, mock_case)


def test_www_authenticate_401_negative():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 401
    mock_response.headers["WWW-Authenticate"] = "invalid credentials"
    rules.www_authenticate_401(mock_response, mock_case)


def test_www_authenticate_401_negative_1():
    mock_case, mock_response = mock_objects()

    # non-401 status code
    mock_response.status_code = 400
    rules.www_authenticate_401(mock_response, mock_case)

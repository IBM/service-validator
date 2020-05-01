import pytest

import schemathesis

from test.validation_hooks import (
    mock_decorator,
    mock_objects,
    prepare_request,
    create_endpoint,
)

schemathesis.register_check = mock_decorator  # must occur before handbook rules imported

from src.ibm_service_validator.validation_hooks import status_code_rules as rules


def test_invalid_request_content_type_positive():
    mock_case, mock_response = mock_objects()

    # Initializing an endpoint object with only section of an API def
    mock_case.endpoint = create_endpoint(
        definition={
            "requestBody": {"content": {"multipart/form-data": {}, "text/plain": {}}}
        }
    )

    request_body = {"foo": "request_body"}

    mock_response.request = prepare_request(
        headers={"Mock-Header": "mock/header"}, data=request_body, json=request_body
    )

    mock_response.status_code = 400
    # Request body with content-type not in the API definition
    with pytest.raises(AssertionError, match="415 status code"):
        rules.invalid_request_content_type(mock_response, mock_case)


def test_invalid_request_content_type_positive_1():
    mock_case, mock_response = mock_objects()

    # Initializing an endpoint object with only section of an API def
    mock_case.endpoint = create_endpoint(
        definition={
            "requestBody": {"content": {"multipart/form-data": {}, "text/plain": {}}}
        }
    )

    request_body = {"foo": "request_body"}

    mock_response.request = prepare_request(
        headers={"Mock-Header": "mock/header"}, data=request_body, json=request_body
    )

    mock_response.status_code = 400
    # Request body with no content-type header
    with pytest.raises(AssertionError, match="415 status code"):
        rules.invalid_request_content_type(mock_response, mock_case)


def test_invalid_request_content_type_negative():
    mock_case, mock_response = mock_objects()

    # Initializing an endpoint object with only section of an API def
    mock_case.endpoint = create_endpoint(
        definition={
            "requestBody": {"content": {"multipart/form-data": {}, "text/plain": {}}}
        }
    )

    request_body = {"foo": "request_body"}

    mock_response.request = prepare_request(
        headers={"Mock-Header": "mock/header"}, data=request_body, json=request_body
    )

    mock_response.status_code = 415
    # Correct status code used
    rules.invalid_request_content_type(mock_response, mock_case)


def test_invalid_request_content_type_negative_1():
    mock_case, mock_response = mock_objects()

    # Initializing an endpoint object with only section of an API def
    mock_case.endpoint = create_endpoint(
        definition={
            "requestBody": {"content": {"multipart/form-data": {}, "text/plain": {}}}
        }
    )

    mock_response.request = prepare_request()

    mock_response.status_code = 400
    # Correct status code used
    rules.invalid_request_content_type(mock_response, mock_case)


def test_no_422_positive():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 422
    with pytest.raises(AssertionError, match="422 code should not be used."):
        rules.no_422(mock_response, mock_case)


def test_no_422_negative():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 400
    rules.no_422(mock_response, mock_case)


def test_no_content_204_positive():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 204
    mock_response._content = {"foo": "response body with a 204"}
    with pytest.raises(
        AssertionError, match="204 response must not include a response body."
    ):
        rules.no_content_204(mock_response, mock_case)


def test_no_content_204_negative():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 204
    rules.no_content_204(mock_response, mock_case)


def test_no_content_204_negative_1():
    mock_case, mock_response = mock_objects()

    mock_response.status_code = 200
    rules.no_content_204(mock_response, mock_case)

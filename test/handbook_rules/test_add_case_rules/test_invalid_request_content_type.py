import pytest

from schemathesis.hooks import HookContext

from src.ibm_service_validator.handbook_rules.add_case_rules import (
    invalid_request_content_type as hooks,
)


def test_add_invalid_request_content_type(mock_case, mock_response):
    mock_response.status_code = 200
    new_case = hooks.add_invalid_request_content_type(
        HookContext(mock_case.endpoint), mock_case, mock_response
    )
    assert new_case.headers["Content-Type"] == "invalid/content/type"


def test_add_invalid_request_content_type_1(mock_case, mock_response):
    mock_case.headers = {"content-type": "application/json"}
    mock_response.status_code = 200
    new_case = hooks.add_invalid_request_content_type(
        HookContext(mock_case.endpoint), mock_case, mock_response
    )
    assert new_case.headers["content-type"] == "invalid/content/type"


def test_add_invalid_request_content_type_2(mock_case, mock_response):
    mock_case.headers = {"Mock-Header": "mock/value"}
    new_case = hooks.add_invalid_request_content_type(
        HookContext(mock_case.endpoint), mock_case, mock_response
    )
    assert new_case.headers["Content-Type"] == "invalid/content/type"


def test_add_invalid_request_content_type_2(mock_case, mock_response):
    mock_response.status_code = 400
    assert not hooks.add_invalid_request_content_type(
        HookContext(mock_case.endpoint), mock_case, mock_response
    )


def test_invalid_request_content_type_positive(
    mock_case, mock_response, prepare_request, request_body
):
    mock_response.request = prepare_request(
        headers={"Content-Type": "invalid/content/type"},
        data=request_body,
        json=request_body,
    )

    # status_code should be 415
    mock_response.status_code = 400
    with pytest.raises(AssertionError, match="415 status code"):
        hooks.invalid_request_content_type(mock_response, mock_case)


def test_invalid_request_content_type_negative(
    mock_case, mock_response, prepare_request, request_body
):
    mock_response.request = prepare_request(
        headers={"Content-Type": "invalid/content/type"},
        data=request_body,
        json=request_body,
    )

    mock_response.status_code = 415
    # Correct status code used
    hooks.invalid_request_content_type(mock_response, mock_case)


def test_invalid_request_content_type_negative_1(
    mock_case, mock_response, prepare_request
):
    mock_response.request = prepare_request()
    # No request body, so check should pass
    hooks.invalid_request_content_type(mock_response, mock_case)


@pytest.fixture()
def request_body():
    return {"foo": "request_body"}

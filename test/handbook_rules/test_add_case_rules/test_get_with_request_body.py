import pytest

from schemathesis.hooks import HookContext

from src.ibm_service_validator.handbook_rules.add_case_rules import (
    get_with_request_body as hooks,
)


def test_add_get_with_request_body(mock_case):
    mock_case.endpoint.method = "GET"
    new_case = hooks.add_get_with_request_body(HookContext(mock_case), mock_case)
    assert new_case.body


def test_get_with_request_body_positive(mock_case, mock_response, prepare_request):
    mock_response.status_code = 400
    mock_response.request.prepare_method("GET")
    mock_response.request.prepare_body(None, None, json={"foo": "requestBody"})
    with pytest.raises(AssertionError, match="Request body with a GET"):
        hooks.get_with_request_body(mock_response, mock_case)


def test_get_with_request_body_negative(mock_case, mock_response):
    mock_response.request.prepare_method("GET")
    # GET request but no body, so assertion should not be run
    hooks.get_with_request_body(mock_response, mock_case)

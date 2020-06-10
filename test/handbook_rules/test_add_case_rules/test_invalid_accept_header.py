import pytest

from schemathesis.hooks import HookContext

from src.ibm_service_validator.handbook_rules.add_case_rules import (
    invalid_accept_header as hooks,
)


def test_add_invalid_accept_header(mock_case):
    new_case = hooks.add_invalid_accept_header(HookContext(mock_case.endpoint), mock_case)
    assert new_case.headers["Accept"] == "invalid/accept"


def test_add_invalid_accept_header_1(mock_case):
    mock_case.headers = {"accept": "application/json"}
    new_case = hooks.add_invalid_accept_header(HookContext(mock_case.endpoint), mock_case)
    assert new_case.headers["accept"] == "invalid/accept"


def test_invalid_accept_header_positive(mock_case, mock_response, prepare_request):
    mock_response.request = prepare_request(headers={"Accept": "invalid/accept"})
    with pytest.raises(AssertionError, match="Requests including Accept header"):
        hooks.invalid_accept_header(mock_response, mock_case)


def test_invalid_accept_header_negative(mock_case, mock_response, prepare_request):
    mock_response.request = prepare_request(headers={"Accept": "application/json"})
    # valid accept header provided
    hooks.invalid_accept_header(mock_response, mock_case)

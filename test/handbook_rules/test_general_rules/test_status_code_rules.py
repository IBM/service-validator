import pytest

from src.ibm_service_validator.handbook_rules.general_rules import (
    status_code_rules as rules,
)


def test_no_422_positive(mock_case, mock_response):
    mock_response.status_code = 422
    with pytest.raises(AssertionError, match="422 code should not be used."):
        rules.no_422(mock_response, mock_case)


def test_no_422_negative(mock_case, mock_response):
    mock_response.status_code = 400
    rules.no_422(mock_response, mock_case)


def test_no_content_204_positive(mock_case, mock_response):
    mock_response.status_code = 204
    mock_response._content = {"foo": "response body with a 204"}
    with pytest.raises(
        AssertionError, match="204 response must not include a response body."
    ):
        rules.no_content_204(mock_response, mock_case)


def test_no_content_204_negative(mock_case, mock_response):
    mock_response.status_code = 204
    rules.no_content_204(mock_response, mock_case)


def test_no_content_204_negative(mock_case, mock_response):
    mock_response.status_code = 201
    rules.no_content_204(mock_response, mock_case)

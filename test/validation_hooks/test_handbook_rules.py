from test.validation_hooks import mock_decorator

import pytest
from requests.models import Response
from src.validation_hooks import handbook_rules

import schemathesis
from schemathesis.models import Case

schemathesis.register_check = mock_decorator


def test_201_status_code_positive():
    mock_case = Case("http://fakeapi.com")
    mock_response = Response()
    mock_response.status_code = 201
    # no location header, should raise an error
    with pytest.raises(AssertionError):
        handbook_rules.location_201(mock_response, mock_case)


def test_201_status_code_negative():
    mock_case = Case("http://fakeapi.com")
    mock_response = Response()
    mock_response.status_code = 201
    mock_response.headers["Location"] = "http://fakeapi.com/created_resource"
    # this call to location_201 should not raise an exception
    handbook_rules.location_201(mock_response, mock_case)

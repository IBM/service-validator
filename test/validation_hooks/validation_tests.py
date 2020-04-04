import pytest

from schemathesis.models import Case
from requests.models import Response

from src.validation_hooks import handbook_rules

def test_201_status_code():
    mock_response = Response()
    mock_case = Case('http://fakeapi.com')
    mock_response.status_code = 201
    # no location header, should raise an error
    with pytest.raises(Exception):
        handbook_rules.location_201(mock_response, mock_case)

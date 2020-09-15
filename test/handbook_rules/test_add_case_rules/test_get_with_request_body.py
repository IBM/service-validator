#!/usr/bin/env python
# Copyright 2020 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from schemathesis.hooks import HookContext

from src.ibm_service_validator.handbook_rules.add_case_rules import (
    get_with_request_body as hooks,
)


def test_add_get_with_request_body_positive(mock_case, mock_response):
    mock_case.endpoint.method = "GET"
    mock_response.status_code = 200
    new_case = hooks.add_get_with_request_body(
        HookContext(mock_case), mock_case, mock_response
    )
    assert new_case.method.upper() == "GET" and new_case.body


def test_add_get_with_request_body_negative(mock_case, mock_response):
    mock_case.endpoint.method = "GET"
    mock_response.status_code = 400
    assert not hooks.add_get_with_request_body(
        HookContext(mock_case), mock_case, mock_response
    )


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

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
    invalid_accept_header as hooks,
)


def test_add_invalid_accept_header(mock_case, mock_response):
    mock_response.status_code = 200
    new_case = hooks.add_invalid_accept_header(
        HookContext(mock_case.endpoint), mock_case, mock_response
    )
    assert new_case.headers["Accept"] == "invalid/accept"


def test_add_invalid_accept_header_1(mock_case, mock_response):
    mock_case.headers = {"accept": "application/json"}
    mock_response.status_code = 200
    new_case = hooks.add_invalid_accept_header(
        HookContext(mock_case.endpoint), mock_case, mock_response
    )
    assert new_case.headers["accept"] == "invalid/accept"


def test_add_invalid_accept_header_negative(mock_case, mock_response):
    mock_case.headers = {"accept": "application/json"}
    mock_response.status_code = 400
    assert not hooks.add_invalid_accept_header(
        HookContext(mock_case.endpoint), mock_case, mock_response
    )


def test_invalid_accept_header_positive(mock_case, mock_response, prepare_request):
    mock_response.request = prepare_request(headers={"Accept": "invalid/accept"})
    with pytest.raises(AssertionError, match="Requests including Accept header"):
        hooks.invalid_accept_header(mock_response, mock_case)


def test_invalid_accept_header_negative(mock_case, mock_response, prepare_request):
    mock_response.request = prepare_request(headers={"Accept": "application/json"})
    # valid accept header provided
    hooks.invalid_accept_header(mock_response, mock_case)

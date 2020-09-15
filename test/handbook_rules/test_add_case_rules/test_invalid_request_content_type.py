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

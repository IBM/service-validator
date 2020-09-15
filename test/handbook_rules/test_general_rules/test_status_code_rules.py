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

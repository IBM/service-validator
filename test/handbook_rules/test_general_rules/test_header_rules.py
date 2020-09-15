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

from src.ibm_service_validator.handbook_rules.general_rules import header_rules as rules


def test_allow_header_in_405_positive(mock_case, mock_response):
    mock_response.status_code = 405
    mock_response.headers["Mock-Header"] = "mock/header"

    with pytest.raises(AssertionError, match="For 405 response, must provide the Allow"):
        rules.allow_header_in_405(mock_response, mock_case)


def test_allow_header_in_405_negative(mock_case, mock_response):
    mock_response.status_code = 405
    mock_response.headers["Allow"] = ["GET", "POST"]

    rules.allow_header_in_405(mock_response, mock_case)


def test_allow_header_in_405_negative_1(mock_case, mock_response):
    # not a 405 response
    mock_response.status_code = 200

    rules.allow_header_in_405(mock_response, mock_case)


def test_content_location_200_positive(mock_case, mock_response):
    mock_response.status_code = 200
    mock_case.endpoint.method = "patch"
    # no content-location header, should raise an error
    with pytest.raises(AssertionError, match="For successful PUT or PATCH response"):
        rules.content_location(mock_response, mock_case)


def test_content_location_200_positive_1(mock_case, mock_response):
    mock_response.status_code = 200
    mock_response.headers["Content-Location"] = "/wrong/relative/path"
    mock_case.endpoint.method = "patch"
    mock_case.endpoint.path = "/path1"
    mock_case.endpoint.base_url = "http://localhost"
    # content-location header given but does not match request uri
    with pytest.raises(
        AssertionError, match="Content-Location header should match the request URI"
    ):
        rules.content_location(mock_response, mock_case)


def test_content_location_201_positive(mock_case, mock_response):
    mock_response.status_code = 201
    # no content-location header, should raise an error
    with pytest.raises(
        AssertionError, match="For 201 response, should provide Content-Location"
    ):
        rules.content_location(mock_response, mock_case)


def test_content_location_201_positive_1(mock_case, mock_response):
    mock_response.status_code = 201
    mock_response.headers["Content-Location"] = "http://fakeapi.com/created_resource"
    # content-location header given but no Location header in response
    with pytest.raises(AssertionError, match="Content-Location header should match"):
        rules.content_location(mock_response, mock_case)


def test_content_location_201_positive_2(mock_case, mock_response):
    mock_response.status_code = 201
    mock_response.headers["Content-Location"] = "http://fakeapi.com/created_resource"
    mock_response.headers["Location"] = "http://fakeapi.com/different_resource"
    # content-location header given but does not match Location header
    with pytest.raises(AssertionError, match="Content-Location header should match"):
        rules.content_location(mock_response, mock_case)


def test_content_location_202_positive(mock_case, mock_response):
    mock_response.status_code = 202
    mock_response.headers["Mock-Header"] = "mock/value"
    mock_case.endpoint.method = "delete"
    # content-location header not provided
    with pytest.raises(
        AssertionError, match="For 202 response from a DELETE, PATCH, POST, or PUT"
    ):
        rules.content_location(mock_response, mock_case)


def test_content_location_200_negative(mock_case, mock_response):
    mock_response.status_code = 200
    mock_response.headers["Content-Location"] = "http://localhost/path1"
    mock_case.endpoint.method = "put"
    mock_case.endpoint.path = "/path1"
    mock_case.endpoint.base_url = "http://localhost"
    # content-location header given and matches the absolute path
    rules.content_location(mock_response, mock_case)


def test_content_location_200_negative_1(mock_case, mock_response):
    mock_response.status_code = 200
    mock_response.headers["Content-Location"] = "/path1"
    mock_case.endpoint.method = "put"
    mock_case.endpoint.path = "/path1"
    mock_case.endpoint.base_url = "http://localhost"
    # content-location header given and matches the relative path
    rules.content_location(mock_response, mock_case)


def test_content_location_201_negative(mock_case, mock_response):
    mock_response.status_code = 201
    mock_response.headers["Content-Location"] = "http://fakeapi.com/created_resource"
    mock_response.headers["Location"] = "http://fakeapi.com/created_resource"
    # content-location header given and matches Location header
    rules.content_location(mock_response, mock_case)


def test_content_location_201_negative_1(mock_case, mock_response):
    mock_response.status_code = 200
    mock_case.endpoint.method = "get"
    # check does not apply to 200 response from a GET
    rules.content_location(mock_response, mock_case)


def test_content_location_202_negative(mock_case, mock_response):
    mock_response.status_code = 202
    mock_response.headers["Content-Location"] = "mock/value"
    mock_case.endpoint.method = "post"
    # content-location header provided
    rules.content_location(mock_response, mock_case)


def test_location_201_positive(mock_case, mock_response):
    mock_response.status_code = 201
    # no location header, should raise an error
    with pytest.raises(AssertionError, match="For 201 response, must provide Location"):
        rules.location_201(mock_response, mock_case)


def test_location_201_negative(mock_case, mock_response):
    mock_response.status_code = 201
    mock_response.headers["Location"] = "http://fakeapi.com/created_resource"

    # this call to location_201 should not raise an exception
    rules.location_201(mock_response, mock_case)


def test_location_201_negative_1(mock_case, mock_response):
    # not a 201 status code
    mock_response.status_code = 200
    mock_response.headers["Location"] = "http://fakeapi.com/created_resource"

    # this call to location_201 should not raise an exception
    rules.location_201(mock_response, mock_case)


def test_no_accept_header_positive(mock_case, mock_response, prepare_request):
    request_body = {"foo": "request_body"}

    mock_response.request = prepare_request(
        headers={"Mock-Header": "mock/header"}, data=request_body, json=request_body
    )

    mock_response._content = {"foo": "response body"}
    # Content-Type should be application/json
    mock_response.headers["Content-Type"] = "text/plain"

    with pytest.raises(AssertionError, match="Accept header not provided"):
        rules.no_accept_header(mock_response, mock_case)


def test_no_accept_header_negative(mock_case, mock_response, prepare_request):
    mock_response.request = prepare_request(headers={"Mock-Header": "mock/header"})

    mock_response._content = {"foo": "response body"}
    mock_response.headers["Content-Type"] = "application/json"

    # Should not raise an error
    rules.no_accept_header(mock_response, mock_case)


def test_no_accept_header_negative_1(mock_case, mock_response, prepare_request):
    mock_response.request = prepare_request()

    # Should not raise an error
    rules.no_accept_header(mock_response, mock_case)


def test_no_accept_header_negative_2(mock_case, mock_response, prepare_request):
    # Request has a non application/json accept header
    mock_response.request = prepare_request(headers={"Accept": "text/plain"})

    mock_response._content = {"foo": "response body"}

    # accept is text/plain, so
    rules.no_accept_header(mock_response, mock_case)


def test_www_authenticate_401_positive(mock_case, mock_response):
    mock_response.status_code = 401
    mock_response.headers["Mock-Header"] = "mock/header"
    with pytest.raises(
        AssertionError, match="401 response must have WWW-Authenticate header."
    ):
        rules.www_authenticate_401(mock_response, mock_case)


def test_www_authenticate_401_negative(mock_case, mock_response):
    mock_response.status_code = 401
    mock_response.headers["WWW-Authenticate"] = "invalid credentials"
    rules.www_authenticate_401(mock_response, mock_case)


def test_www_authenticate_401_negative_1(mock_case, mock_response):
    # non-401 status code
    mock_response.status_code = 400
    rules.www_authenticate_401(mock_response, mock_case)

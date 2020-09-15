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

import os
import pytest
from typing import Any, Callable, Dict, IO

from click.testing import CliRunner

import ibm_service_validator.cli
from .mock_server import flask_app

from requests.models import Response, PreparedRequest
from schemathesis.models import Case, Endpoint, EndpointDefinition

from src.ibm_service_validator.cli.process_config import (
    DEFAULT_CONFIG,
    SCHEMATHESIS_CONFIG_NAME,
)


@pytest.fixture()
def check_str():
    """Comma-separated list of most of the validation functions excluding any add_case_rules."""
    return "allow_header_in_405,location_201,no_422,no_accept_header,no_content_204,www_authenticate_401, \
        not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance"


@pytest.fixture(scope="session")
def cli():
    """CLI runner helper to invoke methods in the CLI."""
    cli_runner = CliRunner()

    class Runner:
        @staticmethod
        def run(*args, **kwargs):
            return cli_runner.invoke(ibm_service_validator.cli.run, args, **kwargs)

        @staticmethod
        def init(*args, **kwargs):
            return cli_runner.invoke(ibm_service_validator.cli.init, args, **kwargs)

        @staticmethod
        def replay(*args, **kwargs):
            return cli_runner.invoke(ibm_service_validator.cli.replay, args, **kwargs)

        @staticmethod
        def main(*args, **kwargs):
            return cli_runner.invoke(
                ibm_service_validator.cli.ibm_service_validator, args, **kwargs
            )

    return Runner()


@pytest.fixture()
def config_off_object():
    return {
        section_name: {rule_name: "off" for rule_name in DEFAULT_CONFIG[section_name]}
        for section_name in DEFAULT_CONFIG
    }


@pytest.fixture()
def config_warn_object():
    return {
        section_name: {rule_name: "warn" for rule_name in DEFAULT_CONFIG[section_name]}
        for section_name in DEFAULT_CONFIG
    }


@pytest.fixture()
def config_partial_warn():
    return {
        SCHEMATHESIS_CONFIG_NAME: {
            "status_code_conformance": "warn",
            "content_type_conformance": "warn",
        },
    }


@pytest.fixture()
def create_endpoint():
    def f(
        path=None,
        method=None,
        definition=None,
        schema=None,
        app=None,
        base_url=None,
        path_parameters=None,
        headers=None,
        cookies=None,
        query=None,
        body=None,
        form_data=None,
    ) -> Endpoint:
        return Endpoint(
            path,
            method,
            EndpointDefinition(raw=definition, resolved=definition, scope="global"),
            schema,
            app,
            base_url,
            path_parameters,
            headers,
            cookies,
            query,
            body,
            form_data,
        )

    return f


@pytest.fixture()
def invalid_examples() -> str:
    """Return path to a schema with invalid examples field."""

    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, "mock_definitions", "invalid_examples.yaml")


@pytest.fixture()
def invalid_schema() -> str:
    """Return path to the invalid API definition."""

    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, "mock_definitions", "invalid_schema.yaml")


@pytest.fixture()
def mixed_api_def() -> str:
    """Return path to API definition that causes status code conformance failure."""

    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, "mock_definitions", "mixed.yaml")


@pytest.fixture()
def mock_case(create_endpoint):
    return Case(endpoint=create_endpoint())


@pytest.fixture()
def mock_response(prepare_request):
    response = Response()
    response.request = prepare_request()
    return response


@pytest.fixture()
def need_authorization() -> str:
    """Return path of the mock server API definition."""

    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, "mock_definitions", "need_authorization.yaml")


@pytest.fixture()
def prepare_request():
    def f(
        method="GET",
        url="http://mockapi.com",
        headers=None,
        files=None,
        data=None,
        params=None,
        auth=None,
        cookies=None,
        hooks=None,
        json=None,
    ) -> PreparedRequest:
        request = PreparedRequest()
        request.prepare(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=data,
            params=params,
            auth=auth,
            cookies=cookies,
            hooks=hooks,
            json=json,
        )

        return request

    return f


@pytest.fixture()
def server_definition() -> str:
    """Return path of the mock server API definition."""

    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, "mock_definitions", "mock_server.yaml")


@pytest.fixture()
def status_code_failure() -> str:
    """Return path to API definition that causes status code conformance failure."""

    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, "mock_definitions", "status_code_conformance_failure.yaml")


@pytest.fixture()
def tmp_cwd(tmp_path):
    """Set the cwd to a temporary path. Return path."""
    os.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def write_to_file():
    def f(
        file_name: str, config: Dict[str, Any], dump: Callable[[Any, IO], None]
    ) -> None:
        config_file = open(file_name, "a+")
        dump(config, config_file)
        config_file.close()

    return f

import os
import pytest
from typing import Any, Callable, Dict, IO

from click.testing import CliRunner

from .mock_server import flask_app
from src.ibm_service_validator.cli import commands

from requests.models import Response, PreparedRequest
from schemathesis.models import Case, Endpoint

from src.ibm_service_validator.cli.process_config import (
    HANDBOOK_CONFIG_NAME,
    SCHEMATHESIS_CONFIG_NAME,
)


@pytest.fixture(scope="session")
def cli():
    """CLI runner helper to invoke methods in the CLI."""
    cli_runner = CliRunner()

    class Runner:
        @staticmethod
        def run(*args, **kwargs):
            return cli_runner.invoke(commands.run, args, **kwargs)

        @staticmethod
        def init(*args, **kwargs):
            return cli_runner.invoke(commands.init, args, **kwargs)

        @staticmethod
        def main(*args, **kwargs):
            return cli_runner.invoke(commands.ibm_service_validator, args, **kwargs)

    return Runner()


@pytest.fixture()
def config_object():
    return {
        HANDBOOK_CONFIG_NAME: {
            "allow_header_in_405": "off",
            "default_response_content_type": "off",
            "location_201": "off",
            "no_422": "off",
            "no_accept_header": "off",
            "no_content_204": "off",
            "www_authenticate_401": "off",
        },
        SCHEMATHESIS_CONFIG_NAME: {
            "not_a_server_error": "off",
            "status_code_conformance": "off",
            "content_type_conformance": "off",
            "response_schema_conformance": "off",
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
            definition,
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
def mock_case():
    return Case("http://mockapi.com")


@pytest.fixture()
def mock_response():
    return Response()


@pytest.fixture()
def write_to_file():
    def f(
        file_name: str, config: Dict[str, Any], dump: Callable[[Any, IO], None]
    ) -> None:
        config_file = open(file_name, "a+")
        dump(config, config_file)
        config_file.close()

    return f


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

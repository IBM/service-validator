import pytest
from _pytest.main import ExitCode

from ..mock_server import flask_app
from multiprocessing import Process

SERVER_PROCESS: Process = None
SERVER_URL: str = None


def setup_module():
    """Start Flask server as subprocess and keep global reference to process."""
    global SERVER_URL
    global SERVER_PROCESS
    app = flask_app.create_app()
    SERVER_URL, SERVER_PROCESS = flask_app.run_server_as_child(app)


def teardown_module():
    SERVER_PROCESS.terminate()


def test_run(cli, server_definition):
    result = cli.run(
        server_definition,
        "--base-url=" + SERVER_URL,
        "--hypothesis-phases=explicit,generate",
    )

    assert result.exit_code == ExitCode.OK


def test_run_with_all_args(cli, server_definition):
    result = cli.run(
        server_definition,
        "--auth=fake_user:fake_password",
        "--auth-type=basic",
        "--base-url=" + SERVER_URL,
        "--header=Authorization:Bearer 123",
        "--hypothesis-phases=generate,explicit",
        "--endpoint=allof",
        "--endpoint=array",
        "--endpoint=boolean",
        "--exitfirst",
        "--hypothesis-deadline=500",
        "--hypothesis-derandomize",
        "--hypothesis-max-examples=10",
        "--hypothesis-seed=0",
        "--hypothesis-verbosity=quiet",
        "--method=get",
        "--request-timeout=500",
        "--show-errors-tracebacks",
        "--tag=test_tag",
    )

    assert result.exit_code == ExitCode.OK


def test_status_code_conformance_failure(cli, status_code_failure):
    args: Iterable[str] = [
        status_code_failure,
        "--base-url=" + SERVER_URL,
        "--hypothesis-phases=generate",
    ]
    result = cli.run(*args)

    assert result.exit_code == ExitCode.TESTS_FAILED


def test_hooks_loaded(cli, server_definition):
    args: Iterable[str] = [
        server_definition,
        "--base-url=" + SERVER_URL,
        "--hypothesis-phases=generate",
    ]
    result = cli.run(*args)

    assert result.exit_code == ExitCode.OK
    # Makes sure handbook rule is loaded and included in output
    assert any(
        [
            "no_422" in line
            for line in result.stdout.split("Performed checks")[1].split("\n")
        ]
    )

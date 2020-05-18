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
    result = cli.run(
        status_code_failure, "--base-url=" + SERVER_URL, "--hypothesis-phases=generate",
    )

    assert result.exit_code == ExitCode.TESTS_FAILED


def test_hooks_loaded(cli, server_definition):
    result = cli.run(
        server_definition, "--base-url=" + SERVER_URL, "--hypothesis-phases=generate",
    )

    assert result.exit_code == ExitCode.OK
    # Makes sure handbook rule is loaded and included in output
    assert any(
        [
            "no_422" in line
            for line in result.stdout.split("Performed checks")[1].split("\n")
        ]
    )


def test_init_with_all_args(cli, tmp_cwd):
    """Tests init command. Creates default config in temp directory."""
    result = cli.init("--json", "--overwrite")

    assert result.exit_code == ExitCode.OK


def test_commands_help(cli):
    result = cli.main("--help")

    lines = result.stdout.split("\n")
    assert any(["Run a suite of tests." in line for line in lines])


def test_commands_help_1(cli):
    result = cli.main("--help")

    lines = result.stdout.split("\n")
    assert any(["Create a default config file." in line for line in lines])


def test_replay(tmp_cwd, cli, server_definition):
    """Tests cassettes and replay feature with basic args."""

    # runs test suite and creates cassette in tmp_cwd
    log_file = "log.yaml"
    result = cli.run(
        server_definition,
        "--base-url=" + SERVER_URL,
        "--hypothesis-phases=explicit,generate",
        "--store-request-log=" + log_file,
    )
    assert result.exit_code == ExitCode.OK

    replay_result = cli.replay(log_file)

    assert replay_result.exit_code == ExitCode.OK
    lines = replay_result.stdout.split("\n")
    assert any(["New status code" in line for line in lines])


def test_replay_with_args(tmp_cwd, cli, server_definition):
    """Tests cassettes and replay feature with basic args."""

    # runs test suite and creates cassette in tmp_cwd
    log_file = "log.yaml"
    result = cli.run(
        server_definition,
        "--base-url=" + SERVER_URL,
        "--hypothesis-phases=explicit,generate",
        "--store-request-log=" + log_file,
    )
    assert result.exit_code == ExitCode.OK

    replay_result = cli.replay(log_file, "--id=1")
    assert replay_result.exit_code == ExitCode.OK
    lines = replay_result.stdout.split("\n")
    assert any(["New status code" in line for line in lines])


def test_replay_with_args_1(tmp_cwd, cli, server_definition):
    """Tests cassettes and replay feature with basic args."""

    # runs test suite and creates cassette in tmp_cwd
    log_file = "log.yaml"
    result = cli.run(
        server_definition,
        "--base-url=" + SERVER_URL,
        "--hypothesis-phases=explicit,generate",
        "--store-request-log=" + log_file,
    )
    assert result.exit_code == ExitCode.OK

    replay_result = cli.replay(log_file, "--uri=/allof")
    assert replay_result.exit_code == ExitCode.OK
    lines = replay_result.stdout.split("\n")
    assert any(["New status code" in line for line in lines])


def test_replay_with_args_2(tmp_cwd, cli, server_definition):
    """Tests cassettes and replay feature with basic args."""

    # runs test suite and creates cassette in tmp_cwd
    log_file = "log.yaml"
    result = cli.run(
        server_definition,
        "--base-url=" + SERVER_URL,
        "--hypothesis-phases=explicit,generate",
        "--store-request-log=" + log_file,
    )
    assert result.exit_code == ExitCode.OK

    replay_result = cli.replay(log_file, "--status=SUCCESS", "--method=GET")
    assert replay_result.exit_code == ExitCode.OK
    lines = replay_result.stdout.split("\n")
    assert any(["New status code" in line for line in lines])

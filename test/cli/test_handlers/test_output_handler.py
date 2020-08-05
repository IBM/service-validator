import pytest
import click

from schemathesis.cli.context import ExecutionContext
from schemathesis.runner.events import AfterExecution, Finished, InternalError
from schemathesis.runner.serialization import (
    SerializedCase,
    SerializedError,
    SerializedTestResult,
)

from src.ibm_service_validator.cli.handlers.output_handler import (
    OutputHandler,
    display_exceptions,
)


@pytest.fixture()
def mock_execution_context():
    return ExecutionContext()


@pytest.fixture()
def after_execution():
    return AfterExecution()


@pytest.fixture()
def finished():
    return Finished(
        passed_count=0,
        failed_count=0,
        errored_count=0,
        has_failures=False,
        has_errors=False,
        has_logs=False,
        is_empty=False,
        total={},
        running_time=1.0,
    )


@pytest.fixture()
def internal_error():
    return InternalError(message="Internal error occurred.", exception_type="exception")


@pytest.fixture()
def output_handler():
    return OutputHandler(frozenset(), False)


@pytest.fixture()
def serialized_case():
    return SerializedCase(requests_code="12345")


@pytest.fixture()
def serialized_error(serialized_case):
    return SerializedError(
        exception="Exception",
        exception_with_traceback="In file: /mock/file\nOn line: 100\nRaised Exception.",
        example=serialized_case,
    )


@pytest.fixture()
def serialized_test_result():
    return SerializedTestResult(
        method="GET",
        path="mock/path",
        has_failures=False,
        has_errors=False,
        has_logs=False,
        is_errored=False,
        seed=0,
        checks=[],
        logs=[],
        errors=[],
        interactions=[],
    )


def test_internal_error_no_exception(
    capsys, output_handler, mock_execution_context, internal_error
):
    with pytest.raises(click.Abort):
        output_handler.handle_event(mock_execution_context, internal_error)
        # internal_error.exception == None
        captured = capsys.readouterr()
        assert captured.out == "Internal error occurred."


def test_non_jsonschema_internal_error(
    capsys, output_handler, mock_execution_context, internal_error
):
    internal_error.exception = "Exception"
    internal_error.exception_type = "Exception"
    with pytest.raises(click.Abort):
        output_handler.handle_event(mock_execution_context, internal_error)
        # internal_error.exception == None
        captured = capsys.readouterr()
        assert captured.out
        assert "--show-exception-tracebacks" in captured.out
        assert "--validate-schema=False" not in captured.out


def test_finished(
    capsys, output_handler, mock_execution_context, finished, serialized_test_result
):
    mock_execution_context.results = [serialized_test_result]
    mock_execution_context.show_errors_tracebacks = True
    finished.has_errors = True
    display_exceptions(mock_execution_context, finished)
    captured = capsys.readouterr()
    assert "== EXCEPTIONS ==" in captured.out
    assert "--show-exception-tracebacks" not in captured.out


def test_finished_1(
    capsys,
    output_handler,
    mock_execution_context,
    finished,
    serialized_error,
    serialized_test_result,
):
    serialized_test_result.errors = [serialized_error]
    serialized_test_result.has_errors = True
    mock_execution_context.results = [serialized_test_result]
    mock_execution_context.show_errors_tracebacks = True
    finished.has_errors = True
    display_exceptions(mock_execution_context, finished)
    captured = capsys.readouterr()
    # Should get the error message with traceback
    assert "In file:" in captured.out
    assert "On line:" in captured.out

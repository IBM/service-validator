from typing import Dict, FrozenSet, List, Optional, Set, Tuple, Union, cast

import click
from schemathesis.cli.context import ExecutionContext
from schemathesis.cli.handlers import EventHandler
from schemathesis.cli.output import default
from schemathesis.models import Status
from schemathesis.runner import events
from schemathesis.runner.serialization import (
    SerializedCase,
    SerializedCheck,
    SerializedTestResult,
)


def handle_after_execution(
    context: ExecutionContext, event: events.AfterExecution, warnings: FrozenSet[str]
) -> None:
    """Display the execution result + current progress at the same line with the method / endpoint names."""
    context.endpoints_processed += 1
    context.results.append(event.result)
    display_execution_result(context, event, warnings)
    default.display_percentage(context, event)


def handle_finished(
    context: ExecutionContext, event: events.Finished, warnings: FrozenSet[str]
) -> None:
    """Show the outcome of the whole testing session."""
    click.echo()
    default.display_hypothesis_output(context.hypothesis_output)
    default.display_errors(context, event)
    display_warnings(context, event, warnings)
    display_failures(context, event, warnings)
    default.display_application_logs(context, event)
    display_statistic(context, event, warnings)
    click.echo()
    display_summary(event, warnings)


def display_execution_result(
    context: ExecutionContext, event: events.AfterExecution, warnings: FrozenSet[str]
) -> None:
    """Display an appropriate symbol for the given event's execution result.

    Note: The ordering of the conditional blocks affects behavior.
    """
    symbol: str
    color: str
    if event.status == Status.success:
        symbol, color = ".", "green"
    elif warn_or_success(event.result, warnings):
        symbol, color = "W", "yellow"
    elif event.status == Status.failure:
        symbol, color = "F", "red"
    else:
        symbol, color = "E", "red"
    context.current_line_length += len(symbol)
    click.secho(symbol, nl=False, fg=color)


def display_failures(
    context: ExecutionContext, event: events.Finished, warnings: FrozenSet[str]
) -> None:
    """Display all failures in the test run."""
    if not event.has_failures:
        return
    failures = [
        result
        for result in context.results
        if not result.is_errored
        and result.has_failures
        and not warn_or_success(result, warnings)
    ]
    if failures:
        default.display_section_name("FAILURES")
        for result in failures:
            display_single_test(
                get_unique_failures(result.checks, warnings), result, "red"
            )


def display_warnings(
    context: ExecutionContext, event: events.Finished, warnings: FrozenSet[str]
) -> None:
    """Display all warnings in the test run."""
    if not event.has_failures:
        return
    warning_results = [
        result
        for result in context.results
        if not result.is_errored and contains_warning(result, warnings)
    ]
    if warning_results:
        default.display_section_name("WARNINGS")
        for result in warning_results:
            display_single_test(
                get_unique_warnings(result.checks, warnings), result, "yellow"
            )


def display_single_test(
    unique_checks: List[SerializedCheck], result: SerializedTestResult, color: str
) -> None:
    """Display a failure for a single method / endpoint."""
    default.display_subsection(result, color)
    display_all_checks(unique_checks, color, result.seed)


def display_all_checks(checks: List[SerializedCheck], color: str, seed: int) -> None:
    for idx, check in enumerate(checks, 1):
        message: Optional[str]
        if check.message:
            message = f"{idx}. {check.message}"
        else:
            message = None
        example = cast(SerializedCase, check.example)
        display_example(example, check.name, message, seed, color)
        # Display every time except the last check
        if idx != len(checks):
            click.echo("\n")


def display_example(
    case: SerializedCase,
    check_name: Optional[str] = None,
    message: Optional[str] = None,
    seed: Optional[int] = None,
    color: Optional[str] = "red",
) -> None:
    if message is not None:
        click.secho(message, fg=color)
        click.echo()
    output = {
        make_verbose_name(attribute): getattr(case, attribute)
        for attribute in (
            "path_parameters",
            "headers",
            "cookies",
            "query",
            "body",
            "form_data",
        )
    }
    max_length = max(map(len, output))
    template = f"{{:<{max_length}}} : {{}}"
    if check_name is not None:
        click.secho(template.format("Check", check_name), fg=color)
    for key, value in output.items():
        if (key == "Body" and value is not None) or value not in (None, {}):
            click.secho(template.format(key, value), fg=color)
    click.echo()
    click.secho(
        f"Run this Python code to reproduce this failure: \n\n    {case.requests_code}",
        fg=color,
    )
    if seed is not None:
        click.secho(
            f"\nOr add this option to your command line parameters: --hypothesis-seed={seed}",
            fg=color,
        )


def display_statistic(
    context: ExecutionContext, event: events.Finished, warnings: FrozenSet[str]
) -> None:
    """Format and print statistic collected by :obj:`models.TestResult`."""
    default.display_section_name("SUMMARY")
    click.echo()
    total = event.total
    if event.is_empty or not total:
        click.secho("No checks were performed.", bold=True)

    if total:
        display_checks_statistics(total, warnings)

    if context.cassette_file_name or context.junit_xml_file:
        click.echo()

    if context.cassette_file_name:
        category = click.style("Network log", bold=True)
        click.secho(f"{category}: {context.cassette_file_name}")

    if context.junit_xml_file:
        category = click.style("JUnit XML file", bold=True)
        click.secho(f"{category}: {context.junit_xml_file}")


def display_checks_statistics(
    total: Dict[str, Dict[Union[str, Status], int]], warnings: FrozenSet[str]
) -> None:
    padding = 20
    col1_len = max(map(len, total.keys())) + padding
    col2_len = (
        len(str(max(total.values(), key=lambda v: v["total"])["total"])) * 2 + padding
    )
    col3_len = padding
    template = f"    {{:{col1_len}}}{{:{col2_len}}}{{:{col3_len}}}"

    warning_checks = [
        (check_name, results)
        for check_name, results in total.items()
        if check_name in warnings
    ]
    if warning_checks:
        click.secho("Warning checks:", bold=True)
        for check_name, results in warning_checks:
            display_warning_checks(check_name, results, template)
        click.echo()

    regular_checks = [
        (check_name, results)
        for check_name, results in total.items()
        if check_name not in warnings
    ]
    if regular_checks:
        click.secho("Performed checks:", bold=True)
        for check_name, results in regular_checks:
            display_check_result(check_name, results, template)


def display_warning_checks(
    check_name: str, results: Dict[Union[str, Status], int], template: str
) -> None:
    """Display the summary warning checks."""

    # Check contains failure, but we know check is configured to warning. Hence, treat failure as warning.
    if Status.failure in results:
        verdict = "WARNING"
        color = "yellow"
    else:
        verdict = "PASSED"
        color = "green"
    success = results.get(Status.success, 0)
    total = results.get("total", 0)
    click.echo(
        template.format(
            check_name,
            f"{success} / {total} passed",
            click.style(verdict, fg=color, bold=True),
        )
    )


def display_check_result(
    check_name: str, results: Dict[Union[str, Status], int], template: str
) -> None:
    """Show the summary for a single check."""
    if Status.failure in results:
        verdict = "FAILED"
        color = "red"
    else:
        verdict = "PASSED"
        color = "green"
    success = results.get(Status.success, 0)
    total = results.get("total", 0)
    click.echo(
        template.format(
            check_name,
            f"{success} / {total} passed",
            click.style(verdict, fg=color, bold=True),
        )
    )


def display_summary(event: events.Finished, warnings: FrozenSet[str]) -> None:
    message, color, status_code = get_summary_output(event, warnings)
    default.display_section_name(message, fg=color)
    raise click.exceptions.Exit(status_code)


def get_summary_counts(
    event: events.Finished, warnings: FrozenSet[str]
) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    counts["passed"] = sum(
        results[Status.success]
        for check_name, results in event.total.items()
        if Status.success in results
    )
    counts["warned"] = sum(
        results[Status.failure]
        for check_name, results in event.total.items()
        if check_name in warnings
        if Status.failure in results
    )
    counts["failed"] = (
        sum(
            results[Status.failure]
            for check_name, results in event.total.items()
            if Status.failure in results
        )
        - counts["warned"]
    )
    counts["errored"] = sum(
        results[Status.error]
        for check_name, results in event.total.items()
        if Status.error in results
    )
    return counts


def get_summary_output(
    event: events.Finished, warnings: FrozenSet[str]
) -> Tuple[str, str, int]:
    counts = get_summary_counts(event, warnings)
    stats = [f"{num} {key}" for key, num in counts.items() if num > 0]
    if not stats:
        message = "No checks performed."
        color = "yellow"
        status_code = 0
    else:
        message = f'{", ".join(stats)} in {event.running_time:.2f}s'
        if counts["failed"] > 0 or counts["errored"] > 0:
            color = "red"
            status_code = 1
        else:
            color = "green"
            status_code = 0
    return message, color, status_code


def contains_warning(result: SerializedTestResult, warnings: FrozenSet[str]) -> bool:
    """Returns true if any check is result is a warning."""
    return any(_warn(check, warnings) for check in result.checks)


def get_unique_failures(
    checks: List[SerializedCheck], warnings: FrozenSet[str]
) -> List[SerializedCheck]:
    """Return only unique checks that should be displayed in the output."""
    seen: Set[Tuple[str, Optional[str]]] = set()
    unique_checks = []
    for check in reversed(checks):
        # There are also could be checks that didn't fail
        if (
            check.example is not None
            and check.value == Status.failure
            and not _warn(check, warnings)
            and (check.name, check.message) not in seen
        ):
            unique_checks.append(check)
            seen.add((check.name, check.message))
    return unique_checks


def get_unique_warnings(
    checks: List[SerializedCheck], warnings: FrozenSet[str]
) -> List[SerializedCheck]:
    """Return only unique checks that should be displayed in the output."""
    seen: Set[Tuple[str, Optional[str]]] = set()
    unique_checks = []
    for check in reversed(checks):
        # There are also could be checks that didn't fail
        if (
            check.example is not None
            and _warn(check, warnings)
            and (check.name, check.message) not in seen
        ):
            unique_checks.append(check)
            seen.add((check.name, check.message))
    return unique_checks


def make_verbose_name(attribute: str) -> str:
    return attribute.capitalize().replace("_", " ")


def warn_or_success(result: SerializedTestResult, warnings: FrozenSet[str]) -> bool:
    """All checks must be failures marked as warnings or successes.

    This function will return True if all checks are successes.
    """
    return all(
        check.value == Status.success or _warn(check, warnings) for check in result.checks
    )


def _warn(check: SerializedCheck, warnings: FrozenSet[str]) -> bool:
    return check.name in warnings and check.value == Status.failure


class OutputHandler(EventHandler):
    def __init__(self, warn: FrozenSet[str]) -> None:
        self.warn: FrozenSet[str] = warn

    def handle_event(
        self, context: ExecutionContext, event: events.ExecutionEvent
    ) -> None:
        """Choose and execute a proper handler for the given event."""
        if isinstance(event, events.Initialized):
            default.handle_initialized(context, event)
        if isinstance(event, events.BeforeExecution):
            default.handle_before_execution(context, event)
        if isinstance(event, events.AfterExecution):
            context.hypothesis_output.extend(event.hypothesis_output)
            handle_after_execution(context, event, self.warn)
        if isinstance(event, events.Finished):
            handle_finished(context, event, self.warn)
        if isinstance(event, events.Interrupted):
            default.handle_interrupted(context, event)
        if isinstance(event, events.InternalError):
            default.handle_internal_error(context, event)

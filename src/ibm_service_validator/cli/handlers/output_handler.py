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
    context: ExecutionContext,
    event: events.Finished,
    warnings: FrozenSet[str],
    statistics: bool = False,
) -> None:
    """Show the outcome of the whole testing session."""
    click.echo()
    default.display_hypothesis_output(context.hypothesis_output)
    display_exceptions(context, event)
    display_warnings(context, event, warnings)
    display_errors(context, event, warnings)
    default.display_application_logs(context, event)
    display_totals(context, event, warnings)
    click.echo()
    display_summary(event, warnings, statistics)


def handle_internal_error(context: ExecutionContext, event: events.InternalError) -> None:
    display_internal_error(context, event)
    raise click.Abort


def display_internal_error(
    context: ExecutionContext, event: events.InternalError
) -> None:
    click.secho(event.message, fg="red")
    if event.exception:
        if context.show_errors_tracebacks:
            message = f"Error: {event.exception_with_traceback}\n"
        else:
            message = (
                f"Error: {event.exception}\n"
                f"Add this option to your command line parameters to see full tracebacks: --show-exception-tracebacks"
            )
        if event.exception_type == "jsonschema.exceptions.ValidationError":
            message += (
                "\n\nYou can disable input schema validation with --validate-schema=false "
                "command-line option.\nIn this case, we cannot guarantee proper"
                " behavior during the test run."
            )
        click.secho(
            message,
            fg="red",
        )


def display_exceptions(context: ExecutionContext, event: events.Finished) -> None:
    """Display all exceptions in the test run."""
    if not event.has_errors:
        return

    default.display_section_name("EXCEPTIONS")
    for result in context.results:
        if result.has_errors:
            display_single_exception(context, result)
    if not context.show_errors_tracebacks:
        click.secho(
            "Add this option to your command line parameters to see full tracebacks: --show-exception-tracebacks",
            fg="magenta",
        )


def display_single_exception(
    context: ExecutionContext, result: SerializedTestResult
) -> None:
    default.display_subsection(result, "magenta")
    for error in result.errors:
        if context.show_errors_tracebacks:
            message = error.exception_with_traceback
        else:
            message = error.exception
        click.secho(message, fg="magenta")
        if error.example is not None:
            display_example(error.example, "magenta", seed=result.seed)


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
    elif event.result.checks and warn_or_success(event.result, warnings):
        symbol, color = "W", "yellow"
    elif event.status == Status.failure:
        symbol, color = "E", "red"
    else:
        # an exception occurred
        symbol, color = "E", "magenta"
    context.current_line_length += len(symbol)
    click.secho(symbol, nl=False, fg=color)


def display_errors(
    context: ExecutionContext, event: events.Finished, warnings: FrozenSet[str]
) -> None:
    """Display all errors in the test run."""
    if not event.has_failures and not event.has_errors:
        return
    errors = [
        result
        for result in context.results
        if result.has_failures and not warn_or_success(result, warnings)
    ]
    if errors:
        default.display_section_name("ERRORS")
        for result in errors:
            display_single_test(get_unique_errors(result.checks, warnings), result, "red")


def display_warnings(
    context: ExecutionContext, event: events.Finished, warnings: FrozenSet[str]
) -> None:
    """Display all warnings in the test run."""
    if not event.has_failures:
        return
    warning_results = [
        result for result in context.results if contains_warning(result, warnings)
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
    """Display an error or warning for a single method / endpoint."""
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
        display_example(example, color, check.name, message, seed)
        # Display every time except the last check
        if idx != len(checks):
            click.echo("\n")


def display_example(
    case: SerializedCase,
    color: str,
    check_name: Optional[str] = None,
    message: Optional[str] = None,
    seed: Optional[int] = None,
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


def display_totals(
    context: ExecutionContext, event: events.Finished, warnings: FrozenSet[str]
) -> None:
    """Format and print statistic collected by :obj:`models.TestResult`."""
    default.display_section_name("SUMMARY")
    click.echo()
    total = event.total
    if event.is_empty or not total:
        click.secho("No checks were performed.", bold=True)

    if total:
        display_checks_totals(total, warnings)

    if context.cassette_file_name or context.junit_xml_file:
        click.echo()

    if context.cassette_file_name:
        category = click.style("Network log", bold=True)
        click.secho(f"{category}: {context.cassette_file_name}")

    if context.junit_xml_file:
        category = click.style("JUnit XML file", bold=True)
        click.secho(f"{category}: {context.junit_xml_file}")


def display_checks_totals(
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
            display_check_result(check_name, results, template, warnings)
        click.echo()

    regular_checks = [
        (check_name, results)
        for check_name, results in total.items()
        if check_name not in warnings
    ]
    if regular_checks:
        click.secho("Performed checks:", bold=True)
        for check_name, results in regular_checks:
            display_check_result(check_name, results, template, warnings)


def display_check_result(
    check_name: str,
    results: Dict[Union[str, Status], int],
    template: str,
    warnings: FrozenSet[str],
) -> None:
    """Show the summary for a single check."""
    if check_name in warnings and Status.failure in results:
        verdict = "WARNING"
        color = "yellow"
    elif Status.failure in results:
        verdict = "ERROR"
        color = "red"
    else:
        verdict = "SUCCESS"
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


def display_summary(
    event: events.Finished, warnings: FrozenSet[str], statistics: bool = False
) -> None:
    counts = get_summary_counts(event, warnings)
    message, color, status_code = get_summary_output(counts, event, warnings)
    if statistics:
        display_statistical_summary(counts, event, warnings, color)
    default.display_section_name(message, fg=color)
    raise click.exceptions.Exit(status_code)


def display_statistical_summary(
    counts: Dict[str, int],
    event: events.Finished,
    warnings: FrozenSet[str],
    color: str = "cyan",
) -> None:
    click.echo()
    default.display_section_name("STATISTICS")
    click.echo()
    error_count, warning_count = (
        counts["errors"],
        counts["warnings"],
    )
    click.secho(f"Total warnings: {warning_count}", fg=color)
    click.secho(f"Total errors: {error_count}", fg=color)
    for severity, check_stats in get_results_by_severity(event, warnings).items():
        if check_stats:
            click.echo()
            click.secho(severity, fg=color, bold=True, underline=True)
            # prints the check name and counts in descending order by count
            for check_name, count in sorted(
                check_stats.items(), key=lambda x: x[1], reverse=True
            ):
                click.secho(f"{check_name} : {count}", fg=color)
    click.echo()


def get_results_by_severity(
    event: events.Finished, warnings: FrozenSet[str]
) -> Dict[str, Dict[str, int]]:
    results: Dict[str, Dict[str, int]] = {"warnings": {}, "errors": {}}
    for check_name, result in event.total.items():
        if check_name in warnings and Status.failure in result:
            results["warnings"][check_name] = result[Status.failure]
        elif check_name not in warnings and Status.failure in result:
            results["errors"][check_name] = result[Status.failure]
    return results


def get_summary_counts(
    event: events.Finished, warnings: FrozenSet[str]
) -> Dict[str, int]:
    return {
        "successes": sum(
            results[Status.success]
            for check_name, results in event.total.items()
            if Status.success in results
        ),
        "warnings": sum(
            results[Status.failure]
            for check_name, results in event.total.items()
            if check_name in warnings and Status.failure in results
        ),
        "errors": sum(
            results[Status.failure]
            for check_name, results in event.total.items()
            if check_name not in warnings and Status.failure in results
        ),
        "exceptions": event.errored_count,
    }


def get_summary_output(
    counts: Dict[str, int], event: events.Finished, warnings: FrozenSet[str]
) -> Tuple[str, str, int]:
    counts_as_messages = [f"{num} {key}" for key, num in counts.items() if num > 0]
    if not counts_as_messages:
        message = "No checks performed."
        color = "yellow"
        status_code = 0
    else:
        message = f'{", ".join(counts_as_messages)} in {event.running_time:.2f}s'
        if counts["errors"] > 0 or counts["exceptions"] > 0:
            color = "red"
            status_code = 1
        else:
            color = "green"
            status_code = 0
    return message, color, status_code


def contains_warning(result: SerializedTestResult, warnings: FrozenSet[str]) -> bool:
    """Returns true if any check is result is a warning."""
    return any(_warn(check, warnings) for check in result.checks)


def get_unique_errors(
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
    def __init__(self, warn: FrozenSet[str], statistics: bool) -> None:
        self.warn: FrozenSet[str] = warn
        self.statistics = statistics

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
            handle_finished(context, event, self.warn, self.statistics)
        if isinstance(event, events.Interrupted):
            default.handle_interrupted(context, event)
        if isinstance(event, events.InternalError):
            handle_internal_error(context, event)

from typing import Dict, Iterable, List, Optional, Tuple, Union

import click
import hypothesis

from schemathesis.cli import run
from schemathesis.cli import schemathesis as register_hooks
from schemathesis.cli.options import CSVOption, OptionalInt, NotSet
from schemathesis.cli import callbacks

from schemathesis.types import Filter
from schemathesis import checks as checks_module

ALL_CHECKS_NAMES = tuple(check.__name__ for check in checks_module.ALL_CHECKS)
CHECKS_TYPE = click.Choice((*ALL_CHECKS_NAMES, "all"))


@click.command()
@click.argument("schema", type=str, callback=callbacks.validate_schema)
@click.option(
    "--auth",
    "-a",
    type=str,
    callback=callbacks.validate_auth,
    help="Server user and password. Example: USER:PASSWORD",
)
@click.option(
    "--auth-type",
    "-A",
    type=click.Choice(["basic", "digest"], case_sensitive=False),
    default="basic",
    help="The authentication mechanism to be used. Defaults to 'basic'.",
)
@click.option(
    "--base-url",
    "-b",
    callback=callbacks.validate_base_url,
    help="The base-url of the API.",
)
@click.option(
    "--checks",
    "-c",
    default=["all"],
    type=CHECKS_TYPE,
    multiple=True,
    help="List of checks to run.",
)
@click.option(
    "--header",
    "-H",
    "headers",
    multiple=True,
    type=str,
    callback=callbacks.validate_headers,
    help="Custom header that will be used in all requests to the server. Example: Authorization: Bearer 123",
)
@click.option(
    "--endpoint",
    "-E",
    "endpoints",
    type=str,
    multiple=True,
    callback=callbacks.validate_regex,
    help="Filter schemathesis test by endpoint pattern.",
)
@click.option(
    "--exitfirst",
    "-x",
    "exit_first",
    is_flag=True,
    default=False,
    help="Exit instantly on first error or failed test.",
)
@click.option(
    "--hypothesis-deadline",
    # max value to avoid overflow. It is maximum amount of days in milliseconds
    type=OptionalInt(1, 999999999 * 24 * 3600 * 1000),
    help="Duration in milliseconds that each individual example with a test is not allowed to exceed.",
)
@click.option(
    "--hypothesis-derandomize",
    help="Use Hypothesis's deterministic mode.",
    is_flag=True,
    default=None,
)
@click.option(
    "--hypothesis-max-examples",
    type=click.IntRange(1),
    help="Maximum number of generated examples per each method/endpoint combination.",
)
@click.option(
    "--hypothesis-phases",
    default=[hypothesis.Phase.explicit],
    type=CSVOption(hypothesis.Phase),
    help="Control which phases should be run.",
)
@click.option(
    "--hypothesis-seed", type=int, help="Set a seed to use for all Hypothesis tests."
)
@click.option(
    "--hypothesis-verbosity",
    type=click.Choice([item.name for item in hypothesis.Verbosity]),
    callback=callbacks.convert_verbosity,
    help="Verbosity level of Hypothesis messages.",
)
@click.option(
    "--method",
    "-M",
    "methods",
    type=str,
    multiple=True,
    callback=callbacks.validate_regex,
    help="Filter schemathesis test by HTTP method.",
)
@click.option(
    "--request-timeout",
    type=click.IntRange(1),
    help="Timeout in milliseconds for network requests during the test run.",
)
@click.option(
    "--show-errors-tracebacks",
    is_flag=True,
    default=False,
    help="Show full tracebacks for internal errors.",
)
@click.option(
    "--tag",
    "-T",
    "tags",
    type=str,
    multiple=True,
    callback=callbacks.validate_regex,
    help="Filter schemathesis test by schema tag pattern.",
)
@click.pass_context
def run_schemathesis(  # pylint: disable=too-many-arguments
    context: click.Context,
    schema: str,
    auth: Optional[Tuple[str, str]],
    auth_type: str,
    base_url: Optional[str],
    checks: Iterable[str],
    headers: Dict[str, str],
    hypothesis_phases: Optional[List[hypothesis.Phase]],
    endpoints: Optional[Filter] = None,
    exit_first: bool = False,
    hypothesis_deadline: Optional[Union[int, NotSet]] = None,
    hypothesis_derandomize: Optional[bool] = None,
    hypothesis_max_examples: Optional[int] = None,
    hypothesis_seed: Optional[int] = None,
    hypothesis_verbosity: Optional[hypothesis.Verbosity] = None,
    methods: Optional[Filter] = None,
    request_timeout: Optional[int] = None,
    show_errors_tracebacks: bool = False,
    tags: Optional[Filter] = None,
) -> None:
    # pylint: disable=too-many-locals

    # Register hooks
    context.invoke(register_hooks, pre_run="src.validation_hooks.handbook_rules")

    # Invoke Schemathesis
    context.forward(run)


if __name__ == "__main__":
    run_schemathesis()

from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

import click
import hypothesis

from schemathesis.cli.options import CSVOption, OptionalInt, NotSet
from schemathesis.cli import callbacks, execute
from schemathesis.cli import replay as _replay
from schemathesis import loaders, runner

from schemathesis.types import Filter
from schemathesis import checks as checks_module
from schemathesis.models import Case
from requests.models import Response

from ibm_service_validator.validation_hooks import HANDBOOK_RULES
from .process_config import create_default_config, process_config_file

ALL_CHECKS: tuple = checks_module.ALL_CHECKS + HANDBOOK_RULES
DEFAULT_WORKERS: int = 1


@click.group()
def ibm_service_validator() -> None:
    pass


@ibm_service_validator.command(short_help="Run a suite of tests.")
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
    "--header",
    "-H",
    "headers",
    multiple=True,
    type=str,
    callback=callbacks.validate_headers,
    help="Custom header will be used in all requests to server. Ex: Authorization: Bearer 123",
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
    # max value to avoid overflow. It is maximum amount of days in milliseconds.
    type=OptionalInt(1, 999999999 * 24 * 3600 * 1000),
    help="Duration in milliseconds each individual example is not allowed to exceed.",
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
    default="explicit",
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
    "--store-request-log",
    help="Store requests and responses into a file.",
    type=click.File("w"),
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
def run(  # pylint: disable=too-many-arguments
    schema: str,
    auth: Optional[Tuple[str, str]],
    auth_type: str,
    base_url: Optional[str],
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
    store_request_log: Optional[click.utils.LazyFile] = None,
    tags: Optional[Filter] = None,
) -> None:
    # pylint: disable=too-many-locals

    checks_off = process_config_file()

    selected_checks = get_selected_checks(checks_off)

    # Invoke Schemathesis
    prepared_runner = runner.prepare(
        schema,
        app=None,
        auth=auth,
        auth_type=auth_type,
        base_url=base_url,
        checks=selected_checks,
        endpoint=endpoints,
        exit_first=exit_first,
        headers=headers,
        loader=loaders.from_path,
        method=methods,
        request_timeout=request_timeout,
        seed=hypothesis_seed,
        store_interactions=store_request_log is not None,
        tag=tags,
        validate_schema=True,
        workers_num=DEFAULT_WORKERS,
        hypothesis_deadline=hypothesis_deadline,
        hypothesis_derandomize=hypothesis_derandomize,
        hypothesis_max_examples=hypothesis_max_examples,
        hypothesis_phases=hypothesis_phases,
        hypothesis_report_multiple_bugs=False,
        hypothesis_suppress_health_check=None,
        hypothesis_verbosity=hypothesis_verbosity,
    )
    execute(
        prepared_runner, DEFAULT_WORKERS, show_errors_tracebacks, store_request_log, None
    )


def get_selected_checks(
    checks_off: Iterable[str],
) -> Iterable[Callable[[Response, Case], None]]:
    return tuple(check for check in ALL_CHECKS if check.__name__ not in checks_off)


@ibm_service_validator.command(short_help="Create a default config file.")
@click.option(
    "--overwrite",
    "-o",
    "overwrite",
    is_flag=True,
    default=False,
    help="Overwrite an existing config file with the default config.",
)
@click.option(
    "--json",
    "-j",
    "write_json",
    is_flag=True,
    default=False,
    help="Overwrite an existing config file with the default config.",
)
def init(write_json: bool, overwrite: bool) -> None:
    create_default_config(write_json, overwrite)


@ibm_service_validator.command(short_help="Replay requests from a saved request log.")
@click.argument("cassette_path", type=click.Path(exists=True))
@click.option("--id", "id_", help="ID of request to replay.", type=str)
@click.option(
    "--status", help="Status (ERROR, FAILURE, SUCCESS) of requests to replay.", type=str
)
@click.option(
    "--uri", help="A regexp that filters requests by their request URI.", type=str
)
@click.option(
    "--method", help="A regexp that filters requests by their request method.", type=str,
)
@click.pass_context
def replay(  # pylint: disable=too-many-arguments
    context: click.Context,
    cassette_path: str,
    id_: Optional[str],
    status: Optional[str],
    uri: Optional[str],
    method: Optional[str],
) -> None:
    # pylint: disable=too-many-locals
    context.forward(_replay)

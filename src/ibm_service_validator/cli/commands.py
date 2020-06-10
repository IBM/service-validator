from typing import Callable, Dict, FrozenSet, Iterable, List, Optional, Tuple, Union
import os

import click
import hypothesis
from ibm_cloud_sdk_core.authenticators.iam_authenticator import IAMAuthenticator

from requests.models import Response
from schemathesis.cli.context import ExecutionContext
from schemathesis.cli.handlers import EventHandler
from schemathesis.cli.output.default import DefaultOutputStyleHandler
from schemathesis.cli.output.short import ShortOutputStyleHandler
from schemathesis.cli.options import CSVOption, OptionalInt, NotSet
from schemathesis.cli import callbacks, execute
from schemathesis.cli import replay as _replay
from schemathesis import loaders, runner

from schemathesis.hooks import GLOBAL_HOOK_DISPATCHER, HookContext
from schemathesis.types import Filter
from schemathesis import checks as checks_module
from schemathesis.models import Case

from ibm_service_validator.cli.handlers.output_handler import OutputHandler
from ibm_service_validator.handbook_rules import ADD_CASE_HOOKS, HANDBOOK_RULES
from ibm_service_validator.cli.process_config import (
    create_default_config,
    process_config,
)

ALL_CHECKS: tuple = checks_module.ALL_CHECKS + HANDBOOK_RULES
API_KEY = "IBM_CLOUD_SERVICE_VALIDATOR_API_KEY"
IAM_ENDPOINT = "IBM_CLOUD_SERVICE_VALIDATOR_IAM_ENDPOINT"
DEFAULT_WORKERS: int = 1


@click.group()
@click.option(
    "--set-api-key", "api_key", type=str, help="Set API key as an environment variable."
)
@click.option(
    "--set-iam-endpoint",
    "iam_endpoint",
    type=str,
    help="Set the IAM endpoint as an environment variable.",
)
def ibm_service_validator(api_key: str = str(), iam_endpoint: str = str()) -> None:
    set_environment_variable(api_key, API_KEY)
    set_environment_variable(iam_endpoint, IAM_ENDPOINT)


def set_environment_variable(val: str, env_var_name: str) -> None:
    if val:
        os.environ[env_var_name] = val


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
    "--checks",
    "-c",
    type=str,
    default="",
    callback=lambda _, __, s: [c.strip() for c in s.split(",") if c.strip()],
    help="Comma-separated list of checks to run.",
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
    "--no-additional-cases",
    is_flag=True,
    default=False,
    help="Additional requests that target specific API behavior will not be sent.",
)
@click.option(
    "--request-timeout",
    type=click.IntRange(1),
    help="Timeout in milliseconds for network requests during the test run.",
)
@click.option(
    "--show-exception-tracebacks",
    is_flag=True,
    default=False,
    help="Show full tracebacks for internal exceptions.",
)
@click.option(
    "--statistics",
    "-s",
    is_flag=True,
    default=False,
    help="Show statistical summary of errors.",
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
@click.option(
    "--with-bearer", "-B", is_flag=True, help="Flag to send bearer token with requests."
)
def run(  # pylint: disable=too-many-arguments
    schema: str,
    auth: Optional[Tuple[str, str]],
    auth_type: str,
    base_url: Optional[str],
    checks: Optional[List[str]],
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
    no_additional_cases: bool = False,
    request_timeout: Optional[int] = None,
    show_exception_tracebacks: bool = False,
    statistics: bool = False,
    store_request_log: Optional[click.utils.LazyFile] = None,
    tags: Optional[Filter] = None,
    with_bearer: bool = False,
) -> None:
    # pylint: disable=too-many-locals

    if with_bearer:
        if "Authorization" not in headers and "authorization" not in headers:
            headers["Authorization"] = get_bearer_token()
        else:
            raise click.UsageError(
                "--with-bearer flag used but Authorization header provided with --header."
            )

    on, warnings = (frozenset(checks), frozenset()) if checks else process_config()

    selected_checks = get_selected_checks(on)
    register_output_handler(warnings, statistics)
    if not no_additional_cases:
        register_add_case_hooks(on)

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
        prepared_runner,
        DEFAULT_WORKERS,
        show_exception_tracebacks,
        store_request_log,
        None,
    )


def get_selected_checks(
    on: FrozenSet[str],
) -> Iterable[Callable[[Response, Case], None]]:
    return tuple(check for check in ALL_CHECKS if check.__name__ in on)


def register_output_handler(warnings: FrozenSet[str], statistics: bool) -> None:
    def after_init_cli_run_handlers(
        context: HookContext,
        handlers: List[EventHandler],
        execution_context: ExecutionContext,
    ) -> None:
        # filters out the Schemathesis output handlers and adds OutputHandler
        handlers[:] = [
            *filter(
                lambda handler: not isinstance(handler, DefaultOutputStyleHandler)
                and not isinstance(handler, ShortOutputStyleHandler),
                handlers,
            ),
            OutputHandler(warnings, statistics),
        ]

    GLOBAL_HOOK_DISPATCHER.register(after_init_cli_run_handlers)


def register_add_case_hooks(on: FrozenSet) -> None:
    # pylint: disable=bad-str-strip-call
    add_case_prefix = "add_"
    for case_hook in ADD_CASE_HOOKS:
        # add add_case hook if its corresponding check is on
        if case_hook.__name__.lstrip(add_case_prefix) in on:
            GLOBAL_HOOK_DISPATCHER.register_hook_with_name("add_case", case_hook)


def get_bearer_token() -> str:
    if API_KEY not in os.environ or IAM_ENDPOINT not in os.environ:
        raise click.UsageError(
            f"Must set {API_KEY} and {IAM_ENDPOINT} environment variables to use --with-bearer."
        )

    try:
        bearer_token = IAMAuthenticator(
            os.environ[API_KEY], url=os.environ[IAM_ENDPOINT]
        ).token_manager.get_token()
        return "Bearer {0}".format(bearer_token)
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Problem getting bearer token.") from e  # pragma: no cover


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

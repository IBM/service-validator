from typing import Any, Callable, Dict, FrozenSet, IO, Iterable, Tuple

import os
import json
import yaml

CONFIG_FILE_NAME: str = "ibm-service-validator-config"
HANDBOOK_CONFIG_NAME: str = "ibm_cloud_api_handbook"
SCHEMATHESIS_CONFIG_NAME: str = "schemathesis_checks"
DEFAULT_CONFIG: Dict[str, Dict[str, str]] = {
    HANDBOOK_CONFIG_NAME: {
        "allow_header_in_405": "on",
        "content_location": "warn",
        "get_with_request_body": "on",
        "invalid_accept_header": "on",
        "invalid_request_content_type": "on",
        "location_201": "on",
        "no_422": "on",
        "no_accept_header": "on",
        "no_content_204": "on",
        "www_authenticate_401": "on",
    },
    SCHEMATHESIS_CONFIG_NAME: {
        "not_a_server_error": "on",
        "status_code_conformance": "on",
        "content_type_conformance": "on",
        "response_schema_conformance": "on",
    },
}


def process_config() -> Tuple[FrozenSet[str], FrozenSet[str]]:
    config = load_config_file_as_dict(os.getcwd())

    if not config:
        config = DEFAULT_CONFIG

    return checks_on(config), warnings(config)


def load_config_file_as_dict(dir: str) -> Dict[str, Any]:
    """Searches up the directory structure for config file and returns config as dict."""

    if not dir:
        return dict()

    path_to_file = os.path.join(dir, CONFIG_FILE_NAME)

    if os.path.exists(path_to_file + ".yaml"):
        return open_get_data_close(path_to_file + ".yaml", yaml.safe_load)
    elif os.path.exists(path_to_file + ".yml"):
        return open_get_data_close(path_to_file + ".yml", yaml.safe_load)
    elif os.path.exists(path_to_file + ".json"):
        return open_get_data_close(path_to_file + ".json", json.load)
    else:
        # search in parent directory
        return load_config_file_as_dict(dir.rsplit("/", 1)[0])


def checks_on(config: Dict[str, Any]) -> FrozenSet[str]:
    """Returns all checks that are not off.

    Note: warnings are included because we still want to run the warning checks.
    """
    # YAML treats unquoted off as implicit boolean. Hence, we check "not x".
    is_off = lambda x: x == "off" or not x
    not_on = {
        *_get_checks(config.get(HANDBOOK_CONFIG_NAME), is_off),
        *_get_checks(config.get(SCHEMATHESIS_CONFIG_NAME), is_off),
    }
    return frozenset(
        {
            *(
                rule
                for rule in DEFAULT_CONFIG[HANDBOOK_CONFIG_NAME]
                if rule not in not_on
            ),
            *(
                rule
                for rule in DEFAULT_CONFIG[SCHEMATHESIS_CONFIG_NAME]
                if rule not in not_on
            ),
        }
    )


def warnings(config: Dict[str, Any]) -> FrozenSet[str]:
    """Returns set of all warnings."""

    is_warning = lambda x: x == "warn"
    return frozenset(
        {
            *_get_checks(config.get(HANDBOOK_CONFIG_NAME), is_warning),
            *_get_checks(config.get(SCHEMATHESIS_CONFIG_NAME), is_warning),
        }
    )


def _get_checks(config: Any, condition: Callable[[Any], bool]) -> Iterable[str]:
    if not config or not isinstance(config, dict):
        return ()

    # YAML treats unquoted off as implicit boolean. Hence, we check "not val".
    return (rule for rule, val in config.items() if condition(val))


def create_default_config(write_json: bool, overwrite: bool) -> None:
    if write_json:
        _create_default_config(CONFIG_FILE_NAME + ".json", overwrite, json.dump)
    else:
        _create_default_config(CONFIG_FILE_NAME + ".yaml", overwrite, yaml.safe_dump)


def _create_default_config(
    file_name: str, overwrite: bool, dump: Callable[[Any, IO], None]
) -> None:
    if os.path.exists(file_name) and not overwrite:
        print(
            "Config file already exists. Use -o or --overwrite to overwrite the config with default values."
        )
        return

    open_write_close(file_name, DEFAULT_CONFIG, dump)


def open_get_data_close(
    path_to_file: str, load: Callable[[IO], Dict[str, Any]]
) -> Dict[str, Any]:
    f = open(path_to_file, "r")
    data = load(f)
    f.close()
    return data


def open_write_close(
    file_name: str, config: Dict[str, Any], dump: Callable[[Any, IO], None]
) -> None:
    """Writes config data to a file in the cwd."""
    config_file = open(file_name, "a+")
    config_file.truncate(0)  # clear contents of file
    dump(config, config_file)
    config_file.close()

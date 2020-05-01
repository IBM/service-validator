from typing import Any, Callable, Dict, IO, Iterable

import os
import json
import yaml

CONFIG_FILE_NAME: str = "ibm-service-validator-config"
HANDBOOK_CONFIG_NAME: str = "ibm_cloud_api_handbook"
SCHEMATHESIS_CONFIG_NAME: str = "schemathesis_checks"


def process_config_file() -> Iterable[str]:
    config = load_config_file_as_dict(os.getcwd())

    if not config:
        return set()

    return checks_off(config)


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


def checks_off(config: Dict[str, Any]) -> Iterable[str]:
    """Returns set of all checks configured to off."""

    handbook_rules = (
        config[HANDBOOK_CONFIG_NAME] if HANDBOOK_CONFIG_NAME in config else None
    )
    schemathesis_rules = (
        config[SCHEMATHESIS_CONFIG_NAME] if SCHEMATHESIS_CONFIG_NAME in config else None
    )

    return {*_checks_off(handbook_rules), *_checks_off(schemathesis_rules)}


def _checks_off(config: Any) -> Iterable[str]:
    if not config or not isinstance(config, dict):
        return set()

    # YAML treats unquoted off as implicit boolean. Hence, we check "not val".
    return {rule for rule, val in config.items() if val == "off" or not val}


def open_get_data_close(
    path_to_file: str, load: Callable[[IO], Dict[str, Any]]
) -> Dict[str, Any]:
    f = open(path_to_file, "r")
    data = load(f)
    f.close()
    return data

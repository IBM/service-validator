from typing import Any, Callable, Dict, IO, Iterable

import os
import json
import yaml

CONFIG_FILE_NAME = "ibm-service-validator-config"
RULE_CONFIG_NAME = "ibm_cloud_api_handbook"


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
    all_rules = config[RULE_CONFIG_NAME] if RULE_CONFIG_NAME in config else None

    if not all_rules or not isinstance(all_rules, dict):
        return set()

    # YAML treats unquoted off as implicit boolean. Hence, we check "not val".
    return {rule for rule, val in all_rules.items() if val == "off" or not val}


def open_get_data_close(
    path_to_file: str, load: Callable[[IO], Dict[str, Any]]
) -> Dict[str, Any]:
    f = open(path_to_file, "r")
    data = load(f)
    f.close()
    return data

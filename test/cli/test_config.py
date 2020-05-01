import os
import json
import yaml

from src.ibm_service_validator.cli.process_config import (
    checks_off,
    load_config_file_as_dict,
    open_get_data_close,
    process_config_file,
)
from src.ibm_service_validator.cli.process_config import (
    CONFIG_FILE_NAME,
    HANDBOOK_CONFIG_NAME,
    SCHEMATHESIS_CONFIG_NAME,
)


def test_process_config_file(tmp_path, config_object, open_write_close):
    # set the cwd to a temporary path that is torn down after tests run
    os.chdir(tmp_path)

    # create a config file in the temp cwd
    open_write_close(CONFIG_FILE_NAME + ".yaml", config_object, yaml.safe_dump)

    checks_turned_off = process_config_file()

    assert all(
        [
            rule in checks_turned_off
            for rule, val in config_object[HANDBOOK_CONFIG_NAME].items()
            if val == "off" or val == False
        ]
    )


def test_process_config_file_1(tmp_path, config_object, open_write_close):
    # set the cwd to a temporary path that is torn down after tests run
    os.chdir(tmp_path)

    # create a config file in the temp cwd
    open_write_close(CONFIG_FILE_NAME + ".yml", config_object, yaml.safe_dump)

    checks_turned_off = process_config_file()

    assert all(
        [
            rule in checks_turned_off
            for rule, val in config_object[HANDBOOK_CONFIG_NAME].items()
            if val == "off" or val == False
        ]
    )


def test_process_config_file_2(tmp_path, config_object, open_write_close):
    # set the cwd to a temporary path that is torn down after tests run
    os.chdir(tmp_path)

    # create a config file in the temp cwd
    open_write_close(CONFIG_FILE_NAME + ".json", config_object, json.dump)

    checks_turned_off = process_config_file()

    assert all(
        [
            rule in checks_turned_off
            for rule, val in config_object[HANDBOOK_CONFIG_NAME].items()
            if val == "off" or val == False
        ]
    )


def test_process_config_file_3(tmp_path):
    """Ensure we receive an empty set when no config file is present."""

    # set the cwd to a temporary path that is torn down after tests run
    os.chdir(tmp_path)

    # did not create a config file
    assert not process_config_file()


def test_load_config_file_as_dict(tmp_path, config_object, open_write_close):
    os.chdir(tmp_path)

    open_write_close(CONFIG_FILE_NAME + ".yaml", config_object, yaml.safe_dump)

    config = load_config_file_as_dict(tmp_path)

    assert config == config_object


def test_load_config_file_as_dict_1(tmp_path, config_object, open_write_close):
    os.chdir(tmp_path)

    open_write_close(CONFIG_FILE_NAME + ".yml", config_object, yaml.safe_dump)

    config = load_config_file_as_dict(tmp_path)

    assert config == config_object


def test_load_config_file_as_dict_2(tmp_path, config_object, open_write_close):
    os.chdir(tmp_path)

    open_write_close(CONFIG_FILE_NAME + ".json", config_object, json.dump)

    config = load_config_file_as_dict(tmp_path)

    assert config == config_object


def test_load_config_file_as_dict_3(tmp_path, config_object, open_write_close):
    """Test finding the config file in a parent directory."""
    os.chdir(tmp_path)
    open_write_close(CONFIG_FILE_NAME + ".json", config_object, json.dump)

    # Make child directory, set cwd to child directory, and call
    # load from starting from child directory
    child_dir_name = "child"
    os.mkdir(child_dir_name)
    os.chdir(child_dir_name)
    config = load_config_file_as_dict(os.getcwd())

    assert config == config_object


def test_checks_off(config_object):
    checks_turned_off = checks_off(config_object)

    assert all(
        [
            rule in checks_turned_off
            for rule, val in config_object[HANDBOOK_CONFIG_NAME].items()
            if val == "off" or val == False
        ]
    )


def test_checks_off_1(config_object):
    checks_turned_off = checks_off(config_object)

    all_config_rules = dict(
        **config_object[HANDBOOK_CONFIG_NAME], **config_object[SCHEMATHESIS_CONFIG_NAME]
    )
    assert all(
        [
            rule in checks_turned_off
            for rule, val in all_config_rules.items()
            if val == "off" or val == False
        ]
    )


def test_checks_off_2():
    mock_config = {HANDBOOK_CONFIG_NAME: ["should not be a list"]}

    # rules must be dict not list, so we expect empty set
    assert not checks_off(mock_config)


def test_checks_off_3():
    mock_config = {"not a valid key": {"rule1": "off"}}

    assert not checks_off(mock_config)


def test_open_get_data_close(tmp_path, config_object, open_write_close):
    os.chdir(tmp_path)

    file_name = "temp_file.yaml"
    open_write_close(file_name, config_object, yaml.safe_dump)

    path_to_file = os.path.join(str(tmp_path), file_name)
    assert open_get_data_close(path_to_file, yaml.safe_load) == config_object

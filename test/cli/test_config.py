import os
import json
import yaml

from src.ibm_service_validator.cli.process_config import (
    checks_off,
    create_default_config,
    load_config_file_as_dict,
    open_get_data_close,
    open_write_close,
    process_config_file,
)
from src.ibm_service_validator.cli.process_config import (
    CONFIG_FILE_NAME,
    DEFAULT_CONFIG,
    HANDBOOK_CONFIG_NAME,
    SCHEMATHESIS_CONFIG_NAME,
)


def test_process_config_file(tmp_cwd, config_object, write_to_file):
    # create a config file in the temp cwd
    write_to_file(CONFIG_FILE_NAME + ".yaml", config_object, yaml.safe_dump)

    checks_turned_off = process_config_file()

    assert all(
        [
            rule in checks_turned_off
            for rule, val in config_object[HANDBOOK_CONFIG_NAME].items()
            if val == "off" or val == False
        ]
    )


def test_process_config_file_1(tmp_cwd, config_object, write_to_file):
    # create a config file in the temp cwd
    write_to_file(CONFIG_FILE_NAME + ".yml", config_object, yaml.safe_dump)

    checks_turned_off = process_config_file()

    assert all(
        [
            rule in checks_turned_off
            for rule, val in config_object[HANDBOOK_CONFIG_NAME].items()
            if val == "off" or val == False
        ]
    )


def test_process_config_file_2(tmp_cwd, config_object, write_to_file):
    # create a config file in the temp cwd
    write_to_file(CONFIG_FILE_NAME + ".json", config_object, json.dump)

    checks_turned_off = process_config_file()

    assert all(
        [
            rule in checks_turned_off
            for rule, val in config_object[HANDBOOK_CONFIG_NAME].items()
            if val == "off" or val == False
        ]
    )


def test_process_config_file_3(tmp_cwd):
    """Ensure we receive an empty set when no config file is present."""
    # did not create a config file
    assert not process_config_file()


def test_load_config_file_as_dict(tmp_cwd, config_object, write_to_file):
    write_to_file(CONFIG_FILE_NAME + ".yaml", config_object, yaml.safe_dump)

    config = load_config_file_as_dict(tmp_cwd)

    assert config == config_object


def test_load_config_file_as_dict_1(tmp_cwd, config_object, write_to_file):
    write_to_file(CONFIG_FILE_NAME + ".yml", config_object, yaml.safe_dump)

    config = load_config_file_as_dict(tmp_cwd)

    assert config == config_object


def test_load_config_file_as_dict_2(tmp_cwd, config_object, write_to_file):
    write_to_file(CONFIG_FILE_NAME + ".json", config_object, json.dump)

    config = load_config_file_as_dict(tmp_cwd)

    assert config == config_object


def test_load_config_file_as_dict_3(tmp_cwd, config_object, write_to_file):
    """Test finding the config file in a parent directory."""

    write_to_file(CONFIG_FILE_NAME + ".json", config_object, json.dump)

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


def test_create_default_config(tmp_cwd):
    create_default_config(write_json=True, overwrite=False)

    path_to_file = os.path.join(str(tmp_cwd), CONFIG_FILE_NAME + ".json")
    assert open_get_data_close(path_to_file, json.load) == DEFAULT_CONFIG


def test_create_default_config_1(tmp_cwd):
    create_default_config(write_json=False, overwrite=False)

    path_to_file = os.path.join(str(tmp_cwd), CONFIG_FILE_NAME + ".yaml")
    assert open_get_data_close(path_to_file, yaml.safe_load) == DEFAULT_CONFIG


def test_create_default_config_2(tmp_cwd, write_to_file):
    """Test overwriting the existing config file."""
    file_name = CONFIG_FILE_NAME + ".yaml"
    json_config = {"error": "writing json, not yaml"}
    # Writing json object to yaml file
    write_to_file(file_name, json_config, json.dump)
    # Should overwrite json object with yaml config
    create_default_config(write_json=False, overwrite=True)

    path_to_file = os.path.join(str(tmp_cwd), file_name)
    assert open_get_data_close(path_to_file, yaml.safe_load) == DEFAULT_CONFIG


def test_create_default_config_3(tmp_cwd, write_to_file):
    """Test overwriting the existing config file."""
    file_name = CONFIG_FILE_NAME + ".yaml"
    json_config = {"error": "writing json, not yaml"}
    # Writing json object to yaml file
    write_to_file(file_name, json_config, json.dump)
    # Should not overwrite file. File should still contain JSON object.
    create_default_config(write_json=False, overwrite=False)

    path_to_file = os.path.join(str(tmp_cwd), CONFIG_FILE_NAME + ".yaml")
    # JSON object should still be in file.
    assert open_get_data_close(path_to_file, json.load) == json_config


def test_open_get_data_close(tmp_cwd, config_object, write_to_file):
    file_name = "temp_file.yaml"
    write_to_file(file_name, config_object, yaml.safe_dump)

    path_to_file = os.path.join(str(tmp_cwd), file_name)
    assert open_get_data_close(path_to_file, yaml.safe_load) == config_object


def test_open_write_close(tmp_cwd, config_object):
    file_name = "temp_file.yaml"

    open_write_close(file_name, config_object, yaml.safe_dump)
    path_to_file = os.path.join(str(tmp_cwd), file_name)
    assert open_get_data_close(path_to_file, yaml.safe_load) == config_object


def test_open_write_close_twice(tmp_cwd, config_object):
    """Write the config object twice. Test that only one config object is in the file."""
    file_name = "temp_file.yaml"

    # write to file twice
    open_write_close(file_name, config_object, yaml.safe_dump)
    open_write_close(file_name, config_object, yaml.safe_dump)

    path_to_file = os.path.join(str(tmp_cwd), file_name)
    assert open_get_data_close(path_to_file, yaml.safe_load) == config_object

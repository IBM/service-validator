import os
import json
import yaml

from src.ibm_service_validator.cli.process_config import (
    checks_on,
    create_default_config,
    load_config_file_as_dict,
    open_get_data_close,
    open_write_close,
    process_config,
)
from src.ibm_service_validator.cli.process_config import (
    CONFIG_FILE_NAME,
    DEFAULT_CONFIG,
    HANDBOOK_CONFIG_NAME,
    SCHEMATHESIS_CONFIG_NAME,
)


def test_process_config(tmp_cwd, config_off_object, write_to_file):
    # create a config file in the temp cwd
    write_to_file(CONFIG_FILE_NAME + ".yaml", config_off_object, yaml.safe_dump)

    on, warnings = process_config()

    assert not on
    assert not warnings


def test_process_config_1(tmp_cwd, config_off_object, write_to_file):
    # create a config file in the temp cwd
    write_to_file(CONFIG_FILE_NAME + ".yml", config_off_object, yaml.safe_dump)

    on, warnings = process_config()

    assert not on
    assert not warnings


def test_process_config_2(tmp_cwd, config_off_object, write_to_file):
    # create a config file in the temp cwd
    write_to_file(CONFIG_FILE_NAME + ".json", config_off_object, json.dump)

    on, warnings = process_config()

    assert not on
    assert not warnings


def test_process_config_3(tmp_cwd):
    """Ensure the checks match the default config when no config file present."""
    # did not create a config file, DEFAULT_CONFIG used
    on, warnings = process_config()
    assert all(
        all(rule in on for rule, val in rules.items() if val and val != "off")
        for _, rules in DEFAULT_CONFIG.items()
    )
    assert all(
        all(rule in warnings for rule, val in rules.items() if val == "warn")
        for _, rules in DEFAULT_CONFIG.items()
    )


def test_process_config_4(tmp_cwd, config_warn_object, write_to_file):
    """Ensure all checks are set to warnings."""
    write_to_file(CONFIG_FILE_NAME + ".json", config_warn_object, json.dump)
    on, warnings = process_config()

    assert all(
        all(rule in on for rule, val in rules.items() if val and val != "off")
        for _, rules in config_warn_object.items()
    )
    assert all(
        all(rule in warnings for rule, val in rules.items() if val == "warn")
        for _, rules in config_warn_object.items()
    )


def test_load_config_file_as_dict(tmp_cwd, config_off_object, write_to_file):
    write_to_file(CONFIG_FILE_NAME + ".yaml", config_off_object, yaml.safe_dump)

    config = load_config_file_as_dict(tmp_cwd)

    assert config == config_off_object


def test_load_config_file_as_dict_1(tmp_cwd, config_off_object, write_to_file):
    write_to_file(CONFIG_FILE_NAME + ".yml", config_off_object, yaml.safe_dump)

    config = load_config_file_as_dict(tmp_cwd)

    assert config == config_off_object


def test_load_config_file_as_dict_2(tmp_cwd, config_off_object, write_to_file):
    write_to_file(CONFIG_FILE_NAME + ".json", config_off_object, json.dump)

    config = load_config_file_as_dict(tmp_cwd)

    assert config == config_off_object


def test_load_config_file_as_dict_3(tmp_cwd, config_off_object, write_to_file):
    """Test finding the config file in a parent directory."""

    write_to_file(CONFIG_FILE_NAME + ".json", config_off_object, json.dump)

    # Make child directory, set cwd to child directory, and call
    # load from starting from child directory
    child_dir_name = "child"
    os.mkdir(child_dir_name)
    os.chdir(child_dir_name)
    config = load_config_file_as_dict(os.getcwd())

    assert config == config_off_object


def test_checks_on(config_off_object):
    assert not checks_on(config_off_object)


def test_checks_on_1():
    mock_config = {HANDBOOK_CONFIG_NAME: ["should not be a list"]}
    on = checks_on(mock_config)

    # no checks explicitly set to off or warn
    assert all(
        all(rule in on for rule, val in rules.items() if val and val != "off")
        for _, rules in DEFAULT_CONFIG.items()
    )


def test_checks_on_2():
    mock_config = {"not a valid key": {"rule1": "off"}}
    on = checks_on(mock_config)

    # no checks explicitly set to off or warn
    assert all(
        all(rule in on for rule, val in rules.items() if val and val != "off")
        for _, rules in DEFAULT_CONFIG.items()
    )


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


def test_open_get_data_close(tmp_cwd, config_off_object, write_to_file):
    file_name = "temp_file.yaml"
    write_to_file(file_name, config_off_object, yaml.safe_dump)

    path_to_file = os.path.join(str(tmp_cwd), file_name)
    assert open_get_data_close(path_to_file, yaml.safe_load) == config_off_object


def test_open_write_close(tmp_cwd, config_off_object):
    file_name = "temp_file.yaml"

    open_write_close(file_name, config_off_object, yaml.safe_dump)
    path_to_file = os.path.join(str(tmp_cwd), file_name)
    assert open_get_data_close(path_to_file, yaml.safe_load) == config_off_object


def test_open_write_close_twice(tmp_cwd, config_off_object):
    """Write the config object twice. Test that only one config object is in the file."""
    file_name = "temp_file.yaml"

    # write to file twice
    open_write_close(file_name, config_off_object, yaml.safe_dump)
    open_write_close(file_name, config_off_object, yaml.safe_dump)

    path_to_file = os.path.join(str(tmp_cwd), file_name)
    assert open_get_data_close(path_to_file, yaml.safe_load) == config_off_object

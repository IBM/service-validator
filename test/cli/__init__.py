from typing import Callable, IO

CONFIG_OBJECT = {
    "ibm_cloud_api_handbook": {
        "allow_header_in_405": "off",
        "invalid_request_content_type": "off",
        "location_201": "off",
        "no_422": "off",
        "no_accept_header": "off",
        "no_content_204": "off",
        "www_authenticate_401": "off",
    }
}


def open_write_config_close(file_name: str, dump: Callable[[IO], None]) -> None:
    config_file = open(file_name, "a+")
    dump(CONFIG_OBJECT, config_file)
    config_file.close()

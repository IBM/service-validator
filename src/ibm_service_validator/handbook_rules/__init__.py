from ibm_service_validator.handbook_rules.add_case_rules import (
    get_with_request_body,
    invalid_accept_header,
    invalid_request_content_type,
)
from ibm_service_validator.handbook_rules.general_rules import header_rules
from ibm_service_validator.handbook_rules.general_rules import status_code_rules

HANDBOOK_RULES: tuple = (
    get_with_request_body.get_with_request_body,
    invalid_accept_header.invalid_accept_header,
    invalid_request_content_type.invalid_request_content_type,
    header_rules.allow_header_in_405,
    header_rules.content_location,
    header_rules.location_201,
    header_rules.no_accept_header,
    header_rules.www_authenticate_401,
    status_code_rules.no_422,
    status_code_rules.no_content_204,
)

ADD_CASE_HOOKS: tuple = (
    get_with_request_body.add_get_with_request_body,
    invalid_accept_header.add_invalid_accept_header,
    invalid_request_content_type.add_invalid_request_content_type,
)

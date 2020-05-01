from ibm_service_validator.validation_hooks import header_rules
from ibm_service_validator.validation_hooks import status_code_rules

HANDBOOK_RULES: tuple = (
    header_rules.allow_header_in_405,
    header_rules.location_201,
    header_rules.no_accept_header,
    header_rules.www_authenticate_401,
    status_code_rules.default_response_content_type,
    status_code_rules.no_422,
    status_code_rules.no_content_204,
)

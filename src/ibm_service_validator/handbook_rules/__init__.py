#!/usr/bin/env python
# Copyright 2020 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

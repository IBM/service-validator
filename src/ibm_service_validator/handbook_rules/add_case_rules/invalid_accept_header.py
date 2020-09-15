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

from typing import Optional
from requests import Response

from schemathesis.models import Case
from schemathesis.hooks import HookContext

from . import get_request_header, original_case_successful, set_request_header


def add_invalid_accept_header(
    context: HookContext, case: Case, response: Response
) -> Optional[Case]:
    if original_case_successful(response):
        set_request_header(case, "Accept", "invalid/accept")
        return case
    else:
        return None


def invalid_accept_header(response: Response, case: Case) -> Optional[bool]:
    accept_header = get_request_header(response.request, "Accept")
    if accept_header == "invalid/accept":
        assert (
            response.status_code == 406
        ), "Requests including Accept header with only unsupported formats MUST be rejected with a 406 status code. https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-headers#negotiation-headers"
    else:
        # skips the check when it's not relevant
        return True
    return None

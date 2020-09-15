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

from . import original_case_successful


def add_get_with_request_body(
    context: HookContext, case: Case, response: Response
) -> Optional[Case]:
    if original_case_successful(response) and case.method.upper() == "GET":
        # add request body if the original case received 2xx response
        case.body = {"requestBody": "request body passed with GET."}
        return case
    else:
        # otherwise, do not create an additional test case
        return None


def get_with_request_body(response: Response, case: Case) -> Optional[bool]:
    """Validates that request body is ignored for otherwise valid GET request.

    Assumes the constructed request is valid aside from the request body.
    """
    request = response.request
    if request.method == "GET" and request.body:
        assert (
            200 <= response.status_code < 300
        ), "Request body with a GET request must not cause an error. https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-methods#get"
    else:
        # skips the test when it's not relevant
        return True
    return None

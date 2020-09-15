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


def no_422(response: Response, case: Case) -> Optional[bool]:
    assert (
        response.status_code != 422
    ), "422 code should not be used. Instead, 400 should be returned in response to invalid request payloads. https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-status-codes#client-errors-4xx"
    return None


def no_content_204(response: Response, case: Case) -> Optional[bool]:
    if response.status_code == 204:
        assert (
            not response.content
        ), "204 response must not include a response body. https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-status-codes#success-2xx"
    else:
        # skips the test when it's not relevant
        return True
    return None

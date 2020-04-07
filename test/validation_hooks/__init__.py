from typing import Callable

from requests.models import Response

from schemathesis.models import Case


def mock_decorator(
    f: Callable[[Response, Case], None]
) -> Callable[[Response, Case], None]:
    return f

from typing import Callable

from requests.models import Response, PreparedRequest

from schemathesis.models import Case, Endpoint


def mock_decorator(
    f: Callable[[Response, Case], None]
) -> Callable[[Response, Case], None]:
    return f


def mock_objects() -> (Case, Response):
    return (Case("http://mockapi.com"), Response())


def prepare_request(
    method="GET",
    url="http://mockapi.com",
    headers=None,
    files=None,
    data=None,
    params=None,
    auth=None,
    cookies=None,
    hooks=None,
    json=None,
) -> PreparedRequest:
    request = PreparedRequest()
    request.prepare(
        method=method,
        url=url,
        headers=headers,
        files=files,
        data=data,
        params=params,
        auth=auth,
        cookies=cookies,
        hooks=hooks,
        json=json,
    )

    return request


def create_endpoint(
    path=None,
    method=None,
    definition=None,
    schema=None,
    app=None,
    base_url=None,
    path_parameters=None,
    headers=None,
    cookies=None,
    query=None,
    body=None,
    form_data=None,
) -> Endpoint:
    return Endpoint(
        path,
        method,
        definition,
        schema,
        app,
        base_url,
        path_parameters,
        headers,
        cookies,
        query,
        body,
        form_data,
    )

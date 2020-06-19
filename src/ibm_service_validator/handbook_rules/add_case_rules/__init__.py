from requests import PreparedRequest, Response

from schemathesis.models import Case


def get_request_header(request: PreparedRequest, header_name: str) -> str:
    return (
        request.headers[header_name]
        if request and request.headers and header_name in request.headers
        else ""
    )


def original_case_successful(response: Response) -> bool:
    return 200 <= response.status_code < 300


def set_request_header(case: Case, header_name: str, header_val: str) -> None:
    """Adds or overwrites header with header_name."""
    if not case.headers:
        case.headers = {header_name: header_val}
        return

    current_headers_dict = {header.lower(): header for header in case.headers}
    if header_name.lower() in current_headers_dict:
        # overwite the existing header
        case.headers[current_headers_dict[header_name.lower()]] = header_val
    else:
        case.headers[header_name] = header_val

import threading, socket
from multiprocessing import Process
from time import sleep

from typing import Optional

from flask import Flask, jsonify, request

VALID_API_KEY = "abc123"
TOKEN = "eyJraWQiOiIyMDIwMDQyNTE4MjkiLCJhbGciOiJSUzI1NiJ9.eyJpYW1faWQiOiJJQk1pZC01NTAwMDVCVEpZIiwiaWQiOiJJQk1pZC01NTAwMDVCVEpZIiwicmVhbG1pZCI6IklCTWlkIiwiaWRlbnRpZmllciI6IjU1MDAwNUJUSlkiLCJnaXZlbl9uYW1lIjoiQmFycmV0dCIsImZhbWlseV9uYW1lIjoiU2Nob25lZmVsZCIsIm5hbWUiOiJCYXJyZXR0IFNjaG9uZWZlbGQiLCJlbWFpbCI6ImJhcnJldHQuc2Nob25lZmVsZEBpYm0uY29tIiwic3ViIjoiYmFycmV0dC5zY2hvbmVmZWxkQGlibS5jb20iLCJhY2NvdW50Ijp7InZhbGlkIjp0cnVlLCJic3MiOiJlZTNkYjcxMDdjN2I0NTdjOGZkZjY3YWZiNjBlNWJkZCJ9LCJpYXQiOjE1ODg4NzcwMDUsImV4cCI6MTU4ODg4MDYwNSwiaXNzIjoiaHR0cHM6Ly9pYW0uY2xvdWQuaWJtLmNvbS9pZGVudGl0eSIsImdyYW50X3R5cGUiOiJ1cm46aWJtOnBhcmFtczpvYXV0aDpncmFudC10eXBlOmFwaWtleSIsInNjb3BlIjoiaWJtIG9wZW5pZCIsImNsaWVudF9pZCI6ImRlZmF1bHQiLCJhY3IiOjEsImFtciI6WyJwd2QiXX0.DEI8uNi-yQOTQWGgZvOk4eAdZ2dt8DYRXL25_tqq7T6hAhx40H2LidwBaOJHjr-x9fMN3K95i5ppkKNZ-s4v6waJNXdNMmtbUSOUUjSR8venlRDlWAfW92uUYaIooZrVdQD05d6fekVZGn_l-a0vIGvc_zkaaR9XDBhYQyLr-0sYZUgsyU66iK5KqsW80B2LgezOx9sMxqlz5KORGsAKke0CeS2z6s-xxCUaKsmMH2XJ92NBPZfTETatmVDuVM6Qjx4yIOGVxuSIP_YZILnmfXCgYrtvb8YjcTKZ7xpaR-iF74nt0ct08tqSiX40KLf_rGP28Q2NzJ8h8-4hlzFltA"


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/allof", methods=["GET"])
    def allof():
        data = {"foo": 2, "bar": "string"}
        return jsonify(data), 200

    @app.route("/array", methods=["GET"])
    def array():
        data = {"list": ["string1", "string2"]}
        return jsonify(data), 200

    @app.route("/boolean", methods=["GET"])
    def boolean():
        data = {"foo": True}
        return jsonify(data), 200

    @app.route("/datetime", methods=["GET"])
    def datetime():
        data = {"foo": "2017-07-21T17:32:28Z"}
        return jsonify(data), 200

    @app.route("/integer", methods=["GET"])
    def integer():
        data = {"foo": 2}
        return jsonify(data), 200

    @app.route("/string", methods=["GET"])
    def string():
        data = {"foo": "string"}
        return jsonify(data), 200

    @app.route("/status_code_conformance_failure", methods=["GET"])
    def status_code_conformance_failure():
        data = {"foo": "string"}
        return jsonify(data), 400

    @app.route("/server_error", methods=["GET"])
    def server_error():
        data = {"foo": "string"}
        return jsonify(data), 500

    @app.route("/need_authorization", methods=["GET"])
    def need_authorization():
        if request.headers.get("Authorization") == "Bearer " + TOKEN:
            return jsonify({"foo": "success!"}), 200
        else:
            return jsonify({"no_auth": "missing valid token"}), 401

    @app.route("/token", methods=["POST"])
    def token():
        if request.form.get("apikey") == VALID_API_KEY:
            data = {
                "access_token": TOKEN,
                "refresh_token": TOKEN,
                "expires_in": 3600,
                "expires": 999999999999999,
                "token_type": "Bearer",
            }
            return jsonify(data), 201
        else:
            return jsonify({"invalid_api_key": "did not get expected API key."}), 401

    return app


def run_server_as_child(
    app: Flask, port: Optional[int] = None, timeout: float = 0.02
) -> int:
    """Starts Flask server as subprocess.

    Returns the server url and a reference to the subprocess.
    """

    if not port:
        port = find_port()

    server_process = Process(target=_run_server, args=(app, port))
    server_process.start()
    # give time for the server to start
    sleep(timeout)
    server_url: str = "http://127.0.0.1:" + str(port)
    return server_url, server_process


def _run_server(app: Flask, port: int) -> None:
    app.run(port=port)


def find_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # selects an available port and binds to it
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


if __name__ == "__main__":
    run_server_as_child(create_app(), 5000)

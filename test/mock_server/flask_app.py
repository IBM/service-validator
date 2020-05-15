import threading, socket
from multiprocessing import Process
from time import sleep

from typing import Optional

from flask import Flask, Response, jsonify


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

# ibm-service-validator 0.5.0

Extends [Schemathesis](https://github.com/kiwicom/schemathesis) to test [IBM API Handbook](https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-intro) compliance and consistency between an API implementation and its OpenAPI definition.

## Overview

This tool takes an OpenAPI definition, a valid API endpoint, and any necessary API credentials and verifies that the API implementation complies with its OpenAPI definition and the [IBM API Handbook](https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-intro).

## Python Version

The minimum python version supported is 3.5.8

## Install

The Service Validator is distributed through PyPI, and you may install using `pip`.

    pip3 install ibm-service-validator

## Use

### Run

The `run` command runs a suite of tests against the service using an API definition.

    ibm-service-validator [env] run <API definition> --base-url <base URL of API> [run options]

#### [env]

The following options may be used to set environment variables used to obtain a bearer token when --with-bearer used:

- --set-api-key: set the IBM_CLOUD_SERVICE_VALIDATOR_API_KEY environment variable to the API key needed to obtain a bearer token.
- --set-iam-endpoint: set the IBM_CLOUD_SERVICE_VALIDATOR_IAM_ENDPOINT to the URL of the API at which the bearer token may be obtained.

Example Usage:

    ibm-service-validator --set-api-key=YOUR_API_KEY --set-iam-endpoint=https://iam.test.cloud.ibm.com/identity/token run path/to/schema -b https://api.com --with-bearer

#### run options

- -a (--auth): provide server username and password in the form `username:password`.
- -A (--auth-type): authentication mechanism. May be "basic" or "digest" (default is "basic").
- -b (--base-url): base url of the service to be tested.
- -c (--checks): comma-separated list of checks to run. Example: `--checks=not_a_server_error,response_schema_conformance`.
  - See [configuration](#configuration) for full list of checks
- -x (--exitfirst): flag to exit and report on the first error or test failure.
- -H (--header): custom header to include in all requests. Example: `-H Authorization:Bearer\ 123`.
- -v (--verbosity): increase the verbosity of the report using the repetition of options. Examples: `-v`, `-vv`, `-vvv` in order of increasing verbosity. We only use one level of verbosity but this is passed to schemathesis which may utilize more levels of verbosity.
- -B (--with-bearer): obtains a bearer token and includes it in tests. Uses [environment variables](#env) to obtain the bearer token.
- --show-errors-tracebacks: flag to show error tracebacks for internal errors.
- --store-request-log: name of yaml file in which to store logs of requests made during testing. Example: `--store-request-log=logs.yaml`.
- --hypothesis-deadline: number of milliseconds allowed for the server to respond (default is 500). Example: `--hypothesis-deadline=300`.
- --hypothesis-phases: determines how test data will be generated. **The default value, `explicit`, indicates test data will only be generated from examples in the OpenAPI definition.** Example: `--hypothesis-phases=explicit,generate` will use explicit OpenAPI examples and generate test data.
  - `explicit`: test data generated from examples. Recommended.
  - `reuse`: reuse old test data.
  - `generate`: test data generated from schema definition.
  - `target`: mutate test data for targeting.
  - `shrink`: shrink test data.
- --hypothesis-verbosity: control how much information is reported. Example: `--hypothesis-verbosity=verbose`
  - `quiet`
  - `normal`
  - `verbose`
  - `debug`

Filter tests by endpoints, methods, and/or tags that match a given endpoint/method/tag pattern. 

- -E (--endpoint) Example: `-E /users/create`, will only test endpoints containing `/users/create`
- -M (--method) Example: `-M GET`, will only test endpoints with GET requests
- -T (--tag) Example: `-T custom_tag`, will only test endpoints with the schema defined tag of `custom_tag`
- -O (--operation-id) Example: `-O custom_operation_id`, will only test the endpoint with the `custom_operation_id` operation_id

Options when generating test data for schema definitions without schema defined examples. When there is no example defined in the API definition, these options will determine how the mock-data is generated when testing that endpoint.

- --hypothesis-derandomize: this flag is used to generate test data deterministically instead of generating random, valid test data.
- --hypothesis-max-examples: this value determines the maximum number of tests to generate for each method. Example: `--hypothesis-max-examples=50`.
- --hypothesis-seed: provide a seed from which random test data will be generated.

### Replay

The `replay` command runs a snapshot of tests and compares new results to the original results. This command takes a file with logs from a previous run of tests.

    ibm-service-validator replay path/to/logs.yaml [options]

Note: To capture these logs, run the service validator with the `--store-request-log` option.

Example: 
- `ibm-service-validator run path/to/mock_server.yaml --base-url https://localhost:5000 --store-request-log=request_log.yaml`
- `ibm-service-validator replay request_log.yaml --status=FAILURE`

This will re-run the service validator on the previous run but only on the endpoints that returned a FAILURE and will report the new result for each endpoint.

#### replay options

- --id: run a specific request by providing the request id (`--id 1`).
- --status: run only the requests with a specific status code (`--status SUCCESS`).
  - SUCCESS
  - ERROR
  - FAILURE
- --uri: run the requests that contain the given uri (`--uri path1/resources`)
- --method: run only the requests that use the given HTTP method (`--method GET`)

## Configuration

### Configuration File

Rules may be configured using a `ibm-service-validator-config.yaml` or `ibm-service-validator-config.json` file.

We look for a configuration file in the current working directory from which the service validator is invoked, and we search up the directory until we find the first matching config file. It is recommended to create this configuration file in the root directory of your project.

Rules may be on, off, or warn. An example of the configuration file is given below:

    ibm_cloud_api_handbook:
        allow_header_in_405: 'on'
        content_location: warn
        get_with_request_body: 'on'
        invalid_accept_header: 'on'
        invalid_request_content_type: 'on'
        location_201: 'on'
        no_422: 'on'
        no_accept_header: 'on'
        no_content_204: 'on'
        www_authenticate_401: 'on'
    schemathesis_checks:
        not_a_server_error: 'on'
        status_code_conformance: 'warn'
        content_type_conformance: 'warn'
        response_schema_conformance: 'on'

### Create Default Configuration File

To initialize a default configuration file in the current working directory, use:

    ibm-service-validator init [options]

#### init options

- -o (--overwrite): if config file already exists, overwrite the existing config file with default values.
- -j (--json): write the default config file as json.

### Add Case Rules

For some rules, we send an additional request to the API to target specific behavior. We call these rules `add_case` rules. The `invalid_request_content_type` rule, for example, tests how the API responds when it receives a request with a request body and an invalid `Content-Type` header. To make this rule effective, we need to send a request to the API with an invalid `Content-Type` header. For `invalid_request_content_type` and all other `add_case` rules listed below, we create an additional request to exercise the behavior the rule is testing. When an `add_case` rule is disabled, the additional request is also disabled.

`add_case` Rules:

- get_with_request_body
- invalid_accept_header
- invalid_request_content_type

## Including Examples in API Definition

Often, a service's requirements are stricter than its schema. For example, an `account_id` may have schema, `type: string`. However, a valid `account_id` is restricted to the set of strings associated with an account. For this reason, the default way to generate requests is to use [OpenAPI examples](https://swagger.io/docs/specification/adding-examples/) in the API definition. Notice examples may be provided using the `example` and `examples` keywords. The service validator supports both `example` and `examples`.

### Important Note on Providing an Object Example

Examples for object properties should be provided in an example object instead of individual property examples. Hence, for the schema:

    schema:
        type: object
        properties:
        id:
            type: integer
        name:
            type: string

Provide an example object:

    schema:
        type: object
        properties:
        id:
            type: integer
        name:
            type: string
        example:
            id: 10
            name: Jessica Smith

Instead of individual property examples:

    schema:
        type: object
        properties:
        id:
            type: integer
            example: 10
        name:
            type: string
            example: Jessica Smith

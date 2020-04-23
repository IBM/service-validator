# ibm-service-validator

Extends [Schemathesis](https://github.com/kiwicom/schemathesis) to test [IBM API Handbook](https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-intro) compliance and consistency between an API implementation and its OpenAPI definition.

Issues may be opened [here](https://github.ibm.com/arf/planning-sdk-squad/issues).

## Overview

This tool takes an OpenAPI definition, a valid API endpoint, and any necessary API credentials and verifies that the API implementation complies with its OpenAPI definition and the [IBM API Handbook](https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-intro).

## Install

1. Find the version of the endpoint validator you want to use in the [releases](https://github.ibm.com/CloudEngineering/ibm-service-validator/releases) tab.
2. Download the corresponding .whl (recommended) or .tar.gz file.
3. `pip install ibm_service_validator-<version>.whl` or `pip install ibm_service_validator-<version>.tar.gz`

## Use

### Command line

    ibm-service-validator <path API definition> --base-url <base URL of API> [options]

#### [options]

- -a (--auth): provide server username and password in the form `username:password`.
- -A (--auth-type): authentication mechanism. May be "basic" or "digest" (default is "basic").
- -b (--base-url): base url of the service to be tested.
- -H (--header): custom header to include in all requests. Example: `-H Authorization:Bearer\ 123`.
- -x (--exitfirst): exit and report on the first error or test failure.
- --show-errors-tracebacks: show error tracebacks for internal errors.
- --hypothesis-deadline: number of milliseconds allowed for the server to respond (default is 500). Example: `--hypothesis-deadline=300`.
- --hypothesis-phases: determines how test data will be generated. **By default, "explicit" indicates test data will only be generated from examples in the OpenAPI definition.** Example: `--hypothesis-deadline=explicit,generate` will use explicit OpenAPI examples and generate test data.
  - `explicit`: test data generated from examples. Recommended.
  - `reuse`: reuse old test data.
  - `generate`: test data generated from schema definition.
  - `target`: mutate test data for targeting.
  - `shrink`: shrink test data.
- --hypothesis-verbosity: control how much information is reported.
  - `quiet`
  - `normal`
  - `verbose`
  - `debug`

Filter tests by endpoints, methods, and/or tags that match a given endpoint/method/tag pattern.

- -E (--endpoint)
- -M (--method)
- -T (--tag)

Options when generating test data from schema definitions (test data comes from OpenAPI examples by default):

- --hypothesis-derandomize: this flag is used to generate test data deterministically instead of generating random, valid test data.
- --hypothesis-max-examples: this value determines the maximum number of tests to generate for each method. Example: `--hypothesis-max-examples=50`.
- --hypothesis-seed: provide a seed from which random test data will be generated.

## Including Examples in API Definition

Often, a service's requirements are stricter than its schema. For example, an `account_id` may have schema, `type: string`. However, a valid `account_id` is restricted to the set of strings associated with an accounts. For this reason, the default way to generate requests is to use [OpenAPI examples](https://swagger.io/docs/specification/adding-examples/) in the API definition.

### Important Note on Property Examples

Examples for object properties should be provided in an example object rather than on a per-property basis. Hence, for the schema:

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

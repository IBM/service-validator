# schemathesis-endpoint-validator

Extends [Schemathesis](https://github.com/kiwicom/schemathesis) to test [IBM API Handbook](https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-intro) compliance and consistency between an API implementation and its OpenAPI definition.

Issues may be opened [here](https://github.ibm.com/arf/planning-sdk-squad/issues).

## Overview

This tool takes an OpenAPI definition, a valid API endpoint, and any necessary API credentials and verifies that the API implementation complies with its OpenAPI definition and the [IBM API Handbook](https://cloud.ibm.com/docs/api-handbook?topic=api-handbook-intro).

## Install

1. Install Schemathesis globally with `pip install schemathesis`.
2. Clone this repository.

## Use

1. Change your current working directory to the root of this repository (`cd <path to schemathesis-endpoint-validator>`).
2. Run `python3 src/cli/run_schemathesis.py --api-def <path to your API definition> --base-url <base URL of API>`

## Including Examples in API Definition

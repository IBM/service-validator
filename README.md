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

Basic use:

    ibm-service-validator --api-def <path API definition> --base-url <base URL of API>

## Including Examples in API Definition

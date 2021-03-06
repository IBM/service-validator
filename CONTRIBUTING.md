# Contributing

## Bug Reports and Issues

[Issues and bug reports](https://github.com/IBM/service-validator/issues).

## Commits

Commits _must_ follow the [Angular commit message guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines). We use [semantic-release](https://github.com/semantic-release/semantic-release) to release versions to `npm`, update the changelog, etc. Following these guidelines is simplified by using the [Commitizen CLI](https://github.com/commitizen/cz-cli) with the `cz-conventional-changelog` adapter.

## Code

This repository uses [pre-commit](https://pre-commit.com/) to auto-format and lint code. Install this tool to auto-format and lint your code before each commit.

## Install Dependencies

1. Install poetry using the [poetry installation guide](https://python-poetry.org/docs/#installation).

2. Set your current working directory to the root of the project, and run `poetry install` to dowload the dependencies.

## Pull Requests

1. Fork the repository.

2. Run `pre-commit install` to enable the the pre-commit hook (install [pre-commit](https://pre-commit.com/) if you do not already have it). This will run code formatters and linters.

3. Run tests with `tox`:

    tox -e py37

4. Implement and test code.

5. If you have set up `pre-commit`, code formatters and linters will run automatically when you commit. To run the formatters and linters manually:

    pre-commit run --all-files

6. Format commit message according to [Angular commit message guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines).

## Adding an IBM API Handbook Rule

If adding an IBM API Handbook rule, be sure to:

1. Add the default configuration value for the handbook rule to `DEFAULT_CONFIG` in `src/ibm_service_validator/cli/process_config.py`.

2. Add the function to `HANDBOOK_RULES` in `src/ibm_service_validator/handbook_rules/__init__.py`.

## Adding an add_case Hook

If adding an `add_case` hook:

1. Be sure to implement the `add_case` hook in a separate file in `src/ibm_service_validator/handbook_rules/add_case_rules`.

2. Add the `add_case` hook to `ADD_CASE_HOOKS` in `src/ibm_service_validator/handbook_rules/__init__.py`.

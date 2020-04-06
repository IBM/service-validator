import os

import click


@click.command()
@click.option("--api-def", help="Relative path to the API definition to test.")
@click.option("--base-url", help="The base-url of the ")
def run_schemathesis(api_def: str, base_url: str) -> None:
    command = (
        "PYTHONPATH=`pwd` schemathesis --pre-run src.validation_hooks.handbook_rules run %s -c all --base-url %s"
        % (api_def, base_url)
    )
    os.system(command)


if __name__ == "__main__":
    run_schemathesis()

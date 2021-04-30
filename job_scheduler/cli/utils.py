import os
import typing as t

import typer
import yaml
from pygments import formatters, highlight, lexers

DEFAULT_SERVICE_ADDR_ENVVAR = "JOB_SCHEDULER_ENDPOINT"
DEFAULT_SERVICE_ADDR = "http://localhost:8000"


def get_service_addr(envvar=DEFAULT_SERVICE_ADDR_ENVVAR):
    return os.environ.get(envvar, DEFAULT_SERVICE_ADDR)


def json_display(data: t.Dict[str, t.Any]):
    result = yaml.dump(data, allow_unicode=True, sort_keys=True)
    colorized = highlight(
        result, lexers.YamlLexer(ensurenl=False), formatters.TerminalFormatter()
    )
    typer.echo(colorized)

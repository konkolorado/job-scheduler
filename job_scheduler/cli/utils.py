import enum
import json
import os
import typing as t

import requests
import typer
import yaml
from pygments import formatters, highlight, lexers

DEFAULT_SERVICE_ADDR_ENVVAR = "JOB_SCHEDULER_ENDPOINT"
DEFAULT_SERVICE_ADDR = "http://localhost:8000"


def get_service_addr(envvar=DEFAULT_SERVICE_ADDR_ENVVAR):
    return os.environ.get(envvar, DEFAULT_SERVICE_ADDR)


def terminal_display(data: t.Dict[str, t.Any], format: str = "yaml"):
    if format == "json":
        result = json.dumps(data, indent=2, sort_keys=True)
        lexer = lexers.JsonLexer()
    else:
        result = yaml.dump(data, allow_unicode=True, sort_keys=True)
        lexer = lexers.YamlLexer(ensurenl=True)

    colorized = highlight(result, lexer, formatters.TerminalFormatter())
    typer.echo(colorized, nl=False)


class OutputFormatChoices(str, enum.Enum):
    yaml: str = "yaml"
    json: str = "json"


OutputFormatOption = typer.Option("yaml", "--output", "-o", help="Output format")


def resilient_request(
    callable: t.Callable[..., requests.Response], *args, **kwargs
) -> t.Dict[str, t.Any]:
    try:
        response = callable(*args, **kwargs)
    except requests.ConnectionError as ce:
        output = {"error": str(ce)}
    else:
        if response.ok:
            output = response.json()
        else:
            output = {"response": response.text}
    return output

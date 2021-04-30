import typing as t
from urllib.parse import urlparse

import typer
from croniter import croniter


def cron_format_validator(cron_string: str) -> str:
    if not croniter.is_valid(cron_string):
        raise typer.BadParameter("Invalid cron string")
    return cron_string


def payload_validator(payload: t.Optional[t.List[str]]) -> t.Optional[t.List[str]]:
    if payload is None:
        return None
    for p in payload:
        if len(p.split("=")) != 2:
            raise typer.BadParameter("Invalid payload string")
    return payload


def url_validator_callback(url: str) -> str:
    try:
        result = urlparse(url)
        if result.scheme and result.netloc:
            return url
    except:
        pass
    raise typer.BadParameter("Invalid url string")

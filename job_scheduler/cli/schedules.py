import typing as t
import uuid

import requests
import typer

from job_scheduler.cli.callbacks import (
    cron_format_validator,
    payload_validator,
    url_validator_callback,
)
from job_scheduler.cli.utils import get_service_addr, json_display

app = typer.Typer()


@app.command()
def create(
    name: str = typer.Option(..., help="A name for this schedule"),
    description: str = typer.Option(..., help="A description for this schedule"),
    schedule: str = typer.Option(
        ...,
        help="A cron string indicating when to run the schedule",
        callback=cron_format_validator,
    ),
    callback_url: str = typer.Option(
        ..., help="The endpoint to POST the data to", callback=url_validator_callback
    ),
    payload: t.Optional[t.List[str]] = typer.Option(
        None,
        help="The data to POST to the endpoint. The data should be key value pairs, "
        "separated by an '='",
        callback=payload_validator,
    ),
):
    """
    Create a new scheduled job
    """
    if payload:
        parsed_payload = {p.split("=")[0]: p.split("=")[1] for p in payload}
    else:
        parsed_payload = {}

    response = requests.post(
        f"{get_service_addr()}/schedule/",
        json={
            "name": name,
            "description": description,
            "schedule": schedule,
            "job": {
                "callback_url": callback_url,
                "http_method": "post",
                "payload": parsed_payload,
            },
        },
    )
    json_display(response.json())


@app.command()
def view(
    schedule_id: uuid.UUID = typer.Argument(
        ..., help="The ID for the schedule that launched the job(s)"
    )
):
    """
    View the details for a single scheduled job
    """
    endpoint = f"{get_service_addr()}/schedule/{schedule_id}"
    response = requests.get(endpoint)
    json_display(response.json())


@app.command()
def update(
    schedule_id: uuid.UUID = typer.Argument(
        ..., help="The ID for the schedule to update"
    ),
    name: str = typer.Option(..., help="A name for this schedule"),
    description: str = typer.Option(..., help="A description for this schedule"),
    schedule: str = typer.Option(
        ...,
        help="A cron string indicating when to run the schedule",
        callback=cron_format_validator,
    ),
    callback_url: str = typer.Option(
        ..., help="The endpoint to POST the data to", callback=url_validator_callback
    ),
    payload: t.Optional[t.List[str]] = typer.Option(
        None,
        help="The data to POST to the endpoint. The data should be key value pairs, "
        "separated by an '='",
        callback=payload_validator,
    ),
):
    """
    Update details for a scheduled job
    """
    if payload:
        parsed_payload = {p.split("=")[0]: p.split("=")[1] for p in payload}
    else:
        parsed_payload = {}

    response = requests.put(
        f"{get_service_addr()}/schedule/{schedule_id}",
        json={
            "name": name,
            "description": description,
            "schedule": schedule,
            "job": {
                "callback_url": callback_url,
                "http_method": "post",
                "payload": parsed_payload,
            },
        },
    )
    json_display(response.json())


@app.command()
def delete(
    schedule_id: uuid.UUID = typer.Argument(
        ..., help="The ID for the schedule to delete"
    )
):
    """
    Delete a scheduled job
    """
    endpoint = f"{get_service_addr()}/schedule/{schedule_id}"
    response = requests.delete(endpoint)
    json_display(response.json())

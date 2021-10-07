import typing as t
import uuid

import requests
import typer

from job_scheduler.cli.callbacks import (
    cron_format_validator,
    payload_validator,
    url_validator_callback,
)
from job_scheduler.cli.utils import (
    OutputFormatChoices,
    OutputFormatOption,
    get_service_addr,
    resilient_request,
    terminal_display,
)

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
    output_format: OutputFormatChoices = OutputFormatOption,
):
    """
    Create a new scheduled job
    """
    if payload:
        parsed_payload = {p.split("=")[0]: p.split("=")[1] for p in payload}
    else:
        parsed_payload = {}

    output = resilient_request(
        requests.post,
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
    terminal_display(output, output_format)


@app.command()
def view(
    schedule_id: uuid.UUID = typer.Argument(
        ..., help="The ID for the schedule that launched the job(s)"
    ),
    output_format: OutputFormatChoices = OutputFormatOption,
):
    """
    View the details for a single schedule
    """
    endpoint = f"{get_service_addr()}/schedule/{schedule_id}"
    output = resilient_request(requests.get, endpoint)
    terminal_display(output, output_format)


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
    output_format: OutputFormatChoices = OutputFormatOption,
):
    """
    Update details for a scheduled job
    """
    if payload:
        parsed_payload = {p.split("=")[0]: p.split("=")[1] for p in payload}
    else:
        parsed_payload = {}

    output = resilient_request(
        requests.put,
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
    terminal_display(output, output_format)


@app.command()
def delete(
    schedule_id: uuid.UUID = typer.Argument(
        ..., help="The ID for the schedule to delete"
    ),
    output_format: OutputFormatChoices = OutputFormatOption,
):
    """
    Delete a scheduled job
    """
    endpoint = f"{get_service_addr()}/schedule/{schedule_id}"
    output = resilient_request(requests.delete, endpoint)
    terminal_display(output, output_format)

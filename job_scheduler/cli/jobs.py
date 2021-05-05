import typing as t
import uuid

import requests
import typer

from job_scheduler.cli.utils import (
    OutputFormatChoices,
    OutputFormatOption,
    get_service_addr,
    json_display,
)

app = typer.Typer()


@app.command()
def view(
    schedule_id: uuid.UUID = typer.Argument(
        ..., help="The ID for the schedule that launched the job(s)"
    ),
    job_id: t.Optional[uuid.UUID] = typer.Option(
        None, help="A specific job occurence to look up"
    ),
    output_format: OutputFormatChoices = OutputFormatOption,
):
    """
    View jobs associated with a Schedule
    """
    endpoint = f"{get_service_addr()}/schedule/{schedule_id}/jobs"
    if job_id is not None:
        endpoint += f"/{job_id}"

    response = requests.get(endpoint)
    json_display(response.json(), output_format)

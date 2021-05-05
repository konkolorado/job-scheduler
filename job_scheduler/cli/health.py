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
def check(output_format: OutputFormatChoices = OutputFormatOption):
    """
    Run a health check on the JobScheduler service
    """
    endpoint = f"{get_service_addr()}/health"
    response = requests.get(endpoint)
    json_display(response.json(), output_format)

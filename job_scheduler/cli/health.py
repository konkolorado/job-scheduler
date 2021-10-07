import requests
import typer

from job_scheduler.cli.utils import (
    OutputFormatChoices,
    OutputFormatOption,
    get_service_addr,
    resilient_request,
    terminal_display,
)

app = typer.Typer()


@app.command()
def check(output_format: OutputFormatChoices = OutputFormatOption):
    """
    Run a health check on the JobScheduler service
    """
    endpoint = f"{get_service_addr()}/health"
    output = resilient_request(requests.get, endpoint)
    terminal_display(output, output_format)

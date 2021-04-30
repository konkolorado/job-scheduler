import requests
import typer

from job_scheduler.cli.utils import get_service_addr

app = typer.Typer()


@app.command()
def check():
    """
    Run a health check on the JobScheduler service
    """
    endpoint = f"{get_service_addr()}/health"
    response = requests.get(endpoint)
    print(response.json())

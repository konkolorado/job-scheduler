import typer

from job_scheduler.cli import health, jobs, schedules
from job_scheduler.cli.utils import DEFAULT_SERVICE_ADDR, DEFAULT_SERVICE_ADDR_ENVVAR

app = typer.Typer(
    help="A CLI for interfacing with the JobScheduler. To configure the JobScheduler "
    f"endpoint, set the {DEFAULT_SERVICE_ADDR_ENVVAR} environment variable. The default "
    f"endpoint is {DEFAULT_SERVICE_ADDR}."
)

app.add_typer(schedules.app, name="schedules")
app.add_typer(jobs.app, name="jobs")
app.add_typer(health.app, name="health")


if __name__ == "__main__":
    app()

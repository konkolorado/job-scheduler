import logging
import typing as t

from watchgod import arun_process

from job_scheduler.logging import setup_logging

logger = logging.getLogger(__name__)


async def reloader(func: t.Callable):
    """
    Use this function to run the service with file watching - every time a file
    change is detected, the process will reload with the latest changes.
    """
    setup_logging()
    await arun_process(".", func, callback=changes_callback)


async def changes_callback(changes: t.Set):
    logger.warning(f"Changes in {len(changes)} file(s). Reloading...")

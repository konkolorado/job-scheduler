from logging.config import dictConfig

from job_scheduler.logging.config import logging_config


def setup_logging():
    dictConfig(logging_config)

import logging
import logging.config

import structlog

from job_scheduler.config import config

logger = structlog.getLogger(__name__)

pre_chain = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
]
if not config.dev_mode:
    pre_chain.append(structlog.processors.format_exc_info)

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": pre_chain,
        },
        "console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            "foreign_pre_chain": pre_chain,
        },
    },
    "handlers": {
        "default": {
            "level": config.logging.level.upper(),
            "class": "logging.StreamHandler",
            "formatter": config.logging.format.lower(),
        },
    },
    "loggers": {
        "job_scheduler": {
            "handlers": ["default"],
            "propagate": False,
            "level": config.logging.level.upper(),
        },
        "uvicorn": {
            "handlers": ["default"],
            "propagate": False,
            "level": config.logging.level.upper(),
        },
        "burgeon": {
            "handlers": ["default"],
            "propagate": False,
            "level": config.logging.level.upper(),
        },
    },
}


def setup_logging():
    logging.config.dictConfig(logging_config)
    structlog.configure(
        processors=pre_chain
        + [
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger.info(
        "Initialized logging",
        log_level=config.logging.level,
        log_format=config.logging.format,
    )

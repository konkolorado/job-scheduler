logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "job_scheduler.logging.formatters.ColourizedFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": True,
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "job_scheduler": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "api": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "job_runner": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "dummy_endpoint": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {"handlers": ["default"], "level": "INFO"},
}

import environ


@environ.config
class API:
    host = environ.var(default="127.0.0.1")
    port = environ.var(default=8000, converter=int)


@environ.config
class Cache:
    url = environ.var(default="redis://localhost")
    ttl_s = environ.var(default=10, converter=int)


@environ.config
class Broker:
    url = environ.var(default="amqp://localhost")
    queue_name = environ.var(default="jobs")
    prefetch_count = environ.var(default=100, converter=int)
    username = environ.var(default="guest")
    password = environ.var(default="guest")


@environ.config
class DummyService:
    host = environ.var(default="127.0.0.1")
    port = environ.var(default=8000, converter=int)
    sleep = environ.var(default=1, converter=float)


@environ.config
class Logging:
    level = environ.var(default="debug")
    format = environ.var(default="console")

    @level.validator
    def _check_log_level(self, attr, value):
        valid_values = ["debug", "info", "warning"]
        if value.lower() not in valid_values:
            raise ValueError(
                f"Invalid value for {attr}: {value}. Supported values are {valid_values}"
            )

    @format.validator
    def _check_log_format(self, attr, value):
        valid_values = ["console", "json"]
        if value.lower() not in valid_values:
            raise ValueError(
                f"Invalid value for {attr}: {value}. Supported values are {valid_values}"
            )


@environ.config
class AppConfig:
    database_url = environ.var(default="redis://localhost")
    dev_mode = environ.bool_var(default=False)

    api = environ.group(API)
    dummy = environ.group(DummyService)
    broker = environ.group(Broker)
    cache = environ.group(Cache)
    logging = environ.group(Logging)


config = environ.to_config(AppConfig)

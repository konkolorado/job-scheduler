import environ


@environ.config
class API:
    host = environ.var(default="127.0.0.1")
    port = environ.var(default=8000, converter=int)
    loglevel = environ.var(default="debug")


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
    loglevel = environ.var(default="debug")


@environ.config
class AppConfig:
    database_url = environ.var(default="redis://localhost")
    dev_mode = environ.bool_var(default=False)

    api = environ.group(API)
    dummy = environ.group(DummyService)
    broker = environ.group(Broker)


config = environ.to_config(AppConfig)

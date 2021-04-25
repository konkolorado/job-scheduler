import environ


@environ.config
class API:
    host = environ.var(default="127.0.0.1")
    port = environ.var(default=8000, converter=int)
    loglevel = environ.var(default="debug")


@environ.config
class DummyService:
    host = environ.var(default="127.0.0.1")
    port = environ.var(default=8000, converter=int)
    sleep = environ.var(default=1, converter=float)
    loglevel = environ.var(default="debug")


@environ.config
class AppConfig:
    broker_url = environ.var(default="redis://localhost")
    database_url = environ.var(default="redis://localhost")
    dev_mode = environ.bool_var(default=False)

    api = environ.group(API)
    dummy = environ.group(DummyService)


config = environ.to_config(AppConfig)

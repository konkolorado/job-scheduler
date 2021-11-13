FROM python:3.9.6-alpine3.14 as base

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    APP_USER=app

RUN apk update && \
    apk add --no-cache \
    build-base \
    curl \
    just

RUN adduser -S ${APP_USER} 
USER ${APP_USER}

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${PATH}:/home/${APP_USER}/.poetry/bin"

WORKDIR /app
COPY poetry.lock pyproject.toml ./


FROM base as prod

RUN poetry install --no-root --no-dev
COPY README.rst justfile ./
COPY job_scheduler job_scheduler
RUN poetry install --no-dev
CMD ["just api"]


FROM base as dev

RUN poetry install --no-root
COPY README.rst justfile ./
COPY job_scheduler job_scheduler
RUN poetry install
CMD ["just api"]
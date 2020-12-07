FROM python:3.9-alpine

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false \
    APP_USER=app

RUN apk update && \
    apk add --no-cache \
    build-base \
    curl

RUN adduser -S ${APP_USER} 
USER ${APP_USER}

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="${PATH}:/home/${APP_USER}/.poetry/bin"

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev --no-root

ADD job_scheduler job_scheduler
COPY README.rst ./
RUN poetry install --no-dev

ADD Makefile ./
CMD ["make api"]
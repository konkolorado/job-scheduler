.PHONY: help test api scheduler runner local mock

define HELPTEXT
Run "make <target>" where <target> is one of
 help:      to print this message
 test:      to run the full suite of tests
 api:	    to start the API service
 scheduler: to start the job scheduler service
 runner:    to start the job execution service
 dummy:     to start a dummy job endpoint for experimenting
 local:     to start a local stack of services
endef
export HELPTEXT

help:
	@echo "$$HELPTEXT"

test:
	poetry run pytest --cov=job_scheduler

api:
	poetry run python job_scheduler/api/main.py

scheduler:
	poetry run python job_scheduler/scheduler/main.py

runner:
	poetry run python job_scheduler/runner/main.py

local:
	docker-compose up -d

dummy:
	poetry run python job_scheduler/dummy_service/main.py
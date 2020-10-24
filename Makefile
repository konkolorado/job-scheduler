.PHONY: help

define HELPTEXT
Please use "make <target>" where <target> is one of
 help:      to print this message
 test:      to run the full suite of tests
 api:		to start the API service
endef
export HELPTEXT

help:
	@echo "$$HELPTEXT"

test:
	poetry run pytest --cov=job_scheduler

api:
	poetry run python job_scheduler/api/main.py
.PHONY: help test api scheduler runner dummy redis image local cfn stack unstack

PROJECT_VERSION := $(shell poetry version -s)

define HELPTEXT
Run "make <target>" where <target> is one of:
 help:       print this message
 test:       run the full suite of tests
 api:	     start the API service
 scheduler:  start the job scheduler service
 runner:     start the job execution service
 dummy:      start a dummy job endpoint
 redis:	     start a local redis instance
 image:      build the project container image
 local:      start a local stack of services
 cfn:        generate and display the project's Cloudformation
 stack:      deploy the project onto AWS
 unstack:    remove the project from AWS
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

dummy:
	poetry run python job_scheduler/dummy_service/main.py

redis:
	docker run -d --name redis -p 6379:6379 redis:6.0-alpine

image:
	docker build . -t  job-scheduler:$(PROJECT_VERSION) --force-rm

local:
	IMAGE_TAG=$(PROJECT_VERSION) docker compose up

cfn:
	@poetry run cdk synth

stack:
	poetry run cdk deploy JobSchedulerStack --require-approval never
	
unstack:
	poetry run cdk destroy JobSchedulerStack --force
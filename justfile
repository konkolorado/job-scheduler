PROJECT_VERSION := `poetry version -s`

# Display all recipes
default:
  @just --list

# Remove generated files and directories
clean:
    rm -rf .pytest_cache cdk.out .venv .coverage

# Start redis as a dependency
redis:
    docker compose up -d redis

# Start rabbitmq as a dependency
rabbitmq:
    docker compose up -d rabbitmq

# Start local instances of the project's dependencies
deps: rabbitmq redis

# Run tests locally
test:
    poetry run pytest --cov=job_scheduler

# Check for code quality
lint:
    poetry run mypy \
        {{ justfile_directory() }}/job_scheduler \
        {{ justfile_directory() }}/tests \
        {{ justfile_directory() }}/cdk
    poetry run isort --check \
        {{ justfile_directory() }}/job_scheduler \
        {{ justfile_directory() }}/tests \
        {{ justfile_directory() }}/cdk
    poetry run black --check \
        {{ justfile_directory() }}/job_scheduler \
        {{ justfile_directory() }}/tests \
        {{ justfile_directory() }}/cdk 

# Start the API
api:
	poetry run python job_scheduler/api/main.py

# Start the scheduler
scheduler:
	poetry run python job_scheduler/scheduler/main.py

# Start the runner
runner:
	poetry run python job_scheduler/runner/main.py

# Start the dummy endpoint service
dummy:
	poetry run python job_scheduler/dummy_service/main.py

# Build the project's image
image:
	docker build . -t job-scheduler:{{ PROJECT_VERSION }} --force-rm

# Start all services locally
local: image
	IMAGE_TAG={{ PROJECT_VERSION }} docker compose up

# Build and show the synthesized Cloudformation
cfn:
	@poetry run cdk synth

# Deploy the project to AWS
stack:
	poetry run cdk deploy JobSchedulerStack --require-approval never
	
# Remove the project from AWS
unstack:
	poetry run cdk destroy JobSchedulerStack --force

Job-Scheduler
-------------

A job scheduler that supports creating and executing jobs based on a schedule. A
job in the service is a single HTTP operation that can be scheduled to recur on
a CRON schedule.

Job
^^^
A job defines an HTTP operation and a schedule. It is of the following form:

.. code-block::
  :json:

  {
    "name": "CLI",
    "description": "From CLI",
    "schedule": "* * * * *",
    "job": {
      "callback_url": "",
      "http_method": "post",
      "payload": {
      }
    }
  }


Installation
============
There are two ways of installing the service - one geared for local development,
and testing, the other designed to be secure and accessible by anyone on the
internet. 

Local
^^^^^
Local installation relies on `just` and `docker` and `poetry` being installed.

- Build the image that gets used in each of the service components:

.. code-block::
  :shell:

  just image

- Start the service and its dependencies locally:

.. code-block::
  :shell:

  just local

After this, the service API will be available at http://localhost:8000 and jobs
can be submitted and run. This form of installation will install the services in
development mode meaning that if any of the source files' contents change the
service will reload itself to pick up the changes.

AWS
^^^
To deploy on AWS, make sure that the AWS CDK is installed and that the current
shell has an AWS profile activated. The deploy process uses the AWS CDK to build
the app image and deploy its infrastructure. You can view the generated
Cloudformation by:

.. code-block::
  :shell:

  make cfn

And to deploy the project:

.. code-block::
  :shell:

  make stack

The output of the deployment will display the URL at which the job scheduler API
is available. The current implementation of the project will deploy the project
with a personally owned DNS name.

Architecture
============

This service has 3 core components: an API, a scheduler, and a runner. The API
is the only user-facing component and handles all job CRUD operations with the
Redis database. The scheduler determines which schedules should be run at any
given  moment my maintaining a priority queue. The runner executes the
schedules. A RabbitMQ job queue sits between the scheduler and the broker
allowing scheduling and running to happen independently of each other. The
scheduler only concerns itself with placing schedules which need to run on the
queue and the runner only concerns itself with reading jobs from the queue and
running them. The scheduler uses a Redis cache to deduplicate jobs that get
placed on the job queue to prevent a slow job update from causing it to execute
multiple times. The runner pulls multiple jobs from the job queue and runs those
using asyncio coroutines with a strict timeout so that slow running jobs don't
bog the system down.

- Consider the Architecture based on how AWS handles auto scaling services
- Try out miro to display this
- Do something cool with instrumentation + logs + dashboards
  - investigate using prometheus to do this
    - https://aws.amazon.com/prometheus/resources/?msg-blogs.sort-by=item.additionalFields.createdDate&msg-blogs.sort-order=desc
- experiment w/ a cdktf
- use PGSQL for DB
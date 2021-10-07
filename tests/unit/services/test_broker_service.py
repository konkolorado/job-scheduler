import random

import pytest

from job_scheduler.broker import FakeBroker, ScheduleBroker
from job_scheduler.services import ack_jobs, dequeue_jobs, enqueue_jobs


@pytest.fixture(scope="session")
async def broker():
    return await FakeBroker.get_broker()


async def test_schedules_enqueued(n_schedules, broker: ScheduleBroker):
    QUEUE_SIZE = random.randint(1, 100)
    schedules = n_schedules(QUEUE_SIZE)

    await enqueue_jobs(broker, *schedules)

    enqueued = await broker.drain()
    enqueued_ids = {e.payload for e in enqueued}

    assert len(enqueued) == QUEUE_SIZE
    for s in schedules:
        assert str(s.id) in enqueued_ids


async def test_schedules_dequeued(n_schedules, broker: ScheduleBroker):
    QUEUE_SIZE = random.randint(1, 100)
    schedules = n_schedules(QUEUE_SIZE)

    await enqueue_jobs(broker, *schedules)

    dequeued = await dequeue_jobs(broker)
    dequeued_ids = {d.payload for d in dequeued}

    assert len(dequeued) == len(schedules)
    for s in schedules:
        assert str(s.id) in dequeued_ids


async def test_schedules_acked(n_schedules, broker: ScheduleBroker):
    QUEUE_SIZE = random.randint(1, 100)
    schedules = n_schedules(QUEUE_SIZE)
    await enqueue_jobs(broker, *schedules)
    dequeued = await dequeue_jobs(broker)
    await ack_jobs(broker, *dequeued)

    # Add 1 schedule so that get doesn't block
    await enqueue_jobs(broker, schedules[0])
    dequeued = await broker.drain()

    assert len(dequeued) == 1

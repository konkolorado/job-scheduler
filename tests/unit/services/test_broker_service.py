import pytest

from job_scheduler.broker import FakeBroker, ScheduleBroker
from job_scheduler.services import ack_jobs, dequeue_jobs, enqueue_jobs


@pytest.fixture(scope="session")
def broker():
    return FakeBroker.get_broker()


async def test_schedules_enqueued(n_schedules, broker: ScheduleBroker):
    schedules = n_schedules(3)

    size_before = await broker.size
    await enqueue_jobs(broker, *schedules)

    enqueued = await broker.drain()

    assert await broker.size == size_before + len(schedules)
    for s in schedules:
        assert str(s.id) in enqueued


async def test_duplicate_schedules_not_enqeued(n_schedules, broker: ScheduleBroker):
    schedules = n_schedules(3)
    schedules *= 2

    size_before = await broker.size
    await enqueue_jobs(broker, *schedules)
    assert await broker.size == size_before + (len(schedules) / 2)

    enqueued = await broker.drain()
    assert len(enqueued) == len(schedules) / 2
    for s in schedules:
        assert str(s.id) in enqueued


async def test_schedules_dequeued(n_schedules, broker: ScheduleBroker):
    schedules = n_schedules(3)
    await enqueue_jobs(broker, *schedules)

    size_before = await broker.size
    dequeued = await dequeue_jobs(broker)

    assert await broker.size == size_before
    assert len(dequeued) == len(schedules)
    for s in schedules:
        assert s.id in dequeued


async def test_schedules_acked(n_schedules, broker: ScheduleBroker):
    schedules = n_schedules(3)

    size_before = await broker.size
    await enqueue_jobs(broker, *schedules)
    dequeued = await dequeue_jobs(broker)
    await ack_jobs(broker, *schedules)

    assert await broker.size == size_before

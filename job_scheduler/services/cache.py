import typing as t

from job_scheduler.api.models import Schedule
from job_scheduler.cache.base import ScheduleCache


async def diff_from_cache(c: ScheduleCache, *schedules: Schedule) -> t.List[Schedule]:
    """
    Given a cache and a list of Schedules, returns only those schedules which
    are not in the cache.
    """
    sid_to_schedule = {str(s.id): s for s in schedules}
    results = await c.get(*sid_to_schedule.keys())
    for r in results:
        if r is not None:
            sid_to_schedule.pop(r)
    return list(sid_to_schedule.values())


async def add_to_cache(c: ScheduleCache, *schedules: Schedule) -> None:
    await c.add(*(str(s.id) for s in schedules))

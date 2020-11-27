from job_scheduler.broker.base import ScheduleBroker


class FakeBroker(ScheduleBroker):
    @classmethod
    def get_broker(cls):
        return cls()

    @classmethod
    def shutdown(cls):
        pass

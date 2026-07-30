
from datetime import datetime
from application.ports.clock import Clock

class FakeClock(Clock):
    def __init__(self, fixed_time: datetime):
        self._time = fixed_time

    def now(self) -> datetime:
        return self._time

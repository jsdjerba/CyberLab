
from application.ports.delay_provider import DelayProvider

class FakeDelayProvider(DelayProvider):
    def __init__(self):
        self.sleep_calls = []

    def sleep(self, seconds: float) -> None:
        self.sleep_calls.append(seconds)

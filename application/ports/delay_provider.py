
from typing import Protocol

class DelayProvider(Protocol):
    def sleep(self, seconds: float) -> None:
        ...

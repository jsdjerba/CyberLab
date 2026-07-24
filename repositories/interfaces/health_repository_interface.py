from typing import Protocol

class IHealthRepository(Protocol):
    def ping(self) -> bool:
        ...
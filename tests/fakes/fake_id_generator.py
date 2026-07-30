
from application.ports.id_generator import IdGenerator

class FakeIdGenerator(IdGenerator):
    def __init__(self):
        self._counter = 0

    def generate(self) -> str:
        self._counter += 1
        return f"id-{self._counter}"

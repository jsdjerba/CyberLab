from enum import Enum

class Level(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4

    @classmethod
    def from_str(cls, value: str) -> 'Level':
        if isinstance(value, Level):
            return value
        cleaned = value.strip().upper()
        try:
            return cls[cleaned]
        except KeyError:
            return cls.BEGINNER

    def __ge__(self, other: 'Level') -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value >= other.value

    def __gt__(self, other: 'Level') -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value > other.value

    def __le__(self, other: 'Level') -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value <= other.value

    def __lt__(self, other: 'Level') -> bool:
        if not isinstance(other, Level):
            return NotImplemented
        return self.value < other.value
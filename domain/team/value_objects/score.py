from dataclasses import dataclass
from domain.team.exceptions.team_exceptions import NegativeScoreException, InvalidPointsException

@dataclass(frozen=True)
class Score:
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise NegativeScoreException("Score cannot be negative.")

    def add(self, points: int) -> 'Score':
        if points <= 0:
            raise InvalidPointsException("Points to add must be strictly positive.")
        return Score(self.value + points)

    def subtract(self, points: int) -> 'Score':
        if points <= 0:
            raise InvalidPointsException("Points to subtract must be strictly positive.")
        if self.value - points < 0:
            raise NegativeScoreException("Subtraction would result in a negative score.")
        return Score(self.value - points)
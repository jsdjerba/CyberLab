from application.labs.interfaces.flag_validator import FlagValidator
from domain.labs.entities.step import Step

class FakeFlagValidator(FlagValidator):
    def __init__(self, expected_flag: str):
        self.expected_flag = expected_flag

    def validate(self, step: Step, submitted_flag: str) -> bool:
        return submitted_flag == self.expected_flag
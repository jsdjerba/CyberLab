from domain.value_objects.team_id import TeamId
from domain.value_objects.student_id import StudentId
from domain.enums.team_type import TeamType

class Team:
    def __init__(self, team_id: TeamId, name: str, team_type: TeamType):
        self.team_id = team_id
        self.name = name
        self.team_type = team_type
        self.members: set[StudentId] = set()

    def add_member(self, student_id: StudentId):
        self.members.add(student_id)

    def remove_member(self, student_id: StudentId):
        self.members.discard(student_id)
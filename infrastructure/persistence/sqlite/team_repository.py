# infrastructure/persistence/sqlite/team_repository.py
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from domain.team.aggregate import Team
from domain.team.value_objects.team_id import TeamId
from domain.team.value_objects.classroom_id import ClassroomId
from domain.team.value_objects.team_color import TeamColor
from domain.team.value_objects.score import Score
from domain.team.entities.team_member import TeamMember
from domain.team.value_objects.student_id import StudentId
from domain.team.value_objects.team_role import TeamRole

from infrastructure.persistence.sqlite.models import TeamModel, TeamMemberModel

class SqlAlchemyTeamRepository:
    """
    Adaptateur Infrastructure pour le Command Side (Write Model).
    Traduit l'état persistant SQLAlchemy <-> Agrégat Team du Domaine.
    """
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, team_id: str) -> Optional[Team]:
        team_model = self._session.get(TeamModel, team_id)
        if not team_model:
            return None

        member_models = self._session.query(TeamMemberModel).filter_by(team_id=team_id).all()

        team = Team(
            team_id=TeamId(team_model.id),
            classroom_id=ClassroomId(team_model.classroom_id),
            color=TeamColor(team_model.color),
            max_size=team_model.max_size
        )
        
        if hasattr(team, 'score'):
            team.score = Score(team_model.score)

        for m in member_models:
            team.add_member(
                student_id=StudentId(m.student_id),
                role=TeamRole(m.role),
                current_time=m.joined_at,
                event_id=f"hydration-{m.id}"
            )
            team.pull_events()

        return team

    def save(self, team: Team) -> None:
        team_model = self._session.get(TeamModel, team.id.value)
        now = datetime.now()
        
        team_score = team.score.value if hasattr(team, 'score') and hasattr(team.score, 'value') else getattr(team, 'score', 0)

        if not team_model:
            team_model = TeamModel(
                id=team.id.value,
                classroom_id=team.classroom_id.value,
                color=team.color.value,
                score=team_score,
                max_size=team.max_size,
                created_at=now,
                updated_at=now
            )
            self._session.add(team_model)
        else:
            team_model.color = team.color.value
            team_model.score = team_score
            team_model.max_size = team.max_size
            team_model.updated_at = now

        existing_members = self._session.query(TeamMemberModel).filter_by(team_id=team.id.value).all()
        existing_map = {m.student_id: m for m in existing_members}
        
        # Correction : team.members est un dictionnaire {student_id: TeamMember}
        domain_map = {}
        for s_id, entity in team.members.items():
            s_id_str = s_id.value if hasattr(s_id, 'value') else str(s_id)
            domain_map[s_id_str] = entity

        # Suppression des membres absents dans l'agrégat domaine
        for student_id, model in existing_map.items():
            if student_id not in domain_map:
                self._session.delete(model)

        # Ajout ou mise à jour des membres présents dans l'agrégat domaine
        for student_id, entity in domain_map.items():
            if student_id in existing_map:
                model = existing_map[student_id]
                model.role = entity.role.value if hasattr(entity.role, 'value') else str(entity.role)
            else:
                new_model = TeamMemberModel(
                    id=f"mem-{student_id}",
                    team_id=team.id.value,
                    student_id=student_id,
                    role=entity.role.value if hasattr(entity.role, 'value') else str(entity.role),
                    joined_at=entity.joined_at
                )
                self._session.add(new_model)
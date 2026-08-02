from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from application.dto.leaderboard_response import LeaderboardResponseDTO, LeaderboardItemDTO
from application.dto.team_details_response import TeamDetailsDTO, TeamMemberDTO
from infrastructure.persistence.sqlite.models import TeamModel, TeamMemberModel

class SqlAlchemyTeamQueryRepository:
    """
    Adaptateur Infrastructure pour le CQRS Read Side.
    Utilise SQLAlchemy Core pour contourner totalement l'Agrégat et projeter vers des DTOs.
    """
    def __init__(self, session: Session):
        self._session = session

    def get_leaderboard(self, classroom_id: str) -> LeaderboardResponseDTO:
        # Requête SQL Core : SELECT teams & COUNT(team_members) GROUP BY teams.id ORDER BY score DESC
        stmt = (
            select(
                TeamModel.id,
                TeamModel.color,
                TeamModel.score,
                func.count(TeamMemberModel.id).label("members_count")
            )
            .outerjoin(TeamMemberModel, TeamModel.id == TeamMemberModel.team_id)
            .where(TeamModel.classroom_id == classroom_id)
            .group_by(TeamModel.id)
            .order_by(TeamModel.score.desc())
        )

        rows = self._session.execute(stmt).all()

        items = []
        for index, row in enumerate(rows, start=1):
            items.append(
                LeaderboardItemDTO(
                    team_id=row.id,
                    color=row.color,
                    score=row.score,
                    rank=index,  # Calcul du rang à la volée
                    members_count=row.members_count
                )
            )

        return LeaderboardResponseDTO(
            classroom_id=classroom_id,
            leaderboard=items
        )

    def get_team_details(self, team_id: str, classroom_id: str) -> Optional[TeamDetailsDTO]:
        # Protection anti-IDOR : Filtrage strict par team_id ET classroom_id simultanément
        team_stmt = select(TeamModel).where(
            TeamModel.id == team_id,
            TeamModel.classroom_id == classroom_id
        )
        team_model = self._session.execute(team_stmt).scalar_one_or_none()

        if not team_model:
            return None

        member_stmt = select(TeamMemberModel).where(TeamMemberModel.team_id == team_id)
        member_models = self._session.execute(member_stmt).scalars().all()

        member_dtos = [
            TeamMemberDTO(
                student_id=m.student_id,
                role=m.role,
                joined_at=m.joined_at
            )
            for m in member_models
        ]

        return TeamDetailsDTO(
            team_id=team_model.id,
            classroom_id=team_model.classroom_id,
            color=team_model.color,
            score=team_model.score,
            members=member_dtos
        )
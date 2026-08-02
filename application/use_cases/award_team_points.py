from application.commands.award_team_points_command import AwardTeamPointsCommand
from application.dto.team_mutation_response import TeamMutationResponseDTO
from application.exceptions.team_application_exceptions import TeamNotFoundApplicationException
from application.ports.team_repository import TeamRepository
from application.ports.clock import Clock
from application.ports.id_generator import IdGenerator
from application.ports.unit_of_work import UnitOfWork
from application.resilience.retry_policy import RetryPolicy

class AwardTeamPointsUseCase:
    def __init__(self, repository: TeamRepository, clock: Clock, id_generator: IdGenerator, unit_of_work: UnitOfWork, retry_policy: RetryPolicy):
        self._repo, self._clock, self._id_gen, self._uow, self._retry_policy = repository, clock, id_generator, unit_of_work, retry_policy

    def execute(self, command: AwardTeamPointsCommand) -> TeamMutationResponseDTO:
        team = self._repo.find_by_id(command.team_id)
        if not team:
            raise TeamNotFoundApplicationException(f"Team {command.team_id} not found.")

        event_id = self._id_gen.generate()
        
        team.award_points(
            points=command.points,
            reason=command.reason,
            current_time=self._clock.now(),
            event_id=event_id
        )
        
        events = team.pull_events()
        
        def persist():
            with self._uow:
                self._repo.save(team)
                self._uow.register_events(events)
                self._uow.commit()

        self._retry_policy.execute(persist)
        
        return TeamMutationResponseDTO(team_id=team.id.value, event_id=event_id, status="SUCCESS")
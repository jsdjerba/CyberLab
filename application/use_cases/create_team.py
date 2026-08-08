from application.commands.create_team_command import CreateTeamCommand
from application.dto.team_mutation_response import TeamMutationResponseDTO
from application.ports.team_repository import TeamRepository
from application.ports.clock import Clock
from application.ports.id_generator import IdGenerator
from application.ports.unit_of_work import UnitOfWork
from application.resilience.retry_policy import RetryPolicy

from domain.team.aggregate import Team
from domain.team.value_objects.team_id import TeamId
from domain.team.value_objects.classroom_id import ClassroomId

class CreateTeamUseCase:
    def __init__(self, repository: TeamRepository, clock: Clock, id_generator: IdGenerator, unit_of_work: UnitOfWork, retry_policy: RetryPolicy):
        self._repo = repository
        self._clock = clock
        self._id_gen = id_generator
        self._uow = unit_of_work
        self._retry_policy = retry_policy

    def execute(self, command: CreateTeamCommand) -> TeamMutationResponseDTO:
        team_id = self._id_gen.generate()
        event_id = self._id_gen.generate()
        
        # Le cast est déjà géré par la frontière HTTP. On passe directement 'command.color'
        team = Team.create(
            team_id=TeamId(team_id),
            classroom_id=ClassroomId(command.classroom_id),
            color=command.color,
            max_size=command.max_size,
            current_time=self._clock.now(),
            event_id=event_id
        )
        
        events = team.pull_events()
        
        def persist():
            with self._uow:
                self._repo.save(team)
                self._uow.register_events(events)
                self._uow.commit()

        # Indentation corrigée : l'exécution se fait au niveau de execute()
        self._retry_policy.execute(persist)
        
        return TeamMutationResponseDTO(team_id=team_id, event_id=event_id, status="SUCCESS")
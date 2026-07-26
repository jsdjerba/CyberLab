import pytest
from dataclasses import FrozenInstanceError

from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.entities.lab_instance import LabInstance

from application.commands.start_lab_command import StartLabCommand
from application.commands.submit_flag_command import SubmitFlagCommand
from application.dtos.step_result_dto import StepResultDto
from application.dtos.lab_result_dto import LabResultDto
from application.dtos.achievement_dto import AchievementDto
from application.mappers.domain_to_dto import DomainToDtoMapper
from domain.exceptions import LabInstanceNotFoundError, LabNotFoundError, StudentNotFoundError

from application.use_cases.submit_flag_use_case import SubmitFlagUseCase

def test_commands_immutability():
    start_cmd = StartLabCommand(student_id=StudentId(1), lab_id=LabId("L1"))
    submit_cmd = SubmitFlagCommand(instance_id="inst_1", step_id=StepId("s1"), submitted_flag="FLAG{test}")

    with pytest.raises(FrozenInstanceError):
        start_cmd.lab_id = LabId("L2") # type: ignore
    with pytest.raises(FrozenInstanceError):
        submit_cmd.submitted_flag = "FLAG{other}" # type: ignore

def test_application_exceptions():
    assert isinstance(LabNotFoundError("L1"), Exception)
    assert isinstance(LabInstanceNotFoundError("i1"), Exception)
    assert isinstance(StudentNotFoundError("s1"), Exception)

def test_domain_to_dto_mapper():
    instance = LabInstance(id="inst_1", lab_id=LabId("L1"), student_id=StudentId(1))
    instance.is_finished = True
    instance.score = 100

    dto = DomainToDtoMapper.to_lab_result_dto(instance)
    assert isinstance(dto, LabResultDto)
    assert dto.instance_id == "inst_1"
    assert dto.score == 100
    assert dto.is_finished is True

def test_submit_flag_use_case_skeleton_raises_not_found():
    class DummyLabRepo:
        def get_by_id(self, lab_id): return None
    class DummyInstanceRepo:
        def get_by_id(self, instance_id): return None
    class DummyStudentRepo:
        def get_history(self, student_id): return None
    class DummyEventBus:
        def publish(self, events): pass

    use_case = SubmitFlagUseCase(
        lab_repository=DummyLabRepo(), # type: ignore
        lab_instance_repository=DummyInstanceRepo(), # type: ignore
        student_repository=DummyStudentRepo(), # type: ignore
        event_bus=DummyEventBus(), # type: ignore
        attempt_policy_service=None, # type: ignore
        challenge_validation_port=None, # type: ignore
        scoring_service=None, # type: ignore
        achievement_service=None # type: ignore
    )

    command = SubmitFlagCommand(instance_id="unknown", step_id=StepId("s1"), submitted_flag="FLAG{}")
    with pytest.raises(LabInstanceNotFoundError):
        use_case.execute(command)
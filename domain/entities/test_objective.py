import pytest

from domain.entities.objective import Objective
from domain.value_objects.objective_id import ObjectiveId


def test_objective_creation_with_valid_values():
    """Vérifie la création correcte avec ses Value Objects et invariants validés."""
    obj_id = ObjectiveId("obj-1")
    objective = Objective(objective_id=obj_id, score_weight=50)
    
    assert objective.objective_id == obj_id
    assert objective.score_weight == 50
    assert objective.is_completed is False


def test_objective_rejects_primitive_objective_id():
    """Anti-Primitive Obsession : Rejette les chaînes brutes pour l'identifiant."""
    with pytest.raises(ValueError, match="objective_id doit être une instance stricte de ObjectiveId"):
        Objective(objective_id="obj-1", score_weight=10)


def test_objective_rejects_negative_score():
    """Valide l'invariant métier du score positif ou nul."""
    with pytest.raises(ValueError, match="score_weight ne peut pas être négatif"):
        Objective(objective_id=ObjectiveId("obj-1"), score_weight=-10)


@pytest.mark.parametrize("invalid_state", [1, 0, "True", None])
def test_objective_requires_boolean_completion_state(invalid_state):
    """Garantit que le statut de complétion est purement booléen."""
    with pytest.raises(ValueError, match="is_completed doit être un booléen strict"):
        Objective(objective_id=ObjectiveId("obj-1"), score_weight=10, is_completed=invalid_state)


def test_objective_complete_changes_state():
    """Vérifie l'encapsulation de la mutation d'état via l'API métier."""
    objective = Objective(objective_id=ObjectiveId("obj-1"), score_weight=10)
    assert objective.is_completed is False
    
    objective.complete()
    assert objective.is_completed is True


def test_objective_complete_is_idempotent():
    """Vérifie qu'appeler multiple fois la complétion ne cause pas d'effets de bord."""
    objective = Objective(objective_id=ObjectiveId("obj-1"), score_weight=10)
    
    objective.complete()
    objective.complete()
    
    assert objective.is_completed is True


def test_objective_entity_equality_uses_identity_only():
    """
    DDD Contract : Deux entités sont égales si leur identité est égale,
    peu importe leurs attributs mutables (score ou complétion).
    """
    obj1 = Objective(objective_id=ObjectiveId("obj-root"), score_weight=10, is_completed=False)
    obj2 = Objective(objective_id=ObjectiveId("obj-root"), score_weight=50, is_completed=True)
    obj3 = Objective(objective_id=ObjectiveId("obj-other"), score_weight=10, is_completed=False)
    
    assert obj1 == obj2
    assert obj1 != obj3


def test_objective_slots_prevent_dynamic_attributes():
    """Sécurité Anti-Leak : Vérifie qu'il est impossible d'injecter des données sensibles (slots=True)."""
    objective = Objective(objective_id=ObjectiveId("obj-1"), score_weight=10)
    
    with pytest.raises(AttributeError):
        objective.fake_secret = "CTF{secret}"
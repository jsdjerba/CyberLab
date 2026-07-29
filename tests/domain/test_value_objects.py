import pytest
from datetime import timedelta
from dataclasses import FrozenInstanceError

from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.attempt_id import AttemptId
from domain.value_objects.correlation_id import CorrelationId
from domain.value_objects.flag_hash import FlagHash
from domain.value_objects.completion_time import CompletionTime


# ==============================================================================
# INTENTION MÉTIER : IDENTIFIANTS DU DOMAINE (IDs)
# ==============================================================================

class TestDomainIdentifiers:
    
    @pytest.mark.parametrize("id_class", [StudentId, LabId, ObjectiveId, AttemptId])
    def test_identifiers_can_be_created_with_valid_values(self, id_class):
        """Vérifie que les identifiants acceptent des chaînes valides."""
        valid_val = "valid-id-1234"
        vo = id_class(value=valid_val)
        assert vo.value == valid_val

    @pytest.mark.parametrize("id_class", [StudentId, LabId, ObjectiveId, AttemptId])
    @pytest.mark.parametrize("invalid_val", ["", "   ", None])
    def test_identifiers_reject_empty_or_whitespace_values(self, id_class, invalid_val):
        """Vérifie la protection contre les identifiants vides ou nuls."""
        with pytest.raises(ValueError, match="ne peut pas être vide"):
            id_class(value=invalid_val)

    @pytest.mark.parametrize("id_class", [StudentId, LabId, ObjectiveId, AttemptId])
    def test_identifiers_are_immutable(self, id_class):
        """Garantit qu'un identifiant ne peut pas muter après sa création."""
        vo = id_class(value="immutable-id")
        with pytest.raises(FrozenInstanceError):
            vo.value = "new-id"

    @pytest.mark.parametrize("id_class", [StudentId, LabId, ObjectiveId, AttemptId])
    def test_identifiers_equality_is_by_value(self, id_class):
        """Garantit l'égalité par valeur, essentielle pour les Value Objects."""
        id1 = id_class(value="same-id")
        id2 = id_class(value="same-id")
        id3 = id_class(value="different-id")
        
        assert id1 == id2
        assert id1 != id3


# ==============================================================================
# INTENTION MÉTIER : CORRELATION ID
# ==============================================================================

class TestCorrelationId:

    def test_correlation_id_accepts_valid_string(self):
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        correlation = CorrelationId(value=valid_uuid)
        assert correlation.value == valid_uuid

    @pytest.mark.parametrize("invalid_val", ["", "   ", None])
    def test_correlation_id_rejects_empty_values(self, invalid_val):
        with pytest.raises(ValueError, match="ne peut pas être vide"):
            CorrelationId(value=invalid_val)

    def test_correlation_id_is_immutable(self):
        correlation = CorrelationId(value="req-uuid")
        with pytest.raises(FrozenInstanceError):
            correlation.value = "new-req"


# ==============================================================================
# INTENTION MÉTIER : FLAG HASH (SÉCURITÉ CRITIQUE)
# ==============================================================================

class TestFlagHash:

    def test_flag_hash_accepts_valid_hash(self):
        """Un hash bcrypt ou sha256 valide doit être accepté."""
        valid_hash = "$2b$12$KIXeW.CUKZc2Vf5WvL7.7OniR.t0C2x7Z2aA4iFzYd.Q5U5X8b5wO"
        flag = FlagHash(value=valid_hash)
        assert flag.value == valid_hash

    def test_flag_hash_rejects_plaintext_flag(self):
        """Bloque catégoriquement toute tentative d'instancier un flag en clair."""
        with pytest.raises(ValueError, match="Le hash ne peut pas contenir un flag en clair"):
            FlagHash(value="CTF{secret_password_123}")

    @pytest.mark.parametrize("invalid_val", ["", "   ", None])
    def test_flag_hash_rejects_empty_values(self, invalid_val):
        with pytest.raises(ValueError, match="Le hash ne peut pas être vide"):
            FlagHash(value=invalid_val)

    def test_flag_hash_is_immutable(self):
        flag = FlagHash(value="valid-hash")
        with pytest.raises(FrozenInstanceError):
            flag.value = "new-hash"


# ==============================================================================
# INTENTION MÉTIER : COMPLETION TIME
# ==============================================================================

class TestCompletionTime:

    def test_completion_time_accepts_valid_duration(self):
        """Accepte une durée positive (ex: 2 heures et 15 minutes)."""
        duration = timedelta(hours=2, minutes=15)
        completion = CompletionTime(duration=duration)
        assert completion.duration == duration

    def test_completion_time_accepts_zero_duration(self):
        """Règle métier validée par le comité : la durée de 0s est autorisée (gérée par AntiCheat)."""
        completion = CompletionTime(duration=timedelta(seconds=0))
        assert completion.duration.total_seconds() == 0

    def test_completion_time_rejects_negative_duration(self):
        """Le temps ne recule pas : rejette les durées négatives."""
        with pytest.raises(ValueError, match="La durée ne peut pas être négative"):
            CompletionTime(duration=timedelta(minutes=-5))

    def test_completion_time_is_immutable(self):
        completion = CompletionTime(duration=timedelta(minutes=10))
        with pytest.raises(FrozenInstanceError):
            completion.duration = timedelta(minutes=20)
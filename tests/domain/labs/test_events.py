import pytest
from datetime import datetime, timezone
from dataclasses import FrozenInstanceError
from domain.labs.events.lab_started import LabStarted

def test_domain_event_timestamp():
    event = LabStarted(lab_instance_id="123")
    assert isinstance(event.timestamp, datetime)
    assert event.timestamp.tzinfo == timezone.utc

def test_event_immutability():
    event = LabStarted(lab_instance_id="123")
    with pytest.raises(FrozenInstanceError):
        event.lab_instance_id = "456"
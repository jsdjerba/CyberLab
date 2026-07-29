import pytest
from dataclasses import dataclass
from domain.common.aggregate_root import AggregateRoot

@dataclass(frozen=True)
class DummyEvent:
    aggregate_id: str

class DummyAggregate(AggregateRoot):
    def __init__(self, aggregate_id: str):
        super().__init__()
        self.aggregate_id = aggregate_id
        self.state = "INITIAL"

    def do_something_valid(self):
        self.state = "UPDATED"
        self.register_event(DummyEvent(aggregate_id=self.aggregate_id))

    def do_something_invalid(self):
        # Invariant violé : lève une exception et ne doit pas émettre d'événement
        raise ValueError("État invalide")

def test_aggregate_root_registers_and_collects_events():
    aggregate = DummyAggregate("agg-123")
    assert aggregate.collect_events() == []

    aggregate.do_something_valid()
    events = aggregate.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], DummyEvent)
    assert events[0].aggregate_id == "agg-123"

    # Vérifie que collect_events vide la liste (ou clear_events)
    aggregate.clear_events()
    assert aggregate.collect_events() == []

def test_domain_invariant_prevents_event_creation_on_failure():
    aggregate = DummyAggregate("agg-456")
    
    with pytest.raises(ValueError):
        aggregate.do_something_invalid()

    # Aucun événement ne doit être enregistré suite à l'échec de la mutation
    assert aggregate.collect_events() == []
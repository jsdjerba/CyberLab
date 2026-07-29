import pytest
from infrastructure.bus.in_memory_event_bus import InMemoryEventBus
from application.ports.event_handler import AbstractEventHandler
from dataclasses import dataclass

@dataclass(frozen=True)
class SampleEvent:
    message: str

class MockHandler(AbstractEventHandler):
    def __init__(self):
        self.handled_events = []

    def handle(self, event) -> None:
        self.handled_events.append(event)

class FaultyHandler(AbstractEventHandler):
    def handle(self, event) -> None:
        raise RuntimeError("Erreur critique dans le handler")

def test_event_bus_subscribes_and_publishes():
    bus = InMemoryEventBus()
    handler = MockHandler()
    
    bus.subscribe(SampleEvent, handler)
    event = SampleEvent(message="Bonjour CyberLab")
    
    bus.publish(event)
    
    assert len(handler.handled_events) == 1
    assert handler.handled_events[0].message == "Bonjour CyberLab"

def test_event_bus_isolates_handler_exceptions():
    bus = InMemoryEventBus()
    faulty_handler = FaultyHandler()
    healthy_handler = MockHandler()

    bus.subscribe(SampleEvent, faulty_handler)
    bus.subscribe(SampleEvent, healthy_handler)

    event = SampleEvent(message="Test isolation")
    
    # Ne doit pas lever l'exception du faulty_handler grâce à l'isolation try/except
    bus.publish(event)

    # Le handler sain doit quand même avoir reçu l'événement
    assert len(healthy_handler.handled_events) == 1
    assert healthy_handler.handled_events[0].message == "Test isolation"
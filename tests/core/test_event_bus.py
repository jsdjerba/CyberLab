import pytest
import logging
from dataclasses import dataclass
from domain.events.event import DomainEvent
from core.events.event_bus import EventBus
from core.events.event_handler import IEventHandler
from core.events.exceptions import EventProcessingError, HandlerNotFound

# --- Mocks ---
@dataclass(frozen=True)
class DummyEvent(DomainEvent):
    data: str

@dataclass(frozen=True)
class BadgeUnlockedEvent(DomainEvent):
    badge_id: str

class DummyHandler(IEventHandler):
    def __init__(self):
        self.received = []
    def handle(self, event: DomainEvent) -> None:
        self.received.append(event)

class FailingHandler(IEventHandler):
    def handle(self, event: DomainEvent) -> None:
        raise ValueError("Simulated DB Crash")

# --- Tests ---
def test_domain_event_auto_fields():
    event = DummyEvent("test")
    assert event.event_id is not None
    assert event.occurred_at is not None

def test_register_and_public_api():
    bus = EventBus()
    handler = DummyHandler()
    bus.register(DummyEvent, handler)
    
    assert bus.get_handler_count(DummyEvent) == 1
    assert bus.has_handler(DummyEvent, handler) is True

def test_double_register():
    bus = EventBus()
    handler = DummyHandler()
    
    bus.register(DummyEvent, handler)
    bus.register(DummyEvent, handler)  # Tentative de doublon
    
    assert bus.get_handler_count(DummyEvent) == 1
    
    bus.publish(DummyEvent("test"))
    assert len(handler.received) == 1  # Exécuté une seule fois

def test_unregister_existing_and_non_existent():
    bus = EventBus()
    handler = DummyHandler()
    
    bus.register(DummyEvent, handler)
    bus.unregister(DummyEvent, handler)
    
    assert bus.get_handler_count(DummyEvent) == 0
    
    # Ne doit pas lever d'exception
    bus.unregister(DummyEvent, handler)

def test_clear_handlers_and_publish():
    bus = EventBus(strict=False)
    handler = DummyHandler()
    bus.register(DummyEvent, handler)
    
    bus.clear_handlers()
    assert bus.get_handler_count(DummyEvent) == 0
    
    # Doit ignorer silencieusement car strict=False
    bus.publish(DummyEvent("test"))
    assert len(handler.received) == 0

def test_independent_event_types():
    bus = EventBus()
    dummy_handler = DummyHandler()
    badge_handler = DummyHandler()
    
    bus.register(DummyEvent, dummy_handler)
    bus.register(BadgeUnlockedEvent, badge_handler)
    
    bus.publish(DummyEvent("test"))
    bus.publish(BadgeUnlockedEvent("CYBER_MASTER"))
    
    assert len(dummy_handler.received) == 1
    assert isinstance(dummy_handler.received[0], DummyEvent)
    
    assert len(badge_handler.received) == 1
    assert isinstance(badge_handler.received[0], BadgeUnlockedEvent)

def test_handler_exception():
    bus = EventBus()
    bus.register(DummyEvent, FailingHandler())
    
    with pytest.raises(EventProcessingError) as exc_info:
        bus.publish(DummyEvent("test"))
        
    error = exc_info.value
    # Vérification que le message public est neutre
    assert str(error) == "A technical error occurred while processing the event."
    assert error.event_type == "DummyEvent"
    assert error.handler_name == "FailingHandler"
    assert "Simulated DB Crash" in str(error.cause)

def test_caplog_outputs(caplog):
    # Injection du logger configuré pour le test
    logger = logging.getLogger("TestBus")
    logger.setLevel(logging.DEBUG)
    bus = EventBus(logger=logger)
    handler = DummyHandler()
    
    with caplog.at_level(logging.DEBUG):
        bus.register(DummyEvent, handler)
        bus.publish(DummyEvent("test"))
        bus.unregister(DummyEvent, handler)

    assert "Registered handler DummyHandler for event DummyEvent" in caplog.text
    assert "Publishing DummyEvent to 1 handler(s)" in caplog.text
    assert "processed DummyEvent in" in caplog.text
    assert "Unregistered handler DummyHandler for event DummyEvent" in caplog.text
import pytest
import logging
from dataclasses import dataclass
from domain.events.base_domain_event import BaseDomainEvent
from application.ports.event_handler import AbstractEventHandler
from application.ports.event_bus import EventCascadeLimitExceeded
from infrastructure.bus.in_memory_event_bus import InMemoryEventBus

# --- Définition des événements factices pour les tests ---
@dataclass(frozen=True, kw_only=True)
class EventA(BaseDomainEvent): pass

@dataclass(frozen=True, kw_only=True)
class EventB(BaseDomainEvent): pass

@dataclass(frozen=True, kw_only=True)
class EventC(BaseDomainEvent): pass

# --- Définition des Handlers factices ---
class CascadingHandler(AbstractEventHandler):
    def __init__(self, bus: InMemoryEventBus, event_to_emit: BaseDomainEvent):
        self.bus = bus
        self.event_to_emit = event_to_emit

    def handle(self, event: BaseDomainEvent) -> None:
        self.bus.publish(self.event_to_emit)

class FailingHandler(AbstractEventHandler):
    def handle(self, event: BaseDomainEvent) -> None:
        raise ValueError("Erreur inattendue dans le handler")


# --- Tests ---
def test_event_bus_blocks_cascade_exceeding_max_depth():
    bus = InMemoryEventBus()
    
    correlation_id = "req-cascade-123"
    event_a = EventA(correlation_id=correlation_id)
    event_b = EventB(correlation_id=correlation_id)
    event_c = EventC(correlation_id=correlation_id)
    
    handler_a = CascadingHandler(bus, event_b)
    handler_b = CascadingHandler(bus, event_c)
    
    bus.subscribe(EventA, handler_a)
    bus.subscribe(EventB, handler_b)
    
    with pytest.raises(EventCascadeLimitExceeded, match="Profondeur maximale de cascade d'événements"):
        bus.publish(event_a)

def test_event_bus_logs_structured_metadata(caplog):
    bus = InMemoryEventBus()
    event_a = EventA(correlation_id="req-log-999")
    
    class DummyHandler(AbstractEventHandler):
        def handle(self, event: BaseDomainEvent) -> None: pass
            
    bus.subscribe(EventA, DummyHandler())
    
    with caplog.at_level(logging.INFO):
        bus.publish(event_a)
        
    assert "EventA" in caplog.text
    assert "req-log-999" in caplog.text
    assert "DummyHandler" in caplog.text

def test_event_bus_handler_isolation_logs_errors_with_correlation_id(caplog):
    bus = InMemoryEventBus()
    event_a = EventA(correlation_id="req-error-404")
    bus.subscribe(EventA, FailingHandler())
    
    with caplog.at_level(logging.ERROR):
        bus.publish(event_a)
        
    assert "Erreur inattendue dans le handler" in caplog.text
    assert "req-error-404" in caplog.text

def test_event_bus_depth_reset_after_failure():
    bus = InMemoryEventBus()
    event_a = EventA(correlation_id="req-reset-1")
    event_b = EventB(correlation_id="req-reset-1")
    event_c = EventC(correlation_id="req-reset-1")
    
    handler_a = CascadingHandler(bus, event_b)
    handler_b = CascadingHandler(bus, event_c)
    
    bus.subscribe(EventA, handler_a)
    bus.subscribe(EventB, handler_b)
    
    with pytest.raises(EventCascadeLimitExceeded):
        bus.publish(event_a)
        
    # Le compteur de profondeur doit être revenu à 0. 
    # S'il ne l'est pas, cet appel plantera immédiatement.
    with pytest.raises(EventCascadeLimitExceeded):
        bus.publish(event_a)

def test_multiple_handlers_receive_same_event(caplog):
    bus = InMemoryEventBus()
    event_a = EventA(correlation_id="req-multi-1")
    
    class SuccessHandler(AbstractEventHandler):
        def __init__(self): self.called = False
        def handle(self, event: BaseDomainEvent) -> None: self.called = True

    h1_failing = FailingHandler()
    h2_success = SuccessHandler()
    
    bus.subscribe(EventA, h1_failing)
    bus.subscribe(EventA, h2_success)
    
    with caplog.at_level(logging.ERROR):
        bus.publish(event_a)
        
    assert h2_success.called is True
    assert "Erreur inattendue dans le handler" in caplog.text
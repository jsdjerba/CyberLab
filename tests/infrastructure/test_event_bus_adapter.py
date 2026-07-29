import pytest
from infrastructure.adapters.event_bus_adapter import EventBusAdapter

def test_event_bus_adapter_publishes_events():
    # Arrange
    bus = EventBusAdapter()
    event_1 = {"type": "LAB_STARTED", "payload": "123"}
    event_2 = {"type": "STEP_COMPLETED", "payload": "456"}
    
    # Act
    bus.publish([event_1, event_2])
    
    # Assert
    assert len(bus.dispatched_events) == 2
    assert bus.dispatched_events[0] == event_1
    assert bus.dispatched_events[1] == event_2

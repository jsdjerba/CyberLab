from infrastructure.adapters.event_bus_adapter import EventBusAdapter

def test_event_bus_adapter_publishes_events():
    adapter = EventBusAdapter()
    events = ["Event1", "Event2", {"type": "CustomEvent"}]

    adapter.publish(events)

    assert len(adapter.dispatched_events) == 3
    assert adapter.dispatched_events == events
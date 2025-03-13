"""Integration tests for the event system."""

import pytest
from unittest.mock import MagicMock, call

from virtuallife.events import (
    EventDispatcher, 
    LoggingHandler, 
    CounterHandler,
    CallbackHandler,
    FilteredHandler,
    AggregateHandler,
    EntityEvents,
    EnvironmentEvents,
    SimulationEvents,
    SystemEvents,
)


@pytest.fixture
def dispatcher():
    """Create a fresh event dispatcher for testing."""
    return EventDispatcher()


def test_complete_event_workflow(dispatcher):
    """Test a complete workflow using the event system."""
    # Arrange
    mock_callback = MagicMock()
    counter_handler = CounterHandler()
    callback_handler = CallbackHandler(mock_callback)
    
    # Create a filter that only accepts events with entity_type="player"
    player_filter = lambda sender, kwargs: kwargs.get("entity_type") == "player"
    player_handler = FilteredHandler(callback_handler, player_filter)
    
    # Subscribe handlers
    dispatcher.subscribe(EntityEvents.CREATED, counter_handler)
    dispatcher.subscribe(EntityEvents.CREATED, player_handler)
    
    # Act - Publish events
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="1", entity_type="player")
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="2", entity_type="npc")
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="3", entity_type="player")
    
    # Assert
    assert counter_handler.count == 3  # All events
    mock_callback.assert_has_calls([
        call(sender="world", entity_id="1", entity_type="player"),
        call(sender="world", entity_id="3", entity_type="player")
    ])
    assert mock_callback.call_count == 2  # Only player events


def test_multiple_event_types(dispatcher):
    """Test handling multiple event types with different handlers."""
    # Arrange
    entity_created_handler = MagicMock()
    entity_destroyed_handler = MagicMock()
    position_changed_handler = MagicMock()
    
    # Subscribe handlers
    dispatcher.subscribe(EntityEvents.CREATED, entity_created_handler)
    dispatcher.subscribe(EntityEvents.DESTROYED, entity_destroyed_handler)
    dispatcher.subscribe(EntityEvents.POSITION_CHANGED, position_changed_handler)
    
    # Act - Publish events
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="1")
    dispatcher.publish(EntityEvents.POSITION_CHANGED, "entity", entity_id="1", old_pos=(0, 0), new_pos=(1, 1))
    dispatcher.publish(EntityEvents.DESTROYED, "world", entity_id="1")
    
    # Assert
    entity_created_handler.assert_called_once_with(sender="world", entity_id="1")
    position_changed_handler.assert_called_once_with(
        sender="entity", entity_id="1", old_pos=(0, 0), new_pos=(1, 1)
    )
    entity_destroyed_handler.assert_called_once_with(sender="world", entity_id="1")


def test_event_propagation_chain(dispatcher):
    """Test that events can trigger other events in a chain."""
    # Arrange
    mock_callback = MagicMock()
    
    # Create a handler that publishes another event
    def entity_created_handler(sender, **kwargs):
        entity_id = kwargs.get("entity_id")
        mock_callback(f"Entity {entity_id} created")
        # Publish a component added event
        dispatcher.publish(
            EntityEvents.COMPONENT_ADDED, 
            sender, 
            entity_id=entity_id, 
            component_type="position"
        )
    
    # Create a handler for the component added event
    def component_added_handler(sender, **kwargs):
        entity_id = kwargs.get("entity_id")
        component_type = kwargs.get("component_type")
        mock_callback(f"Component {component_type} added to entity {entity_id}")
    
    # Subscribe handlers
    dispatcher.subscribe(EntityEvents.CREATED, entity_created_handler)
    dispatcher.subscribe(EntityEvents.COMPONENT_ADDED, component_added_handler)
    
    # Act - Publish initial event
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="1")
    
    # Assert
    mock_callback.assert_has_calls([
        call("Entity 1 created"),
        call("Component position added to entity 1")
    ])


def test_unsubscribing_during_event_handling(dispatcher):
    """Test that handlers can unsubscribe themselves during event handling."""
    # Arrange
    mock_callback = MagicMock()
    
    # Create a one-shot handler that unsubscribes itself after first call
    def one_shot_handler(sender, **kwargs):
        mock_callback(f"Handled event from {sender}")
        dispatcher.unsubscribe(EntityEvents.CREATED, one_shot_handler)
    
    # Subscribe handlers
    dispatcher.subscribe(EntityEvents.CREATED, one_shot_handler)
    
    # Act - Publish events twice
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="1")
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="2")
    
    # Assert
    mock_callback.assert_called_once_with("Handled event from world")
    # Verify the handler unsubscribed itself
    assert not dispatcher.has_subscribers(EntityEvents.CREATED)


def test_aggregate_handler_with_filter(dispatcher):
    """Test an aggregate handler with filtered components."""
    # Arrange
    counter1 = CounterHandler()
    counter2 = CounterHandler()
    
    # Create filters
    player_filter = lambda sender, kwargs: kwargs.get("entity_type") == "player"
    npc_filter = lambda sender, kwargs: kwargs.get("entity_type") == "npc"
    
    # Create filtered handlers
    player_handler = FilteredHandler(counter1, player_filter)
    npc_handler = FilteredHandler(counter2, npc_filter)
    
    # Create aggregate handler
    aggregate = AggregateHandler([player_handler, npc_handler])
    
    # Subscribe handlers
    dispatcher.subscribe(EntityEvents.CREATED, aggregate)
    
    # Act - Publish events
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="1", entity_type="player")
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="2", entity_type="npc")
    dispatcher.publish(EntityEvents.CREATED, "world", entity_id="3", entity_type="item")
    
    # Assert
    assert counter1.count == 1  # Only player events
    assert counter2.count == 1  # Only NPC events 
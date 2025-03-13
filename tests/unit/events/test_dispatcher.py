"""Tests for the event dispatcher."""

import pytest
from unittest.mock import MagicMock, call

from virtuallife.events import EventDispatcher


@pytest.fixture
def dispatcher() -> EventDispatcher:
    """Create a fresh event dispatcher for testing."""
    return EventDispatcher()


def test_subscribe_adds_callback(dispatcher: EventDispatcher):
    """Test that subscribing adds a callback to the event type."""
    # Arrange
    callback = MagicMock()
    event_type = "test_event"
    
    # Act
    dispatcher.subscribe(event_type, callback)
    
    # Assert
    assert dispatcher.has_subscribers(event_type)
    assert event_type in dispatcher.get_event_types()


def test_subscribe_ignores_duplicate_callbacks(dispatcher: EventDispatcher):
    """Test that subscribing the same callback twice only adds it once."""
    # Arrange
    callback = MagicMock()
    event_type = "test_event"
    
    # Act
    dispatcher.subscribe(event_type, callback)
    dispatcher.subscribe(event_type, callback)  # Duplicate
    
    # Get access to internal data to verify actual state
    subscribers = dispatcher._subscribers
    
    # Assert
    assert len(subscribers[event_type]) == 1


def test_unsubscribe_removes_callback(dispatcher: EventDispatcher):
    """Test that unsubscribing removes a callback from the event type."""
    # Arrange
    callback = MagicMock()
    event_type = "test_event"
    dispatcher.subscribe(event_type, callback)
    
    # Act
    dispatcher.unsubscribe(event_type, callback)
    
    # Assert
    assert not dispatcher.has_subscribers(event_type)
    assert event_type not in dispatcher.get_event_types()


def test_unsubscribe_nonexistent_callback_does_nothing(dispatcher: EventDispatcher):
    """Test that unsubscribing a callback that was never subscribed does nothing."""
    # Arrange
    callback = MagicMock()
    event_type = "test_event"
    
    # Act
    dispatcher.unsubscribe(event_type, callback)
    
    # Assert - no error should occur


def test_unsubscribe_from_nonexistent_event_does_nothing(dispatcher: EventDispatcher):
    """Test that unsubscribing from an event type that doesn't exist does nothing."""
    # Arrange
    callback = MagicMock()
    event_type = "nonexistent_event"
    
    # Act
    dispatcher.unsubscribe(event_type, callback)
    
    # Assert - no error should occur


def test_publish_calls_all_subscribers_with_kwargs(dispatcher: EventDispatcher):
    """Test that publishing an event calls all subscribers with kwargs."""
    # Arrange
    callback1 = MagicMock()
    callback2 = MagicMock()
    event_type = "test_event"
    dispatcher.subscribe(event_type, callback1)
    dispatcher.subscribe(event_type, callback2)
    
    # Act
    dispatcher.publish(event_type, "sender", key1="value1", key2="value2")
    
    # Assert
    callback1.assert_called_once_with(sender="sender", key1="value1", key2="value2")
    callback2.assert_called_once_with(sender="sender", key1="value1", key2="value2")


def test_publish_to_nonexistent_event_does_nothing(dispatcher: EventDispatcher):
    """Test that publishing to an event type with no subscribers does nothing."""
    # Arrange
    event_type = "nonexistent_event"
    
    # Act
    dispatcher.publish(event_type, "sender", key1="value1")
    
    # Assert - no error should occur


def test_has_subscribers_returns_true_for_event_with_subscribers(dispatcher: EventDispatcher):
    """Test that has_subscribers returns True for an event type with subscribers."""
    # Arrange
    callback = MagicMock()
    event_type = "test_event"
    dispatcher.subscribe(event_type, callback)
    
    # Act & Assert
    assert dispatcher.has_subscribers(event_type) is True


def test_has_subscribers_returns_false_for_event_without_subscribers(dispatcher: EventDispatcher):
    """Test that has_subscribers returns False for an event type without subscribers."""
    # Arrange
    event_type = "test_event"
    
    # Act & Assert
    assert dispatcher.has_subscribers(event_type) is False


def test_get_event_types_returns_all_event_types(dispatcher: EventDispatcher):
    """Test that get_event_types returns all event types with subscribers."""
    # Arrange
    callback = MagicMock()
    event_type1 = "test_event1"
    event_type2 = "test_event2"
    dispatcher.subscribe(event_type1, callback)
    dispatcher.subscribe(event_type2, callback)
    
    # Act
    event_types = dispatcher.get_event_types()
    
    # Assert
    assert event_types == {event_type1, event_type2}


def test_get_event_types_returns_empty_set_when_no_subscribers(dispatcher: EventDispatcher):
    """Test that get_event_types returns an empty set when there are no subscribers."""
    # Act
    event_types = dispatcher.get_event_types()
    
    # Assert
    assert event_types == set()


def test_clear_removes_all_subscriptions(dispatcher: EventDispatcher):
    """Test that clear removes all subscriptions."""
    # Arrange
    callback = MagicMock()
    event_type1 = "test_event1"
    event_type2 = "test_event2"
    dispatcher.subscribe(event_type1, callback)
    dispatcher.subscribe(event_type2, callback)
    
    # Act
    dispatcher.clear()
    
    # Assert
    assert dispatcher.get_event_types() == set()
    assert dispatcher.has_subscribers(event_type1) is False
    assert dispatcher.has_subscribers(event_type2) is False


def test_clear_event_type_removes_all_subscriptions_for_event_type(dispatcher: EventDispatcher):
    """Test that clear_event_type removes all subscriptions for a specific event type."""
    # Arrange
    callback = MagicMock()
    event_type1 = "test_event1"
    event_type2 = "test_event2"
    dispatcher.subscribe(event_type1, callback)
    dispatcher.subscribe(event_type2, callback)
    
    # Act
    dispatcher.clear_event_type(event_type1)
    
    # Assert
    assert dispatcher.has_subscribers(event_type1) is False
    assert dispatcher.has_subscribers(event_type2) is True


def test_clear_event_type_nonexistent_event_does_nothing(dispatcher: EventDispatcher):
    """Test that clear_event_type for a nonexistent event type does nothing."""
    # Arrange
    callback = MagicMock()
    event_type = "test_event"
    nonexistent_event_type = "nonexistent_event"
    dispatcher.subscribe(event_type, callback)
    
    # Act
    dispatcher.clear_event_type(nonexistent_event_type)
    
    # Assert
    assert dispatcher.has_subscribers(event_type) is True 
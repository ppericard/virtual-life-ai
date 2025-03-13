"""Tests for the event handlers."""

import json
import logging
import pytest
from unittest.mock import MagicMock, call, patch

from virtuallife.events import (
    EventHandler,
    LoggingHandler,
    CounterHandler,
    CallbackHandler,
    JsonLogHandler,
    FilteredHandler,
    AggregateHandler,
)


def test_logging_handler_formats_message(caplog):
    """Test that LoggingHandler formats the message with event data."""
    # Arrange
    with caplog.at_level(logging.INFO):
        handler = LoggingHandler("Entity {entity_id} created by {sender}")
        
        # Act
        handler("world", entity_id="123")
        
        # Assert
        assert "Entity 123 created by world" in caplog.text


def test_logging_handler_logs_error_on_missing_format_key(caplog):
    """Test that LoggingHandler logs an error if a format key is missing."""
    # Arrange
    with caplog.at_level(logging.ERROR):
        handler = LoggingHandler("Entity {entity_id} created by {missing_key}")
        
        # Act
        handler("world", entity_id="123")
        
        # Assert
        assert "Error formatting log message" in caplog.text
        assert "missing_key" in caplog.text


def test_logging_handler_respects_log_level(caplog):
    """Test that LoggingHandler respects the specified log level."""
    # Arrange
    with caplog.at_level(logging.DEBUG):
        handler = LoggingHandler("Message", level=logging.DEBUG)
        
        # Act
        handler("sender")
        
        # Assert
        assert "Message" in caplog.text
        assert caplog.records[0].levelno == logging.DEBUG


def test_counter_handler_increments_count():
    """Test that CounterHandler increments count on each call."""
    # Arrange
    handler = CounterHandler()
    
    # Act
    handler("sender1")
    handler("sender2")
    handler("sender3")
    
    # Assert
    assert handler.count == 3


def test_counter_handler_reset():
    """Test that CounterHandler.reset resets the count to 0."""
    # Arrange
    handler = CounterHandler()
    handler("sender1")
    handler("sender2")
    
    # Act
    handler.reset()
    
    # Assert
    assert handler.count == 0


def test_callback_handler_calls_callback():
    """Test that CallbackHandler calls the callback function with args."""
    # Arrange
    callback = MagicMock()
    handler = CallbackHandler(callback)
    
    # Act
    handler("sender", key1="value1", key2="value2")
    
    # Assert
    callback.assert_called_once_with(sender="sender", key1="value1", key2="value2")


@patch("json.dumps")
@patch("time.time", return_value=1234567890.0)
def test_json_log_handler_logs_json(mock_time, mock_dumps, caplog):
    """Test that JsonLogHandler logs the event data as JSON."""
    # Arrange
    mock_dumps.return_value = '{"key1": "value1", "sender": "test", "timestamp": 1234567890.0}'
    
    with caplog.at_level(logging.INFO):
        handler = JsonLogHandler()
        
        # Act
        handler("test", key1="value1")
        
        # Assert
        mock_dumps.assert_called_once_with({
            "key1": "value1",
            "sender": "test",
            "timestamp": 1234567890.0
        })
        assert '{"key1": "value1", "sender": "test", "timestamp": 1234567890.0}' in caplog.text


def test_json_log_handler_logs_error_on_serialization_failure(caplog):
    """Test that JsonLogHandler logs an error if JSON serialization fails."""
    # Arrange
    with caplog.at_level(logging.ERROR):
        handler = JsonLogHandler()
        
        # Act - pass non-serializable object
        handler("test", key1=object())
        
        # Assert
        assert "Error serializing event to JSON" in caplog.text


def test_filtered_handler_calls_handler_when_filter_passes():
    """Test that FilteredHandler calls the handler when the filter passes."""
    # Arrange
    filter_func = lambda sender, kwargs: kwargs.get("key1") == "value1"
    mock_handler = MagicMock()
    handler = FilteredHandler(mock_handler, filter_func)
    
    # Act
    handler("sender", key1="value1")
    
    # Assert
    mock_handler.assert_called_once_with(sender="sender", key1="value1")


def test_filtered_handler_does_not_call_handler_when_filter_fails():
    """Test that FilteredHandler does not call the handler when the filter fails."""
    # Arrange
    filter_func = lambda sender, kwargs: kwargs.get("key1") == "value1"
    mock_handler = MagicMock()
    handler = FilteredHandler(mock_handler, filter_func)
    
    # Act
    handler("sender", key1="value2")
    
    # Assert
    mock_handler.assert_not_called()


def test_aggregate_handler_calls_all_handlers():
    """Test that AggregateHandler calls all handlers."""
    # Arrange
    mock_handler1 = MagicMock()
    mock_handler2 = MagicMock()
    handler = AggregateHandler([mock_handler1, mock_handler2])
    
    # Act
    handler("sender", key1="value1")
    
    # Assert
    mock_handler1.assert_called_once_with(sender="sender", key1="value1")
    mock_handler2.assert_called_once_with(sender="sender", key1="value1")


def test_aggregate_handler_add_handler():
    """Test that AggregateHandler.add_handler adds a handler."""
    # Arrange
    mock_handler1 = MagicMock()
    mock_handler2 = MagicMock()
    handler = AggregateHandler([mock_handler1])
    
    # Act
    handler.add_handler(mock_handler2)
    handler("sender", key1="value1")
    
    # Assert
    mock_handler1.assert_called_once_with(sender="sender", key1="value1")
    mock_handler2.assert_called_once_with(sender="sender", key1="value1")


def test_aggregate_handler_remove_handler():
    """Test that AggregateHandler.remove_handler removes a handler."""
    # Arrange
    mock_handler1 = MagicMock()
    mock_handler2 = MagicMock()
    handler = AggregateHandler([mock_handler1, mock_handler2])
    
    # Act
    handler.remove_handler(mock_handler1)
    handler("sender", key1="value1")
    
    # Assert
    mock_handler1.assert_not_called()
    mock_handler2.assert_called_once_with(sender="sender", key1="value1")


def test_aggregate_handler_remove_nonexistent_handler_does_nothing():
    """Test that AggregateHandler.remove_handler for a nonexistent handler does nothing."""
    # Arrange
    mock_handler1 = MagicMock()
    mock_handler2 = MagicMock()
    handler = AggregateHandler([mock_handler1])
    
    # Act
    handler.remove_handler(mock_handler2)  # Not in the list
    handler("sender", key1="value1")
    
    # Assert
    mock_handler1.assert_called_once_with(sender="sender", key1="value1") 
"""Standard event handlers for the VirtualLife simulation.

This module provides standard event handler classes that can be used to handle
common event processing scenarios. These handlers can be subclassed or used
directly to respond to events.

Examples:
    >>> from virtuallife.events.dispatcher import EventDispatcher
    >>> from virtuallife.events.types import EntityEvents
    >>> from virtuallife.events.handlers import LoggingHandler
    >>> 
    >>> # Create an event dispatcher
    >>> dispatcher = EventDispatcher()
    >>> 
    >>> # Create a logging handler for entity created events
    >>> logging_handler = LoggingHandler("Entity created: {entity_id}")
    >>> dispatcher.subscribe(EntityEvents.CREATED, logging_handler)
    >>> 
    >>> # Publish an event
    >>> dispatcher.publish(EntityEvents.CREATED, "world", entity_id="123")
    Entity created: 123
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, TypeVar, Union, cast
import json
import time

from virtuallife.events.types import EntityEvents, EnvironmentEvents, SimulationEvents, SystemEvents


class EventHandler(Protocol):
    """Protocol defining the interface for event handlers.
    
    Event handlers must be callable with keyword arguments. The 'sender' argument
    is always provided, along with any additional arguments specified when
    publishing the event.
    """
    
    def __call__(self, sender: Any, **kwargs: Any) -> None:
        """Handle an event.
        
        Args:
            sender: The object that published the event
            **kwargs: Additional data associated with the event
        """
        ...


class LoggingHandler:
    """Event handler that logs events with a configurable message format.
    
    Attributes:
        message_format: String format for log messages, with placeholders for event data
        level: Logging level to use (default: INFO)
        logger: Logger to use (default: root logger)
    """
    
    def __init__(
        self, 
        message_format: str, 
        level: int = logging.INFO,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize the logging handler.
        
        Args:
            message_format: String format for log messages, with placeholders for event data
            level: Logging level to use
            logger: Logger to use, or None to use the root logger
        """
        self.message_format = message_format
        self.level = level
        self.logger = logger or logging.getLogger()
        
    def __call__(self, sender: Any, **kwargs: Any) -> None:
        """Handle an event by logging it.
        
        Args:
            sender: The object that published the event
            **kwargs: Additional data associated with the event
        """
        # Add sender to kwargs for message formatting
        kwargs['sender'] = sender
        
        # Format the message
        try:
            message = self.message_format.format(**kwargs)
            self.logger.log(self.level, message)
        except KeyError as e:
            # If a format key is missing, log that instead
            self.logger.error(f"Error formatting log message: {e}. Event data: {kwargs}")


class CounterHandler:
    """Event handler that counts the number of occurrences of an event.
    
    Attributes:
        count: The current count of events
    """
    
    def __init__(self) -> None:
        """Initialize the counter handler with a count of 0."""
        self.count = 0
        
    def __call__(self, sender: Any, **kwargs: Any) -> None:
        """Handle an event by incrementing the count.
        
        Args:
            sender: The object that published the event
            **kwargs: Additional data associated with the event
        """
        self.count += 1
        
    def reset(self) -> None:
        """Reset the counter to 0."""
        self.count = 0


class CallbackHandler:
    """Event handler that calls a custom function when an event occurs.
    
    Attributes:
        callback: The function to call when the event occurs
    """
    
    def __init__(self, callback: Callable[..., None]) -> None:
        """Initialize the callback handler.
        
        Args:
            callback: The function to call when the event occurs
        """
        self.callback = callback
        
    def __call__(self, sender: Any, **kwargs: Any) -> None:
        """Handle an event by calling the callback function.
        
        Args:
            sender: The object that published the event
            **kwargs: Additional data associated with the event
        """
        self.callback(sender=sender, **kwargs)


class JsonLogHandler:
    """Event handler that logs events as JSON.
    
    This handler is useful for structured logging that can be parsed by
    external tools or for debugging complex event data.
    
    Attributes:
        logger: Logger to use
        level: Logging level to use
    """
    
    def __init__(
        self,
        level: int = logging.INFO,
        logger: Optional[logging.Logger] = None
    ) -> None:
        """Initialize the JSON log handler.
        
        Args:
            level: Logging level to use
            logger: Logger to use, or None to use the root logger
        """
        self.level = level
        self.logger = logger or logging.getLogger()
        
    def __call__(self, sender: Any, **kwargs: Any) -> None:
        """Handle an event by logging it as JSON.
        
        Args:
            sender: The object that published the event
            **kwargs: Additional data associated with the event
        """
        # Create a copy of kwargs to avoid modifying the original
        data = kwargs.copy()
        
        # Add sender and timestamp
        data['sender'] = str(sender)
        data['timestamp'] = time.time()
        
        # Convert to JSON and log
        try:
            json_data = json.dumps(data)
            self.logger.log(self.level, json_data)
        except (TypeError, ValueError) as e:
            # If data can't be serialized to JSON, log that instead
            self.logger.error(f"Error serializing event to JSON: {e}. Event data: {data}")


class FilteredHandler:
    """Event handler that only processes events matching a filter condition.
    
    Attributes:
        handler: The handler to call if the filter condition is met
        filter_func: Function that returns True if the event should be handled
    """
    
    def __init__(
        self,
        handler: Union[EventHandler, Callable[..., None]],
        filter_func: Callable[[Any, Dict[str, Any]], bool]
    ) -> None:
        """Initialize the filtered handler.
        
        Args:
            handler: The handler to call if the filter condition is met
            filter_func: Function that takes (sender, kwargs) and returns True if the event should be handled
        """
        self.handler = handler
        self.filter_func = filter_func
        
    def __call__(self, sender: Any, **kwargs: Any) -> None:
        """Handle an event if it passes the filter.
        
        Args:
            sender: The object that published the event
            **kwargs: Additional data associated with the event
        """
        if self.filter_func(sender, kwargs):
            # Call the handler
            if isinstance(self.handler, Callable):
                self.handler(sender=sender, **kwargs)


class AggregateHandler:
    """Event handler that delegates to multiple handlers.
    
    Attributes:
        handlers: List of handlers to call
    """
    
    def __init__(self, handlers: List[Union[EventHandler, Callable[..., None]]]) -> None:
        """Initialize the aggregate handler.
        
        Args:
            handlers: List of handlers to call
        """
        self.handlers = handlers
        
    def __call__(self, sender: Any, **kwargs: Any) -> None:
        """Handle an event by calling all child handlers.
        
        Args:
            sender: The object that published the event
            **kwargs: Additional data associated with the event
        """
        for handler in self.handlers:
            if isinstance(handler, Callable):
                handler(sender=sender, **kwargs)
                
    def add_handler(self, handler: Union[EventHandler, Callable[..., None]]) -> None:
        """Add a handler to the aggregate.
        
        Args:
            handler: The handler to add
        """
        self.handlers.append(handler)
        
    def remove_handler(self, handler: Union[EventHandler, Callable[..., None]]) -> None:
        """Remove a handler from the aggregate.
        
        Args:
            handler: The handler to remove
        """
        if handler in self.handlers:
            self.handlers.remove(handler) 
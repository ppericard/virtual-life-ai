"""Event system for the VirtualLife simulation.

This package provides a flexible event system based on the observer pattern.
It allows different components of the simulation to communicate without tight coupling.

Components include:
- EventDispatcher: Central event dispatching system
- Event types: Standard event type constants
- Event handlers: Standard handler implementations

Examples:
    >>> from virtuallife.events import EventDispatcher, EntityEvents
    >>> 
    >>> # Create an event dispatcher
    >>> dispatcher = EventDispatcher()
    >>> 
    >>> # Subscribe to an event
    >>> def on_entity_created(sender, entity_id, **kwargs):
    ...     print(f"Entity {entity_id} was created")
    >>> 
    >>> dispatcher.subscribe(EntityEvents.CREATED, on_entity_created)
    >>> 
    >>> # Publish an event
    >>> dispatcher.publish(EntityEvents.CREATED, "world", entity_id="123")
    Entity 123 was created
"""

from virtuallife.events.dispatcher import EventDispatcher, EventCallback
from virtuallife.events.types import (
    EntityEvents,
    EnvironmentEvents,
    SimulationEvents,
    SystemEvents,
)
from virtuallife.events.handlers import (
    EventHandler,
    LoggingHandler,
    CounterHandler,
    CallbackHandler,
    JsonLogHandler,
    FilteredHandler,
    AggregateHandler,
)

__all__ = [
    # Dispatcher
    "EventDispatcher",
    "EventCallback",
    
    # Event types
    "EntityEvents",
    "EnvironmentEvents",
    "SimulationEvents",
    "SystemEvents",
    
    # Handlers
    "EventHandler",
    "LoggingHandler",
    "CounterHandler",
    "CallbackHandler",
    "JsonLogHandler",
    "FilteredHandler",
    "AggregateHandler",
]

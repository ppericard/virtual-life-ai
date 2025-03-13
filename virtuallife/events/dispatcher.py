"""Event dispatcher for the VirtualLife simulation.

This module provides a generic event dispatching system based on the observer pattern.
It allows components to subscribe to events and be notified when those events occur,
without requiring direct coupling between event producers and consumers.

Examples:
    >>> from virtuallife.events.dispatcher import EventDispatcher
    >>> 
    >>> # Create an event dispatcher
    >>> dispatcher = EventDispatcher()
    >>> 
    >>> # Subscribe to an event
    >>> def entity_created_handler(sender, entity_id, **kwargs):
    ...     print(f"Entity {entity_id} was created by {sender}")
    >>> 
    >>> dispatcher.subscribe("entity_created", entity_created_handler)
    >>> 
    >>> # Publish an event
    >>> dispatcher.publish("entity_created", "world", entity_id="123")
    Entity 123 was created by world
"""

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar

# Type for event callback functions
EventCallback = Callable[..., None]

# Type variable for sender
T = TypeVar('T')


class EventDispatcher:
    """Central event dispatching system based on the observer pattern.
    
    The EventDispatcher manages subscriptions to events and handles publishing
    events to all subscribers. It allows for loosely coupled components to
    communicate without direct references to each other.
    
    Attributes:
        subscribers: Dictionary mapping event types to lists of callback functions
    """
    
    def __init__(self) -> None:
        """Initialize the event dispatcher with an empty subscribers dictionary."""
        self._subscribers: Dict[str, List[EventCallback]] = defaultdict(list)
        
    def subscribe(self, event_type: str, callback: EventCallback) -> None:
        """Subscribe a callback function to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            callback: The function to call when the event occurs
        """
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            
    def unsubscribe(self, event_type: str, callback: EventCallback) -> None:
        """Unsubscribe a callback function from an event type.
        
        Args:
            event_type: The type of event to unsubscribe from
            callback: The function to unsubscribe
            
        Note:
            If the callback is not subscribed, this method does nothing.
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            # Clean up empty event types
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]
                
    def publish(self, event_type: str, sender: Any, **kwargs: Any) -> None:
        """Publish an event to all subscribers.
        
        Args:
            event_type: The type of event to publish
            sender: The object that is publishing the event
            **kwargs: Additional data to pass to the callback functions
        """
        if event_type not in self._subscribers:
            return
            
        for callback in self._subscribers[event_type]:
            callback(sender=sender, **kwargs)
            
    def has_subscribers(self, event_type: str) -> bool:
        """Check if an event type has any subscribers.
        
        Args:
            event_type: The event type to check
            
        Returns:
            True if the event type has subscribers, False otherwise
        """
        return event_type in self._subscribers and bool(self._subscribers[event_type])
        
    def get_event_types(self) -> Set[str]:
        """Get all event types that have subscribers.
        
        Returns:
            A set of all event types with subscribers
        """
        return set(self._subscribers.keys())
        
    def clear(self) -> None:
        """Remove all subscriptions."""
        self._subscribers.clear()
        
    def clear_event_type(self, event_type: str) -> None:
        """Remove all subscriptions for a specific event type.
        
        Args:
            event_type: The event type to clear
        """
        if event_type in self._subscribers:
            del self._subscribers[event_type] 
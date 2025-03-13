"""Event types and constants for the VirtualLife simulation.

This module defines standard event types and constants for the event system.
Using these constants ensures consistent event naming across the application.

Examples:
    >>> from virtuallife.events.types import EntityEvents
    >>> from virtuallife.events.dispatcher import EventDispatcher
    >>> 
    >>> dispatcher = EventDispatcher()
    >>> 
    >>> # Subscribe to entity created event
    >>> def on_entity_created(sender, entity_id, **kwargs):
    ...     print(f"Entity {entity_id} was created")
    >>> 
    >>> dispatcher.subscribe(EntityEvents.CREATED, on_entity_created)
"""

from enum import Enum, auto
from typing import Final


class EntityEvents:
    """Constants for entity-related events."""
    
    # Entity lifecycle events
    CREATED: Final[str] = "entity:created"
    DESTROYED: Final[str] = "entity:destroyed"
    
    # Entity component events
    COMPONENT_ADDED: Final[str] = "entity:component_added"
    COMPONENT_REMOVED: Final[str] = "entity:component_removed"
    COMPONENT_UPDATED: Final[str] = "entity:component_updated"
    
    # Entity position events
    POSITION_CHANGED: Final[str] = "entity:position_changed"


class EnvironmentEvents:
    """Constants for environment-related events."""
    
    # Grid events
    GRID_CHANGED: Final[str] = "environment:grid_changed"
    ENTITY_ADDED_TO_GRID: Final[str] = "environment:entity_added_to_grid"
    ENTITY_REMOVED_FROM_GRID: Final[str] = "environment:entity_removed_from_grid"
    
    # Resource events
    RESOURCE_ADDED: Final[str] = "environment:resource_added"
    RESOURCE_REMOVED: Final[str] = "environment:resource_removed"
    RESOURCE_CONSUMED: Final[str] = "environment:resource_consumed"


class SimulationEvents:
    """Constants for simulation-related events."""
    
    # Simulation lifecycle events
    STARTED: Final[str] = "simulation:started"
    PAUSED: Final[str] = "simulation:paused"
    RESUMED: Final[str] = "simulation:resumed"
    STOPPED: Final[str] = "simulation:stopped"
    
    # Simulation step events
    STEP_STARTED: Final[str] = "simulation:step_started"
    STEP_COMPLETED: Final[str] = "simulation:step_completed"


class SystemEvents:
    """Constants for system-related events."""
    
    # System lifecycle events
    REGISTERED: Final[str] = "system:registered"
    UNREGISTERED: Final[str] = "system:unregistered"
    
    # System process events
    PROCESS_STARTED: Final[str] = "system:process_started"
    PROCESS_COMPLETED: Final[str] = "system:process_completed" 
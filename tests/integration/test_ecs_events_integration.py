"""Integration tests for ECS and Events components.

These tests verify that the Entity-Component-System (ECS) architecture and
the Event system work together correctly.
"""

import pytest
from unittest.mock import MagicMock
from typing import List, Type, Any, Dict

from virtuallife.ecs import World, Entity, System
from virtuallife.events import (
    EventDispatcher, 
    EntityEvents, 
    CallbackHandler,
    CounterHandler,
)


class PositionComponent:
    """Component storing the position of an entity."""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def update(self, entity, world, dt) -> None:
        """Update method to satisfy Component protocol."""
        pass


class PositionSystem(System):
    """System that processes position changes and emits events."""
    
    def __init__(self, event_dispatcher: EventDispatcher):
        super().__init__()
        self.event_dispatcher = event_dispatcher
        
    @property
    def required_components(self) -> List[Type]:
        """Get the component types required by this system."""
        return [PositionComponent]
        
    def process(self, world: World, dt: float) -> None:
        """Process entities with position components."""
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            position = entity.get_component(PositionComponent)
            
            # For this test, we'll emit a position changed event for all entities
            self.event_dispatcher.publish(
                EntityEvents.POSITION_CHANGED,
                sender=entity_id,
                entity_id=entity_id,
                old_pos=(position.x, position.y),
                new_pos=(position.x, position.y)  # Same position for simplicity
            )


@pytest.fixture
def world_with_events() -> tuple[World, EventDispatcher]:
    """Create a world and event dispatcher for testing."""
    dispatcher = EventDispatcher()
    world = World()
    
    position_system = PositionSystem(dispatcher)
    world.add_system(position_system)
    
    return world, dispatcher


def test_system_emits_events(world_with_events: tuple[World, EventDispatcher]):
    """Test that systems can emit events properly."""
    world, dispatcher = world_with_events
    
    # Create a mock event handler
    mock_handler = MagicMock()
    dispatcher.subscribe(EntityEvents.POSITION_CHANGED, mock_handler)
    
    # Create an entity with position
    entity = Entity()
    entity.add_component(PositionComponent(10, 10))
    entity_id = world.add_entity(entity)
    
    # Update world
    world.update(1.0)
    
    # Verify the event was emitted
    assert mock_handler.call_count > 0
    call_args = mock_handler.call_args[1]  # Get kwargs
    assert 'sender' in call_args
    assert 'entity_id' in call_args
    assert 'old_pos' in call_args
    assert 'new_pos' in call_args


def test_multiple_event_handlers(world_with_events: tuple[World, EventDispatcher]):
    """Test that multiple event handlers receive system events."""
    world, dispatcher = world_with_events
    
    # Create several event handlers
    callback_mock = MagicMock()
    callback_handler = CallbackHandler(callback_mock)
    counter_handler = CounterHandler()
    
    # Subscribe handlers to the event
    dispatcher.subscribe(EntityEvents.POSITION_CHANGED, callback_handler)
    dispatcher.subscribe(EntityEvents.POSITION_CHANGED, counter_handler)
    
    # Create multiple entities
    entity_count = 5
    for i in range(entity_count):
        entity = Entity()
        entity.add_component(PositionComponent(i * 10, i * 10))
        world.add_entity(entity)
    
    # Update world
    world.update(1.0)
    
    # Verify the callback was called for each entity
    assert callback_mock.call_count == entity_count
    
    # Verify the counter incremented for each entity
    assert counter_handler.count == entity_count


class ComponentAddedSystem(System):
    """System that adds components to entities and emits events."""
    
    def __init__(self, event_dispatcher: EventDispatcher):
        super().__init__()
        self.event_dispatcher = event_dispatcher
        
    @property
    def required_components(self) -> List[Type]:
        """Get the component types required by this system."""
        return []  # No requirements, will register all entities
        
    def process(self, world: World, dt: float) -> None:
        """Process all entities, potentially adding components."""
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            
            # Add a position component if not present
            if not entity.has_component(PositionComponent):
                entity.add_component(PositionComponent(0, 0))
                
                # Emit component added event
                self.event_dispatcher.publish(
                    EntityEvents.COMPONENT_ADDED,
                    sender=entity_id,
                    entity_id=entity_id,
                    component_type="position"
                )


class ComponentAddedEventHandler:
    """Custom event handler that tracks components added to entities."""
    
    def __init__(self):
        self.components_added: Dict[Any, List[str]] = {}
        
    def __call__(self, sender, **kwargs):
        """Handle component added event."""
        entity_id = kwargs.get('entity_id')
        component_type = kwargs.get('component_type')
        
        if entity_id not in self.components_added:
            self.components_added[entity_id] = []
            
        self.components_added[entity_id].append(component_type)


def test_component_lifecycle_events(world_with_events: tuple[World, EventDispatcher]):
    """Test that component lifecycle events are properly emitted and handled."""
    # Create a new world and dispatcher
    dispatcher = EventDispatcher()
    world = World()
    
    # Add our test system
    component_system = ComponentAddedSystem(dispatcher)
    world.add_system(component_system)
    
    # Create our custom event handler
    component_handler = ComponentAddedEventHandler()
    dispatcher.subscribe(EntityEvents.COMPONENT_ADDED, component_handler)
    
    # Create entities without position components
    entities = []
    for _ in range(3):
        entity = Entity()
        entity_id = world.add_entity(entity)
        entities.append(entity_id)
    
    # Update world
    world.update(1.0)
    
    # Verify that events were received for each entity
    assert len(component_handler.components_added) > 0
    
    # Check that all entities now have position components
    for entity_id in entities:
        entity = world.get_entity(entity_id)
        assert entity.has_component(PositionComponent) 
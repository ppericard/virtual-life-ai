"""Tests for the world module."""

from dataclasses import dataclass
from typing import List, Type, Set, Optional, Any
import pytest
from uuid import UUID, uuid4

from virtuallife.ecs.world import World
from virtuallife.ecs.entity import Entity
from virtuallife.ecs.system import System
from virtuallife.types.core import Position


@dataclass
class TestComponent:
    """Test component for testing World class."""
    
    value: int = 0
    
    def update(self, entity: Any, world: Any, dt: float) -> None:
        """Update the component.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update
        """
        self.value += 1


class TestSystem(System):
    """Test system for testing World class."""
    
    def __init__(self) -> None:
        """Initialize the system."""
        super().__init__()
        self.processed_entities: Set[UUID] = set()
        self.process_called = False
    
    @property
    def required_components(self) -> List[Type[Any]]:
        """Get the component types required for an entity to be processed by this system.
        
        Returns:
            A list of component types that an entity must have to be processed
        """
        return [TestComponent]
    
    def process(self, world: World, dt: float) -> None:
        """Process all registered entities.
        
        Args:
            world: The world containing the entities
            dt: Time delta since last update
        """
        self.process_called = True
        for entity_id in self.entities:
            self.processed_entities.add(entity_id)


class AnotherSystem(System):
    """Another test system for testing World class."""
    
    def __init__(self) -> None:
        """Initialize the system."""
        super().__init__()
        self.process_called = False
    
    @property
    def required_components(self) -> List[Type[Any]]:
        """Get the component types required for an entity to be processed by this system.
        
        Returns:
            A list of component types that an entity must have to be processed
        """
        return []
    
    def process(self, world: World, dt: float) -> None:
        """Process all registered entities.
        
        Args:
            world: The world containing the entities
            dt: Time delta since last update
        """
        self.process_called = True


class MockSpatialGrid:
    """Mock spatial grid for testing."""
    
    def __init__(self) -> None:
        """Initialize the mock spatial grid."""
        self.entities: Dict[UUID, Position] = {}
        self.clear_called = False
    
    def add_entity(self, entity_id: UUID, position: Position) -> None:
        """Add an entity to the grid.
        
        Args:
            entity_id: The ID of the entity to add
            position: The position of the entity
        """
        self.entities[entity_id] = position
    
    def remove_entity(self, entity_id: UUID) -> None:
        """Remove an entity from the grid.
        
        Args:
            entity_id: The ID of the entity to remove
        """
        if entity_id in self.entities:
            del self.entities[entity_id]
    
    def clear(self) -> None:
        """Clear all entities from the grid."""
        self.entities.clear()
        self.clear_called = True


def test_world_initialization():
    """Test that worlds can be initialized."""
    # Act
    world = World()
    
    # Assert
    assert isinstance(world.entities, dict)
    assert len(world.entities) == 0
    assert isinstance(world.systems, list)
    assert len(world.systems) == 0


def test_add_entity():
    """Test that entities can be added to worlds."""
    # Arrange
    world = World()
    entity = Entity(position=(10, 20))
    
    # Act
    world.add_entity(entity)
    
    # Assert
    assert entity.id in world.entities
    assert world.entities[entity.id] == entity
    assert world.entity_count == 1
    assert len(world) == 1


def test_add_entity_during_processing():
    """Test that entities added during processing are added after the update cycle."""
    # Arrange
    world = World()
    
    # Start processing
    world._is_processing = True
    
    # Add entity
    entity = Entity(position=(10, 20))
    world.add_entity(entity)
    
    # Assert entity is not added yet
    assert entity.id not in world.entities
    assert len(world._entities_pending_add) == 1
    
    # Stop processing and process pending changes
    world._is_processing = False
    world._process_pending_entity_changes()
    
    # Assert entity is added now
    assert entity.id in world.entities
    assert world.entities[entity.id] == entity
    assert len(world._entities_pending_add) == 0


def test_remove_entity():
    """Test that entities can be removed from worlds."""
    # Arrange
    world = World()
    entity = Entity(position=(10, 20))
    world.add_entity(entity)
    
    # Act
    world.remove_entity(entity.id)
    
    # Assert
    assert entity.id not in world.entities
    assert world.entity_count == 0
    assert len(world) == 0


def test_remove_entity_during_processing():
    """Test that entities removed during processing are removed after the update cycle."""
    # Arrange
    world = World()
    entity = Entity(position=(10, 20))
    world.add_entity(entity)
    
    # Start processing
    world._is_processing = True
    
    # Remove entity
    world.remove_entity(entity.id)
    
    # Assert entity is not removed yet
    assert entity.id in world.entities
    assert entity.id in world._entity_ids_pending_removal
    
    # Stop processing and process pending changes
    world._is_processing = False
    world._process_pending_entity_changes()
    
    # Assert entity is removed now
    assert entity.id not in world.entities
    assert len(world._entity_ids_pending_removal) == 0


def test_remove_nonexistent_entity():
    """Test that removing a nonexistent entity has no effect."""
    # Arrange
    world = World()
    entity_id = uuid4()
    
    # Act
    world.remove_entity(entity_id)
    
    # Assert
    assert entity_id not in world.entities
    assert world.entity_count == 0


def test_get_entity():
    """Test that entities can be retrieved from worlds."""
    # Arrange
    world = World()
    entity = Entity(position=(10, 20))
    world.add_entity(entity)
    
    # Act
    retrieved = world.get_entity(entity.id)
    
    # Assert
    assert retrieved == entity


def test_get_nonexistent_entity():
    """Test that retrieving a nonexistent entity returns None."""
    # Arrange
    world = World()
    entity_id = uuid4()
    
    # Act
    entity = world.get_entity(entity_id)
    
    # Assert
    assert entity is None


def test_get_entities():
    """Test that all entities can be retrieved from a world."""
    # Arrange
    world = World()
    entity1 = Entity(position=(10, 20))
    entity2 = Entity(position=(30, 40))
    world.add_entity(entity1)
    world.add_entity(entity2)
    
    # Act
    entities = world.get_entities()
    
    # Assert
    assert len(entities) == 2
    assert entity1 in entities
    assert entity2 in entities


def test_add_system():
    """Test that systems can be added to worlds."""
    # Arrange
    world = World()
    system = TestSystem()
    
    # Act
    world.add_system(system)
    
    # Assert
    assert system in world.systems
    assert world.system_count == 1


def test_add_system_with_priority():
    """Test that systems are sorted by priority when added."""
    # Arrange
    world = World()
    system1 = TestSystem()
    system2 = AnotherSystem()
    system1.set_priority(10)  # Higher priority
    system2.set_priority(5)   # Lower priority
    
    # Act
    world.add_system(system2)
    world.add_system(system1)
    
    # Assert
    assert world.systems[0] == system1  # Higher priority system should be first
    assert world.systems[1] == system2  # Lower priority system should be second


def test_add_system_registers_existing_entities():
    """Test that adding a system registers existing entities with it."""
    # Arrange
    world = World()
    entity = Entity(position=(10, 20))
    component = TestComponent(value=42)
    entity.add_component(component)
    world.add_entity(entity)
    
    # Act
    system = TestSystem()
    world.add_system(system)
    
    # Assert
    assert entity.id in system.entities


def test_remove_system():
    """Test that systems can be removed from worlds."""
    # Arrange
    world = World()
    system = TestSystem()
    world.add_system(system)
    
    # Act
    world.remove_system(TestSystem)
    
    # Assert
    assert system not in world.systems
    assert world.system_count == 0


def test_update():
    """Test that worlds can update their systems."""
    # Arrange
    world = World()
    system = TestSystem()
    world.add_system(system)
    entity = Entity(position=(10, 20))
    component = TestComponent(value=42)
    entity.add_component(component)
    world.add_entity(entity)
    
    # Act
    world.update(1.0)
    
    # Assert
    assert system.process_called
    assert entity.id in system.processed_entities


def test_update_with_disabled_system():
    """Test that disabled systems are not updated."""
    # Arrange
    world = World()
    system = TestSystem()
    system.disable()
    world.add_system(system)
    
    # Act
    world.update(1.0)
    
    # Assert
    assert not system.process_called


def test_update_processes_pending_changes():
    """Test that updating a world processes pending entity changes."""
    # Arrange
    world = World()
    entity1 = Entity(position=(10, 20))
    entity2 = Entity(position=(30, 40))
    
    # Add one entity now and one during processing
    world.add_entity(entity1)
    
    # Start processing
    world._is_processing = True
    
    # Add/remove entities during processing
    world.add_entity(entity2)
    world.remove_entity(entity1.id)
    
    # Assert entities are not added/removed yet
    assert entity1.id in world.entities
    assert entity2.id not in world.entities
    assert len(world._entities_pending_add) == 1
    assert len(world._entity_ids_pending_removal) == 1
    
    # Act
    world.update(1.0)
    
    # Assert entities are added/removed now
    assert entity1.id not in world.entities
    assert entity2.id in world.entities
    assert len(world._entities_pending_add) == 0
    assert len(world._entity_ids_pending_removal) == 0


def test_set_spatial_grid():
    """Test that a spatial grid can be set for a world."""
    # Arrange
    world = World()
    entity = Entity(position=(10, 20))
    world.add_entity(entity)
    grid = MockSpatialGrid()
    
    # Act
    world.set_spatial_grid(grid)
    
    # Assert
    assert world._spatial_grid == grid
    assert entity.id in grid.entities
    assert grid.entities[entity.id] == entity.position


def test_clear():
    """Test that worlds can be cleared."""
    # Arrange
    world = World()
    entity1 = Entity(position=(10, 20))
    entity2 = Entity(position=(30, 40))
    world.add_entity(entity1)
    world.add_entity(entity2)
    grid = MockSpatialGrid()
    world.set_spatial_grid(grid)
    
    # Act
    world.clear()
    
    # Assert
    assert len(world.entities) == 0
    assert world.entity_count == 0
    assert grid.clear_called
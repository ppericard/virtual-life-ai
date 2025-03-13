"""Tests for the system module."""

from dataclasses import dataclass
from typing import List, Type, Set, Optional, Any
import pytest
from uuid import UUID, uuid4

from virtuallife.ecs.system import System
from virtuallife.ecs.entity import Entity
from virtuallife.ecs.component import Component


@dataclass
class TestComponent:
    """Test component for testing systems."""
    
    value: int = 0
    
    def update(self, entity: Any, world: Any, dt: float) -> None:
        """Update the component.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update
        """
        self.value += 1


@dataclass
class AnotherComponent:
    """Another test component for testing systems."""
    
    name: str = "test"
    
    def update(self, entity: Any, world: Any, dt: float) -> None:
        """Update the component.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update
        """
        self.name = f"{self.name}_updated"


class TestSystem(System):
    """Concrete implementation of the System abstract class for testing."""
    
    def __init__(self) -> None:
        """Initialize the system."""
        super().__init__()
        self.processed_entities: Set[UUID] = set()
        self.entity_added_called = False
        self.entity_removed_called = False
        self.last_added_entity: Optional[Entity] = None
        self.last_removed_entity_id: Optional[UUID] = None
    
    @property
    def required_components(self) -> List[Type[Any]]:
        """Get the component types required for an entity to be processed by this system.
        
        Returns:
            A list of component types that an entity must have to be processed
        """
        return [TestComponent]
    
    def process(self, world: Any, dt: float) -> None:
        """Process all registered entities.
        
        Args:
            world: The world containing the entities
            dt: Time delta since last update
        """
        for entity_id in self.entities:
            self.processed_entities.add(entity_id)
    
    def _on_entity_added(self, entity: Entity) -> None:
        """Called when an entity is added to this system.
        
        Args:
            entity: The entity that was added
        """
        self.entity_added_called = True
        self.last_added_entity = entity
    
    def _on_entity_removed(self, entity_id: UUID) -> None:
        """Called when an entity is removed from this system.
        
        Args:
            entity_id: The ID of the entity that was removed
        """
        self.entity_removed_called = True
        self.last_removed_entity_id = entity_id


class ComplexSystem(System):
    """System that requires multiple components."""
    
    @property
    def required_components(self) -> List[Type[Any]]:
        """Get the component types required for an entity to be processed by this system.
        
        Returns:
            A list of component types that an entity must have to be processed
        """
        return [TestComponent, AnotherComponent]
    
    def process(self, world: Any, dt: float) -> None:
        """Process all registered entities.
        
        Args:
            world: The world containing the entities
            dt: Time delta since last update
        """
        pass


class MockWorld:
    """Mock world for testing systems."""
    
    def __init__(self) -> None:
        """Initialize the mock world."""
        self.entities: dict[UUID, Entity] = {}
    
    def get_entity(self, entity_id: UUID) -> Optional[Entity]:
        """Get an entity by ID.
        
        Args:
            entity_id: The ID of the entity to get
            
        Returns:
            The entity if it exists, None otherwise
        """
        return self.entities.get(entity_id)


def test_system_initialization():
    """Test that systems can be initialized."""
    # Act
    system = TestSystem()
    
    # Assert
    assert isinstance(system.entities, set)
    assert len(system.entities) == 0
    assert system.enabled
    assert system.priority == 0


def test_matches_entity():
    """Test that systems can check if an entity matches their requirements."""
    # Arrange
    system = TestSystem()
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    
    # Act & Assert
    assert system.matches_entity(entity)


def test_not_matches_entity_missing_component():
    """Test that systems don't match entities missing required components."""
    # Arrange
    system = TestSystem()
    entity = Entity()
    
    # Act & Assert
    assert not system.matches_entity(entity)


def test_not_matches_entity_system_disabled():
    """Test that disabled systems don't match any entities."""
    # Arrange
    system = TestSystem()
    system.disable()
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    
    # Act & Assert
    assert not system.matches_entity(entity)


def test_complex_system_matches_entity():
    """Test that systems with multiple required components match correctly."""
    # Arrange
    system = ComplexSystem()
    entity = Entity()
    component1 = TestComponent(value=42)
    component2 = AnotherComponent(name="test")
    entity.add_component(component1)
    entity.add_component(component2)
    
    # Act & Assert
    assert system.matches_entity(entity)


def test_complex_system_not_matches_entity_missing_component():
    """Test that systems with multiple required components don't match entities missing components."""
    # Arrange
    system = ComplexSystem()
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    
    # Act & Assert
    assert not system.matches_entity(entity)


def test_register_entity():
    """Test that entities can be registered with systems."""
    # Arrange
    system = TestSystem()
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    
    # Act
    system.register_entity(entity)
    
    # Assert
    assert entity.id in system.entities
    assert system.entity_added_called
    assert system.last_added_entity == entity


def test_register_entity_not_matching():
    """Test that non-matching entities aren't registered with systems."""
    # Arrange
    system = TestSystem()
    entity = Entity()
    
    # Act
    system.register_entity(entity)
    
    # Assert
    assert entity.id not in system.entities
    assert not system.entity_added_called
    assert system.last_added_entity is None


def test_unregister_entity():
    """Test that entities can be unregistered from systems."""
    # Arrange
    system = TestSystem()
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    system.register_entity(entity)
    
    # Act
    system.unregister_entity(entity.id)
    
    # Assert
    assert entity.id not in system.entities
    assert system.entity_removed_called
    assert system.last_removed_entity_id == entity.id


def test_unregister_entity_not_registered():
    """Test that unregistering a non-registered entity has no effect."""
    # Arrange
    system = TestSystem()
    entity_id = uuid4()
    
    # Act
    system.unregister_entity(entity_id)
    
    # Assert
    assert entity_id not in system.entities
    assert not system.entity_removed_called
    assert system.last_removed_entity_id is None


def test_process():
    """Test that systems can process entities."""
    # Arrange
    system = TestSystem()
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    system.register_entity(entity)
    world = MockWorld()
    
    # Act
    system.process(world, 1.0)
    
    # Assert
    assert entity.id in system.processed_entities


def test_enable_disable():
    """Test that systems can be enabled and disabled."""
    # Arrange
    system = TestSystem()
    
    # Assert
    assert system.enabled
    assert system.is_enabled
    
    # Act
    system.disable()
    
    # Assert
    assert not system.enabled
    assert not system.is_enabled
    
    # Act
    system.enable()
    
    # Assert
    assert system.enabled
    assert system.is_enabled


def test_set_priority():
    """Test that system priority can be set."""
    # Arrange
    system = TestSystem()
    
    # Assert
    assert system.priority == 0
    assert system.get_priority == 0
    
    # Act
    system.set_priority(10)
    
    # Assert
    assert system.priority == 10
    assert system.get_priority == 10 
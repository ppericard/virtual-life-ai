"""Tests for the entity module."""

from dataclasses import dataclass
import pytest
from typing import Any, Optional, Type
from uuid import UUID

from virtuallife.ecs.entity import Entity
from virtuallife.ecs.component import Component
from virtuallife.types.core import Position


@dataclass
class TestComponent:
    """Test component for testing the Entity class."""
    
    value: int = 0
    updated: bool = False
    
    def update(self, entity: Any, world: Any, dt: float) -> None:
        """Update the component.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update
        """
        self.updated = True
        self.value += 1


@dataclass
class AnotherComponent:
    """Another test component for testing the Entity class."""
    
    name: str = "test"
    
    def update(self, entity: Any, world: Any, dt: float) -> None:
        """Update the component.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update
        """
        self.name = f"{self.name}_updated"


def test_entity_creation():
    """Test that entities can be created."""
    # Act
    entity = Entity()
    
    # Assert
    assert isinstance(entity.id, UUID)
    assert entity.position == (0, 0)
    assert hasattr(entity, "_components")
    assert len(entity._components) == 0


def test_entity_creation_with_position():
    """Test that entities can be created with a position."""
    # Act
    entity = Entity(position=(10, 20))
    
    # Assert
    assert entity.position == (10, 20)


def test_add_component():
    """Test that components can be added to entities."""
    # Arrange
    entity = Entity()
    component = TestComponent(value=42)
    
    # Act
    entity.add_component(component)
    
    # Assert
    assert entity.has_component(TestComponent)
    assert entity.get_component(TestComponent) == component
    assert entity.is_dirty


def test_add_duplicate_component():
    """Test that adding a duplicate component raises an error."""
    # Arrange
    entity = Entity()
    component1 = TestComponent(value=42)
    component2 = TestComponent(value=100)
    entity.add_component(component1)
    
    # Act & Assert
    with pytest.raises(ValueError):
        entity.add_component(component2)


def test_remove_component():
    """Test that components can be removed from entities."""
    # Arrange
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    entity.mark_clean()
    
    # Act
    entity.remove_component(TestComponent)
    
    # Assert
    assert not entity.has_component(TestComponent)
    assert entity.get_component(TestComponent) is None
    assert entity.is_dirty


def test_remove_nonexistent_component():
    """Test that removing a nonexistent component has no effect."""
    # Arrange
    entity = Entity()
    entity.mark_clean()
    
    # Act
    entity.remove_component(TestComponent)
    
    # Assert
    assert not entity.has_component(TestComponent)
    assert entity.get_component(TestComponent) is None
    assert not entity.is_dirty  # Should not be marked dirty as nothing changed


def test_get_component():
    """Test that components can be retrieved from entities."""
    # Arrange
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    
    # Act
    retrieved = entity.get_component(TestComponent)
    
    # Assert
    assert retrieved == component
    assert retrieved.value == 42


def test_get_nonexistent_component():
    """Test that retrieving a nonexistent component returns None."""
    # Arrange
    entity = Entity()
    
    # Act
    component = entity.get_component(TestComponent)
    
    # Assert
    assert component is None


def test_has_component():
    """Test that entities can check if they have a component."""
    # Arrange
    entity = Entity()
    component = TestComponent(value=42)
    entity.add_component(component)
    
    # Act & Assert
    assert entity.has_component(TestComponent)
    assert not entity.has_component(AnotherComponent)


def test_get_components():
    """Test that all components can be retrieved from an entity."""
    # Arrange
    entity = Entity()
    component1 = TestComponent(value=42)
    component2 = AnotherComponent(name="test")
    entity.add_component(component1)
    entity.add_component(component2)
    
    # Act
    components = entity.get_components()
    
    # Assert
    assert len(components) == 2
    assert component1 in components
    assert component2 in components


def test_update():
    """Test that entities can update their components."""
    # Arrange
    entity = Entity()
    component1 = TestComponent(value=10)
    component2 = AnotherComponent(name="test")
    entity.add_component(component1)
    entity.add_component(component2)
    
    # Act
    entity.update(None, 1.0)
    
    # Assert
    assert component1.updated
    assert component1.value == 11
    assert component2.name == "test_updated"


def test_dirty_flag():
    """Test that the dirty flag is set correctly."""
    # Arrange
    entity = Entity()
    
    # Assert
    assert entity.is_dirty  # Should be dirty on creation
    
    # Act
    entity.mark_clean()
    
    # Assert
    assert not entity.is_dirty
    
    # Act
    component = TestComponent(value=42)
    entity.add_component(component)
    
    # Assert
    assert entity.is_dirty
    
    # Act
    entity.mark_clean()
    entity.remove_component(TestComponent)
    
    # Assert
    assert entity.is_dirty 
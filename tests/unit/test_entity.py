"""Unit tests for the Entity class."""

from dataclasses import dataclass
from typing import Any
import pytest

from virtuallife.simulation.entity import Entity, Component


@dataclass
class MockComponent:
    """Mock component for testing."""
    value: int = 0
    
    def update(self, entity: Entity, environment: Any) -> None:
        """Update the component state."""
        self.value += 1


@dataclass
class AnotherMockComponent:
    """Another mock component for testing."""
    name: str = "test"
    
    def update(self, entity: Entity, environment: Any) -> None:
        """Update the component state."""
        pass


def test_entity_initialization():
    """Test entity initialization with default values."""
    entity = Entity()
    assert entity.id is not None
    assert entity.position == (0, 0)
    assert len(entity.components) == 0


def test_entity_initialization_with_position():
    """Test entity initialization with custom position."""
    entity = Entity(position=(10, 20))
    assert entity.position == (10, 20)


def test_add_component():
    """Test adding a component to an entity."""
    entity = Entity()
    component = MockComponent()
    entity.add_component("test", component)
    assert entity.has_component("test")
    assert entity.get_component("test") == component


def test_add_duplicate_component():
    """Test that adding a duplicate component raises an error."""
    entity = Entity()
    component = MockComponent()
    entity.add_component("test", component)
    
    with pytest.raises(ValueError):
        entity.add_component("test", MockComponent())


def test_remove_component():
    """Test removing a component from an entity."""
    entity = Entity()
    component = MockComponent()
    entity.add_component("test", component)
    assert entity.has_component("test")
    
    entity.remove_component("test")
    assert not entity.has_component("test")
    assert entity.get_component("test") is None


def test_remove_nonexistent_component():
    """Test removing a component that doesn't exist."""
    entity = Entity()
    # Should not raise an error
    entity.remove_component("nonexistent")


def test_get_component_typed():
    """Test getting a component with type checking."""
    entity = Entity()
    component = MockComponent(value=42)
    entity.add_component("test", component)
    
    # Get with correct type
    typed_component = entity.get_component_typed("test", MockComponent)
    assert typed_component is not None
    assert typed_component.value == 42
    
    # Get nonexistent component
    assert entity.get_component_typed("nonexistent", MockComponent) is None


def test_update():
    """Test updating all components of an entity."""
    entity = Entity()
    component1 = MockComponent(value=0)
    component2 = MockComponent(value=10)
    
    entity.add_component("comp1", component1)
    entity.add_component("comp2", component2)
    
    # Update should call update on all components
    entity.update(None)  # None as environment for testing
    
    assert component1.value == 1
    assert component2.value == 11


def test_multiple_component_types():
    """Test entity with different types of components."""
    entity = Entity()
    mock_comp = MockComponent(value=42)
    another_comp = AnotherMockComponent(name="test")
    
    entity.add_component("mock", mock_comp)
    entity.add_component("another", another_comp)
    
    assert entity.get_component_typed("mock", MockComponent) == mock_comp
    assert entity.get_component_typed("another", AnotherMockComponent) == another_comp 
"""Tests for the component module."""

from dataclasses import dataclass
import pytest
from typing import Dict, Type, Any

from virtuallife.ecs.component import (
    Component, 
    register_component, 
    get_component_class, 
    get_component_type,
    ComponentRegistry
)


@dataclass
class TestComponent:
    """Test component implementation."""
    
    value: int = 0
    
    def update(self, entity: Any, world: Any, dt: float) -> None:
        """Update the component.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update
        """
        self.value += 1


def test_component_protocol():
    """Test that a class implementing the required methods satisfies the Component protocol."""
    # Arrange
    component = TestComponent(value=42)
    
    # Act & Assert
    assert isinstance(component, Component)


def test_component_update():
    """Test that the update method works as expected."""
    # Arrange
    component = TestComponent(value=10)
    
    # Act
    component.update(None, None, 1.0)
    
    # Assert
    assert component.value == 11


@register_component
class RegisteredComponent:
    """A component registered with the component registry."""
    
    def update(self, entity: Any, world: Any, dt: float) -> None:
        """Update method to satisfy Component protocol."""
        pass


def test_register_component():
    """Test that components can be registered."""
    # Assert
    assert "RegisteredComponent" in ComponentRegistry
    assert ComponentRegistry["RegisteredComponent"] == RegisteredComponent


def test_get_component_class():
    """Test that component classes can be retrieved by name."""
    # Act
    component_class = get_component_class("RegisteredComponent")
    
    # Assert
    assert component_class == RegisteredComponent


def test_get_component_class_not_found():
    """Test that getting a non-existent component class raises an error."""
    # Act & Assert
    with pytest.raises(KeyError):
        get_component_class("NonExistentComponent")


def test_get_component_type():
    """Test that the type of a component instance can be retrieved."""
    # Arrange
    component = RegisteredComponent()
    
    # Act
    component_type = get_component_type(component)
    
    # Assert
    assert component_type == RegisteredComponent 
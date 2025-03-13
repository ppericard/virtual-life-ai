"""Component module for the ECS architecture.

This module defines the Component protocol which all components must implement.
Components contain data and behavior that can be attached to entities.

Examples:
    >>> from dataclasses import dataclass
    >>> from virtuallife.ecs.component import Component
    >>> from typing import TYPE_CHECKING
    >>> if TYPE_CHECKING:
    ...     from virtuallife.ecs.entity import Entity
    ...     from virtuallife.ecs.world import World
    ...
    >>> @dataclass
    ... class HealthComponent:
    ...     health: int = 100
    ...     max_health: int = 100
    ...     
    ...     def update(self, entity: "Entity", world: "World", dt: float) -> None:
    ...         # Health regeneration logic would go here
    ...         pass
"""

from typing import Protocol, Any, Type, Dict, TypeVar, runtime_checkable, cast, get_type_hints, final, ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from virtuallife.ecs.entity import Entity
    from virtuallife.ecs.world import World


@runtime_checkable
class Component(Protocol):
    """Protocol defining the interface for entity components.
    
    All components must implement this protocol to be usable with the Entity class.
    Components contain data and behavior that can be attached to entities.
    
    Components are processed by systems based on their type. Each entity can have
    at most one component of each type.
    """
    
    def update(self, entity: "Entity", world: "World", dt: float) -> None:
        """Update the component state.
        
        This method is called by systems during the update cycle. It should
        update the component's state based on the current entity and world state.
        
        Args:
            entity: The entity this component belongs to
            world: The world the entity exists in
            dt: Time delta since last update in seconds
        """
        ...


# Component registry for type lookups
ComponentRegistry: Dict[str, Type[Any]] = {}


def register_component(component_class: Type[Any]) -> Type[Any]:
    """Register a component class in the registry.
    
    This is a decorator that can be used to register component classes
    in the component registry. This is useful for reflection and
    serialization.
    
    Args:
        component_class: The component class to register
        
    Returns:
        The component class (unchanged)
        
    Example:
        >>> @register_component
        ... class HealthComponent:
        ...     health: int = 100
    """
    if hasattr(component_class, "__name__"):
        ComponentRegistry[component_class.__name__] = component_class
    return component_class


def get_component_class(name: str) -> Type[Any]:
    """Get a component class by name.
    
    Args:
        name: The name of the component class
        
    Returns:
        The component class
        
    Raises:
        KeyError: If no component with the given name is registered
    """
    if name not in ComponentRegistry:
        raise KeyError(f"No component with name {name} is registered")
    return ComponentRegistry[name]


T = TypeVar('T')


def get_component_type(component: Any) -> Type[Any]:
    """Get the type of a component instance.
    
    Args:
        component: The component instance
        
    Returns:
        The component type
    """
    return type(component) 
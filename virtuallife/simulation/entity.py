"""Entity module for the VirtualLife simulation.

This module provides the Entity class and the Component protocol, which form the
foundation of the entity-component system used in the simulation.
"""

from dataclasses import dataclass, field
from typing import Dict, Protocol, TypeVar, cast, Optional, Type
from uuid import UUID, uuid4


class Component(Protocol):
    """Protocol defining the interface for entity components.
    
    All components must implement this protocol to be usable with the Entity class.
    The update method is called on each simulation step.
    """
    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Update the component state.
        
        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        ...


# Define a type variable for components that implement the Component protocol
C = TypeVar("C", bound=Component)


@dataclass
class Entity:
    """Base entity class using composition for behaviors.
    
    Entities are the primary objects in the simulation. They exist in the environment
    and can have various components that define their behavior.
    
    Attributes:
        id: Unique identifier for the entity
        position: The (x, y) position of the entity in the environment
        components: Dictionary mapping component names to components
    """
    id: UUID = field(default_factory=uuid4)
    position: tuple[int, int] = field(default=(0, 0))
    components: Dict[str, Component] = field(default_factory=dict)
    
    def add_component(self, name: str, component: Component) -> None:
        """Add a component to the entity.
        
        Args:
            name: The name of the component
            component: The component to add
            
        Raises:
            ValueError: If a component with the same name already exists
        """
        if name in self.components:
            raise ValueError(f"Component {name} already exists on this entity")
        self.components[name] = component
    
    def remove_component(self, name: str) -> None:
        """Remove a component from the entity.
        
        Args:
            name: The name of the component to remove
        """
        if name in self.components:
            del self.components[name]
    
    def has_component(self, name: str) -> bool:
        """Check if the entity has a specific component.
        
        Args:
            name: The name of the component
            
        Returns:
            True if the entity has the component, False otherwise
        """
        return name in self.components
    
    def get_component(self, name: str) -> Optional[Component]:
        """Get a component by name.
        
        Args:
            name: The name of the component
            
        Returns:
            The component if it exists, None otherwise
        """
        return self.components.get(name)
    
    def get_component_typed(self, name: str, component_type: Type[C]) -> Optional[C]:
        """Get a component by name with type checking.
        
        Args:
            name: The name of the component
            component_type: The expected type of the component
            
        Returns:
            The component if it exists and matches the type, None otherwise
        """
        component = self.get_component(name)
        if component is not None and isinstance(component, component_type):
            return cast(component_type, component)
        return None
    
    def update(self, environment: "Environment") -> None:
        """Update the entity's state by updating all components.
        
        Args:
            environment: The environment the entity exists in
        """
        # Update each component
        for component in self.components.values():
            try:
                component.update(self, environment)
            except Exception as e:
                # Log the error but continue with other components
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error updating component {component}: {str(e)}") 
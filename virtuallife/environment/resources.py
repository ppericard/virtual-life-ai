"""Resource management for the VirtualLife simulation.

This module provides the ResourceManager class, which is responsible for
tracking and managing resources in the simulation environment. Resources
can be added, removed, and updated at specific positions.

Examples:
    >>> from virtuallife.environment.resources import ResourceManager
    >>> from virtuallife.types import Position
    >>> 
    >>> # Create a resource manager
    >>> resource_mgr = ResourceManager()
    >>> 
    >>> # Add some resources
    >>> resource_mgr.add_resource("food", (10, 20), 100)
    >>> resource_mgr.add_resource("water", (30, 40), 50)
    >>> 
    >>> # Get resources at a position
    >>> resources = resource_mgr.get_resources_at_position((10, 20))
    >>> resources
    {'food': 100}
    >>> 
    >>> # Consume a resource
    >>> resource_mgr.consume_resource("food", (10, 20), 30)
    >>> resource_mgr.get_resource_amount("food", (10, 20))
    70
"""

from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, List, Optional, Any, Iterator
from collections import defaultdict

from virtuallife.types import Position


@dataclass
class ResourceManager:
    """Manages resources in the simulation environment.
    
    The ResourceManager class tracks resources across the environment,
    allowing for the addition, removal, and updating of resources at
    specific positions.
    
    Attributes:
        resources: Dictionary mapping resource types to position-amount mappings
    """
    
    _resources: Dict[str, Dict[Position, float]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(float))
    )
    
    def add_resource(self, resource_type: str, position: Position, amount: float) -> None:
        """Add a resource at the specified position.
        
        Args:
            resource_type: The type of resource to add
            position: The position to add the resource at
            amount: The amount to add
        """
        self._resources[resource_type][position] += amount
    
    def remove_resource(self, resource_type: str, position: Position) -> None:
        """Remove a resource from the specified position.
        
        Args:
            resource_type: The type of resource to remove
            position: The position to remove the resource from
        """
        if resource_type in self._resources and position in self._resources[resource_type]:
            del self._resources[resource_type][position]
            
            # Clean up empty resource types
            if not self._resources[resource_type]:
                del self._resources[resource_type]
    
    def get_resource_amount(self, resource_type: str, position: Position) -> float:
        """Get the amount of a resource at the specified position.
        
        Args:
            resource_type: The type of resource to get
            position: The position to get the resource amount for
            
        Returns:
            The amount of the resource, or 0.0 if the resource is not present
        """
        if resource_type not in self._resources:
            return 0.0
        
        return self._resources[resource_type].get(position, 0.0)
    
    def get_resources_at_position(self, position: Position) -> Dict[str, float]:
        """Get all resources at the specified position.
        
        Args:
            position: The position to get resources for
            
        Returns:
            A dictionary mapping resource types to amounts
        """
        result = {}
        for resource_type in self._resources:
            if position in self._resources[resource_type]:
                result[resource_type] = self._resources[resource_type][position]
        
        return result
    
    def get_resource_positions(self, resource_type: str) -> List[Position]:
        """Get all positions where a specific resource type exists.
        
        Args:
            resource_type: The type of resource to get positions for
            
        Returns:
            A list of positions where the resource exists
        """
        if resource_type not in self._resources:
            return []
        
        return list(self._resources[resource_type].keys())
    
    def consume_resource(
        self, resource_type: str, position: Position, amount: float
    ) -> float:
        """Consume a resource at the specified position.
        
        Args:
            resource_type: The type of resource to consume
            position: The position to consume the resource at
            amount: The amount to consume
            
        Returns:
            The actual amount consumed, which may be less than requested
            if there's not enough resource
        """
        if resource_type not in self._resources:
            return 0.0
        
        if position not in self._resources[resource_type]:
            return 0.0
        
        available = self._resources[resource_type][position]
        consumed = min(available, amount)
        
        self._resources[resource_type][position] -= consumed
        
        # Clean up if resource is depleted
        if self._resources[resource_type][position] <= 0:
            del self._resources[resource_type][position]
            
            # Clean up empty resource types
            if not self._resources[resource_type]:
                del self._resources[resource_type]
        
        return consumed
    
    def update_resource(
        self, resource_type: str, position: Position, amount: float
    ) -> None:
        """Update a resource at the specified position.
        
        If the resource doesn't exist, it will be created.
        
        Args:
            resource_type: The type of resource to update
            position: The position to update the resource at
            amount: The new amount of the resource
        """
        if amount <= 0:
            self.remove_resource(resource_type, position)
        else:
            self._resources[resource_type][position] = amount
    
    def transfer_resource(
        self,
        resource_type: str,
        from_position: Position,
        to_position: Position,
        amount: float,
    ) -> float:
        """Transfer a resource from one position to another.
        
        Args:
            resource_type: The type of resource to transfer
            from_position: The position to transfer from
            to_position: The position to transfer to
            amount: The amount to transfer
            
        Returns:
            The actual amount transferred, which may be less than requested
            if there's not enough resource
        """
        consumed = self.consume_resource(resource_type, from_position, amount)
        if consumed > 0:
            self.add_resource(resource_type, to_position, consumed)
        
        return consumed
    
    def get_all_resource_types(self) -> Set[str]:
        """Get all resource types in the environment.
        
        Returns:
            A set of all resource types
        """
        return set(self._resources.keys())
    
    def get_total_resource_amount(self, resource_type: str) -> float:
        """Get the total amount of a resource type in the environment.
        
        Args:
            resource_type: The type of resource to get the total amount for
            
        Returns:
            The total amount of the resource
        """
        if resource_type not in self._resources:
            return 0.0
        
        return sum(self._resources[resource_type].values())
    
    def clear(self) -> None:
        """Clear all resources from the environment."""
        self._resources.clear()
    
    def clear_resource_type(self, resource_type: str) -> None:
        """Clear all instances of a specific resource type.
        
        Args:
            resource_type: The type of resource to clear
        """
        if resource_type in self._resources:
            del self._resources[resource_type]
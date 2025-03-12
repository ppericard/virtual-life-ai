"""Standard components for the VirtualLife simulation.

This module provides the standard components that can be added to entities
to provide common behaviors like energy management and movement.
"""

from dataclasses import dataclass
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entity import Entity
    from .environment import Environment


@dataclass
class EnergyComponent:
    """Component for managing entity energy.
    
    This component handles energy levels, consumption, and death when energy
    is depleted.
    
    Attributes:
        energy: Current energy level
        max_energy: Maximum possible energy level
        decay_rate: Rate at which energy decreases per step
        death_threshold: Energy level at which the entity dies
    """
    energy: float = 100.0
    max_energy: float = 100.0
    decay_rate: float = 0.1
    death_threshold: float = 0.0
    
    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Update the energy level and handle death if energy is depleted.
        
        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        self.energy = max(0.0, self.energy - self.decay_rate)
        if self.energy <= self.death_threshold:
            environment.remove_entity(entity.id)
    
    def consume_energy(self, amount: float) -> bool:
        """Consume energy if available.
        
        Args:
            amount: Amount of energy to consume
            
        Returns:
            True if energy was consumed, False if not enough energy
        """
        if self.energy >= amount:
            self.energy = max(0.0, self.energy - amount)
            return True
        return False
    
    def add_energy(self, amount: float) -> None:
        """Add energy, not exceeding max_energy.
        
        Args:
            amount: Amount of energy to add
        """
        self.energy = min(self.max_energy, self.energy + amount)


@dataclass
class MovementComponent:
    """Component for entity movement.
    
    This component allows entities to move around the environment, with
    optional energy cost for movement.
    
    Attributes:
        speed: Movement speed (positions per step)
        movement_cost: Energy cost per unit of movement
    """
    speed: float = 1.0
    movement_cost: float = 0.1
    
    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Move the entity randomly within its speed limit.
        
        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        # Check for energy component
        energy_component = entity.get_component_typed("energy", EnergyComponent)
        if energy_component is not None and energy_component.energy <= 0:
            return
        
        # Calculate random movement
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        
        # Calculate energy cost based on actual movement
        distance = (abs(dx) + abs(dy)) * self.speed
        energy_cost = distance * self.movement_cost
        
        # Check if we have enough energy
        if energy_component is not None:
            if not energy_component.consume_energy(energy_cost):
                return
        
        # Update position
        x, y = entity.position
        new_pos = environment.normalize_position((x + dx, y + dy))
        
        # Update position in environment
        if entity.position in environment.entity_positions:
            environment.entity_positions[entity.position].remove(entity.id)
            if not environment.entity_positions[entity.position]:
                del environment.entity_positions[entity.position]
        
        entity.position = new_pos
        
        if new_pos not in environment.entity_positions:
            environment.entity_positions[new_pos] = set()
        environment.entity_positions[new_pos].add(entity.id)


@dataclass
class ResourceConsumerComponent:
    """Component for consuming resources from the environment.
    
    This component allows entities to consume resources and convert them
    to energy.
    
    Attributes:
        resource_type: Type of resource to consume
        consumption_rate: Amount of resource consumed per step
        energy_conversion: Energy gained per unit of resource
    """
    resource_type: str = "food"
    consumption_rate: float = 1.0
    energy_conversion: float = 0.5
    
    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Consume resources and convert them to energy.
        
        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        energy_component = entity.get_component_typed("energy", EnergyComponent)
        if energy_component is None:
            return
        
        # Get available resource at current position
        available = environment.get_resource(self.resource_type, entity.position)
        if available <= 0:
            return
        
        # Calculate how much we can consume
        to_consume = min(available, self.consumption_rate)
        
        # Convert to energy
        energy_gain = to_consume * self.energy_conversion
        energy_component.add_energy(energy_gain)
        
        # Update resource in environment
        new_amount = available - to_consume
        if new_amount > 0:
            environment.add_resource(self.resource_type, entity.position, new_amount)
        else:
            environment.remove_resource(self.resource_type, entity.position) 
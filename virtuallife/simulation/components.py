"""Standard components for the VirtualLife simulation.

This module provides the standard components that can be added to entities
to provide common behaviors like energy management and movement.
"""

from dataclasses import dataclass
import random
from typing import TYPE_CHECKING, Optional, Dict, Any
from uuid import uuid4

if TYPE_CHECKING:
    from virtuallife.simulation.entity import Entity
    from virtuallife.simulation.environment import Environment


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


class ReproductionComponent:
    """Component that handles entity reproduction."""

    def __init__(
        self,
        reproduction_threshold: float = 80.0,
        reproduction_cost: float = 50.0,
        reproduction_chance: float = 0.1,
        offspring_energy: float = 50.0,
        mutation_rate: float = 0.1,
        inherit_components: Optional[Dict[str, bool]] = None,
    ) -> None:
        """Initialize the reproduction component.

        Args:
            reproduction_threshold: Energy required to reproduce
            reproduction_cost: Energy cost of reproduction
            reproduction_chance: Chance to reproduce when conditions are met
            offspring_energy: Initial energy for offspring
            mutation_rate: Rate at which component values mutate
            inherit_components: Dict of component types to inherit (True) or not (False)
        """
        self.reproduction_threshold = reproduction_threshold
        self.reproduction_cost = reproduction_cost
        self.reproduction_chance = reproduction_chance
        self.offspring_energy = offspring_energy
        self.mutation_rate = mutation_rate
        self.inherit_components = inherit_components or {
            "energy": True,
            "movement": True,
            "consumer": True,
            "reproduction": True
        }

    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Update reproduction state and potentially create offspring.

        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        # Check for energy component
        energy_component = entity.get_component_typed("energy", EnergyComponent)
        if energy_component is None or energy_component.energy < self.reproduction_threshold:
            return

        # Random chance to reproduce
        if random.random() > self.reproduction_chance:
            return

        # Create offspring with inherited components
        from virtuallife.simulation.entity import Entity  # Import here to avoid circular imports
        offspring = Entity(position=entity.position)

        # Transfer energy cost from parent to offspring
        energy_component.energy -= self.reproduction_cost
        
        # Add components to offspring based on inheritance settings
        for component_type, should_inherit in self.inherit_components.items():
            if not should_inherit:
                continue
                
            parent_component = entity.get_component(component_type)
            if parent_component is not None:
                # Create a new component with potentially mutated values
                offspring_component = self._create_mutated_component(parent_component)
                offspring.add_component(component_type, offspring_component)
        
        # Ensure offspring has energy component with initial energy
        if "energy" in self.inherit_components and self.inherit_components["energy"]:
            energy = offspring.get_component_typed("energy", EnergyComponent)
            if energy is not None:
                energy.energy = self.offspring_energy
        
        # Add offspring to environment
        environment.add_entity(offspring)

    def _create_mutated_component(self, component: Any) -> Any:
        """Create a new component with potentially mutated values.
        
        Args:
            component: The parent component to mutate
        
        Returns:
            A new component instance with potentially mutated values
        """
        # Create a new instance of the same component type
        new_component = component.__class__()
        
        # Copy and potentially mutate numeric attributes
        for attr_name, value in vars(component).items():
            if isinstance(value, (int, float)):
                # Apply random mutation based on mutation rate
                if random.random() < self.mutation_rate:
                    mutation_factor = random.uniform(0.8, 1.2)  # ±20% mutation
                    mutated_value = value * mutation_factor
                    setattr(new_component, attr_name, mutated_value)
                else:
                    setattr(new_component, attr_name, value)
            else:
                # Copy non-numeric attributes as is
                setattr(new_component, attr_name, value)
        
        return new_component 
"""Standard components for the VirtualLife simulation.

This module provides the standard components that can be added to entities
to provide common behaviors like energy management and movement.
"""

import random
from typing import Any, Dict, Optional, TYPE_CHECKING

from virtuallife.config.models import (
    EnergyConfig,
    MovementConfig,
    ConsumerConfig,
    ReproductionConfig,
)

if TYPE_CHECKING:
    from virtuallife.simulation.entity import Entity
    from virtuallife.simulation.environment import Environment


class EnergyComponent:
    """Component that manages an entity's energy level."""

    def __init__(
        self,
        config: Optional[EnergyConfig] = None,
        energy: Optional[float] = None,
    ) -> None:
        """Initialize the energy component.

        Args:
            config: Configuration for the energy component
            energy: Initial energy level. If None, uses config's initial_energy
        """
        if config is None:
            config = EnergyConfig()
        self.config = config
        self.energy = energy if energy is not None else config.initial_energy
        self.max_energy = config.max_energy
        self.decay_rate = config.decay_rate
        self.death_threshold = config.death_threshold

    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Update the entity's energy level.

        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        # Apply energy decay
        old_energy = self.energy
        self.energy = max(0.0, old_energy - self.decay_rate)

        # Check for death if energy dropped below threshold or reached zero
        if (old_energy >= self.death_threshold and self.energy < self.death_threshold) or self.energy == 0.0:
            environment.remove_entity(entity)

    def consume_energy(self, amount: float) -> bool:
        """Consume energy if available.
        
        Args:
            amount: Amount of energy to consume
            
        Returns:
            True if energy was consumed, False if insufficient energy
        """
        if self.energy >= amount:
            self.energy = max(0.0, self.energy - amount)
            return True
        return False

    def add_energy(self, amount: float) -> None:
        """Add energy up to max_energy.
        
        Args:
            amount: Amount of energy to add
        """
        self.energy = min(self.max_energy, self.energy + amount)


class MovementComponent:
    """Component that handles entity movement."""

    def __init__(self, config: Optional[MovementConfig] = None) -> None:
        """Initialize the movement component.

        Args:
            config: Movement configuration parameters
        """
        self.config = config or MovementConfig()
        self.speed = self.config.speed
        self.movement_cost = self.config.movement_cost

    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Update entity position with random movement.

        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        # Get energy component
        energy_component = entity.get_component_typed("energy", EnergyComponent)
        if energy_component is None:
            return

        # Calculate movement cost
        movement_cost = self.movement_cost * self.speed
        
        # Check if we have enough energy to move
        if energy_component.energy < movement_cost:
            return
            
        # Consume energy for movement
        energy_component.energy -= movement_cost

        # Random movement
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        
        # Get current position
        x, y = entity.position
        new_pos = (x + dx, y + dy)
        
        # Update position through environment to handle boundaries
        environment.move_entity(entity, new_pos)


class ResourceConsumerComponent:
    """Component that handles resource consumption."""

    def __init__(self, config: Optional[ConsumerConfig] = None) -> None:
        """Initialize the resource consumer component.

        Args:
            config: Consumer configuration parameters
        """
        self.config = config or ConsumerConfig()
        self.resource_type = self.config.resource_type
        self.consumption_rate = self.config.consumption_rate
        self.energy_conversion = self.config.energy_conversion

    def update(self, entity: "Entity", environment: "Environment") -> None:
        """Consume resources and convert to energy.

        Args:
            entity: The entity this component belongs to
            environment: The environment the entity exists in
        """
        # Get energy component
        energy_component = entity.get_component_typed("energy", EnergyComponent)
        if energy_component is None:
            return

        # Try to consume resources
        consumed = environment.consume_resource(
            entity.position,
            self.resource_type,
            self.consumption_rate
        )
        
        if consumed > 0:
            # Convert resource to energy
            energy_gained = consumed * self.energy_conversion
            energy_component.add_energy(energy_gained)


class ReproductionComponent:
    """Component that handles entity reproduction."""

    def __init__(self, config: Optional[ReproductionConfig] = None) -> None:
        """Initialize the reproduction component.

        Args:
            config: Reproduction configuration parameters
        """
        self.config = config or ReproductionConfig()
        self.reproduction_threshold = self.config.reproduction_threshold
        self.reproduction_cost = self.config.reproduction_cost
        self.reproduction_chance = self.config.reproduction_chance
        self.offspring_energy = self.config.offspring_energy
        self.mutation_rate = self.config.mutation_rate
        self.inherit_components = self.config.inherit_components

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
"""Factory module for creating simulations and entities.

This module provides factory functions for creating simulations and entities
with specific configurations and behaviors.
"""

import random
import logging
from typing import Optional, Tuple

from virtuallife.config.models import SimulationConfig
from virtuallife.simulation.entity import Entity
from virtuallife.simulation.environment import Environment
from virtuallife.simulation.runner import SimulationRunner
from virtuallife.simulation.components import (
    EnergyComponent,
    MovementComponent,
    ReproductionComponent,
    ResourceConsumerComponent
)
from virtuallife.visualize.console import ConsoleVisualizer
from virtuallife.visualize.plotting import MatplotlibVisualizer

logger = logging.getLogger(__name__)


class MarkerComponent:
    """A simple marker component to identify entity types."""
    
    def __init__(self, marker_type: str):
        """Initialize the marker component.
        
        Args:
            marker_type: The type of marker (plant, herbivore, predator)
        """
        self.marker_type = marker_type
    
    def update(self, entity: Entity, environment: Environment) -> None:
        """Update method (no-op for markers).
        
        Args:
            entity: The entity this component belongs to
            environment: The simulation environment
        """
        pass


def create_plant(config: SimulationConfig, position: Tuple[int, int]) -> Entity:
    """Create a plant entity.
    
    Args:
        config: The simulation configuration
        position: The (x, y) position for the entity
        
    Returns:
        A new plant entity
    """
    entity = Entity(position=position)
    entity.add_component("energy", EnergyComponent(config=config.energy))
    entity.add_component("plant", MarkerComponent("plant"))
    return entity


def create_herbivore(config: SimulationConfig, position: Tuple[int, int]) -> Entity:
    """Create a herbivore entity.
    
    Args:
        config: The simulation configuration
        position: The (x, y) position for the entity
        
    Returns:
        A new herbivore entity
    """
    entity = Entity(position=position)
    entity.add_component("energy", EnergyComponent(config=config.energy))
    entity.add_component("movement", MovementComponent(config=config.movement))
    entity.add_component("reproduction", ReproductionComponent(config=config.reproduction))
    
    consumer_config = config.consumer.model_copy()
    consumer_config.resource_type = "plant"
    entity.add_component("consumer", ResourceConsumerComponent(config=consumer_config))
    entity.add_component("herbivore", MarkerComponent("herbivore"))
    
    # Configure reproduction to inherit marker
    config.reproduction.inherit_components["herbivore"] = True
    
    return entity


def create_predator(config: SimulationConfig, position: Tuple[int, int]) -> Entity:
    """Create a predator entity.
    
    Args:
        config: The simulation configuration
        position: The (x, y) position for the entity
        
    Returns:
        A new predator entity
    """
    entity = Entity(position=position)
    entity.add_component("energy", EnergyComponent(config=config.energy))
    entity.add_component("movement", MovementComponent(config=config.movement))
    entity.add_component("reproduction", ReproductionComponent(config=config.reproduction))
    
    consumer_config = config.consumer.model_copy()
    consumer_config.resource_type = "herbivore"
    entity.add_component("consumer", ResourceConsumerComponent(config=consumer_config))
    entity.add_component("predator", MarkerComponent("predator"))
    
    # Configure reproduction to inherit marker
    config.reproduction.inherit_components["predator"] = True
    
    return entity


def setup_simulation(
    config: SimulationConfig,
    visualizer_type: str = "none"
) -> Tuple[SimulationRunner, Optional[ConsoleVisualizer | MatplotlibVisualizer]]:
    """Set up a simulation with the given configuration.
    
    Args:
        config: The simulation configuration
        visualizer_type: The type of visualizer to use ("console", "matplotlib", or "none")
        
    Returns:
        A tuple containing the simulation runner and visualizer (if any)
    """
    # Set random seed if provided
    if config.random_seed is not None:
        random.seed(config.random_seed)
        logger.info(f"Using random seed: {config.random_seed}")
    
    # Initialize environment
    environment = Environment(
        width=config.environment.width,
        height=config.environment.height,
        boundary_condition=config.environment.boundary_condition
    )
    
    # Initialize resources
    for resource_type, value in config.resources.resource_types.items():
        for y in range(environment.height):
            for x in range(environment.width):
                if random.random() < config.resources.initial_density:
                    environment.add_resource(
                        resource_type,
                        (x, y),
                        random.uniform(0, config.resources.max_resource)
                    )
    
    # Create initial entities with different roles
    num_entities = config.environment.initial_entities
    num_plants = num_entities // 3
    num_herbivores = num_entities // 3
    num_predators = num_entities - num_plants - num_herbivores
    
    # Create and add entities
    for _ in range(num_plants):
        position = (random.randint(0, environment.width - 1),
                   random.randint(0, environment.height - 1))
        entity = create_plant(config, position)
        environment.add_entity(entity)
    
    for _ in range(num_herbivores):
        position = (random.randint(0, environment.width - 1),
                   random.randint(0, environment.height - 1))
        entity = create_herbivore(config, position)
        environment.add_entity(entity)
    
    for _ in range(num_predators):
        position = (random.randint(0, environment.width - 1),
                   random.randint(0, environment.height - 1))
        entity = create_predator(config, position)
        environment.add_entity(entity)
    
    # Create simulation runner
    runner = SimulationRunner(environment=environment, config=config.model_dump())
    
    # Set up visualization if requested
    visualizer = None
    if visualizer_type == "console":
        visualizer = ConsoleVisualizer()
        visualizer.setup(runner)
    elif visualizer_type == "matplotlib":
        visualizer = MatplotlibVisualizer()
        visualizer.setup(runner)
    
    return runner, visualizer 
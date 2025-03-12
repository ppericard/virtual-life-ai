"""Configuration models for the VirtualLife simulation.

This module defines the Pydantic models used for configuration management,
ensuring type safety and validation for all simulation parameters.
"""

from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field, NonNegativeFloat, PositiveFloat, PositiveInt


class EnergyConfig(BaseModel):
    """Configuration for energy-related parameters."""
    
    initial_energy: PositiveFloat = Field(
        default=100.0,
        description="Initial energy level for new entities"
    )
    max_energy: PositiveFloat = Field(
        default=100.0,
        description="Maximum possible energy level"
    )
    decay_rate: NonNegativeFloat = Field(
        default=0.1,
        description="Rate at which energy decreases per step"
    )
    death_threshold: NonNegativeFloat = Field(
        default=0.0,
        description="Energy level at which the entity dies"
    )


class MovementConfig(BaseModel):
    """Configuration for movement-related parameters."""
    
    speed: PositiveFloat = Field(
        default=1.0,
        description="Movement speed (positions per step)"
    )
    movement_cost: NonNegativeFloat = Field(
        default=0.1,
        description="Energy cost per unit of movement"
    )


class ResourceConfig(BaseModel):
    """Configuration for resource-related parameters."""
    
    resource_types: Dict[str, float] = Field(
        default={"food": 1.0},
        description="Dictionary of resource types and their base values"
    )
    initial_density: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Initial density of resources in the environment"
    )
    regrowth_rate: NonNegativeFloat = Field(
        default=0.05,
        description="Rate at which resources regrow per step"
    )
    max_resource: PositiveFloat = Field(
        default=10.0,
        description="Maximum amount of resource per cell"
    )


class ReproductionConfig(BaseModel):
    """Configuration for reproduction-related parameters."""
    
    reproduction_threshold: PositiveFloat = Field(
        default=80.0,
        description="Energy required to reproduce"
    )
    reproduction_cost: PositiveFloat = Field(
        default=50.0,
        description="Energy cost of reproduction"
    )
    reproduction_chance: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Chance to reproduce when conditions are met"
    )
    offspring_energy: PositiveFloat = Field(
        default=50.0,
        description="Initial energy for offspring"
    )
    mutation_rate: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Rate at which component values mutate"
    )
    inherit_components: Dict[str, bool] = Field(
        default={
            "energy": True,
            "movement": True,
            "consumer": True,
            "reproduction": True
        },
        description="Which components should be inherited by offspring"
    )


class ConsumerConfig(BaseModel):
    """Configuration for resource consumption parameters."""
    
    resource_type: str = Field(
        default="food",
        description="Type of resource to consume"
    )
    consumption_rate: PositiveFloat = Field(
        default=1.0,
        description="Amount of resource consumed per step"
    )
    energy_conversion: PositiveFloat = Field(
        default=0.5,
        description="Energy gained per unit of resource"
    )


class EnvironmentConfig(BaseModel):
    """Configuration for environment parameters."""
    
    width: PositiveInt = Field(
        default=100,
        description="Width of the environment grid"
    )
    height: PositiveInt = Field(
        default=100,
        description="Height of the environment grid"
    )
    boundary_condition: Literal["wrapped", "bounded"] = Field(
        default="wrapped",
        description="How to handle entities at environment boundaries"
    )
    initial_entities: PositiveInt = Field(
        default=10,
        description="Number of entities to create at simulation start"
    )


class SimulationConfig(BaseModel):
    """Main configuration for the simulation."""
    
    environment: EnvironmentConfig = Field(
        default_factory=EnvironmentConfig,
        description="Environment configuration"
    )
    energy: EnergyConfig = Field(
        default_factory=EnergyConfig,
        description="Energy component configuration"
    )
    movement: MovementConfig = Field(
        default_factory=MovementConfig,
        description="Movement component configuration"
    )
    reproduction: ReproductionConfig = Field(
        default_factory=ReproductionConfig,
        description="Reproduction component configuration"
    )
    consumer: ConsumerConfig = Field(
        default_factory=ConsumerConfig,
        description="Resource consumer configuration"
    )
    resources: ResourceConfig = Field(
        default_factory=ResourceConfig,
        description="Resource system configuration"
    )
    random_seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducible simulations"
    )
    max_steps: Optional[int] = Field(
        default=None,
        description="Maximum number of simulation steps (None for infinite)"
    ) 
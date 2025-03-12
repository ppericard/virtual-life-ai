"""Configuration package for VirtualLife simulation.

This package provides configuration management functionality using Pydantic models,
including loading from YAML files and validation.
"""

from virtuallife.config.models import (
    SimulationConfig,
    EnvironmentConfig,
    EnergyConfig,
    MovementConfig,
    ReproductionConfig,
    ConsumerConfig,
    ResourceConfig,
)
from virtuallife.config.loader import (
    load_config,
    save_config,
    get_default_config,
    load_or_default,
)

__all__ = [
    'SimulationConfig',
    'EnvironmentConfig',
    'EnergyConfig',
    'MovementConfig',
    'ReproductionConfig',
    'ConsumerConfig',
    'ResourceConfig',
    'load_config',
    'save_config',
    'get_default_config',
    'load_or_default',
] 
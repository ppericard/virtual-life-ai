"""Unit tests for the configuration system."""

import os
from pathlib import Path
import tempfile
import time

import pytest
import yaml
from pydantic import ValidationError

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


def test_default_config():
    """Test default configuration values."""
    config = get_default_config()
    
    # Test environment defaults
    assert config.environment.width == 100
    assert config.environment.height == 100
    assert config.environment.boundary_condition == "wrapped"
    assert config.environment.initial_entities == 10
    
    # Test energy defaults
    assert config.energy.initial_energy == 100.0
    assert config.energy.max_energy == 100.0
    assert config.energy.decay_rate == 0.1
    assert config.energy.death_threshold == 0.0
    
    # Test movement defaults
    assert config.movement.speed == 1.0
    assert config.movement.movement_cost == 0.1
    
    # Test reproduction defaults
    assert config.reproduction.reproduction_threshold == 80.0
    assert config.reproduction.reproduction_cost == 50.0
    assert config.reproduction.reproduction_chance == 0.1
    assert config.reproduction.offspring_energy == 50.0
    assert config.reproduction.mutation_rate == 0.1
    assert config.reproduction.inherit_components == {
        "energy": True,
        "movement": True,
        "consumer": True,
        "reproduction": True,
    }
    
    # Test consumer defaults
    assert config.consumer.resource_type == "food"
    assert config.consumer.consumption_rate == 1.0
    assert config.consumer.energy_conversion == 0.5
    
    # Test resource defaults
    assert config.resources.resource_types == {"food": 1.0}
    assert config.resources.initial_density == 0.1
    assert config.resources.regrowth_rate == 0.05
    assert config.resources.max_resource == 10.0
    
    # Test optional parameters
    assert config.random_seed is None
    assert config.max_steps is None


def test_config_validation():
    """Test configuration validation."""
    # Test invalid environment size
    with pytest.raises(ValidationError):
        EnvironmentConfig(width=-1, height=100)
    
    # Test invalid energy values
    with pytest.raises(ValidationError):
        EnergyConfig(initial_energy=-50.0)
    
    # Test invalid movement values
    with pytest.raises(ValidationError):
        MovementConfig(speed=-1.0)
    
    # Test invalid reproduction values
    with pytest.raises(ValidationError):
        ReproductionConfig(reproduction_chance=1.5)  # Must be between 0 and 1
    
    # Test invalid consumer values
    with pytest.raises(ValidationError):
        ConsumerConfig(consumption_rate=0.0)  # Must be positive
    
    # Test invalid resource values
    with pytest.raises(ValidationError):
        ResourceConfig(initial_density=2.0)  # Must be between 0 and 1


def test_save_and_load_config():
    """Test saving and loading configuration."""
    config = get_default_config()
    
    # Modify some values
    config.environment.width = 200
    config.energy.initial_energy = 150.0
    config.random_seed = 42
    
    # Create a temporary file path
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"test_config_{int(time.time())}.yaml")
    
    try:
        # Save config
        save_config(config, temp_path)
        
        # Load the saved config
        loaded_config = load_config(temp_path)
        
        # Verify loaded values match original
        assert loaded_config.environment.width == 200
        assert loaded_config.energy.initial_energy == 150.0
        assert loaded_config.random_seed == 42
        
        # Verify other values remain at defaults
        assert loaded_config.environment.height == 100
        assert loaded_config.energy.decay_rate == 0.1
    
    finally:
        # Clean up
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                pass  # Ignore Windows permission errors during cleanup


def test_load_nonexistent_file():
    """Test loading from a nonexistent file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")


def test_load_invalid_yaml():
    """Test loading invalid YAML."""
    # Create a temporary file path
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"test_invalid_{int(time.time())}.yaml")
    
    try:
        # Write invalid YAML
        with open(temp_path, 'w') as f:
            f.write("invalid: yaml: :")
        
        with pytest.raises(yaml.YAMLError):
            load_config(temp_path)
    
    finally:
        # Clean up
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                pass  # Ignore Windows permission errors during cleanup


def test_load_or_default():
    """Test load_or_default function."""
    # Test with no file
    config = load_or_default()
    assert isinstance(config, SimulationConfig)
    assert config.environment.width == 100  # Default value
    
    # Test with nonexistent file
    config = load_or_default("nonexistent.yaml")
    assert isinstance(config, SimulationConfig)
    assert config.environment.width == 100  # Default value
    
    # Test with valid file
    config = get_default_config()
    config.environment.width = 200
    
    # Create a temporary file path
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"test_load_{int(time.time())}.yaml")
    
    try:
        # Save and load config
        save_config(config, temp_path)
        loaded_config = load_or_default(temp_path)
        assert loaded_config.environment.width == 200
    
    finally:
        # Clean up
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                pass  # Ignore Windows permission errors during cleanup


def test_custom_config():
    """Test creating a custom configuration."""
    config = SimulationConfig(
        environment=EnvironmentConfig(
            width=500,
            height=500,
            boundary_condition="bounded",
            initial_entities=100
        ),
        energy=EnergyConfig(
            initial_energy=200.0,
            max_energy=300.0,
            decay_rate=0.05,
            death_threshold=10.0
        ),
        random_seed=42
    )
    
    assert config.environment.width == 500
    assert config.environment.height == 500
    assert config.environment.boundary_condition == "bounded"
    assert config.environment.initial_entities == 100
    assert config.energy.initial_energy == 200.0
    assert config.energy.max_energy == 300.0
    assert config.energy.decay_rate == 0.05
    assert config.energy.death_threshold == 10.0
    assert config.random_seed == 42
    
    # Verify other values remain at defaults
    assert config.movement.speed == 1.0
    assert config.reproduction.mutation_rate == 0.1 
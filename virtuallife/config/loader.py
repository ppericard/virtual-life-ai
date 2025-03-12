"""Configuration loading and saving functionality.

This module provides functions to load and save simulation configurations
from/to YAML files, with validation using Pydantic models.
"""

import os
from pathlib import Path
from typing import Optional, Union

import yaml
from pydantic import ValidationError

from virtuallife.config.models import SimulationConfig


def load_config(config_path: Union[str, Path]) -> SimulationConfig:
    """Load a configuration from a YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Loaded and validated configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If config file contains invalid values
        yaml.YAMLError: If config file is not valid YAML
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    try:
        config = SimulationConfig(**config_dict)
    except ValidationError as e:
        # Add file path context to validation error
        raise ValidationError(
            errors=e.errors(),
            model=e.model,
            title=f"Invalid configuration in {config_path}"
        ) from None
    
    return config


def save_config(config: SimulationConfig, config_path: Union[str, Path]) -> None:
    """Save a configuration to a YAML file.
    
    Args:
        config: Configuration to save
        config_path: Path where to save the configuration
        
    Raises:
        OSError: If unable to write to file
    """
    config_path = Path(config_path)
    
    # Create parent directories if they don't exist
    os.makedirs(config_path.parent, exist_ok=True)
    
    # Convert to dict and save as YAML
    config_dict = config.model_dump()
    with open(config_path, 'w') as f:
        yaml.safe_dump(config_dict, f, sort_keys=False)


def get_default_config() -> SimulationConfig:
    """Get a default configuration instance.
    
    Returns:
        Default configuration loaded from examples/configs/default.yaml,
        or a new instance with default values if the file is not found.
    """
    default_path = Path(__file__).parent.parent.parent / "examples" / "configs" / "default.yaml"
    try:
        return load_config(default_path)
    except (FileNotFoundError, ValidationError):
        return SimulationConfig()


def load_or_default(config_path: Optional[Union[str, Path]] = None) -> SimulationConfig:
    """Load configuration from file or return defaults if not found.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Loaded configuration or default if path not provided/file not found
    """
    if config_path is None:
        return get_default_config()
    
    try:
        return load_config(config_path)
    except FileNotFoundError:
        return get_default_config() 
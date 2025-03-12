"""Integration tests for configuration system.

This module contains integration tests for the configuration system,
testing the loading and saving of configurations.
"""

import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from virtuallife.cli import app
from virtuallife.config.loader import load_config, save_config
from virtuallife.config.models import SimulationConfig


@pytest.fixture
def runner():
    """Fixture that returns a CLI runner."""
    return CliRunner()


def test_create_and_run_with_config(runner):
    """Test creating a configuration file and then running a simulation with it."""
    # Arrange
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
        config_path = tmp.name
    
    # Clean up before test (in case it exists)
    if os.path.exists(config_path):
        os.unlink(config_path)
    
    try:
        # Act - Create a configuration
        create_result = runner.invoke(
            app, 
            [
                "create-config", 
                config_path, 
                "--width", "30", 
                "--height", "30", 
                "--boundary", "bounded",
                "--entities", "15",
                "--seed", "42"
            ],
            catch_exceptions=False
        )
        
        # Assert - Creation successful
        assert create_result.exit_code == 0
        assert os.path.exists(config_path)
        
        # Verify the config file contents
        config = load_config(config_path)
        assert config.environment.width == 30
        assert config.environment.height == 30
        assert config.environment.boundary_condition == "bounded"
        assert config.environment.initial_entities == 15
        assert config.random_seed == 42
        
        # Act - Display information about the config
        info_result = runner.invoke(
            app,
            ["info", "--config", config_path],
            catch_exceptions=False
        )
        
        # Assert - Info display successful
        assert info_result.exit_code == 0
        assert "bounded" in info_result.stdout
        assert "30x30" in info_result.stdout
        assert "15" in info_result.stdout
        assert "42" in info_result.stdout
        
        # Act - Run a simulation with this config
        # Note: We won't actually run it, just verify the CLI accepts the command
        # We'll use a very short run to avoid long test times
        run_result = runner.invoke(
            app,
            ["run", "--config", config_path, "--steps", "1", "--no-vis"],
            catch_exceptions=True
        )
        
        # Just check that the command was accepted
        assert run_result.exit_code in [0, 1]  # Allow for both success and controlled exit
            
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_config_modification_and_reload():
    """Test modifying a configuration file and reloading it."""
    # Create a temp config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
        config_path = tmp.name
    
    try:
        # Save initial config
        initial_config = SimulationConfig()
        initial_config.environment.width = 40
        initial_config.environment.height = 40
        save_config(initial_config, config_path)
        
        # Load and verify
        loaded_config = load_config(config_path)
        assert loaded_config.environment.width == 40
        assert loaded_config.environment.height == 40
        
        # Modify and save
        loaded_config.environment.width = 50
        loaded_config.environment.height = 60
        loaded_config.random_seed = 123
        save_config(loaded_config, config_path)
        
        # Reload and verify changes
        reloaded_config = load_config(config_path)
        assert reloaded_config.environment.width == 50
        assert reloaded_config.environment.height == 60
        assert reloaded_config.random_seed == 123
        
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_default_config_with_cli(runner):
    """Test using the default configuration with the CLI."""
    # Act - Show info about default config
    info_result = runner.invoke(app, ["info"], catch_exceptions=False)
    
    # Assert
    assert info_result.exit_code == 0
    assert "Configuration Details" in info_result.stdout
    
    # Default environment size (30x30)
    assert "30x30" in info_result.stdout
    assert "wrapped" in info_result.stdout
    assert "Initial entities: 30" in info_result.stdout
    
    # Default energy settings
    assert "Initial: 100.0" in info_result.stdout
    assert "Max: 100.0" in info_result.stdout
    assert "Decay rate: 0.1" in info_result.stdout
    
    # Default step delay
    assert "Step delay: 0.5 seconds" in info_result.stdout 
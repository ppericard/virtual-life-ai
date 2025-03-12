"""Functional tests for default configuration behavior.

This module contains end-to-end tests that verify the simulation behavior
using the default configuration from examples/configs/default.yaml.
"""

import time
from pathlib import Path
from unittest import mock

import pytest
from typer.testing import CliRunner

from virtuallife.cli import app
from virtuallife.config.loader import load_or_default
from virtuallife.simulation.environment import Environment
from virtuallife.simulation.runner import SimulationRunner


def test_default_config_loading():
    """Test that the default configuration is loaded correctly."""
    # Load default configuration
    config = load_or_default(None)
    
    # Verify default values
    assert config.environment.width == 30
    assert config.environment.height == 30
    assert config.environment.initial_entities == 30
    assert config.environment.boundary_condition == "wrapped"
    assert config.step_delay == 0.5
    assert config.random_seed is None
    assert config.max_steps is None


@pytest.fixture
def mock_time():
    """Fixture to mock time.sleep for testing delays."""
    with mock.patch('virtuallife.simulation.runner.time.sleep') as mock_sleep:
        yield mock_sleep


@mock.patch("virtuallife.cli.setup_simulation")
def test_simulation_with_default_config(mock_setup_simulation, mock_time):
    """Test running a complete simulation with default configuration."""
    # Arrange
    mock_environment = Environment(30, 30)
    mock_runner = mock.MagicMock()
    mock_visualizer = mock.MagicMock()
    mock_setup_simulation.return_value = (mock_runner, mock_visualizer)
    
    # Configure mock runner to simulate steps and use config
    def run_with_steps(steps=None):
        mock_runner.current_step = 0
        for _ in range(steps or 0):
            mock_runner.current_step += 1
            if "step_delay" in mock_runner.config:
                time.sleep(mock_runner.config["step_delay"])
    mock_runner.run.side_effect = run_with_steps
    
    # Mock runner will receive config as a dictionary
    def setup_sim_side_effect(config, vis_type):
        mock_runner.config = config.model_dump()
        return mock_runner, mock_visualizer
    mock_setup_simulation.side_effect = setup_sim_side_effect
    
    runner = CliRunner()
    
    # Act - Run simulation with default config and fixed seed
    result = runner.invoke(
        app,
        ["run", "--seed", "42", "--steps", "10"],
        catch_exceptions=False
    )
    
    # Assert
    assert result.exit_code == 0
    mock_setup_simulation.assert_called_once()
    
    # Verify the configuration passed to setup_simulation
    config = mock_setup_simulation.call_args[0][0]
    assert config.environment.width == 30
    assert config.environment.height == 30
    assert config.environment.initial_entities == 30
    assert config.random_seed == 42
    assert config.max_steps == 10
    assert config.step_delay == 0.5
    
    # Verify simulation was run
    mock_runner.run.assert_called_once_with(10)
    
    # Verify step delay was respected
    assert mock_time.call_count == 10  # Should be called once per step
    mock_time.assert_called_with(0.5)


@mock.patch("virtuallife.cli.setup_simulation")
def test_step_delay_override(mock_setup_simulation, mock_time):
    """Test that step delay can be overridden via command line."""
    # Arrange
    mock_environment = Environment(30, 30)
    mock_runner = mock.MagicMock()
    mock_visualizer = mock.MagicMock()
    mock_setup_simulation.return_value = (mock_runner, mock_visualizer)
    
    # Configure mock runner to simulate steps and use config
    def run_with_steps(steps=None):
        mock_runner.current_step = 0
        for _ in range(steps or 0):
            mock_runner.current_step += 1
            if "step_delay" in mock_runner.config:
                time.sleep(mock_runner.config["step_delay"])
    mock_runner.run.side_effect = run_with_steps
    
    # Mock runner will receive config as a dictionary
    def setup_sim_side_effect(config, vis_type):
        mock_runner.config = config.model_dump()
        return mock_runner, mock_visualizer
    mock_setup_simulation.side_effect = setup_sim_side_effect
    
    runner = CliRunner()
    
    # Act - Run with custom delay
    result = runner.invoke(
        app,
        ["run", "--seed", "42", "--steps", "5", "--delay", "0.1"],
        catch_exceptions=False
    )
    
    # Assert
    assert result.exit_code == 0
    
    # Verify the configuration
    config = mock_setup_simulation.call_args[0][0]
    assert config.step_delay == 0.1
    
    # Verify delay was used
    assert mock_time.call_count == 5  # Should be called once per step
    mock_time.assert_called_with(0.1)


def test_info_command_with_default_config():
    """Test that the info command correctly displays default configuration."""
    runner = CliRunner()
    
    # Run info command
    result = runner.invoke(app, ["info"])
    
    # Verify output contains expected default values
    assert result.exit_code == 0
    assert "30x30" in result.stdout  # Environment size
    assert "wrapped" in result.stdout  # Boundary condition
    assert "30" in result.stdout  # Initial entities
    assert "0.5 seconds" in result.stdout  # Step delay
    assert "Initial: 100.0" in result.stdout  # Initial energy
    assert "0.1" in result.stdout  # Decay rate
    assert "food" in result.stdout  # Resource type


@mock.patch("virtuallife.cli.setup_simulation")
def test_visualization_modes(mock_setup_simulation):
    """Test that different visualization modes work with default config."""
    # Arrange
    mock_environment = Environment(30, 30)
    mock_runner = mock.MagicMock()
    mock_visualizer = mock.MagicMock()
    mock_setup_simulation.return_value = (mock_runner, mock_visualizer)
    
    runner = CliRunner()
    
    # Test each visualization mode
    for vis_mode in ["console", "matplotlib", "none"]:
        # Reset mock
        mock_setup_simulation.reset_mock()
        
        # Run with specific visualizer
        args = ["run", "--steps", "3"]
        if vis_mode == "none":
            args.append("--no-vis")
        else:
            args.extend(["--visualizer", vis_mode])
            
        result = runner.invoke(app, args, catch_exceptions=False)
        
        # Verify
        assert result.exit_code == 0
        if vis_mode == "none":
            assert mock_setup_simulation.call_args[0][1] == "none"
        else:
            assert mock_setup_simulation.call_args[0][1] == vis_mode


@mock.patch("virtuallife.cli.setup_simulation")
def test_reproducible_simulation(mock_setup_simulation):
    """Test that simulations are reproducible with the same seed."""
    # Arrange
    mock_environment = Environment(30, 30)
    mock_runner = mock.MagicMock()
    mock_visualizer = mock.MagicMock()
    mock_setup_simulation.return_value = (mock_runner, mock_visualizer)
    
    runner = CliRunner()
    
    # Run simulation twice with same seed
    for _ in range(2):
        mock_setup_simulation.reset_mock()
        result = runner.invoke(
            app,
            ["run", "--seed", "42", "--steps", "10"],
            catch_exceptions=False
        )
        
        assert result.exit_code == 0
        config = mock_setup_simulation.call_args[0][0]
        assert config.random_seed == 42 
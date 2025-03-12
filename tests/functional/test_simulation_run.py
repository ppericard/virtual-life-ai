"""Functional tests for running simulations.

This module contains functional tests that demonstrate running simulations
with various parameters and configurations.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from virtuallife.cli import app
from virtuallife.config.models import SimulationConfig
from virtuallife.simulation.environment import Environment
from virtuallife.simulation.runner import SimulationRunner


@pytest.fixture
def config_file():
    """Fixture that creates a temporary configuration file with custom settings."""
    config = SimulationConfig()
    config.environment.width = 20
    config.environment.height = 20
    config.environment.initial_entities = 5
    config.environment.boundary_condition = "wrapped"
    config.energy.initial_energy = 100.0
    config.energy.decay_rate = 0.2
    config.random_seed = 42
    config.max_steps = 10
    
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
        from virtuallife.config.loader import save_config
        save_config(config, tmp.name)
        yield Path(tmp.name)
    
    # Clean up
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)


@mock.patch("virtuallife.cli.setup_simulation")
def test_run_simulation_with_config(mock_setup_simulation, config_file):
    """Test running a complete simulation with a configuration file."""
    # Arrange
    mock_environment = Environment(20, 20)
    mock_runner = mock.MagicMock()
    mock_visualizer = mock.MagicMock()
    mock_setup_simulation.return_value = (mock_runner, mock_visualizer)
    
    # Create a runner for testing
    from typer.testing import CliRunner
    runner = CliRunner()
    
    # Act - Run a simulation with the config file
    result = runner.invoke(
        app, 
        ["run", "--config", str(config_file), "--steps", "5"],
        catch_exceptions=False
    )
    
    # Assert
    assert result.exit_code == 0
    mock_setup_simulation.assert_called_once()
    mock_runner.run.assert_called_once_with(5)


@mock.patch("virtuallife.cli.setup_simulation")
def test_simulation_with_different_visualizers(mock_setup_simulation):
    """Test running simulations with different visualization options."""
    # Arrange
    mock_environment = Environment(20, 20)
    mock_runner = mock.MagicMock()
    mock_visualizer = mock.MagicMock()
    mock_setup_simulation.return_value = (mock_runner, mock_visualizer)
    
    # Create a runner for testing
    from typer.testing import CliRunner
    runner = CliRunner()
    
    # Act - Run with console visualization
    console_result = runner.invoke(
        app, 
        ["run", "--steps", "3", "--visualizer", "console"],
        catch_exceptions=False
    )
    
    # Assert
    assert console_result.exit_code == 0
    assert mock_setup_simulation.call_args[0][1] == "console"
    
    # Reset mock
    mock_setup_simulation.reset_mock()
    
    # Act - Run with matplotlib visualization
    matplotlib_result = runner.invoke(
        app, 
        ["run", "--steps", "3", "--visualizer", "matplotlib"],
        catch_exceptions=False
    )
    
    # Assert
    assert matplotlib_result.exit_code == 0
    assert mock_setup_simulation.call_args[0][1] == "matplotlib"
    
    # Reset mock
    mock_setup_simulation.reset_mock()
    
    # Act - Run with no visualization
    no_vis_result = runner.invoke(
        app, 
        ["run", "--steps", "3", "--no-vis"],
        catch_exceptions=False
    )
    
    # Assert
    assert no_vis_result.exit_code == 0
    assert mock_setup_simulation.call_args[0][1] == "none"


@mock.patch("virtuallife.cli.setup_simulation")
def test_simulation_with_random_seed(mock_setup_simulation):
    """Test running a simulation with a specific random seed."""
    # Arrange
    mock_environment = Environment(20, 20)
    mock_runner = mock.MagicMock()
    mock_visualizer = mock.MagicMock()
    mock_setup_simulation.return_value = (mock_runner, mock_visualizer)
    
    # Create a runner for testing
    from typer.testing import CliRunner
    runner = CliRunner()
    
    # Act - Run with a specific random seed
    result = runner.invoke(
        app, 
        ["run", "--steps", "3", "--seed", "42"],
        catch_exceptions=False
    )
    
    # Assert
    assert result.exit_code == 0
    # Check that config has random_seed=42
    assert mock_setup_simulation.call_args[0][0].random_seed == 42 
"""Tests for the command-line interface.

This module contains tests for the CLI functionality.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from virtuallife.cli import app
from virtuallife.config.models import SimulationConfig


@pytest.fixture
def runner():
    """Fixture that returns a CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_setup_simulation():
    """Fixture that mocks the setup_simulation function."""
    with patch("virtuallife.cli.setup_simulation") as mock:
        # Create a mock runner
        mock_runner = MagicMock()
        mock_visualizer = MagicMock()
        
        # Configure the mock to return our mock runner and visualizer
        mock.return_value = (mock_runner, mock_visualizer)
        
        yield mock


@pytest.fixture
def temp_config_file():
    """Fixture that creates a temporary configuration file."""
    config = SimulationConfig()
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
        from virtuallife.config.loader import save_config
        save_config(config, tmp.name)
        yield Path(tmp.name)
    # Clean up
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)


def test_run_simulation_with_defaults(runner, mock_setup_simulation):
    """Test running a simulation with default settings."""
    # Arrange
    mock_runner, mock_visualizer = mock_setup_simulation.return_value
    
    # Act
    result = runner.invoke(app, ["run", "--steps", "5"])
    
    # Assert
    assert result.exit_code == 0
    mock_setup_simulation.assert_called_once()
    mock_runner.run.assert_called_once_with(5)


def test_run_simulation_with_config(runner, mock_setup_simulation, temp_config_file):
    """Test running a simulation with a configuration file."""
    # Arrange
    mock_runner, mock_visualizer = mock_setup_simulation.return_value
    
    # Act
    result = runner.invoke(app, ["run", "--config", str(temp_config_file), "--steps", "10"])
    
    # Assert
    assert result.exit_code == 0
    mock_setup_simulation.assert_called_once()
    mock_runner.run.assert_called_once_with(10)


def test_run_simulation_with_matplotlib(runner, mock_setup_simulation):
    """Test running a simulation with matplotlib visualization."""
    # Arrange
    mock_runner, mock_visualizer = mock_setup_simulation.return_value
    
    # Act
    result = runner.invoke(app, ["run", "--visualizer", "matplotlib", "--steps", "3"])
    
    # Assert
    assert result.exit_code == 0
    mock_setup_simulation.assert_called_once()
    assert mock_setup_simulation.call_args[0][1] == "matplotlib"
    mock_runner.run.assert_called_once_with(3)


def test_run_simulation_no_visualization(runner, mock_setup_simulation):
    """Test running a simulation with no visualization."""
    # Arrange
    mock_runner, mock_visualizer = mock_setup_simulation.return_value
    
    # Act
    result = runner.invoke(app, ["run", "--no-vis", "--steps", "3"])
    
    # Assert
    assert result.exit_code == 0
    mock_setup_simulation.assert_called_once()
    assert mock_setup_simulation.call_args[0][1] == "none"
    mock_runner.run.assert_called_once_with(3)


def test_show_info_with_defaults(runner):
    """Test displaying information about default configuration."""
    # Act
    result = runner.invoke(app, ["info"])
    
    # Assert
    assert result.exit_code == 0
    assert "Configuration Details" in result.stdout
    assert "Environment" in result.stdout
    assert "Energy" in result.stdout
    assert "Movement" in result.stdout
    assert "Reproduction" in result.stdout
    assert "Resources" in result.stdout


def test_show_info_with_config(runner, temp_config_file):
    """Test displaying information about a configuration file."""
    # Act
    result = runner.invoke(app, ["info", "--config", str(temp_config_file)])
    
    # Assert
    assert result.exit_code == 0
    assert "Configuration Details" in result.stdout
    assert "Environment" in result.stdout
    assert "Energy" in result.stdout
    assert "Movement" in result.stdout
    assert "Reproduction" in result.stdout
    assert "Resources" in result.stdout


def test_create_config(runner):
    """Test creating a configuration file."""
    # Arrange
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
        output_path = tmp.name
    
    # Clean up before test (in case it exists)
    if os.path.exists(output_path):
        os.unlink(output_path)
    
    try:
        # Act
        result = runner.invoke(
            app, 
            [
                "create-config", 
                output_path, 
                "--width", "200", 
                "--height", "200", 
                "--boundary", "bounded",
                "--entities", "20",
                "--seed", "42"
            ]
        )
        
        # Assert
        assert result.exit_code == 0
        assert os.path.exists(output_path)
        
        # Verify the contents of the config file
        from virtuallife.config.loader import load_config
        config = load_config(output_path)
        assert config.environment.width == 200
        assert config.environment.height == 200
        assert config.environment.boundary_condition == "bounded"
        assert config.environment.initial_entities == 20
        assert config.random_seed == 42
        
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_setup_simulation():
    """Test the setup_simulation function directly."""
    # Import the function to test it directly
    from virtuallife.cli import setup_simulation
    
    # Create a configuration
    config = SimulationConfig()
    
    # Test with console visualizer
    runner, visualizer = setup_simulation(config, "console")
    assert runner is not None
    assert visualizer is not None
    assert "step_end" in runner.listeners
    assert len(runner.listeners["step_end"]) == 1
    
    # Test with matplotlib visualizer
    runner, visualizer = setup_simulation(config, "matplotlib")
    assert runner is not None
    assert visualizer is not None
    assert "step_end" in runner.listeners
    assert len(runner.listeners["step_end"]) == 1
    
    # Test with no visualizer
    runner, visualizer = setup_simulation(config, "none")
    assert runner is not None
    assert visualizer is None 
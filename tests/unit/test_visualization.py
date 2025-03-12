"""Unit tests for visualization components."""

import unittest.mock as mock
import pytest
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid Tk issues

from virtuallife.visualize.base import Visualizer
from virtuallife.visualize.console import ConsoleVisualizer
from virtuallife.visualize.plotting import MatplotlibVisualizer
from virtuallife.simulation.runner import SimulationRunner
from virtuallife.simulation.environment import Environment


@pytest.fixture
def mock_environment():
    """Create a mock environment."""
    env = mock.MagicMock(spec=Environment)
    env.width = 3
    env.height = 3
    env.get_entities_at.return_value = []
    env.resources = {}
    env.entity_positions = {}
    env.entities = []  # Add entities attribute
    return env


@pytest.fixture
def mock_runner(mock_environment):
    """Create a mock runner with environment."""
    runner = mock.MagicMock(spec=SimulationRunner)
    runner.environment = mock_environment
    runner.current_step = 5
    return runner


@pytest.fixture
def mock_matplotlib(monkeypatch):
    """Create a mock matplotlib module."""
    mock_plt = mock.MagicMock()
    mock_fig = mock.MagicMock()
    mock_ax = mock.MagicMock()
    mock_plt.subplots.return_value = (mock_fig, mock_ax)
    
    # Mock numpy for array operations
    mock_np = mock.MagicMock()
    mock_np.c_ = mock.MagicMock()
    mock_np.zeros.return_value = mock.MagicMock()
    
    monkeypatch.setattr('virtuallife.visualize.plotting.plt', mock_plt)
    monkeypatch.setattr('virtuallife.visualize.plotting.np', mock_np)
    
    return mock_plt


def test_console_visualizer_initialization():
    """Test initialization of the ConsoleVisualizer."""
    # Act
    visualizer = ConsoleVisualizer()
    
    # Assert
    assert visualizer.entity_symbols["default"] == "○"
    assert visualizer.entity_symbols["plant"] == "♣"
    assert visualizer.entity_symbols["herbivore"] == "□"
    assert visualizer.entity_symbols["predator"] == "△"
    assert visualizer.empty_symbol == "·"
    assert visualizer.runner is None


def test_console_visualizer_setup(mock_runner):
    """Test setup of the ConsoleVisualizer."""
    # Arrange
    visualizer = ConsoleVisualizer()
    
    # Act
    visualizer.setup(mock_runner)
    
    # Assert
    assert visualizer.runner == mock_runner
    mock_runner.add_listener.assert_called_once_with("step_end", visualizer.update)


def test_console_visualizer_update(mock_runner):
    """Test update method of the ConsoleVisualizer."""
    # Arrange
    visualizer = ConsoleVisualizer()
    visualizer.setup(mock_runner)
    
    # Act
    with mock.patch('os.system') as mock_clear:
        visualizer.update(mock_runner)
    
    # Assert
    mock_clear.assert_called_once()
    assert mock_runner.environment.get_entities_at.call_count == 9  # 3x3 grid


def test_matplotlib_visualizer_initialization():
    """Test initialization of the MatplotlibVisualizer."""
    # Act
    visualizer = MatplotlibVisualizer()
    
    # Assert
    assert visualizer.entity_colors["default"] == "gray"
    assert visualizer.entity_colors["plant"] == "green"
    assert visualizer.entity_colors["herbivore"] == "blue"
    assert visualizer.entity_colors["predator"] == "red"
    assert visualizer.fig is None
    assert visualizer.ax is None
    assert visualizer.scatter_plots == {}
    assert visualizer.resource_plot is None


def test_matplotlib_visualizer_custom_colors():
    """Test matplotlib visualizer with custom colors."""
    # Arrange
    custom_colors = {
        "default": "black",
        "plant": "lime",
        "herbivore": "cyan",
        "predator": "magenta"
    }
    
    # Act
    visualizer = MatplotlibVisualizer(custom_colors)
    
    # Assert
    assert visualizer.entity_colors == custom_colors


def test_matplotlib_visualizer_setup(mock_runner, mock_matplotlib):
    """Test setup of the MatplotlibVisualizer."""
    # Arrange
    visualizer = MatplotlibVisualizer()
    
    # Act
    visualizer.setup(mock_runner)
    
    # Assert
    mock_matplotlib.ion.assert_called_once()
    mock_matplotlib.subplots.assert_called_once()
    mock_matplotlib.title.assert_called_with("VirtualLife Simulation")
    assert len(visualizer.scatter_plots) == 4  # default + 3 entity types
    assert visualizer.fig is not None
    assert visualizer.ax is not None


def test_matplotlib_visualizer_update(mock_runner, mock_matplotlib):
    """Test update method of the MatplotlibVisualizer."""
    # Arrange
    visualizer = MatplotlibVisualizer()
    visualizer.setup(mock_runner)
    
    # Create mock scatter plots
    visualizer.scatter_plots = {
        entity_type: mock.MagicMock()
        for entity_type in visualizer.entity_colors
    }
    
    # Act
    visualizer.update(mock_runner)
    
    # Assert
    # Each scatter plot should be updated
    for scatter in visualizer.scatter_plots.values():
        scatter.set_offsets.assert_called_once()
    mock_matplotlib.title.assert_called_with(f"VirtualLife Simulation - Step {mock_runner.current_step}")


def test_matplotlib_visualizer_cleanup(mock_matplotlib):
    """Test cleanup of the MatplotlibVisualizer."""
    # Arrange
    visualizer = MatplotlibVisualizer()
    mock_fig = mock.MagicMock()
    visualizer.fig = mock_fig
    
    # Act
    visualizer.cleanup()
    
    # Assert
    mock_matplotlib.close.assert_called_once_with(mock_fig)
    assert visualizer.fig is None
    assert visualizer.ax is None 
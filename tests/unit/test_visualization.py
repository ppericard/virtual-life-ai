"""Unit tests for the visualization system."""

from unittest.mock import MagicMock, patch
import pytest
import numpy as np

from virtuallife.visualize.base import Visualizer
from virtuallife.visualize.console import ConsoleVisualizer
from virtuallife.visualize.plotting import MatplotlibVisualizer
from virtuallife.simulation.runner import SimulationRunner
from virtuallife.simulation.environment import Environment
from virtuallife.simulation.entity import Entity


@pytest.fixture
def environment():
    """Create a test environment."""
    return Environment(width=10, height=10)


@pytest.fixture
def runner(environment):
    """Create a test simulation runner."""
    return SimulationRunner(environment=environment)


class TestVisualizer(Visualizer):
    """Test implementation of the Visualizer interface."""
    
    def __init__(self):
        self.setup_called = False
        self.update_called = False
        self.cleanup_called = False
    
    def setup(self, runner: SimulationRunner) -> None:
        self.setup_called = True
    
    def update(self, runner: SimulationRunner, **kwargs) -> None:
        self.update_called = True
    
    def cleanup(self) -> None:
        self.cleanup_called = True


def test_visualizer_interface():
    """Test that the visualizer interface works correctly."""
    visualizer = TestVisualizer()
    runner = MagicMock()
    
    visualizer.setup(runner)
    assert visualizer.setup_called
    
    visualizer.update(runner)
    assert visualizer.update_called
    
    visualizer.cleanup()
    assert visualizer.cleanup_called


def test_console_visualizer_initialization():
    """Test console visualizer initialization."""
    visualizer = ConsoleVisualizer()
    assert "plant" in visualizer.entity_symbols
    assert "herbivore" in visualizer.entity_symbols
    assert "predator" in visualizer.entity_symbols
    assert visualizer.empty_symbol == "·"


def test_console_visualizer_custom_symbols():
    """Test console visualizer with custom symbols."""
    custom_symbols = {
        "default": "X",
        "plant": "P",
        "herbivore": "H",
        "predator": "R"
    }
    visualizer = ConsoleVisualizer(entity_symbols=custom_symbols)
    assert visualizer.entity_symbols == custom_symbols


@patch('os.system')
def test_console_visualizer_update(mock_system, runner):
    """Test console visualizer update."""
    visualizer = ConsoleVisualizer()
    
    # Add some test entities
    entity1 = Entity(position=(1, 1))
    entity1.add_component("plant", MagicMock())
    runner.environment.add_entity(entity1)
    
    entity2 = Entity(position=(2, 2))
    entity2.add_component("herbivore", MagicMock())
    runner.environment.add_entity(entity2)
    
    # Capture print output
    with patch('builtins.print') as mock_print:
        visualizer.update(runner)
    
    # Verify screen was cleared
    mock_system.assert_called_once()
    
    # Verify some output was printed
    assert mock_print.call_count > 0


def test_matplotlib_visualizer_initialization():
    """Test matplotlib visualizer initialization."""
    visualizer = MatplotlibVisualizer()
    assert "plant" in visualizer.entity_colors
    assert "herbivore" in visualizer.entity_colors
    assert "predator" in visualizer.entity_colors
    assert visualizer.fig is None
    assert visualizer.ax is None


def test_matplotlib_visualizer_custom_colors():
    """Test matplotlib visualizer with custom colors."""
    custom_colors = {
        "default": "black",
        "plant": "lime",
        "herbivore": "cyan",
        "predator": "magenta"
    }
    visualizer = MatplotlibVisualizer(entity_colors=custom_colors)
    assert visualizer.entity_colors == custom_colors


@patch('matplotlib.pyplot.subplots')
@patch('matplotlib.pyplot.ion')
def test_matplotlib_visualizer_setup(mock_ion, mock_subplots, runner):
    """Test matplotlib visualizer setup."""
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_subplots.return_value = (mock_fig, mock_ax)
    
    visualizer = MatplotlibVisualizer()
    visualizer.setup(runner)
    
    # Verify matplotlib was set up correctly
    mock_ion.assert_called_once()
    mock_subplots.assert_called_once()
    assert visualizer.fig is not None
    assert visualizer.ax is not None
    assert len(visualizer.scatter_plots) == len(visualizer.entity_colors)


@patch('matplotlib.pyplot.subplots')
@patch('matplotlib.pyplot.ion')
def test_matplotlib_visualizer_update(mock_ion, mock_subplots, runner):
    """Test matplotlib visualizer update."""
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_subplots.return_value = (mock_fig, mock_ax)
    
    visualizer = MatplotlibVisualizer()
    visualizer.setup(runner)
    
    # Add some test entities
    entity1 = Entity(position=(1, 1))
    entity1.add_component("plant", MagicMock())
    runner.environment.add_entity(entity1)
    
    entity2 = Entity(position=(2, 2))
    entity2.add_component("herbivore", MagicMock())
    runner.environment.add_entity(entity2)
    
    # Add some resources
    runner.environment.resources["food"] = np.zeros((10, 10))
    
    visualizer.update(runner)
    
    # Verify scatter plots were updated
    for scatter in visualizer.scatter_plots.values():
        assert scatter.set_offsets.called


@patch('matplotlib.pyplot.close')
def test_matplotlib_visualizer_cleanup(mock_close):
    """Test matplotlib visualizer cleanup."""
    mock_fig = MagicMock()
    visualizer = MatplotlibVisualizer()
    visualizer.fig = mock_fig
    
    visualizer.cleanup()
    
    mock_close.assert_called_once_with(mock_fig)
    assert visualizer.fig is None
    assert visualizer.ax is None 
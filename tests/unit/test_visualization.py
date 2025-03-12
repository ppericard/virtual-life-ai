"""Unit tests for the visualization system."""

from unittest.mock import MagicMock, patch
import pytest
import numpy as np
import unittest.mock as mock

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
    """Test implementation of the Visualizer base class."""
    
    def __init__(self, simulation=None):
        """Initialize the test visualizer."""
        self.simulation = simulation
        self.updated = False
        self.cleared = False
        self.rendered = False
        self.setup_called = False
        self.update_called = False
        self.cleanup_called = False
    
    def setup(self, runner):
        """Set up the visualizer.
        
        Args:
            runner: The simulation runner
        """
        self.simulation = runner
        self.setup_called = True
    
    def update(self, simulation=None, **kwargs):
        """Update the visualization.
        
        Args:
            simulation: The simulation runner
            **kwargs: Additional keyword arguments
        """
        self.updated = True
        self.update_called = True
        if simulation:
            self.simulation = simulation
    
    def cleanup(self):
        """Clean up the visualizer."""
        self.cleanup_called = True
    
    def clear(self):
        """Clear the visualization."""
        self.cleared = True
    
    def render(self):
        """Render the visualization."""
        self.rendered = True


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
    """Test initialization of the ConsoleVisualizer."""
    # Arrange
    mock_simulation = mock.MagicMock()
    mock_simulation.environment.width = 10
    mock_simulation.environment.height = 10
    
    # Act
    visualizer = ConsoleVisualizer(mock_simulation)
    
    # Assert
    assert visualizer.simulation == mock_simulation
    assert visualizer.width == 10
    assert visualizer.height == 10
    assert visualizer.grid is not None


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
    visualizer.setup(runner)
    
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
    """Test initialization of the MatplotlibVisualizer."""
    # Arrange
    mock_simulation = mock.MagicMock()
    mock_simulation.environment.width = 10
    mock_simulation.environment.height = 10
    
    # Act
    with mock.patch('matplotlib.pyplot.figure') as mock_figure:
        with mock.patch('matplotlib.pyplot.ion') as mock_ion:
            visualizer = MatplotlibVisualizer(mock_simulation)
    
    # Assert
    assert visualizer.simulation == mock_simulation
    assert visualizer.width == 10
    assert visualizer.height == 10


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
    
    visualizer.update(runner)


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


def test_visualizer_base_methods():
    """Test the base methods of the Visualizer class."""
    # Arrange
    mock_simulation = mock.MagicMock()
    visualizer = TestVisualizer()
    
    # Act & Assert - setup
    visualizer.setup(mock_simulation)
    assert visualizer.setup_called is True
    
    # Act & Assert - update
    visualizer.update(mock_simulation, test_kwarg=True)
    assert visualizer.updated is True
    assert visualizer.update_called is True
    
    # Act & Assert - cleanup
    visualizer.cleanup()
    assert visualizer.cleanup_called is True
    
    # Act & Assert - clear
    visualizer.clear()
    assert visualizer.cleared is True
    
    # Act & Assert - render
    visualizer.render()
    assert visualizer.rendered is True


def test_console_visualizer_update():
    """Test update method of the ConsoleVisualizer."""
    # Arrange
    mock_simulation = mock.MagicMock()
    mock_simulation.environment.width = 10
    mock_simulation.environment.height = 10
    mock_simulation.environment.entities = {}
    mock_simulation.environment.get_entities_at.return_value = []
    
    # Act
    visualizer = ConsoleVisualizer(mock_simulation)
    with mock.patch('virtuallife.visualize.console.os') as mock_os:
        with mock.patch('builtins.print') as mock_print:
            visualizer.update(mock_simulation)
    
    # Assert
    mock_os.system.assert_called_once()
    assert mock_print.call_count > 0


def test_matplotlib_visualizer_update():
    """Test update method of the MatplotlibVisualizer."""
    # Arrange
    mock_simulation = mock.MagicMock()
    mock_simulation.environment.width = 10
    mock_simulation.environment.height = 10
    mock_simulation.environment.entities = {}
    mock_simulation.current_step = 5
    
    # Act
    with mock.patch('matplotlib.pyplot') as mock_plt:
        visualizer = MatplotlibVisualizer(mock_simulation)
        visualizer.fig = mock.MagicMock()
        visualizer.ax = mock.MagicMock()
        visualizer.image_plot = mock.MagicMock()
        visualizer.update(mock_simulation)
    
    # Assert
    mock_simulation.environment.get_entities_at.assert_called()
    visualizer.image_plot.set_data.assert_called_once()


def test_console_visualizer_get_entity_symbol():
    """Test the get_entity_symbol method of the ConsoleVisualizer."""
    # Arrange
    visualizer = ConsoleVisualizer()
    
    # Create mock entities with different components
    entity_with_predator = mock.MagicMock()
    entity_with_predator.has_component.side_effect = lambda x: x == "predator"
    
    entity_with_herbivore = mock.MagicMock()
    entity_with_herbivore.has_component.side_effect = lambda x: x == "herbivore"
    
    entity_with_plant = mock.MagicMock()
    entity_with_plant.has_component.side_effect = lambda x: x == "plant"
    
    default_entity = mock.MagicMock()
    default_entity.has_component.return_value = False
    
    # Act & Assert - use the _get_entity_symbol private method
    assert visualizer._get_entity_symbol(entity_with_predator) == "P"
    assert visualizer._get_entity_symbol(entity_with_herbivore) == "H"
    assert visualizer._get_entity_symbol(entity_with_plant) == "*"
    assert visualizer._get_entity_symbol(default_entity) == "·" 
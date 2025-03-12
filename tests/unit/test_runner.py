"""Unit tests for the simulation runner module."""

from unittest.mock import MagicMock, patch
import pytest
import time

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


def test_simulation_runner_initialization(environment):
    """Test simulation runner initialization."""
    runner = SimulationRunner(environment=environment)
    assert runner.current_step == 0
    assert not runner.running
    assert isinstance(runner.config, dict)
    assert len(runner.config) == 0
    assert isinstance(runner.listeners, dict)
    assert set(runner.listeners.keys()) == {"step_start", "step_end", "entity_added", "entity_removed"}


def test_add_listener(runner):
    """Test adding event listeners."""
    callback = lambda sim, **kwargs: None
    runner.add_listener("step_start", callback)
    assert len(runner.listeners["step_start"]) == 1
    assert runner.listeners["step_start"][0] == callback


def test_add_listener_invalid_event(runner):
    """Test adding listener for invalid event type."""
    callback = lambda sim, **kwargs: None
    with pytest.raises(ValueError, match="Unsupported event type: invalid_event"):
        runner.add_listener("invalid_event", callback)


def test_notify_listeners(runner):
    """Test notifying event listeners."""
    called_data = {"called": False, "args": None}
    
    def callback(sim, **kwargs):
        called_data["called"] = True
        called_data["args"] = kwargs
    
    runner.add_listener("step_start", callback)
    runner.notify_listeners("step_start", test_arg="value")
    
    assert called_data["called"]
    assert called_data["args"]["test_arg"] == "value"


def test_step_updates_entities(environment):
    """Test that step updates all entities."""
    # Create mock entities
    entity1 = MagicMock()
    entity2 = MagicMock()
    
    # Add mock entities to environment
    environment.entities = {1: entity1, 2: entity2}
    
    runner = SimulationRunner(environment=environment)
    runner.step()
    
    # Verify that each entity was updated
    entity1.update.assert_called_once_with(environment)
    entity2.update.assert_called_once_with(environment)
    assert runner.current_step == 1


def test_step_notifies_listeners(runner):
    """Test that step notifies listeners."""
    events = []
    runner.add_listener("step_start", lambda sim, **kwargs: events.append("start"))
    runner.add_listener("step_end", lambda sim, **kwargs: events.append("end"))
    
    runner.step()
    
    assert events == ["start", "end"]


def test_run_for_steps(environment):
    """Test running simulation for specific number of steps."""
    runner = SimulationRunner(environment=environment)
    runner.run(steps=5)
    assert runner.current_step == 5
    assert not runner.running


def test_run_with_delay(environment):
    """Test running simulation with step delay."""
    runner = SimulationRunner(environment=environment, config={"step_delay": 0.1})
    
    start_time = time.time()
    runner.run(steps=2)
    elapsed_time = time.time() - start_time
    
    assert elapsed_time >= 0.2  # At least 2 * 0.1 seconds
    assert runner.current_step == 2


def test_stop_simulation(runner):
    """Test stopping the simulation."""
    def run_in_thread():
        runner.run()  # Run indefinitely
    
    with patch('threading.Thread', MagicMock()) as mock_thread:
        mock_thread.start()
        runner.stop()
        assert not runner.running


def test_run_handles_exceptions(environment):
    """Test that run handles exceptions gracefully."""
    runner = SimulationRunner(environment=environment)
    
    # Create a mock entity that raises an exception
    entity = MagicMock()
    entity.update.side_effect = Exception("Test exception")
    environment.entities = {1: entity}
    
    # Run should complete and set running to False even with exception
    runner.run(steps=1)
    assert not runner.running


def test_entity_removal_during_step(environment):
    """Test that step handles entity removal during updates."""
    # Create an entity that removes itself during update
    entity = Entity()
    
    def remove_self(env):
        env.remove_entity(entity.id)
    
    entity.update = remove_self
    environment.add_entity(entity)
    
    runner = SimulationRunner(environment=environment)
    runner.step()
    
    assert entity.id not in environment.entities 
"""Unit tests for the standard components."""

from unittest.mock import MagicMock
import pytest
from unittest.mock import patch

from virtuallife.simulation.components import (
    EnergyComponent,
    MovementComponent,
    ResourceConsumerComponent,
)
from virtuallife.simulation.entity import Entity
from virtuallife.simulation.environment import Environment


@pytest.fixture
def environment():
    """Create a test environment."""
    return Environment(width=10, height=10)


@pytest.fixture
def entity():
    """Create a test entity."""
    return Entity(position=(5, 5))


def test_energy_component_initialization():
    """Test energy component initialization."""
    component = EnergyComponent()
    assert component.energy == 100.0
    assert component.max_energy == 100.0
    assert component.decay_rate == 0.1
    assert component.death_threshold == 0.0


def test_energy_component_decay():
    """Test energy decay over time."""
    component = EnergyComponent(energy=100.0, decay_rate=10.0)
    entity = Entity()
    env = MagicMock()
    
    component.update(entity, env)
    assert component.energy == 90.0


def test_energy_never_negative():
    """Test that energy never goes below 0 after decay."""
    component = EnergyComponent(energy=5.0, decay_rate=10.0)
    entity = Entity()
    env = MagicMock()
    
    component.update(entity, env)
    assert component.energy == 0.0


def test_energy_custom_death_threshold():
    """Test custom death threshold values."""
    component = EnergyComponent(energy=15.0, decay_rate=10.0, death_threshold=10.0)
    entity = Entity()
    env = MagicMock()
    
    component.update(entity, env)
    # Energy is now 5.0, which is below death_threshold of 10.0
    env.remove_entity.assert_called_once_with(entity.id)


def test_energy_component_death():
    """Test entity death when energy is depleted."""
    component = EnergyComponent(energy=5.0, decay_rate=10.0)
    entity = Entity()
    env = MagicMock()
    
    component.update(entity, env)
    env.remove_entity.assert_called_once_with(entity.id)


def test_energy_consumption():
    """Test energy consumption."""
    component = EnergyComponent(energy=100.0)
    
    # Successful consumption
    assert component.consume_energy(30.0) is True
    assert component.energy == 70.0
    
    # Failed consumption (not enough energy)
    assert component.consume_energy(80.0) is False
    assert component.energy == 70.0


def test_energy_addition():
    """Test adding energy."""
    component = EnergyComponent(energy=50.0, max_energy=100.0)
    
    # Normal addition
    component.add_energy(30.0)
    assert component.energy == 80.0
    
    # Addition exceeding max_energy
    component.add_energy(30.0)
    assert component.energy == 100.0


def test_movement_component_initialization():
    """Test movement component initialization."""
    component = MovementComponent()
    assert component.speed == 1.0
    assert component.movement_cost == 0.1


def test_movement_with_energy(environment, entity):
    """Test movement with energy consumption."""
    energy = EnergyComponent(energy=100.0)
    movement = MovementComponent(speed=1.0, movement_cost=10.0)
    
    entity.add_component("energy", energy)
    entity.add_component("movement", movement)
    environment.add_entity(entity)
    
    old_position = entity.position
    movement.update(entity, environment)
    
    # Position should have changed
    assert entity.position != old_position
    # Energy should have been consumed
    assert energy.energy < 100.0


def test_movement_cost_scaling():
    """Test that movement cost scales correctly with speed."""
    energy = EnergyComponent(energy=100.0)
    movement = MovementComponent(speed=2.0, movement_cost=1.0)
    entity = Entity()
    env = Environment(10, 10)
    
    entity.add_component("energy", energy)
    entity.add_component("movement", movement)
    env.add_entity(entity)
    
    initial_energy = energy.energy
    movement.update(entity, env)
    
    # With speed=2.0, the energy cost should be double
    # Maximum movement is 2 steps (dx=1, dy=1), so max cost is 4.0
    assert initial_energy - energy.energy <= 4.0


def test_movement_boundary_conditions():
    """Test movement with different boundary conditions."""
    # Test wrapped boundaries
    env_wrapped = Environment(10, 10, boundary_condition="wrapped")
    entity = Entity(position=(9, 9))
    movement = MovementComponent()
    entity.add_component("movement", movement)
    env_wrapped.add_entity(entity)
    
    # Force movement to go out of bounds
    with patch('random.randint', return_value=1):
        movement.update(entity, env_wrapped)
        assert entity.position == (0, 0)  # Should wrap around
    
    # Test bounded boundaries
    env_bounded = Environment(10, 10, boundary_condition="bounded")
    entity = Entity(position=(9, 9))
    movement = MovementComponent()
    entity.add_component("movement", movement)
    env_bounded.add_entity(entity)
    
    # Force movement to go out of bounds
    with patch('random.randint', return_value=1):
        movement.update(entity, env_bounded)
        assert entity.position == (9, 9)  # Should stay at boundary


def test_movement_without_energy(environment, entity):
    """Test movement without energy component."""
    movement = MovementComponent()
    entity.add_component("movement", movement)
    environment.add_entity(entity)
    
    old_position = entity.position
    movement.update(entity, environment)
    
    # Position should still change even without energy component
    assert entity.position != old_position


def test_movement_with_depleted_energy(environment, entity):
    """Test movement with depleted energy."""
    energy = EnergyComponent(energy=0.0)
    movement = MovementComponent()
    
    entity.add_component("energy", energy)
    entity.add_component("movement", movement)
    environment.add_entity(entity)
    
    old_position = entity.position
    movement.update(entity, environment)
    
    # Position should not change with no energy
    assert entity.position == old_position


def test_resource_consumer_initialization():
    """Test resource consumer component initialization."""
    component = ResourceConsumerComponent()
    assert component.resource_type == "food"
    assert component.consumption_rate == 1.0
    assert component.energy_conversion == 0.5


def test_resource_consumption(environment, entity):
    """Test resource consumption and energy conversion."""
    energy = EnergyComponent(energy=50.0)
    consumer = ResourceConsumerComponent(
        consumption_rate=2.0,
        energy_conversion=0.5
    )
    
    entity.add_component("energy", energy)
    entity.add_component("consumer", consumer)
    environment.add_entity(entity)
    
    # Add resource to entity's position
    environment.add_resource("food", entity.position, 5.0)
    
    # Update should consume resources and convert to energy
    consumer.update(entity, environment)
    
    # Check resource was consumed
    assert environment.get_resource("food", entity.position) == 3.0
    # Check energy was gained (2.0 * 0.5 = 1.0 energy)
    assert energy.energy == 51.0


def test_resource_consumption_without_energy(environment, entity):
    """Test resource consumption without energy component."""
    consumer = ResourceConsumerComponent()
    entity.add_component("consumer", consumer)
    environment.add_entity(entity)
    
    # Add resource to entity's position
    environment.add_resource("food", entity.position, 5.0)
    
    # Update should do nothing without energy component
    consumer.update(entity, environment)
    
    # Resource should remain unchanged
    assert environment.get_resource("food", entity.position) == 5.0


def test_resource_consumption_depletes_resource(environment, entity):
    """Test that resources are removed when fully consumed."""
    energy = EnergyComponent(energy=50.0)
    consumer = ResourceConsumerComponent(
        consumption_rate=2.0,
        energy_conversion=0.5
    )
    
    entity.add_component("energy", energy)
    entity.add_component("consumer", consumer)
    environment.add_entity(entity)
    
    # Add small amount of resource
    environment.add_resource("food", entity.position, 1.0)
    
    # Update should consume all resources
    consumer.update(entity, environment)
    
    # Resource should be completely removed
    assert environment.get_resource("food", entity.position) == 0.0


def test_different_resource_types(environment, entity):
    """Test consumption of different resource types."""
    energy = EnergyComponent(energy=50.0)
    consumer = ResourceConsumerComponent(
        resource_type="water",
        consumption_rate=1.0,
        energy_conversion=1.0
    )
    
    entity.add_component("energy", energy)
    entity.add_component("consumer", consumer)
    environment.add_entity(entity)
    
    # Add water resource
    environment.add_resource("water", entity.position, 3.0)
    
    # Update should consume water and convert to energy
    consumer.update(entity, environment)
    
    # Check water was consumed
    assert environment.get_resource("water", entity.position) == 2.0
    # Check energy was gained
    assert energy.energy == 51.0 
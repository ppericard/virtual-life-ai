"""Unit tests for the standard components."""

from unittest.mock import MagicMock
import pytest

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
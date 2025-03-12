"""Unit tests for the standard components."""

from unittest.mock import MagicMock, patch
import pytest

from virtuallife.simulation.components import (
    EnergyComponent,
    MovementComponent,
    ResourceConsumerComponent,
    ReproductionComponent,
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


def test_reproduction_component_initialization():
    """Test reproduction component initialization."""
    component = ReproductionComponent()
    assert component.reproduction_threshold == 80.0
    assert component.reproduction_cost == 50.0
    assert component.reproduction_chance == 0.1
    assert component.offspring_energy == 50.0
    assert component.mutation_rate == 0.1
    assert component.inherit_components == {
        "energy": True,
        "movement": True,
        "consumer": True,
        "reproduction": True
    }


def test_reproduction_without_energy():
    """Test that reproduction fails without energy component."""
    component = ReproductionComponent()
    entity = Entity()
    env = MagicMock()
    
    component.update(entity, env)
    env.add_entity.assert_not_called()


def test_reproduction_insufficient_energy():
    """Test that reproduction fails with insufficient energy."""
    component = ReproductionComponent()
    entity = Entity()
    energy = EnergyComponent(energy=70.0)  # Below reproduction threshold
    entity.add_component("energy", energy)
    env = MagicMock()
    
    component.update(entity, env)
    env.add_entity.assert_not_called()


@patch('random.random', return_value=0.0)  # Always reproduce
def test_successful_reproduction(_mock_random):
    """Test successful reproduction with component inheritance."""
    # Create parent entity with components
    parent = Entity(position=(5, 5))
    parent.add_component("energy", EnergyComponent(energy=100.0))
    parent.add_component("movement", MovementComponent(speed=1.0))
    parent.add_component("reproduction", ReproductionComponent())
    
    # Create environment
    env = Environment(10, 10)
    env.add_entity(parent)
    
    # Initial entity count
    initial_count = len(env.entities)
    
    # Update reproduction
    parent.get_component("reproduction").update(parent, env)
    
    # Verify offspring was created
    assert len(env.entities) == initial_count + 1
    
    # Find offspring (the new entity)
    offspring_id = next(eid for eid in env.entities.keys() if eid != parent.id)
    offspring = env.entities[offspring_id]
    
    # Verify offspring has inherited components
    assert offspring.has_component("energy")
    assert offspring.has_component("movement")
    assert offspring.has_component("reproduction")
    
    # Verify parent's energy was reduced
    parent_energy = parent.get_component("energy")
    assert parent_energy.energy == 50.0  # 100 - reproduction_cost


@patch('random.random', return_value=1.0)  # Never reproduce
def test_reproduction_chance(_mock_random):
    """Test that reproduction chance prevents constant reproduction."""
    component = ReproductionComponent()
    entity = Entity()
    entity.add_component("energy", EnergyComponent(energy=100.0))
    env = MagicMock()
    
    component.update(entity, env)
    env.add_entity.assert_not_called()


def test_mutation_in_offspring():
    """Test that offspring components have mutated values."""
    # Create parent with specific values
    parent = Entity()
    parent.add_component("energy", EnergyComponent(energy=100.0, decay_rate=0.1))
    parent.add_component("movement", MovementComponent(speed=1.0, movement_cost=0.1))
    reproduction = ReproductionComponent(mutation_rate=0.5)  # High mutation rate for testing
    parent.add_component("reproduction", reproduction)
    
    # Create environment
    env = Environment(10, 10)
    env.add_entity(parent)
    
    # Force reproduction
    with patch('random.random', return_value=0.0):  # Always reproduce
        reproduction.update(parent, env)
    
    # Find offspring
    offspring_id = next(eid for eid in env.entities.keys() if eid != parent.id)
    offspring = env.entities[offspring_id]
    
    # Get offspring components
    offspring_energy = offspring.get_component_typed("energy", EnergyComponent)
    offspring_movement = offspring.get_component_typed("movement", MovementComponent)
    
    # Verify values are different due to mutation
    assert offspring_energy.decay_rate != 0.1
    assert offspring_movement.speed != 1.0
    assert offspring_movement.movement_cost != 0.1


def test_custom_inheritance_settings():
    """Test that custom inheritance settings are respected."""
    # Create parent with all components
    parent = Entity()
    parent.add_component("energy", EnergyComponent())
    parent.add_component("movement", MovementComponent())
    
    # Create reproduction component that only inherits energy
    reproduction = ReproductionComponent(
        inherit_components={"energy": True, "movement": False}
    )
    parent.add_component("reproduction", reproduction)
    
    # Create environment
    env = Environment(10, 10)
    env.add_entity(parent)
    
    # Force reproduction
    with patch('random.random', return_value=0.0):  # Always reproduce
        reproduction.update(parent, env)
    
    # Find offspring
    offspring_id = next(eid for eid in env.entities.keys() if eid != parent.id)
    offspring = env.entities[offspring_id]
    
    # Verify inheritance
    assert offspring.has_component("energy")
    assert not offspring.has_component("movement") 
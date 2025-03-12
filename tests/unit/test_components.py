"""Unit tests for the standard components."""

from unittest.mock import MagicMock, patch
import pytest

from virtuallife.config.models import (
    EnergyConfig,
    MovementConfig,
    ConsumerConfig,
    ReproductionConfig,
)
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
    return Environment(10, 10)


@pytest.fixture
def entity():
    """Create a test entity."""
    return Entity(position=(5, 5))


def test_energy_component_initialization():
    """Test energy component initialization."""
    # Test with default config
    component = EnergyComponent()
    assert component.energy == 100.0
    assert component.max_energy == 100.0
    assert component.decay_rate == 0.1
    assert component.death_threshold == 0.0
    
    # Test with custom config
    config = EnergyConfig(
        initial_energy=200.0,
        max_energy=300.0,
        decay_rate=0.2,
        death_threshold=10.0
    )
    component = EnergyComponent(config=config)
    assert component.energy == 200.0
    assert component.max_energy == 300.0
    assert component.decay_rate == 0.2
    assert component.death_threshold == 10.0
    
    # Test with custom initial energy
    component = EnergyComponent(config=config, energy=150.0)
    assert component.energy == 150.0


def test_energy_component_decay():
    """Test energy decay over time."""
    config = EnergyConfig(initial_energy=100.0, decay_rate=10.0)
    component = EnergyComponent(config=config)
    entity = Entity()
    env = MagicMock()
    
    component.update(entity, env)
    assert component.energy == 90.0  # 100 - 10
    
    component.update(entity, env)
    assert component.energy == 80.0  # 90 - 10


def test_energy_never_negative():
    """Test that energy never goes below zero."""
    config = EnergyConfig(initial_energy=5.0, decay_rate=10.0)
    component = EnergyComponent(config=config)
    entity = Entity()
    env = MagicMock()
    
    component.update(entity, env)
    assert component.energy == 0.0


def test_energy_custom_death_threshold():
    """Test custom death threshold."""
    config = EnergyConfig(initial_energy=100.0, decay_rate=10.0, death_threshold=50.0)
    component = EnergyComponent(config=config)
    entity = Entity()
    env = MagicMock()
    
    # First update: 100 -> 90 (above threshold)
    component.update(entity, env)
    env.remove_entity.assert_not_called()
    
    # Second update: 90 -> 80 (above threshold)
    component.update(entity, env)
    env.remove_entity.assert_not_called()
    
    # Third update: 80 -> 70 (above threshold)
    component.update(entity, env)
    env.remove_entity.assert_not_called()
    
    # Fourth update: 70 -> 60 (above threshold)
    component.update(entity, env)
    env.remove_entity.assert_not_called()
    
    # Fifth update: 60 -> 50 (at threshold)
    component.update(entity, env)
    env.remove_entity.assert_not_called()
    
    # Sixth update: 50 -> 40 (below threshold)
    component.update(entity, env)
    env.remove_entity.assert_called_once_with(entity)


def test_energy_component_death():
    """Test that entity dies when energy depleted."""
    config = EnergyConfig(initial_energy=5.0, decay_rate=10.0)
    component = EnergyComponent(config=config)
    entity = Entity()
    env = MagicMock()
    
    component.update(entity, env)
    env.remove_entity.assert_called_once_with(entity)


def test_energy_consumption():
    """Test energy consumption."""
    component = EnergyComponent(energy=50.0)
    
    # Successful consumption
    assert component.consume_energy(30.0) is True
    assert component.energy == 20.0
    
    # Failed consumption (not enough energy)
    assert component.consume_energy(30.0) is False
    assert component.energy == 20.0


def test_energy_addition():
    """Test adding energy."""
    config = EnergyConfig(initial_energy=50.0, max_energy=100.0)
    component = EnergyComponent(config=config)
    
    # Normal addition
    component.add_energy(30.0)
    assert component.energy == 80.0
    
    # Addition beyond max_energy
    component.add_energy(30.0)
    assert component.energy == 100.0


def test_movement_component_initialization():
    """Test movement component initialization."""
    # Test with default config
    component = MovementComponent()
    assert component.speed == 1.0
    assert component.movement_cost == 0.1
    
    # Test with custom config
    config = MovementConfig(speed=2.0, movement_cost=0.2)
    component = MovementComponent(config=config)
    assert component.speed == 2.0
    assert component.movement_cost == 0.2


def test_movement_with_energy(environment, entity):
    """Test movement with energy consumption."""
    energy = EnergyComponent(energy=100.0)
    config = MovementConfig(speed=1.0, movement_cost=10.0)
    movement = MovementComponent(config=config)
    
    entity.add_component("energy", energy)
    entity.add_component("movement", movement)
    environment.add_entity(entity)
    
    old_position = entity.position
    movement.update(entity, environment)
    
    # Position should change
    assert entity.position != old_position
    # Energy should be consumed
    assert energy.energy == 90.0  # 100 - (1.0 * 10.0)


def test_movement_cost_scaling():
    """Test that movement cost scales correctly with speed."""
    energy = EnergyComponent(energy=100.0)
    config = MovementConfig(speed=2.0, movement_cost=1.0)
    movement = MovementComponent(config=config)
    
    entity = Entity()
    entity.add_component("energy", energy)
    entity.add_component("movement", movement)
    
    env = Environment(10, 10)
    env.add_entity(entity)
    
    movement.update(entity, env)
    assert energy.energy == 98.0  # 100 - (2.0 * 1.0)


def test_movement_boundary_conditions():
    """Test movement with different boundary conditions."""
    # Test wrapped boundaries
    env_wrapped = Environment(10, 10, boundary_condition="wrapped")
    entity = Entity(position=(9, 9))
    config = MovementConfig(speed=2.0)  # Higher speed to ensure boundary crossing
    movement = MovementComponent(config=config)
    energy = EnergyComponent(energy=100.0)
    
    entity.add_component("energy", energy)
    entity.add_component("movement", movement)
    env_wrapped.add_entity(entity)
    
    # Force movement in positive direction
    with patch('random.uniform', return_value=1.5):
        movement.update(entity, env_wrapped)
        x, y = entity.position
        assert 0 <= x < 10 and 0 <= y < 10  # Should wrap around


def test_movement_without_energy(environment, entity):
    """Test movement without energy component."""
    config = MovementConfig(speed=1.0)
    movement = MovementComponent(config=config)
    entity.add_component("movement", movement)
    environment.add_entity(entity)
    
    old_position = entity.position
    movement.update(entity, environment)
    
    # Without energy component, no movement should occur
    assert entity.position == old_position


def test_movement_with_depleted_energy():
    """Test movement when energy is depleted."""
    movement = MovementComponent()
    energy = EnergyComponent(energy=0.0)
    entity = Entity()
    env = MagicMock()
    
    movement.update(entity, env)
    env.move_entity.assert_not_called()


def test_resource_consumer_initialization():
    """Test resource consumer initialization."""
    # Test with default config
    component = ResourceConsumerComponent()
    assert component.resource_type == "food"
    assert component.consumption_rate == 1.0
    assert component.energy_conversion == 0.5
    
    # Test with custom config
    config = ConsumerConfig(
        resource_type="plants",
        consumption_rate=2.0,
        energy_conversion=0.8
    )
    component = ResourceConsumerComponent(config=config)
    assert component.resource_type == "plants"
    assert component.consumption_rate == 2.0
    assert component.energy_conversion == 0.8


def test_resource_consumption():
    """Test resource consumption and energy conversion."""
    consumer = ResourceConsumerComponent()
    energy = EnergyComponent(energy=50.0)
    entity = Entity()
    entity.add_component("energy", energy)
    
    env = MagicMock()
    env.consume_resource.return_value = 2.0
    
    consumer.update(entity, env)
    
    # Check energy was gained
    assert energy.energy == 51.0  # 50 + (2.0 * 0.5)


def test_resource_consumption_without_energy():
    """Test resource consumption without energy component."""
    consumer = ResourceConsumerComponent()
    entity = Entity()
    env = MagicMock()
    
    consumer.update(entity, env)
    env.consume_resource.assert_not_called()


def test_resource_consumption_depletes_resource():
    """Test that resource is properly depleted."""
    consumer = ResourceConsumerComponent()
    energy = EnergyComponent(energy=50.0)
    entity = Entity()
    entity.add_component("energy", energy)
    
    env = MagicMock()
    env.consume_resource.return_value = 0.0
    
    consumer.update(entity, env)
    assert energy.energy == 50.0  # No energy gained


def test_different_resource_types():
    """Test consuming different resource types."""
    config = ConsumerConfig(
        resource_type="plants",
        consumption_rate=1.0,
        energy_conversion=1.0
    )
    consumer = ResourceConsumerComponent(config=config)
    energy = EnergyComponent(energy=50.0)
    entity = Entity()
    entity.add_component("energy", energy)
    
    env = MagicMock()
    env.consume_resource.return_value = 1.0
    
    consumer.update(entity, env)
    env.consume_resource.assert_called_once_with(entity.position, "plants", 1.0)


def test_reproduction_component_initialization():
    """Test reproduction component initialization."""
    # Test with default config
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
        "reproduction": True,
    }
    
    # Test with custom config
    config = ReproductionConfig(
        reproduction_threshold=100.0,
        reproduction_cost=60.0,
        reproduction_chance=0.2,
        offspring_energy=40.0,
        mutation_rate=0.2,
        inherit_components={"energy": True, "movement": False}
    )
    component = ReproductionComponent(config=config)
    assert component.reproduction_threshold == 100.0
    assert component.reproduction_cost == 60.0
    assert component.reproduction_chance == 0.2
    assert component.offspring_energy == 40.0
    assert component.mutation_rate == 0.2
    assert component.inherit_components == {"energy": True, "movement": False}


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
    config = MovementConfig(speed=1.0)
    parent.add_component("movement", MovementComponent(config=config))
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
    parent.add_component("energy", EnergyComponent(energy=100.0, config=EnergyConfig(decay_rate=0.1)))
    parent.add_component("movement", MovementComponent(config=MovementConfig(speed=1.0, movement_cost=0.1)))
    reproduction = ReproductionComponent(config=ReproductionConfig(mutation_rate=0.5))  # High mutation rate for testing
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
    config = ReproductionConfig(inherit_components={"energy": True, "movement": False})
    reproduction = ReproductionComponent(config=config)
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
"""Full simulation integration test.

This test integrates all three core systems (ECS, Environment, Events) to 
simulate a simple ecosystem with entities, movement, and event tracking.
"""

import pytest
from typing import List, Type, Tuple, Dict, Any, Set
from uuid import UUID, uuid4

from virtuallife.ecs import World, Entity, System
from virtuallife.environment import SpatialGrid, ResourceManager
from virtuallife.environment.boundary import (
    BoundaryCondition,
    create_boundary_handler,
)
from virtuallife.events import (
    EventDispatcher,
    EntityEvents,
    EnvironmentEvents,
    LoggingHandler,
    CounterHandler,
)


# Define components

class PositionComponent:
    """Component storing the position of an entity."""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def update(self, entity, world, dt) -> None:
        """Update method to satisfy Component protocol."""
        pass


class MovementComponent:
    """Component storing movement capabilities of an entity."""
    
    def __init__(self, speed: float = 1.0):
        self.speed = speed
        self.direction_x = 0.0
        self.direction_y = 0.0
        
    def update(self, entity, world, dt) -> None:
        """Update method to satisfy Component protocol."""
        pass


class EnergyComponent:
    """Component storing energy level of an entity."""
    
    def __init__(self, energy: float = 100.0, max_energy: float = 100.0):
        self.energy = energy
        self.max_energy = max_energy
        
    def update(self, entity, world, dt) -> None:
        """Update method to satisfy Component protocol."""
        pass
        
    def consume(self, amount: float) -> float:
        """Consume energy from this component.
        
        Args:
            amount: Amount of energy to consume
            
        Returns:
            The actual amount consumed (may be less if insufficient energy)
        """
        if amount <= 0:
            return 0.0
            
        if amount > self.energy:
            consumed = self.energy
            self.energy = 0.0
            return consumed
            
        self.energy -= amount
        return amount
        
    def add(self, amount: float) -> float:
        """Add energy to this component.
        
        Args:
            amount: Amount of energy to add
            
        Returns:
            The actual amount added (may be less if at max energy)
        """
        if amount <= 0:
            return 0.0
            
        if self.energy + amount > self.max_energy:
            added = self.max_energy - self.energy
            self.energy = self.max_energy
            return added
            
        self.energy += amount
        return amount


# Define systems

class MovementSystem(System):
    """System that updates entity positions based on movement."""
    
    def __init__(self, spatial_grid: SpatialGrid, event_dispatcher: EventDispatcher):
        super().__init__()
        self.spatial_grid = spatial_grid
        self.event_dispatcher = event_dispatcher
        
    @property
    def required_components(self) -> List[Type]:
        """Get the component types required by this system."""
        return [PositionComponent, MovementComponent, EnergyComponent]
        
    def process(self, world: World, dt: float) -> None:
        """Process entities with movement and position components."""
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            pos = entity.get_component(PositionComponent)
            movement = entity.get_component(MovementComponent)
            energy = entity.get_component(EnergyComponent)
            
            # Skip if no energy
            if energy.energy <= 0:
                continue
                
            # Calculate old position for event
            old_pos = (pos.x, pos.y)
            
            # Update position based on movement and speed
            movement_cost = movement.speed * dt
            energy.consume(movement_cost)
            
            pos.x += int(movement.direction_x * movement.speed * dt)
            pos.y += int(movement.direction_y * movement.speed * dt)
            
            # Update spatial grid
            new_pos = (pos.x, pos.y)
            self.spatial_grid.update_entity_position(entity_id, new_pos)
            
            # Emit position changed event
            self.event_dispatcher.publish(
                EntityEvents.POSITION_CHANGED,
                sender=entity_id,
                entity_id=entity_id,
                old_pos=old_pos,
                new_pos=new_pos
            )


class EnergySystem(System):
    """System that handles energy consumption and resource collection."""
    
    def __init__(self, 
                spatial_grid: SpatialGrid, 
                resource_manager: ResourceManager,
                event_dispatcher: EventDispatcher):
        super().__init__()
        self.spatial_grid = spatial_grid
        self.resource_manager = resource_manager
        self.event_dispatcher = event_dispatcher
        
    @property
    def required_components(self) -> List[Type]:
        """Get the component types required by this system."""
        return [PositionComponent, EnergyComponent]
        
    def process(self, world: World, dt: float) -> None:
        """Process entities with energy components."""
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            pos = entity.get_component(PositionComponent)
            energy = entity.get_component(EnergyComponent)
            
            # Basic energy consumption over time
            base_consumption = dt * 0.5  # 0.5 energy per time unit
            energy.consume(base_consumption)
            
            # Check if entity is at a resource location and consume resource
            position = (pos.x, pos.y)
            resource_amount = self.resource_manager.get_resource_amount("food", position)
            
            if resource_amount > 0:
                # Entity can consume up to 10 units per time step
                consume_rate = 10.0 * dt
                max_needed = energy.max_energy - energy.energy
                amount_to_consume = min(resource_amount, consume_rate, max_needed)
                
                if amount_to_consume > 0:
                    consumed = self.resource_manager.consume_resource(
                        "food", position, amount_to_consume
                    )
                    
                    energy_added = energy.add(consumed)
                    
                    # Emit resource consumed event
                    self.event_dispatcher.publish(
                        EnvironmentEvents.RESOURCE_CONSUMED,
                        sender=entity_id,
                        entity_id=entity_id,
                        resource_type="food",
                        position=position,
                        amount=consumed
                    )


class ResourceSpawnSystem(System):
    """System that periodically spawns resources in the environment."""
    
    def __init__(self, 
                resource_manager: ResourceManager,
                event_dispatcher: EventDispatcher,
                spawn_interval: float = 5.0,
                resource_value: float = 25.0):
        super().__init__()
        self.resource_manager = resource_manager
        self.event_dispatcher = event_dispatcher
        self.spawn_interval = spawn_interval
        self.resource_value = resource_value
        self.time_accumulator = 0.0
        self.spawn_positions = [
            (25, 25), (75, 25), (25, 75), (75, 75), (50, 50)
        ]
        
    @property
    def required_components(self) -> List[Type]:
        """Get the component types required by this system."""
        return []  # No entity requirements
        
    def process(self, world: World, dt: float) -> None:
        """Process resource spawning."""
        self.time_accumulator += dt
        
        if self.time_accumulator >= self.spawn_interval:
            self.time_accumulator = 0.0
            
            # Spawn resources at predefined positions
            for position in self.spawn_positions:
                current_amount = self.resource_manager.get_resource_amount("food", position)
                
                # Only spawn if no resource exists or it's below a threshold
                if current_amount < 10.0:
                    self.resource_manager.add_resource(
                        "food", position, self.resource_value
                    )
                    
                    # Emit resource added event
                    self.event_dispatcher.publish(
                        EnvironmentEvents.RESOURCE_ADDED,
                        sender="system",
                        resource_type="food",
                        position=position,
                        amount=self.resource_value
                    )


# Event handler to track entity deaths
class EntityDeathTracker:
    """Event handler to track entity deaths."""
    
    def __init__(self):
        self.dead_entities: Set[UUID] = set()
        
    def __call__(self, sender, **kwargs):
        """Handle entity destroyed event."""
        entity_id = kwargs.get('entity_id')
        self.dead_entities.add(entity_id)


# Fixture for full simulation
@pytest.fixture
def full_simulation() -> Tuple[World, SpatialGrid, ResourceManager, EventDispatcher, EntityDeathTracker]:
    """Create a full simulation with ECS, Environment, and Events."""
    # Create event dispatcher
    dispatcher = EventDispatcher()
    
    # Create environment components
    width, height = 100, 100
    boundary = create_boundary_handler(BoundaryCondition.WRAPPED, width, height)
    grid = SpatialGrid(width, height, boundary)
    resources = ResourceManager()
    
    # Create world
    world = World()
    
    # Create and register event handlers
    position_counter = CounterHandler()
    resource_counter = CounterHandler()
    death_tracker = EntityDeathTracker()
    
    dispatcher.subscribe(EntityEvents.POSITION_CHANGED, position_counter)
    dispatcher.subscribe(EnvironmentEvents.RESOURCE_CONSUMED, resource_counter)
    dispatcher.subscribe(EntityEvents.DESTROYED, death_tracker)
    
    # Create and add systems
    movement_system = MovementSystem(grid, dispatcher)
    energy_system = EnergySystem(grid, resources, dispatcher)
    resource_system = ResourceSpawnSystem(resources, dispatcher)
    
    world.add_system(movement_system)
    world.add_system(energy_system)
    world.add_system(resource_system)
    
    # Initialize resources
    for pos in [(25, 25), (75, 25), (25, 75), (75, 75), (50, 50)]:
        resources.add_resource("food", pos, 50.0)
    
    return world, grid, resources, dispatcher, death_tracker


def test_simple_ecosystem_simulation(full_simulation):
    """Test a simple ecosystem simulation with all components integrated."""
    world, grid, resources, dispatcher, death_tracker = full_simulation
    
    # Create entities with random movement
    entities = []
    positions = [(30, 30), (70, 30), (30, 70), (70, 70)]
    
    for i, pos in enumerate(positions):
        entity = Entity()
        entity.add_component(PositionComponent(pos[0], pos[1]))
        entity.add_component(MovementComponent(speed=1.0))
        entity.add_component(EnergyComponent(energy=50.0))
        
        # Set movement direction to head toward center
        movement = entity.get_component(MovementComponent)
        if pos[0] < 50:
            movement.direction_x = 1.0
        else:
            movement.direction_x = -1.0
            
        if pos[1] < 50:
            movement.direction_y = 1.0
        else:
            movement.direction_y = -1.0
        
        entity_id = world.add_entity(entity)
        grid.add_entity(entity_id, pos)
        entities.append(entity_id)
    
    # Run simulation for 50 steps
    for step in range(50):
        world.update(1.0)
    
    # Verify entities moved from initial positions
    for i, entity_id in enumerate(entities):
        if entity_id in death_tracker.dead_entities:
            continue  # Skip dead entities
            
        entity = world.get_entity(entity_id)
        pos = entity.get_component(PositionComponent)
        initial_pos = positions[i]
        
        # Entity should have moved from initial position
        assert (pos.x, pos.y) != initial_pos
        
    # Verify resources were consumed
    center_resource = resources.get_resource_amount("food", (50, 50))
    assert center_resource < 50.0  # Some resources should have been consumed 
"""Integration tests for ECS and Environment components.

These tests verify that the Entity-Component-System (ECS) architecture and
the Environment components work together correctly.
"""

import pytest
from uuid import UUID, uuid4
from typing import List, Type, Tuple

from virtuallife.ecs import World, Entity, System
from virtuallife.environment import SpatialGrid
from virtuallife.environment.boundary import (
    BoundaryCondition,
    create_boundary_handler,
)


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


class MovementSystem(System):
    """System that updates entity positions based on movement."""
    
    def __init__(self, spatial_grid: SpatialGrid):
        super().__init__()
        self.spatial_grid = spatial_grid
        
    @property
    def required_components(self) -> List[Type]:
        """Get the component types required by this system."""
        return [PositionComponent, MovementComponent]
        
    def process(self, world: World, dt: float) -> None:
        """Process entities with movement and position components."""
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            pos = entity.get_component(PositionComponent)
            movement = entity.get_component(MovementComponent)
            
            # Update position based on movement and speed
            pos.x += int(movement.direction_x * movement.speed * dt)
            pos.y += int(movement.direction_y * movement.speed * dt)
            
            # Update spatial grid
            self.spatial_grid.update_entity_position(entity_id, (pos.x, pos.y))


@pytest.fixture
def world_with_grid() -> Tuple[World, SpatialGrid]:
    """Create a world and spatial grid for testing."""
    width, height = 100, 100
    boundary = create_boundary_handler(BoundaryCondition.WRAPPED, width, height)
    grid = SpatialGrid(width, height, boundary)
    
    world = World()
    movement_system = MovementSystem(grid)
    world.add_system(movement_system)
    
    return world, grid


def test_entity_movement_updates_spatial_grid(world_with_grid: Tuple[World, SpatialGrid]):
    """Test that entity movement updates the spatial grid correctly."""
    world, grid = world_with_grid
    
    # Create an entity with position and movement
    entity = Entity()
    entity.add_component(PositionComponent(10, 10))
    entity.add_component(MovementComponent(speed=1.0))
    
    # Set movement direction (moving right and down)
    movement = entity.get_component(MovementComponent)
    movement.direction_x = 1.0
    movement.direction_y = 1.0
    
    # Add entity to world and grid
    entity_id = world.add_entity(entity)
    grid.add_entity(entity_id, (10, 10))
    
    # Initially, entity should be at (10, 10)
    entities_at_start = grid.get_entities_at_position((10, 10))
    assert entity_id in entities_at_start
    
    # Update world (dt=1.0 means it should move 1 unit in each direction)
    world.update(1.0)
    
    # Entity should now be at (11, 11)
    entities_at_end = grid.get_entities_at_position((11, 11))
    assert entity_id in entities_at_end
    
    # And not at the original position
    entities_at_start = grid.get_entities_at_position((10, 10))
    assert entity_id not in entities_at_start
    
    # Position component should be updated
    position = entity.get_component(PositionComponent)
    assert position.x == 11
    assert position.y == 11


def test_multiple_entities_in_spatial_grid(world_with_grid: Tuple[World, SpatialGrid]):
    """Test that multiple entities can be tracked in the spatial grid."""
    world, grid = world_with_grid
    
    # Create several entities at different positions
    entity_positions = [(5, 5), (10, 10), (15, 15), (20, 20)]
    entity_ids = []
    
    for x, y in entity_positions:
        entity = Entity()
        entity.add_component(PositionComponent(x, y))
        entity_id = world.add_entity(entity)
        grid.add_entity(entity_id, (x, y))
        entity_ids.append(entity_id)
    
    # Check entities at their positions
    for i, (x, y) in enumerate(entity_positions):
        entities = grid.get_entities_at_position((x, y))
        assert entity_ids[i] in entities
    
    # Test spatial queries
    entities_in_radius = grid.get_entities_in_radius((10, 10), radius=7)
    # Should include entities at (5, 5), (10, 10), and (15, 15)
    assert len(entities_in_radius) == 3
    assert entity_ids[0] in entities_in_radius  # (5, 5)
    assert entity_ids[1] in entities_in_radius  # (10, 10)
    assert entity_ids[2] in entities_in_radius  # (15, 15)
    assert entity_ids[3] not in entities_in_radius  # (20, 20)
    
    # Test nearest entities
    nearest = grid.get_nearest_entities((12, 12), count=2)
    # Should be (10, 10) and (15, 15)
    assert len(nearest) == 2
    assert entity_ids[1] in nearest[0] or entity_ids[1] in nearest[1]
    assert entity_ids[2] in nearest[0] or entity_ids[2] in nearest[1]


def test_boundary_conditions_with_movement(world_with_grid: Tuple[World, SpatialGrid]):
    """Test that boundary conditions are applied correctly with movement."""
    world, grid = world_with_grid
    
    # Create entity at edge of grid
    entity = Entity()
    entity.add_component(PositionComponent(99, 99))  # Bottom-right corner
    entity.add_component(MovementComponent(speed=2.0))
    
    # Set movement direction (moving right and down, which should wrap around)
    movement = entity.get_component(MovementComponent)
    movement.direction_x = 1.0
    movement.direction_y = 1.0
    
    # Add entity to world and grid
    entity_id = world.add_entity(entity)
    grid.add_entity(entity_id, (99, 99))
    
    # Update world
    world.update(1.0)
    
    # With wrapped boundaries, entity should now be at (1, 1)
    entities_at_wrapped = grid.get_entities_at_position((1, 1))
    assert entity_id in entities_at_wrapped
    
    # Position component should be updated
    position = entity.get_component(PositionComponent)
    assert position.x == 1
    assert position.y == 1 
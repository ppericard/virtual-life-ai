# VirtualLife Environment

The Environment module manages the spatial and resource aspects of the VirtualLife simulation. It provides specialized components for handling entity positions, boundary conditions, and resource management.

## Core Components

### SpatialGrid

The `SpatialGrid` class provides efficient spatial partitioning for entity position tracking and querying. It enables:

- Tracking entity positions
- Finding entities in specific locations
- Querying entities within a radius or rectangular area
- Efficient nearest-neighbor searches

### BoundaryHandler

The `BoundaryHandler` classes determine how positions are handled at the edges of the simulation area. Three boundary conditions are supported:

- **WrappedBoundary**: Positions wrap around from one edge to the opposite (toroidal world)
- **BoundedBoundary**: Positions are constrained within the grid boundaries
- **InfiniteBoundary**: No boundary constraints are applied

### ResourceManager

The `ResourceManager` class handles the creation, distribution, and consumption of resources in the environment. Key features include:

- Adding resources at specific positions
- Resource consumption and replenishment
- Resource querying by position or area
- Optional resource clustering

## Usage Examples

### Working with the SpatialGrid

```python
from virtuallife.environment import SpatialGrid
from virtuallife.environment.boundary import BoundaryCondition, create_boundary_handler
from uuid import uuid4

# Create a spatial grid with wrapped boundaries
grid_size = (100, 100)
boundary_handler = create_boundary_handler(BoundaryCondition.WRAPPED, grid_size)
grid = SpatialGrid(grid_size[0], grid_size[1], boundary_handler)

# Add entities to the grid
entity_id = uuid4()
position = (10, 20)
grid.add_entity(entity_id, position)

# Update entity position
new_position = (15, 25)
grid.update_entity_position(entity_id, new_position)

# Find entities in an area
entities_in_radius = grid.get_entities_in_radius((15, 25), radius=5)
print(f"Entities within radius: {entities_in_radius}")

# Find entities at a specific position
entities_at_position = grid.get_entities_at_position((15, 25))
print(f"Entities at position: {entities_at_position}")

# Find nearest entities
nearest = grid.get_nearest_entities((15, 25), count=3)
print(f"Nearest entities: {nearest}")

# Remove entity from grid
grid.remove_entity(entity_id)
```

### Using Different Boundary Conditions

```python
from virtuallife.environment.boundary import (
    BoundaryCondition, 
    create_boundary_handler, 
    WrappedBoundary,
    BoundedBoundary,
    InfiniteBoundary
)

# Create boundary handlers using factory function
grid_size = (100, 100)
wrapped = create_boundary_handler(BoundaryCondition.WRAPPED, grid_size)
bounded = create_boundary_handler(BoundaryCondition.BOUNDED, grid_size)
infinite = create_boundary_handler(BoundaryCondition.INFINITE, grid_size)

# Or create them directly
wrapped = WrappedBoundary(100, 100)
bounded = BoundedBoundary(100, 100)
infinite = InfiniteBoundary()

# Normalize positions based on boundary conditions
position = (110, 120)  # Outside grid bounds

# Position wraps around to (10, 20)
wrapped_pos = wrapped.normalize_position(position)
print(f"Wrapped position: {wrapped_pos}")

# Position is clamped to (99, 99)
bounded_pos = bounded.normalize_position(position)
print(f"Bounded position: {bounded_pos}")

# Position remains unchanged
infinite_pos = infinite.normalize_position(position)
print(f"Infinite position: {infinite_pos}")
```

### Managing Resources

```python
from virtuallife.environment.resources import ResourceManager
from uuid import uuid4

# Create a resource manager
resource_manager = ResourceManager()

# Add resources to the environment
resource_manager.add_resource("food", (10, 10), amount=100.0)
resource_manager.add_resource("water", (20, 20), amount=50.0)

# Check resource availability
food_amount = resource_manager.get_resource_amount("food", (10, 10))
print(f"Food at (10, 10): {food_amount}")

# Consume resources
consumed = resource_manager.consume_resource("food", (10, 10), amount=30.0)
print(f"Consumed: {consumed}")  # 30.0
remaining = resource_manager.get_resource_amount("food", (10, 10))
print(f"Remaining: {remaining}")  # 70.0

# Add resource in multiple locations
positions = [(30, 30), (35, 35), (40, 40)]
for pos in positions:
    resource_manager.add_resource("energy", pos, amount=25.0)

# Find resources within area
energy_in_area = resource_manager.get_resources_in_area("energy", (30, 30), radius=15)
print(f"Energy resources in area: {energy_in_area}")

# Remove resources
resource_manager.remove_resource("food", (10, 10))
```

## Integration with ECS

The environment components are designed to work seamlessly with the ECS architecture:

```python
from virtuallife.ecs import World, Entity, System
from virtuallife.environment import SpatialGrid
from virtuallife.environment.boundary import BoundaryCondition, create_boundary_handler
from typing import List, Type
import uuid

# Create an environment
grid_size = (100, 100)
boundary_handler = create_boundary_handler(BoundaryCondition.WRAPPED, grid_size)
grid = SpatialGrid(grid_size[0], grid_size[1], boundary_handler)

# Create ECS world
world = World()

# Define a position component
class PositionComponent:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def update(self, entity, world, dt):
        pass

# Define a system that updates the spatial grid
class SpatialSystem(System):
    def __init__(self, spatial_grid: SpatialGrid):
        super().__init__()
        self.spatial_grid = spatial_grid
        
    @property
    def required_components(self) -> List[Type]:
        return [PositionComponent]
        
    def process(self, world: World, dt: float) -> None:
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            position = entity.get_component(PositionComponent)
            
            # Update position in spatial grid
            self.spatial_grid.update_entity_position(
                entity_id, 
                (position.x, position.y)
            )

# Register the system
spatial_system = SpatialSystem(grid)
world.add_system(spatial_system)

# Create an entity with position
entity = Entity()
entity.add_component(PositionComponent(10, 20))
entity_id = world.add_entity(entity)

# Add entity to spatial grid
grid.add_entity(entity_id, (10, 20))

# Update the world
world.update(0.1)
```

## Performance Considerations

The Environment module is optimized for performance:

- **Spatial partitioning**: Entity lookups use O(1) cell access rather than O(n) entity iteration
- **Sparse resource representation**: Only non-zero resource values are stored
- **Position caching**: Entity positions are cached to avoid redundant calculations
- **Efficient area queries**: Area queries use cell-based filtering before distance checks

## Best Practices

1. **Choose appropriate boundary conditions**: Match the boundary type to your simulation needs
2. **Use spatial queries efficiently**: Prefer cell-based queries over full grid scans
3. **Manage entity-grid synchronization**: Keep entity positions and the spatial grid in sync
4. **Consider cell size trade-offs**: Smaller cells provide more precise spatial partitioning but use more memory
5. **Handle resource depletion properly**: Decide how to handle resource exhaustion (remove or keep at zero)
6. **Optimize resource distribution**: Use clustering for more realistic resource patterns 
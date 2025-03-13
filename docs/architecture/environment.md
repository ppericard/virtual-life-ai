# Environment Architecture

## Overview

The environment in VirtualLife is the space where entities exist and interact. It has been refactored to separate concerns into specialized components: the spatial grid system, boundary handling, and resource management. This document explains the architecture of the environment system, its components, and how they interact.

## Core Components

### Spatial Grid

The spatial grid manages entity positions and provides efficient spatial queries:

- Tracks which entities are at which positions
- Provides methods to find entities in a specific area
- Supports efficient neighborhood queries
- Uses spatial partitioning for performance with large entity counts

### Boundary Handler

The boundary handler manages the edges of the environment:

- Implements different boundary types (wrapped, bounded, infinite)
- Normalizes positions based on boundary rules
- Handles out-of-bounds conditions
- Provides consistent boundary behavior for entity movement

### Resource Management

The resource management system handles the creation, distribution, and consumption of resources:

- Tracks resource types and amounts at specific locations
- Provides methods to add, remove, and query resources
- Implements resource regeneration and decay
- Supports different resource distribution patterns

## Design Decisions

### Separation of Concerns

**Decision**: Split the monolithic Environment class into specialized components

**Rationale**:
- Improves maintainability by focusing each class on a single responsibility
- Makes testing easier as each component can be tested in isolation
- Enables more flexible environment configurations
- Allows for more efficient implementations of specific features

**Implementation**:
```python
# Previously, everything was in a single Environment class:
env = Environment(width=100, height=100)
env.add_entity(entity)
env.add_resource("food", (10, 10), 5.0)
nearby_entities = env.get_entities_in_radius((10, 10), 3)

# Now, we use specialized components:
grid = SpatialGrid(width=100, height=100, boundary_handler=WrappedBoundary(100, 100))
resources = ResourceManager(width=100, height=100)
grid.add_entity(entity)
resources.add_resource("food", (10, 10), 5.0)
nearby_entities = grid.get_entities_in_radius((10, 10), 3)
```

### Spatial Partitioning

**Decision**: Implement a spatial partitioning system for entity lookups

**Rationale**:
- Drastically improves performance for spatial queries in large environments
- Reduces complexity from O(n) to O(k) where k is the number of entities in relevant partitions
- Enables efficient collision detection and proximity checks
- Scales better with increasing entity counts

**Implementation**:
```python
# The grid uses spatial partitioning internally:
class SpatialGrid:
    def __init__(self, width, height, cell_size=10, boundary_handler=None):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.boundary_handler = boundary_handler or WrappedBoundary(width, height)
        self.cells = defaultdict(set)  # Maps cell coordinates to sets of entity IDs
        
    def position_to_cell(self, position):
        """Convert a position to a cell coordinate."""
        x, y = position
        return (x // self.cell_size, y // self.cell_size)
        
    def add_entity(self, entity):
        """Add an entity to the grid."""
        cell = self.position_to_cell(entity.position)
        self.cells[cell].add(entity.id)
```

### Flexible Boundary Conditions

**Decision**: Implement different boundary handlers as strategy objects

**Rationale**:
- Makes it easy to switch between boundary types
- Encapsulates boundary logic in specialized classes
- Enables custom boundary implementations
- Provides consistent behavior across the simulation

**Implementation**:
```python
# Define boundary strategies:
class BoundaryHandler(abc.ABC):
    @abc.abstractmethod
    def normalize_position(self, position: Position) -> Position:
        """Normalize a position according to boundary rules."""
        pass

class WrappedBoundary(BoundaryHandler):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def normalize_position(self, position: Position) -> Position:
        """Wrap position around boundaries (toroidal)."""
        x, y = position
        return (x % self.width, y % self.height)

class BoundedBoundary(BoundaryHandler):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def normalize_position(self, position: Position) -> Position:
        """Clamp position to boundaries."""
        x, y = position
        return (max(0, min(x, self.width - 1)), 
                max(0, min(y, self.height - 1)))
```

### Resource Clustering

**Decision**: Implement resource clustering for more realistic resource distribution

**Rationale**:
- Creates more interesting simulation dynamics
- Models real-world resource distributions more accurately
- Encourages territory formation and competition
- Makes resource collection more strategic

**Implementation**:
```python
def generate_resource_clusters(
    width: int, 
    height: int, 
    resource_type: str,
    cluster_count: int,
    cluster_size: int,
    resource_value: float
) -> None:
    """Generate clusters of resources."""
    for _ in range(cluster_count):
        # Generate cluster center
        center_x = random.randint(0, width - 1)
        center_y = random.randint(0, height - 1)
        
        # Generate resources around center
        for _ in range(cluster_size):
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            x = (center_x + dx) % width
            y = (center_y + dy) % height
            
            # Add resource with random variation
            value = resource_value * random.uniform(0.8, 1.2)
            self.add_resource(resource_type, (x, y), value)
```

## Component Interactions

### Grid and Boundary Handler

The grid uses a boundary handler to normalize positions:

```python
class SpatialGrid:
    def __init__(self, width, height, boundary_handler):
        self.width = width
        self.height = height
        self.boundary_handler = boundary_handler
        
    def move_entity(self, entity_id, dx, dy):
        """Move an entity by delta, respecting boundary conditions."""
        # Get entity's current position
        entity = self.get_entity(entity_id)
        old_position = entity.position
        
        # Calculate new position
        new_x = old_position[0] + dx
        new_y = old_position[1] + dy
        
        # Normalize the position based on boundary conditions
        normalized_position = self.boundary_handler.normalize_position((new_x, new_y))
        
        # Update entity's position
        self.remove_entity_from_position(entity_id, old_position)
        self.add_entity_to_position(entity_id, normalized_position)
        entity.position = normalized_position
```

### Grid and Resource Manager

The grid and resource manager work together to handle entity-resource interactions:

```python
class ConsumptionSystem(System):
    def __init__(self, grid, resources):
        super().__init__()
        self.grid = grid
        self.resources = resources
        self.required_components = [ConsumerComponent]
        
    def process(self, world, dt):
        for entity_id in self.entities:
            entity = world.get_entity(entity_id)
            consumer = entity.get_component(ConsumerComponent)
            
            # Check for resources at entity's position
            position = entity.position
            resource_amount = self.resources.get_resource(
                consumer.resource_type, position)
            
            if resource_amount > 0:
                # Calculate how much to consume
                amount_to_consume = min(resource_amount, consumer.consumption_rate * dt)
                
                # Consume resource
                self.resources.remove_resource(
                    consumer.resource_type, position, amount_to_consume)
                
                # Add energy to entity if it has an energy component
                if entity.has_component(EnergyComponent):
                    energy = entity.get_component(EnergyComponent)
                    energy.add_energy(amount_to_consume * consumer.efficiency)
```

## Usage Examples

### Basic Environment Setup

```python
from virtuallife.environment import SpatialGrid, ResourceManager
from virtuallife.environment.boundary import WrappedBoundary

# Create environment components
width, height = 100, 100
boundary_handler = WrappedBoundary(width, height)
grid = SpatialGrid(width, height, boundary_handler)
resources = ResourceManager(width, height)

# Add resources to the environment
resources.add_resource("grass", (10, 10), 5.0)
resources.add_resource("water", (20, 20), 10.0)

# Create and add entities
herbivore = Entity(position=(5, 5))
herbivore.add_component(ConsumerComponent(resource_type="grass", consumption_rate=0.5))
grid.add_entity(herbivore)
```

### Finding Nearby Entities

```python
from virtuallife.environment import SpatialGrid
from virtuallife.environment.boundary import WrappedBoundary

# Create grid with wrapped boundary
grid = SpatialGrid(100, 100, WrappedBoundary(100, 100))

# Add some entities
for i in range(10):
    entity = Entity(position=(random.randint(0, 99), random.randint(0, 99)))
    grid.add_entity(entity)

# Find entities near a position
center_position = (50, 50)
radius = 10
nearby_entity_ids = grid.get_entities_in_radius(center_position, radius)

print(f"Found {len(nearby_entity_ids)} entities within radius {radius} of {center_position}")

# Get the actual entities
nearby_entities = [grid.get_entity(entity_id) for entity_id in nearby_entity_ids]
```

### Resource Distribution and Consumption

```python
from virtuallife.environment import ResourceManager

# Create resource manager
resources = ResourceManager(100, 100)

# Add resource clusters
resources.generate_resource_clusters(
    resource_type="food", 
    cluster_count=5, 
    cluster_size=20,
    resource_value=2.0
)

# Find resources in an area
center = (50, 50)
radius = 5
food_in_area = resources.get_resources_in_radius("food", center, radius)

print(f"Total food in area: {sum(food_in_area.values())}")

# Consume some resources
entity_position = (52, 48)
if resources.has_resource("food", entity_position):
    amount = resources.get_resource("food", entity_position)
    consumed = min(amount, 0.5)  # Consume up to 0.5 units
    resources.remove_resource("food", entity_position, consumed)
    print(f"Consumed {consumed} units of food at {entity_position}")
```

### Moving Entities with Boundary Conditions

```python
from virtuallife.environment import SpatialGrid
from virtuallife.environment.boundary import WrappedBoundary, BoundedBoundary

# Create grids with different boundary types
wrapped_grid = SpatialGrid(100, 100, WrappedBoundary(100, 100))
bounded_grid = SpatialGrid(100, 100, BoundedBoundary(100, 100))

# Add entity at same position to both grids
entity1 = Entity(position=(90, 90))
entity2 = Entity(position=(90, 90))
wrapped_grid.add_entity(entity1)
bounded_grid.add_entity(entity2)

# Move entities outside the boundaries
wrapped_grid.move_entity(entity1.id, 20, 20)  # Moving to (110, 110)
bounded_grid.move_entity(entity2.id, 20, 20)  # Moving to (110, 110)

# Check final positions
print(f"Wrapped boundary: {entity1.position}")  # Should be (10, 10)
print(f"Bounded boundary: {entity2.position}")  # Should be (99, 99)
```

## Integration with ECS

The environment components integrate with the Entity-Component-System architecture:

```python
from virtuallife.ecs import World, System
from virtuallife.environment import SpatialGrid, ResourceManager
from virtuallife.environment.boundary import WrappedBoundary

# Create environment components
width, height = 100, 100
boundary_handler = WrappedBoundary(width, height)
grid = SpatialGrid(width, height, boundary_handler)
resources = ResourceManager(width, height)

# Create world
world = World()

# Create systems that use environment components
movement_system = MovementSystem(grid)
consumption_system = ConsumptionSystem(grid, resources)
resource_regen_system = ResourceRegenerationSystem(resources)

# Register systems with the world
world.register_system(movement_system)
world.register_system(consumption_system)
world.register_system(resource_regen_system)

# Create entities
for i in range(10):
    entity = Entity(position=(random.randint(0, 99), random.randint(0, 99)))
    entity.add_component(MovementComponent(speed=1.0))
    entity.add_component(ConsumerComponent(resource_type="food", consumption_rate=0.5))
    
    # Add entity to both world and grid
    world.add_entity(entity)
    grid.add_entity(entity)

# Add resources
resources.generate_resource_clusters(
    resource_type="food", 
    cluster_count=5, 
    cluster_size=20,
    resource_value=2.0
)

# Run the simulation
for step in range(100):
    world.update(dt=1.0)
```

## Performance Considerations

The environment architecture is optimized for performance:

1. **Spatial Partitioning**:
   - Divides space into cells for O(1) position lookups
   - Only processes entities in relevant grid cells
   - Significantly improves performance for spatial queries

2. **Sparse Resource Storage**:
   - Only stores non-zero resource values
   - Reduces memory usage for large environments
   - Speeds up resource queries

3. **Efficient Boundary Handling**:
   - Avoids expensive checks for common boundary conditions
   - Optimizes wrapped boundary math for performance
   - Uses fast lookup tables for complex boundary types

4. **Caching**:
   - Caches common queries and calculation results
   - Updates caches incrementally when possible
   - Invalidates caches only when necessary

## Future Extensions

The environment architecture is designed to be extended:

1. **Additional Boundary Types**:
   - Partial wrapping (cylinder topology)
   - Spherical mapping
   - Portals between regions

2. **Enhanced Resource Systems**:
   - Resource flow and diffusion
   - Weather and seasonal effects
   - Terrain types affecting resources

3. **Optimizations**:
   - Multi-resolution grids
   - Quad-tree or octree spatial partitioning
   - Parallel processing for large environments

## Conclusion

The refactored environment architecture provides a flexible and efficient foundation for the VirtualLife simulation. By separating concerns into specialized components (grid, boundary, resources), we've improved maintainability, testability, and performance. The architecture is designed to scale with increasing environment sizes and entity counts, while allowing for future extensions and optimizations. 
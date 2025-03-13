# VirtualLife Event System

The VirtualLife Event System provides a flexible way for components of the simulation to communicate without tight coupling. It follows the observer pattern, allowing components to subscribe to events and be notified when those events occur.

## Key Components

- **EventDispatcher**: Central hub for event publishing and subscription management
- **Event Types**: Standard event type constants for consistent event naming
- **Event Handlers**: Reusable handler implementations for common event processing scenarios

## Getting Started

### Basic Usage

```python
from virtuallife.events import EventDispatcher, EntityEvents

# Create an event dispatcher
dispatcher = EventDispatcher()

# Define a handler function
def on_entity_created(sender, entity_id, **kwargs):
    print(f"Entity {entity_id} was created by {sender}")

# Subscribe to events
dispatcher.subscribe(EntityEvents.CREATED, on_entity_created)

# Publish events
dispatcher.publish(EntityEvents.CREATED, "world", entity_id="123")
# Output: Entity 123 was created by world
```

### Using Standard Event Handlers

```python
from virtuallife.events import EventDispatcher, EntityEvents
from virtuallife.events import LoggingHandler, CounterHandler

# Create an event dispatcher
dispatcher = EventDispatcher()

# Create standard handlers
logging_handler = LoggingHandler("Entity created: {entity_id}")
counter_handler = CounterHandler()

# Subscribe handlers
dispatcher.subscribe(EntityEvents.CREATED, logging_handler)
dispatcher.subscribe(EntityEvents.CREATED, counter_handler)

# Publish events
dispatcher.publish(EntityEvents.CREATED, "world", entity_id="123")
# Output: Entity created: 123

# Check counter
print(f"Entities created: {counter_handler.count}")
# Output: Entities created: 1
```

### Advanced: Filtered and Aggregate Handlers

```python
from virtuallife.events import EventDispatcher, EntityEvents
from virtuallife.events import CounterHandler, FilteredHandler, AggregateHandler

# Create an event dispatcher
dispatcher = EventDispatcher()

# Create counters for different entity types
player_counter = CounterHandler()
npc_counter = CounterHandler()

# Create filters
player_filter = lambda sender, kwargs: kwargs.get("entity_type") == "player"
npc_filter = lambda sender, kwargs: kwargs.get("entity_type") == "npc"

# Create filtered handlers
player_handler = FilteredHandler(player_counter, player_filter)
npc_handler = FilteredHandler(npc_counter, npc_filter)

# Subscribe handlers
dispatcher.subscribe(EntityEvents.CREATED, player_handler)
dispatcher.subscribe(EntityEvents.CREATED, npc_handler)

# Alternatively, use an aggregate handler
# aggregate = AggregateHandler([player_handler, npc_handler])
# dispatcher.subscribe(EntityEvents.CREATED, aggregate)

# Publish events
dispatcher.publish(EntityEvents.CREATED, "world", entity_id="1", entity_type="player")
dispatcher.publish(EntityEvents.CREATED, "world", entity_id="2", entity_type="npc")
dispatcher.publish(EntityEvents.CREATED, "world", entity_id="3", entity_type="item")

# Check counters
print(f"Players created: {player_counter.count}")  # Output: Players created: 1
print(f"NPCs created: {npc_counter.count}")        # Output: NPCs created: 1
```

## Standard Event Types

### Entity Events

- `EntityEvents.CREATED`: Triggered when an entity is created
- `EntityEvents.DESTROYED`: Triggered when an entity is destroyed
- `EntityEvents.COMPONENT_ADDED`: Triggered when a component is added to an entity
- `EntityEvents.COMPONENT_REMOVED`: Triggered when a component is removed from an entity
- `EntityEvents.COMPONENT_UPDATED`: Triggered when a component is updated
- `EntityEvents.POSITION_CHANGED`: Triggered when an entity's position changes

### Environment Events

- `EnvironmentEvents.GRID_CHANGED`: Triggered when the grid changes
- `EnvironmentEvents.ENTITY_ADDED_TO_GRID`: Triggered when an entity is added to the grid
- `EnvironmentEvents.ENTITY_REMOVED_FROM_GRID`: Triggered when an entity is removed from the grid
- `EnvironmentEvents.RESOURCE_ADDED`: Triggered when a resource is added
- `EnvironmentEvents.RESOURCE_REMOVED`: Triggered when a resource is removed
- `EnvironmentEvents.RESOURCE_CONSUMED`: Triggered when a resource is consumed

### Simulation Events

- `SimulationEvents.STARTED`: Triggered when the simulation starts
- `SimulationEvents.PAUSED`: Triggered when the simulation is paused
- `SimulationEvents.RESUMED`: Triggered when the simulation is resumed
- `SimulationEvents.STOPPED`: Triggered when the simulation stops
- `SimulationEvents.STEP_STARTED`: Triggered when a simulation step starts
- `SimulationEvents.STEP_COMPLETED`: Triggered when a simulation step completes

### System Events

- `SystemEvents.REGISTERED`: Triggered when a system is registered
- `SystemEvents.UNREGISTERED`: Triggered when a system is unregistered
- `SystemEvents.PROCESS_STARTED`: Triggered when a system starts processing
- `SystemEvents.PROCESS_COMPLETED`: Triggered when a system completes processing

## Creating Custom Event Handlers

You can create custom event handlers by implementing the `EventHandler` protocol:

```python
from virtuallife.events import EventHandler

class CustomHandler:
    """Custom event handler."""
    
    def __call__(self, sender, **kwargs):
        """Handle an event."""
        entity_id = kwargs.get("entity_id")
        # Custom processing logic
        print(f"Custom handler processed entity {entity_id}")
```

## Best Practices

1. **Use standard event types**: Use the provided event type constants for consistency.
2. **Keep handlers focused**: Each handler should have a single responsibility.
3. **Filter events**: Use filtered handlers to process only relevant events.
4. **Unsubscribe when done**: Remember to unsubscribe handlers when they are no longer needed.
5. **Avoid circular event chains**: Be careful with handlers that publish events to avoid infinite loops.
6. **Include relevant data**: When publishing events, include all data that handlers might need.
7. **Avoid long-running handlers**: Event handlers should complete quickly to avoid blocking other handlers. 
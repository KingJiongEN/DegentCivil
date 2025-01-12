# Quick Start Guide

This guide will help you get started with the Degent Civilization quickly. We'll create a simple simulation with buildings and characters.

## Prerequisites

Ensure you have:
- Completed the [installation](installation.md) process
- Set up your OpenAI API key
- Started the required services (Milvus and Redis)

## Basic Usage

### 1. Configure Environment

First, set up your environment variables:
```bash
export DEBUG=1
export Milvus=1
```

### 2. Start the Simulation

```python
from app.service.simulation import Simulation

# Initialize simulation with config files
simulation = Simulation(
    state_config_file='config/states.yaml',
    oai_config_file='OAI_CONFIG_LIST'
)

# Start the service
simulation.debug_service()  # For testing without frontend
```

### 3. Working with Buildings

```python
# Access building list
buildings = simulation.building_list

# Get a specific building
cafe = buildings.get_building_by_name("Coffee Shop")

# Get building by position
building_at_pos = buildings.get_building_by_pos(x=10, y=10)
```

### 4. Working with Characters

```python
# Access character list
characters = simulation.character_list

# Get character state managers
state_managers = simulation.character_state_managers

# Access specific character's state manager
character_manager = state_managers["Alice"]
```

## Example Scenarios

### 1. Character State Management

```python
# Get character's current state
state_manager = simulation.character_state_managers["Alice"]
current_state = state_manager.current_state.state_name

# Update character state
simulation.update_state()
```

### 2. Message Handling

```python
# Handle server messages
server_msgs = simulation.handle_server_msg()

# Filter messages for specific character
character_manager = simulation.character_state_managers["Alice"]
filtered_msg = simulation.filter_out_msg(server_msgs, character_manager)
```

## Memory System Usage

```python
# Access character's memory
character = simulation.character_list.get_character_by_name("Alice")

# Store a memory
character.memory.store({
    "people": {
        "Bob": {
            "interaction": "Met at cafe",
            "timestamp": "2024-03-15T10:30:00"
        }
    }
})

# Retrieve memories
memories = character.memory.get_people_memory("Bob")
```

## State Management

```python
# Update simulation state
simulation.update_state()

# Save current state
simulation.save_state()
```

## Next Steps

1. Explore more complex scenarios in our [Examples](../examples/advanced-scenarios.md)
2. Learn about the [Character System](../core-concepts/character-system.md)
3. Understand [State Management](../core-concepts/state-management.md)
4. Check out [API Reference](../api-reference/models/character.md) for detailed documentation

## Common Operations

### Building Management

```python
# Get all buildings
all_buildings = simulation.building_list.buildings

# Find building by name
cafe = simulation.building_list.get_building_by_name("Coffee Shop")

# Check if position is inside building
is_inside = cafe.cordinate_in_building(x=5, y=5)
```

### Character Management

```python
# Get all characters
all_characters = simulation.character_list.characters

# Get character by name
character = simulation.character_list.get_character_by_name("Alice")
```

### Simulation Control

```python
# Start simulation
simulation.start_service(city_state_msg)

# Update simulation
simulation.update_state()

# Save simulation state
simulation.save_state()
```

## Troubleshooting

If you encounter issues:

1. Check environment variables:
```bash
echo $DEBUG
echo $Milvus
```

2. Verify Redis connection:
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())
```

3. Check simulation status:
```python
print(simulation.started)
print(simulation.total_update_count)
```

For more detailed information, refer to our [Troubleshooting Guide](../examples/troubleshooting.md). 
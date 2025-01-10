# Quick Start Guide

This guide will help you get started with the Degent Civilization quickly. We'll create a simple town with a few characters and run basic interactions.

## Prerequisites

Ensure you have:
- Completed the [installation](installation.md) process
- Set up your OpenAI API key
- Started the required services (Milvus and Redis)

## Basic Usage

### 1. Start the Service

```bash
DEBUG=1 Milvus=1 python main.py
```

### 2. Create a Simple Town

```python
from app.models.town import Town
from app.models.character import Character
from app.models.building import Building

# Initialize a new town
town = Town(name="MyTown")

# Add some buildings
cafe = Building(
    name="Town Cafe",
    description="A cozy cafe in the heart of town",
    building_type="COMMERCIAL"
)
town.add_building(cafe)

# Add characters
alice = Character(
    name="Alice",
    description="A friendly cafe owner",
    occupation="Cafe Owner",
    location=cafe
)
town.add_character(alice)

# Start the simulation
town.start_simulation()
```

### 3. Basic Character Interactions

```python
# Get character state
alice_state = alice.get_current_state()

# Trigger an interaction
response = alice.interact_with("What's the special today?")
print(response)

# Update character's location
new_location = town.get_building("Town Square")
alice.update_location(new_location)
```

## Example Scenarios

### 1. Character Daily Routine

```python
# Set up a daily routine for Alice
alice.set_schedule([
    {"time": "08:00", "action": "open_cafe", "location": "Town Cafe"},
    {"time": "12:00", "action": "lunch_break", "location": "Town Cafe"},
    {"time": "17:00", "action": "close_cafe", "location": "Town Cafe"}
])

# Start the routine
alice.start_daily_routine()
```

### 2. Town Events

```python
# Create a town event
town.create_event(
    name="Summer Festival",
    description="Annual town summer celebration",
    location="Town Square",
    participants=town.get_all_characters()
)

# Start the event
town.start_event("Summer Festival")
```

## Memory System Usage

```python
# Add a memory for a character
alice.add_memory(
    content="Met Bob at the cafe",
    importance=0.8,
    related_entities=["Bob", "Town Cafe"]
)

# Retrieve relevant memories
cafe_memories = alice.retrieve_memories(
    query="What happened at the cafe today?",
    limit=5
)
```

## State Management

```python
# Change character state
alice.change_state("BUSY")

# Check if character can interact
if alice.can_interact():
    response = alice.interact_with("Hello!")
```

## Next Steps

1. Explore more complex scenarios in our [Examples](../examples/advanced-scenarios.md)
2. Learn about the [Character System](../core-concepts/character-system.md)
3. Understand [State Management](../core-concepts/state-management.md)
4. Check out [API Reference](../api-reference/models/character.md) for detailed documentation

## Common Operations

### Character Management

```python
# Get all characters
all_characters = town.get_all_characters()

# Find characters by trait
merchants = town.find_characters_by_occupation("Merchant")

# Get character relationships
alice_relationships = alice.get_relationships()
```

### Building Management

```python
# Get all buildings
all_buildings = town.get_all_buildings()

# Find buildings by type
shops = town.find_buildings_by_type("COMMERCIAL")

# Get building occupants
cafe_occupants = cafe.get_occupants()
```

### Simulation Control

```python
# Pause simulation
town.pause_simulation()

# Resume simulation
town.resume_simulation()

# Get simulation status
status = town.get_simulation_status()
```

## Troubleshooting

If you encounter issues:

1. Check the logs:
```python
town.get_logs()
character.get_logs()
```

2. Verify service status:
```python
town.check_services_status()
```

3. Reset character state:
```python
character.reset_state()
```

For more detailed information, refer to our [Troubleshooting Guide](../examples/troubleshooting.md). 
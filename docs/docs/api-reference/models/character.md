# Character Model API Reference

The Character Model manages individual characters in the simulation, including their properties, memories, relationships, and interactions with the environment.

## Overview

The Character system consists of several key components:
- Character state and attribute management
- Memory system integration
- Relationship handling
- Inventory and resource management
- Character behavior and decision making

## Character Class

The main Character class handles character operations and state management.

### Properties

- `guid`: Unique identifier for the character
- `name`: Character name
- `money`: Character's financial balance
- `location`: Current position (x, y coordinates)
- `inventory`: Dictionary of owned items
- `relationships`: Dictionary of relationships with other characters
- `memory`: Memory system instance for storing experiences
- `state`: Current character state and status

### Memory System

#### Working Memory

```python
def store_memory(self, memory: Dict[str, Any]) -> None
```
Stores recent experiences and current context in working memory.

```python
def retrieve_memory(self, query: str) -> Dict[str, Any]
```
Retrieves relevant memories based on query.

#### Long-term Memory

```python
def store_entity_memory(self, memory: Dict[str, Any]) -> None
```
Stores memories about other characters and entities.

```python
def store_location_memory(self, memory: Dict[str, Any]) -> None
```
Stores memories about locations and buildings.

```python
def store_transaction_memory(self, memory: Dict[str, Any]) -> None
```
Stores memories about economic transactions.

### Relationship Management

```python
def update_relationship(self, character_id: str, impression: float) -> None
```
Updates relationship status with another character.

```python
def get_relationship(self, character_id: str) -> float
```
Retrieves relationship status with specific character.

### Inventory Management

```python
def add_item(self, item: Dict[str, Any]) -> None
```
Adds item to character inventory.

```python
def remove_item(self, item_id: str) -> bool
```
Removes item from inventory.

```python
def check_item(self, item_id: str) -> bool
```
Checks if character has specific item.

### State Management

```python
def update_state(self, new_state: Dict[str, Any]) -> None
```
Updates character's current state.

```python
def get_state(self) -> Dict[str, Any]
```
Retrieves character's current state.

### Movement and Location

```python
def move_to(self, x: int, y: int) -> bool
```
Moves character to new location.

```python
def get_location(self) -> tuple[int, int]
```
Gets character's current location.

## Usage Example

```python
# Create a new character
character = Character(
    id=1,
    name="John Smith",
    money=1000.0,
    location=(5, 5),
    description="A friendly local shopkeeper",
    inventory={
        "keys": {
            "quantity": 1,
            "description": "Shop keys"
        }
    }
)

# Store a memory
character.store_memory({
    "type": "interaction",
    "entity": "Coffee Shop",
    "action": "purchased coffee",
    "timestamp": "2024-03-15T10:30:00"
})

# Update relationship
character.update_relationship(
    character_id="character_2",
    impression=0.8
)

# Move character
character.move_to(10, 15)

# Add item to inventory
character.add_item({
    "id": "coffee_beans",
    "name": "Coffee Beans",
    "quantity": 5
})
```

## Memory Types

### Entity Memory
Stores information about interactions with other characters and entities:
- People memories
- Relationship status
- Interaction history
- Impressions and opinions

### Location Memory
Stores information about places and buildings:
- Building descriptions
- Past experiences
- Important locations
- Associated activities

### Transaction Memory
Stores information about economic activities:
- Purchase history
- Sale records
- Price information
- Transaction outcomes

## State Management

Characters maintain various states that affect their behavior and interactions:
- Emotional state
- Physical condition
- Current activity
- Social status
- Economic status

The state system allows for dynamic character behavior based on their current condition and circumstances. 
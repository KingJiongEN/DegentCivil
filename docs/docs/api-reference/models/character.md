# Character Model

The Character Model represents individual agents within the simulation, encapsulating their attributes, behaviors, and state management.

## Overview

Characters are the primary actors in the simulation, each with their own:
- Personality traits
- Memory and knowledge
- Current state and behaviors
- Relationships with other characters
- Goals and motivations

## Properties

- `id`: Unique identifier for the character
- `name`: Character's full name
- `traits`: Dictionary of personality traits
- `state`: Current state of the character
- `memory`: Reference to the character's memory system
- `relationships`: Dictionary of relationships with other characters

## Methods

### State Management

```python
def update_state(self, new_state: str) -> None
```
Updates the character's current state and triggers relevant state transition handlers.

### Memory Management

```python
def add_memory(self, memory_content: str, importance: float = 0.5) -> None
```
Adds a new memory to the character's memory system with specified importance.

## Usage Example

```python
character = Character(
    name="John Smith",
    traits={
        "openness": 0.7,
        "conscientiousness": 0.8,
        "extraversion": 0.6,
        "agreeableness": 0.75,
        "neuroticism": 0.4
    }
)

character.update_state("working")
character.add_memory("Met Alice at the coffee shop") 
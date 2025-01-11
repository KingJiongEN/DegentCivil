# Custom States

Custom states in DegentCivil allow you to extend the behavior of characters by implementing new state patterns. This guide will walk you through creating and implementing custom states.

## Overview

States represent different behaviors and activities that characters can engage in. Each state defines:

- Entry conditions
- Exit conditions
- State-specific behaviors
- Transitions to other states

## Creating a Custom State

### 1. Basic Structure

Create a new class that inherits from the base state class:

```python
from app.service.character_state.base_state import BaseState

class MyCustomState(BaseState):
    def __init__(self):
        super().__init__()
        self.state_name = "my_custom_state"
```

### 2. Required Methods

Implement these essential methods:

```python
def enter(self, character):
    """Called when character enters this state"""
    pass

def execute(self, character):
    """Main state logic, called each tick"""
    pass

def exit(self, character):
    """Called when character exits this state"""
    pass

def should_transition(self, character):
    """Define conditions for transitioning to other states"""
    return False, None
```

## State Registration

Register your custom state in the state manager:

```python
from app.service.character_state.state_manager import StateManager

StateManager.register_state("my_custom_state", MyCustomState)
```

## Example Implementation

Here's a complete example of a custom "Shopping" state:

```python
class ShoppingState(BaseState):
    def __init__(self):
        super().__init__()
        self.state_name = "shopping"
        self.shopping_duration = 30  # minutes
        self.start_time = None

    def enter(self, character):
        self.start_time = character.current_time
        character.memory.add_event(f"Started shopping at {character.current_location}")

    def execute(self, character):
        # Shopping logic
        if character.inventory.has_space():
            character.inventory.add_items(self.get_shopping_items())
        
        # Update character's needs
        character.energy -= 0.1
        character.money -= 5

    def exit(self, character):
        character.memory.add_event("Finished shopping")

    def should_transition(self, character):
        # Transition conditions
        if character.current_time - self.start_time >= self.shopping_duration:
            return True, "idle"
        if character.energy < 20:
            return True, "resting"
        return False, None
```

## Best Practices

1. **State Naming**: Use clear, descriptive names for your states
2. **Memory Management**: Always update character memory with significant events
3. **Resource Management**: Handle character resources (energy, money, etc.) carefully
4. **Transition Logic**: Keep transition conditions clear and well-defined
5. **Error Handling**: Implement proper error handling for state-specific operations

## Integration with Other Systems

Custom states can interact with various systems:

- Memory System
- Building System
- Inventory System
- Social System

## Testing Custom States

Create unit tests for your custom states:

```python
def test_shopping_state():
    character = Character()
    state = ShoppingState()
    
    # Test enter
    state.enter(character)
    assert character.memory.has_event("Started shopping")
    
    # Test execute
    state.execute(character)
    assert character.inventory.has_items()
    
    # Test transitions
    should_transition, next_state = state.should_transition(character)
    assert should_transition == False
```

## Common Pitfalls

1. Forgetting to register states
2. Not handling resource depletion
3. Infinite state loops
4. Missing error handling
5. Poor transition logic

## Advanced Features

### State Priorities

```python
def get_priority(self):
    return 5  # Higher number = higher priority
```

### State Dependencies

```python
def check_dependencies(self, character):
    return character.has_money and character.has_inventory_space
```

### State Interruption

```python
def can_be_interrupted(self):
    return True  # Allow state interruption
```

## Performance Considerations

- Keep state logic efficient
- Minimize memory operations
- Cache frequently accessed data
- Use appropriate data structures

## Debugging Tips

1. Use logging for state transitions
2. Monitor resource usage
3. Track state duration
4. Validate state conditions
5. Check memory leaks 
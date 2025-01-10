# Character System

The Character System is one of the core components of the Degent Civilization. It manages the creation, behavior, and interactions of all characters within the town simulation.

## Character Model

```python
class Character:
    def __init__(self, name, description, occupation, location):
        self.name = name
        self.description = description
        self.occupation = occupation
        self.location = location
        self.state = None
        self.memories = []
        self.relationships = {}
        self.schedule = []
```

## Components

### 1. Basic Attributes

- **Name**: Unique identifier for the character
- **Description**: Physical and personality traits
- **Occupation**: Character's role in the town
- **Location**: Current building or place
- **State**: Current activity or status
- **Schedule**: Daily routine and planned activities

### 2. Memory System

Characters maintain memories of:
- Interactions with other characters
- Events they've participated in
- Experiences at locations
- Important information learned
- Emotional responses to situations

```python
# Adding a memory
character.add_memory(
    content="Had a great conversation with Sarah at the cafe",
    importance=0.7,
    related_entities=["Sarah", "Cafe"],
    emotion="happy"
)

# Retrieving memories
relevant_memories = character.retrieve_memories(
    query="What do I know about Sarah?",
    limit=5
)
```

### 3. Relationship System

Characters maintain relationships with:
- Other characters
- Buildings they frequently visit
- Organizations they belong to

```python
# Managing relationships
character.update_relationship(
    target="Sarah",
    relationship_type="friend",
    strength=0.8
)

# Checking relationships
friends = character.get_relationships_by_type("friend")
```

### 4. State Management

Characters can be in various states:
- IDLE: Default state
- BUSY: Engaged in an activity
- INTERACTING: Talking with others
- WORKING: Performing job duties
- RESTING: Taking a break

```python
# State transitions
character.change_state("BUSY")
if character.can_interact():
    character.change_state("INTERACTING")
```

## Behavior System

### 1. Decision Making

Characters make decisions based on:
- Current state
- Personal goals
- Memories
- Relationships
- Environmental factors

```python
decision = character.make_decision(
    context="Should I visit the cafe?",
    options=["go_to_cafe", "stay_here"],
    factors=["time", "energy", "relationships"]
)
```

### 2. Interaction System

Characters can interact through:
- Conversations
- Activities
- Trade
- Relationships
- Events

```python
# Basic interaction
response = character.interact_with(
    target="Sarah",
    action="greet",
    context="morning meeting"
)

# Complex interaction
interaction = character.start_complex_interaction(
    target="Sarah",
    interaction_type="business_meeting",
    duration=30,
    location="Office"
)
```

### 3. Schedule Management

Characters follow daily routines:
- Work schedules
- Break times
- Social activities
- Personal tasks

```python
# Setting up a schedule
character.set_schedule([
    {
        "time": "08:00",
        "action": "start_work",
        "location": "Office",
        "duration": 240
    },
    {
        "time": "12:00",
        "action": "lunch_break",
        "location": "Cafe",
        "duration": 60
    }
])

# Checking schedule
next_activity = character.get_next_activity()
```

## Integration with Other Systems

### 1. Building Integration

Characters interact with buildings:
- Entering/leaving
- Using facilities
- Working
- Living

```python
# Moving to a new location
character.move_to(building)

# Interacting with building
character.use_building_facility(
    building="Cafe",
    facility="Coffee Machine"
)
```

### 2. Event Integration

Characters participate in events:
- Town festivals
- Work meetings
- Social gatherings
- Personal events

```python
# Joining an event
character.join_event(
    event_name="Summer Festival",
    role="participant"
)

# Creating an event
character.create_event(
    name="Birthday Party",
    location="Home",
    invited_characters=["Sarah", "John"]
)
```

### 3. Memory Integration

Characters use memories for:
- Decision making
- Relationship building
- Conversation context
- Learning

```python
# Using memories in interaction
relevant_context = character.get_memory_context(
    interaction_type="conversation",
    target="Sarah"
)

# Learning from experiences
character.learn_from_interaction(
    interaction_result="positive",
    target="Sarah",
    context="business deal"
)
```

## Advanced Features

### 1. Personality Traits

Characters have unique personalities:
- Extroversion/Introversion
- Agreeableness
- Conscientiousness
- Emotional stability
- Openness

### 2. Emotional System

Characters experience emotions:
- Based on interactions
- Affecting decisions
- Influencing relationships
- Changing over time

### 3. Learning System

Characters can learn and adapt:
- New skills
- Better decisions
- Relationship preferences
- Behavioral patterns

## API Reference

For detailed API documentation, see:
- [Character Model API](../api-reference/models/character.md)
- [Character State API](../api-reference/services/character-state.md)
- [Memory System API](../api-reference/models/memory.md)

## Examples

Check out our [Examples](../examples/basic-usage.md) section for:
- Character creation
- Interaction scenarios
- Schedule management
- Complex behaviors 
# Emotion API Reference

The Emotion module manages character emotions and emotional state transitions in the simulation.

## Overview

The Emotion system handles:
- Multiple emotion categories
- Emotion intensity tracking
- Emotional state updates
- Event-based emotion changes
- Emotional memory

## Emotion Class

### Constants

```python
emotional_options = [
    "joy", "trust", "fear", "surprise", 
    "sadness", "disgust", "anger", "anticipation"
]

positive_emotions = ["joy", "trust", "anticipation", "surprise"]
negative_emotions = ["fear", "surprise", "sadness", "disgust", "anger"]
```

### Properties

- `emotion`: Dictionary mapping emotion types to intensity values (0-10)
- `update_alpha`: Weight for new emotion updates (default: 0.7)
- `passive_decay_alpha`: Rate of passive emotion decay (default: 0.01)
- `impressive_event`: Dictionary storing significant emotional events

### Methods

#### Emotion Management

```python
def update(self, emotions: list[dict] = None) -> None
```
Updates emotional states based on new events or passive decay.

Example input:
```python
emotions = [
    {
        "emotion": "joy",
        "change": 4,
        "explanation": "I feel much happy because I got a gift from Jay."
    },
    {
        "emotion": "trust",
        "change": 2,
        "explanation": "I trust Jay, he is a kind person."
    }
]
```

```python
def update_single_emotion(self, emotion: str, intensity_change: float, event: str = None) -> None
```
Updates a single emotion's intensity and records the triggering event.

#### State Queries

```python
@property
def impression(self) -> Dict[str, float]
```
Returns current emotional state values.

```python
@property
def extreme_emotion(self) -> dict
```
Returns the most intense emotion and its value.

```python
@property
def most_impressive_event(self) -> tuple[str, str]
```
Returns the most significant emotional event and its associated emotion.

### Initialization

```python
def random_init_emotions(self) -> None
```
Initializes emotions with balanced random values:
- 10% chance for high intensity (6-10)
- 80% chance for low intensity (0-4)
- 10% chance for medium intensity (4-6)

## Usage Example

```python
# Create new emotion instance
emotion = Emotion(
    emotion={
        "joy": 5.0,
        "trust": 3.0
    },
    update_alpha=0.7,
    decay_alpha=0.01
)

# Update emotions based on events
emotion.update([
    {
        "emotion": "joy",
        "change": 2,
        "explanation": "Had a great conversation"
    }
])

# Get current emotional state
current_state = emotion.impression
dominant_emotion = emotion.extreme_emotion
```

## Integration Points

### Character System
- Emotional state influences character decisions
- Events trigger emotional updates
- Emotional memory affects relationships

### Memory System
- Significant emotional events are stored
- Emotional context for memories
- Event-emotion associations

### Behavior System
- Emotions influence action choices
- Emotional thresholds trigger behaviors
- Mood affects social interactions 
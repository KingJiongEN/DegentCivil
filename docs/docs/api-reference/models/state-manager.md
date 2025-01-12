# State Manager API Reference

The State Manager system handles internal character states and emotions, managing numerical values and tracking significant events that affect character behavior.

## Overview

The State Manager consists of:
- State value management (0-10 scale)
- State change tracking
- Event significance tracking
- Automatic state decay

## StateManager Class

The StateManager class handles internal state tracking and modifications.

### Properties

- `states`: Dictionary mapping state types to numerical values (0-10)
- `update_rate`: Rate at which states change (default 0.7)
- `decay_rate`: Rate of automatic state decay (default 0.01)
- `significant_events`: Record of events causing major state changes

### Class Variables

```python
state_options = ["positive_a", "positive_b", "negative_a", "neutral_a", 
                 "negative_b", "negative_c", "negative_d", "positive_c"]

positive_states = ["positive_a", "positive_b", "positive_c", "neutral_a"]
negative_states = ["negative_a", "neutral_a", "negative_b", "negative_c", "negative_d"]
```

### Methods

#### State Management

```python
def initialize_states(self) -> None
```
Initializes states with balanced random values.

```python
def update_states(self, state_changes: list[dict] = None) -> None
```
Updates states based on provided changes or applies decay if None.

```python
def update_single_state(self, state_type: str, intensity_delta: float, trigger: str = None) -> None
```
Updates a single state value with validation.

#### State Decay

```python
def apply_decay(self, state_type=None, custom_rate=None) -> None
```
Applies natural decay to states over time.

#### Event Tracking

```python
def record_significant_event(self, state_type: str, state_delta: float, trigger: str) -> None
```
Records events that cause significant state changes.

#### State Access

```python
@property
def current_states(self) -> Dict[str, float]
```
Returns dictionary of all current state values.

```python
@property
def most_significant_event(self) -> tuple[str, str]
```
Returns the most impactful event and affected state.

```python
@property
def dominant_state(self) -> dict
```
Returns the highest-value state and its value.

## Usage Example

```python
# Initialize state manager
state_manager = StateManager(
    initial_state={"positive_a": 7.0, "negative_a": 3.0},
    update_rate=0.7,
    decay_rate=0.01
)

# Update states
state_changes = [{
    'state': 'positive_a',
    'change': 2.0,
    'reason': 'Received good news'
}]
state_manager.update_states(state_changes)

# Check current states
current_states = state_manager.current_states
dominant = state_manager.dominant_state

# Apply decay
state_manager.apply_decay()

# Check significant events
trigger, state = state_manager.most_significant_event
```

## Implementation Notes

### State Values
- All states are constrained between 0 and 10
- Values are rounded to 2 decimal places
- Initial values are randomly distributed with specific probabilities:
  - 10% chance: 6-10 range
  - 80% chance: 0-4 range
  - 10% chance: 4-6 range

### State Changes
- Intensity changes must be between -5 and 5
- Changes include trigger reasons for tracking
- Significant events are tracked separately
- State types must be from predefined options

### Decay System
- Automatic decay applies to all states
- Higher states (>7) decay faster
- Lower states may increase slightly
- Custom decay rates can be specified
- Decay maintains value bounds (0-10)

## Value Constraints

### State Values
- Minimum: 0.0
- Maximum: 10.0
- Precision: 2 decimal places

### Change Intensity
- Minimum: -5.0
- Maximum: 5.0
- Validation: Required for all changes 
# Preference Model API Reference

The Preference Model manages character preferences across different categories, providing a system for tracking and evolving character tastes and preferences over time.

## Overview

The Preference Model consists of:
- Category-based preference scoring
- Dynamic preference management
- Preference evolution mechanics
- Top preference tracking

## PreferenceModel Class

The PreferenceModel class handles preference scoring and management across multiple categories.

### Properties

- `categories`: List of available preference categories (style_a through style_l)
- `preferences`: Dictionary mapping categories to preference scores (0-10)

### Class Variables

```python
categories = [
    "style_a", "style_b", "style_c", "style_d", 
    "style_e", "style_f", "style_g", "style_h", 
    "style_i", "style_j", "style_k", "style_l"
]
```

### Methods

#### Preference Management

```python
def __init__(self, preferences: Dict[str, float]={}) -> None
```
Initializes preference model with optional initial preferences. Default values are randomly generated between 0 and 10.

```python
def update_preferences(self) -> None
```
Updates preference values with small random adjustments (-0.2 to +0.2), maintaining values between 0 and 10.

#### Preference Access

```python
@property
def top_preferences(self, count=1) -> str
```
Returns comma-separated string of top N preferred categories.

```python
@property
def preference_scores(self) -> Dict[str, float]
```
Returns dictionary of all current preference scores.

## Usage Example

```python
# Create preference model with default random values
preferences = PreferenceModel()

# Create with specific initial preferences
initial_prefs = {
    "style_a": 8.5,
    "style_b": 3.2,
    "style_c": 6.7
}
preferences = PreferenceModel(initial_prefs)

# Get top preference
top_style = preferences.top_preferences

# Get all preference scores
all_scores = preferences.preference_scores

# Update preferences
preferences.update_preferences()
```

## Implementation Notes

- Preference scores are constrained between 0 and 10
- Unspecified preferences are initialized with random values
- Preference updates use small random adjustments
- Top preferences can be retrieved individually or in groups
- All preference categories are initialized even if not specified
- Invalid preference values will raise an assertion error

## Value Constraints

### Preference Scores
- Minimum value: 0.0
- Maximum value: 10.0
- Type: float

### Update Adjustments
- Minimum adjustment: -0.2
- Maximum adjustment: +0.2
- Frequency: Per update call 
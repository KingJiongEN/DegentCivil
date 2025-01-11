# Prompt Engineering

This guide covers advanced techniques for crafting effective prompts in DegentCivil to achieve more realistic and engaging character behaviors.

## Core Principles

1. **Clarity**: Write clear, unambiguous prompts
2. **Context**: Provide relevant background information
3. **Consistency**: Maintain consistent character personalities
4. **Constraints**: Set appropriate behavioral boundaries
5. **Creativity**: Allow room for dynamic responses

## Prompt Structure

### Basic Template

```yaml
Character Context:
  - Name: {character_name}
  - Role: {character_role}
  - Personality: {personality_traits}
  - Current State: {emotional_state}

Situation Context:
  - Location: {current_location}
  - Time: {current_time}
  - Present Characters: {other_characters}
  - Recent Events: {recent_memory}

Task:
  - Objective: {specific_task}
  - Constraints: {behavioral_limits}
  - Expected Output: {response_format}
```

## Advanced Techniques

### 1. Memory Integration

Include relevant memory snippets:

```yaml
Recent Memories:
  - Personal: {character_experiences}
  - Social: {interactions_with_others}
  - Environmental: {location_observations}
```

### 2. Emotional Context

Define emotional states and triggers:

```yaml
Emotional State:
  - Current Mood: {mood}
  - Stress Level: {stress}
  - Relationship Status: {relationships}
```

### 3. Decision Making

Guide character decision processes:

```yaml
Decision Framework:
  - Options: {available_choices}
  - Priorities: {character_values}
  - Consequences: {potential_outcomes}
```

## Best Practices

### 1. Character Consistency

- Maintain consistent personality traits
- Reference past decisions and experiences
- Use character-specific vocabulary
- Consider character development arc

### 2. Environmental Awareness

- Include relevant location details
- Consider time of day effects
- Account for weather conditions
- Reference nearby objects/items

### 3. Social Dynamics

- Define relationship contexts
- Include social status considerations
- Account for group dynamics
- Reference social norms

## Common Patterns

### 1. Dialogue Generation

```yaml
Dialogue Context:
  Speaker: {character_name}
  Listener: {target_character}
  Relationship: {relationship_type}
  Topic: {conversation_subject}
  Tone: {emotional_tone}
```

### 2. Decision Making

```yaml
Decision Context:
  Situation: {current_problem}
  Options: {available_choices}
  Constraints: {limitations}
  Values: {character_priorities}
```

### 3. Emotional Responses

```yaml
Emotion Trigger:
  Event: {triggering_event}
  Impact: {personal_significance}
  History: {related_experiences}
  Response Range: {acceptable_reactions}
```

## Optimization Techniques

### 1. Token Efficiency

- Use concise language
- Remove redundant information
- Prioritize crucial context
- Structure information hierarchically

### 2. Response Shaping

- Set clear output formats
- Define response boundaries
- Include validation criteria
- Specify detail level

### 3. Error Prevention

- Include sanity checks
- Define fallback behaviors
- Set reasonable limits
- Validate outputs

## Testing and Iteration

### 1. Prompt Testing

```python
def test_prompt_effectiveness():
    test_cases = [
        {"input": base_prompt, "expected": "realistic_response"},
        {"input": modified_prompt, "expected": "improved_response"}
    ]
    
    for case in test_cases:
        response = generate_response(case["input"])
        validate_response(response, case["expected"])
```

### 2. Quality Metrics

- Response relevance
- Character consistency
- Behavioral realism
- Output formatting
- Performance impact

## Troubleshooting

### Common Issues

1. **Inconsistent Responses**
   - Review character context
   - Check for conflicting instructions
   - Validate emotional states

2. **Poor Performance**
   - Optimize prompt length
   - Remove unnecessary context
   - Streamline instructions

3. **Unrealistic Behavior**
   - Enhance situational context
   - Adjust behavioral constraints
   - Review social dynamics

## Advanced Examples

### Complex Social Interaction

```yaml
Interaction Context:
  Primary Character:
    Name: John Smith
    Role: Merchant
    Goals: Make sales, maintain relationships
    Current State: Busy with customers

  Social Environment:
    Location: Market Square
    Time: Peak business hours
    Present Characters:
      - Regular customers
      - Competing merchants
      - Town guards

  Behavioral Guidelines:
    - Maintain professional demeanor
    - Balance multiple customer interactions
    - Respond to competition appropriately
    - Follow market regulations
```

### Emergency Response

```yaml
Emergency Context:
  Situation: Building fire
  Character Role: Town Guard
  Primary Objectives:
    - Ensure civilian safety
    - Coordinate with other guards
    - Maintain order
  
  Response Parameters:
    - Urgency level: High
    - Authority level: Official
    - Communication style: Clear, commanding
    - Action constraints: Safety protocols
```

## Performance Optimization

1. **Caching Strategies**
   - Cache common prompt templates
   - Store frequently used character contexts
   - Reuse environmental descriptions

2. **Batch Processing**
   - Group similar prompt types
   - Process related character interactions
   - Combine environmental updates

3. **Resource Management**
   - Monitor token usage
   - Track response times
   - Optimize context length 
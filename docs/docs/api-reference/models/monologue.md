# Inner Monologue API Reference

The Inner Monologue system manages characters' internal thoughts and emotional expressions, providing a mechanism for characters to process their perceptions, plans, memories, and emotions.

## Overview

The Inner Monologue system consists of two main components:
- MonologuePrompt for generating prompts for internal dialogue
- InnerMonologue for managing and processing character's internal thoughts

## MonologuePrompt Class

The MonologuePrompt class handles the generation of prompts for character's internal dialogue.

### Properties

- `character`: Reference to the associated character
- `prompt_type`: Type of prompt (PromptType.INNER_MONOLOGUE)
- `PROMPT`: Template for generating monologue prompts

### Methods

```python
def create_prompt(self, **kwargs) -> str
```
Creates a formatted prompt using character attributes and provided parameters.

```python
def format_attr(self, **kwargs) -> str
```
Formats the prompt template by replacing placeholders with actual values.

### Default Prompt Structure

The prompt includes:
- Character name and bio
- World understanding from memory
- Internal status
- Current plan and step
- Emotional state
- Criteria for monologue generation

## InnerMonologue Class

The InnerMonologue class manages a character's internal dialogue system.

### Properties

- `character`: Reference to the associated character
- `content`: Dictionary storing current monologue content
- `prompt`: Associated MonologuePrompt instance

### Methods

#### Content Management

```python
def sample_monologue(self, size=2) -> list
```
Returns a random sample of monologue entries.

```python
def set_monologue(self, content: dict) -> None
```
Updates monologue content and saves the response.

#### LLM Integration

```python
def build_prompt(self) -> str
```
Constructs prompt for LLM using character's emotional state.

```python
def call_llm(self) -> None
```
Asynchronously generates new monologue content using LLM.

#### State Management

```python
@property
def inner_monologue(self) -> dict
```
Returns current monologue content.

```python
@property
def emoji(self) -> str
```
Returns associated emoji for current emotional state.

## Message Format

### Example Monologue Response

```json
{
    "monologue_understanding": "Jack is busy, I should not bother him.",
    "monologue_status": "I'm feeling tired and hungry.",
    "monologue_plan": "I should go to the library to find the book.",
    "monologue_emotion": "Feeling so sad, god damn.",
    "emoji": "😟"
}
```

## Usage Example

```python
# Create inner monologue for a character
monologue = InnerMonologue(character)

# Generate new monologue
monologue.call_llm()

# Access monologue content
current_thoughts = monologue.inner_monologue
emotional_state = monologue.emoji

# Sample random thoughts
sample_thoughts = monologue.sample_monologue(size=2)
```

## Implementation Notes

- Monologues are limited to 20 words per category
- Uses asynchronous LLM calls for content generation
- Integrates with character's emotion and memory systems
- Maintains consistent first-person narration style
- Automatically saves prompts and responses for record keeping 
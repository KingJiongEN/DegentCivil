# Steps to Add a New Character State

## Basic Concepts

Each state contains three main lifecycle methods:

1. `enter_state`: Executed when entering the state
2. `update_state`: Executed when updating the state
3. `exit_state`: Executed when exiting the state

### State Lifecycle Example

```python
from app.service.character_state.base_state import BaseState
from app.constants.prompt_type import PromptType
from app.constants.character_state import CharacterState

class ExampleState(BaseState):
    def __init__(self, character, character_list, building_list, on_change_state):
        # Configure basic state properties
        super().__init__(
            character=character,
            main_prompt=PromptType.EXAMPLE,  # Define the main prompt type used by the state
            character_list=character_list,
            building_list=building_list,
            followed_states=[CharacterState.IDLE],  # Define subsequent states that can be transitioned to
            on_change_state=on_change_state,
            state_name=CharacterState.EXAMPLE  # State name
        )

    def enter_state(self, **kwargs):
        """Operations executed when entering the state"""
        # Call parent class enter_state method
        super().enter_state(**kwargs)
        # Add specific entry logic here
        print(f"{self.character.name} entered example state")

    def update_state(self, msg, date, **kwargs):
        """Operations executed when updating the state"""
        # Call parent class update_state method
        return_dict = super().update_state(msg, date, **kwargs)
        # Add specific update logic here
        return return_dict

    def exit_state(self, **kwargs):
        """Operations executed when exiting the state"""
        # Call parent class exit_state method
        success, msg = super().exit_state(**kwargs)
        # Add specific exit logic here
        return success, msg
```

### Adding a New Prompt

Each state typically needs a corresponding Prompt class to handle LLM interactions. Here's an example of creating a new Prompt:
BasePrompt.recordable_key will be automatically stored into working memory, a dict storing values for further state processing. 
```python
from app.llm.prompt.base_prompt import BasePrompt

class ExamplePrompt(BasePrompt):
    # Define prompt template
    PROMPT = '''
    Current Character: {character_name}
    Current Location: {location}
    
    Please make a decision based on the following information:
    {context}
    
    Please return your decision in JSON format:
    {
        "decision": "your decision",
        "reason": "reason for decision"
    }
    '''
    
    def __init__(self, prompt_type, state):
        super().__init__(prompt_type, state)
        # Set keys to be recorded in working memory
        self.recordable_key = ["decision", "reason"]
        
    def create_prompt(self):
        """Create complete prompt"""
        # Add specific prompt processing logic here
        return self.format_attr(
            character_name=self.character.name,
            location=self.character.in_building_name,
            context="Context information goes here"
        )
```

## Complete Steps

1. **Define New Prompt Type**
```python
# app/constants/prompt_type.py
class PromptType(Enum):
    # ... other prompt types ...
    EXAMPLE = auto()
```

2. **Create New State Type**
```python
# app/constants/character_state.py
class CharacterState(Enum):
    # ... other states ...
    EXAMPLE = auto()
```

3. **Register New State**
```python
# app/service/character_state/__init__.py
from .example_state import ExampleState
```

```python
# app/service/character_state/state_factory.py
from .example_state import ExampleState

def get_initialized_states(character, change_state_callback):
    return {
        # ... other states ...
        CharacterState.EXAMPLE: ExampleState(
            character,
            character_list,
            building_list,
            change_state_callback
        ),
    }
```

4. **Register Prompt Class**
```python
# app/service/character_state/__init__.py
from .example_prompt import ExamplePrompt

PromptName2Registered = {
    # ... other prompts ...
    PromptType.EXAMPLE: ExamplePrompt,
}
```

## Important Notes

1. Ensure new states include appropriate `followed_states`
2. Set `recordable_key` when creating Prompt class
3. State transition logic should be implemented in `update_state`
4. Use `self.turn_on_states()` to trigger state transitions



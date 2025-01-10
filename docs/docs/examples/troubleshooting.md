# Debugging State and State Transitions

## Overview

When developing new states or troubleshooting state transitions, you can create a debug configuration YAML file to test specific scenarios with customized working memories.

## Example: Testing ChatingState

Let's examine how to debug the ChatingState class:

```python
@register(name='CHATING', type="state")
class ChatingState(BaseState):
    def __init__(self, character: Character, 
                 character_list: CharacterList, 
                 building_list: BuildingList,  
                 on_change_state, 
                 followed_states=[CharacterState.SUM],
                 main_prompt = PromptType.CHATING,
                 state_name = CharacterState.CHATING,
                 arbitrary_wm=dict()
    )    
```

## Creating a Debug Configuration

You can customize state initialization arguments and working memory using a debug configuration file:

```yaml
# config/debug_chat.yaml
States:
  Jack Brown:  
    ACT:
        followed_states: 
            - CHATING 
    CHATING: 
        arbitrary_wm: 
            act_obj: Emma Smith
            init_conversation: Hi, how are you?  
  Emma Smith:
    IDLE: {}
```

### Configuration Components

1. **Character Configuration**: Define states for each character under their name
2. **State Parameters**: Customize state-specific settings
   - `followed_states`: Define valid state transitions
   - `arbitrary_wm`: Set initial working memory values

### Running the Debug Configuration

Execute your simulation with the debug configuration:

```zsh
DEBUG=1 python main.py configs/debug_chat.yaml
```

## Best Practices

1. **Working Memory Testing**
   - Use `arbitrary_wm` to simulate different memory states
   - Test edge cases and boundary conditions
   - Verify memory persistence across state transitions

2. **State Transitions**
   - Configure `followed_states` to test transition paths
   - Verify state entry and exit conditions

3. **Character Interactions**
   - Set up multiple characters to test interactions
   - Verify message passing between states
   - Test concurrent state transitions

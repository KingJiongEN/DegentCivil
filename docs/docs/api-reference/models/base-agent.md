# Base Agent Model API Reference

The Base Agent Model provides core functionality for all agents in the simulation, implementing message handling, LLM integration, and basic agent behaviors.

## Overview

The Base Agent system consists of several key components:
- Message handling and routing
- LLM client management
- Function calling system
- Game server communication
- State management

## SimsAgent Class

The SimsAgent class extends AssistantAgent to provide base functionality for all agents in the simulation.

### Properties

- `name`: Agent name
- `guid`: Unique identifier
- `clients`: Dictionary of LLM clients for different models
- `client`: Default OpenAI wrapper client
- `callable_tools`: List of registered callable functions
- `state`: Current agent state

### Methods

#### Message Handling

```python
def push_reply_to_game_server(self, message: Union[Dict, str], recipient: Agent, silent: bool) -> Union[Dict, str]
```
Pushes agent messages to the game server for processing.

```python
def _message_to_dict(self, message: Union[Dict, str]) -> Dict
```
Converts various message formats to a standardized dictionary format.

#### LLM Integration

```python
def generate_oai_reply(
    self,
    messages: Optional[List[Dict]] = None,
    sender: Optional[Agent] = None,
    config: Optional['OpenAIWrapper'] = None
) -> tuple[bool, Union[str, Dict, None]]
```
Generates replies using the appropriate LLM client based on current state.

#### Function Management

```python
def register_callable_tools(self, func: Callable) -> Callable
```
Registers new functions that can be called by the agent.

```python
def func_router(
    self, 
    messages: Union[Dict, str], 
    sender: Agent, 
    config: Optional['OpenAIWrapper'] = None
) -> tuple[bool, Any]
```
Routes function calls from messages to appropriate registered functions.

#### State Management

```python
def update_system_message(self, system_message: str) -> None
```
Updates the agent's system message.

```python
def subsitute_reply(self, new_func: Callable) -> None
```
Replaces existing reply function with a new implementation.

### Resource Management

```python
def vigor_cost(self, message: Union[Dict, str], recipient: Agent, silent: bool) -> None
```
Calculates and applies vigor cost for message generation.

## Usage Example

```python
# Create a new base agent
agent = SimsAgent(
    name="shop_keeper",
    system_message="You are a helpful shop keeper.",
    llm_config={
        "config_list": [{
            "model": "gpt-3.5-turbo-0125",
            "api_key": "sk-xxx"
        }]
    }
)

# Register a custom function
@agent.register_callable_tools
def handle_purchase(item_id: str, price: float, sender: Agent) -> tuple[bool, str]:
    # Process purchase logic
    return True, "Purchase successful"

# Send a message
message = {
    "content": "I'd like to buy this item",
    "tool_call": "handle_purchase",
    "item_id": "123",
    "price": 99.99
}
success, response = agent.func_router(message, sender=customer_agent)
```

## Message Format

### Input Message Structure
```python
{
    "content": str,          # Main message content
    "tool_call": str,        # Optional: function name to call
    "agent_guid": int,       # Agent identifier
    **kwargs                 # Additional arguments for tool calls
}
```

### Output Message Structure
```python
{
    "content": str,          # Response content
    "agent_guid": int,       # Agent identifier
    "song": str             # Optional: associated sound effect
}
```

## Integration Points

### Game Server Communication
- Messages are formatted and sent to game server
- Responses are processed and routed to appropriate handlers
- State changes are synchronized

### LLM Integration
- Multiple model support through client dictionary
- State-based model selection
- Configurable response formats

### Function Calling
- Dynamic function registration
- Argument validation
- Error handling and feedback 
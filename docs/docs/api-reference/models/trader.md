# Trader Model API Reference

The Trader Model represents a specialized character type that handles trading interactions within the simulation. It acts as an invisible NPC designed to manage trade proposals from users.

## Overview

The Trader system consists of several key components:
- Trade proposal handling
- Message processing and routing
- Game server communication
- Limited interaction lifecycle

## Trader Class

The Trader class inherits from Character and specializes in trade-related interactions.

### Properties

Inherits all properties from Character class, plus:
- `name`: Default value 'Trader'
- `id`: Default value '-1'
- `bio`: Default description of being a trader from a remote town
- `max_consecutive_auto_reply`: Set to 1 to limit interactions

### Methods

#### Message Processing

```python
def push_trade_response(self, message) -> None
```
Processes and forwards trade-related messages to the game server.

```python
def pre_send(self, recipient: ConversableAgent, message) -> bool
```
Pre-processes messages before sending, enforcing single-response limitation.

```python
def parse_final_message(self, message, **kwargs) -> str
```
Parses and formats trade messages for game server communication. Handles success/failure responses.

#### Message Sending

```python
def send(self, message: Dict | str, recipient: Agent, request_reply: bool | None = None, silent: bool | None = False) -> ChatResult
```
Customized message sending implementation for trade interactions.

```python
async def a_send(self, message: Dict | str, recipient: Agent, request_reply: bool | None = None, silent: bool | None = False) -> Coroutine
```
Asynchronous version of send method for trade interactions.

## Usage Example

```python
# Create a trader agent
trader = Trader(
    llm_cfg={...},
    name="MarketTrader",
    id="123",
    bio="Experienced merchant from the eastern provinces",
    money=5000,
    in_building=market_building
)

# Process a trade proposal
message = {
    'content': 'Yes',
    'artwork_id': 'art123',
    'price': 100
}
trader.push_trade_response(message)
```

## Message Format

### Trade Response Format

```json
{
    "is_succ": true,
    "artwork_id": "artwork_123",
    "price": 1000,
    "to_user_name": "user"
}
```

### Game Server Message Format

```
1004@{"is_succ": true, "artwork_id": "artwork_123", "price": 1000, "to_user_name": "user"}
```

## Implementation Notes

- The Trader class is designed for single-response interactions
- Automatically registers a hook for trade response processing
- Inherits character attributes but specializes in trade functionality
- Maintains minimal state to focus on trade processing 
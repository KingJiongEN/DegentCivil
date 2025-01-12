# Transaction API Reference

The Transaction system manages trading interactions between characters, tracking trade records and handling resource exchanges within the simulation.

## Overview

The system consists of two main components:
- Trade record management and persistence
- Trade execution and validation

## TradeRecord Class

The TradeRecord class maintains detailed information about individual trades.

### Properties

- `buyer`: Reference to purchasing Character
- `seller`: Reference to selling Character
- `resource_id`: Unique identifier for traded resource
- `remaining_budget`: Buyer's remaining funds after trade
- `like_score`: Buyer's preference score for the resource
- `emotion`: Emotional state during trade
- `timestamp`: Time of transaction
- `market_price`: Base market value
- `expected_price`: Anticipated transaction price
- `final_price`: Actual transaction price

### Methods

```python
def __str__(self) -> str
```
Returns formatted string representation of trade record.

```python
def __eq__(self, other: TradeRecord) -> bool
```
Compares trade records for equality based on seller, resource, and timestamp.

#### Static Methods

```python
@staticmethod
def to_str(trade_record: TradeRecord) -> str
```
Converts trade record to string format.

```python
@staticmethod
def from_str(trade_record_str: str, character_list: CharacterList) -> TradeRecord
```
Creates TradeRecord instance from string representation.

## Trade Class

The Trade class handles trade execution and validation.

### Methods

```python
@staticmethod
def make_trade(
    buyer: Character, 
    seller: Character, 
    resource_id: str, 
    price: float, 
    resource_type: str = "drawings", 
    **kwargs
) -> Tuple[bool, TradeRecord]
```
Executes trade between characters and generates trade record.

#### Parameters

- `buyer`: Character initiating purchase
- `seller`: Character selling resource
- `resource_id`: ID of resource being traded
- `price`: Agreed transaction price
- `resource_type`: Type of resource (default: "drawings")
- `**kwargs`: Additional trade details for record

#### Returns

- Tuple containing success status and TradeRecord (if successful)

## Usage Example

```python
# Execute a trade
success, record = Trade.make_trade(
    buyer=buyer_character,
    seller=seller_character,
    resource_id="artwork_123",
    price=100.0,
    remaining_budget=900.0,
    like_score=8.5,
    emotion="excited",
    market_price=90.0,
    expected_price=95.0,
    final_price=100.0
)

# Access trade record
if success:
    print(f"Trade completed: {record}")
    print(f"Buyer: {record.buyer.name}")
    print(f"Final price: {record.final_price}")

# Convert record to string
record_str = TradeRecord.to_str(record)

# Reconstruct record from string
reconstructed_record = TradeRecord.from_str(record_str, character_list)
```

## Implementation Notes

### Trade Validation
- Verifies buyer has sufficient funds
- Confirms resource type is valid
- Ensures resource exists in seller's inventory
- Validates ownership transfer

### Resource Types
- Currently supports "drawings" resource type
- Extensible for additional resource types
- Type validation required for all trades

### Transaction Process
1. Validates buyer's funds
2. Verifies resource availability
3. Transfers resource ownership
4. Updates character balances
5. Generates trade record

### Record Format

```text
[resource_id]: artwork_123
[timestamp]: 1234567890.123
[buyer]: BuyerName
[seller]: SellerName
[remaining_budget]: 900.0
[market_price]: 90.0
[emotion]: excited
[like_score]: 8.5
[expected_price]: 95.0
[final_price]: 100.0
```

## Value Constraints

### Numerical Values
- All prices must be positive floats
- Budget must be sufficient for transaction
- Like score typically ranges from 0 to 10

### Resource Types
- Must be from supported type list
- Currently limited to "drawings"
- Case-sensitive validation 
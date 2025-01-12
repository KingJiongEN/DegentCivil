# Memory Model API Reference

The Memory Model manages different types of memory storage and retrieval for characters in the simulation, including entity memory, location memory, and transaction records.

## Overview

The Memory system consists of several key components:
- Entity memory for character interactions
- Location memory for building/place information 
- Transaction records for economic activities
- Working memory for temporary storage
- Numeric memory with moving average updates

## Memory Class

The main Memory class handles persistent storage and retrieval of memories.

### Properties

- `entity_name`: Name of the entity owning this memory
- `datastore`: MilvusDataStore instance for vector storage
- `numeric_memory`: Dictionary of numeric values with moving average updates

### Methods

#### Memory Storage

```python
def store(self, memory: Dict[str, Any]) -> None
```
Stores a memory object across entity, location and transaction collections.

```python
def store_entity_memory(self, memory: Dict[str, Any]) -> None
```
Stores memories related to people/entities.

```python
def store_location_memory(self, memory: Dict[str, Any]) -> None
```
Stores memories related to buildings/locations.

```python
def store_transaction_memory(self, memory: Dict[str, Any]) -> None
```
Stores memories related to economic transactions.

#### Memory Retrieval

```python
def get_memory(self, main_category: str, name: str) -> Dict[str, Any]
```
Retrieves memories by category and name.

```python
def get_people_memory(self, name: str, default=[]) -> Dict[str, Any]
```
Retrieves memories about specific people.

```python
def get_building_memory(self, name: str, default=[]) -> Dict[str, Any]
```
Retrieves memories about specific buildings.

```python
def get_records_memory(self, name: str) -> Dict[str, Any]
```
Retrieves transaction records by name.

## WorkingMemory Class

Manages temporary memory storage that can be forgotten.

### Methods

```python
def store_memory(self, name: str, memory: Any) -> None
```
Stores a temporary memory.

```python
def retrieve_by_name(self, name: str, default=None) -> Any
```
Retrieves a temporary memory by name.

```python
def forget_by_name(self, name: str) -> None
```
Removes a temporary memory.

## Memory Types

### PeopleMemory

Stores memories about specific people.

#### Properties
- `name`: Person's name
- `relationship`: Relationship status
- `impression`: Overall impression
- `episodicMemory`: List of specific memories

### BuildingMemory

Stores memories about buildings and locations.

#### Properties
- `name`: Building name
- `relationship`: Relationship with the building
- `impression`: Overall impression
- `episodicMemory`: List of specific memories

### ExperienceMemory

Stores memories about plans and actions.

#### Properties
- `plan`: Overall plan
- `acts`: List of specific actions

## Usage Example

```python
# Create memory instance for a character
memory = Memory(entity_name="John")

# Store a new memory
memory.store({
    "people": {
        "Alice": {
            "relationship": "friend",
            "impression": "friendly",
            "memory": "Met at the coffee shop"
        }
    },
    "building": {
        "Coffee Shop": {
            "relationship": "frequent customer",
            "impression": "cozy place",
            "memory": "Good coffee and atmosphere"
        }
    }
})

# Retrieve memories
alice_memories = memory.get_people_memory("Alice")
coffee_shop_memories = memory.get_building_memory("Coffee Shop")
``` 
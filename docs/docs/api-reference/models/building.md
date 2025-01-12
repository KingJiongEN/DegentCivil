# Building Model API Reference

The Building Model manages buildings, their properties, equipment, and job positions in the simulation. It handles building-character interactions and maintains building state.

## Overview

The Building system consists of several key components:
- Building management with physical properties and locations
- Equipment handling within buildings
- Job position management
- Building-character interactions
- Building state persistence

## Building Class

The main Building class handles building operations and state management.

### Properties

- `guid`: Unique identifier for the building
- `name`: Building name
- `position`: Building coordinates (xMin, yMin, xMax, yMax)
- `money`: Building's financial balance
- `description`: Text describing the building
- `instruction`: Building operation instructions
- `equipments`: Dictionary of equipment within the building
- `job_positions`: Dictionary of available jobs

### Methods

#### Building Management

```python
def cordinate_in_building(self, x: int, y: int) -> bool
```
Checks if given coordinates are within building boundaries.

```python
def random_pos_inside(self) -> tuple[int, int]
```
Returns random valid coordinates inside the building.

#### Equipment Management

```python
def add_equipments(self, equipments: dict) -> dict
```
Adds new equipment to the building.

```python
def update_equipments(self, equipments: dict) -> None
```
Updates existing equipment information.

```python
def equipment_instr(self, equip_name: str) -> str
```
Returns instructions for specific equipment.

#### Job Management

```python
def add_jobs(self, jobs: dict) -> dict
```
Adds new job positions to the building.

```python
def update_jobs(self, jobs: dict) -> None
```
Updates existing job information.

## BuildingList Class

Manages collections of buildings in the simulation.

### Methods

```python
def add_building(self, building: Building) -> None
```
Adds a building to the list.

```python
def get_building_by_id(self, building_id: str) -> Optional[Building]
```
Retrieves building by ID.

```python
def get_building_by_name(self, building_name: str) -> Optional[Building]
```
Retrieves building by name.

```python
def get_building_by_pos(self, x: int, y: int) -> Optional[Building]
```
Retrieves building at specified coordinates.

## InBuildingEquip Class

Manages equipment within buildings.

### Properties

- `name`: Equipment name
- `instruction`: Usage instructions
- `status`: Current equipment status
- `interactable`: Whether equipment can be interacted with
- `functions`: Available interaction functions

### Methods

```python
def random_choose(self) -> int
```
Randomly selects an instance from similar equipment.

```python
def modify_internal_properties(self, prop: dict) -> None
```
Updates equipment properties.

## Job Class

Manages job positions within buildings.

### Properties

- `name`: Job title
- `description`: Job description
- `salary`: Job salary
- `num_positions`: Number of available positions
- `applicants`: List of current applicants

### Methods

```python
def add_applicant(self, applicant) -> None
```
Adds new job applicant.

```python
def remove_applicant(self, applicant) -> None
```
Removes job applicant.

## Usage Example

```python
# Create a new building
building = Building(
    id=1,
    name="Coffee Shop",
    llm_cfg={...},
    xMin=0, yMin=0, xMax=10, yMax=10,
    description="A cozy coffee shop in town",
    instruction="Serve coffee and snacks to customers",
    equipments={
        "coffee_machine": {
            "name": "Coffee Machine",
            "instruction": "Press button to brew coffee",
            "status": "operational"
        }
    },
    jobs={
        "barista": {
            "description": "Make and serve coffee",
            "salary": 15.0,
            "num_positions": 2
        }
    }
)

# Add equipment
building.add_equipments({
    "cash_register": {
        "name": "Cash Register",
        "instruction": "Process payments",
        "status": "operational"
    }
})

# Check if position is inside building
is_inside = building.cordinate_in_building(5, 5)

# Get available jobs
available_jobs = building.available_jobs
``` 
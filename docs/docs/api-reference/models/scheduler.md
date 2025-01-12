# Scheduler API Reference

The Scheduler system manages character tasks, schedules, and agendas within the simulation, providing a framework for temporal organization of activities.

## Overview

The system consists of three main components:
- Schedule management for step-by-step activities
- Task tracking with status management
- Agenda organization for time-based events

## Schedule Class

The Schedule class manages sequences of steps and their progression.

### Properties

- `steps`: List of sequential steps to complete
- `summary`: Overview description of the schedule
- `current_index`: Current position in the step sequence

### Methods

```python
def advance(self) -> str
```
Advances to the next step in the schedule. Returns the next step or completion message.

```python
def set_steps(self, steps: list[str], summary: str, **kwargs) -> None
```
Initializes the schedule with a list of steps and summary description.

#### State Properties

```python
@property
def current_step(self) -> str
```
Returns the current active step or status message.

```python
@property
def is_empty(self) -> bool
```
Checks if schedule has been initialized.

```python
@property
def is_complete(self) -> bool
```
Checks if all steps have been completed.

## Task Class

The Task class manages individual tasks and their execution states.

### Properties

- `description`: Task description
- `timing`: Scheduled time for the task
- `status`: Current task status
- `schedule`: Associated Schedule instance

### Constants

```python
PENDING, ACTIVE, PAUSED, DONE = 'pending', 'active', 'paused', 'done'
```

### Methods

```python
def update_status(self) -> None
```
Updates task status based on schedule completion.

```python
def set_status(self, status: str) -> None
```
Sets task status to specified state.

```python
def update_schedule(self, schedule: Schedule) -> None
```
Associates a Schedule instance with the task.

## Agenda Class

The Agenda class manages collections of time-based tasks.

### Properties

- `agenda`: LimitedLengthDict of tasks indexed by time
- `candidate_status`: List of valid task statuses

### Methods

```python
def add_event(self, event: str, time: str) -> None
```
Adds a new event to the agenda.

```python
def check_date(self, date: str) -> Optional[Task]
```
Retrieves task scheduled for specified date.

#### Task Access

```python
@property
def incompleted_events(self) -> list[Task]
```
Returns list of tasks not marked as completed.

```python
@property
def completed_events(self) -> list[Task]
```
Returns list of completed tasks.

## Usage Example

```python
# Create and manage a schedule
schedule = Schedule()
schedule.set_steps(
    steps=["Go to cafe", "Order coffee", "Meet with friend"],
    summary="Coffee meeting with friend"
)

# Create and track a task
task = Task(
    description="Meeting with Dorothy Johnson",
    timing="2021-10-01 14:00"
)
task.update_schedule(schedule)

# Manage agenda
agenda = Agenda()
agenda.add_event(
    event="Performance review meeting",
    time="2021-10-01 14:00"
)

# Check schedule progress
current_step = schedule.current_step
schedule.advance()
```

## Implementation Notes

### Task States
- Tasks can be in one of four states: pending, active, paused, or done
- State transitions are validated against allowed states
- Status updates can be triggered by schedule completion

### Agenda Management
- Uses LimitedLengthDict to maintain a maximum of 20 events
- Automatically removes oldest events when limit is reached
- Provides filtering for completed and incomplete events

### Schedule Tracking
- Maintains step-by-step progression
- Provides completion status
- Supports empty state handling 
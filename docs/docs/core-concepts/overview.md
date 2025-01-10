# Core Concepts Overview

The Degent Civil is built around several key concepts that work together to create a dynamic and interactive virtual town environment. This overview will introduce you to these core concepts and how they interact with each other.

## System Architecture

```mermaid
flowchart TD
    Start[Start Simulation] --> Init[Initialize Simulation]
    Init --> LoadData[Load Frontend/Backend Data]
    LoadData --> CreateManagers[Create Character State Managers]
    
    CreateManagers --> UpdateLoop[Update Loop]
    
    UpdateLoop --> HandleMsg{Handle Server Messages}
    HandleMsg -->|New Day| ResetCountdown[Reset Newday Countdown]
    HandleMsg -->|Other Messages| FilterMsg[Filter Messages by State]
    
    ResetCountdown --> UpdateStates
    FilterMsg --> UpdateStates[Update Character States]
    
    UpdateStates --> StateChains[Execute State Chains]
    
    StateChains --> EnterChain[Enter State Chain]
    StateChains --> ExitChain[Exit State Chain]
    StateChains --> UpdateChain[Update State Chain]
    StateChains --> PostLLMChain[Post LLM Chain]
    
    EnterChain --> |Functions|BuildPrompt[Build Prompt]
    BuildPrompt --> CallLLM[Call LLM]
    
    CallLLM --> ProcessResponse[Process LLM Response]
    ProcessResponse --> StateRouter{State Router}
    
    StateRouter -->|Change State| NextState[Change to Next State]
    StateRouter -->|Stay| UpdateLoop
    
    NextState --> UpdateLoop
    
    UpdateLoop --> |Continue|HandleMsg
    UpdateLoop --> |End|End[End Simulation]

    subgraph "State Functions"
        EnterChain
        ExitChain
        UpdateChain
        PostLLMChain
    end

    subgraph "LLM Processing"
        BuildPrompt
        CallLLM
        ProcessResponse
    end
```

## Key Components

### 1. Simulation

The Simulation is the main container and orchestrator of the simulation. It:
- Manages all characters and buildings
- Coordinates events and interactions
- Maintains the simulation state
- Handles time progression
- Manages global resources

### 2. Characters

Characters are the intelligent agents within the simulation. They:
- Have personalities and traits
- Maintain relationships with other characters
- Follow daily routines and schedules
- Interact with other characters and buildings
- Store and retrieve memories
- Change states based on activities

### 3. Buildings

Buildings are locations within the simulation where:
- Characters can be located
- Activities take place
- Events can be hosted
- Resources can be stored
- Services can be provided

### 4. State Management

The state system:
- Controls character behavior
- Manages transitions between activities
- Handles interruptions and priorities
- Ensures realistic behavior patterns
- Coordinates multi-character interactions

### 5. Memory System

The memory system allows characters to:
- Store experiences and information
- Retrieve relevant memories
- Influence decision making
- Build relationships over time
- Learn from past interactions


## Component Interactions

### Character-Building Interaction

```mermaid
sequenceDiagram
    participant C as Character
    participant B as Building
    participant S as Simulation
    
    C->>S: Request location change
    S->>B: Check availability
    B->>S: Confirm space
    S->>C: Update location
    C->>B: Perform activity
```

### Character-Character Interaction

```mermaid
sequenceDiagram
    participant C1 as Character 1
    participant SM as State Manager
    participant C2 as Character 2
    
    C1->>SM: Request interaction
    SM->>C2: Check availability
    C2->>SM: Confirm state
    SM->>C1: Enable interaction
    C1->>C2: Interact
```

### Memory-State Interaction

```mermaid
sequenceDiagram
    participant C as Character
    participant M as Memory System
    participant S as State Manager
    
    C->>S: Current situation
    S->>M: Request relevant memories
    M->>S: Provide context
    S->>C: Determine action
```

## System Flow

1. **Initialization**
   - Town creation
   - Character and building setup
   - State system initialization
   - Memory system preparation

2. **Runtime**
   - Time progression
   - State updates
   - Interaction processing
   - Memory management
   - Event handling

3. **Interaction Processing**
   - State checking
   - Memory retrieval
   - Action determination
   - Response generation
   - Memory storage

## Integration Points

### 1. LLM Integration

The system integrates with Large Language Models for:
- Natural language processing
- Decision making
- Response generation
- Memory summarization
- Personality expression

### 2. Database Integration

Persistent storage is used for:
- Character data
- Memory vectors
- Relationship graphs
- State history
- Event logs

### 3. External Services

The system can connect with:
- WebSocket for real-time updates
- Redis for caching
- Milvus for vector search
- Custom APIs for extended functionality

## Next Steps

- Learn more about the [Character System](character-system.md)
- Explore [State Management](state-management.md)
- Understand the [Memory System](memory-system.md)
- Study the [Building System](building-system.md)
- Dive into [Simulation Logic](simulation-logic.md) 
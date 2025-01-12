# Entity Factory API Reference

The Entity Factory module provides functionality for creating new agents and characters in the simulation, handling inheritance and trait generation.

## AgentCreation Class

A static utility class that handles the creation of new agents based on parent characteristics.

### Constants

```python
default_bio = "The biography of your parents are: Parent A: {p1bio} and Parent B: {p2bio}"
```

### Static Methods

#### Agent Creation

```python
@staticmethod
def build_new_agent_from_msg(msg: dict, character_ls: CharacterList) -> Character
```
Creates a new agent from a message containing agent specifications.

```python
@staticmethod
def build_new_agent(agent_id: int, character_ls: CharacterList) -> Character
```
Builds a new agent with inherited traits from parent agents.

#### Parent Management

```python
@staticmethod
def find_parent_agent(agent_id: int, character_ls: CharacterList) -> tuple[Character, Character]
```
Locates and returns both parent agents for a given agent ID.

#### Trait Generation

```python
@staticmethod
def create_bio(par1: Character, par2: Character) -> dict
```
Generates a biography for the new agent based on parent biographies using LLM.

```python
@staticmethod
def create_mbti(par1: Character, par2: Character) -> dict
```
Creates MBTI personality type through trait inheritance from parents.

#### Resource Allocation

```python
@staticmethod
def allocate_llm(self) -> dict
```
Assigns LLM configuration to the new agent based on available API resources.

### Creation Process

1. Message Processing
   ```python
   content = json.loads(msg['msg'])
   agent_id = content['agent_guid']
   ```

2. Parent Identification
   ```python
   par1, par2 = AgentCreation.find_parent_agent(agent_id, character_ls)
   ```

3. Feature Generation
   ```python
   new_chara_features = {
       "bio": created_bio,
       "mbti": inherited_mbti,
       "name": assigned_name,
       "llm_cfg": allocated_config
   }
   ```

## Usage Example

```python
# Create new agent from message
new_agent = AgentCreation.build_new_agent_from_msg(
    msg={
        "msg": json.dumps({
            "agent_guid": 123,
            "parent_agent_guid1": 456,
            "parent_agent_guid2": 789
        })
    },
    character_ls=character_list
)

# Direct agent creation
new_agent = AgentCreation.build_new_agent(
    agent_id=123,
    character_ls=character_list
)
```

## Integration Points

### Database Integration
- Agent data retrieval
- Parent information storage
- New agent registration

### LLM Integration
- Biography generation
- Personality trait inheritance
- Character backstory creation

### Resource Management
- API allocation
- Load balancing between cheap and official APIs
- Configuration management

### Name Management
- Unique name generation
- Name inheritance patterns
- Name validation 
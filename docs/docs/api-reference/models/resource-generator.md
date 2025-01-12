# Resource Generator API Reference

The Resource Generator system provides image generation capabilities through OpenAI's DALL-E model, managing the creation and caching of AI-generated artwork within the simulation.

## Overview

The system consists of two main components:
- DALLEAgent for handling image generation requests
- Caching mechanism for efficient resource management

## DALLEAgent Class

The DALLEAgent class inherits from ConversableAgent and manages DALL-E image generation requests.

### Properties

- `owner`: Reference to the owning Character instance
- `client`: OpenAI client instance for API calls
- `api_key`: OpenAI API key for authentication

### Methods

#### Image Generation

```python
def draw(self, prompt: str, api_key: str = None) -> Drawing
```
Generates an image using DALL-E based on the provided prompt. Returns a Drawing instance.

```python
def generate_dalle_reply(self, messages: Optional[List[Dict]], sender: Agent, config) -> tuple[bool, dict]
```
Processes messages and generates image replies. Returns success status and image information.

#### Asynchronous Operations

```python
async def a_generate_dalle_reply(self, messages: Optional[List[Dict]], sender: Agent, config)
```
Asynchronous version of generate_dalle_reply.

```python
async def a_process_then_reply(self, message, sender: Agent, restart=True, silent=True)
```
Processes messages and generates replies asynchronously.

#### Validation

```python
def sanity_check(self, id, image_url, description) -> bool
```
Validates image generation results for proper formatting and content.

## DALL-E Call Function

```python
def dalle_call(client: OpenAI, model: str, prompt: str, size: str, quality: str, n: int) -> str
```
Handles direct DALL-E API calls with caching support.

### Parameters

- `client`: OpenAI client instance
- `model`: DALL-E model version
- `prompt`: Image generation prompt
- `size`: Output image dimensions
- `quality`: Image quality setting
- `n`: Number of images to generate

### Returns

- URL string for the generated image

## Usage Example

```python
# Initialize DALL-E agent
dalle_agent = DALLEAgent(
    name="ArtGenerator",
    owner=character,
    llm_config={
        "config_list": [{
            "api_key": "your-api-key",
            "base_url": "https://api.openai.com/v1"
        }]
    }
)

# Generate image
message = {"content": "A serene landscape with mountains at sunset"}
response = await dalle_agent.a_process_then_reply(
    message=message,
    sender=character
)

# Access generated image
image_url = response['img_url']
image_id = response['img_id']
```

## Cache Implementation

The system uses diskcache for efficient resource management:

```python
cache = Cache(".cache/")
key = (model, prompt, size, quality, n)
```

### Cache Features

- Disk-based storage in `.cache/` directory
- Key based on generation parameters
- Automatic retrieval of cached results
- Fallback to API calls for cache misses

## Implementation Notes

- Supports both synchronous and asynchronous operations
- Implements error handling and retry logic
- Maintains image generation history
- Uses caching to optimize API usage
- Validates all generated content
- Integrates with character's drawing collection

## Response Format

```json
{
    "img_url": "https://...",
    "img_id": "uuid-string"
}
``` 
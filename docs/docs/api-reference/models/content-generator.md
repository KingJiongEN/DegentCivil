# Content Generator API Reference

The Content Generator module provides functionality for generating and managing drawings and artwork in the simulation.

## Drawing Class

Represents a single drawing or artwork piece in the simulation.

### Properties

- `id`: Unique identifier for the drawing
- `owner`: Reference to the Character who owns the drawing
- `image_url`: URL to the drawing's image
- `description`: Text description of the drawing
- `price`: Current price of the drawing
- `timestamp`: Creation timestamp

### Methods

```python
@classmethod
async def a_draw(cls, prompt: str, owner: Character, api_key: str = None) -> Drawing
```
Creates a new drawing.

```python
def set_price(self, price: int) -> None
```
Sets the drawing's price.

## DrawingList Class

Manages a collection of drawings for a character.

### Properties

- `cache`: Local storage for drawings
- `drawings`: List of Drawing objects
- `owner`: Reference to the owning Character

### Methods

```python
def add(self, drawing: Drawing) -> None
```
Adds a drawing to the collection and updates storage.

```python
def get(self, id: str) -> Optional[Drawing]
```
Retrieves a drawing by ID.

## Integration Points

### Vector Storage
- Milvus integration for artwork embeddings
- Similarity search capabilities
- Market value adjustments

### Database Storage
- Artwork metadata storage
- Price history tracking
- Ownership records

### Image Generation
- DALLE-3 integration
- Prompt processing
- Image caching 
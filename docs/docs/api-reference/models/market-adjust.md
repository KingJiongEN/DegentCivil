# Market Adjust API Reference

The Market Adjust system manages dynamic pricing for artworks based on market conditions, using embedding-based similarity to adjust prices according to market trends.

## Overview

The system consists of:
- Market-based price adjustment
- Embedding similarity calculations
- Database integration for artwork pricing
- Automated price fluctuation handling

## MarketAdjust Class

The MarketAdjust class handles market-based price adjustments for artworks.

### Properties

- `commodities`: List of commodities to track
- `model`: Embedding model (default: OpenAI text-embedding-3-large)
- `artwork_milvus_data_store`: Milvus collection for artwork data

### Methods

#### Market Updates

```python
def update(self) -> None
```
Retrieves market information and triggers price updates.

```python
def get_market_info(self) -> str
```
Retrieves current market information for analysis.

```python
def update_market(self, market: str) -> None
```
Updates artwork prices based on market conditions using similarity analysis.

#### Embedding Operations

```python
def call_model(self, commodity: str) -> list[float]
```
Generates embeddings for market analysis using the configured model.

```python
def get_commodity_embed(self, commodity) -> list[float]
```
Retrieves or generates embeddings for a commodity.

#### Price Adjustments

```python
def price_fluctuation(self, market_embed: list[float], commodity_embed: list[float]) -> float
```
Calculates price adjustments based on embedding similarity.

```python
def price_fluctuation_by_sim(self, resource_id: str, sim: float) -> float
```
Calculates and applies price adjustments using pre-computed similarity.

```python
def artwork_price_change(self, artwork_id: str, delta_price: float) -> Optional[float]
```
Updates artwork price in database and returns new price.

## Usage Example

```python
# Initialize market adjuster
market = MarketAdjust(
    commodities=[],
    model=OpenAIEmbeddings(model="text-embedding-3-large")
)

# Update market prices
market.update()

# Manual market update
market_news = "Market trend update: Increased demand for abstract art"
market.update_market(market_news)

# Direct price adjustment
artwork_id = "art123"
similarity = 0.75
adjustment = market.price_fluctuation_by_sim(artwork_id, similarity)
```

## Implementation Notes

### Similarity Calculation
- Uses cosine similarity between embeddings
- Similarity range: 0 to 1
- Price adjustment formula: (similarity - 0.4) * 1000

### Market Analysis
- High similarity search (top 20 matches)
- Low similarity search (bottom 20 matches)
- Configurable similarity thresholds
- Automatic price updates based on market trends

### Database Integration
- Milvus vector database for artwork data
- Automatic price updates in database
- Price change logging and tracking

### Embedding Requirements
- Commodities must have either:
  - 'description' attribute
  - 'embed' attribute
- Descriptions must be strings
- Embeddings must be compatible with model

## Configuration Parameters

### Search Parameters
```python
{
    "metric_type": "COSINE",
    "params": {
        "radius": 0.0,    # Outer search boundary
        "range_filter": 0.2  # Inner search boundary
    }
}
```

### Price Adjustment Constraints
- Base adjustment multiplier: 1000
- Similarity threshold: 0.4
- Adjustments can be positive or negative
- No maximum adjustment limit

## Error Handling

- Validates commodity attributes
- Verifies description types
- Checks artwork existence in database
- Logs price change notifications 
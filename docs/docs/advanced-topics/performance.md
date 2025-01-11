# Performance Optimization

This guide covers advanced techniques for optimizing the performance of your DegentCivil simulation.

## Performance Overview

DegentCivil's performance is influenced by several key factors:

1. Number of active characters
2. Complexity of character states
3. Memory system usage
4. Database operations
5. LLM API calls
6. Event processing
7. Physical simulation calculations

## Optimization Strategies

### 1. Character Management

#### Batch Processing

```python
def process_characters_in_batches(characters, batch_size=100):
    for i in range(0, len(characters), batch_size):
        batch = characters[i:i+batch_size]
        process_character_batch(batch)
```

#### State Optimization

```python
class OptimizedState(BaseState):
    def __init__(self):
        super().__init__()
        self.cached_data = {}
        
    def execute(self, character):
        if self.should_update_cache():
            self.cached_data = self.heavy_computation()
        return self.cached_data
```

### 2. Memory System

#### Memory Pruning

```python
def optimize_memory(character):
    # Remove old, less relevant memories
    character.memory.prune_old_memories(threshold_days=30)
    
    # Compress similar memories
    character.memory.compress_similar_memories()
    
    # Archive rarely accessed memories
    character.memory.archive_inactive_memories()
```

#### Efficient Querying

```python
def query_memory(character, query, limit=10):
    # Use indexed fields for faster queries
    return character.memory.query(
        query,
        limit=limit,
        use_cache=True,
        index_fields=['timestamp', 'importance']
    )
```

### 3. Database Optimization

#### Connection Pooling

```python
from app.database import Database

class OptimizedDatabase(Database):
    def __init__(self):
        self.connection_pool = create_connection_pool(
            min_connections=5,
            max_connections=20,
            idle_timeout=300
        )
```

#### Query Optimization

```python
class QueryOptimizer:
    def __init__(self):
        self.query_cache = {}
        
    def optimize_query(self, query):
        # Use prepared statements
        if query in self.query_cache:
            return self.query_cache[query]
            
        # Analyze and optimize new queries
        optimized = self.analyze_and_optimize(query)
        self.query_cache[query] = optimized
        return optimized
```

### 4. LLM Integration

#### Token Management

```python
class TokenManager:
    def __init__(self, max_tokens=4096):
        self.max_tokens = max_tokens
        
    def optimize_prompt(self, prompt):
        # Truncate and optimize prompt to fit token limit
        return self.truncate_to_token_limit(prompt)
        
    def batch_requests(self, prompts):
        # Combine similar prompts to reduce API calls
        return self.combine_similar_prompts(prompts)
```

#### Response Caching

```python
class LLMCache:
    def __init__(self):
        self.cache = {}
        
    def get_response(self, prompt):
        cache_key = self.generate_cache_key(prompt)
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        response = self.call_llm_api(prompt)
        self.cache[cache_key] = response
        return response
```

## Monitoring and Profiling

### 1. Performance Metrics

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'character_updates': [],
            'memory_operations': [],
            'database_queries': [],
            'llm_calls': []
        }
        
    def record_metric(self, category, duration):
        self.metrics[category].append({
            'timestamp': time.time(),
            'duration': duration
        })
        
    def analyze_performance(self):
        return {
            category: self.calculate_statistics(data)
            for category, data in self.metrics.items()
        }
```

### 2. Profiling Tools

```python
import cProfile
import pstats

def profile_simulation(simulation, duration):
    profiler = cProfile.Profile()
    profiler.enable()
    
    simulation.run(duration)
    
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    return stats
```

## Memory Management

### 1. Memory Pooling

```python
class MemoryPool:
    def __init__(self, initial_size=1000):
        self.pool = [None] * initial_size
        self.available = set(range(initial_size))
        
    def allocate(self):
        if not self.available:
            self.expand_pool()
        return self.pool[self.available.pop()]
        
    def release(self, index):
        self.available.add(index)
```

### 2. Garbage Collection

```python
import gc

def optimize_memory_usage():
    # Run garbage collection
    gc.collect()
    
    # Disable automatic garbage collection
    gc.disable()
    
    # Manual collection at specific intervals
    def scheduled_gc():
        gc.collect()
        schedule_next_gc()
```

## Configuration Optimization

### 1. Tuning Parameters

```python
class SimulationConfig:
    def __init__(self):
        self.update_interval = 0.1  # seconds
        self.max_characters = 1000
        self.memory_limit = 1000000  # bytes
        self.cache_size = 10000
        self.batch_size = 100
```

### 2. Dynamic Adjustment

```python
class DynamicOptimizer:
    def __init__(self, simulation):
        self.simulation = simulation
        
    def adjust_parameters(self):
        # Monitor system resources
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        
        # Adjust parameters based on usage
        if cpu_usage > 80:
            self.reduce_update_frequency()
        if memory_usage > 80:
            self.clear_caches()
```

## Best Practices

1. **Profile First**
   - Identify bottlenecks
   - Measure impact of changes
   - Set performance baselines

2. **Optimize Incrementally**
   - Make one change at a time
   - Measure impact of each change
   - Document improvements

3. **Balance Resources**
   - CPU vs Memory usage
   - Network vs Local processing
   - Storage vs Computation

4. **Cache Strategically**
   - Identify frequently accessed data
   - Set appropriate cache sizes
   - Implement cache invalidation

5. **Monitor Continuously**
   - Track performance metrics
   - Set up alerts
   - Regular optimization reviews 
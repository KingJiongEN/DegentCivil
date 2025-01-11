# Database Management

This guide covers advanced database management techniques for DegentCivil, including optimization, maintenance, and best practices.

## Database Architecture

DegentCivil uses a flexible database architecture that supports multiple storage backends:

1. SQLite (default for local development)
2. PostgreSQL (recommended for production)
3. MongoDB (optional for specific use cases)

## Basic Setup

### SQLite Configuration

```python
from app.database import Database

db_config = {
    'type': 'sqlite',
    'path': 'simulation.db',
    'journal_mode': 'WAL'
}

db = Database(db_config)
```

### PostgreSQL Configuration

```python
db_config = {
    'type': 'postgresql',
    'host': 'localhost',
    'port': 5432,
    'database': 'degent_civil',
    'user': 'username',
    'password': 'password',
    'max_connections': 20
}
```

## Data Models

### Character Data

```python
class CharacterModel:
    table_name = 'characters'
    schema = {
        'id': 'UUID PRIMARY KEY',
        'name': 'TEXT NOT NULL',
        'age': 'INTEGER',
        'occupation': 'TEXT',
        'location_id': 'UUID REFERENCES locations(id)',
        'state': 'JSONB',
        'created_at': 'TIMESTAMP',
        'updated_at': 'TIMESTAMP'
    }
    indexes = [
        ('name_idx', 'name'),
        ('location_idx', 'location_id'),
        ('state_idx', 'state', 'gin')
    ]
```

### Memory Storage

```python
class MemoryModel:
    table_name = 'memories'
    schema = {
        'id': 'UUID PRIMARY KEY',
        'character_id': 'UUID REFERENCES characters(id)',
        'content': 'TEXT',
        'importance': 'FLOAT',
        'timestamp': 'TIMESTAMP',
        'metadata': 'JSONB'
    }
    indexes = [
        ('character_timestamp_idx', ['character_id', 'timestamp']),
        ('importance_idx', 'importance')
    ]
```

## Query Optimization

### Index Management

```python
class IndexManager:
    def __init__(self, database):
        self.db = database
        
    def create_indexes(self):
        """Create optimized indexes based on common queries"""
        queries = [
            """
            CREATE INDEX IF NOT EXISTS char_location_idx 
            ON characters (location_id) 
            WHERE active = true
            """,
            """
            CREATE INDEX IF NOT EXISTS memory_importance_idx 
            ON memories (importance) 
            WHERE importance > 0.7
            """
        ]
        for query in queries:
            self.db.execute(query)
            
    def analyze_index_usage(self):
        """Monitor and analyze index usage patterns"""
        return self.db.execute("""
            SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
        """)
```

### Query Planning

```python
class QueryPlanner:
    def optimize_query(self, query):
        """Analyze and optimize query execution plan"""
        explain_query = f"EXPLAIN ANALYZE {query}"
        plan = self.db.execute(explain_query)
        
        if self.needs_optimization(plan):
            return self.rewrite_query(query)
        return query
        
    def needs_optimization(self, plan):
        """Check if query plan needs optimization"""
        return (
            self.has_sequential_scan(plan) or
            self.has_high_cost(plan) or
            self.has_poor_row_estimate(plan)
        )
```

## Performance Tuning

### Connection Pooling

```python
from psycopg2 import pool

class ConnectionPool:
    def __init__(self, config):
        self.pool = pool.SimpleConnectionPool(
            minconn=5,
            maxconn=20,
            **config
        )
        
    def get_connection(self):
        return self.pool.getconn()
        
    def return_connection(self, conn):
        self.pool.putconn(conn)
        
    def close_all(self):
        self.pool.closeall()
```

### Query Caching

```python
class QueryCache:
    def __init__(self):
        self.cache = {}
        self.ttl = 300  # 5 minutes
        
    def get(self, query, params=None):
        key = self.generate_key(query, params)
        if key in self.cache:
            entry = self.cache[key]
            if not self.is_expired(entry):
                return entry['data']
        return None
        
    def set(self, query, params, data):
        key = self.generate_key(query, params)
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
```

## Data Migration

### Migration Manager

```python
class MigrationManager:
    def __init__(self, database):
        self.db = database
        self.migrations_table = 'schema_migrations'
        
    def create_migrations_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
    def apply_migrations(self, migrations_dir):
        """Apply pending migrations"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations(migrations_dir)
        
        for migration in pending:
            self.apply_migration(migration)
            self.record_migration(migration)
```

### Data Backup

```python
class BackupManager:
    def create_backup(self, path):
        """Create database backup"""
        if self.db.type == 'postgresql':
            os.system(f'pg_dump {self.db.name} > {path}')
        elif self.db.type == 'sqlite':
            import shutil
            shutil.copy2(self.db.path, path)
            
    def restore_backup(self, path):
        """Restore database from backup"""
        if self.db.type == 'postgresql':
            os.system(f'psql {self.db.name} < {path}')
        elif self.db.type == 'sqlite':
            import shutil
            shutil.copy2(path, self.db.path)
```

## Maintenance

### Database Cleanup

```python
class DatabaseMaintenance:
    def cleanup_old_data(self):
        """Remove old, unnecessary data"""
        queries = [
            """
            DELETE FROM memories 
            WHERE importance < 0.1 
            AND timestamp < NOW() - INTERVAL '30 days'
            """,
            """
            DELETE FROM character_states 
            WHERE updated_at < NOW() - INTERVAL '7 days'
            """
        ]
        for query in queries:
            self.db.execute(query)
            
    def vacuum_database(self):
        """Reclaim storage and update statistics"""
        self.db.execute("VACUUM ANALYZE")
```

### Monitoring

```python
class DatabaseMonitor:
    def check_health(self):
        """Check database health metrics"""
        metrics = {
            'connection_count': self.get_connection_count(),
            'database_size': self.get_database_size(),
            'cache_hit_ratio': self.get_cache_hit_ratio(),
            'slow_queries': self.get_slow_queries()
        }
        return metrics
        
    def get_slow_queries(self):
        return self.db.execute("""
            SELECT query, calls, total_time, rows
            FROM pg_stat_statements
            ORDER BY total_time DESC
            LIMIT 10
        """)
```

## Best Practices

1. **Regular Maintenance**
   - Schedule regular cleanup tasks
   - Monitor database size
   - Update statistics regularly
   - Backup data frequently

2. **Query Optimization**
   - Use appropriate indexes
   - Optimize complex queries
   - Monitor query performance
   - Use prepared statements

3. **Connection Management**
   - Use connection pooling
   - Close unused connections
   - Monitor connection usage
   - Set appropriate timeouts

4. **Data Integrity**
   - Use transactions appropriately
   - Implement proper constraints
   - Validate data before insertion
   - Handle errors gracefully

5. **Security**
   - Use strong authentication
   - Encrypt sensitive data
   - Regular security audits
   - Proper access control 
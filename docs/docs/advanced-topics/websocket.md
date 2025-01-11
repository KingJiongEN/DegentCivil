# WebSocket Integration

This guide covers the implementation of WebSocket functionality in DegentCivil for real-time communication and updates.

## Overview

WebSocket integration enables:

- Real-time simulation updates
- Character state broadcasting
- Event notifications
- Interactive debugging
- Live monitoring

## Basic Setup

### Server Implementation

```python
import asyncio
import websockets
import json

class SimulationWebSocket:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        
    async def start_server(self):
        server = await websockets.serve(
            self.handle_connection,
            self.host,
            self.port
        )
        print(f"WebSocket server running on ws://{self.host}:{self.port}")
        await server.wait_closed()
        
    async def handle_connection(self, websocket, path):
        self.clients.add(websocket)
        try:
            await self.handle_messages(websocket)
        finally:
            self.clients.remove(websocket)
```

### Client Implementation

```python
class SimulationClient:
    def __init__(self, uri='ws://localhost:8765'):
        self.uri = uri
        self.websocket = None
        
    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print(f"Connected to {self.uri}")
        
    async def receive_updates(self):
        while True:
            try:
                message = await self.websocket.recv()
                await self.handle_message(json.loads(message))
            except websockets.exceptions.ConnectionClosed:
                break
```

## Message Protocol

### Message Structure

```python
class WebSocketMessage:
    def __init__(self, type, data):
        self.type = type
        self.data = data
        
    def to_json(self):
        return json.dumps({
            'type': self.type,
            'data': self.data,
            'timestamp': time.time()
        })
        
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(data['type'], data['data'])
```

### Message Types

```python
class MessageTypes:
    CHARACTER_UPDATE = 'character_update'
    STATE_CHANGE = 'state_change'
    EVENT_NOTIFICATION = 'event_notification'
    ERROR = 'error'
    HEARTBEAT = 'heartbeat'
```

## Real-time Updates

### Character State Broadcasting

```python
class CharacterStatePublisher:
    def __init__(self, websocket_server):
        self.server = websocket_server
        
    async def publish_state_change(self, character):
        message = WebSocketMessage(
            MessageTypes.STATE_CHANGE,
            {
                'character_id': character.id,
                'new_state': character.state_name,
                'location': character.location.name,
                'timestamp': time.time()
            }
        )
        await self.broadcast_message(message)
        
    async def broadcast_message(self, message):
        if not self.server.clients:
            return
            
        await asyncio.gather(
            *[client.send(message.to_json())
              for client in self.server.clients]
        )
```

### Event Notifications

```python
class EventNotifier:
    def __init__(self, websocket_server):
        self.server = websocket_server
        
    async def notify_event(self, event_type, event_data):
        message = WebSocketMessage(
            MessageTypes.EVENT_NOTIFICATION,
            {
                'event_type': event_type,
                'data': event_data,
                'timestamp': time.time()
            }
        )
        await self.server.broadcast_message(message)
```

## Connection Management

### Connection Pool

```python
class ConnectionPool:
    def __init__(self):
        self.connections = {}
        self.max_connections = 1000
        
    async def add_connection(self, client_id, websocket):
        if len(self.connections) >= self.max_connections:
            raise Exception("Maximum connections reached")
            
        self.connections[client_id] = websocket
        
    async def remove_connection(self, client_id):
        if client_id in self.connections:
            del self.connections[client_id]
```

### Authentication

```python
class WebSocketAuth:
    def __init__(self):
        self.tokens = {}
        
    async def authenticate(self, websocket, token):
        if not self.is_valid_token(token):
            await websocket.close(1008, "Invalid token")
            return False
        return True
        
    def is_valid_token(self, token):
        return token in self.tokens
```

## Error Handling

### Error Types

```python
class WebSocketError:
    INVALID_MESSAGE = 1001
    AUTH_FAILED = 1002
    RATE_LIMIT = 1003
    SERVER_ERROR = 1004
    
    @staticmethod
    def create_error_message(code, message):
        return WebSocketMessage(
            MessageTypes.ERROR,
            {
                'code': code,
                'message': message
            }
        )
```

### Error Handling Middleware

```python
class ErrorHandler:
    async def handle_error(self, websocket, error):
        error_message = WebSocketError.create_error_message(
            error.code,
            str(error)
        )
        await websocket.send(error_message.to_json())
```

## Performance Optimization

### Message Batching

```python
class MessageBatcher:
    def __init__(self, max_size=100, max_wait=1.0):
        self.max_size = max_size
        self.max_wait = max_wait
        self.batch = []
        
    async def add_message(self, message):
        self.batch.append(message)
        if len(self.batch) >= self.max_size:
            await self.flush()
            
    async def flush(self):
        if not self.batch:
            return
            
        batch_message = WebSocketMessage(
            'batch',
            self.batch
        )
        self.batch = []
        return batch_message
```

### Rate Limiting

```python
class RateLimiter:
    def __init__(self, max_messages=100, window_seconds=60):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.message_counts = {}
        
    async def check_rate_limit(self, client_id):
        now = time.time()
        if client_id not in self.message_counts:
            self.message_counts[client_id] = []
            
        # Clean old messages
        self.message_counts[client_id] = [
            timestamp for timestamp in self.message_counts[client_id]
            if now - timestamp <= self.window_seconds
        ]
        
        if len(self.message_counts[client_id]) >= self.max_messages:
            raise WebSocketError(
                WebSocketError.RATE_LIMIT,
                "Rate limit exceeded"
            )
            
        self.message_counts[client_id].append(now)
```

## Monitoring and Debugging

### Connection Monitor

```python
class ConnectionMonitor:
    def __init__(self):
        self.metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0
        }
        
    def update_metrics(self, metric_name, value=1):
        self.metrics[metric_name] += value
        
    def get_metrics(self):
        return self.metrics
```

### Debug Mode

```python
class WebSocketDebugger:
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.log_queue = asyncio.Queue()
        
    async def log_message(self, direction, message):
        if not self.enabled:
            return
            
        await self.log_queue.put({
            'timestamp': time.time(),
            'direction': direction,
            'message': message
        })
        
    async def process_logs(self):
        while True:
            log = await self.log_queue.get()
            print(f"[{log['timestamp']}] {log['direction']}: {log['message']}")
```

## Best Practices

1. **Connection Management**
   - Implement heartbeat mechanism
   - Handle reconnection gracefully
   - Clean up resources properly
   - Monitor connection health

2. **Security**
   - Use secure WebSocket (wss://)
   - Implement authentication
   - Validate all messages
   - Rate limit connections

3. **Performance**
   - Batch messages when possible
   - Implement compression
   - Monitor memory usage
   - Handle backpressure

4. **Error Handling**
   - Graceful error recovery
   - Meaningful error messages
   - Proper logging
   - Circuit breakers

5. **Testing**
   - Unit test message handlers
   - Load test connections
   - Test error scenarios
   - Verify message protocols 
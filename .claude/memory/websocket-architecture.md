# WebSocket Event Streaming Architecture

Real-time event streaming architecture for ADW observability and swimlane visualization.

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Real-Time Event Flow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Agent Execution                                                │
│        │                                                        │
│        ▼                                                        │
│  ┌─────────────┐                                               │
│  │ Hook Events │──► ADW Event ──► WebSocket Server             │
│  └─────────────┘         │              │                       │
│                          │              │                       │
│                          ▼              ▼                       │
│                    ┌──────────┐   ┌───────────────┐            │
│                    │ Database │   │ Broadcasting  │            │
│                    │ Logging  │   │ to Clients    │            │
│                    └──────────┘   └───────────────┘            │
│                                         │                       │
│                          ┌──────────────┼──────────────┐       │
│                          ▼              ▼              ▼       │
│                    ┌─────────┐   ┌─────────┐   ┌─────────┐    │
│                    │ Client  │   │ Client  │   │ Client  │    │
│                    │   1     │   │   2     │   │   N     │    │
│                    └─────────┘   └─────────┘   └─────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## WebSocket Server Implementation

### FastAPI WebSocket Endpoint

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Set
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        self.active_connections -= disconnected

manager = ConnectionManager()

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive client messages
            data = await websocket.receive_text()
            # Handle client messages (filters, subscriptions, etc.)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## Event Message Format

### ADW Event Schema

```json
{
  "type": "adw_event",
  "adw_id": "a1b2c3d4",
  "step": "build",
  "event_type": "ToolUseBlock",
  "timestamp": "2026-01-01T14:30:00Z",
  "summary": "Writing authentication middleware to handle JWT tokens",
  "payload": {
    "tool_name": "Write",
    "file_path": "/src/middleware/auth.py",
    "duration_ms": 45
  }
}
```

### System Event Schema

```json
{
  "type": "system",
  "event": "step_complete",
  "adw_id": "a1b2c3d4",
  "step": "build",
  "status": "completed",
  "duration_ms": 45000
}
```

## Broadcasting Implementation

### From Hook Scripts

```python
async def broadcast_event(event: dict):
    """Broadcast event to WebSocket server."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/api/events/broadcast",
            json=event
        ) as response:
            return response.status == 200
```

### Internal API Endpoint

```python
@app.post("/api/events/broadcast")
async def broadcast_event(event: dict):
    await manager.broadcast(event)
    return {"status": "broadcasted", "clients": len(manager.active_connections)}
```

## Resilient Client Implementation

### Connection Management

```typescript
class ADWWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;

  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws/events');

    this.ws.onopen = () => {
      console.log('Connected to ADW event stream');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleEvent(data);
    };

    this.ws.onclose = () => {
      this.scheduleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      setTimeout(() => this.connect(), Math.min(delay, 30000));
    }
  }

  private handleEvent(event: ADWEvent) {
    // Dispatch to appropriate handler based on event type
    eventBus.emit(event.event_type, event);
  }
}
```

### Event Filtering

```typescript
class EventFilter {
  private adwId: string | null = null;
  private stepFilter: Set<string> = new Set();
  private typeFilter: Set<string> = new Set();

  setADWFilter(adwId: string) {
    this.adwId = adwId;
  }

  setStepFilter(steps: string[]) {
    this.stepFilter = new Set(steps);
  }

  setTypeFilter(types: string[]) {
    this.typeFilter = new Set(types);
  }

  shouldShow(event: ADWEvent): boolean {
    if (this.adwId && event.adw_id !== this.adwId) return false;
    if (this.stepFilter.size && !this.stepFilter.has(event.step)) return false;
    if (this.typeFilter.size && !this.typeFilter.has(event.event_type)) return false;
    return true;
  }
}
```

## Swimlane Visualization

### Lane Structure

```text
┌─────────────────────────────────────────────────────────────────┐
│ ADW: a1b2c3d4 - Feature Implementation                          │
├────────────┬────────────┬────────────┬────────────┬─────────────┤
│    Plan    │   Build    │   Review   │    Fix     │   Status    │
├────────────┼────────────┼────────────┼────────────┼─────────────┤
│ 💬 Created │ 🛠️ Write   │            │            │ ● Running   │
│    spec    │   auth.py  │            │            │             │
│            │ 🛠️ Write   │            │            │ Cost: $0.42 │
│            │   tests.py │            │            │             │
│            │ 🧠 Thinking│            │            │ Tokens: 12K │
└────────────┴────────────┴────────────┴────────────┴─────────────┘
```

### Vue Component Pattern

```vue
<template>
  <div class="swimlane-container">
    <div
      v-for="step in steps"
      :key="step.name"
      class="swimlane"
      :class="{ active: step.name === currentStep }"
    >
      <div class="lane-header">{{ step.name }}</div>
      <div class="lane-events">
        <EventCard
          v-for="event in getEventsForStep(step.name)"
          :key="event.id"
          :event="event"
          @click="selectEvent(event)"
        />
      </div>
    </div>
    <StatusPanel :adw-id="adwId" :cost="totalCost" :tokens="totalTokens" />
  </div>
</template>
```

## Reconnection Strategies

### Exponential Backoff

```python
class ReconnectionStrategy:
    def __init__(self):
        self.base_delay = 1.0
        self.max_delay = 60.0
        self.attempts = 0

    def next_delay(self) -> float:
        delay = min(
            self.base_delay * (2 ** self.attempts),
            self.max_delay
        )
        self.attempts += 1
        return delay

    def reset(self):
        self.attempts = 0
```

### Heartbeat Mechanism

```python
async def heartbeat_loop(websocket: WebSocket):
    while True:
        try:
            await websocket.send_json({"type": "ping"})
            await asyncio.sleep(30)
        except:
            break
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
| --- | --- | --- |
| No reconnection | Clients disconnect permanently | Exponential backoff |
| Blocking broadcasts | Slow clients block all | Async with timeouts |
| No heartbeat | Stale connections accumulate | Ping/pong mechanism |
| Unbuffered events | Events lost during reconnect | Client-side buffering |
| No filtering | UI overwhelmed | Server/client filtering |

## Cross-References

- @hook-event-patterns.md - Event types and payloads
- @production-patterns.md - Backend infrastructure
- @three-pillars-orchestration.md - Observability pillar

---

**Token Budget:** ~1,600 tokens
**Last Updated:** 2026-01-01

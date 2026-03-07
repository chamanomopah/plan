# Hook Event Patterns

Event types and handling patterns for ADW observability through Claude Code hooks.

## Event Types

> **Documentation Verification:** The event types listed here are Claude Code internal types that may change between releases. For authoritative current event types, query the `hook-management` skill which delegates to `docs-management` for official documentation.

The ADW system captures these event types during agent execution:

| Event Type | Icon | Source | Description |
| --- | --- | --- | --- |
| `TextBlock` | 💬 | Agent output | Text response from agent |
| `ToolUseBlock` | 🛠️ | Agent action | Tool invocation (Read, Write, Bash, etc.) |
| `ThinkingBlock` | 🧠 | Agent reasoning | Extended thinking output |
| `PreToolUse` | 🪝 | Hook trigger | Before tool execution |
| `PostToolUse` | 🪝 | Hook trigger | After tool execution |
| `StepStart` | ⚙️ | System | Workflow step beginning |
| `StepEnd` | ⚙️ | System | Workflow step completion |

## Event Payload Structure

### Base Event Schema

```python
class ADWEvent(BaseModel):
    type: str                    # Event type from table above
    adw_id: str                  # 8-char UUID for workflow correlation
    step: str                    # Current step (plan, build, review, fix)
    timestamp: datetime
    payload: dict                # Event-specific data
    summary: str | None          # AI-generated 15-word summary
```

### ToolUseBlock Payload

```python
class ToolUsePayload(BaseModel):
    tool_name: str               # Read, Write, Bash, Edit, etc.
    tool_inputs: dict            # Arguments passed to tool
    tool_output: str | None      # Result (truncated if large)
    duration_ms: int
```

### ThinkingBlock Payload

```python
class ThinkingPayload(BaseModel):
    thinking_text: str           # Extended thinking content
    token_count: int
```

### StepStart/End Payload

```python
class StepPayload(BaseModel):
    step_name: str
    inputs: dict                 # Step inputs
    outputs: dict | None         # Step outputs (StepEnd only)
    duration_ms: int | None      # Total duration (StepEnd only)
    status: str                  # 'running', 'completed', 'failed'
```

## Hook Configuration

### PreToolUse Hooks

Intercept before tool execution:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "command": "python adw_modules/hooks/pre_tool.py"
      }
    ]
  }
}
```

Hook receives JSON via stdin:

```json
{
  "hook_type": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.py",
    "content": "..."
  },
  "session_id": "abc123",
  "adw_id": "a1b2c3d4"
}
```

### PostToolUse Hooks

Capture after tool execution:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "command": "python adw_modules/hooks/post_tool.py"
      }
    ]
  }
}
```

Hook receives tool result:

```json
{
  "hook_type": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {...},
  "tool_output": "File written successfully",
  "duration_ms": 45,
  "session_id": "abc123",
  "adw_id": "a1b2c3d4"
}
```

## Event Broadcasting Pattern

### Hook to WebSocket Flow

```text
Agent Execution
      │
      ▼
┌─────────────────┐
│  PreToolUse     │──► Hook script ──► WebSocket broadcast
│  Hook Trigger   │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Tool Execution │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  PostToolUse    │──► Hook script ──► WebSocket broadcast
│  Hook Trigger   │
└─────────────────┘
```

### Broadcast Script Pattern

```python
#!/usr/bin/env python
import sys
import json
import asyncio
from adw_modules.adw_websockets import broadcast_event
from adw_modules.adw_summarizer import summarize

async def main():
    event_data = json.load(sys.stdin)

    # Generate AI summary
    summary = await summarize(event_data)

    # Build ADW event
    adw_event = {
        "type": "adw_event",
        "adw_id": event_data.get("adw_id"),
        "step": event_data.get("step", "unknown"),
        "event_type": event_data.get("hook_type"),
        "summary": summary,
        "payload": event_data
    }

    # Broadcast to connected clients
    await broadcast_event(adw_event)

if __name__ == "__main__":
    asyncio.run(main())
```

## AI-Generated Summaries

Haiku generates concise summaries for each event:

```python
async def summarize(event: dict) -> str:
    event_type = event.get("hook_type", event.get("type"))
    tool_name = event.get("tool_name", "")

    prompt = f"""Summarize this agent event in exactly 15 words or less.
Be specific and actionable.

Event Type: {event_type}
Tool: {tool_name}
Data: {json.dumps(event)[:500]}

Summary:"""

    response = await claude.complete(
        prompt,
        model="claude-3-haiku",
        max_tokens=50
    )
    return response.strip()
```

### Summary Examples

| Event | Summary |
| --- | --- |
| Write to app.py | "Created app.py with Flask application entry point and route definitions" |
| Read tests/*.py | "Read 5 test files to understand existing test patterns and coverage" |
| Bash: npm install | "Installed 47 npm dependencies including React and TypeScript" |
| ThinkingBlock | "Analyzing database schema to determine optimal query structure" |

## Event Logging to Database

```python
async def log_event(event: ADWEvent):
    await db.execute("""
        INSERT INTO agent_logs
        (agent_id, adw_id, step, event_type, summary, payload, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, NOW())
    """,
        event.agent_id,
        event.adw_id,
        event.step,
        event.type,
        event.summary,
        json.dumps(event.payload)
    )
```

## Filtering and Querying

### By Event Type

```python
async def get_tool_events(adw_id: str) -> list[ADWEvent]:
    return await db.fetch_all("""
        SELECT * FROM agent_logs
        WHERE adw_id = $1 AND event_type IN ('PreToolUse', 'PostToolUse')
        ORDER BY created_at
    """, adw_id)
```

### By Step

```python
async def get_step_events(adw_id: str, step: str) -> list[ADWEvent]:
    return await db.fetch_all("""
        SELECT * FROM agent_logs
        WHERE adw_id = $1 AND step = $2
        ORDER BY created_at
    """, adw_id, step)
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
| --- | --- | --- |
| No event correlation | Can't trace workflow | Use adw_id consistently |
| Missing summaries | Hard to scan logs | Always generate summaries |
| Raw payload logging | Token waste | Truncate large payloads |
| Sync broadcasting | Blocks agent | Async event dispatch |
| No event filtering | UI overwhelmed | Filter by type/step |

## Cross-References

- @websocket-architecture.md - Real-time event streaming
- @production-patterns.md - Database logging patterns
- @adw-framework.md - ADW conceptual framework

---

**Token Budget:** ~1,500 tokens
**Last Updated:** 2026-01-01

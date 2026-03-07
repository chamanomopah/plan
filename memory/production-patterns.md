# Production ADW Patterns

Patterns for deploying AI Developer Workflows in production environments with full observability and reliability.

## Production Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Production ADW Stack                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────────┐     ┌───────────────┐ │
│  │   Frontend  │◄───►│     Backend     │◄───►│   Database    │ │
│  │  (Vue/React)│     │    (FastAPI)    │     │ (PostgreSQL)  │ │
│  │             │     │                 │     │               │ │
│  │  Swimlanes  │     │  ADW Modules    │     │  Workflow     │ │
│  │  Events     │     │  WebSocket      │     │  State        │ │
│  │  Controls   │     │  Orchestrator   │     │  Logs         │ │
│  └─────────────┘     └─────────────────┘     └───────────────┘ │
│        │                     │                      │          │
│        └─────────────────────┼──────────────────────┘          │
│                              │                                  │
│                    ┌─────────▼─────────┐                       │
│                    │  Claude SDK       │                       │
│                    │  Agent Execution  │                       │
│                    └───────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Backend Structure

```text
adws/
├── adw_modules/               # Core infrastructure
│   ├── adw_agent_sdk.py       # Typed Pydantic wrapper for Claude SDK
│   ├── adw_logging.py         # Step lifecycle logging
│   ├── adw_websockets.py      # Real-time event broadcasting
│   ├── adw_summarizer.py      # AI-generated event summaries
│   └── adw_database.py        # PostgreSQL operations
│
├── adw_workflows/             # Multi-step workflow implementations
│   ├── adw_plan_build.py
│   ├── adw_plan_build_review.py
│   └── adw_plan_build_review_fix.py
│
└── adw_triggers/              # Workflow trigger mechanisms
    ├── adw_manual_trigger.py
    └── adw_scripts.py
```

## Database Schema

### Core Tables

```sql
-- Orchestrator singleton state
CREATE TABLE orchestrator_agents (
    id UUID PRIMARY KEY,
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    config JSONB
);

-- Managed agent registry
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    orchestrator_id UUID REFERENCES orchestrator_agents(id),
    name VARCHAR(255),
    status VARCHAR(50),
    model VARCHAR(100),
    project_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    context_tokens INTEGER,
    cost_usd DECIMAL(10, 6)
);

-- Event logs with AI summaries
CREATE TABLE agent_logs (
    id SERIAL PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    adw_id VARCHAR(50),
    step VARCHAR(50),
    event_type VARCHAR(50),
    summary TEXT,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE
);

-- 3-way conversation log
CREATE TABLE orchestrator_chat (
    id SERIAL PRIMARY KEY,
    orchestrator_id UUID REFERENCES orchestrator_agents(id),
    role VARCHAR(20),  -- 'user', 'orchestrator', 'agent'
    agent_id UUID,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE
);
```

## Cost Tracking

### Token Usage Schema

```python
class CostMetrics(BaseModel):
    agent_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    cost_usd: Decimal
    timestamp: datetime
```

### Per-Agent Cost Tracking

```python
async def track_cost(agent_id: str, usage: TokenUsage):
    cost = calculate_cost(usage.model, usage)
    await db.execute("""
        UPDATE agents
        SET cost_usd = cost_usd + $1,
            context_tokens = $2
        WHERE id = $3
    """, cost, usage.total_tokens, agent_id)
```

### Cost Aggregation

```python
async def get_workflow_cost(adw_id: str) -> Decimal:
    result = await db.fetch_one("""
        SELECT SUM(cost_usd) as total_cost
        FROM agents
        WHERE adw_id = $1
    """, adw_id)
    return result['total_cost']
```

## Session Management

### Session Persistence

```python
class ADWSession:
    adw_id: str
    workflow_type: str
    current_step: str
    project_path: str
    created_at: datetime
    status: str  # 'running', 'paused', 'completed', 'failed'

    async def save(self):
        await db.upsert("adw_sessions", self.dict())

    async def resume(self):
        state = await db.fetch_one(
            "SELECT * FROM adw_sessions WHERE adw_id = $1",
            self.adw_id
        )
        return ADWSession(**state)
```

### State Checkpoints

```python
async def checkpoint_step(adw_id: str, step: str, state: dict):
    await db.execute("""
        INSERT INTO adw_checkpoints (adw_id, step, state, created_at)
        VALUES ($1, $2, $3, NOW())
    """, adw_id, step, json.dumps(state))
```

## Error Recovery

### Retry Patterns

```python
class RetryConfig:
    max_attempts: int = 3
    backoff_base: float = 2.0
    max_backoff: float = 60.0

async def with_retry(func, config: RetryConfig):
    for attempt in range(config.max_attempts):
        try:
            return await func()
        except RecoverableError as e:
            if attempt == config.max_attempts - 1:
                raise
            wait = min(
                config.backoff_base ** attempt,
                config.max_backoff
            )
            await asyncio.sleep(wait)
```

### Graceful Degradation

```python
async def run_step_with_fallback(step: str, inputs: dict):
    try:
        return await run_step(step, inputs, model="sonnet")
    except ContextOverflowError:
        # Fall back to smaller context
        return await run_step(step, inputs, model="haiku")
    except APIError as e:
        if e.status == 529:  # Overloaded
            await asyncio.sleep(60)
            return await run_step(step, inputs)
        raise
```

## Observability Requirements

### What to Log

| Event | Data | Purpose |
| --- | --- | --- |
| Step Start | adw_id, step, inputs | Workflow tracking |
| Step End | adw_id, step, outputs, duration | Performance |
| Tool Use | tool_name, inputs, outputs | Debugging |
| Error | error_type, message, stack | Troubleshooting |
| Cost | tokens, model, cost_usd | Budget tracking |

### AI-Generated Summaries

Every event gets a 15-word summary via Haiku:

```python
async def summarize_event(event: ADWEvent) -> str:
    prompt = f"""Summarize this agent event in 15 words or less:
    Type: {event.type}
    Data: {event.data[:500]}
    """
    return await claude.complete(prompt, model="haiku")
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
| --- | --- | --- |
| No state persistence | Can't resume after failure | Database checkpoints |
| Missing cost tracking | Budget overruns | Track per-agent costs |
| No graceful shutdown | Lost work | Checkpoint before exit |
| Unbounded retries | Infinite loops | Max attempts with backoff |
| Missing observability | Blind debugging | Log all events |

## Cross-References

- @adw-framework.md - ADW conceptual framework
- @websocket-architecture.md - Real-time event streaming
- @hook-event-patterns.md - Event types and handling
- @three-pillars-orchestration.md - Orchestrator pattern

---

**Token Budget:** ~1,700 tokens
**Last Updated:** 2026-01-01

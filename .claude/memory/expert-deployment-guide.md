# Expert Deployment Guide

When and how to deploy different types of agent experts.

## Two Types of Agent Experts

### Codebase Experts

Experts that understand your code and help you build:

- **Scope**: One per domain (database, websocket, API, etc.)
- **Storage**: File system (YAML in repo)
- **Updates**: After code changes (via self-improve)
- **Users**: Developers and agents
- **Examples**: Database expert, WebSocket expert, Auth expert

### Product Experts

Experts that understand your users and personalize experiences:

- **Scope**: One per user
- **Storage**: Database (JSONB per user)
- **Updates**: After user actions
- **Users**: End users (through adaptive UI)
- **Examples**: Shopping preference expert, Content recommendation expert

## Decision Matrix: When to Create an Expert

### Codebase Expert Triggers

| Signal | Score | Notes |
| --- | --- | --- |
| Domain has 1000+ lines of code | +2 | Significant complexity |
| Multiple files in domain | +1 | Spread across codebase |
| Frequent changes to domain | +2 | Worth keeping expertise current |
| Critical business logic | +2 | Mistakes are costly |
| Complex patterns/conventions | +1 | Need to capture knowledge |
| Multiple developers touch it | +1 | Shared understanding valuable |
| You personally understand it well | +1 | Can validate expertise |

**Scoring:**

- 6+: Definitely create expert
- 4-5: Probably create expert
- 2-3: Consider based on pain points
- 0-1: Skip, not worth maintenance

### Product Expert Triggers

| Signal | Score | Notes |
| --- | --- | --- |
| Personalization valuable to users | +2 | Clear UX benefit |
| Rich user behavior data available | +2 | Can learn meaningfully |
| Low-latency UI required | -1 | Adds complexity |
| Privacy-sensitive domain | -1 | Requires careful handling |
| High traffic volume | +1 | Amortizes setup cost |
| Competitive differentiation | +1 | Worth investment |
| User opt-in acceptable | +1 | Simpler compliance |

**Scoring:**

- 5+: Strong candidate
- 3-4: Explore carefully
- 0-2: Probably not worth it
- Negative: Significant concerns to address first

## Codebase Expert Deployment

### Phase 1: Setup

```bash
# Create expert structure
/create-expert {domain}

# Seed initial expertise
/seed-expertise {domain} [focus-areas]

# Iterate until stable
/improve-expertise {domain} false
/improve-expertise {domain} false
# Repeat until no changes
```

### Phase 2: Integration

Add to development workflow:

```yaml
# In .claude/hooks.json or similar
post_build:
  - "/improve-expertise {domain} true"

# Or manual reminder in PR template
- [ ] Run `/improve-expertise {domain}` if domain files changed
```

### Phase 3: Usage

```bash
# Quick questions
/query-expert {domain} "How do I...?"

# Planning with expertise
/experts:{domain}:plan "Add new feature X"

# Full workflow
/experts:{domain}:plan-build-improve "Implement Y"
```

### Phase 4: Maintenance

| Trigger | Action |
| --- | --- |
| After any code change | `/improve-expertise {domain} true` |
| Weekly maintenance | `/improve-expertise {domain} false` |
| Before major planning | Validate expertise current |
| New team member | Review expertise for accuracy |

## Product Expert Deployment

### Phase 1: Infrastructure

```sql
-- Add expertise column to users table
ALTER TABLE users
ADD COLUMN expertise JSONB DEFAULT '{}';

-- Create action tracking table
CREATE TABLE user_actions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action_type VARCHAR(50),
  context JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Phase 2: Action Tracking

```typescript
// Track user actions
app.use(async (req, res, next) => {
  const action = extractAction(req);
  if (action && req.user) {
    await trackAction(req.user.id, action);
  }
  next();
});
```

### Phase 3: Expertise Updates

```typescript
// Async worker for expertise updates
async function processExpertiseQueue() {
  const job = await queue.pop();
  const expertise = await loadExpertise(job.userId);
  const updated = updateExpertise(expertise, job.action);
  await saveExpertise(job.userId, updated);
}
```

### Phase 4: Personalized UI

```typescript
// Load expertise for UI generation
async function renderPage(userId: string) {
  const expertise = await loadExpertise(userId);
  const recommendations = await generateRecommendations(expertise);
  const layout = selectLayout(expertise);
  return { recommendations, layout };
}
```

## Common Deployment Patterns

### Pattern 1: Gradual Rollout (Codebase)

```text
Week 1: Seed expertise for most critical domain
Week 2: Iterate self-improve, validate accuracy
Week 3: Integrate into workflow, team uses
Week 4: Expand to second domain
```

### Pattern 2: A/B Test (Product)

```text
Group A: Generic experience (control)
Group B: Expertise-personalized experience

Measure:
- Engagement metrics
- Conversion rates
- User satisfaction
```

### Pattern 3: Hybrid Expert

For domains that span codebase and user:

```yaml
# User has preferences that affect code behavior
user_config_expert:
  codebase_component:
    - Configuration loading
    - Feature flags
    - Permission checks
  user_component:
    - Personal preferences
    - Usage patterns
    - Feature access history
```

## Expertise Boundaries

### When to Split Experts

| Signal | Action |
| --- | --- |
| Expertise > 800 lines | Consider splitting |
| Two distinct sub-domains | Split by sub-domain |
| Different update frequencies | Separate for efficiency |
| Different access patterns | Optimize separately |

### Expert Hierarchy Example

```text
experts/
  database/           # Core database operations
  database-migrations/# Schema changes specifically
  database-perf/      # Query optimization
  api/                # HTTP endpoints
  api-auth/           # Auth-specific endpoints
```

## Troubleshooting

### Expertise Not Updating

1. Check self-improve prompt is running
2. Verify git diff shows domain changes
3. Run with `false` flag for full rescan
4. Check for YAML syntax errors

### Expertise Too Large

1. Enforce line limits strictly
2. Summarize verbose sections
3. Split into sub-experts
4. Remove low-value content

### Expertise Inaccurate

1. Run full self-improve (flag=false)
2. Manually review key sections
3. Check file paths still valid
4. Validate function names exist

### Product Expert Latency

1. Pre-compute recommendations
2. Cache hot user expertise
3. Use progressive loading UI
4. Implement tiered personalization

## Related Memory Files

- `act-learn-reuse.md`: Core pattern explanation
- `meta-prompt-patterns.md`: Template patterns
- `context-layers.md`: Context management

## Related Skills

- `agent-expert-creation`: Full setup workflow
- `product-expert-design`: User-facing experts
- `self-improve-prompt-design`: Maintenance patterns

---

**Token Budget:** ~1,707 tokens
**Last Updated:** 2025-12-15

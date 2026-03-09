# Act-Learn-Reuse Pattern

The three-step workflow that transforms generic agents into learning experts.

## The Core Problem

> "The massive problem with agents is this. Your agents forget. And that means your agents don't learn."

Every agent execution starts fresh. Without a mechanism to persist learning, agents:

- Repeat the same exploration every time
- Make the same mistakes repeatedly
- Never build expertise in a domain
- Waste tokens rediscovering information

## The Solution: Act-Learn-Reuse

```text
┌─────────────────────────────────────────────┐
│ ACT: Take useful action                     │
│      • Build a feature                      │
│      • Fix a bug                            │
│      • Answer a question                    │
│      • Generate code                        │
└──────────────────┬──────────────────────────┘
                   │ produces learnings
                   ▼
┌─────────────────────────────────────────────┐
│ LEARN: Update expertise file                │
│      • Self-improve prompt validates        │
│      • Mental model syncs with codebase     │
│      • New patterns captured                │
│      • Known issues updated                 │
└──────────────────┬──────────────────────────┘
                   │ persists knowledge
                   ▼
┌─────────────────────────────────────────────┐
│ REUSE: Read expertise first                 │
│      • Next execution loads mental model    │
│      • Faster, more confident execution     │
│      • Builds on previous learning          │
│      • Continuous improvement loop          │
└─────────────────────────────────────────────┘
```

## Key Components

### Expertise File (Mental Model)

The expertise file is the agent's working memory:

- **Format**: YAML, JSON, or TOML
- **Size**: 300-1000 lines (enforced limit)
- **Content**: Domain knowledge, patterns, operations, issues
- **NOT source of truth**: Validates against codebase

### Self-Improve Prompt

The prompt that teaches agents HOW to learn:

- Runs after every ACT step
- Validates expertise against codebase
- Updates mental model with discoveries
- Enforces line limits
- Maintains accuracy over time

### Question/Plan Prompts (REUSE)

Prompts that leverage expertise:

- Load expertise file first
- Answer questions from mental model
- Create plans grounded in domain knowledge
- Fast execution (no exploration needed)

## The Workflow in Practice

### Step 1: Create Expert

```bash
/create-expert database
```

Creates directory structure:

```text
.claude/commands/experts/database/
  expertise.yaml      # Empty, to be seeded
  question.md         # REUSE: Query expertise
  self-improve.md     # LEARN: Update expertise
  plan.md             # REUSE: Create plans
```

### Step 2: Seed Expertise

```bash
/seed-expertise database
```

Agent explores codebase and creates initial mental model.

### Step 3: Iterate Self-Improve

```bash
/improve-expertise database false
```

Run until stable (no changes detected). This validates and refines the initial seed.

### Step 4: Use the Expert

```bash
/query-expert database "How does connection pooling work?"
```

Agent answers from expertise - fast, confident, grounded.

### Step 5: After Code Changes (ACT)

After making changes to database code:

```bash
/improve-expertise database true
```

Uses git diff to efficiently update only affected areas.

## Critical Distinctions

| Aspect | Mental Model (Expertise) | Source of Truth (Code) |
| --- | --- | --- |
| Purpose | Fast reference | Actual implementation |
| Updates | Self-improve prompt | Human developers |
| Accuracy | Approximate, validated | Definitive |
| Size | Bounded (1000 lines) | Unbounded |
| Duplication | Acceptable (it's a cache) | Avoid |

## When to Use Agent Experts

| Scenario | Use Expert? | Why |
| --- | --- | --- |
| Evolving, complex domain | Yes | High ROI from learning |
| Stable, simple code | No | Overkill |
| Frequent changes | Yes | Self-improve keeps up |
| Rarely touched | No | Not worth maintenance |
| Critical business logic | Yes | Expertise prevents mistakes |
| Utility functions | No | Simple enough to explore |

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
| --- | --- | --- |
| Treating expertise as docs | Creates duplication | It's a mental model, not documentation |
| Manual expertise updates | Wastes human time | Self-improve prompt only |
| Skipping LEARN step | Expertise drifts | Always run after ACT |
| No line limits | Context overflow | Enforce max strictly |
| Experts for everything | Maintenance burden | Only complex, evolving domains |

## Context Protection

The plan-build-improve workflow protects top-level context:

```text
Top-Level Agent (protected)
    │
    ├──► Plan Sub-Agent (80K tokens)
    │         └──► Returns: plan.md only
    │
    ├──► Build Sub-Agent (executes plan)
    │         └──► Returns: summary + git diff
    │
    └──► Self-Improve Sub-Agent
              └──► Returns: expertise update summary
```

Each sub-agent gets full context for its task, but only summaries flow back.

## Key Quotes

> "The expertise file is the mental model of the problem space for your agent expert... This is not a source of truth. This is a working memory file, a mental model."
>
> "Don't directly update this expertise file. Teach your agents how to directly update it so they can maintain it."
>
> "True experts are always learning. They're updating their mental model."

## Related Skills

- `agent-expert-creation`: Full expert setup
- `expertise-file-design`: YAML structure patterns
- `self-improve-prompt-design`: Maintenance workflows
- `meta-agentic-creation`: Build experts that build experts

---

**Token Budget:** ~1,440 tokens
**Last Updated:** 2025-12-15

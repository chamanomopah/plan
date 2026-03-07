# Composable ADW Steps

The four workflow steps that form the backbone of AI Developer Workflows. Each step is independently runnable and chainable.

## The Four Steps

| Step | Type | Output | Purpose |
| --- | --- | --- | --- |
| `/plan` | Deterministic output | Spec file at known path | Create implementation specification |
| `/build` | Non-deterministic | Code changes | Implement based on spec |
| `/review` | Deterministic output | PASS/FAIL report | Validate implementation |
| `/fix` | Non-deterministic | Targeted fixes | Resolve review issues |

## Step Characteristics

### Deterministic Output Steps

These steps produce predictable, structured output:

**`/plan`**

- Input: Task description, issue context
- Output: `specs/{type}-{id}-{description}.md`
- Always produces a file at a known, predictable path
- Content is AI-generated, location is deterministic

**`/review`**

- Input: Implementation + original spec
- Output: Risk-tiered report (PASS/FAIL with issues)
- Structured format enables programmatic parsing
- Issues categorized by severity

### Non-Deterministic Execution Steps

These steps produce creative, adaptive output:

**`/build`**

- Input: Plan file path
- Output: Code changes, file modifications
- Full creative autonomy within plan constraints
- Commits with `build:` prefix

**`/fix`**

- Input: Review issues list
- Output: Targeted fixes addressing specific issues
- Focused scope - only what review flagged
- Commits with `fix:` prefix

## Step Isolation Principle

> "Each step must be runnable individually."

**Why Isolation Matters:**

- Debug failures at specific step
- Re-run failed steps without full workflow
- Test steps independently
- Compose different workflow variations

**Isolation Requirements:**

```text
┌────────────────────────────────────────────────────┐
│ Each step MUST:                                    │
├────────────────────────────────────────────────────┤
│ • Accept inputs via arguments or file paths        │
│ • Produce outputs to known locations               │
│ • Be executable standalone                         │
│ • Not depend on workflow context                   │
│ • Complete or fail cleanly (no partial states)     │
└────────────────────────────────────────────────────┘
```

## Workflow Compositions

### plan_build

Simplest composition - plan and implement.

```text
/plan → specs/plan.md → /build → Code changes
```

**Use when:**

- High confidence in straightforward tasks
- Fast iteration needed
- Chore-type work

### plan_build_review

Adds quality gate before completion.

```text
/plan → specs/plan.md → /build → /review → PASS/FAIL
```

**Use when:**

- Medium complexity features
- Quality validation needed
- Building trust in workflow

### plan_build_review_fix

Full autonomous cycle with self-correction.

```text
/plan → specs/plan.md → /build → /review → [if FAIL] → /fix → [loop until PASS]
```

**Use when:**

- Complex features
- Full ZTE (Zero-Touch Engineering) desired
- High stakes implementations

## Step Interface Contracts

### /plan Contract

```yaml
inputs:
  task_description: string      # What to implement
  issue_context: string?        # GitHub issue body, etc.
  project_path: string          # Where to work

outputs:
  spec_file_path: string        # Path to generated spec
  success: boolean
```

### /build Contract

```yaml
inputs:
  plan_path: string             # Path to spec file
  project_path: string          # Where to work

outputs:
  files_changed: list[string]   # Modified files
  commit_hash: string?          # If committed
  success: boolean
```

### /review Contract

```yaml
inputs:
  project_path: string          # Where to review
  spec_path: string?            # Original spec for comparison

outputs:
  status: "PASS" | "FAIL"
  issues: list[Issue]           # If FAIL
  severity: "low" | "medium" | "high" | "critical"
  success: boolean
```

### /fix Contract

```yaml
inputs:
  issues: list[Issue]           # From review output
  project_path: string

outputs:
  fixes_applied: list[string]   # What was fixed
  success: boolean
```

## Error Handling Between Steps

### Failure Modes

| Step | Failure Type | Recovery Action |
| --- | --- | --- |
| /plan | Can't generate spec | Retry with more context |
| /build | Build errors, tests fail | Return to /plan for refinement |
| /review | Critical issues found | Proceed to /fix |
| /fix | Can't fix issue | Escalate to human |

### Loop Limits

Prevent infinite fix loops:

```python
MAX_FIX_ATTEMPTS = 3

for attempt in range(MAX_FIX_ATTEMPTS):
    review = await run_review()
    if review.status == "PASS":
        break
    await run_fix(review.issues)
else:
    escalate_to_human("Max fix attempts reached")
```

## Success Criteria Per Step

### /plan Success

- [ ] Spec file created at expected path
- [ ] Spec includes clear acceptance criteria
- [ ] Scope is bounded and achievable
- [ ] Technical approach defined

### /build Success

- [ ] All spec requirements addressed
- [ ] Code compiles/passes linting
- [ ] Tests pass (if tests exist)
- [ ] Changes committed

### /review Success

- [ ] All code reviewed against spec
- [ ] Issues categorized by severity
- [ ] Clear PASS/FAIL determination
- [ ] Actionable issue descriptions

### /fix Success

- [ ] All flagged issues addressed
- [ ] No new issues introduced
- [ ] Changes committed

## Orchestration Pattern

```python
async def plan_build_review_fix(task: str, project_path: str):
    # Step 1: Plan (deterministic file output)
    plan_path = await run_step("/plan", task, project_path)

    # Step 2: Build (non-deterministic, creative)
    await run_step("/build", plan_path, project_path)

    # Step 3: Review (deterministic PASS/FAIL output)
    review = await run_step("/review", project_path)

    # Step 4: Fix if needed (non-deterministic)
    if review.status == "FAIL":
        await run_step("/fix", review.issues, project_path)
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
| --- | --- | --- |
| Monolithic steps | Can't isolate failures | Split into focused steps |
| Unbounded loops | Infinite fix attempts | Set MAX_FIX_ATTEMPTS |
| Missing contracts | Unpredictable I/O | Define explicit interfaces |
| Coupled steps | Can't run independently | Pass data via files |
| No observability | Can't debug failures | Log step start/end/result |

## Cross-References

- @composable-primitives.md - General primitive concepts
- @adw-anatomy.md - ADW structure and phases
- @validation-commands.md - Review patterns
- @plan-format-guide.md - Spec file structure

---

**Token Budget:** ~1,650 tokens
**Last Updated:** 2026-01-01

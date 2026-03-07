# Automated Implementation Workflow Hooks

## Overview

This document describes 4 hooks that create an automated implementation verification workflow. These hooks work together to form a continuous loop that validates implementation against specifications, creates patches for issues found, and implements fixes.

**Problem Solved**: LLMs have context limitations that make it difficult to implement complex plans in a single session. This workflow breaks down the implementation into iterative cycles, with each cycle validating progress and making targeted fixes.

## Workflow Architecture

The hooks implement a 4-phase loop:

```
┌─────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION LOOP                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────┐ │
│   │  TEST    │───▶│  REVIEW  │───▶│  PATCH   │───▶│ IMPLE │ │
│   │          │    │          │    │          │    │  MENT │ │
│   └──────────┘    └──────────┘    └──────────┘    └───────┘ │
│       │              │              │              │       │
│       ▼              ▼              ▼              ▼       │
│   Validate       Compare        Create         Execute    │
│   functionality  against spec   targeted       patch plan  │
│                                  fixes                      │
│       │                                              │      │
│       └──────────────────────────────────────────────┘      │
│                    (if fixes needed)                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

Add this to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "type": "command",
        "matcher": "user_exit|completion",
        "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/run-workflow.sh\" test",
        "description": "Run test suite when session ends to validate implementation",
        "async": true,
        "timeout": 300
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "matcher": "Skill",
        "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/run-workflow.sh\"",
        "description": "Trigger automated workflow after command execution",
        "async": true,
        "timeout": 180
      }
    ]
  }
}
```

## Hook 1: Test Hook (TEST)

**Event**: `SessionEnd`
**Purpose**: Run test suite when session ends to validate implementation

**Behavior**:
- Fires when Claude session ends (user exit or completion)
- Executes `/test` command to run all validation tests
- Captures test results in JSON format
- Stores results in `.claude/workflow/last-test-output.json`

**Integration**: Part of the automated workflow loop - always the first phase after implementation

## Hook 2: Review Hook (REVIEW)

**Event**: `PostToolUse` (after `/test` completes)
**Purpose**: Compare implementation against specification to verify alignment

**Behavior**:
- Triggers after test command completes successfully
- Executes `/review` command with the spec file
- Captures review findings (blockers, tech_debt, skippable issues)
- Stores results in `.claude/workflow/last-review-output.json`

**Decision Logic**:
- If `success: true` (no blockers) → Workflow complete
- If `success: false` (blockers found) → Proceed to PATCH phase

## Hook 3: Patch Hook (PATCH)

**Event**: `PostToolUse` (after `/review` finds blockers)
**Purpose**: Create minimal surgical patch plan for targeted fixes

**Behavior**:
- Triggers when review finds blocker issues
- Extracts first blocker issue from review output
- Executes `/patch` command with the issue description
- Creates patch plan file (e.g., `specs/patch/patch-fix-button-disabled-state.md`)
- Stores patch path in `.claude/workflow/current-patch.txt`

**Scope Guidelines**:
- Keep changes minimal (1-50 lines preferred)
- Only fix the specific issue reported
- Don't refactor or add unrelated improvements

## Hook 4: Implement Hook (IMPLEMENT)

**Event**: `PostToolUse` (after `/patch` creates plan)
**Purpose**: Execute the patch/plan to implement fixes

**Behavior**:
- Triggers when patch plan is created
- Reads patch plan file path from workflow state
- Executes `/implement` command with the plan file
- Applies changes to codebase
- Stores implementation output in `.claude/workflow/last-implement-output.txt`

**After Implementation**:
- Returns to TEST phase to validate changes
- Continues loop until review passes with no blockers

## Workflow State Management

The workflow maintains state in `.claude/workflow/state.json`:

```json
{
  "iteration": 0,
  "current_step": "test",
  "last_result": null,
  "loop_count": 0
}
```

**State Fields**:
- `iteration`: Total number of workflow cycles run
- `current_step`: Current phase in the loop (test, review, patch, implement)
- `last_result`: Result of last executed step
- `loop_count`: Number of complete loops executed

## Exit Conditions

The workflow terminates successfully when:

1. **TEST passes**: All validation tests pass
2. **REVIEW passes**: No blocker issues found
3. **Loop limit reached**: Maximum loops (default: 10) exceeded

**Loop Limit**: Prevents infinite loops when issues cannot be automatically resolved. Requires manual intervention when limit is reached.

## Logging and Debugging

All workflow execution is logged to `.claude/workflow/workflow.log`:

```
[2026-03-05 14:32:15] [INFO] 🚀 Starting Automated Workflow (max loops: 10)
[2026-03-05 14:32:15] [INFO] Starting from step: test
[2026-03-05 14:32:16] [INFO] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2026-03-05 14:32:16] [INFO] Loop iteration: 1/10
[2026-03-05 14:32:16] [INFO] 🧪 Starting TEST phase...
[2026-03-05 14:32:20] [SUCCESS] ✅ All tests passed!
[2026-03-05 14:32:20] [INFO] 🔍 Starting REVIEW phase...
[2026-03-05 14:32:25] [WARNING] ⚠️  Review found blockers - proceeding to patch
[2026-03-05 14:32:25] [INFO] 🩹 Starting PATCH phase...
[2026-03-05 14:32:30] [SUCCESS] ✅ Patch plan created: specs/patch/patch-fix-validation.md
[2026-03-05 14:32:30] [INFO] 🔨 Starting IMPLEMENT phase...
[2026-03-05 14:32:45] [SUCCESS] ✅ Implementation completed
[2026-03-05 14:32:45] [INFO] 🔄 Continuing to next loop...
```

## File Structure

```
.claude/
├── hooks/
│   ├── run-workflow.sh          # Main workflow orchestrator
│   ├── test-hook.sh             # Test phase hook
│   ├── review-hook.sh           # Review phase hook
│   ├── patch-hook.sh            # Patch phase hook
│   └── implement-hook.sh        # Implement phase hook
├── workflow/
│   ├── state.json               # Current workflow state
│   ├── workflow.log             # Execution log
│   ├── last-test-output.json    # Test results
│   ├── last-review-output.json  # Review findings
│   ├── last-patch-output.txt    # Patch plan path
│   └── last-implement-output.txt # Implementation summary
├── commands/
│   ├── implement.md             # Implement command
│   ├── test.md                  # Test command
│   ├── review.md                # Review command
│   └── patch.md                 # Patch command
└── settings.json                # Hook configurations
```

## Usage Examples

**Manual Workflow Trigger**:
```bash
# Start workflow from test phase
bash .claude/hooks/run-workflow.sh test

# Start from specific phase
bash .claude/hooks/run-workflow.sh review

# Set maximum loops
bash .claude/hooks/run-workflow.sh test 5
```

**View Current State**:
```bash
cat .claude/workflow/state.json
```

**View Logs**:
```bash
tail -f .claude/workflow/workflow.log
```

## Benefits

1. **Context Management**: Breaks complex implementations into manageable chunks
2. **Continuous Validation**: Every change is automatically tested and reviewed
3. **Targeted Fixes**: Patches address specific issues without scope creep
4. **Audit Trail**: Complete history of all workflow executions
5. **Non-Blocking**: Async hooks don't interrupt Claude's workflow
6. **Self-Correcting**: Automatically iterates until all blockers resolved

## Configuration Requirements

**Minimum Requirements**:
- Bash shell available
- `jq` for JSON parsing
- `claude` CLI available in PATH
- `.claude/commands/` directory with test, review, patch, implement commands

**Optional**:
- `notify-send` or similar for desktop notifications
- Custom test runners configured in project

## Troubleshooting

**Workflow not starting**:
- Check `.claude/workflow/workflow.log` for errors
- Verify all hook scripts are executable (`chmod +x`)
- Ensure `jq` is installed: `jq --version`

**Infinite loops**:
- Check `loop_count` in `state.json`
- Manual intervention required after max loops (default: 10)
- Review blockers in `last-review-output.json`

**Tests failing**:
- Check `last-test-output.json` for specific failures
- Manual fixes may be required for systemic issues

**Patch not applying**:
- Verify patch plan exists in `specs/patch/`
- Check `last-patch-output.txt` for patch path
- Manual intervention may be required for complex issues

## Implementation Details

The workflow orchestrator (`.claude/hooks/run-workflow.sh`) handles:

1. **State Persistence**: Saves/loads workflow state between executions
2. **Error Handling**: Gracefully handles failures at each phase
3. **Loop Control**: Prevents infinite loops with configurable maximum
4. **Logging**: Comprehensive logging of all operations
5. **JSON Parsing**: Extracts structured data from command outputs

Each phase is implemented as a separate function:
- `run_test()`: Executes test command and parses JSON output
- `run_review()`: Executes review command and checks for blockers
- `run_patch()`: Creates patch plan from review issues
- `run_implement()`: Applies patch/plan to codebase

The main `run_workflow()` function orchestrates the loop:
1. Load current state
2. Determine starting phase
3. Execute each phase sequentially
4. Check completion criteria
5. Either exit or continue to next loop

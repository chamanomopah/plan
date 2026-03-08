# E2E Test Auto-Generation

## Overview

Automatic E2E test generation based on implemented plan analysis following Zero-Touch Engineering (ZTE) principles.

## New Approach (v2.0.0)

Instead of asking users what feature to test, the `/e2e-test-design` command now:

1. **Receives the plan** (already implemented spec file)
2. **Detects project structure** automatically
3. **Generates N tests** based on actual testing needs
4. **Returns ONLY count + file paths** (no emojis, no explanations)

## Workflow Integration

```text
Plan → Implement → /e2e-test-design [spec] → N tests → /test-e2e [each] → Validation
```

## Test Generation Logic

### By Plan Type

**Chore Plans:**
- 1-2 validation tests
- Focus on step verification
- Test affected functionality

**Bug Plans:**
- 2-3 tests
- Reproduction scenario
- Fix verification
- Regression prevention

**Feature Plans:**
- 3+ tests
- Complete user journeys
- Acceptance criteria coverage
- Edge cases and error handling
- Integration points

### Auto-Detection

The command automatically detects:
- Routes and URLs from implementation
- Components that need testing
- API endpoints for validation
- Data flow through application
- User interaction touchpoints

## Output Structure

```
.claude/
  e2e-tests/
    [plan-name]/
      01-[test-name].md
      02-[test-name].md
      ...
      test-summary.json
```

## Usage

```bash
# Generate tests from implemented plan
/e2e-test-design specs/feature-user-authentication.md

# Execute all generated tests
/test-e2e .claude/e2e-tests/feature-user-authentication/

# Execute specific test
/test-e2e .claude/e2e-tests/feature-user-authentication/01-user-login.md
```

## Return Format

```
5 test cases created

.claude/e2e-tests/feature-example/01-main-journey.md
.claude/e2e-tests/feature-example/02-error-handling.md
.claude/e2e-tests/feature-example/03-edge-cases.md
.claude/e2e-tests/feature-example/04-integration.md
.claude/e2e-tests/feature-example/05-regression.md
```

**NO emojis, NO explanations, NO summaries.** Just count + file paths.

## ZTE Alignment

This approach supports Zero-Touch Engineering progression:
- **In-Loop**: Manual test creation (v1.0.0)
- **Out-Loop**: Automatic generation, manual review (v2.0.0)
- **Zero-Touch**: Auto-generation + auto-execution (future)

## Related Files

- `.claude/commands/e2e-test-design.md` - Test generator command
- `.claude/commands/test-e2e.md` - Test execution command
- `memory/plan-format-guide.md` - Plan structure reference
- `C:\.nero\docs\tac\memory\zte-progression.md` - ZTE methodology

## Version History

- **v2.0.0** (2025-03-07): Automatic test generation from plan analysis
- **v1.0.0** (2025-12-26): Manual test design approach
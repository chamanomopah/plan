---
name: e2e-test-design
description: Automatically analyze implemented plan and generate comprehensive E2E tests. Use after implementation to create validation tests based on specs/plan analysis.
argument-hint: [spec-file-path]
allowed-tools: Read, Grep, Glob, Write
---

# E2E Test Design Generator

Automatically analyze implemented plan and generate comprehensive E2E tests based on spec file analysis.

**OUTPUT REQUIREMENT: Return ONLY count + file paths. No emojis, no explanations, no summaries.**

Example output:
```
5 test cases created

.claude/e2e-tests/plan-name/01-test.md
.claude/e2e-tests/plan-name/02-test.md
```

## Variables

- `spec_file`: $1 - Path to the spec/plan file to analyze (default: searches specs/ directory)

## Instructions

1. **Locate and Read Spec File**: Load the spec file to understand what was implemented
2. **Analyze Implementation**: Detect project structure and identify what needs testing
3. **Generate Test Strategy**: Create comprehensive E2E tests based on implementation analysis
4. **Create Test Files**: Generate individual test files for each user journey
5. **Report Results**: Return ONLY count + file paths (no emojis, no explanations)

## Auto-Analysis Process

### 1. Spec Analysis

When executed, automatically:

1. **Read the spec file** to understand:
   - Plan type (Chore, Bug, or Feature)
   - User stories and requirements
   - Implementation details
   - Relevant files and changes
   - Acceptance criteria

2. **Detect project structure**:
   - Technology stack (web, mobile, API, etc.)
   - Testing frameworks available
   - Entry points and routes
   - Key components and interactions

3. **Generate test strategy** based on:
   - **Chore plans**: Focus on validation tests for maintenance changes
   - **Bug plans**: Focus on regression and reproduction scenario tests
   - **Feature plans**: Focus on complete user journey and acceptance criteria tests

### 2. Test Generation Logic

For each plan type, generate appropriate E2E tests:

**Chore Plans:**
- Validation tests for each step in "Step by Step Tasks"
- Regression tests for affected functionality
- Performance verification if applicable

**Bug Plans:**
- Reproduction test matching "Steps to Reproduce"
- Fix verification test
- Regression tests for related functionality

**Feature Plans:**
- Complete user journey tests for each user story
- Individual component/feature tests
- Edge case and error handling tests
- Integration tests based on "Testing Strategy"

### 3. Test Creation

Create individual test files following this structure:

```markdown
# E2E Test: [Test Name]

## User Story
[From spec or derived from implementation]

## Test Environment
- Base URL: [Detected or default]
- Test Data: [Generated test data]

## Test Steps
1. [Specific step with verification points]
2. **Verify** [Expected state]
3. [Continue steps...]

## Success Criteria
- [ ] [Criterion 1 - from acceptance criteria]
- [ ] [Criterion 2]
- [ ] [Continue criteria]

## Expected Output
{
  "test_name": "[Test Name]",
  "status": "passed|failed",
  "screenshots": ["screenshots/[test-name]/..."],
  "error": null
}
```

### 4. Output Organization

Create tests in organized structure:

```
.claude/
  e2e-tests/
    [plan-name]/
      01-[test-name].md
      02-[test-name].md
      ...
      test-summary.json
```

## Test Coverage Matrix

Generate tests based on plan complexity:

| Plan Type | Min Tests | Focus Areas |
|-----------|-----------|-------------|
| **Chore** | 1-2 | Step validation, affected areas |
| **Bug** | 2-3 | Reproduction, fix verification, regression |
| **Feature** | 3+ | User journeys, acceptance criteria, edge cases |

## Required Output Format

**CRITICAL**: After generating tests, return ONLY:

```
[N] test cases created

.claude/e2e-tests/[plan-name]/01-[test-name].md
.claude/e2e-tests/[plan-name]/02-[test-name].md
.claude/e2e-tests/[plan-name]/03-[test-name].md
```

**NO emojis, NO explanations, NO summaries.** Just count + file paths.

## Internal Output Format (JSON)

For internal processing, also generate JSON summary:

```json
{
  "plan_analyzed": "specs/feature-example.md",
  "plan_type": "Feature",
  "tests_created": 5,
  "test_files": [
    ".claude/e2e-tests/feature-example/01-main-user-journey.md",
    ".claude/e2e-tests/feature-example/02-error-handling.md",
    ".claude/e2e-tests/feature-example/03-edge-cases.md",
    ".claude/e2e-tests/feature-example/04-integration.md",
    ".claude/e2e-tests/feature-example/05-regression.md"
  ],
  "coverage_summary": {
    "user_stories": 2,
    "acceptance_criteria": 8,
    "edge_cases": 3,
    "integration_points": 2
  },
  "next_steps": [
    "Review generated tests for completeness",
    "Run tests using: /test-e2e [test-file]",
    "Execute all tests: /test-e2e .claude/e2e-tests/[plan-name]/"
  ]
}
```

## Auto-Detection Heuristics

When analyzing the spec:

1. **URL/Route Detection**: Look for routes in "Relevant Files" and implementation
2. **Component Detection**: Identify UI components that need testing
3. **API Detection**: Find API endpoints that need validation
4. **Data Flow**: Trace data movement through the application
5. **User Touchpoints**: Identify all user interaction points

## Example Workflow

```bash
# User executes command
/e2e-test-design specs/feature-user-authentication.md

# Command automatically:
1. Reads spec/feature-user-authentication.md
2. Detects it's a Feature plan with authentication flows
3. Identifies routes: /login, /register, /logout
4. Detects components: LoginForm, RegisterForm
5. Generates comprehensive E2E tests
6. Returns concise output:

# Output:
5 test cases created

.claude/e2e-tests/feature-user-authentication/01-user-login.md
.claude/e2e-tests/feature-user-authentication/02-user-registration.md
.claude/e2e-tests/feature-user-authentication/03-password-reset.md
.claude/e2e-tests/feature-user-authentication/04-session-management.md
.claude/e2e-tests/feature-user-authentication/05-error-handling.md
```

## Integration with Testing Commands

Generated tests are compatible with:

- `/test-e2e [test-file]` - Execute individual test
- `/test-e2e [directory]` - Execute all tests in directory
- `/resolve-failed-e2e-test [result]` - Fix failed tests

## Memory References

- @plan-format-guide.md - Understanding plan structures
- @zte-progression.md - Zero-Touch Engineering methodology
- @test-e2e.md - E2E test execution command
- @resolve-failed-e2e-test.md - Failed test resolution

## Version History

- **v2.0.0** (2025-03-07): Complete rewrite for automatic test generation based on plan analysis
- **v1.0.0** (2025-12-26): Initial manual design approach

---

## Last Updated

**Date:** 2025-03-07
**Model:** claude-sonnet-4-6
**Approach:** Automatic test generation from implemented plans

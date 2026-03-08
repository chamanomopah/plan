---
description: Analyze a failed E2E test, fix the underlying issue, and verify the fix. Use after /test-e2e reports failures.
argument-hint: [test-result-json]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Resolve Failed E2E Test

Analyze a failed E2E test, fix the underlying issue, and verify the fix.

## Variables

- `test_result`: $ARGUMENTS - JSON object from /test-e2e command with failed test details

## Input Format

Expects a JSON object from the /test-e2e command:

```json
{
  "test_name": "Basic Query Execution",
  "status": "failed",
  "screenshots": [
    "screenshots/01_initial_state.png",
    "screenshots/02_query_input.png"
  ],
  "error": "Step 8 failed: Results did not appear within 5 seconds"
}
```

## Instructions

### 1. Validate Test Status (100% Required)

**CRITICAL**: This command accepts ONLY 100% test completion as success.

Check the test result for completion percentage:
- If `status` shows "passed" but completion is < 100% (e.g., "8/9 steps" or "91%"), **TREAT AS FAILED**
- Partial success = FAILURE. All steps must pass.
- Any console errors (even "non-blocking") = FAILURE
- Any missing functionality = FAILURE

**100% Requirement:**
- ✅ ALL test steps must pass
- ✅ NO console errors (404s, warnings, etc.)
- ✅ ALL functionality working perfectly
- ✅ Screenshots must show complete, correct UI state

If test is < 100% complete, proceed to analyze the gaps.

### 2. Analyze the E2E Failure

Review the test result:

- **test_name**: Which user journey needs analysis
- **status**: Current completion status (treat < 100% as failed)
- **error**: The specific step that failed or any gaps
- **screenshots**: Visual evidence of state at failure
- **console_errors**: Any console errors, warnings, or 404s

Extract key information:

- Which step(s) failed or are incomplete
- What was the expected behavior (100% functionality)
- What actually happened (gaps, errors, issues)
- Visual clues from screenshots
- Console errors or warnings

### 2. Locate the Test Specification

Read the original test specification to understand:

- The full user story
- All test steps
- Success criteria
- Context around the failing step

### 3. Analyze Screenshots for Issues

**MANDATORY**: Always analyze screenshots, even for "passing" tests.

Review captured screenshots to:

- **Compare against expected UI state** - Is everything rendered correctly?
- **Identify visual anomalies** - Misaligned elements, missing components, wrong colors
- **Check for error messages on screen** - Any error toasts, modals, or inline errors
- **Verify UI completeness** - All buttons, inputs, and elements present and visible
- **Look for console errors visible in UI** - Error boundaries, error states
- **Check for loading states** - Indicators of incomplete functionality
- **Verify responsive layout** - Elements properly positioned and sized

**Screenshot Analysis Checklist:**
- [ ] All expected UI elements present
- [ ] No visual errors or broken components
- [ ] No error messages visible
- [ ] Layout appears correct
- [ ] No loading spinners stuck
- [ ] Text/content is correct
- [ ] No console errors visible in DevTools (if shown)

### 4. Investigate All Errors

**CRITICAL**: Investigate ALL errors, including "non-blocking" ones:

- **Console 404 errors** - Missing files, wrong paths, failed resource loads
- **Console warnings** - Deprecated APIs, missing resources, potential issues
- **JavaScript errors** - Any runtime exceptions
- **Network errors** - Failed API calls, timeout issues
- **Missing functionality** - Features not working as expected

**Error Investigation Steps:**
1. Check browser console for all errors/warnings
2. Review network tab for failed requests
3. Check server logs for backend errors
4. Verify all static resources load correctly
5. Test functionality manually to reproduce issues

**NO error is "non-blocking"** - All must be fixed for 100% completion.

### 5. Identify Root Cause

Common E2E failure causes:

| Symptom | Likely Cause |
| --- | --- |
| Element not found | Selector changed, slow load |
| Wrong text | Logic error, data issue |
| Timeout | Performance issue, missing element |
| Unexpected redirect | Auth issue, error state |
| Missing element | Component not rendering |

### 6. Fix the Issue

Apply fixes based on root cause:

- **UI issue**: Fix component rendering, layout, or visual elements
- **Logic issue**: Fix business logic
- **Timing issue**: Add proper waits/loading states
- **Data issue**: Fix data handling
- **Console error**: Fix missing files, wrong paths, failed resource loads
- **Network error**: Fix API calls, timeouts, or backend issues
- **Missing functionality**: Implement incomplete features

**IMPORTANT**:
- Fix the application, not the test (unless test is genuinely incorrect)
- Fix ALL errors, including "non-blocking" ones
- Continue fixing until 100% completion achieved

### 7. Re-run E2E Test

Execute the original E2E test again:

```text
/test-e2e {original_test_file}
```

**Success criteria (STRICT)**:
- ✅ ALL test steps must pass (100%)
- ✅ NO console errors
- ✅ NO console warnings
- ✅ ALL functionality working perfectly
- ✅ Screenshots show complete, correct UI state

**If test shows < 100% or any errors**: Continue fixing and retrying.

### 8. Verify No Regressions

Run related E2E tests to ensure fix doesn't break other flows.

## Output Format

Report your resolution:

```markdown
## E2E Resolution Complete

### Failure Analysis
- **Test**: {test_name}
- **Failed Step**: [step number and description]
- **Root Cause**: [what caused the failure]
- **Screenshot Evidence**: [observations from screenshots]

### Fix Applied
- **File(s) Modified**: [list of files]
- **Change Summary**: [brief description]
- **Type of Fix**: [UI/Logic/Performance/Data]

### Validation
- **E2E Test**: PASS (100% - ALL steps complete)
- **Console Errors**: NONE
- **Console Warnings**: NONE
- **Screenshots Analysis**: ALL checks passed
- **Related Tests**: PASS/FAIL
- **New Screenshots**: [paths to verification screenshots]

**Completion**: Must be 100% - all steps passing, no errors, no warnings

### Notes
[Any observations or recommendations]
```

## Retry Logic

**CONTINUE UNTIL 100% ACHIEVED**

If the fix doesn't achieve 100%:

1. Review new screenshots for clues
2. Consider timing/async issues
3. Check for environment-specific problems
4. Apply alternative fix
5. Investigate console errors/warnings
6. Fix missing functionality
7. **Repeat until 100% completion**

**NO MAXIMUM RETRIES** - Continue fixing until:
- ✅ ALL test steps pass (100%)
- ✅ NO console errors
- ✅ NO console warnings
- ✅ ALL functionality working perfectly

**Required Analysis**:
- Always analyze screenshots for any issues
- Always check console for errors/warnings
- Always verify all functionality works
- Never accept "good enough" or "non-blocking" issues

**Persistence**: Keep fixing and re-testing until 100% achieved.

## Integration with Closed Loop

This command is the **RESOLVE** phase for E2E:

```text
/test-e2e {spec} → [failure JSON] → /resolve-failed-e2e-test {result} → /test-e2e
                                                                            ↓
                                                                     [verify fix]
```

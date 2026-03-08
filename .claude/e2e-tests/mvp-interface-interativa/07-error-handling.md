# E2E Test: Error Handling and Edge Cases

## User Story
As a user, I want the system to handle errors gracefully and show clear error messages when something goes wrong.

## Test Environment
- Base URL: http://localhost:8000
- Test Data: Various edge case scenarios

## Test Steps

### Test Case 1: Server Not Running

1. **Test interface when server is down**
   - Stop FastAPI server
   - Try to open `http://localhost:8000`
   - **Verify** Browser shows connection refused or similar error
   - **Verify** Clear error message explains server is not running
   - Start server
   - **Verify** Interface loads successfully

### Test Case 2: Invalid File Path

2. **Test accessing non-existent file**
   - Start server and open interface
   - Select any project
   - Use browser dev tools to manually call API:
     ```
     GET /api/files/heroPage_design/nonexistent.html
     ```
   - **Verify** API returns 404 status
   - **Verify** Error message: "File not found: nonexistent.html"
   - **Verify** Interface shows user-friendly error in visualization area
   - **Verify** Error message suggests checking file list

3. **Test accessing non-existent project**
   - Manually navigate to:
     ```
     /api/projects/nonexistent_project/files
     ```
   - **Verify** API returns 404 status
   - **Verify** Error message: "Project not found: nonexistent_project"

### Test Case 3: Corrupted File Content

4. **Test malformed JSON in structured files**
   - Create file `corrupted.json` with invalid JSON:
     ```json
     {
       "type": "askQuestionTool",
       "options": [INVALID SYNTAX HERE
     }
     ```
   - Try to open `corrupted.json` in interface
   - **Verify** Error message appears: "Invalid JSON format"
   - **Verify** Error suggests validating JSON syntax
   - **Verify** Interface does not crash
   - **Verify** User can still navigate to other files

5. **Test unsupported file type**
   - Create file `unsupported.xyz` with binary content
   - Try to open `unsupported.xyz`
   - **Verify** Detector returns default module: "text_editor"
   - **Verify** Content is displayed as text (may show binary characters)
   - **Verify** No crash or error occurs
   - **Verify** User can still interact with interface

### Test Case 4: Webhook Failures

6. **Test webhook unreachable**
   - Configure webhook URL: `https://this-domain-does-not-exist-12345.com/webhook`
   - Try to send command
   - **Verify** Loading state appears
   - **Verify** After timeout, error message appears
   - **Verify** Error message: "Unable to reach webhook. Check the URL."
   - **Verify** Retry button is available
   - **Verify** User can modify webhook URL and retry

7. **Test webhook returns 4xx/5xx error**
   - Configure webhook that returns 500 error
   - Try to send command
   - **Verify** Retry mechanism activates (up to 3 attempts)
   - **Verify** After retries, final error message appears
   - **Verify** Error message: "Webhook returned error 500. Please try again later."
   - **Verify** Error includes HTTP status code

8. **Test webhook timeout**
   - Configure webhook that delays response > 30 seconds
   - Try to send command
   - **Verify** Loading state appears
   - **Verify** After 30s timeout, error message appears
   - **Verify** Error message: "Webhook request timed out after 30 seconds"
   - **Verify** Retry option is available

9. **Test malformed webhook response**
   - Configure webhook that returns invalid JSON
   - Try to send command
   - **Verify** Request is sent (2xx status)
   - **Verify** Error message: "Invalid response from webhook"
   - **Verify** System logs response for debugging

### Test Case 5: WebSocket Failures

10. **Test WebSocket connection failure**
    - Start server with WebSocket endpoint disabled or blocked
    - Open interface
    - **Verify** "Disconnected" indicator appears in header
    - **Verify** Warning message: "Real-time updates unavailable"
    - **Verify** Interface still works (file viewing, webhook sending)
    - **Verify** Manual reload still works

11. **Test WebSocket disconnection during session**
    - Open interface with WebSocket connected
    - Kill server or block WebSocket port
    - **Verify** "Disconnected" indicator appears
    - **Verify** Toast notification: "Connection lost"
    - Restart server/unblock port
    - **Verify** "Reconnected" indicator appears
    - **Verify** Toast notification: "Connection restored"

12. **Test WebSocket message parsing error**
    - Send malformed message to WebSocket client from server
    - **Verify** Error is logged in console
    - **Verify** Interface does not crash
    - **Verify** User can still use interface normally

### Test Case 6: Concurrent Access Issues

13. **Test multiple users modifying same file**
    - Open interface in two browser windows
    - Both users select same file
    - User 1 sends webhook command to modify file
    - User 2 sends webhook command to modify same file
    - **Verify** Both users receive update notifications
    - **Verify** Both users see final state (last write wins)
    - **Verify** No conflict error occurs

14. **Test file locked by external process**
    - Use external process to lock file (prevent modification)
    - Try to send webhook command that would modify file
    - **Verify** Webhook is sent successfully
    - **Verify** Error appears: "Failed to modify file (file may be locked)"
    - **Verify** Original file content is preserved
    - **Verify** User is notified of the failure

### Test Case 7: Empty/Null Data

15. **Test empty file**
    - Create empty file `empty.txt`
    - Open in interface
    - **Verify** File loads successfully
    - **Verify** Empty state message: "This file is empty"
    - **Verify** Default module is used (text_editor)
    - **Verify** Sidebar shows input field for adding content

16. **Test null webhook URL**
    - Configure project with null webhook URL
    - Try to send command
    - **Verify** Error message: "No webhook URL configured"
    - **Verify** User is prompted to configure webhook URL
    - **Verify** "Configurar" button is highlighted

17. **Test missing project config**
    - Create project folder without config.json
    - Select project
    - **Verify** Project loads with default settings
    - **Verify** Files are listed correctly
    - **Verify** Global webhook is used
    - **Verify** No error occurs

### Test Case 8: Large Files

18. **Test large file handling**
    - Create large HTML file (>1MB)
    - Open in interface
    - **Verify** File loads successfully
    - **Verify** Loading indicator appears during load
    - **Verify** Preview renders correctly
    - **Verify** Performance is acceptable

19. **Test large webhook payload**
    - Select large file
    - Send webhook command
    - **Verify** Payload includes complete file content
    - **Verify** Request completes successfully
    - **Verify** No truncation occurs

### Test Case 9: Special Characters

20. **Test filenames with special characters**
    - Create file: `test file (1).html`
    - Create file: `test-file-ñoño.html`
    - **Verify** Files appear in file list
    - **Verify** Files can be opened
    - **Verify** File URLs are properly encoded

21. **Test content with special characters**
    - Create file with unicode, emojis, special chars
    - Open in interface
    - **Verify** Content displays correctly
    - **Verify** Special characters are preserved
    - **Verify** Webhook payload includes correct encoding

## Success Criteria
- [ ] Server not running shows clear error message
- [ ] Non-existent files return 404 with user-friendly error
- [ ] Corrupted/malformed files show appropriate error messages
- [ ] Unsupported file types fall back to text_editor
- [ ] Webhook unreachable errors show retry option
- [ ] Webhook errors include HTTP status codes
- [ ] Webhook timeout is handled correctly
- [ ] WebSocket disconnection shows visual indicator
- [ ] WebSocket reconnection works automatically
- [ ] Concurrent modifications don't crash system
- [ ] Empty files show empty state message
- [ ] Null webhook URL shows configuration prompt
- [ ] Missing config.json uses defaults
- [ ] Large files load with loading indicator
- [ ] Special characters in filenames work correctly
- [ ] Special characters in content are preserved

## Expected Output
{
  "test_name": "Error Handling and Edge Cases",
  "status": "passed",
  "screenshots": ["screenshots/error-handling/01-server-down.png", "screenshots/error-handling/02-file-not-found.png", "screenshots/error-handling/03-webhook-error.png", "screenshots/error-handling/04-websocket-disconnected.png", "screenshots/error-handling/05-empty-file.png"],
  "error": null
}

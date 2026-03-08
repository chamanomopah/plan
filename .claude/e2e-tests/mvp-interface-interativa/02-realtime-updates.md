# E2E Test: Real-time Updates via WebSocket

## User Story
As a user, I want to see real-time updates when files are modified, so I can immediately see changes made by AI agents.

## Test Environment
- Base URL: http://localhost:8000
- Test Data: Projects in `projetos/` directory
- Test File: projetos/heroPage_design/design.html

## Test Steps

1. **Prepare test environment**
   - Start FastAPI server
   - Open interface in two separate browser tabs/windows
   - Navigate to `http://localhost:8000` in both tabs
   - **Verify** Both tabs establish WebSocket connections
   - **Verify** Both tabs show the interface correctly

2. **Select same project and file in both tabs**
   - In Tab 1: Select "heroPage_design" project
   - In Tab 1: Click on "design.html"
   - In Tab 2: Select "heroPage_design" project
   - In Tab 2: Click on "design.html"
   - **Verify** Both tabs show the same file content
   - **Verify** Both tabs show HTML preview of design.html
   - Note the current content/state of the file

3. **Modify file externally**
   - Open `projetos/heroPage_design/design.html` in text editor
   - Make a visible change (e.g., modify text, change color)
   - Save the file
   - **Verify** File is saved successfully

4. **Verify real-time update in Tab 1**
   - **Verify** Within 500ms, Tab 1 shows a toast notification: "File updated: design.html"
   - **Verify** HTML preview in Tab 1 refreshes automatically
   - **Verify** New content is visible in visualization area
   - **Verify** File header shows updated timestamp
   - **Verify** Sidebar input is preserved (not cleared)

5. **Verify real-time update in Tab 2**
   - **Verify** Within 500ms, Tab 2 shows a toast notification: "File updated: design.html"
   - **Verify** HTML preview in Tab 2 refreshes automatically
   - **Verify** New content is visible in visualization area
   - **Verify** File header shows updated timestamp
   - **Verify** Sidebar input is preserved (not cleared)

6. **Test sidebar preservation**
   - In Tab 1: Type some text in the sidebar input field (don't send)
   - Wait for file to be modified externally again
   - **Verify** Visualization area updates with new content
   - **Verify** Sidebar input text is NOT cleared or modified
   - **Verify** User can continue typing or send the preserved input

7. **Test WebSocket reconnection**
   - In one tab, disconnect network temporarily or restart server
   - **Verify** Tab shows "Disconnected" indicator
   - Restore network or server
   - **Verify** Tab shows "Reconnected" indicator
   - **Verify** WebSocket connection is re-established automatically
   - **Verify** File content loads correctly after reconnection

8. **Test multiple file updates**
   - Modify the file 3 times in quick succession (within 1 second)
   - **Verify** Debounce mechanism prevents 3 separate updates
   - **Verify** Only 1 update notification appears after 500ms
   - **Verify** Final content reflects all 3 changes

## Success Criteria
- [ ] WebSocket connection is established automatically on page load
- [ ] Multiple tabs can connect to WebSocket simultaneously
- [ ] File modifications trigger WebSocket events within 500ms
- [ ] All connected tabs receive update notifications
- [ ] Visualization area updates automatically without page refresh
- [ ] Sidebar input is preserved during updates
- [ ] Toast notifications appear for file updates
- [ ] WebSocket reconnection works automatically after disconnect
- [ ] Debounce mechanism prevents excessive updates
- [ ] File timestamp updates correctly in header

## Expected Output
{
  "test_name": "Real-time Updates via WebSocket",
  "status": "passed",
  "screenshots": ["screenshots/realtime-updates/01-two-tabs.png", "screenshots/realtime-updates/02-toast-notification.png", "screenshots/realtime-updates/03-auto-refresh.png", "screenshots/realtime-updates/04-sidebar-preserved.png"],
  "error": null
}

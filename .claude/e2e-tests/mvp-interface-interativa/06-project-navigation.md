# E2E Test: Project Navigation and File Switching

## User Story
As a user, I want to easily navigate between projects and files, with the interface maintaining state appropriately.

## Test Environment
- Base URL: http://localhost:8000
- Test Data: Multiple projects in `projetos/` directory

## Test Steps

### Test Case 1: Project Selection

1. **Test project dropdown functionality**
   - Open interface at `http://localhost:8000`
   - Locate project selector dropdown in header (top left)
   - **Verify** Default project is selected or "Select Project" placeholder
   - Click on dropdown
   - **Verify** Dropdown shows list of available projects:
     - heroPage_design
     - qualification_questions
     - sdlcWorkflow_structure
   - **Verify** Each project shows icon (if configured in config.json)
   - **Verify** Each project shows display name

2. **Test project switching**
   - Select "heroPage_design"
   - **Verify** Sidebar updates with project files
   - **Verify** Webhook URL updates to project-specific webhook
   - **Verify** File list shows: design.html
   - Select "qualification_questions"
   - **Verify** Sidebar clears and reloads
   - **Verify** File list shows: askQuestionTool1, askQuestionToo2
   - **Verify** Webhook URL updates to qualification_questions webhook
   - Select "sdlcWorkflow_structure"
   - **Verify** Sidebar updates with project files
   - **Verify** File list shows: structure.meirmaid

### Test Case 2: File Navigation Within Project

3. **Test file selection and display**
   - Select "heroPage_design" project
   - **Verify** File list shows: design.html
   - Click on "design.html"
   - **Verify** File is highlighted as active
   - **Verify** Visualization area shows HTML preview
   - **Verify** File header shows: "design.html"
   - **Verify** File header shows file type badge

4. **Test multi-file project navigation**
   - Select "qualification_questions" project
   - **Verify** File list shows: askQuestionTool1, askQuestionToo2
   - Click on "askQuestionTool1"
   - **Verify** askQuestionTool1 is highlighted as active
   - **Verify** Visualization area shows AskQuestionTool options
   - **Verify** Sidebar shows checkboxes for askQuestionTool1
   - Click on "askQuestionToo2"
   - **Verify** askQuestionToo2 is now highlighted as active
   - **Verify** askQuestionTool1 is no longer highlighted
   - **Verify** Visualization area updates to show askQuestionToo2 content
   - **Verify** Sidebar updates to show checkboxes for askQuestionToo2
   - Click back on "askQuestionTool1"
   - **Verify** Previous file state is restored
   - **Verify** Visualization area shows askQuestionTool1 again

### Test Case 3: File State Preservation

5. **Test preserving sidebar input during file switch**
   - Select "heroPage_design" project
   - Click on "design.html"
   - Type in sidebar input: "Change header to blue"
   - Do NOT send (don't click "Enviar para Webhook")
   - Switch to "qualification_questions" project
   - Click on "askQuestionTool1"
   - Select some options
   - Switch back to "heroPage_design" project
   - Click on "design.html"
   - **Verify** Sidebar input still shows: "Change header to blue"
   - **Verify** Input was NOT cleared when switching projects
   - **Verify** User can now send the preserved input

6. **Test file modification indicator**
   - Select "qualification_questions" project
   - Note the current state of askQuestionTool1
   - Use external editor to modify askQuestionTool1 file
   - **Verify** Toast notification appears: "File updated: askQuestionTool1"
   - **Verify** File list shows "Modified" badge next to askQuestionTool1
   - **Verify** Visualization area refreshes with new content
   - Switch to askQuestionToo2
   - Switch back to askQuestionTool1
   - **Verify** "Modified" badge is still visible
   - **Verify** Latest content is displayed

### Test Case 4: Reload and Refresh

7. **Test reload button**
   - Locate reload button in header (top right)
   - Click reload button
   - **Verify** Page does NOT fully reload
   - **Verify** File list refreshes
   - **Verify** All file modification indicators are cleared
   - **Verify** WebSocket connection is verified/re-established if needed
   - **Verify** Current file content is reloaded

8. **Test browser refresh**
   - Press F5 or browser refresh button
   - **Verify** Page fully reloads
   - **Verify** WebSocket reconnects automatically
   - **Verify** Last selected project is remembered (if state persists)
   - **Verify** Last selected file is remembered (if state persists)
   - **Verify** All UI elements render correctly

### Test Case 5: Project Configuration (config.json)

9. **Test project config display**
   - Select "heroPage_design" project
   - Open `projetos/heroPage_design/config.json`
   - **Verify** config.json contains display_name, icon, webhook
   - **Verify** Project dropdown shows custom display_name if present
   - **Verify** Project dropdown shows custom icon if present
   - **Verify** Sidebar uses webhook from config.json if specified

10. **Test module overrides in config**
    - Add module override to config.json:
    ```json
    {
      "module_overrides": {
        "design.html": {
          "module": "html_preview"
        }
      }
    }
    ```
    - Reload interface
    - Click on "design.html"
    - **Verify** System uses specified module (html_preview)
    - **Verify** Detector respects module override from config

### Test Case 6: Keyboard Navigation

11. **Test keyboard shortcuts (if implemented)**
    - With file list focused:
    - Press Arrow Down
    - **Verify** Selection moves to next file
    - Press Arrow Up
    - **Verify** Selection moves to previous file
    - Press Enter
    - **Verify** Selected file opens in visualization area

12. **Test project dropdown keyboard navigation**
    - Focus on project dropdown
    - Press Arrow Down/Up
    - **Verify** Different projects are highlighted
    - Press Enter
    - **Verify** Selected project loads

## Success Criteria
- [ ] Project dropdown lists all available projects
- [ ] Switching projects updates sidebar with correct files
- [ ] File list shows all files in selected project
- [ ] Clicking file displays it in visualization area
- [ ] Active file is highlighted in file list
- [ ] File type badge displays correctly
- [ ] Sidebar input is preserved when switching files
- [ ] File modification indicator appears when file changes externally
- [ ] Reload button refreshes content without full page reload
- [ ] Browser refresh maintains state (if implemented)
- [ ] Project config.json is respected for display name and icon
- [ ] Module overrides in config.json are applied
- [ ] Keyboard navigation works (if implemented)

## Expected Output
{
  "test_name": "Project Navigation and File Switching",
  "status": "passed",
  "screenshots": ["screenshots/navigation/01-project-dropdown.png", "screenshots/navigation/02-file-list.png", "screenshots/navigation/03-file-switching.png", "screenshots/navigation/04-modified-badge.png", "screenshots/navigation/05-config-display.png"],
  "error": null
}

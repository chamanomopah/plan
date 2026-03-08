# E2E Test: File Type Detection and Module Rendering

## User Story
As a user, I want the system to automatically detect file types and render them with appropriate visualization modules.

## Test Environment
- Base URL: http://localhost:8000
- Test Data: Multiple file types in `projetos/` directory

## Test Steps

### Test Case 1: HTML File Detection

1. **Select heroPage_design project**
   - Open interface
   - Select "heroPage_design" from project dropdown
   - Click on "design.html"
   - **Verify** Detector identifies file type as "HTML"
   - **Verify** Module loaded: "html_preview"
   - **Verify** Visualization area shows: HTML preview in iframe
   - **Verify** Sidebar shows: Multi-line text input field
   - **Verify** Metadata shows: supports_edit: true

### Test Case 2: Mermaid Diagram Detection

2. **Select sdlcWorkflow_structure project**
   - Select "sdlcWorkflow_structure" from project dropdown
   - Click on "structure.meirmaid"
   - **Verify** Detector identifies file type as "Mermaid"
   - **Verify** Module loaded: "meirmaid"
   - **Verify** Visualization area shows: Rendered Mermaid diagram
   - **Verify** Diagram supports zoom and pan interactions
   - **Verify** Sidebar shows: Text input field for instructions
   - **Verify** Metadata shows: supports_edit: true

### Test Case 3: AskQuestionTool JSON Detection

3. **Select qualification_questions project**
   - Select "qualification_questions" from project dropdown
   - Click on "askQuestionTool1"
   - **Verify** Detector identifies file type as "askQuestionTool" (JSON)
   - **Verify** Module loaded: "claudeCode_askQuestionTool"
   - **Verify** Visualization area shows: Read-only list of options
   - **Verify** Sidebar shows: Interactive checkboxes/radio buttons
   - **Verify** Sidebar includes comment field
   - **Verify** Metadata shows: allow_multiple (from JSON)

### Test Case 4: Content-based Detection (No Extension)

4. **Test content detection without file extension**
   - Create new file `test_file` in any project (no extension)
   - Add HTML content: `<!DOCTYPE html><html><body>Test</body></html>`
   - Refresh file list in interface
   - Click on `test_file`
   - **Verify** Detector reads first 1024 bytes
   - **Verify** Detector identifies as HTML based on `<!DOCTYPE html>` pattern
   - **Verify** Module loaded: "html_preview"
   - **Verify** Content renders correctly

5. **Test JSON detection without extension**
   - Create file `questions` (no extension)
   - Add JSON content:
   ```json
   {
     "type": "askQuestionTool",
     "question": "Test question",
     "options": [
       {"id": "opt1", "text": "Option 1", "selected": false}
     ]
   }
   ```
   - Click on `questions` file
   - **Verify** Detector identifies as "askQuestionTool" based on JSON structure
   - **Verify** Module loaded: "claudeCode_askQuestionTool"
   - **Verify** Options render correctly

### Test Case 5: Kanban Board Detection

6. **Test Kanban module**
   - Create file `kanban.json` with:
   ```json
   {
     "type": "kanban",
     "columns": [
       {"name": "To Do", "cards": ["Task 1", "Task 2"]},
       {"name": "In Progress", "cards": ["Task 3"]}
     ]
   }
   ```
   - Click on `kanban.json`
   - **Verify** Detector identifies as "kanban"
   - **Verify** Module loaded: "kanban"
   - **Verify** Visualization area shows: Kanban board with columns and cards
   - **Verify** Sidebar shows: Input fields for adding/moving cards

### Test Case 6: TodoList Detection

7. **Test TodoList module**
   - Create file `todolist.json` with:
   ```json
   {
     "type": "todolist",
     "tasks": [
       {"id": "1", "text": "Task 1", "completed": false},
       {"id": "2", "text": "Task 2", "completed": true}
     ]
   }
   ```
   - Click on `todolist.json`
   - **Verify** Detector identifies as "todolist"
   - **Verify** Module loaded: "todolist"
   - **Verify** Visualization area shows: Task list with checkboxes
   - **Verify** Sidebar shows: Input field for adding tasks

### Test Case 7: Empty File Handling

8. **Test empty file**
   - Create empty file `empty.txt`
   - Click on `empty.txt`
   - **Verify** Detector returns default module: "text_editor"
   - **Verify** Visualization area shows: Empty text editor placeholder
   - **Verify** Sidebar shows: Text input field

## Success Criteria
- [ ] HTML files are detected and rendered with html_preview module
- [ ] Mermaid files are detected and rendered with meirmaid module
- [ ] AskQuestionTool JSON is detected and rendered with checkboxes
- [ ] Files without extension are detected by content patterns
- [ ] Kanban JSON is detected and rendered as board
- [ ] TodoList JSON is detected and rendered as task list
- [ ] Empty files default to text_editor module
- [ ] Each module renders correct visualization in main area
- [ ] Each module provides appropriate input in sidebar
- [ ] Module metadata is correct (supports_edit, content_type)

## Expected Output
{
  "test_name": "File Type Detection and Module Rendering",
  "status": "passed",
  "screenshots": ["screenshots/file-detection/01-html-preview.png", "screenshots/file-detection/02-mermaid-diagram.png", "screenshots/file-detection/03-askquestiontool.png", "screenshots/file-detection/04-kanban-board.png", "screenshots/file-detection/05-todolist.png"],
  "error": null
}

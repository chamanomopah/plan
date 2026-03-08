# E2E Test: Module-Specific Interactions

## User Story
As a user, I want each visualization module to provide appropriate interaction options based on the file type.

## Test Environment
- Base URL: http://localhost:8000
- Test Data: Various file types in `projetos/` directory

## Test Steps

### Test Case 1: HTML Preview Module

1. **Test HTML visualization**
   - Select "heroPage_design" project
   - Click on "design.html"
   - **Verify** Module: "html_preview"
   - **Verify** Visualization area: HTML rendered in iframe sandbox
   - **Verify** HTML is displayed correctly (not as source code)
   - **Verify** Iframe has sandbox attributes for security

2. **Test HTML sidebar input**
   - **Verify** Sidebar shows: Multi-line textarea
   - **Verify** Textarea accepts HTML edits or instructions
   - **Verify** Textarea has placeholder text
   - Type: "Change background color to white"
   - **Verify** Text is visible and editable
   - Click "Enviar para Webhook"
   - **Verify** Payload includes text input

### Test Case 2: Mermaid Diagram Module

3. **Test Mermaid visualization**
   - Select "sdlcWorkflow_structure" project
   - Click on "structure.meirmaid"
   - **Verify** Module: "meirmaid"
   - **Verify** Visualization area: Mermaid diagram rendered to SVG
   - **Verify** Diagram is interactive:
     - Can drag to pan
     - Can scroll to zoom
     - Can reset zoom

4. **Test Mermaid sidebar input**
   - **Verify** Sidebar shows: Text input field
   - **Verify** Placeholder: "Enter instructions for modifying diagram"
   - Type: "Add deployment step after testing"
   - **Verify** Input is accepted
   - Click "Enviar para Webhook"
   - **Verify** Payload includes instruction

### Test Case 3: AskQuestionTool Module

5. **Test AskQuestionTool visualization (read-only)**
   - Select "qualification_questions" project
   - Click on "askQuestionTool1"
   - **Verify** Module: "claudeCode_askQuestionTool"
   - **Verify** Visualization area shows:
     - Question text
     - List of options (read-only)
     - Current state of each option (selected/unselected)
     - Cannot modify options in visualization area

6. **Test AskQuestionTool sidebar input (interactive)**
   - **Verify** Sidebar shows:
     - Interactive checkboxes if `allow_multiple: true`
     - Radio buttons if `allow_multiple: false`
     - Comment text field
   - Select option 1 and option 2
   - **Verify** Checkboxes update state
   - Type in comment field: "These are high priority"
   - **Verify** Comment is accepted
   - Click "Enviar para Webhook"
   - **Verify** Payload includes:
     ```json
     {
       "user_input": {
         "type": "options",
         "data": {
           "selected_options": ["opt1", "opt2"],
           "comment": "These are high priority"
         }
       }
     }
     ```

### Test Case 4: Kanban Board Module

7. **Test Kanban visualization (read-only)**
   - Create `kanban.json` with columns and cards
   - Click on `kanban.json`
   - **Verify** Module: "kanban"
   - **Verify** Visualization area shows:
     - Columns displayed horizontally
     - Cards displayed in each column
     - Visual distinction between columns
     - Cannot drag cards in visualization area

8. **Test Kanban sidebar input**
   - **Verify** Sidebar shows:
     - "Add card" text field
     - Column selector dropdown
     - "Move card" section with card selector
     - Target column selector
   - Type "New Task" in "Add card" field
   - Select "To Do" column
   - Click "Add" button
   - **Verify** Form data is prepared for webhook
   - **Verify** Cannot directly modify board in visualization

### Test Case 5: TodoList Module

9. **Test TodoList visualization (read-only)**
   - Create `todolist.json` with tasks
   - Click on `todolist.json`
   - **Verify** Module: "todolist"
   - **Verify** Visualization area shows:
     - List of tasks
     - Checkboxes next to each task (showing completion state)
     - Strikethrough for completed tasks
     - Cannot modify tasks in visualization area

10. **Test TodoList sidebar input**
    - **Verify** Sidebar shows:
      - "Add task" text field
      - "Toggle task" dropdown with task list
    - Type "New task item" in "Add task" field
    - Click "Add" button
    - **Verify** Task data is prepared for webhook
    - Select existing task from "Toggle task" dropdown
    - Click "Toggle" button
    - **Verify** Toggle data is prepared for webhook

### Test Case 6: Form Module

11. **Test Form visualization (read-only)**
    - Create `form.json` with field definitions
    - Click on `form.json`
    - **Verify** Module: "formulario"
    - **Verify** Visualization area shows:
      - Form fields with current values
      - Read-only display of form data
      - Cannot edit fields in visualization area

12. **Test Form sidebar input**
    - **Verify** Sidebar shows:
      - Interactive form fields matching form definition
      - Text inputs for text fields
      - Dropdowns for select fields
      - Checkboxes for boolean fields
    - Fill in form fields in sidebar
    - Click "Enviar para Webhook"
    - **Verify** Payload includes:
      ```json
      {
        "user_input": {
          "type": "form",
          "data": {
            "field1": "value1",
            "field2": "value2"
          }
        }
      }
      ```

### Test Case 7: Image Preview Module

13. **Test Image visualization**
    - Add image file to project (PNG, JPG, etc.)
    - Click on image file
    - **Verify** Module: "image_preview"
    - **Verify** Visualization area shows:
      - Image rendered at appropriate size
      - Zoom controls (+/- buttons)
      - Pan functionality when zoomed
    - **Verify** Cannot modify image in visualization area

14. **Test Image sidebar input**
    - **Verify** Sidebar shows:
      - Text input for image editing instructions
    - Type: "Resize to 50% width"
    - Click "Enviar para Webhook"
    - **Verify** Payload includes instruction

### Test Case 8: Excalidraw Module

15. **Test Excalidraw visualization**
    - Create `excalidraw.json` with Excalidraw data
    - Click on `excalidraw.json`
    - **Verify** Module: "excalidraw"
    - **Verify** Visualization area shows:
      - Excalidraw diagram rendered
      - Elements displayed correctly
      - Cannot edit in visualization area

16. **Test Excalidraw sidebar input**
    - **Verify** Sidebar shows:
      - Text input for modification instructions
    - Type instruction for modifying diagram
    - Click "Enviar para Webhook"
    - **Verify** Payload includes instruction

## Success Criteria
- [ ] HTML module renders preview in iframe
- [ ] Mermaid module renders interactive diagram (zoom/pan)
- [ ] AskQuestionTool shows read-only options in visualization, interactive in sidebar
- [ ] Kanban shows read-only board in visualization, input controls in sidebar
- [ ] TodoList shows read-only tasks in visualization, input controls in sidebar
- [ ] Form shows read-only data in visualization, interactive fields in sidebar
- [ ] Image module shows zoomable image
- [ ] Excalidraw module renders diagram
- [ ] Visualization area is always read-only
- [ ] Sidebar provides appropriate input controls for each module
- [ ] All sidebar inputs correctly format webhook payload

## Expected Output
{
  "test_name": "Module-Specific Interactions",
  "status": "passed",
  "screenshots": ["screenshots/module-interactions/01-html-preview.png", "screenshots/module-interactions/02-mermaid-zoom.png", "screenshots/module-interactions/03-askquestiontool-readonly.png", "screenshots/module-interactions/04-askquestiontool-sidebar.png", "screenshots/module-interactions/05-kanban-board.png", "screenshots/module-interactions/06-todolist.png"],
  "error": null
}

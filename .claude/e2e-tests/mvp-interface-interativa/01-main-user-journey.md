# E2E Test: Main User Journey - Complete Flow

## User Story
As a user, I want to open the interface, select a project, view files, and send commands via webhook to edit the files.

## Test Environment
- Base URL: http://localhost:8000
- Test Data: Projects in `projetos/` directory
- Test Webhook: https://maceio-n8n-alfa42.serveousercontent.com/webhook/plan

## Test Steps

1. **Start the FastAPI server**
   - Run `python main.py` or `uvicorn app:app --reload`
   - **Verify** Server starts on port 8000
   - **Verify** WebSocket endpoint is available at `/ws`

2. **Open the interface in browser**
   - Navigate to `http://localhost:8000`
   - **Verify** Page loads successfully
   - **Verify** Layout shows header with project selector
   - **Verify** Sidebar is visible on the left
   - **Verify** Main visualization area is visible on the right
   - **Verify** WebSocket connection is established (check browser console)

3. **Select a project from dropdown**
   - Click on project selector dropdown in header
   - **Verify** List of available projects appears:
     - heroPage_design
     - qualification_questions
     - sdlcWorkflow_structure
   - Select "heroPage_design"
   - **Verify** Sidebar updates with project files
   - **Verify** Webhook URL for project is displayed
   - **Verify** File list shows: design.html

4. **View a file in the visualization area**
   - Click on "design.html" in sidebar file list
   - **Verify** File is highlighted as active
   - **Verify** File header shows: "design.html" with file type
   - **Verify** HTML preview appears in main visualization area (read-only)
   - **Verify** Sidebar shows text input field for HTML type
   - **Verify** "Enviar para Webhook" button is visible and enabled

5. **Input user command**
   - Type in sidebar text field: "Mudar cor do header para azul"
   - **Verify** Text is accepted in the input field
   - **Verify** Input field allows multi-line text

6. **Send command to webhook**
   - Click "Enviar para Webhook" button
   - **Verify** Button shows loading state
   - **Verify** Success message appears after sending
   - **Verify** Payload was sent to configured webhook URL

7. **Verify webhook payload structure**
   - Check webhook received payload with following structure:
   ```json
   {
     "project": "heroPage_design",
     "file": "design.html",
     "file_path": "/projetos/heroPage_design/design.html",
     "timestamp": "valid ISO timestamp",
     "current_state": {
       "content": "HTML content",
       "type": "html"
     },
     "user_input": {
       "type": "text",
       "data": "Mudar cor do header para azul"
     },
     "metadata": {
       "module": "html_preview",
       "supports_edit": true
     }
   }
   ```

## Success Criteria
- [ ] Server starts successfully on port 8000
- [ ] Interface loads with correct layout (header, sidebar, main area)
- [ ] WebSocket connection is established automatically
- [ ] Project selector lists all available projects
- [ ] Selecting project updates sidebar with correct files
- [ ] Clicking file displays it in visualization area with correct module
- [ ] Sidebar shows appropriate input field for file type
- [ ] User can input text command in sidebar
- [ ] Sending webhook shows visual feedback
- [ ] Webhook receives complete and correctly structured payload
- [ ] All required fields are present in payload

## Expected Output
{
  "test_name": "Main User Journey - Complete Flow",
  "status": "passed",
  "screenshots": ["screenshots/main-journey/01-interface-loaded.png", "screenshots/main-journey/02-project-selected.png", "screenshots/main-journey/03-file-viewed.png", "screenshots/main-journey/04-webhook-sent.png"],
  "error": null
}

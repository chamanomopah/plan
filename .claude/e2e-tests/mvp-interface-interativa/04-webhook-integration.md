# E2E Test: Webhook Integration and Scope Hierarchy

## User Story
As a user, I want commands to be sent to the correct webhook based on global/project/file-level configuration.

## Test Environment
- Base URL: http://localhost:8000
- Test Webhook URL: https://maceio-n8n-alfa42.serveousercontent.com/webhook/plan
- Test File: webhooks.json

## Test Steps

### Test Case 1: Global Webhook (Fallback)

1. **Verify global webhook configuration**
   - Open `webhooks.json`
   - **Verify** `global.default_webhook` is set
   - **Verify** `global.timeout` is 30
   - **Verify** `global.retry_attempts` is 3

2. **Test global webhook usage**
   - Select project without specific webhook override
   - Select any file
   - Input test command: "Test global webhook"
   - Click "Enviar para Webhook"
   - **Verify** Request is sent to global webhook URL
   - **Verify** Payload includes project, file, and user_input
   - **Verify** Request completes within timeout period

### Test Case 2: Project-Level Webhook Override

3. **Configure project-specific webhook**
   - In `webhooks.json`, verify project-level webhook:
   ```json
   {
     "projects": {
       "heroPage_design": {
         "webhook": "https://n8n.example.com/webhook/design",
         "override_global": true
       }
     }
   }
   ```
   - Select "heroPage_design" project
   - **Verify** Sidebar displays project webhook URL
   - **Verify** Badge shows "Project" scope
   - Select any file in project
   - Input test command: "Test project webhook"
   - Click "Enviar para Webhook"
   - **Verify** Request is sent to project webhook URL (not global)
   - **Verify** Payload structure is correct

### Test Case 3: File-Level Webhook Override

4. **Configure file-specific webhook**
   - In `webhooks.json`, configure file-level webhook:
   ```json
   {
     "projects": {
       "qualification_questions": {
         "webhook": "https://n8n.example.com/webhook/questions",
         "files": {
           "askQuestionTool1": {
             "webhook": "https://n8n.example.com/webhook/ask1"
           }
         }
       }
     }
   }
   ```
   - Select "qualification_questions" project
   - Select `askQuestionTool1` file
   - **Verify** Sidebar displays file-specific webhook URL
   - **Verify** Badge shows "File" scope
   - Select options and add comment
   - Click "Enviar para Webhook"
   - **Verify** Request is sent to file-level webhook URL
   - **Verify** Other files in project use project webhook

### Test Case 4: Webhook Payload Structure

5. **Verify complete payload structure**
   - Send command from any file
   - Capture webhook payload
   - **Verify** Payload contains:
     ```json
     {
       "project": "string (project name)",
       "file": "string (file name)",
       "file_path": "string (full path)",
       "timestamp": "ISO 8601 format",
       "current_state": {
         "content": "string (file content)",
         "type": "string (file type)"
       },
       "user_input": {
         "type": "text|options|form",
         "data": "string or object (user data)"
       },
       "metadata": {
         "module": "string (module name)",
         "supports_edit": "boolean"
       }
     }
     ```

6. **Test different user_input types**
   - **HTML file**: Verify `user_input.type = "text"` and `data = "string"`
   - **AskQuestionTool**: Verify `user_input.type = "options"` and `data = array of selected options`
   - **Form**: Verify `user_input.type = "form"` and `data = form fields object`

### Test Case 5: Error Handling

7. **Test webhook timeout**
   - Configure webhook URL that delays response > 30s
   - Send command
   - **Verify** Timeout error message appears
   - **Verify** Error is displayed in interface
   - **Verify** System logs timeout event

8. **Test invalid webhook URL**
   - Configure webhook URL: `https://invalid-domain-12345.com/webhook`
   - Send command
   - **Verify** Connection error message appears
   - **Verify** Retry mechanism attempts up to 3 times
   - **Verify** Final error message is shown to user

9. **Test webhook retry with exponential backoff**
   - Configure webhook that returns 500 error
   - Send command
   - **Verify** First attempt fails
   - **Verify** Retry 1 after ~1s backoff
   - **Verify** Retry 2 after ~2s backoff
   - **Verify** Retry 3 after ~4s backoff
   - **Verify** Final error message after 3 attempts

### Test Case 6: Webhook Configuration in UI

10. **Test webhook configuration in sidebar**
    - Select any project
    - **Verify** Webhook URL is displayed in sidebar
    - **Verify** "Configurar" button is present
    - Click "Configurar" button
    - **Verify** Edit modal/panel appears
    - **Verify** Current webhook URL is pre-filled
    - Modify webhook URL and save
    - **Verify** New webhook URL is displayed
    - **Verify** Next command uses new webhook URL
    - **Verify** Configuration is persisted in webhooks.json

## Success Criteria
- [ ] Global webhook is used as default fallback
- [ ] Project-level webhook overrides global webhook
- [ ] File-level webhook overrides project webhook
- [ ] Webhook scope badge displays correctly (Global/Project/File)
- [ ] Payload structure matches specification exactly
- [ ] user_input type varies correctly by file type
- [ ] Timeout errors are handled gracefully
- [ ] Invalid URLs show appropriate error messages
- [ ] Retry mechanism works with exponential backoff
- [ ] Webhook can be configured through UI
- [ ] Configuration changes persist to webhooks.json

## Expected Output
{
  "test_name": "Webhook Integration and Scope Hierarchy",
  "status": "passed",
  "screenshots": ["screenshots/webhook-integration/01-global-webhook.png", "screenshots/webhook-integration/02-project-webhook.png", "screenshots/webhook-integration/03-file-webhook.png", "screenshots/webhook-integration/04-error-handling.png", "screenshots/webhook-integration/05-config-modal.png"],
  "error": null
}

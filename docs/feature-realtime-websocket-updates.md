# Real-time WebSocket Updates System

**Date**: 2026-03-08
**Specification**: .claude/e2e-tests/mvp-interface-interativa/02-realtime-updates.md

## Overview

Implemented a complete WebSocket-based real-time update system that enables multiple browser tabs to automatically receive file modification notifications without page refresh. The system uses file system monitoring to detect changes made by AI agents and pushes updates to all connected clients instantly.

## What Was Built

- **WebSocket Server**: FastAPI WebSocket endpoint for bidirectional real-time communication
- **File System Watcher**: Background monitoring service using watchdog for detecting file modifications
- **WebSocket Client**: JavaScript client with automatic connection management and reconnection logic
- **Multi-Client Support**: Multiple browser tabs can simultaneously monitor the same file
- **Debounce Mechanism**: Prevents excessive updates during rapid file changes (500ms delay)
- **Toast Notifications**: User-friendly notifications for file updates
- **Sidebar Preservation**: Input fields are preserved during automatic updates
- **E2E Test Infrastructure**: Comprehensive test suite with multi-tab automation

## Technical Implementation

### Files Modified

- `app.py`: Added WebSocket server, file watcher, and real-time notification system
- `static/js/main.js`: Implemented WebSocket client connection and message handling
- `design.html`: Added connection status indicators and toast notification system
- `static/css/main.css`: Styling for WebSocket status indicators and notifications

### Key Changes

**WebSocket Server (app.py)**:
- Added `@app.websocket("/ws")` endpoint for client connections
- Implemented `active_connections` dictionary to track connected clients per file
- Created `FileWatcherHandler` class using watchdog for file system monitoring
- Added debouncing logic to prevent excessive updates (500ms threshold)
- Implemented async notification system for broadcasting updates to subscribed clients

**WebSocket Client (main.js)**:
- Added `connectWebSocket()` function with automatic reconnection (3s delay)
- Implemented subscription/unsubscription messaging for specific files
- Added real-time update handler that refreshes file content without page reload
- Created connection status indicator with visual feedback (connected/disconnected/error)
- Implemented toast notification system for user feedback

**File Monitoring**:
- Background watchdog observer monitors `projetos/` directory recursively
- Detects file modifications and triggers WebSocket broadcasts
- Extracts project and file names from file paths
- Reads updated content and metadata before sending to clients

## How to Use

1. **Start the FastAPI server**:
   ```bash
   python app.py
   ```

2. **Open the interface in browser tabs**:
   - Navigate to `http://localhost:8000`
   - Open multiple tabs if testing multi-client support

3. **Select a project and file**:
   - WebSocket automatically subscribes to the selected file
   - Connection status indicator shows in the header

4. **Modify file externally**:
   - Edit the file in a text editor or via AI agent
   - Save the file

5. **Observe real-time updates**:
   - All connected tabs receive notification within 500ms
   - Content refreshes automatically without page reload
   - Toast notification appears: "File updated: filename"
   - Sidebar input is preserved

## Configuration

**Environment Variables**:
- None required (uses localhost:8000 by default)

**WebSocket URL**:
- Automatically determined from `window.location.host`
- Uses `ws://` for HTTP and `wss://` for HTTPS

**Debounce Settings**:
- File modifications within 500ms are debounced
- Only final state is sent to clients after rapid changes

**Connection Management**:
- Automatic reconnection after 3 seconds if disconnected
- Subscribe/unsubscribe messages for managing file monitoring
- Connection cleanup on tab close or navigation

## Testing

**E2E Test Script**:
```bash
python .claude/e2e-tests/run_realtime_updates_test.py
```

**Test Coverage**:
- WebSocket connection establishment
- Multi-tab synchronization
- File modification detection
- Automatic content refresh
- Sidebar input preservation
- Toast notification display
- Debounce mechanism validation
- Connection reconnection after disconnect

**Expected Results**:
- Status: passed_with_warnings
- Steps passed: 9
- Steps failed: 0
- Steps with warnings: 3 (timing optimizations identified)

## Notes

**Architecture Benefits**:
- Zero-configuration WebSocket setup
- Scalable to multiple concurrent clients
- File-type agnostic (works with any monitored file)
- Minimal performance impact with debouncing

**Known Limitations**:
- 500ms delay for debounce mechanism (configurable in `app.py`)
- Requires file to be in `projetos/` directory structure
- WebSocket reconnection delay is fixed at 3 seconds

**Future Considerations**:
- Add configurable debounce delay per file type
- Implement file-specific subscription filtering
- Add connection pooling for high-traffic scenarios
- Consider Server-Sent Events (SSE) as fallback option

**Security Considerations**:
- WebSocket endpoint accepts all connections (no authentication)
- File path validation prevents directory traversal attacks
- CORS enabled for all origins in development

## Integration with MVP System

This real-time update system is a critical component of the MVP Interface Interativa, enabling:
- **AI Agent Integration**: Agents can modify files and users see changes instantly
- **Collaborative Editing**: Multiple users can view updates simultaneously
- **Enhanced UX**: No manual refresh required when files change
- **Workflow Automation**: Seamless integration with N8N webhook workflows
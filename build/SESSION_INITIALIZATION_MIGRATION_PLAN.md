# Session Initialization Migration Plan

## Objective
Move session creation from GUI startup (auto-create in desktop_app.py) to service launcher phase, ensuring persistence layer is verified before GUI launches. This provides proper isolation and guarantees session_id is available at GUI initialization time.

## Current Architecture (To Be Replaced)

```
./unhinged
  → control/cli/main.py
    → control/service_launcher.py (launches services)
    → control/gtk4_gui/launch.py
      → control/gtk4_gui/desktop_app/app.py
        → GUISessionLogger.__init__() [session_id = "TBD"]
        → _auto_create_session() [via GLib.idle_add]
          → ChatService.create_conversation()
          → SessionManager._on_session_created()
          → GUISessionLogger.update_session_id() [rename log file]
```

## Target Architecture (After Migration)

```
./unhinged
  → control/cli/main.py
    → control/service_launcher.py
      → SessionInitializationService.create_session() [NEW]
        → Verify persistence layer is live
        → ChatService.create_conversation()
        → SessionStore.write() [persist to Redis + CRDB]
        → Return session_id
      → Pass session_id to GUI launcher
    → control/gtk4_gui/launch.py
      → control/gtk4_gui/desktop_app/app.py
        → GUISessionLogger.__init__(session_id) [session_id known at init]
        → No auto-create needed
```

## Implementation Phases

### Phase 1: Design SessionInitializationService
- Location: `libs/python/session/session_initialization.py`
- Responsibilities:
  - Verify persistence layer (Redis + CRDB) is available
  - Create conversation via ChatService
  - Persist to SessionStore
  - Return session_id or raise exception
- No backward compatibility needed

### Phase 2: Implement SessionInitializationService
- Create service with proper error handling
- Use event logging for diagnostics
- Timeout handling for persistence layer checks

### Phase 3: Update Service Launcher
- Call SessionInitializationService after services are ready
- Pass session_id to GUI launcher via environment variable or return value
- Handle session creation failures gracefully

### Phase 4: Update GUISessionLogger
- Accept optional session_id parameter in __init__
- If session_id provided: use it directly (no TBD)
- If session_id not provided: use TBD (backward compat, deprecated)

### Phase 5: Remove GUI Auto-Create
- Delete _auto_create_session from desktop_app.py
- Remove session creation from ChatroomView
- Remove SessionManager.create_new_session calls

### Phase 6: Clean Up
- Remove deprecated code paths
- Update documentation
- Verify no broken references

## Key Design Decisions

1. **No Backward Compatibility**: Session MUST be created before GUI starts
2. **Fail Fast**: If persistence layer unavailable, fail at service launcher phase
3. **Proper Isolation**: Session creation is service-layer concern, not GUI concern
4. **Event Logging**: All operations logged via event framework for diagnostics
5. **Session Info in Startup Output**: Already implemented, will work with new flow

## Files to Modify

- `libs/python/session/session_initialization.py` (NEW)
- `control/service_launcher.py` (add session init call)
- `control/gtk4_gui/launch.py` (accept session_id parameter)
- `libs/event-framework/python/src/events/gui_session_logger.py` (accept session_id)
- `control/gtk4_gui/desktop_app/app.py` (remove _auto_create_session)
- `control/gtk4_gui/views/chatroom/chatroom_view.py` (remove session creation)
- `control/gtk4_gui/views/chatroom/session.py` (remove or archive)

## Testing Strategy

1. Unit tests for SessionInitializationService
2. Integration test: service launcher → session creation → GUI launch
3. Verify session_id appears in startup output
4. Verify log file is created with correct session_id (not TBD)
5. Verify persistence layer verification works

## Success Criteria

- ✅ Session created before GUI launches
- ✅ Session_id available at GUISessionLogger initialization
- ✅ No TBD placeholders in log files
- ✅ Session info printed to stdout during startup
- ✅ All tests pass
- ✅ No backward compatibility code remains


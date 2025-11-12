# Workspace State Management - Implementation Roadmap

## Overview

Implement Redux-like state management for Document Workspace using Redis + CRDB via Python persistence platform.

## Phase 1: State Manager Core (Estimated: 2-3 hours)

### 1.1 Create WorkspaceStateManager Class
**File**: `control/gtk4_gui/state/workspace_state_manager.py`

```python
class WorkspaceStateManager:
    """Redux-like state manager for workspace"""
    
    def __init__(self, document_type: str, persistence_client):
        self.document_type = document_type
        self.persistence_client = persistence_client
        self.state = {}
        self.subscribers = []
        self.action_history = []
    
    def dispatch(self, action: dict):
        """Dispatch action and update state"""
        # Validate action
        # Apply reducer
        # Persist to Redis
        # Notify subscribers
        pass
    
    def subscribe(self, callback):
        """Subscribe to state changes"""
        pass
    
    def get_state(self):
        """Get current state"""
        pass
    
    def get_state_slice(self, path: str):
        """Get slice of state (e.g., "documents", "current_state.selected_id")"""
        pass
```

### 1.2 Define Action Types
**File**: `control/gtk4_gui/state/workspace_actions.py`

```python
class WorkspaceActions:
    # Document operations
    SELECT_DOCUMENT = "SELECT_DOCUMENT"
    CREATE_DOCUMENT = "CREATE_DOCUMENT"
    UPDATE_DOCUMENT = "UPDATE_DOCUMENT"
    DELETE_DOCUMENT = "DELETE_DOCUMENT"
    LOAD_DOCUMENTS = "LOAD_DOCUMENTS"
    
    # Filter/View operations
    SET_FILTER = "SET_FILTER"
    SET_EDITOR_MODE = "SET_EDITOR_MODE"
    SET_METRICS_VIEW = "SET_METRICS_VIEW"
    
    # UI state
    UPDATE_UI_STATE = "UPDATE_UI_STATE"
    SET_ZOOM_LEVEL = "SET_ZOOM_LEVEL"
    SET_SCROLL_POSITION = "SET_SCROLL_POSITION"
```

### 1.3 Implement Reducer Functions
**File**: `control/gtk4_gui/state/workspace_reducer.py`

```python
def workspace_reducer(state, action):
    """Pure reducer function"""
    
    action_type = action.get("type")
    payload = action.get("payload", {})
    
    if action_type == WorkspaceActions.SELECT_DOCUMENT:
        return select_document_reducer(state, payload)
    
    elif action_type == WorkspaceActions.CREATE_DOCUMENT:
        return create_document_reducer(state, payload)
    
    # ... more reducers
    
    return state

def select_document_reducer(state, payload):
    """Handle document selection"""
    return {
        **state,
        "current_state": {
            **state.get("current_state", {}),
            "selected_document_id": payload["document_id"]
        }
    }

def create_document_reducer(state, payload):
    """Handle document creation"""
    new_doc = payload["document"]
    return {
        **state,
        "documents": {
            **state.get("documents", {}),
            new_doc["id"]: new_doc
        }
    }

# ... more reducer functions
```

### 1.4 Initial State Schema
**File**: `control/gtk4_gui/state/workspace_state_schema.py`

```python
def create_initial_state(document_type: str, session_id: str):
    """Create initial workspace state"""
    return {
        "id": f"workspace_state_{session_id}",
        "type": "workspace_state",
        "document_type": document_type,
        "session_id": session_id,
        
        "current_state": {
            "selected_document_id": None,
            "registry_filter": "all",
            "editor_mode": "view",
            "metrics_view": "overview"
        },
        
        "documents": {},
        
        "ui": {
            "sidebar_expanded": True,
            "zoom_level": 1.0,
            "scroll_position": 0
        },
        
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
```

## Phase 2: Redis Integration (Estimated: 1-2 hours)

### 2.1 Redis State Store
**File**: `control/gtk4_gui/state/redis_state_store.py`

```python
class RedisStateStore:
    """Redis-backed state store"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def save_state(self, state_id: str, state: dict):
        """Save state to Redis"""
        pass
    
    def load_state(self, state_id: str):
        """Load state from Redis"""
        pass
    
    def subscribe_to_changes(self, state_id: str, callback):
        """Subscribe to state changes via Pub/Sub"""
        pass
```

### 2.2 Pub/Sub Integration
- Publish state changes to Redis channel
- Subscribe tabs to state changes
- Handle connection failures

## Phase 3: CRDB Persistence (Estimated: 1-2 hours)

### 3.1 Persist State Changes
- Save state mutations to CRDB
- Maintain audit trail
- Implement state recovery on app restart

### 3.2 State Recovery
- Load last known state from CRDB on startup
- Validate state integrity
- Handle corrupted state gracefully

## Phase 4: Tab Integration (Estimated: 2-3 hours)

### 4.1 Update Registry Tab
- Connect to state manager
- Dispatch actions on document operations
- Subscribe to state changes
- Update UI when state changes

### 4.2 Update Editor Tab
- Connect to state manager
- Dispatch actions on document edits
- Subscribe to selected document changes
- Update UI when document changes

### 4.3 Update Metrics Tab
- Connect to state manager
- Subscribe to document changes
- Update metrics when state changes

## File Structure

```
control/gtk4_gui/state/
├── __init__.py
├── workspace_state_manager.py      # Main state manager
├── workspace_actions.py             # Action type definitions
├── workspace_reducer.py             # Reducer functions
├── workspace_state_schema.py        # Initial state schema
├── redis_state_store.py             # Redis integration
├── crdb_state_store.py              # CRDB integration
└── state_utils.py                   # Utility functions
```

## Testing Strategy

### Unit Tests
- Test reducer functions (pure functions, easy to test)
- Test action validation
- Test state schema

### Integration Tests
- Test state manager with mock persistence
- Test Redis integration
- Test CRDB persistence

### UI Tests
- Test tab synchronization
- Test state recovery on restart
- Test error handling

## Success Criteria

✅ State persists across app restarts  
✅ All tabs stay in sync  
✅ State changes are auditable in CRDB  
✅ No state loss on network failures  
✅ Performance is acceptable (< 100ms state updates)  
✅ Code is testable and maintainable  

## Estimated Timeline

- Phase 1 (Core): 2-3 hours
- Phase 2 (Redis): 1-2 hours
- Phase 3 (CRDB): 1-2 hours
- Phase 4 (Integration): 2-3 hours
- Testing & Refinement: 2-3 hours

**Total: 8-13 hours**

## Key Decisions

1. **Redux-like Pattern**: Familiar to developers, proven pattern
2. **Redis for Live State**: Fast, in-memory, Pub/Sub support
3. **CRDB for Durability**: Persistent, auditable, recoverable
4. **Python Persistence Platform**: Reuse existing infrastructure
5. **Pure Reducers**: Easy to test, reason about, debug

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Redis connection loss | Fallback to in-memory state, retry connection |
| State corruption | Validate state schema, implement recovery |
| Performance issues | Profile state updates, optimize hot paths |
| Complexity | Start with simple state, add features incrementally |

## Next Steps

1. Review design with team
2. Create Phase 1 implementation
3. Write unit tests for reducers
4. Integrate with existing persistence platform
5. Test with real document operations


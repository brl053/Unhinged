# Workspace State Management Design

## Problem Statement

Frontend state management is fundamentally different from backend state management:

**Backend**: Stateless services, clean separation, easy to reason about
**Frontend**: Thousand pieces of interconnected state, all needing real-time visualization

Traditional solutions (Redux, Vuex, MobX) keep state in-memory only, losing it on app restart.

## Solution: Persistent State via Python Persistence Platform

Use the same infrastructure you already built for backend persistence, but for frontend state.

```
┌─────────────────────────────────────────────────────────┐
│ GTK4 UI (Document Workspace Tabs)                       │
│ ├─ Registry Tab                                         │
│ ├─ Editor Tab                                           │
│ └─ Metrics Tab                                          │
└────────────────┬────────────────────────────────────────┘
                 │ (state mutations)
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Workspace State Manager (Redux-like pattern)            │
│ ├─ Dispatch actions                                     │
│ ├─ Reduce to new state                                  │
│ └─ Notify subscribers                                   │
└────────────────┬────────────────────────────────────────┘
                 │ (persist state)
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Python Persistence Platform                             │
│ ├─ Document Store (state documents)                     │
│ ├─ Redis (live state, Pub/Sub)                          │
│ └─ CRDB (durable state, audit trail)                    │
└─────────────────────────────────────────────────────────┘
```

## Architecture

### State Structure

```python
# Workspace state document (stored in Redis + CRDB)
{
    "id": "workspace_state_<session_id>",
    "type": "workspace_state",
    "document_type": "graph",  # or "tool", "user", etc.
    
    # Current state
    "current_state": {
        "selected_document_id": "doc-123",
        "registry_filter": "active",
        "editor_mode": "edit",
        "metrics_view": "performance"
    },
    
    # Document cache (for quick access)
    "documents": {
        "doc-123": {...},
        "doc-456": {...}
    },
    
    # UI state
    "ui": {
        "sidebar_expanded": true,
        "zoom_level": 1.0,
        "scroll_position": 0
    },
    
    # Metadata
    "created_at": "2025-11-12T10:00:00Z",
    "updated_at": "2025-11-12T10:05:00Z",
    "session_id": "session_abc123"
}
```

### State Mutations (Redux-like Actions)

```python
# Actions that modify state
class WorkspaceActions:
    SELECT_DOCUMENT = "SELECT_DOCUMENT"
    CREATE_DOCUMENT = "CREATE_DOCUMENT"
    UPDATE_DOCUMENT = "UPDATE_DOCUMENT"
    DELETE_DOCUMENT = "DELETE_DOCUMENT"
    SET_FILTER = "SET_FILTER"
    SET_EDITOR_MODE = "SET_EDITOR_MODE"
    SET_METRICS_VIEW = "SET_METRICS_VIEW"
    UPDATE_UI_STATE = "UPDATE_UI_STATE"

# Action dispatch
state_manager.dispatch({
    "type": WorkspaceActions.SELECT_DOCUMENT,
    "payload": {"document_id": "doc-123"}
})
```

### Reducer Pattern

```python
def workspace_reducer(state, action):
    """Pure function: (state, action) -> new_state"""
    
    if action["type"] == WorkspaceActions.SELECT_DOCUMENT:
        return {
            **state,
            "current_state": {
                **state["current_state"],
                "selected_document_id": action["payload"]["document_id"]
            }
        }
    
    elif action["type"] == WorkspaceActions.CREATE_DOCUMENT:
        new_doc = action["payload"]["document"]
        return {
            **state,
            "documents": {
                **state["documents"],
                new_doc["id"]: new_doc
            }
        }
    
    # ... more reducers
    
    return state
```

### Subscriber Pattern (Pub/Sub)

```python
# Tabs subscribe to state changes
registry_tab.subscribe(state_manager, ["documents", "current_state"])
editor_tab.subscribe(state_manager, ["current_state", "ui"])
metrics_tab.subscribe(state_manager, ["documents", "current_state"])

# When state changes, subscribers are notified
state_manager.on_state_change(lambda new_state: {
    "registry_tab": registry_tab.update(new_state),
    "editor_tab": editor_tab.update(new_state),
    "metrics_tab": metrics_tab.update(new_state)
})
```

## Implementation Strategy

### Phase 1: State Manager Core
- Create `WorkspaceStateManager` class
- Implement dispatch/reduce pattern
- Implement subscriber notification
- Integrate with Python persistence platform

### Phase 2: Redis Integration
- Store state in Redis for fast access
- Implement Pub/Sub for real-time updates
- Handle Redis connection failures gracefully

### Phase 3: CRDB Persistence
- Persist state changes to CRDB
- Implement state recovery on app restart
- Maintain audit trail of mutations

### Phase 4: Tab Integration
- Update Registry tab to use state manager
- Update Editor tab to use state manager
- Update Metrics tab to use state manager
- Ensure all tabs stay in sync

## Key Benefits

1. **Persistent State**: Survives app restart
2. **Real-time Sync**: All tabs see same state via Pub/Sub
3. **Audit Trail**: CRDB maintains history of mutations
4. **Familiar Pattern**: Redux-like API developers know
5. **Reusable**: Same pattern for all document types
6. **Testable**: Pure reducer functions are easy to test
7. **Debuggable**: Can replay state mutations from CRDB

## Comparison to Traditional Approaches

| Aspect | Redux | Vuex | Your Approach |
|--------|-------|------|---------------|
| State Storage | Memory | Memory | Redis + CRDB |
| Persistence | None | None | Automatic |
| Survives Restart | No | No | Yes |
| Audit Trail | No | No | Yes (CRDB) |
| Real-time Sync | No | No | Yes (Pub/Sub) |
| Infrastructure | None | None | Existing platform |

## Example: Document Selection Flow

```
User clicks document in Registry
    ↓
Registry Tab dispatches action
    ↓
WorkspaceStateManager.dispatch({
    type: SELECT_DOCUMENT,
    payload: {document_id: "doc-123"}
})
    ↓
Reducer updates state
    ↓
State persisted to Redis + CRDB
    ↓
Pub/Sub notifies all subscribers
    ↓
Editor Tab receives update
    ↓
Editor Tab renders selected document
    ↓
Metrics Tab receives update
    ↓
Metrics Tab renders document metrics
```

## Next Steps

1. Design `WorkspaceStateManager` class
2. Implement reducer functions
3. Integrate with Python persistence platform
4. Add Redis Pub/Sub support
5. Update tabs to use state manager
6. Test state persistence and recovery


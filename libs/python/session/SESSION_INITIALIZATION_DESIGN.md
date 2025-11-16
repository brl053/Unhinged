# SessionInitializationService Design

## Purpose
Create chat sessions before GUI startup, verifying persistence layer is live and returning session_id for GUI initialization.

## Class Definition

```python
class SessionInitializationService:
    """Initialize sessions with persistence layer verification"""
    
    def __init__(self, timeout: int = 30):
        """
        Args:
            timeout: Max seconds to wait for persistence layer
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def create_session(self, session_name: str = None) -> str:
        """
        Create a new session with persistence verification.
        
        Args:
            session_name: Optional session name (default: timestamp-based)
        
        Returns:
            session_id: UUID of created session
        
        Raises:
            SessionInitializationError: If persistence layer unavailable
                or session creation fails
        """
        # 1. Verify persistence layer is live
        # 2. Create conversation via ChatService
        # 3. Persist to SessionStore
        # 4. Return session_id
    
    def _verify_persistence_layer(self) -> bool:
        """Check Redis and CRDB are available"""
        # Try to connect to Redis
        # Try to connect to document store
        # Return True if both available
    
    def _create_conversation(self, session_name: str) -> str:
        """Create conversation and return ID"""
        # Use ChatService.create_conversation()
        # Return conversation_id
    
    def _persist_session(self, session_id: str, metadata: dict) -> bool:
        """Persist session to SessionStore"""
        # Use SessionStore.write()
        # Return success status
```

## Error Handling

```python
class SessionInitializationError(Exception):
    """Base exception for session initialization"""
    pass

class PersistenceLayerUnavailableError(SessionInitializationError):
    """Raised when Redis or CRDB not available"""
    pass

class SessionCreationFailedError(SessionInitializationError):
    """Raised when ChatService fails"""
    pass

class SessionPersistenceFailedError(SessionInitializationError):
    """Raised when SessionStore write fails"""
    pass
```

## Integration Points

1. **Service Launcher**: Calls create_session() after services ready
2. **CLI**: Passes session_id to GUI launcher
3. **GUISessionLogger**: Receives session_id at initialization
4. **Event Logging**: All operations logged via event framework

## Testing

- Unit tests for each method
- Mock persistence layer for offline testing
- Integration test with real services
- Timeout handling verification


# OpenTelemetry Implementation Guide

**Version**: 1.0.0
**Date**: 2025-10-06
**Author**: Unhinged Team

## 🚀 **Implementation Specifications**

### **1. Scalability and Performance Optimization**

#### **Sampling Strategies by Service Type**

```yaml
# sampling-config.yaml
sampling_strategies:
  # Frontend services - lower sampling due to high volume
  frontend:
    default_strategy:
      type: probabilistic
      param: 0.01  # 1% sampling
    per_operation_strategies:
      - operation: "user_interaction"
        type: probabilistic
        param: 0.05  # 5% for user interactions
      - operation: "error_boundary"
        type: probabilistic
        param: 1.0   # 100% for errors

  # Gateway services - moderate sampling
  gateway:
    default_strategy:
      type: adaptive
      max_traces_per_second: 100
      param: 0.1   # 10% base sampling
    per_operation_strategies:
      - operation: "websocket_connection"
        type: probabilistic
        param: 0.2   # 20% for WebSocket events

  # Backend services - higher sampling for business logic
  backend:
    default_strategy:
      type: adaptive
      max_traces_per_second: 200
      param: 0.2   # 20% base sampling
    per_operation_strategies:
      - operation: "chat_message"
        type: probabilistic
        param: 0.5   # 50% for chat operations

  # Critical services - high sampling
  critical:
    default_strategy:
      type: probabilistic
      param: 0.8   # 80% sampling
    per_operation_strategies:
      - operation: "authentication"
        type: probabilistic
        param: 1.0   # 100% for auth operations
```

#### **Batching Configuration**

```yaml
# batching-config.yaml
processors:
  batch/traces:
    timeout: 1s
    send_batch_size: 512      # Optimal for traces
    send_batch_max_size: 1024

  batch/metrics:
    timeout: 5s
    send_batch_size: 2048     # Larger batches for metrics
    send_batch_max_size: 4096

  batch/logs:
    timeout: 2s
    send_batch_size: 1024     # Medium batches for logs
    send_batch_max_size: 2048

  # Memory optimization
  memory_limiter:
    limit_mib: 256            # 256MB limit per collector
    spike_limit_mib: 64       # 64MB spike allowance
    check_interval: 5s
```

### **2. Library API Design Examples**

#### **TypeScript Usage Examples**

```typescript
// Basic usage with environment defaults
import { createLogger } from '@unhinged/observability';

const logger = createLogger({ service: 'chat-service' });

// Runtime flag override
const debugLogger = createLogger({
  service: 'debug-service',
  flags: process.env.NODE_ENV === 'production' ? 'CDL' : 'C'
});

// Advanced configuration
const analyticsLogger = createLogger({
  service: 'analytics-service',
  flags: 'L',  // Data lake only
  defaultMetadata: {
    component: 'user-analytics',
    version: '2.1.0'
  }
});

// Usage with OpenTelemetry context
import { trace, context } from '@opentelemetry/api';

const span = trace.getActiveSpan();
span?.setAttributes({
  'user.id': '12345',
  'session.id': 'sess_abc123'
});

logger.info('User action completed', {
  action: 'message_sent',
  messageId: 'msg_xyz789',
  conversationId: 'conv_456'
});

// Error logging with exception
try {
  await sendMessage(messageData);
} catch (error) {
  logger.error('Failed to send message', error, {
    messageId: messageData.id,
    retryCount: 3
  });
}
```
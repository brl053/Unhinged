# Event Framework Usage Examples

This document provides comprehensive examples of using the Unhinged Event Framework in both Kotlin and Python implementations.

## Basic Logging Examples

### Kotlin Basic Usage

```kotlin
import com.unhinged.events.*

fun main() {
    // Create a simple logger
    val logger = EventLoggerFactory.createLogger("example-service")
    
    // Basic logging
    logger.debug("Debug message for troubleshooting")
    logger.info("Service operation completed")
    logger.warn("Deprecated API usage detected")
    logger.error("Failed to process request", RuntimeException("Connection timeout"))
    
    // Logging with metadata
    logger.info("User login successful", mapOf(
        "user_id" to "user123",
        "login_method" to "oauth",
        "ip_address" to "192.168.1.100",
        "user_agent" to "Mozilla/5.0..."
    ))
}
```

### Python Basic Usage

```python
from unhinged_events import create_service_logger

def main():
    # Create a simple logger
    logger = create_service_logger("example-service")
    
    # Basic logging
    logger.debug("Debug message for troubleshooting")
    logger.info("Service operation completed")
    logger.warn("Deprecated API usage detected")
    logger.error("Failed to process request", exception=ConnectionError("Connection timeout"))
    
    # Logging with metadata
    logger.info("User login successful", {
        "user_id": "user123",
        "login_method": "oauth",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
    })

if __name__ == "__main__":
    main()
```

## ServiceBase Integration Examples

### Kotlin ServiceBase Extension

```kotlin
import com.unhinged.events.*
import com.unhinged.framework.ServiceBase

class ChatService : ServiceBase("chat-service", "1.2.0", 8080) {
    
    // Use the event logger extension
    private val eventLogger = this.eventLogger
    
    override suspend fun initialize() {
        eventLogger.info("Initializing chat service", mapOf(
            "max_connections" to 1000,
            "message_queue_size" to 10000
        ))
        
        try {
            initializeMessageQueue()
            initializeUserSessions()
            eventLogger.info("Chat service initialization completed")
        } catch (e: Exception) {
            eventLogger.error("Failed to initialize chat service", e)
            throw e
        }
    }
    
    override fun registerGrpcServices(serverBuilder: ServerBuilder<*>) {
        serverBuilder.addService(ChatServiceImpl(eventLogger))
    }
    
    private fun initializeMessageQueue() {
        eventLogger.debug("Initializing message queue")
        // Implementation...
    }
    
    private fun initializeUserSessions() {
        eventLogger.debug("Initializing user session manager")
        // Implementation...
    }
}

class ChatServiceImpl(private val eventLogger: EventLogger) : ChatServiceGrpc.ChatServiceImplBase() {
    
    override fun sendMessage(request: SendMessageRequest, responseObserver: StreamObserver<SendMessageResponse>) {
        val requestLogger = eventLogger.withContext(mapOf(
            "request_id" to request.requestId,
            "user_id" to request.userId,
            "conversation_id" to request.conversationId
        ))
        
        requestLogger.info("Processing send message request", mapOf(
            "message_length" to request.message.length,
            "message_type" to request.messageType.name
        ))
        
        try {
            val response = processMessage(request)
            
            requestLogger.info("Message sent successfully", mapOf(
                "message_id" to response.messageId,
                "delivery_time_ms" to response.deliveryTimeMs
            ))
            
            responseObserver.onNext(response)
            responseObserver.onCompleted()
            
        } catch (e: Exception) {
            requestLogger.error("Failed to send message", e, mapOf(
                "error_type" to e.javaClass.simpleName
            ))
            responseObserver.onError(e)
        }
    }
}
```

### Python AI Service Example

```python
import asyncio
import time
from typing import Dict, Any
from unhinged_events import create_service_logger, LLMEventType
from unhinged_events.protobuf_integration import create_universal_emitter

class LLMInferenceService:
    def __init__(self, service_id: str = "llm-inference-service"):
        self.service_id = service_id
        self.logger = create_service_logger(service_id, version="2.1.0")
        self.event_emitter = create_universal_emitter(self.logger, service_id)
        
        # Log service startup
        self.logger.info("LLM Inference Service initialized", {
            "model_cache_size": 5,
            "max_concurrent_requests": 10,
            "supported_models": ["llama3.2", "gpt-4", "claude-3"]
        })
    
    async def process_inference_request(
        self, 
        prompt: str, 
        model: str, 
        user_id: str, 
        session_id: str,
        parameters: Dict[str, Any] = None
    ) -> str:
        """Process an LLM inference request with comprehensive logging"""
        
        # Create request-specific logger
        request_logger = self.logger.with_context({
            "user_id": user_id,
            "session_id": session_id,
            "model": model,
            "request_id": f"req_{int(time.time() * 1000)}"
        })
        
        # Log request start
        request_logger.info("Starting LLM inference", {
            "prompt_length": len(prompt),
            "model": model,
            "parameters": parameters or {}
        })
        
        # Emit protobuf-compatible start event
        self.event_emitter.emit_llm_inference_event(
            event_type=LLMEventType.STARTED,
            model_name=model,
            user_id=user_id,
            session_id=session_id
        )
        
        start_time = time.time()
        
        try:
            # Simulate model loading
            if not self._is_model_loaded(model):
                request_logger.info("Loading model", {"model": model})
                await self._load_model(model)
            
            # Simulate inference
            request_logger.debug("Running inference", {
                "model_status": "loaded",
                "inference_mode": "streaming"
            })
            
            result = await self._run_inference(prompt, model, parameters or {})
            
            # Calculate metrics
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            prompt_tokens = len(prompt.split())
            response_tokens = len(result.split())
            
            # Log successful completion
            request_logger.info("LLM inference completed", {
                "latency_ms": latency_ms,
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "tokens_per_second": response_tokens / (latency_ms / 1000) if latency_ms > 0 else 0
            })
            
            # Emit completion event
            self.event_emitter.emit_llm_inference_event(
                event_type=LLMEventType.COMPLETED,
                model_name=model,
                prompt_tokens=prompt_tokens,
                response_tokens=response_tokens,
                latency_ms=latency_ms,
                success=True,
                user_id=user_id,
                session_id=session_id
            )
            
            return result
            
        except Exception as e:
            # Calculate partial metrics
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            # Log error
            request_logger.error("LLM inference failed", exception=e, metadata={
                "error_type": type(e).__name__,
                "latency_ms": latency_ms,
                "model": model
            })
            
            # Emit failure event
            self.event_emitter.emit_llm_inference_event(
                event_type=LLMEventType.FAILED,
                model_name=model,
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
                user_id=user_id,
                session_id=session_id
            )
            
            raise
    
    def _is_model_loaded(self, model: str) -> bool:
        """Check if model is loaded (mock implementation)"""
        return model in ["llama3.2"]  # Simulate some models being pre-loaded
    
    async def _load_model(self, model: str):
        """Load model (mock implementation)"""
        self.logger.debug(f"Loading model {model}")
        await asyncio.sleep(0.1)  # Simulate loading time
        self.logger.info(f"Model {model} loaded successfully")
    
    async def _run_inference(self, prompt: str, model: str, parameters: Dict[str, Any]) -> str:
        """Run inference (mock implementation)"""
        await asyncio.sleep(0.05)  # Simulate inference time
        return f"Response from {model}: This is a mock response to '{prompt[:50]}...'"

# Usage example
async def main():
    service = LLMInferenceService()
    
    try:
        result = await service.process_inference_request(
            prompt="What is the capital of France?",
            model="llama3.2",
            user_id="user123",
            session_id="session456",
            parameters={"temperature": 0.7, "max_tokens": 100}
        )
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## OpenTelemetry Integration Examples

### Kotlin with OpenTelemetry

```kotlin
import com.unhinged.events.*
import io.opentelemetry.api.trace.Tracer
import io.opentelemetry.api.trace.Span

class TracedService(private val tracer: Tracer) {
    private val logger = EventLoggerFactory.createLogger("traced-service")
    
    fun processWithTracing(userId: String, operation: String) {
        val span = tracer.spanBuilder("process-operation")
            .setAttribute("user.id", userId)
            .setAttribute("operation.name", operation)
            .startSpan()
        
        span.makeCurrent().use {
            // Logger automatically picks up trace context
            logger.info("Starting traced operation", mapOf(
                "user_id" to userId,
                "operation" to operation
            ))
            
            try {
                performOperation(operation)
                
                logger.info("Traced operation completed successfully")
                span.setStatus(StatusCode.OK)
                
            } catch (e: Exception) {
                logger.error("Traced operation failed", e)
                span.setStatus(StatusCode.ERROR, e.message ?: "Unknown error")
                span.recordException(e)
                throw e
            }
        }
    }
}
```

### Python with OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from unhinged_events import create_service_logger

class TracedService:
    def __init__(self):
        self.logger = create_service_logger("traced-service")
        self.tracer = trace.get_tracer(__name__)
    
    def process_with_tracing(self, user_id: str, operation: str):
        with self.tracer.start_as_current_span("process-operation") as span:
            span.set_attributes({
                "user.id": user_id,
                "operation.name": operation
            })
            
            # Logger automatically picks up trace context
            self.logger.info("Starting traced operation", {
                "user_id": user_id,
                "operation": operation
            })
            
            try:
                self.perform_operation(operation)
                
                self.logger.info("Traced operation completed successfully")
                span.set_status(Status(StatusCode.OK))
                
            except Exception as e:
                self.logger.error("Traced operation failed", exception=e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def perform_operation(self, operation: str):
        # Mock operation
        if operation == "fail":
            raise ValueError("Simulated failure")
        return f"Operation {operation} completed"
```

## Configuration Examples

### Advanced Kotlin Configuration

```kotlin
import com.unhinged.events.*

fun createProductionLogger(): EventLogger {
    val config = EventLoggerConfig(
        serviceId = "production-service",
        version = "2.1.0",
        environment = "production",
        minLogLevel = LogLevel.INFO,
        outputFormat = OutputFormat.YAML,
        includeStackTrace = false, // Reduce log size in production
        contextData = mapOf(
            "datacenter" to "us-west-2",
            "cluster" to "prod-cluster-1",
            "instance_id" to System.getenv("INSTANCE_ID"),
            "deployment_version" to "v2.1.0-abc123"
        )
    )
    
    return EventLoggerFactory.createLogger(config)
}

fun createDevelopmentLogger(): EventLogger {
    val config = EventLoggerConfig(
        serviceId = "dev-service",
        version = "dev",
        environment = "development",
        minLogLevel = LogLevel.DEBUG,
        outputFormat = OutputFormat.YAML,
        includeStackTrace = true,
        contextData = mapOf(
            "developer" to System.getProperty("user.name"),
            "branch" to "feature/new-logging"
        )
    )
    
    return EventLoggerFactory.createLogger(config)
}
```

### Advanced Python Configuration

```python
import os
from unhinged_events import EventLoggerConfig, LogLevel, OutputFormat, create_logger

def create_production_logger():
    config = EventLoggerConfig(
        service_id="production-service",
        version="2.1.0",
        environment="production",
        min_log_level=LogLevel.INFO,
        output_format=OutputFormat.YAML,
        include_stack_trace=False,  # Reduce log size in production
        context_data={
            "datacenter": "us-west-2",
            "cluster": "prod-cluster-1",
            "instance_id": os.getenv("INSTANCE_ID"),
            "deployment_version": "v2.1.0-abc123"
        }
    )
    
    return create_logger(config)

def create_development_logger():
    config = EventLoggerConfig(
        service_id="dev-service",
        version="dev",
        environment="development",
        min_log_level=LogLevel.DEBUG,
        output_format=OutputFormat.YAML,
        include_stack_trace=True,
        context_data={
            "developer": os.getenv("USER"),
            "branch": "feature/new-logging"
        }
    )
    
    return create_logger(config)
```

These examples demonstrate the comprehensive capabilities of the Event Framework across different use cases, from basic logging to complex service integrations with OpenTelemetry tracing.

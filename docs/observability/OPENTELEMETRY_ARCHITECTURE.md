# OpenTelemetry Unified Observability Architecture

**Version**: 1.0.0
**Date**: 2025-10-06
**Author**: Unhinged Team

## 🎯 **Architecture Overview**

Our unified observability solution integrates OpenTelemetry with our existing CDC event system, providing comprehensive tracing, metrics, and logging across our distributed architecture.

## 🏗️ **1. OpenTelemetry Sidecar Integration**

### **Gateway Collector Configuration**

```yaml
# otel-collector-config.yaml
receivers:
  # gRPC OTLP receiver for backend services
  otlp/grpc:
    endpoint: 0.0.0.0:4317
    protocols:
      grpc:
        max_recv_msg_size: 4194304  # 4MB
        max_concurrent_streams: 16

  # HTTP OTLP receiver for frontend/web clients
  otlp/http:
    endpoint: 0.0.0.0:4318
    protocols:
      http:
        cors:
          allowed_origins:
            - "http://localhost:3000"
            - "https://app.unhinged.ai"

processors:
  # Batch processor for performance optimization
  batch:
    timeout: 1s
    send_batch_size: 1024
    send_batch_max_size: 2048

  # Memory limiter to prevent OOM
  memory_limiter:
    limit_mib: 512
    spike_limit_mib: 128
    check_interval: 5s

  # Probabilistic sampling for high-volume traces
  probabilistic_sampler:
    sampling_percentage: 10.0  # 10% sampling rate

  # Tail sampling for intelligent trace selection
  tail_sampling:
    decision_wait: 10s
    policies:
      # Always sample error traces
      - name: error-policy
        type: status_code
        status_code:
          status_codes: [ERROR]
      # Sample slow traces (>1s)
      - name: latency-policy
        type: latency
        latency:
          threshold_ms: 1000

exporters:
  # CDC Kafka exporter for event stream integration
  kafka:
    brokers: ["kafka:9092"]
    topic: "observability.traces"
    protocol_version: "2.6.0"
    producer:
      max_message_bytes: 1000000
      required_acks: 1
      compression: "gzip"

  # Jaeger exporter for trace visualization
  jaeger:
    endpoint: "jaeger-collector:14250"
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp/grpc, otlp/http]
      processors: [memory_limiter, batch, tail_sampling]
      exporters: [kafka, jaeger]
    metrics:
      receivers: [otlp/grpc, otlp/http]
      processors: [memory_limiter, batch]
      exporters: [kafka]
```
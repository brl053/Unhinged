# OpenTelemetry Deployment Architecture

**Version**: 1.0.0
**Date**: 2025-10-06
**Author**: Unhinged Team

## 🏗️ **Telemetry Flow Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           TELEMETRY FLOW ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐             │
│  │   Frontend      │    │   Gateway       │    │   Backend       │             │
│  │   React/TS      │    │ Node.js/Rust    │    │   Kotlin        │             │
│  │                 │    │                 │    │                 │             │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │             │
│  │ │ OTEL SDK    │ │    │ │ OTEL SDK    │ │    │ │ OTEL SDK    │ │             │
│  │ │ - Traces    │ │    │ │ - Traces    │ │    │ │ - Traces    │ │             │
│  │ │ - Metrics   │ │    │ │ - Metrics   │ │    │ │ - Metrics   │ │             │
│  │ │ - Logs      │ │    │ │ - Logs      │ │    │ │ - Logs      │ │             │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │             │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘             │
│           │                       │                       │                     │
│           │ OTLP/HTTP             │ OTLP/gRPC            │ OTLP/gRPC           │
│           │ Port: 4318            │ Port: 4317           │ Port: 4317          │
│           │                       │                      │                     │
│           └───────────────────────┼──────────────────────┘                     │
│                                   │                                            │
│                    ┌──────────────▼──────────────┐                             │
│                    │   OpenTelemetry Collector   │                             │
│                    │        (Gateway Mode)       │                             │
│                    │                             │                             │
│                    │  ┌─────────────────────────┐ │                             │
│                    │  │      Receivers         │ │                             │
│                    │  │  • OTLP/gRPC :4317     │ │                             │
│                    │  │  • OTLP/HTTP :4318     │ │                             │
│                    │  │  • Prometheus :8889    │ │                             │
│                    │  └─────────────────────────┘ │                             │
│                    │                             │                             │
│                    │  ┌─────────────────────────┐ │                             │
│                    │  │      Processors        │ │                             │
│                    │  │  • Batch Processing    │ │                             │
│                    │  │  • Memory Limiting     │ │                             │
│                    │  │  • Tail Sampling       │ │                             │
│                    │  │  • Attribute Enrichment│ │                             │
│                    │  └─────────────────────────┘ │                             │
│                    │                             │                             │
│                    │  ┌─────────────────────────┐ │                             │
│                    │  │       Exporters        │ │                             │
│                    │  │  • Kafka CDC Stream    │ │                             │
│                    │  │  • Jaeger Backend      │ │                             │
│                    │  │  • Prometheus TSDB     │ │                             │
│                    │  │  • Data Lake (S3/GCS)  │ │                             │
│                    │  └─────────────────────────┘ │                             │
│                    └──────────────┬──────────────┘                             │
│                                   │                                            │
│              ┌────────────────────┼────────────────────┐                       │
│              │                    │                    │                       │
│    ┌─────────▼─────────┐ ┌────────▼────────┐ ┌────────▼────────┐               │
│    │ Kafka CDC Stream  │ │ Observability   │ │ Data Lake       │               │
│    │                   │ │ Backend         │ │ Storage         │               │
│    │ Topics:           │ │                 │ │                 │               │
│    │ • observability.  │ │ • Jaeger        │ │ • S3/GCS        │               │
│    │   traces          │ │ • Prometheus    │ │ • Delta Lake    │               │
│    │ • observability.  │ │ • Grafana       │ │ • Parquet       │               │
│    │   metrics         │ │ • AlertManager  │ │ • Iceberg       │               │
│    │ • observability.  │ │                 │ │                 │               │
│    │   logs            │ │                 │ │                 │               │
│    └─────────┬─────────┘ └─────────────────┘ └─────────────────┘               │
│              │                                                                 │
│    ┌─────────▼─────────┐                                                       │
│    │ Apache Flink      │                                                       │
│    │ Stream Processor  │                                                       │
│    │                   │                                                       │
│    │ • Real-time       │                                                       │
│    │   Aggregation     │                                                       │
│    │ • Anomaly         │                                                       │
│    │   Detection       │                                                       │
│    │ • Alert           │                                                       │
│    │   Generation      │                                                       │
│    │ • Data Lake       │                                                       │
│    │   ETL Pipeline    │                                                       │
│    └───────────────────┘                                                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 **Integration Patterns**

### **1. CDC Integration with @unhinged/events**

```typescript
// packages/observability/src/integration/CDCIntegration.ts
import { EventEmitter } from '@unhinged/events';
import { LogEvent, TraceEvent } from '../generated/observability';

export class CDCObservabilityIntegration {
  private eventEmitter: EventEmitter;

  constructor(eventEmitter: EventEmitter) {
    this.eventEmitter = eventEmitter;
  }

  /**
   * Emit log entry as CDC event
   */
  async emitLogEvent(logEntry: LogEntry): Promise<void> {
    const cdcEvent: LogEvent = {
      eventId: generateEventId(),
      timestamp: { seconds: Math.floor(Date.now() / 1000), nanos: 0 },
      eventType: 'log_entry',
      sequenceNumber: await this.getNextSequenceNumber(),

      traceContext: {
        traceId: logEntry.traceId || '',
        spanId: logEntry.spanId || '',
        correlationId: logEntry.metadata?.correlationId,
        requestId: logEntry.metadata?.requestId,
        sessionId: logEntry.sessionId || '',
        userId: logEntry.userId || '',
      },

      resource: {
        serviceName: logEntry.service,
        serviceVersion: process.env.SERVICE_VERSION || '1.0.0',
        deploymentEnvironment: process.env.NODE_ENV || 'development',
        attributes: {
          'host.name': os.hostname(),
          'process.pid': process.pid.toString(),
        }
      },

      level: this.mapLogLevel(logEntry.level),
      message: logEntry.message,
      metadata: this.structFromObject(logEntry.metadata || {}),

      destinations: {
        console: true,
        cdcStream: true,
        dataLake: this.shouldSendToDataLake(logEntry),
        dataLakeOptions: {
          tableName: 'observability_logs',
          partitionStrategy: 'date_hour_service',
          batchSize: 1000,
          flushIntervalSeconds: 60,
          compression: CompressionType.COMPRESSION_SNAPPY
        }
      },

      partitionInfo: {
        datePartition: new Date().toISOString().split('T')[0],
        hourPartition: new Date().getHours().toString().padStart(2, '0'),
        servicePartition: logEntry.service,
        levelPartition: logEntry.level,
        customPartitions: {
          'user_id': logEntry.userId || 'anonymous',
          'session_id': logEntry.sessionId || 'no_session'
        }
      }
    };

    // Emit to CDC stream
    await this.eventEmitter.emit('observability.log_entry', cdcEvent);
  }

  private shouldSendToDataLake(logEntry: LogEntry): boolean {
    // Send to data lake based on level and service
    if (logEntry.level === 'error' || logEntry.level === 'fatal') {
      return true;
    }

    // Send analytics and audit logs to data lake
    if (logEntry.service.includes('analytics') ||
        logEntry.metadata?.category === 'audit') {
      return true;
    }

    // Sample other logs based on configuration
    return Math.random() < 0.1; // 10% sampling for regular logs
  }

  private async getNextSequenceNumber(): Promise<number> {
    // Implementation depends on your CDC sequence management
    return Date.now();
  }
}
```

### **2. Flink Stream Processing Configuration**

```yaml
# flink-observability-job.yaml
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: observability-processor
spec:
  image: flink:1.17-scala_2.12-java11
  flinkVersion: v1_17
  flinkConfiguration:
    taskmanager.numberOfTaskSlots: "4"
    state.backend: rocksdb
    state.checkpoints.dir: "s3://unhinged-checkpoints/observability"
    execution.checkpointing.interval: "60s"
    execution.checkpointing.min-pause: "30s"

  serviceAccount: flink-service-account

  jobManager:
    resource:
      memory: "1024m"
      cpu: 1

  taskManager:
    resource:
      memory: "2048m"
      cpu: 2
    replicas: 3

  job:
    jarURI: "s3://unhinged-jars/observability-processor-1.0.0.jar"
    parallelism: 6
    upgradeMode: stateless

    args:
      - "--kafka.bootstrap.servers=kafka:9092"
      - "--kafka.group.id=observability-processor"
      - "--kafka.topics=observability.traces,observability.metrics,observability.logs"
      - "--data-lake.path=s3://unhinged-data-lake/observability/"
      - "--data-lake.format=parquet"
      - "--alerting.webhook=https://alerts.unhinged.ai/webhook"
```

### **3. Docker Compose for Development**

```yaml
# docker-compose.observability.yml
version: '3.8'

services:
  # OpenTelemetry Collector
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.88.0
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./configs/otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
      - "8889:8889"   # Prometheus metrics
      - "8888:8888"   # Collector metrics
    environment:
      - KAFKA_BROKERS=kafka:9092
      - JAEGER_ENDPOINT=jaeger:14250
    depends_on:
      - kafka
      - jaeger
    networks:
      - observability

  # Jaeger for trace visualization
  jaeger:
    image: jaegertracing/all-in-one:1.50
    ports:
      - "16686:16686"  # Jaeger UI
      - "14250:14250"  # gRPC collector
    environment:
      - COLLECTOR_OTLP_ENABLED=true
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - observability

  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:v2.47.0
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    networks:
      - observability

  # Grafana for visualization
  grafana:
    image: grafana/grafana:10.1.0
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./configs/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./configs/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - observability

  # Elasticsearch for Jaeger storage
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - observability

  # Kafka for CDC events
  kafka:
    image: confluentinc/cp-kafka:7.4.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: true
    depends_on:
      - zookeeper
    networks:
      - observability

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - observability

  # Redis for caching and rate limiting
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    networks:
      - observability

volumes:
  grafana-storage:
  elasticsearch-data:

networks:
  observability:
    driver: bridge
```

## 📊 **Performance Recommendations**

### **Sampling Strategy Summary**

| Service Type | Base Sampling | Error Sampling | Critical Operations |
|--------------|---------------|----------------|-------------------|
| Frontend     | 1%            | 100%           | 5% (user actions) |
| Gateway      | 10%           | 100%           | 20% (WebSocket)   |
| Backend      | 20%           | 100%           | 50% (business)    |
| Critical     | 80%           | 100%           | 100% (auth/pay)   |

### **Resource Allocation**

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| OTEL Collector | 200m | 500m | 256Mi | 512Mi |
| Jaeger | 100m | 300m | 512Mi | 1Gi |
| Prometheus | 200m | 1000m | 1Gi | 2Gi |
| Grafana | 100m | 200m | 256Mi | 512Mi |

### **Network Optimization**

- **Compression**: Use Snappy for Kafka, Gzip for OTLP
- **Batching**: 1s timeout, 1024 batch size for traces
- **Connection Pooling**: Keep-alive 30s, max 16 concurrent streams
- **Sampling**: Adaptive sampling based on service load

## 🚀 **Quick Start Commands**

```bash
# 1. Start observability stack
docker-compose -f docker-compose.observability.yml up -d

# 2. Generate proto bindings with observability
./proto/build.sh
./proto/build-gateway.sh

# 3. Install observability library
npm install @unhinged/observability

# 4. Configure environment
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_SERVICE_NAME=your-service-name
export OTEL_RESOURCE_ATTRIBUTES=service.version=1.0.0

# 5. Start your services with observability
npm run dev  # Frontend
make gateway-dev  # Gateway
make backend-run  # Backend
```

## 📈 **Monitoring URLs**

- **Jaeger UI**: http://localhost:16686
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Gateway Docs**: http://localhost:8082/docs
- **Gateway Metrics**: http://localhost:8082/metrics

This comprehensive observability solution provides:

✅ **Unified logging** with Unix-style permission flags
✅ **OpenTelemetry integration** across all languages
✅ **CDC event stream** integration with dual persistence
✅ **Scalable architecture** with Flink stream processing
✅ **Performance optimization** with intelligent sampling
✅ **Complete deployment** configuration for development and production
```
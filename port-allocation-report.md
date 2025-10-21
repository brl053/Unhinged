# Unhinged Port Allocation Report
# Generated: 2025-10-20T18:22:08.024635

## Current Port Allocations

⚠️  **Port 2181** - CONFLICT
   - zookeeper (From docker-compose.yml)
   - zookeeper (From build-config.yml)

⚠️  **Port 3000** - CONFLICT
   - frontend (From docker-compose.yml)
   - grafana (From docker-compose.all.yml)
   - grafana (From docker-compose.yml)

✅ **Port 3001** - OK
   - grafana (From docker-compose.observability.yml)

✅ **Port 3100** - OK
   - loki (From docker-compose.observability.yml)

✅ **Port 3200** - OK
   - tempo (From docker-compose.observability.yml)

✅ **Port 4317** - OK
   - tempo (From docker-compose.observability.yml)

✅ **Port 4318** - OK
   - tempo (From docker-compose.observability.yml)

✅ **Port 4319** - OK
   - otel-collector (From docker-compose.observability.yml)

✅ **Port 4320** - OK
   - otel-collector (From docker-compose.observability.yml)

✅ **Port 5432** - OK
   - database (From build-config.yml)

✅ **Port 5433** - OK
   - postgres (From docker-compose.simple.yml)

⚠️  **Port 6379** - CONFLICT
   - redis (From docker-compose.yml)
   - redis (From docker-compose.all.yml)
   - redis (From docker-compose.yml)

✅ **Port 7077** - OK
   - spark-master (From docker-compose.yml)

⚠️  **Port 7474** - CONFLICT
   - neo4j (From docker-compose.all.yml)
   - neo4j (From docker-compose.yml)

⚠️  **Port 7687** - CONFLICT
   - neo4j (From docker-compose.all.yml)
   - neo4j (From docker-compose.yml)

⚠️  **Port 8000** - CONFLICT
   - speech-to-text (From docker-compose.yml)
   - whisper-tts (From docker-compose.simple.yml)
   - whisper-tts (From build-config.yml)

⚠️  **Port 8001** - CONFLICT
   - vision-ai (From docker-compose.yml)
   - vision-ai (From docker-compose.simple.yml)

✅ **Port 8002** - OK
   - text-to-speech (From docker-compose.yml)

⚠️  **Port 8080** - CONFLICT
   - backend (From docker-compose.yml)
   - database (From docker-compose.yml)
   - cockroachdb (From docker-compose.all.yml)
   - cockroachdb (From docker-compose.yml)
   - backend (From build-config.yml)

⚠️  **Port 8081** - CONFLICT
   - cdc-service (From docker-compose.yml)
   - flink-jobmanager (From docker-compose.yml)
   - weaviate (From docker-compose.all.yml)
   - weaviate (From docker-compose.yml)

✅ **Port 8082** - OK
   - spark-master (From docker-compose.yml)

✅ **Port 8083** - OK
   - weaviate (From docker-compose.yml)

✅ **Port 8084** - OK
   - chroma (From docker-compose.yml)

✅ **Port 8085** - OK
   - kafka-ui (From docker-compose.yml)

⚠️  **Port 8090** - CONFLICT
   - persistence-platform (From docker-compose.all.yml)
   - persistence-platform (From docker-compose.yml)

✅ **Port 8889** - OK
   - otel-collector (From docker-compose.observability.yml)

⚠️  **Port 9000** - CONFLICT
   - minio (From docker-compose.all.yml)
   - minio (From docker-compose.yml)

⚠️  **Port 9001** - CONFLICT
   - minio (From docker-compose.all.yml)
   - minio (From docker-compose.yml)

⚠️  **Port 9042** - CONFLICT
   - cassandra (From docker-compose.yml)
   - cassandra (From docker-compose.all.yml)
   - cassandra (From docker-compose.yml)

⚠️  **Port 9090** - CONFLICT
   - prometheus (From docker-compose.observability.yml)
   - persistence-platform (From docker-compose.all.yml)
   - prometheus (From docker-compose.all.yml)
   - persistence-platform (From docker-compose.yml)
   - prometheus (From docker-compose.yml)

✅ **Port 9091** - OK
   - whisper-tts (From docker-compose.simple.yml)

⚠️  **Port 9092** - CONFLICT
   - kafka (From docker-compose.yml)
   - vision-ai (From docker-compose.simple.yml)
   - kafka (From build-config.yml)

⚠️  **Port 9200** - CONFLICT
   - elasticsearch (From docker-compose.yml)
   - elasticsearch (From docker-compose.all.yml)
   - elasticsearch (From docker-compose.yml)

⚠️  **Port 9300** - CONFLICT
   - elasticsearch (From docker-compose.yml)
   - elasticsearch (From docker-compose.all.yml)
   - elasticsearch (From docker-compose.yml)

⚠️  **Port 11434** - CONFLICT
   - llm (From docker-compose.yml)
   - llm (From build-config.yml)

⚠️  **Port 14268** - CONFLICT
   - jaeger (From docker-compose.all.yml)
   - jaeger (From docker-compose.yml)

⚠️  **Port 16686** - CONFLICT
   - jaeger (From docker-compose.all.yml)
   - jaeger (From docker-compose.yml)

⚠️  **Port 26257** - CONFLICT
   - database (From docker-compose.yml)
   - cockroachdb (From docker-compose.all.yml)
   - cockroachdb (From docker-compose.yml)

⚠️  **Port 27017** - CONFLICT
   - mongodb (From docker-compose.all.yml)
   - mongodb (From docker-compose.yml)

## Recommendations

### Standard Port Ranges
- **Frontend Services**: 3000-3099
- **Backend APIs**: 8000-8099
- **Databases**: 5400-5499
- **Message Queues**: 9090-9199
- **Monitoring**: 9200-9299
- **Admin UIs**: 8100-8199

### Conflict Resolution Priority
1. Move admin UIs to higher ports (8100+)
2. Keep core services on standard ports
3. Use internal Docker networking where possible

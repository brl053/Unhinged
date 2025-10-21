#!/bin/bash
# Unhinged Production Port Reset Script
# @llm-type infrastructure-script
# @llm-legend Comprehensive port reset implementing categorical allocation
# @llm-key Atomic migration to conflict-free port allocation across all services
# @llm-map Production deployment script for Unhinged port architecture
# @llm-axiom Port reset must be atomic, reversible, and preserve functionality
# @llm-token port-reset-script: Production port migration with safety guarantees

set -e

echo '🔧 Unhinged Production Port Reset'
echo '=================================='
echo ''
echo '📋 Implementing categorical port allocation:'
echo '   Frontend:      1000-1099'
echo '   Backend APIs:  1100-1199'
echo '   Databases:     1200-1299'
echo '   Vector/AI:     1300-1399'
echo '   Messaging:     1400-1499'
echo '   AI/ML:         1500-1599'
echo '   Admin UIs:     1600-1699'
echo '   Storage:       1700-1799'
echo '   Observability: 1800-1899'
echo '   Platform:      1900-1999'
echo ''

# Create timestamped backup
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo '💾 Creating backups with timestamp: '$BACKUP_TIMESTAMP

cp build-config.yml build-config.yml.backup.$BACKUP_TIMESTAMP
cp docker-compose.observability.yml docker-compose.observability.yml.backup.$BACKUP_TIMESTAMP
cp docker-compose.simple.yml docker-compose.simple.yml.backup.$BACKUP_TIMESTAMP
cp docker-compose.yml docker-compose.yml.backup.$BACKUP_TIMESTAMP
cp platforms/docker-compose.all.yml platforms/docker-compose.all.yml.backup.$BACKUP_TIMESTAMP

echo '✅ Backups created'
echo ''

echo '🔄 Resetting Web interfaces and user-facing applications (1000-1099)'

# Reset frontend to 1000:3000 in docker-compose.yml
echo '  📍 frontend: 1000:3000 (docker-compose.yml)'
sed -i 's/[0-9]\+:3000/1000:3000/g' docker-compose.yml


echo '🔄 Resetting REST APIs and application services (1100-1199)'

# Reset backend to 1100:8080 in docker-compose.yml
echo '  📍 backend: 1100:8080 (docker-compose.yml)'
sed -i 's/[0-9]\+:8080/1100:8080/g' docker-compose.yml

# Reset backend to 1100:8080 in build-config.yml
echo '  📍 backend: 1100:8080 (build-config.yml)'
sed -i 's/[0-9]\+:8080/1100:8080/g' build-config.yml

# Reset speech-to-text to 1101:8000 in docker-compose.yml
echo '  📍 speech-to-text: 1101:8000 (docker-compose.yml)'
sed -i 's/[0-9]\+:8000/1101:8000/g' docker-compose.yml

# Reset text-to-speech to 1102:8000 in docker-compose.yml
echo '  📍 text-to-speech: 1102:8000 (docker-compose.yml)'
sed -i 's/[0-9]\+:8000/1102:8000/g' docker-compose.yml

# Reset vision-ai to 1103:8000 in docker-compose.yml
echo '  📍 vision-ai: 1103:8000 (docker-compose.yml)'
sed -i 's/[0-9]\+:8000/1103:8000/g' docker-compose.yml

# Reset vision-ai to 1103:8000 in docker-compose.simple.yml
echo '  📍 vision-ai: 1103:8000 (docker-compose.simple.yml)'
sed -i 's/[0-9]\+:8000/1103:8000/g' docker-compose.simple.yml

# Reset whisper-tts to 1104:8000 in build-config.yml
echo '  📍 whisper-tts: 1104:8000 (build-config.yml)'
sed -i 's/[0-9]\+:8000/1104:8000/g' build-config.yml

# Reset whisper-tts to 1104:8000 in docker-compose.simple.yml
echo '  📍 whisper-tts: 1104:8000 (docker-compose.simple.yml)'
sed -i 's/[0-9]\+:8000/1104:8000/g' docker-compose.simple.yml


echo '🔄 Resetting SQL, NoSQL, and graph databases (1200-1299)'

# Reset cassandra to 1207:9042 in docker-compose.yml
echo '  📍 cassandra: 1207:9042 (docker-compose.yml)'
sed -i 's/[0-9]\+:9042/1207:9042/g' docker-compose.yml

# Reset cassandra to 1207:9042 in platforms/docker-compose.all.yml
echo '  📍 cassandra: 1207:9042 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:9042/1207:9042/g' platforms/docker-compose.all.yml

# Reset cockroachdb to 1202:26257 in docker-compose.yml
echo '  📍 cockroachdb: 1202:26257 (docker-compose.yml)'
sed -i 's/[0-9]\+:26257/1202:26257/g' docker-compose.yml

# Reset cockroachdb to 1202:26257 in platforms/docker-compose.all.yml
echo '  📍 cockroachdb: 1202:26257 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:26257/1202:26257/g' platforms/docker-compose.all.yml

# Reset cockroachdb-ui to 1203:8080 in docker-compose.yml
echo '  📍 cockroachdb-ui: 1203:8080 (docker-compose.yml)'
sed -i 's/[0-9]\+:8080/1203:8080/g' docker-compose.yml

# Reset cockroachdb-ui to 1203:8080 in platforms/docker-compose.all.yml
echo '  📍 cockroachdb-ui: 1203:8080 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:8080/1203:8080/g' platforms/docker-compose.all.yml

# Reset database to 1200:5432 in docker-compose.yml
echo '  📍 database: 1200:5432 (docker-compose.yml)'
sed -i 's/[0-9]\+:5432/1200:5432/g' docker-compose.yml

# Reset database to 1200:5432 in build-config.yml
echo '  📍 database: 1200:5432 (build-config.yml)'
sed -i 's/[0-9]\+:5432/1200:5432/g' build-config.yml

# Reset mongodb to 1204:27017 in docker-compose.yml
echo '  📍 mongodb: 1204:27017 (docker-compose.yml)'
sed -i 's/[0-9]\+:27017/1204:27017/g' docker-compose.yml

# Reset mongodb to 1204:27017 in platforms/docker-compose.all.yml
echo '  📍 mongodb: 1204:27017 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:27017/1204:27017/g' platforms/docker-compose.all.yml

# Reset neo4j-bolt to 1206:7687 in docker-compose.yml
echo '  📍 neo4j-bolt: 1206:7687 (docker-compose.yml)'
sed -i 's/[0-9]\+:7687/1206:7687/g' docker-compose.yml

# Reset neo4j-bolt to 1206:7687 in platforms/docker-compose.all.yml
echo '  📍 neo4j-bolt: 1206:7687 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:7687/1206:7687/g' platforms/docker-compose.all.yml

# Reset neo4j-http to 1205:7474 in docker-compose.yml
echo '  📍 neo4j-http: 1205:7474 (docker-compose.yml)'
sed -i 's/[0-9]\+:7474/1205:7474/g' docker-compose.yml

# Reset neo4j-http to 1205:7474 in platforms/docker-compose.all.yml
echo '  📍 neo4j-http: 1205:7474 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:7474/1205:7474/g' platforms/docker-compose.all.yml

# Reset postgres to 1201:5432 in docker-compose.simple.yml
echo '  📍 postgres: 1201:5432 (docker-compose.simple.yml)'
sed -i 's/[0-9]\+:5432/1201:5432/g' docker-compose.simple.yml


echo '🔄 Resetting Vector databases and AI data stores (1300-1399)'

# Reset chroma to 1301:8000 in docker-compose.yml
echo '  📍 chroma: 1301:8000 (docker-compose.yml)'
sed -i 's/[0-9]\+:8000/1301:8000/g' docker-compose.yml

# Reset elasticsearch to 1303:9200 in docker-compose.yml
echo '  📍 elasticsearch: 1303:9200 (docker-compose.yml)'
sed -i 's/[0-9]\+:9200/1303:9200/g' docker-compose.yml

# Reset elasticsearch to 1303:9200 in platforms/docker-compose.all.yml
echo '  📍 elasticsearch: 1303:9200 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:9200/1303:9200/g' platforms/docker-compose.all.yml

# Reset redis to 1302:6379 in docker-compose.yml
echo '  📍 redis: 1302:6379 (docker-compose.yml)'
sed -i 's/[0-9]\+:6379/1302:6379/g' docker-compose.yml

# Reset redis to 1302:6379 in platforms/docker-compose.all.yml
echo '  📍 redis: 1302:6379 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:6379/1302:6379/g' platforms/docker-compose.all.yml

# Reset weaviate to 1300:8080 in docker-compose.yml
echo '  📍 weaviate: 1300:8080 (docker-compose.yml)'
sed -i 's/[0-9]\+:8080/1300:8080/g' docker-compose.yml

# Reset weaviate to 1300:8080 in platforms/docker-compose.all.yml
echo '  📍 weaviate: 1300:8080 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:8080/1300:8080/g' platforms/docker-compose.all.yml


echo '🔄 Resetting Event streaming and message brokers (1400-1499)'

# Reset cdc-service to 1402:8080 in docker-compose.yml
echo '  📍 cdc-service: 1402:8080 (docker-compose.yml)'
sed -i 's/[0-9]\+:8080/1402:8080/g' docker-compose.yml

# Reset kafka to 1400:9092 in docker-compose.yml
echo '  📍 kafka: 1400:9092 (docker-compose.yml)'
sed -i 's/[0-9]\+:9092/1400:9092/g' docker-compose.yml

# Reset kafka to 1400:9092 in build-config.yml
echo '  📍 kafka: 1400:9092 (build-config.yml)'
sed -i 's/[0-9]\+:9092/1400:9092/g' build-config.yml

# Reset zookeeper to 1401:2181 in docker-compose.yml
echo '  📍 zookeeper: 1401:2181 (docker-compose.yml)'
sed -i 's/[0-9]\+:2181/1401:2181/g' docker-compose.yml

# Reset zookeeper to 1401:2181 in build-config.yml
echo '  📍 zookeeper: 1401:2181 (build-config.yml)'
sed -i 's/[0-9]\+:2181/1401:2181/g' build-config.yml


echo '🔄 Resetting Machine learning and AI processing (1500-1599)'

# Reset flink-jobmanager to 1501:8081 in docker-compose.yml
echo '  📍 flink-jobmanager: 1501:8081 (docker-compose.yml)'
sed -i 's/[0-9]\+:8081/1501:8081/g' docker-compose.yml

# Reset llm to 1500:11434 in docker-compose.yml
echo '  📍 llm: 1500:11434 (docker-compose.yml)'
sed -i 's/[0-9]\+:11434/1500:11434/g' docker-compose.yml

# Reset llm to 1500:11434 in build-config.yml
echo '  📍 llm: 1500:11434 (build-config.yml)'
sed -i 's/[0-9]\+:11434/1500:11434/g' build-config.yml

# Reset spark-master to 1502:7077 in docker-compose.yml
echo '  📍 spark-master: 1502:7077 (docker-compose.yml)'
sed -i 's/[0-9]\+:7077/1502:7077/g' docker-compose.yml


echo '🔄 Resetting Management and administrative interfaces (1600-1699)'

# Reset kafka-ui to 1600:8080 in docker-compose.yml
echo '  📍 kafka-ui: 1600:8080 (docker-compose.yml)'
sed -i 's/[0-9]\+:8080/1600:8080/g' docker-compose.yml

# Reset persistence-platform-ui to 1602:9090 in platforms/docker-compose.all.yml
echo '  📍 persistence-platform-ui: 1602:9090 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:9090/1602:9090/g' platforms/docker-compose.all.yml

# Reset spark-ui to 1601:8080 in docker-compose.yml
echo '  📍 spark-ui: 1601:8080 (docker-compose.yml)'
sed -i 's/[0-9]\+:8080/1601:8080/g' docker-compose.yml


echo '🔄 Resetting Object storage and file systems (1700-1799)'

# Reset minio-api to 1700:9000 in docker-compose.yml
echo '  📍 minio-api: 1700:9000 (docker-compose.yml)'
sed -i 's/[0-9]\+:9000/1700:9000/g' docker-compose.yml

# Reset minio-api to 1700:9000 in platforms/docker-compose.all.yml
echo '  📍 minio-api: 1700:9000 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:9000/1700:9000/g' platforms/docker-compose.all.yml

# Reset minio-console to 1701:9001 in docker-compose.yml
echo '  📍 minio-console: 1701:9001 (docker-compose.yml)'
sed -i 's/[0-9]\+:9001/1701:9001/g' docker-compose.yml

# Reset minio-console to 1701:9001 in platforms/docker-compose.all.yml
echo '  📍 minio-console: 1701:9001 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:9001/1701:9001/g' platforms/docker-compose.all.yml


echo '🔄 Resetting Monitoring, logging, and tracing (1800-1899)'

# Reset grafana to 1807:3000 in docker-compose.yml
echo '  📍 grafana: 1807:3000 (docker-compose.yml)'
sed -i 's/[0-9]\+:3000/1807:3000/g' docker-compose.yml

# Reset grafana to 1807:3000 in docker-compose.observability.yml
echo '  📍 grafana: 1807:3000 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:3000/1807:3000/g' docker-compose.observability.yml

# Reset grafana to 1807:3000 in platforms/docker-compose.all.yml
echo '  📍 grafana: 1807:3000 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:3000/1807:3000/g' platforms/docker-compose.all.yml

# Reset jaeger-collector to 1801:14268 in platforms/docker-compose.all.yml
echo '  📍 jaeger-collector: 1801:14268 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:14268/1801:14268/g' platforms/docker-compose.all.yml

# Reset jaeger-ui to 1800:16686 in platforms/docker-compose.all.yml
echo '  📍 jaeger-ui: 1800:16686 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:16686/1800:16686/g' platforms/docker-compose.all.yml

# Reset loki to 1802:3100 in docker-compose.observability.yml
echo '  📍 loki: 1802:3100 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:3100/1802:3100/g' docker-compose.observability.yml

# Reset otel-collector-grpc to 1808:4317 in docker-compose.observability.yml
echo '  📍 otel-collector-grpc: 1808:4317 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:4317/1808:4317/g' docker-compose.observability.yml

# Reset otel-collector-http to 1809:4318 in docker-compose.observability.yml
echo '  📍 otel-collector-http: 1809:4318 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:4318/1809:4318/g' docker-compose.observability.yml

# Reset otel-collector-metrics to 1810:8889 in docker-compose.observability.yml
echo '  📍 otel-collector-metrics: 1810:8889 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:8889/1810:8889/g' docker-compose.observability.yml

# Reset prometheus to 1806:9090 in docker-compose.yml
echo '  📍 prometheus: 1806:9090 (docker-compose.yml)'
sed -i 's/[0-9]\+:9090/1806:9090/g' docker-compose.yml

# Reset prometheus to 1806:9090 in docker-compose.observability.yml
echo '  📍 prometheus: 1806:9090 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:9090/1806:9090/g' docker-compose.observability.yml

# Reset prometheus to 1806:9090 in platforms/docker-compose.all.yml
echo '  📍 prometheus: 1806:9090 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:9090/1806:9090/g' platforms/docker-compose.all.yml

# Reset tempo-grpc to 1804:4317 in docker-compose.observability.yml
echo '  📍 tempo-grpc: 1804:4317 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:4317/1804:4317/g' docker-compose.observability.yml

# Reset tempo-http to 1803:3200 in docker-compose.observability.yml
echo '  📍 tempo-http: 1803:3200 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:3200/1803:3200/g' docker-compose.observability.yml

# Reset tempo-otlp to 1805:4318 in docker-compose.observability.yml
echo '  📍 tempo-otlp: 1805:4318 (docker-compose.observability.yml)'
sed -i 's/[0-9]\+:4318/1805:4318/g' docker-compose.observability.yml


echo '🔄 Resetting Core platform and infrastructure (1900-1999)'

# Reset persistence-platform-api to 1900:8080 in platforms/docker-compose.all.yml
echo '  📍 persistence-platform-api: 1900:8080 (platforms/docker-compose.all.yml)'
sed -i 's/[0-9]\+:8080/1900:8080/g' platforms/docker-compose.all.yml


echo '✅ Port reset completed!'
echo ''
echo '🔍 Validating new port allocation...'
cd build && python3 port_allocator.py --validate

echo ''
echo '🎉 Unhinged port reset successful!'
echo ''
echo '📊 New port allocation:'
cd build && python3 port_allocator.py --summary

echo ''
echo '🚀 Ready to start services with conflict-free ports!'
echo 'Run: make start'

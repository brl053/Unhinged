# 📊 Prometheus Metrics Monitoring Guide

## 🎯 Key Metrics Dashboard

### **Service Health Metrics**
```promql
# Service availability
up{job=~"unhinged-.*"}

# Service uptime
(time() - process_start_time_seconds{job="unhinged-backend"}) / 3600

# HTTP request rate
rate(http_server_requests_total[5m])

# Error rate
rate(http_server_requests_total{status=~"4..|5.."}[5m]) / rate(http_server_requests_total[5m]) * 100
```

### **Performance Metrics**
```promql
# Response time percentiles
histogram_quantile(0.95, rate(http_server_request_duration_seconds_bucket[5m]))
histogram_quantile(0.50, rate(http_server_request_duration_seconds_bucket[5m]))

# Request throughput
sum(rate(http_server_requests_total[5m])) by (job)

# Active connections
http_server_active_connections
```

### **JVM Metrics (Backend)**
```promql
# Memory usage
jvm_memory_used_bytes{job="unhinged-backend"}
jvm_memory_max_bytes{job="unhinged-backend"}

# Memory utilization percentage
(jvm_memory_used_bytes / jvm_memory_max_bytes) * 100

# Garbage collection
rate(jvm_gc_collection_seconds_total[5m])
jvm_gc_collection_seconds_count

# Thread count
jvm_threads_current
jvm_threads_peak
```

### **System Metrics**
```promql
# CPU usage
process_cpu_seconds_total
rate(process_cpu_seconds_total[5m]) * 100

# File descriptors
process_files_open_files
process_files_max_files

# Network I/O
rate(process_network_receive_bytes_total[5m])
rate(process_network_transmit_bytes_total[5m])
```

## 🔍 Monitoring Queries

### **Health Dashboard Queries**
```bash
# Check all services status
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result[] | {job: .metric.job, status: .value[1]}'

# Get response time for backend
curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_server_request_duration_seconds_bucket{job=\"unhinged-backend\"}[5m]))"

# Check memory usage
curl -s "http://localhost:9090/api/v1/query?query=jvm_memory_used_bytes{job=\"unhinged-backend\",area=\"heap\"}"

# Error rate calculation
curl -s "http://localhost:9090/api/v1/query?query=rate(http_server_requests_total{status=~\"4..|5..\"}[5m]) / rate(http_server_requests_total[5m]) * 100"
```

### **Alerting Thresholds**
```promql
# High error rate (>5%)
rate(http_server_requests_total{status=~"4..|5.."}[5m]) / rate(http_server_requests_total[5m]) * 100 > 5

# High response time (>1s for 95th percentile)
histogram_quantile(0.95, rate(http_server_request_duration_seconds_bucket[5m])) > 1

# High memory usage (>80%)
(jvm_memory_used_bytes / jvm_memory_max_bytes) * 100 > 80

# Service down
up == 0
```

## 📈 Custom Metrics

### **Unhinged-Specific Metrics**
```promql
# Chat request metrics (when implemented)
unhinged_chat_requests_total
unhinged_chat_request_duration_seconds

# AI service metrics
unhinged_vision_processing_duration_seconds
unhinged_tts_generation_duration_seconds

# Consciousness metrics
unhinged_consciousness_state_changes_total
unhinged_multimodal_coordination_latency_seconds
```

## 🎯 Monitoring Best Practices

### **1. Key Performance Indicators (KPIs)**
- **Availability**: `up` metric for all services
- **Latency**: 95th percentile response times
- **Throughput**: Requests per second
- **Error Rate**: 4xx/5xx response percentage
- **Resource Utilization**: CPU, Memory, Disk

### **2. Monitoring Frequency**
- **Real-time**: 5-15 second intervals for critical metrics
- **Historical**: 1-5 minute intervals for trends
- **Long-term**: 1-hour intervals for capacity planning

### **3. Alert Conditions**
- Service down for >30 seconds
- Error rate >5% for >2 minutes
- Response time >1s for >5 minutes
- Memory usage >80% for >10 minutes
- Disk usage >90%

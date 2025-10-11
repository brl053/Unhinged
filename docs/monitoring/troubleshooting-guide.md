# 🛠️ Unhinged Troubleshooting Workflow

## 🚨 Step-by-Step Diagnostic Process

### **Phase 1: Initial Assessment (2 minutes)**

```bash
# 1. Quick system overview
./scripts/health-check.sh --quick

# 2. Check running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 3. Check system resources
df -h                    # Disk space
free -h                  # Memory
top -bn1 | head -20      # CPU usage
```

### **Phase 2: Service-Specific Diagnosis (5 minutes)**

```bash
# 4. Identify failing service
./scripts/health-check.sh

# 5. Check specific service health
./scripts/health-check.sh --service [failing-service]

# 6. Check service logs
docker logs [container-name] --tail 50
# OR for backend:
tail -f backend/logs/application.log
```

### **Phase 3: Deep Dive Analysis (10 minutes)**

```bash
# 7. Check metrics for patterns
curl -s "http://localhost:9090/api/v1/query?query=up" | jq .

# 8. Check network connectivity
curl -v http://localhost:8080/health
curl -v http://localhost:8001/health

# 9. Check resource constraints
docker stats --no-stream
```

## 🔍 Common Issues & Solutions

### **Backend Service Issues**

#### **Issue: Backend Not Starting**
```bash
# Symptoms
curl http://localhost:8080/health
# Connection refused

# Diagnosis
cd backend && ./gradlew build
docker logs unhinged-backend 2>&1 | tail -20

# Common Causes & Solutions
# 1. Port already in use
lsof -i :8080
kill [PID]

# 2. Database connection failure
./scripts/health-check.sh --service database
docker-compose up -d postgres

# 3. Build/compilation errors
cd backend && ./gradlew clean build
```

#### **Issue: Backend Responding Slowly**
```bash
# Symptoms
curl -w "@curl-format.txt" http://localhost:8080/health

# Diagnosis
curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_server_request_duration_seconds_bucket[5m]))"

# Solutions
# 1. Check JVM memory
curl -s http://localhost:8080/metrics | grep jvm_memory

# 2. Check database performance
PGPASSWORD=password psql -h localhost -p 5433 -U postgres -d unhinged -c "SELECT * FROM pg_stat_activity;"

# 3. Restart service
docker restart unhinged-backend
```

### **AI Services Issues**

#### **Issue: Vision AI Service Down**
```bash
# Symptoms
curl http://localhost:8001/health
# Connection refused or 500 error

# Diagnosis
docker logs vision-ai-service --tail 50

# Common Solutions
# 1. GPU/CUDA issues
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# 2. Model loading failure
docker exec -it vision-ai-service ls -la /app/models/

# 3. Memory issues
docker stats vision-ai-service --no-stream

# 4. Restart service
docker restart vision-ai-service
```

#### **Issue: Whisper TTS Service Errors**
```bash
# Diagnosis
curl -s http://localhost:8000/health | jq .
docker logs whisper-tts-service --tail 30

# Common Solutions
# 1. Audio model issues
docker exec -it whisper-tts-service python -c "import whisper; print(whisper.available_models())"

# 2. Audio processing errors
# Check for corrupted audio files or unsupported formats

# 3. Resource constraints
# Whisper requires significant CPU/GPU for processing
```

### **Database Issues**

#### **Issue: PostgreSQL Connection Failures**
```bash
# Symptoms
./scripts/health-check.sh --service database
# Connection failed

# Diagnosis
docker logs unhinged-postgres --tail 20
docker exec -it unhinged-postgres pg_isready

# Solutions
# 1. Container not running
docker start unhinged-postgres

# 2. Port conflicts
lsof -i :5433
docker port unhinged-postgres

# 3. Authentication issues
PGPASSWORD=password psql -h localhost -p 5433 -U postgres -c "SELECT 1;"

# 4. Database corruption (rare)
docker exec -it unhinged-postgres pg_dump unhinged > backup.sql
```

### **Observability Stack Issues**

#### **Issue: Grafana Not Accessible**
```bash
# Symptoms
curl http://localhost:3001/api/health
# Connection refused

# Diagnosis
docker logs unhinged-grafana --tail 20

# Solutions
# 1. Container restart
docker restart unhinged-grafana

# 2. Port conflicts
lsof -i :3001

# 3. Volume/permission issues
docker volume inspect unhinged_grafana-storage
```

#### **Issue: Prometheus Not Collecting Metrics**
```bash
# Symptoms
curl -s "http://localhost:9090/api/v1/query?query=up" | jq '.data.result | length'
# Returns 0 or fewer targets than expected

# Diagnosis
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health, lastError: .lastError}'

# Solutions
# 1. Check Prometheus config
docker exec -it unhinged-prometheus cat /etc/prometheus/prometheus.yml

# 2. Network connectivity
docker exec -it unhinged-prometheus wget -qO- http://backend:8080/metrics

# 3. Service discovery issues
# Ensure services are in the same Docker network
docker network ls
docker network inspect unhinged-network
```

## 📋 Log Locations

### **Service Logs**
```bash
# Backend (if running locally)
tail -f backend/logs/application.log
tail -f backend/logs/error.log

# Docker container logs
docker logs unhinged-backend --follow
docker logs vision-ai-service --follow
docker logs whisper-tts-service --follow
docker logs unhinged-postgres --follow

# Observability logs
docker logs unhinged-grafana --follow
docker logs unhinged-prometheus --follow
docker logs unhinged-loki --follow
```

### **System Logs**
```bash
# Docker daemon logs
journalctl -u docker.service --follow

# System resource logs
dmesg | tail -20
/var/log/syslog | tail -50
```

## 🚀 Recovery Procedures

### **Quick Recovery (Service Restart)**
```bash
# Restart specific service
docker restart [service-name]

# Restart all services
docker-compose restart

# Restart observability stack
docker-compose -f docker-compose.observability.yml restart
```

### **Full System Recovery**
```bash
# 1. Stop all services
docker-compose down
docker-compose -f docker-compose.observability.yml down

# 2. Clean up (if needed)
docker system prune -f
docker volume prune -f

# 3. Restart infrastructure
docker-compose -f docker-compose.observability.yml up -d
docker-compose up -d postgres

# 4. Wait for services to be ready
sleep 30

# 5. Start application services
cd backend && ./gradlew run &
docker-compose up -d vision-ai whisper-tts

# 6. Verify health
./scripts/health-check.sh
```

### **Emergency Contacts & Escalation**
```bash
# 1. Check system status
./scripts/health-check.sh > health-report.txt

# 2. Collect logs
mkdir -p debug-logs/$(date +%Y%m%d_%H%M%S)
docker logs unhinged-backend > debug-logs/backend.log
docker logs vision-ai-service > debug-logs/vision-ai.log
docker logs unhinged-grafana > debug-logs/grafana.log

# 3. System information
docker ps > debug-logs/containers.txt
docker stats --no-stream > debug-logs/resources.txt
df -h > debug-logs/disk.txt
```

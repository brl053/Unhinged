# 🎯 Unhinged Monitoring Quick Reference

## 🔗 Essential URLs
```bash
# Core Services
Backend API:        http://localhost:8080/health
Vision AI:          http://localhost:8001/health  
Whisper TTS:        http://localhost:8000/health
Context LLM:        http://localhost:8002/health

# Observability Stack
Grafana:            http://localhost:3001 (admin/unhinged_observability)
Prometheus:         http://localhost:9090
Loki:               http://localhost:3100
Metrics Endpoint:   http://localhost:8080/metrics

# Optional Services
Frontend:           http://localhost:3000
Kafka UI:           http://localhost:8090
Ollama:             http://localhost:11434
```

## ⚡ Quick Commands
```bash
# Health Checks
./scripts/health-check.sh --quick                    # Fast ping test
./scripts/health-check.sh                           # Full health check
./scripts/health-check.sh --service backend         # Specific service
./scripts/health-check.sh --service observability  # Monitoring stack

# Service Status
docker ps | grep unhinged                           # Running containers
curl -s http://localhost:8080/health | jq .         # Backend detailed health
curl -s http://localhost:3001/api/health | jq .     # Grafana health

# Metrics Queries
curl -s "http://localhost:9090/api/v1/query?query=up" | jq .
curl -s http://localhost:8080/metrics | grep jvm_memory
curl -s "http://localhost:9090/api/v1/targets" | jq '.data.activeTargets[].health'

# Logs
docker logs unhinged-backend --tail 20              # Backend logs
docker logs vision-ai-service --tail 20             # Vision AI logs
docker logs unhinged-grafana --tail 20              # Grafana logs

# Troubleshooting
lsof -i :8080                                       # Check port usage
docker stats --no-stream                           # Resource usage
docker system df                                    # Docker disk usage
```

## 🚨 Emergency Procedures
```bash
# Quick Restart
docker restart unhinged-backend
docker restart vision-ai-service
docker-compose -f docker-compose.observability.yml restart

# Full Recovery
docker-compose down && docker-compose up -d
./scripts/health-check.sh

# Collect Debug Info
mkdir debug-$(date +%Y%m%d_%H%M%S)
./scripts/health-check.sh > debug-*/health.txt
docker logs unhinged-backend > debug-*/backend.log
docker ps > debug-*/containers.txt
```

## 📊 Key Metrics Thresholds
```bash
# Service Health
up == 1                                             # Service is running
up == 0                                             # Service is down

# Performance
response_time_95th < 1s                             # Good performance
response_time_95th > 2s                             # Performance issue
error_rate < 5%                                     # Acceptable error rate
error_rate > 10%                                    # Critical error rate

# Resources
jvm_memory_usage < 80%                              # Healthy memory
jvm_memory_usage > 90%                              # Memory pressure
cpu_usage < 70%                                     # Normal CPU load
cpu_usage > 90%                                     # High CPU load
```

## 🎯 Monitoring Checklist
```bash
# Daily Health Check
□ ./scripts/health-check.sh
□ Check Grafana dashboards
□ Review error logs
□ Verify backup status

# Weekly Review
□ Analyze performance trends
□ Review resource utilization
□ Check for security updates
□ Validate monitoring alerts

# Monthly Maintenance
□ Clean up old logs
□ Review capacity planning
□ Update monitoring thresholds
□ Test disaster recovery
```

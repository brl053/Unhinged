# 🧠 Unhinged Health Dashboard

A beautiful, real-time static HTML dashboard for monitoring the complete Unhinged consciousness ecosystem.

## 🚀 Quick Start

### **1. Start the Dashboard Server**
```bash
# Navigate to the dashboard directory
cd static-dashboard

# Start the dashboard server (default port 8888)
python3 serve.py

# Or specify a custom port
python3 serve.py 9999
```

### **2. Access the Dashboard**
Open your browser and navigate to:
```
http://localhost:8888
```

## 🎯 Features

### **Real-time Health Monitoring**
- ✅ **Service Status**: Live health checks for all services
- 🔄 **Auto-refresh**: Updates every 30 seconds automatically
- 📊 **Overall Status**: System-wide health indicator
- 🎨 **Visual Indicators**: Color-coded status badges

### **Service Coverage**
- 🚀 **Backend**: Kotlin/Ktor API server (port 8080)
- 👁️ **Vision AI**: Computer vision service (port 8001)
- 🎤 **Whisper TTS**: Speech processing service (port 8000)
- 🧠 **Context LLM**: Language model service (port 8002)
- 📊 **Grafana**: Monitoring dashboards (port 3001)
- 📈 **Prometheus**: Metrics collection (port 9090)
- 📝 **Loki**: Log aggregation (port 3100)

### **Interactive Features**
- 🔍 **Individual Health Checks**: Click to check specific services
- 💬 **Chat Endpoint Testing**: Test the backend chat functionality
- 📊 **Metrics Validation**: Verify Prometheus metrics collection
- 📋 **Log Access**: Quick access to service logs
- 🔗 **Direct Links**: One-click access to service UIs

## 🎨 Dashboard Sections

### **1. Header**
- System title and branding
- Last update timestamp
- Manual refresh button
- Auto-refresh toggle

### **2. Overall Status**
- System-wide health indicator
- Service count summary
- Visual status representation

### **3. Core Services**
- Backend API health and response status
- Database connection status
- Essential service monitoring

### **4. AI Services**
- Vision AI with GPU and model status
- Whisper TTS with audio capabilities
- Context LLM with processing status

### **5. Observability Stack**
- Grafana dashboard access
- Prometheus metrics and targets
- Loki log aggregation status

### **6. Quick Actions**
- Health check script execution
- Chat endpoint testing
- Metrics validation
- Log viewing commands

## 🔧 Configuration

### **Service URLs**
The dashboard monitors these default endpoints:
```javascript
{
    backend: 'http://localhost:8080/health',
    'vision-ai': 'http://localhost:8001/health',
    'whisper-tts': 'http://localhost:8000/health',
    'context-llm': 'http://localhost:8002/health',
    grafana: 'http://localhost:3001/api/health',
    prometheus: 'http://localhost:9090/-/healthy',
    loki: 'http://localhost:3100/ready'
}
```

### **Customization**
To modify service endpoints, edit `dashboard.js`:
```javascript
// Update the services object in the UnhingedDashboard constructor
this.services = {
    // Add or modify service endpoints here
};
```

## 🌐 CORS Configuration

The dashboard server includes CORS headers to allow cross-origin requests to your services. If you encounter CORS issues:

1. **Check browser console** for specific error messages
2. **Verify service endpoints** are accessible
3. **Ensure services allow CORS** from the dashboard origin

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- 🖥️ **Desktop**: Full feature set with grid layout
- 📱 **Mobile**: Optimized single-column layout
- 📟 **Tablet**: Adaptive grid with touch-friendly controls

## 🎨 Theme & Styling

### **Dark Theme**
- Modern dark color scheme
- High contrast for readability
- Gradient accents and animations
- Professional appearance

### **Status Colors**
- 🟢 **Green**: Service online and healthy
- 🟡 **Yellow**: Service degraded or warning
- 🔴 **Red**: Service offline or error
- ⚪ **Gray**: Service checking or unknown

## 🔍 Troubleshooting

### **Dashboard Not Loading**
```bash
# Check if the server is running
ps aux | grep serve.py

# Verify port availability
lsof -i :8888

# Check for Python errors
python3 serve.py
```

### **Services Showing Offline**
```bash
# Verify services are running
docker ps | grep unhinged

# Check service health manually
curl http://localhost:8080/health
curl http://localhost:8001/health

# Run comprehensive health check
./scripts/health-check.sh
```

### **CORS Errors**
```bash
# Check browser console for specific errors
# Ensure services are accessible from dashboard origin
# Verify service CORS configuration
```

## 🚀 Advanced Usage

### **Integration with CI/CD**
```bash
# Use dashboard for automated health checks
curl -s http://localhost:8888/api/health

# Integrate with monitoring systems
# Export dashboard metrics for external tools
```

### **Custom Monitoring**
```javascript
// Add custom service monitoring
// Extend dashboard functionality
// Integrate with external APIs
```

## 📋 File Structure

```
static-dashboard/
├── index.html          # Main dashboard HTML
├── styles.css          # Dashboard styling
├── dashboard.js        # JavaScript functionality
├── serve.py           # Python HTTP server
└── README.md          # This documentation
```

## 🎯 Next Steps

1. **Start the dashboard**: `python3 serve.py`
2. **Access the UI**: http://localhost:8888
3. **Monitor your services**: Real-time health tracking
4. **Customize as needed**: Modify for your specific setup

---

**🧠 Unhinged Consciousness Ecosystem - Health Dashboard v1.0**

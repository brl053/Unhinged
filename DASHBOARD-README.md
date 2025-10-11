# 🧠 Unhinged Health Dashboard

A beautiful, self-contained HTML dashboard for real-time monitoring of the complete Unhinged consciousness ecosystem.

## 🚀 Quick Start

### **Option 1: Direct Browser Access**
```bash
# Simply open the HTML file in your browser
open unhinged-health-dashboard.html

# Or double-click the file in your file manager
```

### **Option 2: Script Launcher**
```bash
# Use the provided launcher script
./scripts/open-dashboard.sh

# The script will:
# - Open the dashboard in your default browser
# - Display helpful information and tips
# - Show service monitoring details
```

## ✨ **Key Features**

### **🌐 Self-Contained HTML File**
- ✅ **No Server Required**: Runs directly in any modern browser
- 📁 **Single File**: All CSS and JavaScript embedded inline
- 🚫 **No Dependencies**: No external libraries or frameworks
- 📱 **Universal Compatibility**: Works on any device with a web browser

### **🔄 Real-Time Monitoring**
- ⚡ **Auto-refresh**: Updates every 30 seconds automatically
- 🎯 **Manual Refresh**: Instant updates with refresh button
- 🎨 **Visual Status**: Color-coded service indicators
- 📊 **Overall Health**: System-wide status summary

### **🎨 Modern Interface**
- 🌙 **Dark Theme**: Professional dark design
- 📱 **Responsive**: Perfect on desktop, tablet, and mobile
- ⚡ **Smooth Animations**: Hover effects and transitions
- 🎨 **Beautiful Gradients**: Blue/green accent colors

## 🔧 **Monitored Services**

### **Core Services**
- 🚀 **Backend** (Port 8080) - Kotlin/Ktor API with observability
- 🐘 **Database** (Port 5433) - PostgreSQL data persistence

### **AI Services**
- 👁️ **Vision AI** (Port 8001) - Computer vision processing
- 🎤 **Whisper TTS** (Port 8000) - Speech-to-text and TTS
- 🧠 **Context LLM** (Port 8002) - Context-aware language model

### **Observability Stack**
- 📊 **Grafana** (Port 3001) - Monitoring dashboards
- 📈 **Prometheus** (Port 9090) - Metrics collection
- 📝 **Loki** (Port 3100) - Log aggregation

## 🎯 **Dashboard Sections**

### **1. Header**
- System title with gradient branding
- Last update timestamp
- Manual refresh button
- Auto-refresh toggle (30-second intervals)

### **2. Overall Status**
- System-wide health indicator
- Service count summary (healthy/total)
- Visual status representation

### **3. Service Cards**
Each service displays:
- **Status Badge**: Online/Offline/Degraded/Checking
- **Port Information**: Service endpoint details
- **Health Details**: Service-specific status data
- **Action Buttons**: Check, Open, Documentation links

### **4. Quick Actions**
- 🏥 **Health Check Script**: Instructions for comprehensive checks
- 💬 **Chat Test**: Direct testing of backend chat endpoint
- 📊 **Metrics Check**: Validation of Prometheus metrics
- 📋 **Log Commands**: Copy-paste commands for log viewing

## 🔍 **Status Indicators**

### **Color Coding**
- 🟢 **Green (Online)**: Service is healthy and responding
- 🟡 **Yellow (Degraded)**: Service has issues but is functional
- 🔴 **Red (Offline)**: Service is down or unreachable
- ⚪ **Gray (Checking)**: Status check in progress

### **Overall System Status**
- **Healthy**: All services are online
- **Degraded**: Some services have issues
- **Unhealthy**: Multiple services are down
- **Unknown**: Unable to determine status

## 💡 **Usage Tips**

### **Real-Time Monitoring**
- Dashboard automatically refreshes every 30 seconds
- Click any service card to perform individual health check
- Use the manual refresh button for instant updates
- Toggle auto-refresh off for manual control

### **Service Testing**
- Click "🔍 Check" buttons for individual service tests
- Use "🔗 Open" links to access service UIs directly
- "📚 Docs" links provide API documentation
- Quick Actions test specific functionality

### **Troubleshooting**
- Check browser console for CORS or network errors
- Ensure services are running before expecting green status
- Refresh the page to reset all status checks
- Use the health check script for comprehensive diagnosis

## 🔧 **Technical Details**

### **Browser Compatibility**
- ✅ **Chrome/Chromium**: Full support
- ✅ **Firefox**: Full support
- ✅ **Safari**: Full support
- ✅ **Edge**: Full support
- ⚠️ **Internet Explorer**: Limited support (modern browsers recommended)

### **CORS Considerations**
The dashboard makes cross-origin requests to your services. If you encounter CORS errors:
1. Ensure services are configured to allow CORS
2. Check browser console for specific error messages
3. Some services may need CORS headers configured

### **Security**
- Dashboard runs locally in your browser
- No data is sent to external servers
- All service communication is direct to your local services
- Safe to use in development and production environments

## 🎨 **Customization**

### **Adding Services**
To monitor additional services, edit the HTML file:
```javascript
// Find the services object in the JavaScript section
this.services = {
    // Add your service here
    'my-service': { url: 'http://localhost:PORT/health', port: PORT }
};
```

### **Styling Changes**
Modify the CSS variables in the `<style>` section:
```css
:root {
    --primary-color: #2563eb;    /* Change primary color */
    --success-color: #10b981;    /* Change success color */
    --background-color: #0f172a; /* Change background */
    /* ... other variables ... */
}
```

## 🚀 **Advantages Over Server-Based Dashboards**

### **Simplicity**
- 📁 **Single File**: No complex setup or configuration
- 🚫 **No Server**: No need to run additional services
- ⚡ **Instant Access**: Open and use immediately

### **Portability**
- 📧 **Email Friendly**: Can be shared via email
- 💾 **Backup Ready**: Easy to backup and restore
- 🔄 **Version Control**: Simple to track changes

### **Performance**
- ⚡ **Fast Loading**: No external dependencies to download
- 💾 **Low Resource**: Minimal system resource usage
- 🌐 **Offline Capable**: Works without internet (for local services)

## 🎯 **Perfect For**

- 👨‍💻 **Development**: Monitor services during development
- 🏭 **Production**: Quick health overview for operations
- 🚨 **Incident Response**: Rapid status assessment
- 📊 **Demos**: Show system health to stakeholders
- 🔧 **Debugging**: Identify failing services quickly

---

**🧠 The Unhinged Health Dashboard provides enterprise-grade monitoring in a simple, self-contained HTML file!**

**Just open `unhinged-health-dashboard.html` in your browser and start monitoring! 🚀**

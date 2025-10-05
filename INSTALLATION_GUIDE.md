# 🔧 gRPC Tool - Installation Guide

## ✅ **Installation Complete!**

Your gRPC Tool is now installed and available in multiple ways:

---

## 🚀 **How to Start the gRPC Tool**

### **Method 1: From Applications Menu (Recommended)**
1. **Open your Applications menu** (Activities/Super key)
2. **Search for "gRPC Tool"** or look in the Development category
3. **Click on the gRPC Tool icon** to launch

### **Method 2: Using the Launcher Script**
```bash
cd /home/e-bliss-station-1/projects/Unhinged
./launch-grpc-tool.sh
```

### **Method 3: Direct AppImage Execution**
```bash
cd /home/e-bliss-station-1/projects/Unhinged
./src-tauri/target/debug/bundle/appimage/gRPC\ Tool_0.1.0_amd64.AppImage
```

### **Method 4: From Terminal (Development)**
```bash
cd /home/e-bliss-station-1/projects/Unhinged
./src-tauri/target/debug/unhinged-desktop
```

---

## 📁 **Installation Files Created**

### **Desktop Entry**
- **Location**: `~/.local/share/applications/grpc-tool.desktop`
- **Purpose**: Makes the app appear in your Applications menu
- **Category**: Development tools

### **AppImage Bundle**
- **Location**: `src-tauri/target/debug/bundle/appimage/gRPC Tool_0.1.0_amd64.AppImage`
- **Purpose**: Portable executable that runs on any Linux system
- **Size**: ~15MB (includes all dependencies)

### **Launcher Script**
- **Location**: `launch-grpc-tool.sh`
- **Purpose**: Easy command-line launcher with helpful messages
- **Features**: Automatic path detection and error checking

### **Additional Packages**
- **Debian Package**: `src-tauri/target/debug/bundle/deb/gRPC Tool_0.1.0_amd64.deb`
- **RPM Package**: `src-tauri/target/debug/bundle/rpm/gRPC Tool-0.1.0-1.x86_64.rpm`

---

## 🎯 **Quick Start Guide**

### **1. Launch the Tool**
- Find "gRPC Tool" in your Applications menu
- Or run `./launch-grpc-tool.sh` from the project directory

### **2. Connect to a gRPC Server**
1. Enter **Host** (e.g., `localhost`, `api.example.com`)
2. Enter **Port** (e.g., `9090`, `443`)
3. Check **"Use TLS"** if the server requires encryption
4. Click **"Connect"**

### **3. Discover Services**
1. After successful connection, click **"Discover Services"**
2. Services will appear in the left panel
3. Expand services to see available methods

### **4. Inspect Methods**
1. Click on any method to see its details
2. View input/output types and streaming information
3. Method signature appears in the main panel

---

## 🔧 **System Integration**

### **Desktop Environment Integration**
- ✅ **Applications Menu**: Appears in Development category
- ✅ **Search**: Searchable by "gRPC", "API", "client", "reflection"
- ✅ **Icon**: Uses network-server icon from system theme
- ✅ **Window Class**: Proper window management integration

### **File Associations**
- The tool is registered as a Development application
- Can be pinned to dock/taskbar like any other app
- Supports standard window operations (minimize, maximize, close)

---

## 🛠️ **Troubleshooting**

### **If the App Doesn't Appear in Applications Menu**
```bash
# Refresh the desktop database
update-desktop-database ~/.local/share/applications

# Or restart your desktop session
```

### **If AppImage Won't Run**
```bash
# Make sure it's executable
chmod +x "src-tauri/target/debug/bundle/appimage/gRPC Tool_0.1.0_amd64.AppImage"

# Check for missing dependencies (rare with AppImage)
ldd "src-tauri/target/debug/bundle/appimage/gRPC Tool_0.1.0_amd64.AppImage"
```

### **If Connection Fails**
- Verify the gRPC server is running and accessible
- Check if the server supports reflection (most modern servers do)
- Ensure firewall/network allows connections to the specified port
- Try with and without TLS depending on server configuration

---

## 📦 **Distribution Options**

### **For Other Users**
You can share the AppImage file - it's completely portable:
```bash
# Copy this file to any Linux system
src-tauri/target/debug/bundle/appimage/gRPC Tool_0.1.0_amd64.AppImage
```

### **For System-Wide Installation**
```bash
# Install the Debian package system-wide (requires sudo)
sudo dpkg -i "src-tauri/target/debug/bundle/deb/gRPC Tool_0.1.0_amd64.deb"
```

---

## 🎉 **You're All Set!**

Your gRPC Tool is now fully installed and integrated with your system. You can:

- **Launch from Applications menu** like any other app
- **Connect to any gRPC server** with reflection support
- **Discover services dynamically** without protobuf files
- **Inspect method signatures** and streaming types
- **Professional developer experience** with dark theme and native performance

The tool is ready to help you explore, test, and debug gRPC services!

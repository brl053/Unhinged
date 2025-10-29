# Unhinged JavaScript SDK

Beautiful syntax sugar for Unhinged system operations. Instead of raw HTTP calls to the control proxy, get clean, intuitive APIs.

## Installation

```html
<!-- Browser -->
<script src="unhinged-sdk.js"></script>

<!-- Or ES6 Module -->
<script type="module">
import { UnhingedSDK } from './unhinged-sdk.js';
</script>
```

```javascript
// Node.js
const { UnhingedSDK } = require('./unhinged-sdk.js');
```

## Quick Start

```javascript
// Initialize the SDK
const unhinged = new UnhingedSDK({
    baseUrl: 'http://localhost:9000',  // Control proxy URL
    timeout: 30000
});

// Beautiful system operations
await unhinged.service.start('applications');
await unhinged.file.write('/tmp/hello.txt', 'Hello World!');
await unhinged.network.ping('google.com');
await unhinged.package.apt.install('docker.io');
```

## API Reference

### Service Management

```javascript
// Start/stop service tiers
await unhinged.service.start('applications');
await unhinged.service.start('infrastructure'); 
await unhinged.service.stop('ai_services');
await unhinged.service.restart('applications');

// Get service status
const status = await unhinged.service.status();
console.log('Running services:', status.running_services);
```

### File Operations

```javascript
// File I/O
await unhinged.file.write('/path/to/file.txt', 'content');
const content = await unhinged.file.read('/path/to/file.txt');
const exists = await unhinged.file.exists('/path/to/file.txt');
await unhinged.file.remove('/path/to/file.txt');
```

### File System

```javascript
// Directory operations
await unhinged.fs.mkdir('/tmp/mydir');
await unhinged.fs.rmdir('/tmp/mydir');
const files = await unhinged.fs.ls('/tmp');
```

### Network Operations

```javascript
// Network utilities
const pingResult = await unhinged.network.ping('google.com', 4);
await unhinged.network.wget('https://example.com/file.zip', '/tmp/file.zip');

// HTTP requests (curl equivalent)
const response = await unhinged.network.curl('https://api.github.com/user', {
    headers: { 'Authorization': 'token xyz' }
});
```

### Package Management

```javascript
// APT packages
await unhinged.package.apt.update();
await unhinged.package.apt.install('docker.io');

// NPM packages  
await unhinged.package.npm.install('express');
await unhinged.package.npm.install('react', { global: true });

// Python packages
await unhinged.package.pip.install('fastapi');
```

### Process Management

```javascript
// Execute commands
const result = await unhinged.process.exec('ls -la /tmp');
console.log('Output:', result.stdout);

// Process control
await unhinged.process.kill(1234, 'TERM');
```

### System Information

```javascript
// System stats
const info = await unhinged.system.info();
const resources = await unhinged.system.resources();

console.log('CPU cores:', info.cpu_count);
console.log('Memory usage:', resources.memory_usage);
```

## Error Handling

```javascript
try {
    await unhinged.service.start('nonexistent-tier');
} catch (error) {
    if (error instanceof UnhingedError) {
        console.error('Unhinged error:', error.message);
        console.error('Status code:', error.status);
    } else {
        console.error('Network error:', error.message);
    }
}
```

## Integration with HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>Unhinged Control Panel</title>
    <script src="unhinged-sdk.js"></script>
</head>
<body>
    <button onclick="startApplications()">Start Applications</button>
    <button onclick="checkStatus()">Check Status</button>
    
    <script>
        const unhinged = new UnhingedSDK();
        
        async function startApplications() {
            try {
                const result = await unhinged.service.start('applications');
                alert('Applications started successfully!');
            } catch (error) {
                alert('Failed to start applications: ' + error.message);
            }
        }
        
        async function checkStatus() {
            const status = await unhinged.service.status();
            console.log('Service status:', status);
        }
    </script>
</body>
</html>
```

## Advanced Usage

### Custom Configuration

```javascript
const unhinged = new UnhingedSDK({
    baseUrl: 'https://my-unhinged-server.com',
    timeout: 60000,
    headers: {
        'X-API-Key': 'my-secret-key'
    }
});
```

### Batch Operations

```javascript
// Start multiple service tiers
await Promise.all([
    unhinged.service.start('infrastructure'),
    unhinged.service.start('applications'),
    unhinged.service.start('ai_services')
]);

// Create multiple directories
await Promise.all([
    unhinged.fs.mkdir('/tmp/dir1'),
    unhinged.fs.mkdir('/tmp/dir2'),
    unhinged.fs.mkdir('/tmp/dir3')
]);
```

### Real-time Monitoring

```javascript
// Poll service status
setInterval(async () => {
    const status = await unhinged.service.status();
    updateUI(status);
}, 5000);

function updateUI(status) {
    document.getElementById('running-services').textContent = 
        status.running_services.join(', ');
}
```

## Future Language Bindings

This JavaScript SDK serves as the reference implementation. Future language bindings will follow the same API patterns:

- **Kotlin**: `unhinged.service.start("applications")`
- **Python**: `unhinged.service.start("applications")`  
- **Go**: `unhinged.Service.Start("applications")`
- **Rust**: `unhinged.service().start("applications")`

## Architecture

```
JavaScript SDK → HTTP Control Proxy → System Controller → Build System → Docker/OS
```

The SDK provides beautiful abstractions over the HTTP control proxy, which translates operations into system calls while maintaining audit trails for future OS development.

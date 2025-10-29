/*
 * @llm-type misc.client-sdk
 * @llm-does javascript client sdk providing syntax sugar for
 */

class UnhingedSDK {
    constructor(options = {}) {
        this.baseUrl = options.baseUrl || 'http://localhost:9000';
        this.timeout = options.timeout || 30000;
        this.apiVersion = 'v1';
        
        // Initialize subsystems
        this.service = new ServiceManager(this);
        this.file = new FileManager(this);
        this.network = new NetworkManager(this);
        this.package = new PackageManager(this);
        this.fs = new FileSystemManager(this);
        this.process = new ProcessManager(this);
        this.system = new SystemManager(this);
    }

    /**
     * Make HTTP request to control proxy
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            timeout: this.timeout,
            ...options
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: response.statusText }));
                throw new UnhingedError(`HTTP ${response.status}: ${error.error || error.detail}`, response.status);
            }

            return await response.json();
        } catch (error) {
            if (error instanceof UnhingedError) throw error;
            throw new UnhingedError(`Network error: ${error.message}`, 0);
        }
    }
}

/**
 * Service Management - Beautiful service orchestration
 */
class ServiceManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Start a service tier
     * @example await service.start('applications')
     */
    async start(tier) {
        return await this.sdk.request(`/control/system/tier/${tier}/start`, {
            method: 'POST'
        });
    }

    /**
     * Stop a service tier  
     * @example await service.stop('applications')
     */
    async stop(tier) {
        return await this.sdk.request(`/control/system/tier/${tier}/stop`, {
            method: 'POST'
        });
    }

    /**
     * Get service status
     * @example const status = await service.status()
     */
    async status() {
        return await this.sdk.request('/control/system/status');
    }

    /**
     * Restart a service tier
     * @example await service.restart('applications')
     */
    async restart(tier) {
        await this.stop(tier);
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2s
        return await this.start(tier);
    }
}

/**
 * File Operations - Clean file I/O
 */
class FileManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Write content to file
     * @example await file.write('/tmp/test.txt', 'Hello World')
     */
    async write(path, content) {
        return await this.sdk.request('/control/system/file/write', {
            method: 'POST',
            body: { path, content }
        });
    }

    /**
     * Read file content
     * @example const content = await file.read('/tmp/test.txt')
     */
    async read(path) {
        const result = await this.sdk.request('/control/system/file/read', {
            method: 'POST',
            body: { path }
        });
        return result.content;
    }

    /**
     * Check if file exists
     * @example const exists = await file.exists('/tmp/test.txt')
     */
    async exists(path) {
        try {
            await this.sdk.request('/control/system/file/stat', {
                method: 'POST',
                body: { path }
            });
            return true;
        } catch (error) {
            if (error.status === 404) return false;
            throw error;
        }
    }

    /**
     * Delete file
     * @example await file.remove('/tmp/test.txt')
     */
    async remove(path) {
        return await this.sdk.request('/control/system/file/remove', {
            method: 'DELETE',
            body: { path }
        });
    }
}

/**
 * Network Operations - Simple networking
 */
class NetworkManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Ping a host
     * @example const result = await network.ping('google.com')
     */
    async ping(host, count = 4) {
        return await this.sdk.request('/control/system/network/ping', {
            method: 'POST',
            body: { host, count }
        });
    }

    /**
     * Download file (wget equivalent)
     * @example await network.wget('https://example.com/file.zip', '/tmp/file.zip')
     */
    async wget(url, destination) {
        return await this.sdk.request('/control/system/network/wget', {
            method: 'POST',
            body: { url, destination }
        });
    }

    /**
     * Make HTTP request (curl equivalent)
     * @example const response = await network.curl('https://api.github.com/user', { headers: { 'Authorization': 'token xyz' } })
     */
    async curl(url, options = {}) {
        return await this.sdk.request('/control/system/network/curl', {
            method: 'POST',
            body: { url, options }
        });
    }
}

/**
 * Package Management - Clean package operations
 */
class PackageManager {
    constructor(sdk) {
        this.sdk = sdk;
        this.apt = new AptManager(sdk);
        this.npm = new NpmManager(sdk);
        this.pip = new PipManager(sdk);
    }
}

class AptManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Install package via apt
     * @example await package.apt.install('docker.io')
     */
    async install(packageName) {
        return await this.sdk.request('/control/system/package/apt/install', {
            method: 'POST',
            body: { package: packageName }
        });
    }

    /**
     * Update package lists
     * @example await package.apt.update()
     */
    async update() {
        return await this.sdk.request('/control/system/package/apt/update', {
            method: 'POST'
        });
    }
}

class NpmManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Install npm package
     * @example await package.npm.install('express')
     */
    async install(packageName, options = {}) {
        return await this.sdk.request('/control/system/package/npm/install', {
            method: 'POST',
            body: { package: packageName, ...options }
        });
    }
}

class PipManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Install pip package
     * @example await package.pip.install('fastapi')
     */
    async install(packageName) {
        return await this.sdk.request('/control/system/package/pip/install', {
            method: 'POST',
            body: { package: packageName }
        });
    }
}

/**
 * File System Operations - Directory management
 */
class FileSystemManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Create directory
     * @example await fs.mkdir('/tmp/mydir')
     */
    async mkdir(path, recursive = true) {
        return await this.sdk.request('/control/system/fs/mkdir', {
            method: 'POST',
            body: { path, recursive }
        });
    }

    /**
     * Remove directory
     * @example await fs.rmdir('/tmp/mydir')
     */
    async rmdir(path, recursive = false) {
        return await this.sdk.request('/control/system/fs/rmdir', {
            method: 'DELETE',
            body: { path, recursive }
        });
    }

    /**
     * List directory contents
     * @example const files = await fs.ls('/tmp')
     */
    async ls(path) {
        const result = await this.sdk.request('/control/system/fs/ls', {
            method: 'POST',
            body: { path }
        });
        return result.files;
    }
}

/**
 * Process Management
 */
class ProcessManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Execute command
     * @example const result = await process.exec('ls -la')
     */
    async exec(command, options = {}) {
        return await this.sdk.request('/control/system/process/exec', {
            method: 'POST',
            body: { command, ...options }
        });
    }

    /**
     * Kill process by PID
     * @example await process.kill(1234)
     */
    async kill(pid, signal = 'TERM') {
        return await this.sdk.request('/control/system/process/kill', {
            method: 'POST',
            body: { pid, signal }
        });
    }
}

/**
 * System Information
 */
class SystemManager {
    constructor(sdk) {
        this.sdk = sdk;
    }

    /**
     * Get system info
     * @example const info = await system.info()
     */
    async info() {
        return await this.sdk.request('/control/system/info');
    }

    /**
     * Get resource usage
     * @example const usage = await system.resources()
     */
    async resources() {
        return await this.sdk.request('/control/system/resources');
    }
}

/**
 * Custom error class for Unhinged operations
 */
class UnhingedError extends Error {
    constructor(message, status = 0) {
        super(message);
        this.name = 'UnhingedError';
        this.status = status;
    }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    // Node.js
    module.exports = { UnhingedSDK, UnhingedError };
} else if (typeof window !== 'undefined') {
    // Browser
    window.UnhingedSDK = UnhingedSDK;
    window.UnhingedError = UnhingedError;
}

// Default export for ES6 modules
export { UnhingedSDK, UnhingedError };

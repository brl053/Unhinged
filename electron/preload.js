/**
 * @fileoverview Electron Preload Script - Secure IPC Bridge
 * 
 * @description
 * Preload script that exposes a secure API to the renderer process for
 * communicating with the main process. Follows Electron security best
 * practices with context isolation and no node integration.
 * 
 * @security_principles
 * - Context isolation enabled
 * - No direct Node.js access in renderer
 * - Validated IPC communication
 * - Sanitized data transfer
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

const { contextBridge, ipcRenderer } = require('electron');

/**
 * Universal System API exposed to renderer process
 * 
 * @description
 * Secure API that allows the renderer to communicate with the main process
 * for DSL schema access, backend service communication, and system commands.
 */
const universalSystemAPI = {
  /**
   * Get the Universal System DSL schema
   * 
   * @returns {Promise<Object>} The loaded DSL schema
   */
  getSchema: () => ipcRenderer.invoke('get-schema'),
  
  /**
   * Get application configuration
   * 
   * @returns {Promise<Object>} Application configuration
   */
  getConfig: () => ipcRenderer.invoke('get-config'),
  
  /**
   * Execute a system command (voice commands)
   * 
   * @param {string} command - The command to execute
   * @returns {Promise<Object>} Command execution result
   */
  executeCommand: (command) => {
    // Validate command input
    if (typeof command !== 'string' || command.length === 0) {
      return Promise.reject(new Error('Invalid command'));
    }
    
    // Sanitize command (basic security)
    const sanitizedCommand = command.trim().substring(0, 1000);
    
    return ipcRenderer.invoke('execute-command', sanitizedCommand);
  },
  
  /**
   * Make a request to backend services
   * 
   * @param {string} endpoint - Backend endpoint
   * @param {Object} data - Request data
   * @returns {Promise<Object>} Backend response
   */
  backendRequest: (endpoint, data) => {
    // Validate endpoint
    if (typeof endpoint !== 'string' || endpoint.length === 0) {
      return Promise.reject(new Error('Invalid endpoint'));
    }
    
    return ipcRenderer.invoke('backend-request', endpoint, data);
  },
  
  /**
   * Listen for schema updates
   * 
   * @param {Function} callback - Callback function for schema updates
   */
  onSchemaUpdate: (callback) => {
    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }
    
    ipcRenderer.on('schema-updated', (event, schema) => {
      callback(schema);
    });
  },
  
  /**
   * Remove schema update listener
   */
  removeSchemaUpdateListener: () => {
    ipcRenderer.removeAllListeners('schema-updated');
  },
};

/**
 * Expose the Universal System API to the renderer process
 * 
 * @description
 * Uses contextBridge to securely expose the API to the renderer process
 * without giving access to Node.js APIs directly.
 */
contextBridge.exposeInMainWorld('universalSystem', universalSystemAPI);

/**
 * Log successful preload initialization
 */
console.log('✅ Universal System preload script initialized');

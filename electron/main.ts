/**
 * @fileoverview Electron Main Process - Universal System Runtime
 * 
 * @description
 * Main process for the Universal System Electron application. Handles window
 * management, DSL schema loading, backend service integration, and IPC
 * communication with the renderer process.
 * 
 * @design_principles
 * - DSL-first architecture: Load and validate schema on startup
 * - Service integration: Connect to existing Unhinged backend services
 * - Development-friendly: Hot reload, debugging, error handling
 * - Security-conscious: Proper IPC boundaries and validation
 * 
 * @llm_contract
 * This main process serves as the bridge between:
 * 1. Universal System DSL schema definitions
 * 2. Existing Unhinged backend services (LLM, TTS, Tools)
 * 3. Electron renderer process for UI generation
 * 4. Ubuntu desktop environment integration
 * 
 * @author LLM Agent
 * @version 1.0.0
 * @since 2025-01-04
 */

import { app, BrowserWindow, ipcMain, Menu, shell } from 'electron';
import { join } from 'path';
import { readFileSync, existsSync } from 'fs';
import { parse as parseYaml } from 'yaml';

/**
 * Universal System configuration interface
 * 
 * @description
 * Configuration object for the Universal System runtime including
 * DSL schema location, backend service endpoints, and development settings.
 */
interface UniversalSystemConfig {
  /** Path to the Universal System DSL schema file */
  schemaPath: string;
  
  /** Backend service endpoints */
  services: {
    llm: string;
    tts: string;
    backend: string;
  };
  
  /** Development configuration */
  development: {
    hotReload: boolean;
    devTools: boolean;
    debugMode: boolean;
  };
  
  /** Window configuration */
  window: {
    width: number;
    height: number;
    minWidth: number;
    minHeight: number;
  };
}

/**
 * Universal System DSL schema interface
 * 
 * @description
 * TypeScript interface matching the YAML schema structure for
 * compile-time validation and IDE support.
 */
interface UniversalSystemSchema {
  version: string;
  description: string;
  principles: Record<string, string>;
  primitives: {
    layout: { types: ComponentDefinition[] };
    input: { types: ComponentDefinition[] };
    display: { types: ComponentDefinition[] };
    action: { types: ComponentDefinition[] };
  };
  examples: Record<string, ComponentInstance>;
  llm_guidelines: {
    understanding_patterns: string[];
    generation_principles: string[];
    voice_command_mapping: Record<string, string>;
  };
}

/**
 * Component definition from DSL schema
 */
interface ComponentDefinition {
  name: string;
  purpose: string;
  props: string[];
  state?: string[];
  actions?: string[];
}

/**
 * Component instance from DSL examples
 */
interface ComponentInstance {
  component: string;
  props?: Record<string, any>;
  state?: Record<string, any>;
  actions?: Record<string, string>;
  children?: ComponentInstance[];
}

/**
 * Global application state
 */
class UniversalSystemApp {
  private mainWindow: BrowserWindow | null = null;
  private config: UniversalSystemConfig;
  private schema: UniversalSystemSchema | null = null;
  
  constructor() {
    this.config = this.loadConfiguration();
    this.setupEventHandlers();
  }
  
  /**
   * Load application configuration
   * 
   * @description
   * Loads configuration with sensible defaults for development.
   * In production, this would load from a config file.
   */
  private loadConfiguration(): UniversalSystemConfig {
    return {
      schemaPath: join(__dirname, '../schema/universal-system.yml'),
      services: {
        llm: process.env.LLM_SERVICE_URL || 'http://localhost:11434',
        tts: process.env.TTS_SERVICE_URL || 'http://localhost:8001',
        backend: process.env.BACKEND_URL || 'http://localhost:8080',
      },
      development: {
        hotReload: process.env.NODE_ENV === 'development',
        devTools: process.env.NODE_ENV === 'development',
        debugMode: process.env.DEBUG === 'true',
      },
      window: {
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
      },
    };
  }
  
  /**
   * Load and validate Universal System DSL schema
   * 
   * @description
   * Loads the YAML schema file and validates its structure.
   * This schema drives all UI generation and component interpretation.
   */
  private async loadSchema(): Promise<void> {
    try {
      if (!existsSync(this.config.schemaPath)) {
        throw new Error(`Schema file not found: ${this.config.schemaPath}`);
      }
      
      const schemaContent = readFileSync(this.config.schemaPath, 'utf-8');
      this.schema = parseYaml(schemaContent) as UniversalSystemSchema;
      
      // Validate schema structure
      if (!this.schema.version || !this.schema.primitives) {
        throw new Error('Invalid schema structure: missing required fields');
      }
      
      console.log(`✅ Universal System DSL Schema loaded: v${this.schema.version}`);
      console.log(`📊 Primitives: ${Object.keys(this.schema.primitives).length} categories`);
      console.log(`📋 Examples: ${Object.keys(this.schema.examples || {}).length} components`);
      
    } catch (error) {
      console.error('❌ Failed to load DSL schema:', error);
      throw error;
    }
  }
  
  /**
   * Create the main application window
   * 
   * @description
   * Creates the main Electron window with proper security settings,
   * development tools, and IPC communication setup.
   */
  private createMainWindow(): void {
    this.mainWindow = new BrowserWindow({
      width: this.config.window.width,
      height: this.config.window.height,
      minWidth: this.config.window.minWidth,
      minHeight: this.config.window.minHeight,
      
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: join(__dirname, 'preload.js'),
      },
      
      // Window styling
      titleBarStyle: 'default',
      show: false, // Show after ready-to-show event
      
      // Development settings
      ...(this.config.development.devTools && {
        webPreferences: {
          ...this.mainWindow?.webPreferences,
          devTools: true,
        },
      }),
    });
    
    // Load the renderer
    if (this.config.development.hotReload) {
      // Development: Load from webpack dev server
      this.mainWindow.loadURL('http://localhost:3000');
    } else {
      // Production: Load built files
      this.mainWindow.loadFile(join(__dirname, '../renderer/index.html'));
    }
    
    // Show window when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
      
      if (this.config.development.devTools) {
        this.mainWindow?.webContents.openDevTools();
      }
    });
    
    // Handle window closed
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });
    
    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
  }
  
  /**
   * Setup application event handlers
   * 
   * @description
   * Configures Electron app events and IPC handlers for communication
   * between main and renderer processes.
   */
  private setupEventHandlers(): void {
    // App ready event
    app.whenReady().then(async () => {
      await this.loadSchema();
      this.createMainWindow();
      this.setupIpcHandlers();
      this.setupApplicationMenu();
      
      console.log('🚀 Universal System Electron App Ready');
    });
    
    // App window events
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });
    
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createMainWindow();
      }
    });
  }
  
  /**
   * Setup IPC handlers for renderer communication
   * 
   * @description
   * Handles communication between the renderer process and main process,
   * including DSL schema requests, backend service calls, and system commands.
   */
  private setupIpcHandlers(): void {
    // Get DSL schema
    ipcMain.handle('get-schema', () => {
      return this.schema;
    });
    
    // Get application configuration
    ipcMain.handle('get-config', () => {
      return {
        services: this.config.services,
        development: this.config.development,
      };
    });
    
    // Execute system command (for voice commands)
    ipcMain.handle('execute-command', async (event, command: string) => {
      // TODO: Implement secure command execution
      console.log('🎤 Voice command received:', command);
      return { success: true, result: `Executed: ${command}` };
    });
    
    // Backend service proxy
    ipcMain.handle('backend-request', async (event, endpoint: string, data?: any) => {
      // TODO: Implement backend service communication
      console.log('🔗 Backend request:', endpoint, data);
      return { success: true, data: 'Backend response placeholder' };
    });
  }
  
  /**
   * Setup application menu
   * 
   * @description
   * Creates the application menu with development tools and system integration.
   */
  private setupApplicationMenu(): void {
    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: 'Universal System',
        submenu: [
          { role: 'about' },
          { type: 'separator' },
          { role: 'services' },
          { type: 'separator' },
          { role: 'hide' },
          { role: 'hideOthers' },
          { role: 'unhide' },
          { type: 'separator' },
          { role: 'quit' },
        ],
      },
      {
        label: 'Edit',
        submenu: [
          { role: 'undo' },
          { role: 'redo' },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' },
          { role: 'selectAll' },
        ],
      },
      {
        label: 'View',
        submenu: [
          { role: 'reload' },
          { role: 'forceReload' },
          { role: 'toggleDevTools' },
          { type: 'separator' },
          { role: 'resetZoom' },
          { role: 'zoomIn' },
          { role: 'zoomOut' },
          { type: 'separator' },
          { role: 'togglefullscreen' },
        ],
      },
      {
        label: 'Window',
        submenu: [
          { role: 'minimize' },
          { role: 'close' },
        ],
      },
    ];
    
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }
}

// Initialize the Universal System application
const universalSystemApp = new UniversalSystemApp();

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

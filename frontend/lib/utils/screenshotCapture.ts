/**
 * @fileoverview Screenshot Capture Utility
 * @purpose Utility functions for capturing screenshots in Linux environment
 * @editable true - LLM should update when adding new capture methods or platforms
 * @deprecated false
 * 
 * @remarks
 * This utility provides screenshot capture functionality using various Linux tools.
 * Designed to work with the ImageUpload component and vision processing pipeline.
 * Supports both full desktop and targeted window capture.
 * 
 * @example
 * ```typescript
 * // Capture full desktop
 * const screenshot = await captureDesktop();
 * 
 * // Capture specific URL
 * const webScreenshot = await captureWebpage('http://localhost:3000');
 * 
 * // Capture browser window
 * const browserScreenshot = await captureBrowserWindow();
 * ```
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

/**
 * Screenshot capture options
 * @public
 */
export interface ScreenshotOptions {
  /** Output file path */
  outputPath?: string;
  /** Image format */
  format?: 'png' | 'jpg' | 'webp';
  /** Image quality (1-100) */
  quality?: number;
  /** Window dimensions */
  dimensions?: {
    width: number;
    height: number;
  };
  /** Delay before capture (ms) */
  delay?: number;
  /** Capture specific window by name */
  windowName?: string;
  /** Capture specific window by ID */
  windowId?: string;
}

/**
 * Screenshot capture result
 * @public
 */
export interface ScreenshotResult {
  /** Success status */
  success: boolean;
  /** Output file path */
  filePath?: string;
  /** File size in bytes */
  fileSize?: number;
  /** Image dimensions */
  dimensions?: {
    width: number;
    height: number;
  };
  /** Error message if failed */
  error?: string;
  /** Capture method used */
  method?: string;
}

/**
 * Available screenshot capture methods
 * @public
 */
export enum CaptureMethod {
  CHROMIUM_HEADLESS = 'chromium-headless',
  XWD = 'xwd',
  GNOME_SCREENSHOT = 'gnome-screenshot',
  SCROT = 'scrot',
  IMAGEMAGICK = 'imagemagick'
}

/**
 * Generate unique filename for screenshots
 */
const generateScreenshotFilename = (format: string = 'png'): string => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  return `screenshot_${timestamp}.${format}`;
};

/**
 * Check if a command is available in the system
 */
const isCommandAvailable = async (command: string): Promise<boolean> => {
  try {
    await execAsync(`which ${command}`);
    return true;
  } catch {
    return false;
  }
};

/**
 * Get file information
 */
const getFileInfo = async (filePath: string): Promise<{ size: number; exists: boolean }> => {
  try {
    const stats = await fs.promises.stat(filePath);
    return { size: stats.size, exists: true };
  } catch {
    return { size: 0, exists: false };
  }
};

/**
 * Capture screenshot using Chromium headless browser
 * Best for web content capture
 */
export const captureWebpage = async (
  url: string, 
  options: ScreenshotOptions = {}
): Promise<ScreenshotResult> => {
  const {
    outputPath = `/tmp/${generateScreenshotFilename()}`,
    dimensions = { width: 1920, height: 1080 },
    delay = 5000,
    quality = 90
  } = options;

  try {
    // Check if Chromium is available
    const chromiumPaths = ['/snap/bin/chromium', 'chromium-browser', 'chromium', 'google-chrome'];
    let chromiumPath = '';
    
    for (const path of chromiumPaths) {
      if (await isCommandAvailable(path)) {
        chromiumPath = path;
        break;
      }
    }
    
    if (!chromiumPath) {
      return {
        success: false,
        error: 'No Chromium/Chrome browser found',
        method: CaptureMethod.CHROMIUM_HEADLESS
      };
    }

    // Capture screenshot
    const command = `${chromiumPath} --headless --disable-gpu --virtual-time-budget=${delay} --screenshot="${outputPath}" --window-size=${dimensions.width},${dimensions.height} "${url}"`;
    
    const { stdout, stderr } = await execAsync(command);
    
    // Check if file was created
    const fileInfo = await getFileInfo(outputPath);
    
    if (!fileInfo.exists || fileInfo.size === 0) {
      return {
        success: false,
        error: `Screenshot file not created or empty. stderr: ${stderr}`,
        method: CaptureMethod.CHROMIUM_HEADLESS
      };
    }

    return {
      success: true,
      filePath: outputPath,
      fileSize: fileInfo.size,
      dimensions,
      method: CaptureMethod.CHROMIUM_HEADLESS
    };

  } catch (error) {
    return {
      success: false,
      error: `Chromium capture failed: ${error instanceof Error ? error.message : String(error)}`,
      method: CaptureMethod.CHROMIUM_HEADLESS
    };
  }
};

/**
 * Capture full desktop screenshot using XWD
 */
export const captureDesktop = async (
  options: ScreenshotOptions = {}
): Promise<ScreenshotResult> => {
  const {
    outputPath = `/tmp/${generateScreenshotFilename()}`,
    format = 'png'
  } = options;

  try {
    // Check if XWD is available
    if (!await isCommandAvailable('xwd')) {
      return {
        success: false,
        error: 'XWD command not available',
        method: CaptureMethod.XWD
      };
    }

    // Capture using XWD
    const xwdPath = outputPath.replace(/\.[^.]+$/, '.xwd');
    await execAsync(`xwd -root -out "${xwdPath}"`);

    // Convert to desired format if needed
    if (format !== 'xwd') {
      if (await isCommandAvailable('convert')) {
        await execAsync(`convert "${xwdPath}" "${outputPath}"`);
        // Remove temporary XWD file
        await fs.promises.unlink(xwdPath);
      } else {
        return {
          success: true,
          filePath: xwdPath,
          fileSize: (await getFileInfo(xwdPath)).size,
          method: CaptureMethod.XWD
        };
      }
    }

    const fileInfo = await getFileInfo(outputPath);
    
    return {
      success: fileInfo.exists && fileInfo.size > 0,
      filePath: outputPath,
      fileSize: fileInfo.size,
      method: CaptureMethod.XWD,
      error: !fileInfo.exists ? 'Screenshot file not created' : undefined
    };

  } catch (error) {
    return {
      success: false,
      error: `XWD capture failed: ${error instanceof Error ? error.message : String(error)}`,
      method: CaptureMethod.XWD
    };
  }
};

/**
 * Capture specific browser window
 */
export const captureBrowserWindow = async (
  options: ScreenshotOptions = {}
): Promise<ScreenshotResult> => {
  const {
    outputPath = `/tmp/${generateScreenshotFilename()}`,
    windowName = 'Chromium'
  } = options;

  try {
    // Find browser window
    const { stdout } = await execAsync(`xwininfo -tree -root | grep -i "${windowName}"`);
    
    if (!stdout.trim()) {
      return {
        success: false,
        error: `No window found with name: ${windowName}`,
        method: CaptureMethod.XWD
      };
    }

    // Extract window ID
    const windowIdMatch = stdout.match(/0x[0-9a-f]+/i);
    if (!windowIdMatch) {
      return {
        success: false,
        error: 'Could not extract window ID',
        method: CaptureMethod.XWD
      };
    }

    const windowId = windowIdMatch[0];

    // Capture window
    const xwdPath = outputPath.replace(/\.[^.]+$/, '.xwd');
    await execAsync(`xwd -id ${windowId} -out "${xwdPath}"`);

    // Convert to PNG if ImageMagick is available
    if (await isCommandAvailable('convert')) {
      await execAsync(`convert "${xwdPath}" "${outputPath}"`);
      await fs.promises.unlink(xwdPath);
    } else {
      // Use XWD file directly
      await fs.promises.rename(xwdPath, outputPath);
    }

    const fileInfo = await getFileInfo(outputPath);
    
    return {
      success: fileInfo.exists && fileInfo.size > 0,
      filePath: outputPath,
      fileSize: fileInfo.size,
      method: CaptureMethod.XWD,
      error: !fileInfo.exists ? 'Screenshot file not created' : undefined
    };

  } catch (error) {
    return {
      success: false,
      error: `Browser window capture failed: ${error instanceof Error ? error.message : String(error)}`,
      method: CaptureMethod.XWD
    };
  }
};

/**
 * Auto-detect best capture method and take screenshot
 */
export const captureScreenshot = async (
  target: 'desktop' | 'browser' | string,
  options: ScreenshotOptions = {}
): Promise<ScreenshotResult> => {
  // If target is a URL, use webpage capture
  if (target.startsWith('http://') || target.startsWith('https://')) {
    return captureWebpage(target, options);
  }

  // If target is 'desktop', capture full desktop
  if (target === 'desktop') {
    return captureDesktop(options);
  }

  // If target is 'browser', capture browser window
  if (target === 'browser') {
    return captureBrowserWindow(options);
  }

  // Otherwise, treat as window name
  return captureBrowserWindow({ ...options, windowName: target });
};

/**
 * Capture screenshot and convert to base64 for ImageUpload component
 */
export const captureScreenshotAsBase64 = async (
  target: 'desktop' | 'browser' | string,
  options: ScreenshotOptions = {}
): Promise<{ success: boolean; data?: string; error?: string; result?: ScreenshotResult }> => {
  try {
    const result = await captureScreenshot(target, options);
    
    if (!result.success || !result.filePath) {
      return {
        success: false,
        error: result.error || 'Screenshot capture failed',
        result
      };
    }

    // Read file and convert to base64
    const fileBuffer = await fs.promises.readFile(result.filePath);
    const base64Data = `data:image/png;base64,${fileBuffer.toString('base64')}`;

    // Clean up temporary file
    try {
      await fs.promises.unlink(result.filePath);
    } catch {
      // Ignore cleanup errors
    }

    return {
      success: true,
      data: base64Data,
      result
    };

  } catch (error) {
    return {
      success: false,
      error: `Base64 conversion failed: ${error instanceof Error ? error.message : String(error)}`
    };
  }
};

/**
 * Quick capture of localhost development server
 */
export const captureLocalhost = async (
  port: number = 3000,
  path: string = '',
  options: ScreenshotOptions = {}
): Promise<ScreenshotResult> => {
  const url = `http://localhost:${port}${path}`;
  return captureWebpage(url, {
    delay: 3000, // Give time for React to render
    dimensions: { width: 1920, height: 1080 },
    ...options
  });
};

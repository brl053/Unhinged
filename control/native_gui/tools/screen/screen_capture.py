"""
Screen Capture Module for Screenshots and Screen Recording
Provides fast screen capture using mss with OCR and vision AI integration.
"""

import mss
import numpy as np
import cv2
import time
import threading
from typing import Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path
import base64
import json


@dataclass
class ScreenConfig:
    """Screen capture configuration"""
    monitor: int = 0           # Monitor index (0 = all monitors)
    region: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    compression_quality: int = 95  # JPEG quality (1-100)
    capture_cursor: bool = True    # Include cursor in screenshots
    auto_crop: bool = False        # Auto-crop to content
    scale_factor: float = 1.0      # Scale captured images


class ScreenCapture:
    """Fast screen capture using mss"""
    
    def __init__(self, config: Optional[ScreenConfig] = None):
        self.config = config or ScreenConfig()
        self.sct = mss.mss()
        self.monitors = self.sct.monitors
        
        # Vision integration
        self.vision_client = None
        self.ocr_enabled = False
        
        # Statistics
        self.screenshots_taken = 0
        self.total_capture_time = 0.0
        
        print(f"📺 Screen capture initialized: {len(self.monitors)-1} monitors detected")
        for i, monitor in enumerate(self.monitors[1:], 1):  # Skip "All monitors"
            print(f"   Monitor {i}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
    
    def get_monitors(self) -> List[Dict]:
        """Get available monitors"""
        monitor_list = []
        for i, monitor in enumerate(self.monitors):
            if i == 0:  # Skip "All monitors" entry
                continue
            
            monitor_info = {
                'index': i,
                'width': monitor['width'],
                'height': monitor['height'],
                'left': monitor['left'],
                'top': monitor['top'],
                'name': f"Monitor {i}"
            }
            monitor_list.append(monitor_info)
        
        return monitor_list
    
    def capture_screenshot(self, monitor: Optional[int] = None, 
                          region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """Capture screenshot from specified monitor or region"""
        start_time = time.time()
        
        try:
            # Determine capture area
            if region:
                # Custom region: (x, y, width, height) -> mss format
                x, y, width, height = region
                capture_area = {"top": y, "left": x, "width": width, "height": height}
            else:
                # Use monitor
                monitor_index = monitor if monitor is not None else self.config.monitor
                if monitor_index >= len(self.monitors):
                    print(f"❌ Monitor {monitor_index} not available")
                    return None
                
                capture_area = self.monitors[monitor_index]
            
            # Capture screenshot
            screenshot = self.sct.grab(capture_area)
            
            # Convert to numpy array
            img = np.array(screenshot)
            
            # Convert BGRA to BGR (remove alpha channel)
            if img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Apply scaling if needed
            if self.config.scale_factor != 1.0:
                new_width = int(img.shape[1] * self.config.scale_factor)
                new_height = int(img.shape[0] * self.config.scale_factor)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Auto-crop if enabled
            if self.config.auto_crop:
                img = self._auto_crop_content(img)
            
            # Update statistics
            self.screenshots_taken += 1
            self.total_capture_time += time.time() - start_time
            
            return img
            
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def _auto_crop_content(self, img: np.ndarray) -> np.ndarray:
        """Auto-crop image to content (remove empty borders)"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Find non-zero pixels (content)
            coords = cv2.findNonZero(gray)
            
            if coords is not None:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(coords)
                
                # Add small padding
                padding = 10
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img.shape[1] - x, w + 2 * padding)
                h = min(img.shape[0] - y, h + 2 * padding)
                
                # Crop image
                return img[y:y+h, x:x+w]
            
            return img
            
        except Exception as e:
            print(f"⚠️ Auto-crop failed: {e}")
            return img
    
    def save_screenshot(self, filename: str, monitor: Optional[int] = None, 
                       region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Capture and save screenshot"""
        try:
            img = self.capture_screenshot(monitor, region)
            if img is None:
                return False
            
            # Ensure directory exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            # Save with specified quality
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                cv2.imwrite(filename, img, [cv2.IMWRITE_JPEG_QUALITY, self.config.compression_quality])
            else:
                cv2.imwrite(filename, img)
            
            print(f"📸 Screenshot saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save screenshot: {e}")
            return False
    
    def screenshot_to_base64(self, monitor: Optional[int] = None, 
                           region: Optional[Tuple[int, int, int, int]] = None) -> Optional[str]:
        """Capture screenshot and return as base64 string"""
        try:
            img = self.capture_screenshot(monitor, region)
            if img is None:
                return None
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, self.config.compression_quality])
            
            # Convert to base64
            base64_str = base64.b64encode(buffer).decode('utf-8')
            return base64_str
            
        except Exception as e:
            print(f"❌ Base64 encoding failed: {e}")
            return None
    
    def enable_ocr(self, vision_client=None):
        """Enable OCR functionality"""
        if vision_client is None:
            try:
                from ..vision.vision_client import VisionClient
                self.vision_client = VisionClient()
            except Exception as e:
                print(f"❌ Failed to initialize vision client: {e}")
                return False
        else:
            self.vision_client = vision_client
        
        self.ocr_enabled = True
        print("📺 OCR enabled for screen capture")
        return True
    
    def extract_text_from_screen(self, monitor: Optional[int] = None, 
                                region: Optional[Tuple[int, int, int, int]] = None) -> Optional[str]:
        """Extract text from screen using OCR"""
        if not self.ocr_enabled or not self.vision_client:
            print("❌ OCR not enabled")
            return None
        
        try:
            # Capture screenshot
            img = self.capture_screenshot(monitor, region)
            if img is None:
                return None
            
            # Convert to bytes
            _, buffer = cv2.imencode('.jpg', img)
            image_bytes = buffer.tobytes()
            
            # Extract text using vision service
            result = self.vision_client.extract_text_ocr(image_bytes)
            
            if result.get('success') and result.get('extracted_text'):
                text = result['extracted_text'].strip()
                print(f"📺 Extracted {len(text)} characters from screen")
                return text
            else:
                print("⚠️ No text extracted from screen")
                return None
                
        except Exception as e:
            print(f"❌ Screen OCR failed: {e}")
            return None
    
    def analyze_screen_content(self, prompt: str = "Describe what you see on this screen", 
                             monitor: Optional[int] = None, 
                             region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Dict]:
        """Analyze screen content using vision AI"""
        if not self.vision_client:
            print("❌ Vision client not available")
            return None
        
        try:
            # Capture screenshot
            img = self.capture_screenshot(monitor, region)
            if img is None:
                return None
            
            # Analyze using vision AI
            result = self.vision_client.analyze_frame(img, prompt)
            
            if result.get('success'):
                print(f"📺 Screen analysis: {result['description'][:100]}...")
                return result
            else:
                print(f"❌ Screen analysis failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Screen analysis failed: {e}")
            return None
    
    def detect_ui_elements(self, monitor: Optional[int] = None, 
                          region: Optional[Tuple[int, int, int, int]] = None) -> Optional[List[Dict]]:
        """Detect UI elements on screen"""
        if not self.vision_client:
            print("❌ Vision client not available")
            return None
        
        try:
            # Capture screenshot
            img = self.capture_screenshot(monitor, region)
            if img is None:
                return None
            
            # Convert to bytes
            _, buffer = cv2.imencode('.jpg', img)
            image_bytes = buffer.tobytes()
            
            # Detect UI elements
            result = self.vision_client.detect_ui_elements(image_bytes)
            
            if result.get('success') and result.get('ui_elements'):
                ui_elements = result['ui_elements']
                print(f"📺 Detected {len(ui_elements)} UI elements")
                return ui_elements
            else:
                print("⚠️ No UI elements detected")
                return []
                
        except Exception as e:
            print(f"❌ UI element detection failed: {e}")
            return None
    
    def capture_window_by_title(self, window_title: str) -> Optional[np.ndarray]:
        """Capture specific window by title (platform-specific)"""
        try:
            import platform
            system = platform.system()
            
            if system == "Linux":
                return self._capture_window_linux(window_title)
            elif system == "Windows":
                return self._capture_window_windows(window_title)
            elif system == "Darwin":  # macOS
                return self._capture_window_macos(window_title)
            else:
                print(f"⚠️ Window capture not supported on {system}")
                return None
                
        except Exception as e:
            print(f"❌ Window capture failed: {e}")
            return None
    
    def _capture_window_linux(self, window_title: str) -> Optional[np.ndarray]:
        """Capture window on Linux using xwininfo and xwd"""
        try:
            import subprocess
            
            # Find window ID
            result = subprocess.run(['xwininfo', '-name', window_title], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"⚠️ Window '{window_title}' not found")
                return None
            
            # Extract window geometry
            lines = result.stdout.split('\n')
            x = y = width = height = 0
            
            for line in lines:
                if 'Absolute upper-left X:' in line:
                    x = int(line.split(':')[1].strip())
                elif 'Absolute upper-left Y:' in line:
                    y = int(line.split(':')[1].strip())
                elif 'Width:' in line:
                    width = int(line.split(':')[1].strip())
                elif 'Height:' in line:
                    height = int(line.split(':')[1].strip())
            
            if width > 0 and height > 0:
                return self.capture_screenshot(region=(x, y, width, height))
            
            return None
            
        except Exception as e:
            print(f"❌ Linux window capture failed: {e}")
            return None
    
    def _capture_window_windows(self, window_title: str) -> Optional[np.ndarray]:
        """Capture window on Windows"""
        # Would need pywin32 for full implementation
        print("⚠️ Windows window capture not implemented")
        return None
    
    def _capture_window_macos(self, window_title: str) -> Optional[np.ndarray]:
        """Capture window on macOS"""
        # Would need PyObjC for full implementation
        print("⚠️ macOS window capture not implemented")
        return None
    
    def get_capture_stats(self) -> Dict:
        """Get screen capture statistics"""
        avg_time = (self.total_capture_time / self.screenshots_taken 
                   if self.screenshots_taken > 0 else 0)
        
        return {
            'screenshots_taken': self.screenshots_taken,
            'total_capture_time': self.total_capture_time,
            'average_capture_time': avg_time,
            'monitors_available': len(self.monitors) - 1,
            'ocr_enabled': self.ocr_enabled,
            'vision_client_connected': self.vision_client.is_connected() if self.vision_client else False
        }
    
    def cleanup(self):
        """Clean up resources"""
        if self.vision_client:
            self.vision_client.close()
            self.vision_client = None
        
        if self.sct:
            self.sct.close()
        
        print("📺 Screen capture cleaned up")


# Test function
def test_screen_capture():
    """Test screen capture functionality"""
    print("📺 Testing screen capture...")
    
    try:
        capture = ScreenCapture()
        
        # Get monitors
        monitors = capture.get_monitors()
        print(f"Available monitors: {len(monitors)}")
        
        # Take screenshot
        img = capture.capture_screenshot()
        if img is not None:
            print(f"Screenshot captured: {img.shape}")
            
            # Save test screenshot
            capture.save_screenshot("test_screenshot.jpg")
        
        # Test OCR if vision service available
        if capture.enable_ocr():
            text = capture.extract_text_from_screen()
            if text:
                print(f"Extracted text: {text[:100]}...")
        
        # Get stats
        stats = capture.get_capture_stats()
        print(f"Capture stats: {stats}")
        
        capture.cleanup()
        print("✅ Screen capture test completed")
        
    except Exception as e:
        print(f"❌ Screen capture test failed: {e}")


if __name__ == "__main__":
    test_screen_capture()

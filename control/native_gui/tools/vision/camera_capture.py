"""
Camera Capture Module for Real-time Video Recording and Image Capture
Provides OpenCV-based camera capture for vision AI integration.
"""

import cv2
import numpy as np
import threading
import time
import io
import collections
from typing import Optional, Callable, List, Tuple, Dict, Deque
from dataclasses import dataclass
from pathlib import Path
import base64
import queue
import sys
import os

# Add event framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../libs/event-framework/python/src'))
from unhinged_events import create_gui_logger

# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-vision-tool", "1.0.0")

# YOLO imports
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    gui_logger.info("YOLO object detection available", {
        "event_type": "feature_availability",
        "component": "vision_analysis",
        "feature": "yolo_detection",
        "status": "available"
    })
except ImportError:
    gui_logger.warn("YOLO not available - install with: pip install ultralytics", {
        "event_type": "dependency_missing",
        "component": "vision_analysis",
        "dependency": "ultralytics",
        "install_command": "pip install ultralytics"
    })
    YOLO_AVAILABLE = False


@dataclass
class CameraConfig:
    """Camera capture configuration"""
    width: int = 640           # Frame width
    height: int = 480          # Frame height
    fps: int = 30              # Frames per second
    device_index: int = 0      # Camera device index
    format: str = "BGR"        # Color format (BGR, RGB, GRAY)
    buffer_size: int = 30      # Frame buffer size
    auto_exposure: bool = True # Auto exposure control
    brightness: float = 0.5    # Brightness (0.0 to 1.0)
    contrast: float = 0.5      # Contrast (0.0 to 1.0)

    # Advanced buffering options
    circular_buffer: bool = True    # Use circular buffer
    frame_queue_size: int = 10      # Frame queue size for processing
    motion_detection: bool = False  # Enable motion detection
    object_detection: bool = False  # Enable YOLO object detection
    face_detection: bool = False    # Enable face detection (via YOLO)
    recording_buffer_seconds: int = 5  # Seconds of video to buffer for recording

    # YOLO configuration
    yolo_model: str = "yolov8n.pt"  # YOLO model (nano for speed)
    yolo_confidence: float = 0.5    # Detection confidence threshold
    yolo_classes: List[int] = None  # Specific classes to detect (None = all)


class CameraCapture:
    """Real-time camera capture using OpenCV"""
    
    def __init__(self, config: Optional[CameraConfig] = None):
        self.config = config or CameraConfig()
        self.cap = None
        self.is_capturing = False
        self.capture_thread = None
        self.frame_lock = threading.Lock()

        # Advanced buffering system
        if self.config.circular_buffer:
            self.frame_buffer: Deque[np.ndarray] = collections.deque(maxlen=self.config.buffer_size)
        else:
            self.frame_buffer: List[np.ndarray] = []

        # Frame processing queues
        self.frame_queue = queue.Queue(maxsize=self.config.frame_queue_size)
        self.processing_queue = queue.Queue(maxsize=self.config.frame_queue_size)

        # Current state
        self.current_frame = None
        self.previous_frame = None  # For motion detection

        # Video recording
        self.video_writer = None
        self.is_recording_video = False
        self.recording_start_time = None
        self.recording_filename = None

        # Video recording buffer
        recording_buffer_frames = int(self.config.fps * self.config.recording_buffer_seconds)
        self.recording_buffer: Deque[np.ndarray] = collections.deque(maxlen=recording_buffer_frames)

        # Callbacks
        self.on_frame_captured: Optional[Callable[[np.ndarray], None]] = None
        self.on_motion_detected: Optional[Callable[[np.ndarray, float], None]] = None
        self.on_objects_detected: Optional[Callable[[List], None]] = None
        self.on_face_detected: Optional[Callable[[List], None]] = None
        self.on_buffer_full: Optional[Callable[[], None]] = None
        self.on_vision_analysis: Optional[Callable[[Dict], None]] = None
        self.on_ocr_text: Optional[Callable[[str], None]] = None

        # Statistics and monitoring
        self.frames_captured = 0
        self.frames_dropped = 0
        self.fps_actual = 0.0
        self.last_fps_time = time.time()
        self.motion_threshold = 1000  # Motion detection threshold

        # Processing threads
        self.processing_thread = None
        self.is_processing = False

        # YOLO model
        self.yolo_model = None
        if YOLO_AVAILABLE and (self.config.object_detection or self.config.face_detection):
            self._initialize_yolo()

        # Vision service client
        self.vision_client = None
        self.vision_analysis_enabled = False
        self.vision_analysis_interval = 2.0  # Analyze every 2 seconds
        self.last_vision_analysis = 0

        # Initialize camera
        self._initialize_camera()
    
    def _initialize_camera(self):
        """Initialize camera with error handling"""
        try:
            # Try to open camera
            self.cap = cv2.VideoCapture(self.config.device_index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Could not open camera device {self.config.device_index}")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Set exposure and brightness if supported
            if self.config.auto_exposure:
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
            
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.config.brightness)
            self.cap.set(cv2.CAP_PROP_CONTRAST, self.config.contrast)
            
            # Get actual camera properties
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            gui_logger.info("Camera initialized successfully", {
                "event_type": "camera_initialization",
                "component": "camera_capture",
                "width": actual_width,
                "height": actual_height,
                "fps": actual_fps,
                "device_index": self.config.device_index
            })

        except Exception as e:
            gui_logger.error("Failed to initialize camera", exception=e, metadata={
                "event_type": "camera_initialization_failure",
                "component": "camera_capture",
                "device_index": self.config.device_index,
                "error_category": "hardware"
            })
            if self.cap:
                self.cap.release()
                self.cap = None
            raise

    def _initialize_yolo(self):
        """Initialize YOLO model for object detection"""
        try:
            gui_logger.info("Loading YOLO model", {
                "event_type": "model_loading",
                "component": "vision_analysis",
                "model": self.config.yolo_model
            })
            self.yolo_model = YOLO(self.config.yolo_model)

            # Test model with dummy data
            dummy_frame = np.zeros((640, 480, 3), dtype=np.uint8)
            results = self.yolo_model(dummy_frame, verbose=False)

            gui_logger.info("YOLO model loaded successfully", {
                "event_type": "model_loaded",
                "component": "vision_analysis",
                "model": self.config.yolo_model,
                "status": "ready"
            })

        except Exception as e:
            print(f"❌ Failed to initialize YOLO: {e}")
            self.yolo_model = None

    def enable_vision_analysis(self, vision_client=None, interval: float = 2.0):
        """Enable vision AI analysis of frames"""
        if vision_client is None:
            try:
                from .vision_client import VisionClient
                self.vision_client = VisionClient()
            except Exception as e:
                print(f"❌ Failed to initialize vision client: {e}")
                return False
        else:
            self.vision_client = vision_client

        self.vision_analysis_enabled = True
        self.vision_analysis_interval = interval
        print(f"🎯 Vision analysis enabled (interval: {interval}s)")
        return True

    def disable_vision_analysis(self):
        """Disable vision AI analysis"""
        self.vision_analysis_enabled = False
        if self.vision_client:
            self.vision_client.close()
            self.vision_client = None
        print("🎯 Vision analysis disabled")
    
    def get_available_cameras(self) -> List[Dict[str, any]]:
        """Get comprehensive list of available camera devices"""
        cameras = []

        # Test camera indices 0-9 (covers most systems)
        for i in range(10):
            try:
                test_cap = cv2.VideoCapture(i)
                if test_cap.isOpened():
                    # Test if we can actually read a frame
                    ret, frame = test_cap.read()
                    if ret and frame is not None:
                        # Get detailed camera info
                        width = int(test_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(test_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = test_cap.get(cv2.CAP_PROP_FPS)

                        # Get additional properties
                        brightness = test_cap.get(cv2.CAP_PROP_BRIGHTNESS)
                        contrast = test_cap.get(cv2.CAP_PROP_CONTRAST)
                        saturation = test_cap.get(cv2.CAP_PROP_SATURATION)

                        # Determine camera type/name
                        camera_name = self._get_camera_name(i)

                        camera_info = {
                            'index': i,
                            'name': camera_name,
                            'width': width,
                            'height': height,
                            'fps': fps,
                            'brightness': brightness,
                            'contrast': contrast,
                            'saturation': saturation,
                            'is_available': True,
                            'supports_capture': True,
                            'backend': self._get_camera_backend(test_cap)
                        }

                        # Test different resolutions
                        camera_info['supported_resolutions'] = self._test_camera_resolutions(test_cap)

                        cameras.append(camera_info)

                test_cap.release()

            except Exception as e:
                print(f"⚠️ Error testing camera {i}: {e}")
                continue

        return cameras

    def _get_camera_name(self, index: int) -> str:
        """Get descriptive camera name based on index and system"""
        import platform
        system = platform.system()

        if system == "Linux":
            try:
                # Try to read from /sys/class/video4linux/
                device_path = f"/sys/class/video4linux/video{index}/name"
                if Path(device_path).exists():
                    with open(device_path, 'r') as f:
                        return f.read().strip()
            except:
                pass

        # Default naming
        if index == 0:
            return "Default Camera"
        elif index == 1:
            return "External Camera"
        else:
            return f"Camera {index}"

    def _get_camera_backend(self, cap) -> str:
        """Get camera backend information"""
        try:
            backend_name = cap.getBackendName()
            return backend_name
        except:
            return "Unknown"

    def _test_camera_resolutions(self, cap) -> List[Tuple[int, int]]:
        """Test supported camera resolutions"""
        common_resolutions = [
            (320, 240),   # QVGA
            (640, 480),   # VGA
            (800, 600),   # SVGA
            (1024, 768),  # XGA
            (1280, 720),  # HD
            (1920, 1080), # Full HD
            (2560, 1440), # QHD
            (3840, 2160)  # 4K
        ]

        supported = []
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        for width, height in common_resolutions:
            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

                actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                if actual_width == width and actual_height == height:
                    supported.append((width, height))

            except:
                continue

        # Restore original resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, original_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, original_height)

        return supported

    def switch_camera(self, device_index: int) -> bool:
        """Switch to a different camera device"""
        if device_index == self.config.device_index:
            print(f"⚠️ Already using camera {device_index}")
            return True

        was_capturing = self.is_capturing

        try:
            # Stop current capture
            if was_capturing:
                self.stop_capture()

            # Release current camera
            if self.cap:
                self.cap.release()
                self.cap = None

            # Update config and reinitialize
            self.config.device_index = device_index
            self._initialize_camera()

            # Restart capture if it was running
            if was_capturing:
                self.start_capture()

            print(f"📹 Switched to camera {device_index}")
            return True

        except Exception as e:
            print(f"❌ Failed to switch camera: {e}")
            return False

    def get_camera_capabilities(self, device_index: Optional[int] = None) -> Dict:
        """Get detailed capabilities of a camera"""
        if device_index is None:
            device_index = self.config.device_index

        capabilities = {
            'device_index': device_index,
            'properties': {},
            'supported_formats': [],
            'controls': {}
        }

        try:
            test_cap = cv2.VideoCapture(device_index)
            if not test_cap.isOpened():
                return capabilities

            # Test various properties
            properties = [
                ('FRAME_WIDTH', cv2.CAP_PROP_FRAME_WIDTH),
                ('FRAME_HEIGHT', cv2.CAP_PROP_FRAME_HEIGHT),
                ('FPS', cv2.CAP_PROP_FPS),
                ('BRIGHTNESS', cv2.CAP_PROP_BRIGHTNESS),
                ('CONTRAST', cv2.CAP_PROP_CONTRAST),
                ('SATURATION', cv2.CAP_PROP_SATURATION),
                ('HUE', cv2.CAP_PROP_HUE),
                ('GAIN', cv2.CAP_PROP_GAIN),
                ('EXPOSURE', cv2.CAP_PROP_EXPOSURE),
                ('AUTO_EXPOSURE', cv2.CAP_PROP_AUTO_EXPOSURE),
                ('FOCUS', cv2.CAP_PROP_FOCUS),
                ('AUTOFOCUS', cv2.CAP_PROP_AUTOFOCUS)
            ]

            for prop_name, prop_id in properties:
                try:
                    value = test_cap.get(prop_id)
                    capabilities['properties'][prop_name] = value
                except:
                    capabilities['properties'][prop_name] = None

            # Test supported resolutions
            capabilities['supported_resolutions'] = self._test_camera_resolutions(test_cap)

            test_cap.release()

        except Exception as e:
            print(f"⚠️ Error getting camera capabilities: {e}")

        return capabilities

    def start_video_recording(self, filename: str, codec: str = 'mp4v', fps: Optional[int] = None) -> bool:
        """Start recording video to file"""
        if self.is_recording_video:
            print("⚠️ Already recording video")
            return False

        if not self.is_capturing:
            print("❌ Camera not capturing - start capture first")
            return False

        try:
            # Use current FPS or specified FPS
            recording_fps = fps or self.config.fps

            # Get current frame size
            if self.current_frame is None:
                print("❌ No current frame available")
                return False

            height, width = self.current_frame.shape[:2]

            # Define codec
            fourcc = cv2.VideoWriter_fourcc(*codec)

            # Create video writer
            self.video_writer = cv2.VideoWriter(filename, fourcc, recording_fps, (width, height))

            if not self.video_writer.isOpened():
                print(f"❌ Failed to open video writer for {filename}")
                return False

            self.is_recording_video = True
            self.recording_start_time = time.time()
            self.recording_filename = filename

            print(f"🎬 Started video recording: {filename} ({width}x{height} @ {recording_fps}fps)")
            return True

        except Exception as e:
            print(f"❌ Failed to start video recording: {e}")
            return False

    def stop_video_recording(self) -> Optional[str]:
        """Stop video recording and return filename"""
        if not self.is_recording_video:
            print("⚠️ Not recording video")
            return None

        try:
            self.is_recording_video = False

            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

            recording_duration = time.time() - self.recording_start_time if self.recording_start_time else 0
            filename = self.recording_filename

            print(f"🎬 Video recording stopped: {filename} ({recording_duration:.1f}s)")

            self.recording_start_time = None
            self.recording_filename = None

            return filename

        except Exception as e:
            print(f"❌ Error stopping video recording: {e}")
            return None

    def create_video_from_frames(self, frames: List[np.ndarray], filename: str,
                                fps: int = 30, codec: str = 'mp4v') -> bool:
        """Create video file from list of frames"""
        if not frames:
            print("❌ No frames provided")
            return False

        try:
            # Get frame dimensions
            height, width = frames[0].shape[:2]

            # Define codec
            fourcc = cv2.VideoWriter_fourcc(*codec)

            # Create video writer
            video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))

            if not video_writer.isOpened():
                print(f"❌ Failed to create video writer for {filename}")
                return False

            # Write frames
            for i, frame in enumerate(frames):
                # Convert RGB to BGR if needed
                if self.config.format == "RGB":
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                video_writer.write(frame)

                if (i + 1) % 30 == 0:  # Progress every 30 frames
                    print(f"🎬 Writing frame {i+1}/{len(frames)}")

            video_writer.release()

            duration = len(frames) / fps
            print(f"🎬 Video created: {filename} ({len(frames)} frames, {duration:.1f}s)")
            return True

        except Exception as e:
            print(f"❌ Error creating video from frames: {e}")
            return False
    
    def start_capture(self) -> bool:
        """Start camera capture"""
        if self.is_capturing:
            print("⚠️ Camera already capturing")
            return False
        
        if not self.cap or not self.cap.isOpened():
            print("❌ Camera not initialized")
            return False
        
        try:
            self.is_capturing = True
            self.is_processing = True
            self.frames_captured = 0
            self.frames_dropped = 0
            self.last_fps_time = time.time()

            # Clear queues and buffers
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break

            while not self.processing_queue.empty():
                try:
                    self.processing_queue.get_nowait()
                except queue.Empty:
                    break

            # Start capture thread
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True
            )
            self.capture_thread.start()

            # Start processing thread
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                daemon=True
            )
            self.processing_thread.start()

            print("📹 Camera capture and processing started")
            return True

        except Exception as e:
            print(f"❌ Failed to start capture: {e}")
            self.is_capturing = False
            self.is_processing = False
            return False
    
    def stop_capture(self):
        """Stop camera capture and processing"""
        if not self.is_capturing:
            print("⚠️ Camera not capturing")
            return

        self.is_capturing = False
        self.is_processing = False

        # Wait for threads to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)

        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)

        print("📹 Camera capture and processing stopped")
    
    def _capture_loop(self):
        """Enhanced capture loop with advanced buffering"""
        frame_time = 1.0 / self.config.fps

        try:
            while self.is_capturing and self.cap and self.cap.isOpened():
                start_time = time.time()

                # Capture frame
                ret, frame = self.cap.read()

                if not ret:
                    print("⚠️ Failed to capture frame")
                    self.frames_dropped += 1
                    continue

                # Convert color format if needed
                if self.config.format == "RGB":
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                elif self.config.format == "GRAY":
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Update current frame and buffers
                with self.frame_lock:
                    self.previous_frame = self.current_frame
                    self.current_frame = frame.copy()

                    # Add to main buffer
                    if self.config.circular_buffer:
                        self.frame_buffer.append(frame.copy())
                    else:
                        self.frame_buffer.append(frame.copy())
                        if len(self.frame_buffer) > self.config.buffer_size:
                            self.frame_buffer.pop(0)

                    # Add to recording buffer
                    self.recording_buffer.append(frame.copy())

                # Add to processing queue (non-blocking)
                try:
                    self.frame_queue.put_nowait(frame.copy())
                except queue.Full:
                    # Drop oldest frame if queue is full
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame.copy())
                        self.frames_dropped += 1
                    except queue.Empty:
                        pass

                # Update statistics
                self.frames_captured += 1
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    self.fps_actual = self.frames_captured / (current_time - self.last_fps_time)
                    self.frames_captured = 0
                    self.last_fps_time = current_time

                # Write to video file if recording
                if self.is_recording_video and self.video_writer:
                    # Convert RGB to BGR for video writing
                    video_frame = frame
                    if self.config.format == "RGB":
                        video_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    self.video_writer.write(video_frame)

                # Call frame callback
                if self.on_frame_captured:
                    self.on_frame_captured(frame)

                # Frame rate control
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as e:
            print(f"❌ Error in capture loop: {e}")
        finally:
            self.is_capturing = False

    def _processing_loop(self):
        """Processing loop for motion detection, face detection, etc."""
        try:
            while self.is_processing:
                try:
                    # Get frame from queue (blocking with timeout)
                    frame = self.frame_queue.get(timeout=1.0)

                    # Motion detection
                    if self.config.motion_detection and self.previous_frame is not None:
                        motion_level = self._detect_motion(frame, self.previous_frame)
                        if motion_level > self.motion_threshold and self.on_motion_detected:
                            self.on_motion_detected(frame, motion_level)

                    # YOLO object detection
                    if self.config.object_detection and self.yolo_model:
                        detections = self._detect_objects_yolo(frame)
                        if detections and self.on_objects_detected:
                            self.on_objects_detected(detections)

                    # Face detection (via YOLO or OpenCV)
                    if self.config.face_detection:
                        if self.yolo_model:
                            faces = self._detect_faces_yolo(frame)
                        else:
                            faces = self._detect_faces_opencv(frame)

                        if faces and self.on_face_detected:
                            self.on_face_detected(faces)

                    # Vision AI analysis (periodic)
                    if self.vision_analysis_enabled and self.vision_client:
                        current_time = time.time()
                        if current_time - self.last_vision_analysis >= self.vision_analysis_interval:
                            self._analyze_frame_with_vision(frame)
                            self.last_vision_analysis = current_time

                    # Add to processing queue for external processing
                    try:
                        self.processing_queue.put_nowait(frame)
                    except queue.Full:
                        # Drop oldest processed frame
                        try:
                            self.processing_queue.get_nowait()
                            self.processing_queue.put_nowait(frame)
                        except queue.Empty:
                            pass

                except queue.Empty:
                    continue  # Timeout, check if still processing
                except Exception as e:
                    print(f"⚠️ Error in processing loop: {e}")

        except Exception as e:
            print(f"❌ Error in processing loop: {e}")
        finally:
            self.is_processing = False

    def _detect_motion(self, current_frame: np.ndarray, previous_frame: np.ndarray) -> float:
        """Simple motion detection using frame difference"""
        try:
            # Convert to grayscale if needed
            if len(current_frame.shape) == 3:
                current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            else:
                current_gray = current_frame

            if len(previous_frame.shape) == 3:
                previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
            else:
                previous_gray = previous_frame

            # Calculate frame difference
            diff = cv2.absdiff(current_gray, previous_gray)

            # Apply threshold
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

            # Calculate motion level (number of changed pixels)
            motion_level = np.sum(thresh) / 255

            return motion_level

        except Exception as e:
            print(f"⚠️ Motion detection error: {e}")
            return 0.0

    def _detect_objects_yolo(self, frame: np.ndarray) -> List[Dict]:
        """YOLO-based object detection"""
        try:
            if not self.yolo_model:
                return []

            # Run YOLO inference
            results = self.yolo_model(frame, verbose=False, conf=self.config.yolo_confidence)

            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())

                        # Get class name
                        class_name = self.yolo_model.names[class_id]

                        # Filter by classes if specified
                        if self.config.yolo_classes and class_id not in self.config.yolo_classes:
                            continue

                        detection = {
                            'bbox': (int(x1), int(y1), int(x2-x1), int(y2-y1)),  # x, y, w, h
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': class_name,
                            'center': (int((x1+x2)/2), int((y1+y2)/2))
                        }
                        detections.append(detection)

            return detections

        except Exception as e:
            print(f"⚠️ YOLO object detection error: {e}")
            return []

    def _detect_faces_yolo(self, frame: np.ndarray) -> List[Dict]:
        """YOLO-based face detection (person class)"""
        try:
            # Use YOLO to detect persons, then assume faces are in upper portion
            detections = self._detect_objects_yolo(frame)

            faces = []
            for detection in detections:
                if detection['class_name'] == 'person':
                    # Estimate face location (upper 1/4 of person bounding box)
                    x, y, w, h = detection['bbox']
                    face_h = h // 4
                    face_w = w // 2
                    face_x = x + (w - face_w) // 2
                    face_y = y

                    face = {
                        'bbox': (face_x, face_y, face_w, face_h),
                        'confidence': detection['confidence'],
                        'type': 'estimated_face'
                    }
                    faces.append(face)

            return faces

        except Exception as e:
            print(f"⚠️ YOLO face detection error: {e}")
            return []

    def _detect_faces_opencv(self, frame: np.ndarray) -> List[Dict]:
        """OpenCV Haar cascade face detection (fallback)"""
        try:
            # Convert to grayscale
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame

            # Load face cascade (this should be cached in a real implementation)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Detect faces
            faces_raw = face_cascade.detectMultiScale(gray, 1.1, 4)

            faces = []
            for (x, y, w, h) in faces_raw:
                face = {
                    'bbox': (x, y, w, h),
                    'confidence': 0.8,  # Haar cascades don't provide confidence
                    'type': 'opencv_face'
                }
                faces.append(face)

            return faces

        except Exception as e:
            print(f"⚠️ OpenCV face detection error: {e}")
            return []

    def _analyze_frame_with_vision(self, frame: np.ndarray):
        """Analyze frame using vision AI service (non-blocking)"""
        def analyze_async():
            try:
                if not self.vision_client or not self.vision_client.is_connected():
                    return

                # Analyze frame
                result = self.vision_client.analyze_frame(frame, "Describe what you see in this image")

                if result['success']:
                    # Call vision analysis callback
                    if self.on_vision_analysis:
                        self.on_vision_analysis(result)

                    # Extract OCR text if available
                    if result.get('extracted_text') and self.on_ocr_text:
                        self.on_ocr_text(result['extracted_text'])

            except Exception as e:
                print(f"⚠️ Vision analysis error: {e}")

        # Run analysis in background thread
        import threading
        threading.Thread(target=analyze_async, daemon=True).start()
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the most recent frame"""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def capture_image(self) -> Optional[np.ndarray]:
        """Capture a single image"""
        if not self.cap or not self.cap.isOpened():
            print("❌ Camera not available")
            return None
        
        try:
            ret, frame = self.cap.read()
            if ret:
                # Convert color format if needed
                if self.config.format == "RGB":
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                elif self.config.format == "GRAY":
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                print("📸 Image captured")
                return frame
            else:
                print("❌ Failed to capture image")
                return None
                
        except Exception as e:
            print(f"❌ Error capturing image: {e}")
            return None
    
    def save_image(self, filename: str, frame: Optional[np.ndarray] = None) -> bool:
        """Save image to file"""
        try:
            if frame is None:
                frame = self.capture_image()
            
            if frame is None:
                return False
            
            # Convert RGB back to BGR for saving
            if self.config.format == "RGB":
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            success = cv2.imwrite(filename, frame)
            if success:
                print(f"📸 Image saved to {filename}")
            else:
                print(f"❌ Failed to save image to {filename}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error saving image: {e}")
            return False
    
    def frame_to_base64(self, frame: Optional[np.ndarray] = None) -> Optional[str]:
        """Convert frame to base64 string"""
        try:
            if frame is None:
                frame = self.get_current_frame()
            
            if frame is None:
                return None
            
            # Convert to BGR for encoding
            if self.config.format == "RGB":
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            
            # Convert to base64
            base64_str = base64.b64encode(buffer).decode('utf-8')
            
            return base64_str

        except Exception as e:
            print(f"❌ Error converting frame to base64: {e}")
            return None

    def get_frame_buffer(self) -> List[np.ndarray]:
        """Get copy of current frame buffer"""
        with self.frame_lock:
            if self.config.circular_buffer:
                return list(self.frame_buffer)
            else:
                return self.frame_buffer.copy()

    def get_recording_buffer(self) -> List[np.ndarray]:
        """Get copy of recording buffer"""
        with self.frame_lock:
            return list(self.recording_buffer)

    def get_processed_frame(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """Get a processed frame from the processing queue"""
        try:
            return self.processing_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def capture_burst(self, count: int = 5, interval: float = 0.1) -> List[np.ndarray]:
        """Capture a burst of images"""
        frames = []

        if not self.cap or not self.cap.isOpened():
            print("❌ Camera not available for burst capture")
            return frames

        try:
            for i in range(count):
                frame = self.capture_image()
                if frame is not None:
                    frames.append(frame)
                    print(f"📸 Burst capture {i+1}/{count}")
                else:
                    print(f"❌ Failed to capture burst frame {i+1}")

                if i < count - 1:  # Don't sleep after last frame
                    time.sleep(interval)

            print(f"📸 Burst capture completed: {len(frames)}/{count} frames")
            return frames

        except Exception as e:
            print(f"❌ Error in burst capture: {e}")
            return frames

    def save_frame_buffer(self, directory: str, prefix: str = "frame") -> int:
        """Save all frames in buffer to files"""
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)

            frames = self.get_frame_buffer()
            saved_count = 0

            for i, frame in enumerate(frames):
                filename = f"{directory}/{prefix}_{i:04d}.jpg"
                if self.save_image(filename, frame):
                    saved_count += 1

            print(f"📸 Saved {saved_count}/{len(frames)} frames to {directory}")
            return saved_count

        except Exception as e:
            print(f"❌ Error saving frame buffer: {e}")
            return 0

    def create_timelapse_frames(self, duration_seconds: int, interval_seconds: float = 1.0) -> List[np.ndarray]:
        """Capture frames for timelapse over specified duration"""
        frames = []
        start_time = time.time()
        next_capture = start_time

        print(f"📹 Starting timelapse capture for {duration_seconds} seconds...")

        try:
            while time.time() - start_time < duration_seconds:
                current_time = time.time()

                if current_time >= next_capture:
                    frame = self.capture_image()
                    if frame is not None:
                        frames.append(frame)
                        elapsed = current_time - start_time
                        print(f"📸 Timelapse frame {len(frames)} at {elapsed:.1f}s")

                    next_capture = current_time + interval_seconds

                time.sleep(0.1)  # Small sleep to prevent busy waiting

            print(f"📹 Timelapse capture completed: {len(frames)} frames")
            return frames

        except Exception as e:
            print(f"❌ Error in timelapse capture: {e}")
            return frames

    def get_motion_frames(self, threshold: float = None) -> List[Tuple[np.ndarray, float]]:
        """Get frames where motion was detected above threshold"""
        if threshold is None:
            threshold = self.motion_threshold

        motion_frames = []
        frames = self.get_frame_buffer()

        if len(frames) < 2:
            return motion_frames

        try:
            for i in range(1, len(frames)):
                motion_level = self._detect_motion(frames[i], frames[i-1])
                if motion_level > threshold:
                    motion_frames.append((frames[i], motion_level))

            print(f"🎯 Found {len(motion_frames)} frames with motion > {threshold}")
            return motion_frames

        except Exception as e:
            print(f"❌ Error getting motion frames: {e}")
            return motion_frames

    def annotate_frame_with_faces(self, frame: np.ndarray) -> np.ndarray:
        """Annotate frame with detected faces"""
        try:
            annotated_frame = frame.copy()
            faces = self._detect_faces(frame)

            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Add label
                cv2.putText(annotated_frame, 'Face', (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            return annotated_frame

        except Exception as e:
            print(f"❌ Error annotating frame: {e}")
            return frame
    
    def get_camera_info(self) -> Dict[str, any]:
        """Get camera information and statistics"""
        info = {
            'is_initialized': self.cap is not None and self.cap.isOpened(),
            'is_capturing': self.is_capturing,
            'device_index': self.config.device_index,
            'resolution': f"{self.config.width}x{self.config.height}",
            'target_fps': self.config.fps,
            'actual_fps': self.fps_actual,
            'frames_captured': self.frames_captured,
            'buffer_size': len(self.frame_buffer),
            'format': self.config.format
        }
        
        if self.cap and self.cap.isOpened():
            info.update({
                'actual_width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'actual_height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'brightness': self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': self.cap.get(cv2.CAP_PROP_CONTRAST)
            })
        
        return info
    
    def cleanup(self):
        """Clean up camera resources"""
        if self.is_capturing:
            self.stop_capture()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Stop video recording if active
        if self.is_recording_video:
            self.stop_video_recording()

        # Clear buffers
        if hasattr(self.frame_buffer, 'clear'):
            self.frame_buffer.clear()
        else:
            self.frame_buffer = []

        self.recording_buffer.clear()
        self.current_frame = None

        print("📹 Camera resources cleaned up")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


# Test function for standalone testing
def test_camera_capture():
    """Test camera capture functionality"""
    print("📹 Testing camera capture...")
    
    try:
        capture = CameraCapture()
        
        # Get available cameras
        cameras = capture.get_available_cameras()
        print(f"Available cameras: {len(cameras)}")
        for camera in cameras:
            print(f"  - Camera {camera['index']}: {camera['width']}x{camera['height']}")
        
        # Test single image capture
        frame = capture.capture_image()
        if frame is not None:
            print(f"Captured image: {frame.shape}")
            
            # Save test image
            capture.save_image("test_capture.jpg", frame)
        
        # Test camera info
        info = capture.get_camera_info()
        print(f"Camera info: {info}")
        
        capture.cleanup()
        print("✅ Camera capture test completed")
        
    except Exception as e:
        print(f"❌ Camera capture test failed: {e}")


if __name__ == "__main__":
    test_camera_capture()

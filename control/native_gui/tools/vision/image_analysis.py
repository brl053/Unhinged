"""
Real-time Image Analysis Pipeline
Combines YOLO object detection with vision AI for comprehensive image understanding.
"""

import cv2
import numpy as np
import threading
import time
import queue
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class AnalysisConfig:
    """Configuration for image analysis pipeline"""
    # YOLO settings
    enable_yolo: bool = True
    yolo_confidence: float = 0.5
    yolo_classes: List[int] = None
    
    # Vision AI settings
    enable_vision_ai: bool = True
    vision_analysis_interval: float = 2.0
    vision_prompt: str = "Describe what you see in this image"
    
    # OCR settings
    enable_ocr: bool = True
    ocr_interval: float = 5.0
    
    # Performance settings
    max_queue_size: int = 10
    analysis_threads: int = 2
    save_annotations: bool = False
    annotation_directory: str = "annotations"


class ImageAnalysisPipeline:
    """Real-time image analysis combining multiple AI models"""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        
        # Analysis queues
        self.frame_queue = queue.Queue(maxsize=self.config.max_queue_size)
        self.result_queue = queue.Queue(maxsize=self.config.max_queue_size)
        
        # Worker threads
        self.analysis_threads = []
        self.is_running = False
        
        # AI models
        self.yolo_model = None
        self.vision_client = None
        
        # Timing control
        self.last_vision_analysis = 0
        self.last_ocr_analysis = 0
        
        # Results storage
        self.latest_results = {}
        self.analysis_history = []
        self.results_lock = threading.Lock()
        
        # Callbacks
        self.on_yolo_detection: Optional[Callable[[List[Dict]], None]] = None
        self.on_vision_analysis: Optional[Callable[[Dict], None]] = None
        self.on_ocr_result: Optional[Callable[[str], None]] = None
        self.on_combined_analysis: Optional[Callable[[Dict], None]] = None
        
        # Statistics
        self.frames_processed = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models"""
        # Initialize YOLO
        if self.config.enable_yolo:
            try:
                from ultralytics import YOLO
                self.yolo_model = YOLO("yolov8n.pt")
                print("🎯 YOLO model initialized")
            except Exception as e:
                print(f"⚠️ YOLO initialization failed: {e}")
                self.config.enable_yolo = False
        
        # Initialize Vision AI client
        if self.config.enable_vision_ai:
            try:
                from .vision_client import VisionClient
                self.vision_client = VisionClient()
                if self.vision_client.is_connected():
                    print("🎯 Vision AI client initialized")
                else:
                    print("⚠️ Vision AI client not connected")
                    self.config.enable_vision_ai = False
            except Exception as e:
                print(f"⚠️ Vision AI initialization failed: {e}")
                self.config.enable_vision_ai = False
    
    def start(self):
        """Start analysis pipeline"""
        if self.is_running:
            print("⚠️ Analysis pipeline already running")
            return
        
        self.is_running = True
        
        # Start worker threads
        for i in range(self.config.analysis_threads):
            thread = threading.Thread(target=self._analysis_worker, args=(i,), daemon=True)
            thread.start()
            self.analysis_threads.append(thread)
        
        print(f"🎯 Analysis pipeline started with {self.config.analysis_threads} threads")
    
    def stop(self):
        """Stop analysis pipeline"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Wait for threads to finish
        for thread in self.analysis_threads:
            if thread.is_alive():
                thread.join(timeout=2.0)
        
        self.analysis_threads.clear()
        print("🎯 Analysis pipeline stopped")
    
    def analyze_frame(self, frame: np.ndarray, frame_id: Optional[str] = None) -> bool:
        """Add frame to analysis queue"""
        if not self.is_running:
            print("⚠️ Analysis pipeline not running")
            return False
        
        try:
            frame_data = {
                'frame': frame.copy(),
                'timestamp': time.time(),
                'frame_id': frame_id or f"frame_{int(time.time() * 1000)}"
            }
            
            self.frame_queue.put_nowait(frame_data)
            return True
            
        except queue.Full:
            print("⚠️ Analysis queue full, dropping frame")
            return False
    
    def _analysis_worker(self, worker_id: int):
        """Worker thread for frame analysis"""
        print(f"🎯 Analysis worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get frame from queue
                frame_data = self.frame_queue.get(timeout=1.0)
                
                # Perform analysis
                result = self._analyze_frame_comprehensive(frame_data)
                
                # Store result
                with self.results_lock:
                    self.latest_results[frame_data['frame_id']] = result
                    self.analysis_history.append(result)
                    
                    # Keep only last 100 results
                    if len(self.analysis_history) > 100:
                        self.analysis_history.pop(0)
                
                # Add to result queue
                try:
                    self.result_queue.put_nowait(result)
                except queue.Full:
                    pass  # Drop result if queue full
                
                # Call callbacks
                self._trigger_callbacks(result)
                
                # Update statistics
                self.frames_processed += 1
                self.total_processing_time += result.get('processing_time', 0)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Analysis worker {worker_id} error: {e}")
                self.error_count += 1
    
    def _analyze_frame_comprehensive(self, frame_data: Dict) -> Dict:
        """Perform comprehensive analysis on frame"""
        start_time = time.time()
        frame = frame_data['frame']
        
        result = {
            'frame_id': frame_data['frame_id'],
            'timestamp': frame_data['timestamp'],
            'analysis_timestamp': start_time,
            'yolo_detections': [],
            'vision_analysis': None,
            'ocr_text': None,
            'processing_time': 0,
            'errors': []
        }
        
        # YOLO object detection
        if self.config.enable_yolo and self.yolo_model:
            try:
                yolo_results = self.yolo_model(frame, verbose=False, conf=self.config.yolo_confidence)
                detections = []
                
                for yolo_result in yolo_results:
                    boxes = yolo_result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = box.conf[0].cpu().numpy()
                            class_id = int(box.cls[0].cpu().numpy())
                            class_name = self.yolo_model.names[class_id]
                            
                            # Filter by classes if specified
                            if self.config.yolo_classes and class_id not in self.config.yolo_classes:
                                continue
                            
                            detection = {
                                'bbox': [int(x1), int(y1), int(x2-x1), int(y2-y1)],
                                'confidence': float(confidence),
                                'class_id': class_id,
                                'class_name': class_name,
                                'center': [int((x1+x2)/2), int((y1+y2)/2)]
                            }
                            detections.append(detection)
                
                result['yolo_detections'] = detections
                
            except Exception as e:
                result['errors'].append(f"YOLO error: {e}")
        
        # Vision AI analysis (periodic)
        current_time = time.time()
        if (self.config.enable_vision_ai and self.vision_client and 
            current_time - self.last_vision_analysis >= self.config.vision_analysis_interval):
            
            try:
                vision_result = self.vision_client.analyze_frame(frame, self.config.vision_prompt)
                result['vision_analysis'] = vision_result
                self.last_vision_analysis = current_time
                
            except Exception as e:
                result['errors'].append(f"Vision AI error: {e}")
        
        # OCR analysis (periodic)
        if (self.config.enable_ocr and self.vision_client and 
            current_time - self.last_ocr_analysis >= self.config.ocr_interval):
            
            try:
                ocr_result = self.vision_client.extract_text_ocr(cv2.imencode('.jpg', frame)[1].tobytes())
                if ocr_result.get('success') and ocr_result.get('extracted_text'):
                    result['ocr_text'] = ocr_result['extracted_text']
                    self.last_ocr_analysis = current_time
                
            except Exception as e:
                result['errors'].append(f"OCR error: {e}")
        
        result['processing_time'] = time.time() - start_time
        return result
    
    def _trigger_callbacks(self, result: Dict):
        """Trigger appropriate callbacks based on analysis results"""
        try:
            # YOLO detections callback
            if result['yolo_detections'] and self.on_yolo_detection:
                self.on_yolo_detection(result['yolo_detections'])
            
            # Vision analysis callback
            if result['vision_analysis'] and self.on_vision_analysis:
                self.on_vision_analysis(result['vision_analysis'])
            
            # OCR callback
            if result['ocr_text'] and self.on_ocr_result:
                self.on_ocr_result(result['ocr_text'])
            
            # Combined analysis callback
            if self.on_combined_analysis:
                self.on_combined_analysis(result)
                
        except Exception as e:
            print(f"⚠️ Callback error: {e}")
    
    def get_latest_result(self, frame_id: Optional[str] = None) -> Optional[Dict]:
        """Get latest analysis result"""
        with self.results_lock:
            if frame_id:
                return self.latest_results.get(frame_id)
            elif self.analysis_history:
                return self.analysis_history[-1]
            return None
    
    def get_analysis_summary(self) -> Dict:
        """Get analysis pipeline statistics"""
        with self.results_lock:
            avg_processing_time = (self.total_processing_time / self.frames_processed 
                                 if self.frames_processed > 0 else 0)
            
            return {
                'frames_processed': self.frames_processed,
                'average_processing_time': avg_processing_time,
                'error_count': self.error_count,
                'queue_size': self.frame_queue.qsize(),
                'result_queue_size': self.result_queue.qsize(),
                'is_running': self.is_running,
                'yolo_enabled': self.config.enable_yolo,
                'vision_ai_enabled': self.config.enable_vision_ai,
                'ocr_enabled': self.config.enable_ocr
            }
    
    def create_annotated_frame(self, frame: np.ndarray, result: Optional[Dict] = None) -> np.ndarray:
        """Create annotated frame with analysis results"""
        if result is None:
            result = self.get_latest_result()
        
        if not result:
            return frame
        
        annotated = frame.copy()
        
        try:
            # Draw YOLO detections
            for detection in result.get('yolo_detections', []):
                x, y, w, h = detection['bbox']
                confidence = detection['confidence']
                class_name = detection['class_name']
                
                # Draw bounding box
                cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Add label
                label = f"{class_name}: {confidence:.2f}"
                cv2.putText(annotated, label, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Add vision analysis text
            vision_analysis = result.get('vision_analysis')
            if vision_analysis and vision_analysis.get('success'):
                description = vision_analysis['description'][:80] + "..." if len(vision_analysis['description']) > 80 else vision_analysis['description']
                
                # Add background
                overlay = annotated.copy()
                cv2.rectangle(overlay, (10, annotated.shape[0]-50), 
                            (annotated.shape[1]-10, annotated.shape[0]-10), 
                            (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, annotated, 0.3, 0, annotated)
                
                # Add text
                cv2.putText(annotated, description, (15, annotated.shape[0]-25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            return annotated
            
        except Exception as e:
            print(f"⚠️ Annotation error: {e}")
            return frame
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()
        
        if self.vision_client:
            self.vision_client.close()
            self.vision_client = None
        
        # Clear queues
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.result_queue.empty():
            try:
                self.result_queue.get_nowait()
            except queue.Empty:
                break
        
        print("🎯 Analysis pipeline cleaned up")


# Test function
def test_analysis_pipeline():
    """Test image analysis pipeline"""
    print("🎯 Testing analysis pipeline...")
    
    try:
        config = AnalysisConfig(
            enable_yolo=True,
            enable_vision_ai=False,  # Disable for test
            enable_ocr=False
        )
        
        pipeline = ImageAnalysisPipeline(config)
        pipeline.start()
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_frame, 'TEST FRAME', (200, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Analyze frame
        pipeline.analyze_frame(test_frame, "test_frame_1")
        
        # Wait for processing
        time.sleep(2)
        
        # Get results
        result = pipeline.get_latest_result()
        summary = pipeline.get_analysis_summary()
        
        print(f"Analysis result: {result}")
        print(f"Pipeline summary: {summary}")
        
        pipeline.cleanup()
        print("✅ Analysis pipeline test completed")
        
    except Exception as e:
        print(f"❌ Analysis pipeline test failed: {e}")


if __name__ == "__main__":
    test_analysis_pipeline()

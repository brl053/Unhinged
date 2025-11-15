#!/usr/bin/env python3
"""
Hybrid GUI Analysis Service

Combines OpenCV (for structured UI elements) and YOLOv8 (for complex/semantic detection).

OpenCV detects:
  - Buttons, panels, text fields (rectangular regions)
  - Edges, corners, contours
  - Color-based UI elements

YOLOv8 detects:
  - Complex objects in UI (images, icons, people)
  - Semantic understanding of content
  - Non-standard UI patterns

This hybrid approach is efficient and accurate for GUI analysis.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class HybridGUIAnalysisService:
    """Hybrid GUI element detection using OpenCV + YOLOv8"""

    # GUI element classes and their visual characteristics
    ELEMENT_CLASSES = {
        "button": {"color": (0, 255, 0), "priority": 1, "min_area": 100},
        "text_field": {"color": (255, 0, 0), "priority": 2, "min_area": 50},
        "panel": {"color": (0, 0, 255), "priority": 3, "min_area": 500},
        "icon": {"color": (255, 255, 0), "priority": 4, "min_area": 20},
        "label": {"color": (255, 0, 255), "priority": 5, "min_area": 30},
        "menu": {"color": (0, 255, 255), "priority": 6, "min_area": 200},
        "checkbox": {"color": (128, 0, 0), "priority": 7, "min_area": 15},
        "radio": {"color": (0, 128, 0), "priority": 8, "min_area": 15},
        "slider": {"color": (0, 0, 128), "priority": 9, "min_area": 100},
        "table": {"color": (128, 128, 0), "priority": 10, "min_area": 1000},
    }

    def __init__(
        self,
        model_size: str = "m",
        output_dir: Optional[Path] = None,
        use_opencv: bool = True,
        use_yolo: bool = True,
    ):
        """
        Initialize hybrid GUI analysis service.

        Args:
            model_size: YOLOv8 model size ("n" nano, "s" small, "m" medium, "l" large, "x" xlarge)
            output_dir: Directory to save analysis results
            use_opencv: Enable OpenCV-based GUI detection (default: True)
            use_yolo: Enable YOLOv8 detection (default: True)
        """
        self.model_size = model_size
        self.output_dir = output_dir or Path.cwd() / "build" / "tmp" / "generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.use_opencv = use_opencv
        self.use_yolo = use_yolo
        self.model = None
        self.model_loaded = False

        logger.info("Hybrid GUI Analysis Service initialized")
        logger.info(f"OpenCV detection: {'enabled' if use_opencv else 'disabled'}")
        logger.info(f"YOLOv8 detection: {'enabled' if use_yolo else 'disabled'}")
        logger.info(f"YOLOv8 model size: {model_size}")
        logger.info(f"Output directory: {self.output_dir}")

    def _detect_gui_elements_opencv(self, image_path: Path) -> List[Dict[str, Any]]:
        """
        Detect GUI elements using OpenCV (fast, rule-based approach).

        Detects:
        - Rectangular regions (buttons, panels, text fields)
        - Edges and corners
        - Color-based UI elements

        Args:
            image_path: Path to screenshot image

        Returns:
            List of detected elements with bounding boxes and types
        """
        try:
            import cv2
        except ImportError:
            logger.warning("OpenCV not available, skipping OpenCV detection")
            return []

        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                logger.warning(f"Could not read image: {image_path}")
                return []

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect edges
            edges = cv2.Canny(gray, 50, 150)

            # Find contours (potential UI elements)
            contours, _ = cv2.findContours(
                edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )

            detections = []

            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h

                # Filter by size (avoid noise)
                if area < 50 or area > 500000:
                    continue

                # Approximate shape
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                # Classify based on shape and size
                element_type = "unknown"
                confidence = 0.5

                # Rectangles (buttons, text fields, panels)
                if len(approx) == 4:
                    aspect_ratio = w / h if h > 0 else 0

                    if 0.5 < aspect_ratio < 2.0 and 100 < area < 10000:
                        element_type = "button"
                        confidence = 0.7
                    elif aspect_ratio > 2.0 and 50 < area < 5000:
                        element_type = "text_field"
                        confidence = 0.6
                    elif area > 10000:
                        element_type = "panel"
                        confidence = 0.8

                # Circles (checkboxes, radio buttons)
                elif len(approx) > 6:
                    if 15 < area < 500:
                        element_type = "checkbox"
                        confidence = 0.6

                if element_type != "unknown":
                    detections.append(
                        {
                            "type": element_type,
                            "confidence": confidence,
                            "source": "opencv",
                            "bbox": {
                                "x1": float(x),
                                "y1": float(y),
                                "x2": float(x + w),
                                "y2": float(y + h),
                            },
                            "center": {
                                "x": float(x + w / 2),
                                "y": float(y + h / 2),
                            },
                            "width": float(w),
                            "height": float(h),
                        }
                    )

            logger.info(f"OpenCV detected {len(detections)} GUI elements")
            return detections

        except Exception as e:
            logger.warning(f"OpenCV detection failed: {e}")
            return []

    def _load_model(self):
        """Load YOLOv8 model (lazy loading)"""
        if self.model_loaded:
            return

        try:
            from ultralytics import YOLO

            model_name = f"yolov8{self.model_size}.pt"
            logger.info(f"Loading YOLOv8 model: {model_name}")

            self.model = YOLO(model_name)
            self.model_loaded = True

            logger.info("YOLOv8 model loaded successfully")

        except ImportError:
            logger.error("ultralytics not installed. Run: pip install ultralytics")
            raise
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise

    def analyze_screenshot(
        self, image_path: str, confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Analyze screenshot using hybrid approach (OpenCV + YOLOv8).

        Args:
            image_path: Path to screenshot image
            confidence: Detection confidence threshold (0.0-1.0)

        Returns:
            Dict with:
                - detections: List of detected elements (from both OpenCV and YOLOv8)
                - image_path: Path to analyzed image
                - analysis_time: Time taken in seconds
                - total_detections: Number of elements detected
                - element_counts: Count by element type
                - detection_sources: Count by detection source (opencv/yolo)
                - metadata: Additional metadata
        """
        import time
        from pathlib import Path

        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            logger.info(f"Analyzing screenshot (hybrid): {image_path}")
            start_time = time.time()

            detections = []
            element_counts = {cls: 0 for cls in self.ELEMENT_CLASSES.keys()}
            detection_sources = {"opencv": 0, "yolo": 0}
            image_data = None

            # Step 1: OpenCV detection (fast, rule-based)
            if self.use_opencv:
                logger.info("Running OpenCV GUI detection...")
                opencv_detections = self._detect_gui_elements_opencv(image_path)
                detections.extend(opencv_detections)
                detection_sources["opencv"] = len(opencv_detections)
                for det in opencv_detections:
                    if det["type"] in element_counts:
                        element_counts[det["type"]] += 1

            # Step 2: YOLOv8 detection (semantic, complex objects)
            if self.use_yolo:
                logger.info("Running YOLOv8 detection...")
                self._load_model()

                results = self.model(str(image_path), conf=confidence, verbose=False)
                image_data = results[0] if results and len(results) > 0 else None

                if results and len(results) > 0:
                    result = results[0]

                    if result.boxes is not None:
                        for box in result.boxes:
                            class_id = int(box.cls[0])
                            class_name = result.names.get(class_id, "unknown")

                            detection = {
                                "type": class_name.lower(),
                                "confidence": float(box.conf[0]),
                                "source": "yolo",
                                "bbox": {
                                    "x1": float(box.xyxy[0][0]),
                                    "y1": float(box.xyxy[0][1]),
                                    "x2": float(box.xyxy[0][2]),
                                    "y2": float(box.xyxy[0][3]),
                                },
                                "center": {
                                    "x": float((box.xyxy[0][0] + box.xyxy[0][2]) / 2),
                                    "y": float((box.xyxy[0][1] + box.xyxy[0][3]) / 2),
                                },
                                "width": float(box.xyxy[0][2] - box.xyxy[0][0]),
                                "height": float(box.xyxy[0][3] - box.xyxy[0][1]),
                            }

                            detections.append(detection)
                            detection_sources["yolo"] += 1

            analysis_time = time.time() - start_time

            # Save annotated image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            annotated_filename = f"analysis_{timestamp}.png"
            annotated_path = self.output_dir / annotated_filename

            # Draw annotations on image
            self._draw_annotations(image_path, detections, annotated_path)

            logger.info(
                f"Analysis complete: {len(detections)} elements detected "
                f"(OpenCV: {detection_sources['opencv']}, YOLOv8: {detection_sources['yolo']})"
            )

            return {
                "image_path": str(image_path),
                "annotated_image_path": str(annotated_path),
                "detections": detections,
                "total_detections": len(detections),
                "element_counts": {k: v for k, v in element_counts.items() if v > 0},
                "detection_sources": detection_sources,
                "analysis_time": analysis_time,
                "confidence_threshold": confidence,
                "model_size": self.model_size,
                "timestamp": timestamp,
                "metadata": {
                    "image_width": image_data.orig_shape[1] if image_data else 0,
                    "image_height": image_data.orig_shape[0] if image_data else 0,
                    "detection_method": "hybrid (opencv + yolo)",
                },
            }

        except Exception as e:
            logger.error(f"Screenshot analysis failed: {e}")
            raise

    def _draw_annotations(
        self, image_path: Path, detections: List[Dict], output_path: Path
    ):
        """Draw bounding boxes on image and save."""
        try:
            import cv2
            from PIL import Image, ImageDraw
        except ImportError:
            logger.warning("Could not draw annotations (PIL/OpenCV not available)")
            return

        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            draw = ImageDraw.Draw(image)

            # Draw detections
            for det in detections:
                bbox = det["bbox"]
                x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]

                # Get color for element type
                color_tuple = self.ELEMENT_CLASSES.get(det["type"], {}).get(
                    "color", (255, 0, 0)
                )
                color = tuple(int(c) for c in color_tuple)

                # Draw rectangle
                draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

                # Draw label
                label = f"{det['type']} ({det['confidence']:.2f})"
                draw.text((x1, y1 - 10), label, fill=color)

            # Save annotated image
            image.save(str(output_path))
            logger.info(f"Annotated image saved: {output_path}")

        except Exception as e:
            logger.warning(f"Could not draw annotations: {e}")


# Backward compatibility alias
YOLOAnalysisService = HybridGUIAnalysisService

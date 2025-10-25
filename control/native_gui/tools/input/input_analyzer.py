
import logging; gui_logger = logging.getLogger(__name__)

"""
Input Analysis and Pattern Detection
Analyzes keyboard and mouse input patterns for productivity insights and automation.
"""

import time
import math
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, deque
from enum import Enum
import json


class PatternType(Enum):
    """Types of input patterns"""
    TYPING_RHYTHM = "typing_rhythm"
    MOUSE_GESTURE = "mouse_gesture"
    HOTKEY_SEQUENCE = "hotkey_sequence"
    REPETITIVE_ACTION = "repetitive_action"
    WORKFLOW_PATTERN = "workflow_pattern"
    IDLE_PERIOD = "idle_period"
    BURST_ACTIVITY = "burst_activity"


@dataclass
class Pattern:
    """Detected input pattern"""
    pattern_type: PatternType
    confidence: float
    timestamp: float
    duration: float
    data: Dict[str, Any]
    description: str


@dataclass
class AnalysisConfig:
    """Configuration for input analysis"""
    # Pattern detection thresholds
    typing_rhythm_window: float = 5.0  # seconds
    mouse_gesture_threshold: float = 100.0  # pixels
    repetition_threshold: int = 3
    idle_threshold: float = 30.0  # seconds
    burst_threshold: int = 10  # events per second
    
    # Analysis features
    enable_typing_analysis: bool = True
    enable_mouse_analysis: bool = True
    enable_workflow_analysis: bool = True
    enable_productivity_metrics: bool = True
    
    # Data retention
    max_patterns: int = 1000
    analysis_window: float = 3600.0  # 1 hour


class InputAnalyzer:
    """Analyzes input patterns and provides insights"""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        
        # Pattern storage
        self.detected_patterns: deque = deque(maxlen=self.config.max_patterns)
        self.pattern_history: Dict[PatternType, List[Pattern]] = defaultdict(list)
        
        # Input data buffers
        self.keyboard_events: deque = deque(maxlen=1000)
        self.mouse_events: deque = deque(maxlen=1000)
        self.combined_events: deque = deque(maxlen=2000)
        
        # Analysis state
        self.current_typing_session = None
        self.current_mouse_session = None
        self.last_activity_time = 0
        self.idle_periods = []
        
        # Metrics tracking
        self.productivity_metrics = {
            'typing_speed': 0,
            'mouse_efficiency': 0,
            'hotkey_usage': 0,
            'idle_time_ratio': 0,
            'activity_bursts': 0
        }
        
        # Pattern templates
        self.gesture_templates = self._initialize_gesture_templates()
        self.workflow_templates = self._initialize_workflow_templates()
        
    
    def add_keyboard_event(self, event_data: Dict):
        """Add keyboard event for analysis"""
        try:
            event_data['input_type'] = 'keyboard'
            self.keyboard_events.append(event_data)
            self.combined_events.append(event_data)
            self.last_activity_time = event_data.get('timestamp', time.time())
            
            # Trigger analysis
            if self.config.enable_typing_analysis:
                self._analyze_typing_patterns()
            
        except Exception as e:
            gui_logger.warn(f" Error adding keyboard event: {e}")
    
    def add_mouse_event(self, event_data: Dict):
        """Add mouse event for analysis"""
        try:
            event_data['input_type'] = 'mouse'
            self.mouse_events.append(event_data)
            self.combined_events.append(event_data)
            self.last_activity_time = event_data.get('timestamp', time.time())
            
            # Trigger analysis
            if self.config.enable_mouse_analysis:
                self._analyze_mouse_patterns()
            
        except Exception as e:
            gui_logger.warn(f" Error adding mouse event: {e}")
    
    def _analyze_typing_patterns(self):
        """Analyze typing patterns and rhythm"""
        try:
            if len(self.keyboard_events) < 10:
                return
            
            recent_events = list(self.keyboard_events)[-20:]  # Last 20 events
            
            # Calculate typing rhythm
            keystroke_intervals = []
            for i in range(1, len(recent_events)):
                if recent_events[i].get('event_type') == 'press':
                    interval = recent_events[i]['timestamp'] - recent_events[i-1]['timestamp']
                    if interval < 2.0:  # Reasonable typing interval
                        keystroke_intervals.append(interval)
            
            if len(keystroke_intervals) >= 5:
                avg_interval = statistics.mean(keystroke_intervals)
                rhythm_variance = statistics.variance(keystroke_intervals)
                
                # Detect consistent rhythm
                if rhythm_variance < 0.1 and len(keystroke_intervals) >= 10:
                    pattern = Pattern(
                        pattern_type=PatternType.TYPING_RHYTHM,
                        confidence=min(0.9, 1.0 - rhythm_variance),
                        timestamp=time.time(),
                        duration=keystroke_intervals[-1] - keystroke_intervals[0],
                        data={
                            'average_interval': avg_interval,
                            'variance': rhythm_variance,
                            'keystrokes': len(keystroke_intervals),
                            'wpm_estimate': 60 / (avg_interval * 5) if avg_interval > 0 else 0
                        },
                        description=f"Consistent typing rhythm detected (WPM: {60 / (avg_interval * 5):.1f})"
                    )
                    self._add_pattern(pattern)
            
            # Detect burst typing
            recent_presses = [e for e in recent_events if e.get('event_type') == 'press']
            if len(recent_presses) >= self.config.burst_threshold:
                time_span = recent_presses[-1]['timestamp'] - recent_presses[0]['timestamp']
                if time_span < 1.0:  # Burst within 1 second
                    pattern = Pattern(
                        pattern_type=PatternType.BURST_ACTIVITY,
                        confidence=0.8,
                        timestamp=time.time(),
                        duration=time_span,
                        data={
                            'event_count': len(recent_presses),
                            'rate': len(recent_presses) / time_span,
                            'type': 'typing_burst'
                        },
                        description=f"Typing burst: {len(recent_presses)} keys in {time_span:.1f}s"
                    )
                    self._add_pattern(pattern)
                    
        except Exception as e:
            gui_logger.warn(f" Typing analysis error: {e}")
    
    def _analyze_mouse_patterns(self):
        """Analyze mouse movement patterns and gestures"""
        try:
            if len(self.mouse_events) < 5:
                return
            
            recent_events = list(self.mouse_events)[-10:]  # Last 10 events
            move_events = [e for e in recent_events if e.get('event_type') == 'move']
            
            if len(move_events) >= 3:
                # Calculate movement path
                path = [(e['x'], e['y']) for e in move_events if e.get('x') is not None]
                
                if len(path) >= 3:
                    # Detect circular gestures
                    if self._is_circular_gesture(path):
                        pattern = Pattern(
                            pattern_type=PatternType.MOUSE_GESTURE,
                            confidence=0.7,
                            timestamp=time.time(),
                            duration=move_events[-1]['timestamp'] - move_events[0]['timestamp'],
                            data={
                                'gesture_type': 'circular',
                                'path_length': len(path),
                                'radius': self._calculate_gesture_radius(path)
                            },
                            description="Circular mouse gesture detected"
                        )
                        self._add_pattern(pattern)
                    
                    # Detect straight line gestures
                    elif self._is_straight_line_gesture(path):
                        pattern = Pattern(
                            pattern_type=PatternType.MOUSE_GESTURE,
                            confidence=0.6,
                            timestamp=time.time(),
                            duration=move_events[-1]['timestamp'] - move_events[0]['timestamp'],
                            data={
                                'gesture_type': 'line',
                                'path_length': len(path),
                                'distance': self._calculate_path_distance(path)
                            },
                            description="Linear mouse gesture detected"
                        )
                        self._add_pattern(pattern)
            
            # Detect repetitive clicking
            click_events = [e for e in recent_events if e.get('event_type') == 'click' and e.get('pressed')]
            if len(click_events) >= self.config.repetition_threshold:
                # Check if clicks are in similar positions
                positions = [(e['x'], e['y']) for e in click_events if e.get('x') is not None]
                if self._are_positions_clustered(positions):
                    pattern = Pattern(
                        pattern_type=PatternType.REPETITIVE_ACTION,
                        confidence=0.8,
                        timestamp=time.time(),
                        duration=click_events[-1]['timestamp'] - click_events[0]['timestamp'],
                        data={
                            'action_type': 'repetitive_clicking',
                            'click_count': len(click_events),
                            'cluster_center': self._calculate_cluster_center(positions)
                        },
                        description=f"Repetitive clicking detected: {len(click_events)} clicks"
                    )
                    self._add_pattern(pattern)
                    
        except Exception as e:
            gui_logger.warn(f" Mouse analysis error: {e}")
    
    def _is_circular_gesture(self, path: List[Tuple[int, int]]) -> bool:
        """Check if path represents a circular gesture"""
        try:
            if len(path) < 5:
                return False
            
            # Calculate center point
            center_x = sum(p[0] for p in path) / len(path)
            center_y = sum(p[1] for p in path) / len(path)
            
            # Calculate distances from center
            distances = [math.sqrt((p[0] - center_x)**2 + (p[1] - center_y)**2) for p in path]
            
            # Check if distances are relatively consistent (circular)
            if len(distances) > 0:
                avg_distance = statistics.mean(distances)
                variance = statistics.variance(distances) if len(distances) > 1 else 0
                
                # Low variance indicates circular motion
                return variance < (avg_distance * 0.3)**2 and avg_distance > 20
            
            return False
            
        except Exception:
            return False
    
    def _is_straight_line_gesture(self, path: List[Tuple[int, int]]) -> bool:
        """Check if path represents a straight line gesture"""
        try:
            if len(path) < 3:
                return False
            
            # Calculate total distance vs direct distance
            total_distance = self._calculate_path_distance(path)
            direct_distance = math.sqrt(
                (path[-1][0] - path[0][0])**2 + (path[-1][1] - path[0][1])**2
            )
            
            # If path is mostly straight, ratio should be close to 1
            if direct_distance > 50:  # Minimum distance for gesture
                ratio = direct_distance / total_distance if total_distance > 0 else 0
                return ratio > 0.8
            
            return False
            
        except Exception:
            return False
    
    def _calculate_path_distance(self, path: List[Tuple[int, int]]) -> float:
        """Calculate total distance of path"""
        total = 0
        for i in range(1, len(path)):
            total += math.sqrt(
                (path[i][0] - path[i-1][0])**2 + (path[i][1] - path[i-1][1])**2
            )
        return total
    
    def _calculate_gesture_radius(self, path: List[Tuple[int, int]]) -> float:
        """Calculate average radius of circular gesture"""
        center_x = sum(p[0] for p in path) / len(path)
        center_y = sum(p[1] for p in path) / len(path)
        
        distances = [math.sqrt((p[0] - center_x)**2 + (p[1] - center_y)**2) for p in path]
        return statistics.mean(distances) if distances else 0
    
    def _are_positions_clustered(self, positions: List[Tuple[int, int]], threshold: float = 50) -> bool:
        """Check if positions are clustered together"""
        if len(positions) < 2:
            return False
        
        center = self._calculate_cluster_center(positions)
        
        # Check if all positions are within threshold of center
        for pos in positions:
            distance = math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2)
            if distance > threshold:
                return False
        
        return True
    
    def _calculate_cluster_center(self, positions: List[Tuple[int, int]]) -> Tuple[float, float]:
        """Calculate center of position cluster"""
        if not positions:
            return (0, 0)
        
        center_x = sum(p[0] for p in positions) / len(positions)
        center_y = sum(p[1] for p in positions) / len(positions)
        return (center_x, center_y)
    
    def _add_pattern(self, pattern: Pattern):
        """Add detected pattern to storage"""
        self.detected_patterns.append(pattern)
        self.pattern_history[pattern.pattern_type].append(pattern)
        
        # Keep only recent patterns per type
        if len(self.pattern_history[pattern.pattern_type]) > 100:
            self.pattern_history[pattern.pattern_type] = self.pattern_history[pattern.pattern_type][-100:]
        
    
    def detect_idle_periods(self):
        """Detect periods of user inactivity"""
        current_time = time.time()
        
        if self.last_activity_time > 0:
            idle_duration = current_time - self.last_activity_time
            
            if idle_duration > self.config.idle_threshold:
                pattern = Pattern(
                    pattern_type=PatternType.IDLE_PERIOD,
                    confidence=1.0,
                    timestamp=self.last_activity_time,
                    duration=idle_duration,
                    data={
                        'idle_duration': idle_duration,
                        'start_time': self.last_activity_time,
                        'end_time': current_time
                    },
                    description=f"Idle period: {idle_duration:.1f} seconds"
                )
                self._add_pattern(pattern)
                self.idle_periods.append(pattern)
    
    def get_productivity_insights(self) -> Dict[str, Any]:
        """Generate productivity insights from patterns"""
        insights = {
            'typing_efficiency': self._calculate_typing_efficiency(),
            'mouse_efficiency': self._calculate_mouse_efficiency(),
            'pattern_summary': self._get_pattern_summary(),
            'recommendations': self._generate_recommendations(),
            'activity_timeline': self._generate_activity_timeline()
        }
        
        return insights
    
    def _calculate_typing_efficiency(self) -> Dict[str, float]:
        """Calculate typing efficiency metrics"""
        typing_patterns = self.pattern_history[PatternType.TYPING_RHYTHM]
        
        if not typing_patterns:
            return {'wpm': 0, 'consistency': 0, 'burst_frequency': 0}
        
        recent_patterns = [p for p in typing_patterns if time.time() - p.timestamp < 3600]
        
        if recent_patterns:
            avg_wpm = statistics.mean([p.data.get('wpm_estimate', 0) for p in recent_patterns])
            consistency = 1.0 - statistics.mean([p.data.get('variance', 1) for p in recent_patterns])
        else:
            avg_wpm = 0
            consistency = 0
        
        burst_patterns = self.pattern_history[PatternType.BURST_ACTIVITY]
        burst_frequency = len([p for p in burst_patterns if time.time() - p.timestamp < 3600])
        
        return {
            'wpm': avg_wpm,
            'consistency': max(0, consistency),
            'burst_frequency': burst_frequency
        }
    
    def _calculate_mouse_efficiency(self) -> Dict[str, float]:
        """Calculate mouse efficiency metrics"""
        gesture_patterns = self.pattern_history[PatternType.MOUSE_GESTURE]
        repetitive_patterns = self.pattern_history[PatternType.REPETITIVE_ACTION]
        
        recent_gestures = len([p for p in gesture_patterns if time.time() - p.timestamp < 3600])
        recent_repetitive = len([p for p in repetitive_patterns if time.time() - p.timestamp < 3600])
        
        return {
            'gesture_usage': recent_gestures,
            'repetitive_actions': recent_repetitive,
            'efficiency_score': max(0, 1.0 - (recent_repetitive * 0.1))
        }
    
    def _get_pattern_summary(self) -> Dict[str, int]:
        """Get summary of detected patterns"""
        summary = {}
        for pattern_type in PatternType:
            count = len([p for p in self.pattern_history[pattern_type] 
                        if time.time() - p.timestamp < 3600])
            summary[pattern_type.value] = count
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate productivity recommendations"""
        recommendations = []
        
        # Analyze typing patterns
        typing_efficiency = self._calculate_typing_efficiency()
        if typing_efficiency['consistency'] < 0.5:
            recommendations.append("Consider practicing typing to improve consistency")
        
        if typing_efficiency['burst_frequency'] > 10:
            recommendations.append("Try to maintain steady typing pace instead of bursts")
        
        # Analyze mouse patterns
        mouse_efficiency = self._calculate_mouse_efficiency()
        if mouse_efficiency['repetitive_actions'] > 5:
            recommendations.append("Consider using keyboard shortcuts to reduce repetitive clicking")
        
        # Analyze idle time
        idle_patterns = self.pattern_history[PatternType.IDLE_PERIOD]
        recent_idle = [p for p in idle_patterns if time.time() - p.timestamp < 3600]
        if len(recent_idle) > 3:
            recommendations.append("Frequent breaks detected - consider time management techniques")
        
        return recommendations
    
    def _generate_activity_timeline(self) -> List[Dict]:
        """Generate activity timeline"""
        timeline = []
        
        # Combine all recent patterns
        all_patterns = []
        for patterns in self.pattern_history.values():
            all_patterns.extend([p for p in patterns if time.time() - p.timestamp < 3600])
        
        # Sort by timestamp
        all_patterns.sort(key=lambda p: p.timestamp)
        
        for pattern in all_patterns[-20:]:  # Last 20 patterns
            timeline.append({
                'timestamp': pattern.timestamp,
                'type': pattern.pattern_type.value,
                'description': pattern.description,
                'confidence': pattern.confidence
            })
        
        return timeline
    
    def _initialize_gesture_templates(self) -> Dict:
        """Initialize gesture recognition templates"""
        return {
            'circle': {'min_points': 8, 'variance_threshold': 0.3},
            'line': {'min_distance': 50, 'straightness_threshold': 0.8},
            'zigzag': {'direction_changes': 3, 'min_distance': 30}
        }
    
    def _initialize_workflow_templates(self) -> Dict:
        """Initialize workflow pattern templates"""
        return {
            'copy_paste': ['ctrl+c', 'ctrl+v'],
            'save_sequence': ['ctrl+s'],
            'undo_redo': ['ctrl+z', 'ctrl+y']
        }
    
    def export_analysis(self, filename: str):
        """Export analysis results to file"""
        try:
            export_data = {
                'patterns': [
                    {
                        'type': p.pattern_type.value,
                        'confidence': p.confidence,
                        'timestamp': p.timestamp,
                        'duration': p.duration,
                        'data': p.data,
                        'description': p.description
                    }
                    for p in self.detected_patterns
                ],
                'insights': self.get_productivity_insights(),
                'export_timestamp': time.time()
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            
        except Exception as e:
            gui_logger.error(f" Failed to export analysis: {e}")


# Test function
def test_input_analyzer():
    """Test input analyzer functionality"""
    
    try:
        analyzer = InputAnalyzer()
        
        # Simulate keyboard events
        for i in range(10):
            event = {
                'key': 'a',
                'event_type': 'press',
                'timestamp': time.time() + i * 0.1,
                'char': 'a'
            }
            analyzer.add_keyboard_event(event)
            time.sleep(0.01)
        
        # Simulate mouse events
        for i in range(5):
            event = {
                'event_type': 'move',
                'x': 100 + i * 10,
                'y': 100 + i * 10,
                'timestamp': time.time() + i * 0.1
            }
            analyzer.add_mouse_event(event)
        
        # Get insights
        insights = analyzer.get_productivity_insights()
        
        gui_logger.info(" Input analyzer test completed", {"status": "success"})
        
    except Exception as e:
        gui_logger.error(f" Input analyzer test failed: {e}")


if __name__ == "__main__":
    test_input_analyzer()

#!/usr/bin/env python3

"""
@llm-type service
@llm-legend Build performance monitoring and metrics collection system
@llm-key Provides comprehensive build performance tracking, caching analytics, and optimization insights
@llm-map Performance monitoring system that tracks build metrics and provides optimization recommendations
@llm-axiom Performance monitoring must be lightweight and provide actionable insights for developers
@llm-contract Returns structured performance data and optimization recommendations
@llm-token build-monitoring: Performance tracking and analytics for build system

Build Performance Monitoring System

Provides comprehensive monitoring and analytics for the enhanced build system:
- Build time tracking and analysis
- Cache performance metrics
- Resource utilization monitoring
- Performance trend analysis
- Optimization recommendations

Author: Unhinged Team
Version: 2.0.0
Date: 2025-10-19
"""

import json
import time
import psutil
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class BuildMetrics:
    """Metrics for a single build operation"""
    target: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    cache_hit: bool
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_io_mb: float
    parallel_workers: int
    artifacts_count: int
    artifacts_size_mb: float
    error_message: Optional[str] = None

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    total_entries: int
    total_size_mb: float
    hit_rate: float
    miss_rate: float
    evictions: int
    storage_efficiency: float

@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_cores: int
    cpu_usage_percent: float
    memory_total_gb: float
    memory_available_gb: float
    disk_total_gb: float
    disk_free_gb: float
    load_average: List[float]

@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    period_start: str
    period_end: str
    total_builds: int
    successful_builds: int
    failed_builds: int
    average_build_time: float
    fastest_build_time: float
    slowest_build_time: float
    cache_metrics: CacheMetrics
    system_metrics: SystemMetrics
    target_performance: Dict[str, Dict[str, float]]
    optimization_recommendations: List[str]

class BuildPerformanceMonitor:
    """Monitor and analyze build performance"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.metrics_dir = project_root / ".build-metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        self.metrics_file = self.metrics_dir / "build_metrics.jsonl"
        self.cache_dir = project_root / ".build-cache"
        
    def start_build_monitoring(self, target: str) -> Dict[str, Any]:
        """Start monitoring a build operation"""
        start_time = time.time()
        
        # Capture initial system state
        initial_state = {
            'target': target,
            'start_time': start_time,
            'start_cpu': psutil.cpu_percent(interval=1),
            'start_memory': psutil.virtual_memory().used / (1024**2),
            'start_disk_io': self._get_disk_io()
        }
        
        return initial_state
    
    def end_build_monitoring(self, initial_state: Dict[str, Any], success: bool, 
                           cache_hit: bool = False, artifacts: List[Any] = None,
                           error_message: Optional[str] = None) -> BuildMetrics:
        """End monitoring and record metrics"""
        end_time = time.time()
        duration = end_time - initial_state['start_time']
        
        # Calculate resource usage
        end_cpu = psutil.cpu_percent(interval=1)
        end_memory = psutil.virtual_memory().used / (1024**2)
        end_disk_io = self._get_disk_io()
        
        # Calculate artifacts metrics
        artifacts = artifacts or []
        artifacts_count = len(artifacts)
        artifacts_size_mb = sum(getattr(a, 'size', 0) for a in artifacts) / (1024**2)
        
        # Create metrics record
        metrics = BuildMetrics(
            target=initial_state['target'],
            start_time=initial_state['start_time'],
            end_time=end_time,
            duration=duration,
            success=success,
            cache_hit=cache_hit,
            cpu_usage_percent=(initial_state['start_cpu'] + end_cpu) / 2,
            memory_usage_mb=end_memory - initial_state['start_memory'],
            disk_io_mb=end_disk_io - initial_state['start_disk_io'],
            parallel_workers=psutil.cpu_count(),
            artifacts_count=artifacts_count,
            artifacts_size_mb=artifacts_size_mb,
            error_message=error_message
        )
        
        # Store metrics
        self._store_metrics(metrics)
        
        return metrics
    
    def get_cache_metrics(self) -> CacheMetrics:
        """Get cache performance metrics"""
        if not self.cache_dir.exists():
            return CacheMetrics(0, 0.0, 0.0, 100.0, 0, 0.0)
        
        # Count cache entries and calculate size
        cache_files = list(self.cache_dir.glob('*'))
        total_entries = len(cache_files)
        total_size_bytes = sum(f.stat().st_size for f in cache_files if f.is_file())
        total_size_mb = total_size_bytes / (1024**2)
        
        # Calculate hit/miss rates from recent builds
        recent_metrics = self._get_recent_metrics(hours=24)
        total_recent = len(recent_metrics)
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        
        hit_rate = (cache_hits / total_recent * 100) if total_recent > 0 else 0.0
        miss_rate = 100.0 - hit_rate
        
        # Storage efficiency (simplified)
        storage_efficiency = min(100.0, (total_size_mb / 1000) * 100) if total_size_mb > 0 else 0.0
        
        return CacheMetrics(
            total_entries=total_entries,
            total_size_mb=total_size_mb,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            evictions=0,  # Would need to track this separately
            storage_efficiency=storage_efficiency
        )
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            # getloadavg not available on Windows
            load_avg = [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            cpu_cores=psutil.cpu_count(),
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            memory_total_gb=memory.total / (1024**3),
            memory_available_gb=memory.available / (1024**3),
            disk_total_gb=disk.total / (1024**3),
            disk_free_gb=disk.free / (1024**3),
            load_average=load_avg
        )
    
    def generate_performance_report(self, hours: int = 24) -> PerformanceReport:
        """Generate comprehensive performance report"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get metrics for the period
        metrics = self._get_metrics_for_period(start_time, end_time)
        
        if not metrics:
            # Return empty report if no data
            return PerformanceReport(
                period_start=start_time.isoformat(),
                period_end=end_time.isoformat(),
                total_builds=0,
                successful_builds=0,
                failed_builds=0,
                average_build_time=0.0,
                fastest_build_time=0.0,
                slowest_build_time=0.0,
                cache_metrics=self.get_cache_metrics(),
                system_metrics=self.get_system_metrics(),
                target_performance={},
                optimization_recommendations=[]
            )
        
        # Calculate build statistics
        successful_builds = sum(1 for m in metrics if m.success)
        failed_builds = len(metrics) - successful_builds
        durations = [m.duration for m in metrics]
        
        # Calculate target-specific performance
        target_performance = defaultdict(list)
        for m in metrics:
            target_performance[m.target].append(m.duration)
        
        target_stats = {}
        for target, times in target_performance.items():
            target_stats[target] = {
                'average': statistics.mean(times),
                'min': min(times),
                'max': max(times),
                'count': len(times)
            }
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(metrics)
        
        return PerformanceReport(
            period_start=start_time.isoformat(),
            period_end=end_time.isoformat(),
            total_builds=len(metrics),
            successful_builds=successful_builds,
            failed_builds=failed_builds,
            average_build_time=statistics.mean(durations),
            fastest_build_time=min(durations),
            slowest_build_time=max(durations),
            cache_metrics=self.get_cache_metrics(),
            system_metrics=self.get_system_metrics(),
            target_performance=target_stats,
            optimization_recommendations=recommendations
        )
    
    def _store_metrics(self, metrics: BuildMetrics):
        """Store metrics to file"""
        try:
            with open(self.metrics_file, 'a') as f:
                json.dump(asdict(metrics), f)
                f.write('\n')
        except IOError as e:
            print(f"Warning: Failed to store metrics: {e}")
    
    def _get_recent_metrics(self, hours: int = 24) -> List[BuildMetrics]:
        """Get metrics from recent builds"""
        cutoff_time = time.time() - (hours * 3600)
        metrics = []
        
        if not self.metrics_file.exists():
            return metrics
        
        try:
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data['start_time'] >= cutoff_time:
                        metrics.append(BuildMetrics(**data))
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to read metrics: {e}")
        
        return metrics
    
    def _get_metrics_for_period(self, start_time: datetime, end_time: datetime) -> List[BuildMetrics]:
        """Get metrics for a specific time period"""
        start_timestamp = start_time.timestamp()
        end_timestamp = end_time.timestamp()
        metrics = []
        
        if not self.metrics_file.exists():
            return metrics
        
        try:
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if start_timestamp <= data['start_time'] <= end_timestamp:
                        metrics.append(BuildMetrics(**data))
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to read metrics: {e}")
        
        return metrics
    
    def _get_disk_io(self) -> float:
        """Get current disk I/O in MB"""
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                return (disk_io.read_bytes + disk_io.write_bytes) / (1024**2)
        except AttributeError:
            pass
        return 0.0
    
    def _generate_optimization_recommendations(self, metrics: List[BuildMetrics]) -> List[str]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        if not metrics:
            return recommendations
        
        # Analyze cache performance
        cache_hits = sum(1 for m in metrics if m.cache_hit)
        cache_hit_rate = cache_hits / len(metrics)
        
        if cache_hit_rate < 0.5:
            recommendations.append(
                f"Low cache hit rate ({cache_hit_rate:.1%}). Consider using more aggressive caching strategies."
            )
        
        # Analyze build times
        slow_builds = [m for m in metrics if m.duration > 300]  # 5 minutes
        if slow_builds:
            recommendations.append(
                f"{len(slow_builds)} builds took longer than 5 minutes. Consider using parallel builds or incremental compilation."
            )
        
        # Analyze memory usage
        high_memory_builds = [m for m in metrics if m.memory_usage_mb > 2000]  # 2GB
        if high_memory_builds:
            recommendations.append(
                f"{len(high_memory_builds)} builds used more than 2GB memory. Consider optimizing memory usage or increasing system memory."
            )
        
        # Analyze failure rate
        failed_builds = [m for m in metrics if not m.success]
        failure_rate = len(failed_builds) / len(metrics)
        if failure_rate > 0.1:  # 10%
            recommendations.append(
                f"High failure rate ({failure_rate:.1%}). Review common error patterns and improve build reliability."
            )
        
        # Target-specific recommendations
        target_times = defaultdict(list)
        for m in metrics:
            target_times[m.target].append(m.duration)
        
        for target, times in target_times.items():
            avg_time = statistics.mean(times)
            if avg_time > 180:  # 3 minutes
                recommendations.append(
                    f"Target '{target}' averages {avg_time:.1f}s. Consider optimizing this specific target."
                )
        
        if not recommendations:
            recommendations.append("Build performance looks good! No specific optimizations needed.")
        
        return recommendations

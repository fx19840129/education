#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能指标收集器
"""

import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum

from ..errors.exceptions import EducationSystemError


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricData:
    """指标数据"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class PerformanceStats:
    """性能统计"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0


class MetricsCollector:
    """指标收集器"""
    _instance = None
    _initialized = False
    
    def __new__(cls, max_history: int = 1000):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, max_history: int = 1000):
        if self._initialized:
            return
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, list] = defaultdict(list)
        self.lock = threading.RLock()
        
        # 性能统计
        self.performance_stats = PerformanceStats()
        self.start_time = time.time()
        self._initialized = True
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """增加计数器"""
        with self.lock:
            key = self._build_key(name, tags)
            self.counters[key] += value
            self._record_metric(MetricData(
                name=name,
                value=self.counters[key],
                timestamp=datetime.now(),
                tags=tags or {},
                metric_type=MetricType.COUNTER
            ))
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """设置仪表值"""
        with self.lock:
            key = self._build_key(name, tags)
            self.gauges[key] = value
            self._record_metric(MetricData(
                name=name,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {},
                metric_type=MetricType.GAUGE
            ))
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """记录计时器"""
        with self.lock:
            key = self._build_key(name, tags)
            self.timers[key].append(duration)
            # 保持最近100个记录
            if len(self.timers[key]) > 100:
                self.timers[key] = self.timers[key][-100:]
            
            self._record_metric(MetricData(
                name=name,
                value=duration,
                timestamp=datetime.now(),
                tags=tags or {},
                metric_type=MetricType.TIMER
            ))
    
    def time_function(self, name: str, tags: Dict[str, str] = None):
        """函数计时装饰器"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.increment_counter(f"{name}.success", tags=tags)
                    return result
                except Exception as e:
                    self.increment_counter(f"{name}.error", tags=tags)
                    raise
                finally:
                    duration = time.time() - start_time
                    self.record_timer(name, duration, tags)
            return wrapper
        return decorator
    
    def record_ai_call(self, provider: str, model: str, duration: float, 
                      success: bool, tokens: int = 0, cost: float = 0.0):
        """记录AI调用"""
        tags = {"provider": provider, "model": model}
        
        self.increment_counter("ai_calls.total", tags=tags)
        if success:
            self.increment_counter("ai_calls.success", tags=tags)
        else:
            self.increment_counter("ai_calls.failed", tags=tags)
        
        self.record_timer("ai_calls.duration", duration, tags)
        
        if tokens > 0:
            self.increment_counter("ai_calls.tokens", value=tokens, tags=tags)
        
        if cost > 0:
            self.increment_counter("ai_calls.cost", value=int(cost * 1000), tags=tags)  # 转换为厘
    
    def record_plan_generation(self, plan_type: str, duration: float, 
                             word_count: int, exercise_count: int, success: bool):
        """记录学习计划生成"""
        tags = {"plan_type": plan_type}
        
        self.increment_counter("plan_generation.total", tags=tags)
        if success:
            self.increment_counter("plan_generation.success", tags=tags)
        else:
            self.increment_counter("plan_generation.failed", tags=tags)
        
        self.record_timer("plan_generation.duration", duration, tags)
        self.increment_counter("plan_generation.words", value=word_count, tags=tags)
        self.increment_counter("plan_generation.exercises", value=exercise_count, tags=tags)
    
    def record_content_generation(self, content_type: str, duration: float, 
                                item_count: int, success: bool):
        """记录内容生成"""
        tags = {"content_type": content_type}
        
        self.increment_counter("content_generation.total", tags=tags)
        if success:
            self.increment_counter("content_generation.success", tags=tags)
        else:
            self.increment_counter("content_generation.failed", tags=tags)
        
        self.record_timer("content_generation.duration", duration, tags)
        self.increment_counter("content_generation.items", value=item_count, tags=tags)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self.lock:
            uptime = time.time() - self.start_time
            
            # 计算性能统计
            total_requests = sum(self.counters.values())
            successful_requests = sum(
                v for k, v in self.counters.items() 
                if k.endswith('.success')
            )
            failed_requests = sum(
                v for k, v in self.counters.items() 
                if k.endswith('.error') or k.endswith('.failed')
            )
            
            # 计算平均响应时间
            all_timers = []
            for timer_values in self.timers.values():
                all_timers.extend(timer_values)
            
            avg_response_time = sum(all_timers) / len(all_timers) if all_timers else 0.0
            min_response_time = min(all_timers) if all_timers else 0.0
            max_response_time = max(all_timers) if all_timers else 0.0
            
            # 计算每秒请求数
            requests_per_second = total_requests / uptime if uptime > 0 else 0.0
            
            # 计算错误率
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "uptime_seconds": uptime,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "average_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "requests_per_second": requests_per_second,
                "error_rate_percent": error_rate,
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "timer_stats": {
                    name: {
                        "count": len(values),
                        "avg": sum(values) / len(values) if values else 0,
                        "min": min(values) if values else 0,
                        "max": max(values) if values else 0
                    }
                    for name, values in self.timers.items()
                }
            }
    
    def get_performance_stats(self) -> PerformanceStats:
        """获取性能统计"""
        summary = self.get_metrics_summary()
        
        self.performance_stats.total_requests = summary["total_requests"]
        self.performance_stats.successful_requests = summary["successful_requests"]
        self.performance_stats.failed_requests = summary["failed_requests"]
        self.performance_stats.average_response_time = summary["average_response_time"]
        self.performance_stats.min_response_time = summary["min_response_time"]
        self.performance_stats.max_response_time = summary["max_response_time"]
        self.performance_stats.requests_per_second = summary["requests_per_second"]
        self.performance_stats.error_rate = summary["error_rate_percent"]
        
        return self.performance_stats
    
    def reset_metrics(self):
        """重置指标"""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.timers.clear()
            self.performance_stats = PerformanceStats()
            self.start_time = time.time()
    
    def _build_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """构建指标键"""
        if not tags:
            return name
        
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def _record_metric(self, metric: MetricData):
        """记录指标"""
        key = self._build_key(metric.name, metric.tags)
        self.metrics[key].append(metric)


# 全局指标收集器实例
metrics_collector = MetricsCollector()

def get_metrics() -> MetricsCollector:
    """获取指标收集器实例"""
    return metrics_collector

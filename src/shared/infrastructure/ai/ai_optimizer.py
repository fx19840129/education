#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI调用优化器
优化AI调用性能，包括重试机制、熔断器、负载均衡等
"""

import time
import random
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import threading
from collections import deque

from ..monitoring.metrics import get_metrics
from ..errors.exceptions import AIGenerationError, NetworkError


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3
    timeout: float = 30.0


@dataclass
class LoadBalancerConfig:
    """负载均衡配置"""
    strategy: str = "round_robin"  # round_robin, random, weighted
    health_check_interval: float = 30.0
    max_failures: int = 3


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过熔断器调用函数"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise AIGenerationError("熔断器开启，服务不可用")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _on_success(self):
        """成功回调（调用者必须已持有锁）"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        """失败回调（调用者必须已持有锁）"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN


class RetryManager:
    """重试管理器"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """带重试的执行"""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.config.max_retries:
                    break
                
                # 计算延迟时间
                delay = self._calculate_delay(attempt)
                time.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            # 添加随机抖动
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.providers: List[Dict[str, Any]] = []
        self.current_index = 0
        self.health_status: Dict[str, bool] = {}
        self.failure_counts: Dict[str, int] = {}
        self.last_health_check = 0
        self.lock = threading.Lock()
    
    def add_provider(self, name: str, weight: int = 1, health_check: Callable = None):
        """添加提供商"""
        with self.lock:
            provider = {
                "name": name,
                "weight": weight,
                "health_check": health_check,
                "enabled": True
            }
            self.providers.append(provider)
            self.health_status[name] = True
            self.failure_counts[name] = 0
    
    def remove_provider(self, name: str):
        """移除提供商"""
        with self.lock:
            self.providers = [p for p in self.providers if p["name"] != name]
            self.health_status.pop(name, None)
            self.failure_counts.pop(name, None)
    
    def get_provider(self) -> Optional[str]:
        """获取可用的提供商"""
        with self.lock:
            # 健康检查
            self._health_check()
            
            # 过滤可用的提供商
            available_providers = [
                p for p in self.providers 
                if p["enabled"] and self.health_status.get(p["name"], True)
            ]
            
            if not available_providers:
                return None
            
            # 选择提供商
            if self.config.strategy == "round_robin":
                provider = available_providers[self.current_index % len(available_providers)]
                self.current_index += 1
            elif self.config.strategy == "random":
                provider = random.choice(available_providers)
            elif self.config.strategy == "weighted":
                provider = self._weighted_selection(available_providers)
            else:
                provider = available_providers[0]
            
            return provider["name"]
    
    def _weighted_selection(self, providers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """加权选择"""
        total_weight = sum(p["weight"] for p in providers)
        if total_weight == 0:
            return providers[0]
        
        random_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for provider in providers:
            current_weight += provider["weight"]
            if random_value <= current_weight:
                return provider
        
        return providers[-1]
    
    def _health_check(self):
        """健康检查"""
        current_time = time.time()
        if current_time - self.last_health_check < self.config.health_check_interval:
            return
        
        for provider in self.providers:
            if provider["health_check"]:
                try:
                    # 添加超时保护
                    import signal
                    def timeout_handler(signum, frame):
                        raise TimeoutError("健康检查超时")
                    
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(1)  # 1秒超时
                    
                    is_healthy = provider["health_check"]()
                    self.health_status[provider["name"]] = is_healthy
                    
                    signal.alarm(0)  # 取消超时
                except Exception as e:
                    print(f"健康检查失败 {provider['name']}: {e}")
                    self.health_status[provider["name"]] = False
        
        self.last_health_check = current_time
    
    def report_failure(self, provider_name: str):
        """报告失败"""
        with self.lock:
            self.failure_counts[provider_name] = self.failure_counts.get(provider_name, 0) + 1
            
            if self.failure_counts[provider_name] >= self.config.max_failures:
                self.health_status[provider_name] = False
    
    def report_success(self, provider_name: str):
        """报告成功"""
        with self.lock:
            self.failure_counts[provider_name] = 0
            self.health_status[provider_name] = True


class AIOptimizer:
    """AI调用优化器"""
    
    def __init__(self, retry_config: RetryConfig = None, 
                 circuit_config: CircuitBreakerConfig = None,
                 load_balancer_config: LoadBalancerConfig = None):
        self.retry_manager = RetryManager(retry_config or RetryConfig())
        self.circuit_breaker = CircuitBreaker(circuit_config or CircuitBreakerConfig())
        self.load_balancer = LoadBalancer(load_balancer_config or LoadBalancerConfig())
        self.metrics = get_metrics()
        
        # 性能统计
        self.call_times = deque(maxlen=1000)
        self.success_rates = deque(maxlen=100)
    
    def add_provider(self, name: str, weight: int = 1, health_check: Callable = None):
        """添加AI提供商"""
        self.load_balancer.add_provider(name, weight, health_check)
    
    def optimize_call(self, func: Callable, *args, **kwargs) -> Any:
        """优化AI调用"""
        start_time = time.time()
        
        try:
            # 选择提供商
            provider = self.load_balancer.get_provider()
            if not provider:
                raise AIGenerationError("没有可用的AI提供商")
            
            # 通过熔断器调用
            result = self.circuit_breaker.call(
                self.retry_manager.execute_with_retry,
                func, *args, **kwargs
            )
            
            # 记录成功
            self.load_balancer.report_success(provider)
            self._record_success(start_time)
            
            return result
            
        except Exception as e:
            # 记录失败
            if 'provider' in locals():
                self.load_balancer.report_failure(provider)
            self._record_failure(start_time, e)
            raise e
    
    def _record_success(self, start_time: float):
        """记录成功调用"""
        duration = time.time() - start_time
        self.call_times.append(duration)
        self.success_rates.append(1)
        
        # 记录指标
        self.metrics.increment_counter("ai_optimizer.successful_calls")
        self.metrics.record_timer("ai_optimizer.call_duration", duration)
    
    def _record_failure(self, start_time: float, error: Exception):
        """记录失败调用"""
        duration = time.time() - start_time
        self.call_times.append(duration)
        self.success_rates.append(0)
        
        # 记录指标
        self.metrics.increment_counter("ai_optimizer.failed_calls")
        self.metrics.record_timer("ai_optimizer.failed_call_duration", duration)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if not self.call_times:
            return {
                "average_call_time": 0.0,
                "success_rate": 0.0,
                "total_calls": 0,
                "circuit_breaker_state": self.circuit_breaker.state.value
            }
        
        return {
            "average_call_time": sum(self.call_times) / len(self.call_times),
            "success_rate": sum(self.success_rates) / len(self.success_rates),
            "total_calls": len(self.call_times),
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "available_providers": len([
                p for p in self.load_balancer.providers 
                if self.load_balancer.health_status.get(p["name"], True)
            ])
        }


# 全局AI优化器实例
_ai_optimizer = None

def get_ai_optimizer() -> AIOptimizer:
    """获取AI优化器实例"""
    global _ai_optimizer
    if _ai_optimizer is None:
        _ai_optimizer = AIOptimizer()
    return _ai_optimizer

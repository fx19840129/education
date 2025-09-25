#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化器
优化API调用频率、并发处理和响应时间
"""

import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import os
from collections import defaultdict, deque

class OptimizationLevel(Enum):
    """优化级别"""
    BASIC = "basic"           # 基础优化
    BALANCED = "balanced"     # 平衡优化
    AGGRESSIVE = "aggressive" # 激进优化

class RequestPriority(Enum):
    """请求优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class PerformanceMetrics:
    """性能指标"""
    avg_response_time: float
    cache_hit_rate: float
    api_call_frequency: float
    concurrent_requests: int
    error_rate: float
    throughput: float
    cpu_usage: float
    memory_usage: float

@dataclass
class OptimizationConfig:
    """优化配置"""
    max_concurrent_requests: int = 10
    request_timeout: float = 30.0
    cache_ttl: int = 3600
    batch_size: int = 5
    rate_limit_per_minute: int = 60
    retry_attempts: int = 3
    connection_pool_size: int = 20

@dataclass
class RequestTask:
    """请求任务"""
    task_id: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: RequestPriority
    created_at: datetime
    timeout: float = 30.0

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        
        # 性能监控
        self.metrics_history = deque(maxlen=1000)
        self.request_times = deque(maxlen=100)
        self.error_count = 0
        self.total_requests = 0
        
        # 并发控制
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_requests)
        self.active_requests = 0
        self.request_lock = threading.Lock()
        
        # 请求队列
        self.task_queue = asyncio.PriorityQueue()
        self.processing_tasks = {}
        
        # 速率限制
        self.rate_limiter = self._create_rate_limiter()
        
        # 缓存优化
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0
        }
        
        # 批处理
        self.batch_queue = defaultdict(list)
        self.batch_timer = None
        
        # 自动优化
        self.optimization_enabled = True
        self.last_optimization = datetime.now()
        
        print(f"性能优化器初始化完成，配置: {asdict(self.config)}")
    
    def _create_rate_limiter(self):
        """创建速率限制器"""
        return {
            "requests": deque(maxlen=self.config.rate_limit_per_minute),
            "window_size": 60  # 1分钟窗口
        }
    
    def optimize_api_calls(self, function: Callable, *args, priority: RequestPriority = RequestPriority.NORMAL, **kwargs):
        """优化API调用"""
        task_id = f"task_{int(time.time() * 1000000)}"
        
        # 检查速率限制
        if not self._check_rate_limit():
            raise Exception("API调用频率超限，请稍后重试")
        
        # 创建任务
        task = RequestTask(
            task_id=task_id,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority,
            created_at=datetime.now(),
            timeout=kwargs.get('timeout', self.config.request_timeout)
        )
        
        # 添加到队列
        return self._submit_task(task)
    
    def _check_rate_limit(self) -> bool:
        """检查速率限制"""
        now = time.time()
        limiter = self.rate_limiter
        
        # 清理过期请求
        while limiter["requests"] and now - limiter["requests"][0] > limiter["window_size"]:
            limiter["requests"].popleft()
        
        # 检查是否超限
        if len(limiter["requests"]) >= self.config.rate_limit_per_minute:
            return False
        
        # 记录请求
        limiter["requests"].append(now)
        return True
    
    def _submit_task(self, task: RequestTask):
        """提交任务"""
        # 检查并发限制
        with self.request_lock:
            if self.active_requests >= self.config.max_concurrent_requests:
                # 队列已满，根据优先级决定是否替换
                if task.priority.value >= RequestPriority.HIGH.value:
                    return self._execute_task_immediate(task)
                else:
                    raise Exception("并发请求数量达到上限")
            
            self.active_requests += 1
        
        # 异步执行任务
        future = self.executor.submit(self._execute_task, task)
        self.processing_tasks[task.task_id] = {
            "task": task,
            "future": future,
            "start_time": time.time()
        }
        
        return future
    
    def _execute_task(self, task: RequestTask):
        """执行任务"""
        start_time = time.time()
        
        try:
            # 记录开始
            self.total_requests += 1
            
            # 执行函数
            result = task.function(*task.args, **task.kwargs)
            
            # 记录性能指标
            response_time = time.time() - start_time
            self.request_times.append(response_time)
            
            # 成功执行
            return {
                "success": True,
                "result": result,
                "response_time": response_time,
                "task_id": task.task_id
            }
            
        except Exception as e:
            # 记录错误
            self.error_count += 1
            response_time = time.time() - start_time
            
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "task_id": task.task_id
            }
            
        finally:
            # 释放并发槽位
            with self.request_lock:
                self.active_requests -= 1
            
            # 清理任务记录
            if task.task_id in self.processing_tasks:
                del self.processing_tasks[task.task_id]
    
    def _execute_task_immediate(self, task: RequestTask):
        """立即执行高优先级任务"""
        print(f"立即执行高优先级任务: {task.task_id}")
        return self._execute_task(task)
    
    def batch_optimize(self, requests: List[Dict[str, Any]], batch_key: str = "default"):
        """批量优化处理"""
        if not requests:
            return []
        
        # 根据配置确定批次大小
        batch_size = min(self.config.batch_size, len(requests))
        results = []
        
        # 分批处理
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batch_results = self._process_batch(batch, f"{batch_key}_batch_{i}")
            results.extend(batch_results)
        
        return results
    
    def _process_batch(self, batch: List[Dict[str, Any]], batch_id: str) -> List[Any]:
        """处理单个批次"""
        print(f"处理批次 {batch_id}，大小: {len(batch)}")
        
        futures = []
        for i, request in enumerate(batch):
            task_id = f"{batch_id}_item_{i}"
            
            # 创建任务
            task = RequestTask(
                task_id=task_id,
                function=request["function"],
                args=request.get("args", ()),
                kwargs=request.get("kwargs", {}),
                priority=RequestPriority(request.get("priority", RequestPriority.NORMAL.value)),
                created_at=datetime.now()
            )
            
            # 提交任务
            try:
                future = self._submit_task(task)
                futures.append(future)
            except Exception as e:
                print(f"批次任务提交失败: {e}")
                futures.append(None)
        
        # 等待所有任务完成
        results = []
        for future in futures:
            if future:
                try:
                    result = future.result(timeout=self.config.request_timeout)
                    results.append(result)
                except Exception as e:
                    results.append({"success": False, "error": str(e)})
            else:
                results.append({"success": False, "error": "Task submission failed"})
        
        return results
    
    def cache_optimize(self, cache_key: str, cache_data: Any, ttl: int = None):
        """缓存优化"""
        if ttl is None:
            ttl = self.config.cache_ttl
        
        # 更新缓存统计
        self.cache_stats["total_requests"] += 1
        
        # 实际的缓存逻辑应该在这里实现
        # 这里只是示例
        cache_result = {
            "key": cache_key,
            "data": cache_data,
            "ttl": ttl,
            "cached_at": datetime.now().isoformat()
        }
        
        print(f"缓存优化: {cache_key}, TTL: {ttl}秒")
        return cache_result
    
    def get_cache_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.cache_stats["total_requests"]
        if total == 0:
            return 0.0
        
        hits = self.cache_stats["hits"]
        return (hits / total) * 100
    
    def concurrent_optimize(self, tasks: List[Callable], max_workers: int = None) -> List[Any]:
        """并发优化处理"""
        if max_workers is None:
            max_workers = min(self.config.max_concurrent_requests, len(tasks))
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_task = {}
            for i, task in enumerate(tasks):
                if callable(task):
                    future = executor.submit(task)
                    future_to_task[future] = i
                else:
                    # 如果是字典格式的任务
                    future = executor.submit(task["function"], *task.get("args", ()), **task.get("kwargs", {}))
                    future_to_task[future] = i
            
            # 收集结果
            results = [None] * len(tasks)
            for future in as_completed(future_to_task):
                task_index = future_to_task[future]
                try:
                    result = future.result(timeout=self.config.request_timeout)
                    results[task_index] = {"success": True, "result": result}
                except Exception as e:
                    results[task_index] = {"success": False, "error": str(e)}
        
        return results
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        # 计算平均响应时间
        avg_response_time = sum(self.request_times) / len(self.request_times) if self.request_times else 0
        
        # 计算缓存命中率
        cache_hit_rate = self.get_cache_hit_rate()
        
        # 计算API调用频率（每分钟）
        recent_requests = len([t for t in self.rate_limiter["requests"] if time.time() - t <= 60])
        api_call_frequency = recent_requests
        
        # 计算错误率
        error_rate = (self.error_count / max(self.total_requests, 1)) * 100
        
        # 计算吞吐量（每秒处理的请求数）
        if self.request_times:
            throughput = 1 / avg_response_time if avg_response_time > 0 else 0
        else:
            throughput = 0
        
        return PerformanceMetrics(
            avg_response_time=avg_response_time,
            cache_hit_rate=cache_hit_rate,
            api_call_frequency=api_call_frequency,
            concurrent_requests=self.active_requests,
            error_rate=error_rate,
            throughput=throughput,
            cpu_usage=0.0,  # 需要实际监控实现
            memory_usage=0.0  # 需要实际监控实现
        )
    
    def auto_optimize(self):
        """自动优化"""
        if not self.optimization_enabled:
            return
        
        # 获取当前性能指标
        metrics = self.get_performance_metrics()
        
        # 基于指标调整配置
        optimization_applied = False
        
        # 响应时间优化
        if metrics.avg_response_time > 5.0:  # 5秒响应时间阈值
            if self.config.max_concurrent_requests < 20:
                self.config.max_concurrent_requests += 2
                optimization_applied = True
                print("响应时间过长，增加并发请求数")
        
        # 错误率优化
        if metrics.error_rate > 10.0:  # 10%错误率阈值
            if self.config.retry_attempts < 5:
                self.config.retry_attempts += 1
                optimization_applied = True
                print("错误率过高，增加重试次数")
        
        # 缓存命中率优化
        if metrics.cache_hit_rate < 50.0:  # 50%缓存命中率阈值
            if self.config.cache_ttl < 7200:  # 最大2小时
                self.config.cache_ttl = int(self.config.cache_ttl * 1.5)
                optimization_applied = True
                print("缓存命中率过低，延长缓存时间")
        
        # API调用频率优化
        if metrics.api_call_frequency > self.config.rate_limit_per_minute * 0.8:
            if self.config.batch_size < 10:
                self.config.batch_size += 2
                optimization_applied = True
                print("API调用频率过高，增加批处理大小")
        
        if optimization_applied:
            self.last_optimization = datetime.now()
            print(f"自动优化已应用，新配置: {asdict(self.config)}")
        
        return optimization_applied
    
    def set_optimization_level(self, level: OptimizationLevel):
        """设置优化级别"""
        if level == OptimizationLevel.BASIC:
            self.config.max_concurrent_requests = 5
            self.config.batch_size = 3
            self.config.cache_ttl = 1800
        elif level == OptimizationLevel.BALANCED:
            self.config.max_concurrent_requests = 10
            self.config.batch_size = 5
            self.config.cache_ttl = 3600
        elif level == OptimizationLevel.AGGRESSIVE:
            self.config.max_concurrent_requests = 20
            self.config.batch_size = 10
            self.config.cache_ttl = 7200
        
        print(f"优化级别设置为: {level.value}")
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        metrics = self.get_performance_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "config": asdict(self.config),
            "metrics": asdict(metrics),
            "statistics": {
                "total_requests": self.total_requests,
                "error_count": self.error_count,
                "active_requests": self.active_requests,
                "last_optimization": self.last_optimization.isoformat() if self.last_optimization else None
            },
            "recommendations": self._generate_optimization_recommendations(metrics)
        }
    
    def _generate_optimization_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if metrics.avg_response_time > 3.0:
            recommendations.append("考虑增加并发请求数或使用批处理")
        
        if metrics.cache_hit_rate < 60.0:
            recommendations.append("优化缓存策略，延长TTL或改进缓存键设计")
        
        if metrics.error_rate > 5.0:
            recommendations.append("检查API稳定性，考虑增加重试次数或改进错误处理")
        
        if metrics.api_call_frequency > 50:
            recommendations.append("考虑使用更大的批处理或实现更激进的缓存策略")
        
        if metrics.throughput < 1.0:
            recommendations.append("系统吞吐量较低，建议检查性能瓶颈")
        
        if not recommendations:
            recommendations.append("系统性能良好，保持当前优化策略")
        
        return recommendations
    
    def reset_metrics(self):
        """重置性能指标"""
        self.request_times.clear()
        self.error_count = 0
        self.total_requests = 0
        self.cache_stats = {"hits": 0, "misses": 0, "total_requests": 0}
        print("性能指标已重置")
    
    def shutdown(self):
        """关闭优化器"""
        print("正在关闭性能优化器...")
        self.executor.shutdown(wait=True)
        print("性能优化器已关闭")

# 全局性能优化器实例
performance_optimizer = PerformanceOptimizer()

if __name__ == "__main__":
    # 测试性能优化器
    print("=== 性能优化器测试 ===")
    
    # 定义测试函数
    def test_api_call(word: str, delay: float = 0.1):
        """模拟API调用"""
        time.sleep(delay)
        return f"Generated content for {word}"
    
    def test_slow_api_call(word: str):
        """模拟慢速API调用"""
        time.sleep(2.0)
        return f"Slow generated content for {word}"
    
    def test_error_api_call(word: str):
        """模拟错误API调用"""
        raise Exception(f"API error for {word}")
    
    # 测试基础优化
    print("\n--- 基础API调用优化测试 ---")
    try:
        future = performance_optimizer.optimize_api_calls(
            test_api_call, 
            "apple", 
            delay=0.5,
            priority=RequestPriority.NORMAL
        )
        result = future.result(timeout=10)
        print(f"API调用结果: {result}")
    except Exception as e:
        print(f"API调用失败: {e}")
    
    # 测试批量优化
    print("\n--- 批量优化测试 ---")
    batch_requests = [
        {"function": test_api_call, "args": ("word1",), "kwargs": {"delay": 0.2}},
        {"function": test_api_call, "args": ("word2",), "kwargs": {"delay": 0.3}},
        {"function": test_api_call, "args": ("word3",), "kwargs": {"delay": 0.1}},
    ]
    
    batch_results = performance_optimizer.batch_optimize(batch_requests, "test_batch")
    print(f"批量处理结果数: {len(batch_results)}")
    for i, result in enumerate(batch_results):
        if result.get("success"):
            print(f"  批次 {i}: 成功 - 响应时间 {result.get('response_time', 0):.2f}s")
        else:
            print(f"  批次 {i}: 失败 - {result.get('error', 'Unknown error')}")
    
    # 测试并发优化
    print("\n--- 并发优化测试 ---")
    concurrent_tasks = [
        lambda: test_api_call("concurrent1", 0.3),
        lambda: test_api_call("concurrent2", 0.2),
        lambda: test_api_call("concurrent3", 0.4),
    ]
    
    concurrent_results = performance_optimizer.concurrent_optimize(concurrent_tasks, max_workers=3)
    print(f"并发处理结果数: {len(concurrent_results)}")
    for i, result in enumerate(concurrent_results):
        if result.get("success"):
            print(f"  并发任务 {i}: 成功")
        else:
            print(f"  并发任务 {i}: 失败 - {result.get('error', 'Unknown error')}")
    
    # 测试性能指标
    print("\n--- 性能指标 ---")
    metrics = performance_optimizer.get_performance_metrics()
    print(f"平均响应时间: {metrics.avg_response_time:.2f}s")
    print(f"缓存命中率: {metrics.cache_hit_rate:.1f}%")
    print(f"API调用频率: {metrics.api_call_frequency}/分钟")
    print(f"并发请求数: {metrics.concurrent_requests}")
    print(f"错误率: {metrics.error_rate:.1f}%")
    print(f"吞吐量: {metrics.throughput:.2f} 请求/秒")
    
    # 测试自动优化
    print("\n--- 自动优化测试 ---")
    optimization_applied = performance_optimizer.auto_optimize()
    print(f"自动优化已应用: {optimization_applied}")
    
    # 设置优化级别
    print("\n--- 优化级别测试 ---")
    performance_optimizer.set_optimization_level(OptimizationLevel.AGGRESSIVE)
    
    # 获取优化报告
    print("\n--- 优化报告 ---")
    report = performance_optimizer.get_optimization_report()
    print(f"总请求数: {report['statistics']['total_requests']}")
    print(f"错误数: {report['statistics']['error_count']}")
    print(f"当前配置 - 最大并发: {report['config']['max_concurrent_requests']}")
    print(f"当前配置 - 批处理大小: {report['config']['batch_size']}")
    
    print("\n优化建议:")
    for rec in report["recommendations"]:
        print(f"  • {rec}")
    
    print("\n性能优化器测试完成！")

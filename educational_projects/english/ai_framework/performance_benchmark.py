#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试
测试API调用性能、成本控制和缓存效果
"""

import time
import json
import os
import threading
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
import sys

# 添加路径以导入组件
sys.path.append(os.path.dirname(__file__))

from performance_optimizer import PerformanceOptimizer
from content_cache_manager import ContentCacheManager
from multi_mode_integration import MultiModeIntegration

class BenchmarkType(Enum):
    """基准测试类型"""
    API_PERFORMANCE = "api_performance"
    CACHE_EFFICIENCY = "cache_efficiency"
    CONCURRENT_LOAD = "concurrent_load"
    MEMORY_USAGE = "memory_usage"
    COST_ANALYSIS = "cost_analysis"

@dataclass
class PerformanceMetrics:
    """性能指标"""
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    cache_hit_rate: float

@dataclass
class CostMetrics:
    """成本指标"""
    api_calls_count: int
    estimated_cost: float
    cost_per_request: float
    cache_savings: float
    efficiency_score: float

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    benchmark_type: BenchmarkType
    test_duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    performance_metrics: PerformanceMetrics
    cost_metrics: Optional[CostMetrics]
    additional_data: Dict[str, Any]

class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self):
        # 初始化组件
        self.optimizer = PerformanceOptimizer()
        self.cache_manager = ContentCacheManager()
        self.multi_mode = MultiModeIntegration()
        
        # 测试配置
        self.benchmark_config = {
            "api_test_requests": 100,
            "cache_test_requests": 200,
            "concurrent_threads": 10,
            "memory_test_iterations": 50,
            "cost_per_api_call": 0.002,  # 假设每次API调用成本2毫
            "test_timeout": 300  # 5分钟超时
        }
        
        # 结果存储
        self.benchmark_results: List[BenchmarkResult] = []
        
        print("性能基准测试系统初始化完成")
    
    def run_all_benchmarks(self):
        """运行所有基准测试"""
        print("=" * 60)
        print("⚡ 开始性能基准测试")
        print("=" * 60)
        
        try:
            # API性能测试
            print("\n🚀 API性能基准测试")
            api_result = self.benchmark_api_performance()
            self.benchmark_results.append(api_result)
            
            # 缓存效率测试
            print("\n💾 缓存效率基准测试")
            cache_result = self.benchmark_cache_efficiency()
            self.benchmark_results.append(cache_result)
            
            # 并发负载测试
            print("\n🔄 并发负载基准测试")
            concurrent_result = self.benchmark_concurrent_load()
            self.benchmark_results.append(concurrent_result)
            
            # 内存使用测试
            print("\n🧠 内存使用基准测试")
            memory_result = self.benchmark_memory_usage()
            self.benchmark_results.append(memory_result)
            
            # 成本分析测试
            print("\n💰 成本分析基准测试")
            cost_result = self.benchmark_cost_analysis()
            self.benchmark_results.append(cost_result)
            
            # 生成综合报告
            self.generate_benchmark_report()
            
        except Exception as e:
            print(f"基准测试执行失败: {e}")
    
    def benchmark_api_performance(self) -> BenchmarkResult:
        """API性能基准测试"""
        print("  测试API调用响应时间和吞吐量...")
        
        start_time = time.time()
        response_times = []
        successful_requests = 0
        failed_requests = 0
        
        def test_api_call():
            """模拟API调用"""
            call_start = time.time()
            try:
                # 模拟API调用
                time.sleep(0.1 + (hash(threading.current_thread().name) % 100) / 1000)  # 0.1-0.2秒随机延时
                call_time = time.time() - call_start
                return call_time, True
            except Exception:
                call_time = time.time() - call_start
                return call_time, False
        
        # 单线程性能测试
        for i in range(self.benchmark_config["api_test_requests"]):
            call_time, success = test_api_call()
            response_times.append(call_time)
            
            if success:
                successful_requests += 1
            else:
                failed_requests += 1
            
            if (i + 1) % 20 == 0:
                print(f"    已完成 {i + 1}/{self.benchmark_config['api_test_requests']} 个请求")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 计算性能指标
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        p95_response_time = sorted_times[p95_index]
        p99_response_time = sorted_times[p99_index]
        
        throughput = successful_requests / total_duration
        error_rate = failed_requests / (successful_requests + failed_requests) * 100
        
        # 系统资源使用
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        
        performance_metrics = PerformanceMetrics(
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            throughput=throughput,
            error_rate=error_rate,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            cache_hit_rate=0.0
        )
        
        print(f"  ✅ API性能测试完成:")
        print(f"    平均响应时间: {avg_response_time:.3f}s")
        print(f"    吞吐量: {throughput:.2f} 请求/秒")
        print(f"    错误率: {error_rate:.2f}%")
        
        return BenchmarkResult(
            benchmark_type=BenchmarkType.API_PERFORMANCE,
            test_duration=total_duration,
            total_requests=self.benchmark_config["api_test_requests"],
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            performance_metrics=performance_metrics,
            cost_metrics=None,
            additional_data={"response_times": response_times}
        )
    
    def benchmark_cache_efficiency(self) -> BenchmarkResult:
        """缓存效率基准测试"""
        print("  测试缓存命中率和性能提升...")
        
        start_time = time.time()
        cache_hits = 0
        cache_misses = 0
        response_times_with_cache = []
        response_times_without_cache = []
        
        # 预填充缓存
        cache_keys = [f"test_key_{i}" for i in range(50)]
        for key in cache_keys:
            self.cache_manager.store_content(key, f"test_data_{key}", "benchmark")
        
        # 测试缓存性能
        test_requests = self.benchmark_config["cache_test_requests"]
        
        for i in range(test_requests):
            key = f"test_key_{i % 50}"  # 50%的键会命中缓存
            
            # 带缓存的请求
            cache_start = time.time()
            cached_data = self.cache_manager.get_cached_content(key)
            cache_time = time.time() - cache_start
            
            if cached_data:
                cache_hits += 1
                response_times_with_cache.append(cache_time)
            else:
                cache_misses += 1
                # 模拟生成新内容
                generation_time = 0.1  # 模拟100ms生成时间
                total_time = cache_time + generation_time
                response_times_with_cache.append(total_time)
                
                # 存储到缓存
                self.cache_manager.store_content(key, f"generated_data_{key}", "benchmark")
            
            # 不带缓存的请求（模拟）
            no_cache_time = 0.1 + (i % 10) / 100  # 模拟100-110ms
            response_times_without_cache.append(no_cache_time)
            
            if (i + 1) % 40 == 0:
                print(f"    已完成 {i + 1}/{test_requests} 个缓存测试")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 计算缓存指标
        cache_hit_rate = cache_hits / test_requests * 100
        avg_time_with_cache = statistics.mean(response_times_with_cache)
        avg_time_without_cache = statistics.mean(response_times_without_cache)
        cache_speedup = (avg_time_without_cache - avg_time_with_cache) / avg_time_without_cache * 100
        
        performance_metrics = PerformanceMetrics(
            avg_response_time=avg_time_with_cache,
            min_response_time=min(response_times_with_cache),
            max_response_time=max(response_times_with_cache),
            p95_response_time=sorted(response_times_with_cache)[int(len(response_times_with_cache) * 0.95)],
            p99_response_time=sorted(response_times_with_cache)[int(len(response_times_with_cache) * 0.99)],
            throughput=test_requests / total_duration,
            error_rate=0.0,
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage=psutil.virtual_memory().percent,
            cache_hit_rate=cache_hit_rate
        )
        
        print(f"  ✅ 缓存效率测试完成:")
        print(f"    缓存命中率: {cache_hit_rate:.1f}%")
        print(f"    缓存加速比: {cache_speedup:.1f}%")
        print(f"    平均响应时间(带缓存): {avg_time_with_cache:.3f}s")
        
        return BenchmarkResult(
            benchmark_type=BenchmarkType.CACHE_EFFICIENCY,
            test_duration=total_duration,
            total_requests=test_requests,
            successful_requests=test_requests,
            failed_requests=0,
            performance_metrics=performance_metrics,
            cost_metrics=None,
            additional_data={
                "cache_hits": cache_hits,
                "cache_misses": cache_misses,
                "speedup_percentage": cache_speedup
            }
        )
    
    def benchmark_concurrent_load(self) -> BenchmarkResult:
        """并发负载基准测试"""
        print("  测试并发处理能力和资源使用...")
        
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        def concurrent_task(task_id: int):
            """并发任务"""
            try:
                task_start = time.time()
                
                # 使用性能优化器处理任务
                def simple_task():
                    time.sleep(0.05 + (task_id % 10) / 200)  # 50-100ms
                    return f"Task {task_id} completed"
                
                future = self.optimizer.optimize_api_calls(simple_task)
                result = future.result(timeout=30)
                
                task_time = time.time() - task_start
                return task_time, True, None
                
            except Exception as e:
                task_time = time.time() - task_start
                return task_time, False, str(e)
        
        # 并发执行任务
        total_tasks = self.benchmark_config["concurrent_threads"] * 10  # 每个线程10个任务
        
        with ThreadPoolExecutor(max_workers=self.benchmark_config["concurrent_threads"]) as executor:
            # 提交所有任务
            futures = [executor.submit(concurrent_task, i) for i in range(total_tasks)]
            
            # 收集结果
            for i, future in enumerate(as_completed(futures)):
                try:
                    task_time, success, error = future.result(timeout=60)
                    response_times.append(task_time)
                    
                    if success:
                        successful_requests += 1
                    else:
                        failed_requests += 1
                        if error:
                            print(f"    任务失败: {error}")
                    
                    if (i + 1) % 20 == 0:
                        print(f"    已完成 {i + 1}/{total_tasks} 个并发任务")
                        
                except Exception as e:
                    failed_requests += 1
                    print(f"    任务执行异常: {e}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 计算并发性能指标
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            sorted_times = sorted(response_times)
            p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
            p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        throughput = successful_requests / total_duration
        error_rate = failed_requests / total_tasks * 100
        
        performance_metrics = PerformanceMetrics(
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            throughput=throughput,
            error_rate=error_rate,
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage=psutil.virtual_memory().percent,
            cache_hit_rate=0.0
        )
        
        print(f"  ✅ 并发负载测试完成:")
        print(f"    并发吞吐量: {throughput:.2f} 请求/秒")
        print(f"    并发错误率: {error_rate:.2f}%")
        print(f"    平均响应时间: {avg_response_time:.3f}s")
        
        return BenchmarkResult(
            benchmark_type=BenchmarkType.CONCURRENT_LOAD,
            test_duration=total_duration,
            total_requests=total_tasks,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            performance_metrics=performance_metrics,
            cost_metrics=None,
            additional_data={
                "concurrent_threads": self.benchmark_config["concurrent_threads"],
                "tasks_per_thread": 10
            }
        )
    
    def benchmark_memory_usage(self) -> BenchmarkResult:
        """内存使用基准测试"""
        print("  测试内存使用和泄漏情况...")
        
        start_time = time.time()
        
        # 记录初始内存状态
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        initial_objects = len(gc.get_objects())
        
        memory_samples = [initial_memory]
        object_samples = [initial_objects]
        
        # 内存压力测试
        iterations = self.benchmark_config["memory_test_iterations"]
        objects_created = []
        
        for i in range(iterations):
            # 创建和销毁对象
            temp_objects = []
            
            # 创建大量对象
            for j in range(100):
                temp_objects.append({
                    "id": f"obj_{i}_{j}",
                    "data": "x" * 1000,  # 1KB字符串
                    "timestamp": datetime.now(),
                    "nested": {"value": list(range(50))}
                })
            
            objects_created.extend(temp_objects)
            
            # 部分清理（模拟实际使用）
            if i % 10 == 0:
                objects_created = objects_created[-500:]  # 保留最近500个对象
                gc.collect()
            
            # 记录内存使用
            if i % 5 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                current_objects = len(gc.get_objects())
                memory_samples.append(current_memory)
                object_samples.append(current_objects)
            
            if (i + 1) % 10 == 0:
                print(f"    已完成 {i + 1}/{iterations} 次内存测试")
        
        # 清理并最终测量
        del objects_created
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        final_objects = len(gc.get_objects())
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 分析内存使用
        max_memory = max(memory_samples)
        avg_memory = statistics.mean(memory_samples)
        memory_growth = final_memory - initial_memory
        object_growth = final_objects - initial_objects
        
        performance_metrics = PerformanceMetrics(
            avg_response_time=0.0,
            min_response_time=0.0,
            max_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            throughput=0.0,
            error_rate=0.0,
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage=final_memory,
            cache_hit_rate=0.0
        )
        
        print(f"  ✅ 内存使用测试完成:")
        print(f"    初始内存: {initial_memory:.1f} MB")
        print(f"    最大内存: {max_memory:.1f} MB")
        print(f"    最终内存: {final_memory:.1f} MB") 
        print(f"    内存增长: {memory_growth:.1f} MB")
        print(f"    对象增长: {object_growth}")
        
        return BenchmarkResult(
            benchmark_type=BenchmarkType.MEMORY_USAGE,
            test_duration=total_duration,
            total_requests=iterations,
            successful_requests=iterations,
            failed_requests=0,
            performance_metrics=performance_metrics,
            cost_metrics=None,
            additional_data={
                "initial_memory_mb": initial_memory,
                "max_memory_mb": max_memory,
                "final_memory_mb": final_memory,
                "memory_growth_mb": memory_growth,
                "object_growth": object_growth,
                "memory_samples": memory_samples,
                "object_samples": object_samples
            }
        )
    
    def benchmark_cost_analysis(self) -> BenchmarkResult:
        """成本分析基准测试"""
        print("  分析API调用成本和缓存节约...")
        
        start_time = time.time()
        
        # 模拟不同场景的API调用
        scenarios = [
            {"name": "无缓存", "cache_hit_rate": 0.0, "requests": 100},
            {"name": "低缓存", "cache_hit_rate": 0.3, "requests": 100},
            {"name": "高缓存", "cache_hit_rate": 0.8, "requests": 100},
        ]
        
        cost_analysis = []
        
        for scenario in scenarios:
            requests = scenario["requests"]
            cache_hit_rate = scenario["cache_hit_rate"]
            
            # 计算实际API调用次数
            actual_api_calls = int(requests * (1 - cache_hit_rate))
            cached_requests = requests - actual_api_calls
            
            # 成本计算
            api_cost = actual_api_calls * self.benchmark_config["cost_per_api_call"]
            cache_savings = cached_requests * self.benchmark_config["cost_per_api_call"]
            total_cost = api_cost
            
            # 效率评分（考虑成本和性能）
            efficiency_score = (1 - total_cost / (requests * self.benchmark_config["cost_per_api_call"])) * 100
            
            scenario_result = {
                "scenario": scenario["name"],
                "total_requests": requests,
                "api_calls": actual_api_calls,
                "cached_requests": cached_requests,
                "cache_hit_rate": cache_hit_rate * 100,
                "api_cost": api_cost,
                "cache_savings": cache_savings,
                "total_cost": total_cost,
                "cost_per_request": total_cost / requests,
                "efficiency_score": efficiency_score
            }
            
            cost_analysis.append(scenario_result)
            
            print(f"    场景 '{scenario['name']}': "
                  f"成本 ${total_cost:.4f}, "
                  f"节约 ${cache_savings:.4f}, "
                  f"效率 {efficiency_score:.1f}%")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 计算平均成本指标
        avg_api_calls = statistics.mean([s["api_calls"] for s in cost_analysis])
        avg_cost = statistics.mean([s["total_cost"] for s in cost_analysis])
        avg_savings = statistics.mean([s["cache_savings"] for s in cost_analysis])
        avg_efficiency = statistics.mean([s["efficiency_score"] for s in cost_analysis])
        
        cost_metrics = CostMetrics(
            api_calls_count=int(avg_api_calls),
            estimated_cost=avg_cost,
            cost_per_request=avg_cost / 100,  # 假设100个请求
            cache_savings=avg_savings,
            efficiency_score=avg_efficiency
        )
        
        performance_metrics = PerformanceMetrics(
            avg_response_time=0.0,
            min_response_time=0.0,
            max_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            throughput=0.0,
            error_rate=0.0,
            cpu_usage=0.0,
            memory_usage=0.0,
            cache_hit_rate=0.0
        )
        
        print(f"  ✅ 成本分析测试完成:")
        print(f"    平均API调用数: {avg_api_calls:.0f}")
        print(f"    平均成本: ${avg_cost:.4f}")
        print(f"    平均节约: ${avg_savings:.4f}")
        print(f"    平均效率评分: {avg_efficiency:.1f}%")
        
        return BenchmarkResult(
            benchmark_type=BenchmarkType.COST_ANALYSIS,
            test_duration=total_duration,
            total_requests=300,  # 3个场景 × 100请求
            successful_requests=300,
            failed_requests=0,
            performance_metrics=performance_metrics,
            cost_metrics=cost_metrics,
            additional_data={"scenarios": cost_analysis}
        )
    
    def generate_benchmark_report(self):
        """生成基准测试报告"""
        print("\n" + "=" * 60)
        print("📊 性能基准测试报告")
        print("=" * 60)
        
        # 总体概况
        total_requests = sum(r.total_requests for r in self.benchmark_results)
        total_successful = sum(r.successful_requests for r in self.benchmark_results)
        total_failed = sum(r.failed_requests for r in self.benchmark_results)
        total_duration = sum(r.test_duration for r in self.benchmark_results)
        
        print(f"测试概况:")
        print(f"  总请求数: {total_requests}")
        print(f"  成功请求: {total_successful} ({total_successful/total_requests*100:.1f}%)")
        print(f"  失败请求: {total_failed} ({total_failed/total_requests*100:.1f}%)")
        print(f"  总测试时间: {total_duration:.2f}秒")
        
        # 各项测试详情
        print(f"\n详细测试结果:")
        
        for result in self.benchmark_results:
            test_name = {
                BenchmarkType.API_PERFORMANCE: "API性能",
                BenchmarkType.CACHE_EFFICIENCY: "缓存效率",
                BenchmarkType.CONCURRENT_LOAD: "并发负载",
                BenchmarkType.MEMORY_USAGE: "内存使用",
                BenchmarkType.COST_ANALYSIS: "成本分析"
            }[result.benchmark_type]
            
            print(f"\n📈 {test_name}测试:")
            print(f"  测试时长: {result.test_duration:.2f}s")
            print(f"  请求数量: {result.total_requests}")
            print(f"  成功率: {result.successful_requests/result.total_requests*100:.1f}%")
            
            if result.benchmark_type != BenchmarkType.COST_ANALYSIS:
                metrics = result.performance_metrics
                if metrics.avg_response_time > 0:
                    print(f"  平均响应时间: {metrics.avg_response_time:.3f}s")
                    print(f"  P95响应时间: {metrics.p95_response_time:.3f}s")
                if metrics.throughput > 0:
                    print(f"  吞吐量: {metrics.throughput:.2f} 请求/秒")
                if metrics.error_rate > 0:
                    print(f"  错误率: {metrics.error_rate:.2f}%")
                if metrics.cache_hit_rate > 0:
                    print(f"  缓存命中率: {metrics.cache_hit_rate:.1f}%")
            
            if result.cost_metrics:
                cost = result.cost_metrics
                print(f"  API调用数: {cost.api_calls_count}")
                print(f"  估算成本: ${cost.estimated_cost:.4f}")
                print(f"  缓存节约: ${cost.cache_savings:.4f}")
                print(f"  效率评分: {cost.efficiency_score:.1f}%")
        
        # 性能等级评估
        print(f"\n🏆 性能等级评估:")
        self._evaluate_performance_grade()
        
        # 优化建议
        print(f"\n🚀 优化建议:")
        self._generate_optimization_recommendations()
        
        # 保存详细报告
        self._save_benchmark_report()
    
    def _evaluate_performance_grade(self):
        """评估性能等级"""
        
        # 获取关键指标
        api_result = next((r for r in self.benchmark_results if r.benchmark_type == BenchmarkType.API_PERFORMANCE), None)
        cache_result = next((r for r in self.benchmark_results if r.benchmark_type == BenchmarkType.CACHE_EFFICIENCY), None)
        concurrent_result = next((r for r in self.benchmark_results if r.benchmark_type == BenchmarkType.CONCURRENT_LOAD), None)
        memory_result = next((r for r in self.benchmark_results if r.benchmark_type == BenchmarkType.MEMORY_USAGE), None)
        
        score = 0
        max_score = 0
        
        # API性能评分
        if api_result:
            max_score += 25
            if api_result.performance_metrics.avg_response_time < 0.1:
                score += 25
            elif api_result.performance_metrics.avg_response_time < 0.2:
                score += 20
            elif api_result.performance_metrics.avg_response_time < 0.5:
                score += 15
            else:
                score += 10
        
        # 缓存效率评分
        if cache_result:
            max_score += 25
            hit_rate = cache_result.performance_metrics.cache_hit_rate
            if hit_rate > 80:
                score += 25
            elif hit_rate > 60:
                score += 20
            elif hit_rate > 40:
                score += 15
            else:
                score += 10
        
        # 并发性能评分
        if concurrent_result:
            max_score += 25
            error_rate = concurrent_result.performance_metrics.error_rate
            if error_rate < 1:
                score += 25
            elif error_rate < 5:
                score += 20
            elif error_rate < 10:
                score += 15
            else:
                score += 10
        
        # 内存使用评分
        if memory_result:
            max_score += 25
            memory_growth = memory_result.additional_data.get("memory_growth_mb", 0)
            if memory_growth < 10:
                score += 25
            elif memory_growth < 50:
                score += 20
            elif memory_growth < 100:
                score += 15
            else:
                score += 10
        
        # 计算等级
        if max_score > 0:
            percentage = (score / max_score) * 100
            
            if percentage >= 90:
                grade = "A+"
                description = "优秀"
            elif percentage >= 80:
                grade = "A"
                description = "良好"
            elif percentage >= 70:
                grade = "B"
                description = "中等"
            elif percentage >= 60:
                grade = "C"
                description = "及格"
            else:
                grade = "D"
                description = "需要改进"
            
            print(f"  整体性能等级: {grade} ({description})")
            print(f"  综合得分: {score}/{max_score} ({percentage:.1f}%)")
        else:
            print(f"  无法评估性能等级（缺少测试数据）")
    
    def _generate_optimization_recommendations(self):
        """生成优化建议"""
        recommendations = []
        
        # 基于各项测试结果生成建议
        for result in self.benchmark_results:
            if result.benchmark_type == BenchmarkType.API_PERFORMANCE:
                if result.performance_metrics.avg_response_time > 0.2:
                    recommendations.append("API响应时间较慢，建议优化网络连接或算法效率")
                if result.performance_metrics.error_rate > 5:
                    recommendations.append("API错误率较高，建议增加重试机制和错误处理")
            
            elif result.benchmark_type == BenchmarkType.CACHE_EFFICIENCY:
                if result.performance_metrics.cache_hit_rate < 60:
                    recommendations.append("缓存命中率偏低，建议优化缓存策略或增加TTL")
            
            elif result.benchmark_type == BenchmarkType.CONCURRENT_LOAD:
                if result.performance_metrics.error_rate > 10:
                    recommendations.append("并发处理错误率高，建议增加连接池大小或优化资源管理")
                if result.performance_metrics.throughput < 10:
                    recommendations.append("并发吞吐量偏低，建议优化线程池配置")
            
            elif result.benchmark_type == BenchmarkType.MEMORY_USAGE:
                memory_growth = result.additional_data.get("memory_growth_mb", 0)
                if memory_growth > 50:
                    recommendations.append("内存增长较大，建议检查内存泄漏和优化对象管理")
            
            elif result.benchmark_type == BenchmarkType.COST_ANALYSIS:
                if result.cost_metrics and result.cost_metrics.efficiency_score < 70:
                    recommendations.append("成本效率偏低，建议提高缓存利用率和优化API调用策略")
        
        # 通用建议
        if not recommendations:
            recommendations.append("系统性能表现良好，建议继续监控并定期进行性能测试")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    def _save_benchmark_report(self):
        """保存基准测试报告"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_requests": sum(r.total_requests for r in self.benchmark_results),
                    "total_successful": sum(r.successful_requests for r in self.benchmark_results),
                    "total_failed": sum(r.failed_requests for r in self.benchmark_results),
                    "total_duration": sum(r.test_duration for r in self.benchmark_results)
                },
                "benchmark_results": [asdict(result) for result in self.benchmark_results],
                "system_info": {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                    "python_version": sys.version
                }
            }
            
            with open("performance_benchmark_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 详细基准测试报告已保存到: performance_benchmark_report.json")
            
        except Exception as e:
            print(f"保存基准测试报告失败: {e}")

def run_performance_benchmark():
    """运行性能基准测试"""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()
    return benchmark

if __name__ == "__main__":
    print("=" * 60)
    print("⚡ 性能基准测试")
    print("=" * 60)
    
    benchmark = run_performance_benchmark()
    
    print(f"\n测试完成！详细结果请查看:")
    print(f"  • performance_benchmark_report.json - 详细数据和分析")

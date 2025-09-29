#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI批处理器
优化AI调用性能，支持批量处理和智能调度
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue, Empty

from ..monitoring.metrics import get_metrics
from ..cache.cache_manager import get_cache
from ..errors.exceptions import AIGenerationError


class BatchStatus(Enum):
    """批处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BatchRequest:
    """批处理请求"""
    id: str
    data: Any
    priority: int = 1
    timeout: int = 60
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None
    created_at: float = field(default_factory=time.time)
    status: BatchStatus = BatchStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchConfig:
    """批处理配置"""
    max_batch_size: int = 10
    max_wait_time: float = 2.0  # 最大等待时间（秒）
    max_concurrent_batches: int = 3
    retry_delay: float = 1.0
    enable_priority: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600


class BatchProcessor:
    """AI批处理器"""
    
    def __init__(self, config: BatchConfig = None):
        self.config = config or BatchConfig()
        self.metrics = get_metrics()
        self.cache = get_cache()
        
        # 批处理队列
        self.request_queue = Queue()
        self.pending_requests: Dict[str, BatchRequest] = {}
        self.completed_requests: Dict[str, BatchRequest] = {}
        self.processing_batches: List[List[BatchRequest]] = []
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_batches)
        self.worker_threads = []
        self.shutdown_event = threading.Event()
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "completed_requests": 0,
            "failed_requests": 0,
            "cached_requests": 0,
            "average_batch_size": 0.0,
            "average_processing_time": 0.0
        }
        
        # 启动工作线程
        self._start_workers()
    
    def _start_workers(self):
        """启动工作线程"""
        for i in range(self.config.max_concurrent_batches):
            worker = threading.Thread(target=self._worker_loop, name=f"BatchWorker-{i}")
            worker.daemon = True
            worker.start()
            self.worker_threads.append(worker)
    
    def _worker_loop(self):
        """工作线程循环"""
        while not self.shutdown_event.is_set():
            try:
                # 收集批处理请求
                batch = self._collect_batch()
                if batch:
                    self._process_batch(batch)
                else:
                    time.sleep(0.1)  # 避免忙等待
            except Exception as e:
                print(f"批处理工作线程错误: {e}")
                time.sleep(1)
    
    def _collect_batch(self) -> List[BatchRequest]:
        """收集批处理请求"""
        batch = []
        start_time = time.time()
        
        while len(batch) < self.config.max_batch_size:
            try:
                # 尝试获取请求
                if batch:
                    # 如果已有请求，使用短超时
                    timeout = max(0.1, self.config.max_wait_time - (time.time() - start_time))
                    request = self.request_queue.get(timeout=timeout)
                else:
                    # 如果没有请求，等待更长时间
                    request = self.request_queue.get(timeout=self.config.max_wait_time)
                
                # 检查请求是否超时
                if time.time() - request.created_at > request.timeout:
                    request.status = BatchStatus.FAILED
                    request.error = "请求超时"
                    self._handle_request_completion(request)
                    continue
                
                batch.append(request)
                
            except Empty:
                break
        
        return batch
    
    def _process_batch(self, batch: List[BatchRequest]):
        """处理批处理请求"""
        if not batch:
            return
        
        # 更新统计信息
        self.stats["total_requests"] += len(batch)
        self.stats["average_batch_size"] = (
            (self.stats["average_batch_size"] * (self.stats["total_requests"] - len(batch)) + len(batch)) 
            / self.stats["total_requests"]
        )
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 按优先级排序
            if self.config.enable_priority:
                batch.sort(key=lambda x: x.priority, reverse=True)
            
            # 处理批处理请求
            self._execute_batch(batch)
            
            # 更新处理时间统计
            processing_time = time.time() - start_time
            self.stats["average_processing_time"] = (
                (self.stats["average_processing_time"] * (self.stats["total_requests"] - len(batch)) + processing_time) 
                / self.stats["total_requests"]
            )
            
            # 记录性能指标
            self.metrics.record_timer("batch_processing.duration", processing_time)
            self.metrics.increment_counter("batch_processing.batches_processed")
            self.metrics.increment_counter("batch_processing.requests_processed", len(batch))
            
        except Exception as e:
            # 处理批处理失败
            for request in batch:
                request.status = BatchStatus.FAILED
                request.error = str(e)
                self._handle_request_completion(request)
    
    def _execute_batch(self, batch: List[BatchRequest]):
        """执行批处理请求"""
        # 这里应该调用实际的AI处理函数
        # 暂时模拟处理
        for request in batch:
            try:
                # 检查缓存
                if self.config.enable_caching:
                    cache_key = self._generate_cache_key(request)
                    cached_result = self.cache.get(cache_key)
                    if cached_result is not None:
                        request.result = cached_result
                        request.status = BatchStatus.COMPLETED
                        self.stats["cached_requests"] += 1
                        self._handle_request_completion(request)
                        continue
                
                # 处理请求（这里应该调用实际的AI处理函数）
                result = self._process_single_request(request)
                
                # 缓存结果
                if self.config.enable_caching and result is not None:
                    cache_key = self._generate_cache_key(request)
                    self.cache.set(cache_key, result, self.config.cache_ttl)
                
                request.result = result
                request.status = BatchStatus.COMPLETED
                self.stats["completed_requests"] += 1
                
            except Exception as e:
                request.status = BatchStatus.FAILED
                request.error = str(e)
                self.stats["failed_requests"] += 1
            
            self._handle_request_completion(request)
    
    def _process_single_request(self, request: BatchRequest) -> Any:
        """处理单个请求"""
        # 检查是否有处理函数
        processor_func = request.metadata.get("processor_func")
        if processor_func:
            return processor_func(request.data)
        
        # 默认处理逻辑
        time.sleep(0.1)  # 模拟处理时间
        return f"processed_{request.id}"
    
    def _generate_cache_key(self, request: BatchRequest) -> str:
        """生成缓存键"""
        import hashlib
        import json
        
        # 基于请求数据生成缓存键
        data_str = json.dumps(request.data, sort_keys=True) if isinstance(request.data, dict) else str(request.data)
        key_data = f"{request.id}:{data_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _handle_request_completion(self, request: BatchRequest):
        """处理请求完成"""
        # 调用回调函数
        if request.callback:
            try:
                request.callback(request)
            except Exception as e:
                print(f"回调函数执行失败: {e}")
        
        # 移动到已完成列表
        if request.id in self.pending_requests:
            del self.pending_requests[request.id]
        self.completed_requests[request.id] = request
    
    def submit_request(self, request_id: str, data: Any, priority: int = 1, 
                      timeout: int = 60, callback: Optional[Callable] = None, 
                      processor_func: Optional[Callable] = None) -> str:
        """提交批处理请求"""
        request = BatchRequest(
            id=request_id,
            data=data,
            priority=priority,
            timeout=timeout,
            callback=callback
        )
        
        # 存储处理函数
        if processor_func:
            request.metadata["processor_func"] = processor_func
        
        self.pending_requests[request_id] = request
        self.request_queue.put(request)
        
        return request_id
    
    def get_request_status(self, request_id: str) -> Optional[BatchStatus]:
        """获取请求状态"""
        if request_id in self.pending_requests:
            return self.pending_requests[request_id].status
        elif request_id in self.completed_requests:
            return self.completed_requests[request_id].status
        return None
    
    def get_request_result(self, request_id: str) -> Any:
        """获取请求结果"""
        if request_id in self.pending_requests:
            return self.pending_requests[request_id].result
        elif request_id in self.completed_requests:
            return self.completed_requests[request_id].result
        return None
    
    def wait_for_completion(self, request_id: str, timeout: float = None) -> bool:
        """等待请求完成"""
        # 检查是否已完成
        if request_id in self.completed_requests:
            return self.completed_requests[request_id].status == BatchStatus.COMPLETED
        
        # 检查是否在待处理列表中
        if request_id not in self.pending_requests:
            return False
        
        request = self.pending_requests[request_id]
        start_time = time.time()
        
        while request.status == BatchStatus.PENDING or request.status == BatchStatus.PROCESSING:
            if timeout and (time.time() - start_time) > timeout:
                return False
            time.sleep(0.1)
        
        return request.status == BatchStatus.COMPLETED
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "pending_requests": len(self.pending_requests),
            "queue_size": self.request_queue.qsize(),
            "active_workers": len([t for t in self.worker_threads if t.is_alive()])
        }
    
    def shutdown(self, wait: bool = True):
        """关闭批处理器"""
        self.shutdown_event.set()
        
        if wait:
            # 等待所有工作线程完成
            for worker in self.worker_threads:
                worker.join(timeout=5.0)
        
        self.executor.shutdown(wait=wait)


# 全局批处理器实例
_batch_processor = None

def get_batch_processor() -> BatchProcessor:
    """获取批处理器实例"""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor

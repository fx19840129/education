"""
事件总线
实现发布-订阅模式，支持同步和异步事件处理
"""

import asyncio
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Type, Union
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum

from .events import BaseEvent, EventType
from .event_handlers import EventHandler, AsyncEventHandler, EventHandlerRegistry


class EventBusMode(Enum):
    """事件总线模式"""
    SYNC = "sync"      # 同步模式
    ASYNC = "async"    # 异步模式
    MIXED = "mixed"    # 混合模式


@dataclass
class EventBusConfig:
    """事件总线配置"""
    mode: EventBusMode = EventBusMode.MIXED
    max_workers: int = 10
    queue_size: int = 1000
    enable_logging: bool = True
    enable_metrics: bool = True
    retry_failed_handlers: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0


class EventBus:
    """
    事件总线
    支持同步和异步事件处理，提供发布-订阅模式
    """
    
    def __init__(self, config: EventBusConfig = None):
        self.config = config or EventBusConfig()
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self.async_handlers: Dict[EventType, List[AsyncEventHandler]] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self.event_queue = asyncio.Queue(maxsize=self.config.queue_size)
        self.lock = threading.RLock()
        self.running = False
        self.metrics = {
            "events_published": 0,
            "events_processed": 0,
            "handlers_executed": 0,
            "handlers_failed": 0,
            "average_processing_time": 0.0
        }
    
    def subscribe(self, event_type: EventType, handler: Union[EventHandler, AsyncEventHandler, Callable],
                  priority: int = 0, filter_func: Optional[Callable[[BaseEvent], bool]] = None) -> 'EventBus':
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理器
            priority: 优先级（数字越小优先级越高）
            filter_func: 过滤函数
        """
        with self.lock:
            if asyncio.iscoroutinefunction(handler):
                # 异步处理器
                if event_type not in self.async_handlers:
                    self.async_handlers[event_type] = []
                
                if isinstance(handler, AsyncEventHandler):
                    async_handler = handler
                else:
                    async_handler = AsyncEventHandler(
                        handler=handler,
                        priority=priority,
                        filter_func=filter_func
                    )
                
                self.async_handlers[event_type].append(async_handler)
                # 按优先级排序
                self.async_handlers[event_type].sort(key=lambda h: h.priority)
            else:
                # 同步处理器
                if event_type not in self.handlers:
                    self.handlers[event_type] = []
                
                if isinstance(handler, EventHandler):
                    sync_handler = handler
                else:
                    sync_handler = EventHandler(
                        handler=handler,
                        priority=priority,
                        filter_func=filter_func
                    )
                
                self.handlers[event_type].append(sync_handler)
                # 按优先级排序
                self.handlers[event_type].sort(key=lambda h: h.priority)
        
        return self
    
    def unsubscribe(self, event_type: EventType, handler: Union[EventHandler, AsyncEventHandler, Callable]) -> bool:
        """
        取消订阅事件
        
        Args:
            event_type: 事件类型
            handler: 事件处理器
            
        Returns:
            是否成功取消订阅
        """
        with self.lock:
            removed = False
            
            # 从同步处理器中移除
            if event_type in self.handlers:
                for i, sync_handler in enumerate(self.handlers[event_type]):
                    if (sync_handler.handler == handler or 
                        (isinstance(handler, EventHandler) and sync_handler == handler)):
                        self.handlers[event_type].pop(i)
                        removed = True
                        break
            
            # 从异步处理器中移除
            if event_type in self.async_handlers:
                for i, async_handler in enumerate(self.async_handlers[event_type]):
                    if (async_handler.handler == handler or 
                        (isinstance(handler, AsyncEventHandler) and async_handler == handler)):
                        self.async_handlers[event_type].pop(i)
                        removed = True
                        break
            
            return removed
    
    def publish(self, event: BaseEvent) -> bool:
        """
        发布事件
        
        Args:
            event: 事件对象
            
        Returns:
            是否成功发布
        """
        try:
            with self.lock:
                self.metrics["events_published"] += 1
            
            if self.config.mode == EventBusMode.SYNC:
                return self._publish_sync(event)
            elif self.config.mode == EventBusMode.ASYNC:
                return self._publish_async(event)
            else:  # MIXED
                return self._publish_mixed(event)
        except Exception as e:
            print(f"发布事件失败: {e}")
            return False
    
    def _publish_sync(self, event: BaseEvent) -> bool:
        """同步发布事件"""
        event_type = event.event_type
        
        # 处理同步处理器
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                if handler.filter_func and not handler.filter_func(event):
                    continue
                
                try:
                    start_time = time.time()
                    handler.handle(event)
                    processing_time = time.time() - start_time
                    
                    with self.lock:
                        self.metrics["handlers_executed"] += 1
                        self._update_average_processing_time(processing_time)
                except Exception as e:
                    with self.lock:
                        self.metrics["handlers_failed"] += 1
                    print(f"同步处理器执行失败: {e}")
                    if self.config.retry_failed_handlers:
                        self._retry_handler(handler, event)
        
        # 处理异步处理器（在同步模式下也同步执行）
        if event_type in self.async_handlers:
            for handler in self.async_handlers[event_type]:
                if handler.filter_func and not handler.filter_func(event):
                    continue
                
                try:
                    start_time = time.time()
                    asyncio.run(handler.handle(event))
                    processing_time = time.time() - start_time
                    
                    with self.lock:
                        self.metrics["handlers_executed"] += 1
                        self._update_average_processing_time(processing_time)
                except Exception as e:
                    with self.lock:
                        self.metrics["handlers_failed"] += 1
                    print(f"异步处理器执行失败: {e}")
                    if self.config.retry_failed_handlers:
                        self._retry_handler(handler, event)
        
        with self.lock:
            self.metrics["events_processed"] += 1
        
        return True
    
    def _publish_async(self, event: BaseEvent) -> bool:
        """异步发布事件"""
        try:
            # 在混合模式下，直接处理异步处理器
            event_type = event.event_type
            
            if event_type in self.async_handlers:
                for handler in self.async_handlers[event_type]:
                    if handler.filter_func and not handler.filter_func(event):
                        continue
                    
                    # 在新的事件循环中运行
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(handler.handle(event))
                        loop.close()
                    except Exception as e:
                        print(f"异步处理器执行失败: {e}")
            
            with self.lock:
                self.metrics["events_processed"] += 1
            
            return True
        except Exception as e:
            print(f"异步发布事件失败: {e}")
            return False
    
    def _publish_mixed(self, event: BaseEvent) -> bool:
        """混合模式发布事件"""
        event_type = event.event_type
        
        # 同步处理器同步执行
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                if handler.filter_func and not handler.filter_func(event):
                    continue
                
                try:
                    start_time = time.time()
                    handler.handle(event)
                    processing_time = time.time() - start_time
                    
                    with self.lock:
                        self.metrics["handlers_executed"] += 1
                        self._update_average_processing_time(processing_time)
                except Exception as e:
                    with self.lock:
                        self.metrics["handlers_failed"] += 1
                    print(f"同步处理器执行失败: {e}")
        
        # 异步处理器同步执行（在测试环境中）
        if event_type in self.async_handlers:
            for handler in self.async_handlers[event_type]:
                if handler.filter_func and not handler.filter_func(event):
                    continue
                
                try:
                    start_time = time.time()
                    # 在新的事件循环中运行异步处理器
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(handler.handle(event))
                    loop.close()
                    processing_time = time.time() - start_time
                    
                    with self.lock:
                        self.metrics["handlers_executed"] += 1
                        self._update_average_processing_time(processing_time)
                except Exception as e:
                    with self.lock:
                        self.metrics["handlers_failed"] += 1
                    print(f"异步处理器执行失败: {e}")
        
        with self.lock:
            self.metrics["events_processed"] += 1
        
        return True
    
    async def _execute_async_handler(self, handler: AsyncEventHandler, event: BaseEvent):
        """执行异步处理器"""
        try:
            start_time = time.time()
            await handler.handle(event)
            processing_time = time.time() - start_time
            
            with self.lock:
                self.metrics["handlers_executed"] += 1
                self._update_average_processing_time(processing_time)
        except Exception as e:
            with self.lock:
                self.metrics["handlers_failed"] += 1
            print(f"异步处理器执行失败: {e}")
            if self.config.retry_failed_handlers:
                await self._retry_async_handler(handler, event)
    
    def _retry_handler(self, handler: Union[EventHandler, AsyncEventHandler], event: BaseEvent):
        """重试处理器"""
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.retry_delay * (attempt + 1))
                if isinstance(handler, EventHandler):
                    handler.handle(event)
                else:
                    asyncio.run(handler.handle(event))
                break
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    print(f"处理器重试失败: {e}")
    
    async def _retry_async_handler(self, handler: AsyncEventHandler, event: BaseEvent):
        """重试异步处理器"""
        for attempt in range(self.config.max_retries):
            try:
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                await handler.handle(event)
                break
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    print(f"异步处理器重试失败: {e}")
    
    def _update_average_processing_time(self, processing_time: float):
        """更新平均处理时间"""
        total_handlers = self.metrics["handlers_executed"]
        if total_handlers > 0:
            self.metrics["average_processing_time"] = (
                (self.metrics["average_processing_time"] * (total_handlers - 1) + processing_time) / total_handlers
            )
        else:
            self.metrics["average_processing_time"] = processing_time
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        with self.lock:
            return self.metrics.copy()
    
    def get_subscribers(self, event_type: EventType) -> Dict[str, List[str]]:
        """获取订阅者信息"""
        with self.lock:
            subscribers = {
                "sync_handlers": [],
                "async_handlers": []
            }
            
            if event_type in self.handlers:
                subscribers["sync_handlers"] = [h.handler.__name__ for h in self.handlers[event_type]]
            
            if event_type in self.async_handlers:
                subscribers["async_handlers"] = [h.handler.__name__ for h in self.async_handlers[event_type]]
            
            return subscribers
    
    def clear_subscribers(self, event_type: EventType = None):
        """清空订阅者"""
        with self.lock:
            if event_type is None:
                self.handlers.clear()
                self.async_handlers.clear()
            else:
                if event_type in self.handlers:
                    del self.handlers[event_type]
                if event_type in self.async_handlers:
                    del self.async_handlers[event_type]
    
    def shutdown(self):
        """关闭事件总线"""
        self.running = False
        self.executor.shutdown(wait=True)


# 全局事件总线实例
_global_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """获取全局事件总线"""
    return _global_event_bus


def publish_event(event: BaseEvent) -> bool:
    """发布事件（全局）"""
    return _global_event_bus.publish(event)


def subscribe_event(event_type: EventType, handler: Union[EventHandler, AsyncEventHandler, Callable],
                   priority: int = 0, filter_func: Optional[Callable[[BaseEvent], bool]] = None) -> EventBus:
    """订阅事件（全局）"""
    return _global_event_bus.subscribe(event_type, handler, priority, filter_func)

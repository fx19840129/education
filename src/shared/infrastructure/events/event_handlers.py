"""
事件处理器
定义事件处理器的基类和注册机制
"""

import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field

from .events import BaseEvent, EventType


@dataclass
class EventHandler:
    """同步事件处理器"""
    handler: Callable[[BaseEvent], Any]
    priority: int = 0
    filter_func: Optional[Callable[[BaseEvent], bool]] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def handle(self, event: BaseEvent) -> Any:
        """处理事件"""
        if not self.enabled:
            return None
        
        if self.filter_func and not self.filter_func(event):
            return None
        
        return self.handler(event)


@dataclass
class AsyncEventHandler:
    """异步事件处理器"""
    handler: Callable[[BaseEvent], Any]
    priority: int = 0
    filter_func: Optional[Callable[[BaseEvent], bool]] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    async def handle(self, event: BaseEvent) -> Any:
        """处理事件"""
        if not self.enabled:
            return None
        
        if self.filter_func and not self.filter_func(event):
            return None
        
        if asyncio.iscoroutinefunction(self.handler):
            return await self.handler(event)
        else:
            return self.handler(event)


class BaseEventHandler(ABC):
    """事件处理器基类"""
    
    def __init__(self, priority: int = 0, enabled: bool = True):
        self.priority = priority
        self.enabled = enabled
        self.metadata = {}
    
    @abstractmethod
    def can_handle(self, event: BaseEvent) -> bool:
        """判断是否能处理事件"""
        pass
    
    @abstractmethod
    def handle(self, event: BaseEvent) -> Any:
        """处理事件"""
        pass


class BaseAsyncEventHandler(ABC):
    """异步事件处理器基类"""
    
    def __init__(self, priority: int = 0, enabled: bool = True):
        self.priority = priority
        self.enabled = enabled
        self.metadata = {}
    
    @abstractmethod
    def can_handle(self, event: BaseEvent) -> bool:
        """判断是否能处理事件"""
        pass
    
    @abstractmethod
    async def handle(self, event: BaseEvent) -> Any:
        """处理事件"""
        pass


class EventHandlerRegistry:
    """事件处理器注册表"""
    
    def __init__(self):
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self.async_handlers: Dict[EventType, List[AsyncEventHandler]] = {}
        self.lock = threading.RLock()
    
    def register_handler(self, event_type: EventType, handler: Union[EventHandler, BaseEventHandler],
                        priority: int = 0) -> 'EventHandlerRegistry':
        """注册同步处理器"""
        with self.lock:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            
            if isinstance(handler, EventHandler):
                event_handler = handler
            elif isinstance(handler, BaseEventHandler):
                event_handler = EventHandler(
                    handler=handler.handle,
                    priority=priority or handler.priority,
                    enabled=handler.enabled,
                    metadata=handler.metadata
                )
            else:
                event_handler = EventHandler(handler=handler, priority=priority)
            
            self.handlers[event_type].append(event_handler)
            # 按优先级排序
            self.handlers[event_type].sort(key=lambda h: h.priority)
        
        return self
    
    def register_async_handler(self, event_type: EventType, handler: Union[AsyncEventHandler, BaseAsyncEventHandler],
                              priority: int = 0) -> 'EventHandlerRegistry':
        """注册异步处理器"""
        with self.lock:
            if event_type not in self.async_handlers:
                self.async_handlers[event_type] = []
            
            if isinstance(handler, AsyncEventHandler):
                event_handler = handler
            elif isinstance(handler, BaseAsyncEventHandler):
                event_handler = AsyncEventHandler(
                    handler=handler.handle,
                    priority=priority or handler.priority,
                    enabled=handler.enabled,
                    metadata=handler.metadata
                )
            else:
                event_handler = AsyncEventHandler(handler=handler, priority=priority)
            
            self.async_handlers[event_type].append(event_handler)
            # 按优先级排序
            self.async_handlers[event_type].sort(key=lambda h: h.priority)
        
        return self
    
    def unregister_handler(self, event_type: EventType, handler: Union[EventHandler, BaseEventHandler]) -> bool:
        """取消注册同步处理器"""
        with self.lock:
            if event_type not in self.handlers:
                return False
            
            for i, h in enumerate(self.handlers[event_type]):
                if (h.handler == handler or 
                    (isinstance(handler, BaseEventHandler) and h.handler == handler.handle)):
                    self.handlers[event_type].pop(i)
                    return True
            
            return False
    
    def unregister_async_handler(self, event_type: EventType, handler: Union[AsyncEventHandler, BaseAsyncEventHandler]) -> bool:
        """取消注册异步处理器"""
        with self.lock:
            if event_type not in self.async_handlers:
                return False
            
            for i, h in enumerate(self.async_handlers[event_type]):
                if (h.handler == handler or 
                    (isinstance(handler, BaseAsyncEventHandler) and h.handler == handler.handle)):
                    self.async_handlers[event_type].pop(i)
                    return True
            
            return False
    
    def get_handlers(self, event_type: EventType) -> List[EventHandler]:
        """获取同步处理器"""
        with self.lock:
            return self.handlers.get(event_type, []).copy()
    
    def get_async_handlers(self, event_type: EventType) -> List[AsyncEventHandler]:
        """获取异步处理器"""
        with self.lock:
            return self.async_handlers.get(event_type, []).copy()
    
    def get_all_handlers(self) -> Dict[EventType, Dict[str, List]]:
        """获取所有处理器"""
        with self.lock:
            result = {}
            for event_type in EventType:
                result[event_type] = {
                    "sync_handlers": [h.handler.__name__ for h in self.handlers.get(event_type, [])],
                    "async_handlers": [h.handler.__name__ for h in self.async_handlers.get(event_type, [])]
                }
            return result
    
    def clear_handlers(self, event_type: EventType = None):
        """清空处理器"""
        with self.lock:
            if event_type is None:
                self.handlers.clear()
                self.async_handlers.clear()
            else:
                if event_type in self.handlers:
                    del self.handlers[event_type]
                if event_type in self.async_handlers:
                    del self.async_handlers[event_type]


# 装饰器支持
def event_handler(event_type: EventType, priority: int = 0, enabled: bool = True):
    """事件处理器装饰器"""
    def decorator(func: Callable[[BaseEvent], Any]) -> Callable[[BaseEvent], Any]:
        func._event_type = event_type
        func._priority = priority
        func._enabled = enabled
        return func
    return decorator


def async_event_handler(event_type: EventType, priority: int = 0, enabled: bool = True):
    """异步事件处理器装饰器"""
    def decorator(func: Callable[[BaseEvent], Any]) -> Callable[[BaseEvent], Any]:
        func._event_type = event_type
        func._priority = priority
        func._enabled = enabled
        return func
    return decorator


# 全局注册表实例
_global_registry = EventHandlerRegistry()


def get_handler_registry() -> EventHandlerRegistry:
    """获取全局处理器注册表"""
    return _global_registry


def register_handler(event_type: EventType, handler: Union[EventHandler, BaseEventHandler],
                    priority: int = 0) -> EventHandlerRegistry:
    """注册处理器（全局）"""
    return _global_registry.register_handler(event_type, handler, priority)


def register_async_handler(event_type: EventType, handler: Union[AsyncEventHandler, BaseAsyncEventHandler],
                          priority: int = 0) -> EventHandlerRegistry:
    """注册异步处理器（全局）"""
    return _global_registry.register_async_handler(event_type, handler, priority)


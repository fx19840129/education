"""
服务定位器
提供统一的服务获取和管理
"""

import threading
from typing import Any, Dict, Type, Optional, Callable, TypeVar
from ..di.container import DIContainer, get_container

T = TypeVar('T')
from ..di.interfaces import (
    IAIClient, IDataProcessor, IDocumentGenerator, IContentGenerator,
    IProgressTracker, ICacheManager, IConfigManager
)


class ServiceLocator:
    """
    服务定位器
    提供统一的服务获取接口，支持服务注册和解析
    """
    
    def __init__(self, container: DIContainer = None):
        self.container = container or get_container()
        self._lock = threading.RLock()
        self._service_cache: Dict[Type, Any] = {}
        self._service_factories: Dict[Type, Callable] = {}
    
    def register_service(self, service_type: Type, factory: Callable[[], Any] = None, 
                        instance: Any = None, cache: bool = True) -> 'ServiceLocator':
        """
        注册服务
        
        Args:
            service_type: 服务类型
            factory: 服务工厂函数
            instance: 服务实例
            cache: 是否缓存实例
        """
        with self._lock:
            if instance is not None:
                self._service_cache[service_type] = instance
            elif factory is not None:
                self._service_factories[service_type] = factory
            else:
                # 如果没有提供工厂或实例，创建一个默认工厂
                def default_factory():
                    return service_type()
                self._service_factories[service_type] = default_factory
            
            return self
    
    def get_service(self, service_type: Type[T]) -> T:
        """
        获取服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例
        """
        with self._lock:
            # 首先尝试从缓存获取
            if service_type in self._service_cache:
                return self._service_cache[service_type]
            
            # 尝试从工厂创建
            if service_type in self._service_factories:
                instance = self._service_factories[service_type]()
                if self._should_cache(service_type):
                    self._service_cache[service_type] = instance
                return instance
            
            # 尝试从DI容器解析
            try:
                instance = self.container.resolve(service_type)
                if self._should_cache(service_type):
                    self._service_cache[service_type] = instance
                return instance
            except (ValueError, RuntimeError):
                pass
            
            # 尝试直接实例化
            try:
                instance = service_type()
                if self._should_cache(service_type):
                    self._service_cache[service_type] = instance
                return instance
            except Exception as e:
                raise RuntimeError(f"Failed to create service {service_type}: {e}")
    
    def _should_cache(self, service_type: Type) -> bool:
        """判断是否应该缓存服务"""
        # 对于单例服务，应该缓存
        if self.container.is_registered(service_type):
            descriptor = self.container.get_registered_services()[service_type]
            return descriptor.lifetime.value == "singleton"
        
        # 默认不缓存
        return False
    
    def has_service(self, service_type: Type) -> bool:
        """检查是否有服务"""
        with self._lock:
            return (service_type in self._service_cache or 
                   service_type in self._service_factories or
                   self.container.is_registered(service_type))
    
    def remove_service(self, service_type: Type) -> bool:
        """移除服务"""
        with self._lock:
            removed = False
            
            if service_type in self._service_cache:
                del self._service_cache[service_type]
                removed = True
            
            if service_type in self._service_factories:
                del self._service_factories[service_type]
                removed = True
            
            return removed
    
    def clear_cache(self):
        """清空缓存"""
        with self._lock:
            self._service_cache.clear()
    
    def get_cached_services(self) -> Dict[Type, Any]:
        """获取缓存的服务"""
        return self._service_cache.copy()
    
    def get_registered_services(self) -> Dict[Type, Any]:
        """获取已注册的服务类型"""
        with self._lock:
            services = {}
            services.update(self._service_cache)
            services.update(self._service_factories)
            
            # 添加DI容器中的服务
            for service_type in self.container.get_registered_services():
                services[service_type] = f"DI: {service_type.__name__}"
            
            return services


# 便捷方法
def get_service_locator() -> ServiceLocator:
    """获取全局服务定位器"""
    return _global_locator


def get_service(service_type: Type[T]) -> T:
    """获取服务（全局）"""
    return _global_locator.get_service(service_type)


def register_service(service_type: Type, factory: Callable[[], Any] = None, 
                    instance: Any = None, cache: bool = True) -> ServiceLocator:
    """注册服务（全局）"""
    return _global_locator.register_service(service_type, factory, instance, cache)


# 全局服务定位器实例
_global_locator = ServiceLocator()


# 预定义的服务获取方法
def get_ai_client() -> IAIClient:
    """获取AI客户端"""
    return get_service(IAIClient)


def get_data_processor() -> IDataProcessor:
    """获取数据处理器"""
    return get_service(IDataProcessor)


def get_document_generator() -> IDocumentGenerator:
    """获取文档生成器"""
    return get_service(IDocumentGenerator)


def get_content_generator() -> IContentGenerator:
    """获取内容生成器"""
    return get_service(IContentGenerator)


def get_progress_tracker() -> IProgressTracker:
    """获取进度跟踪器"""
    return get_service(IProgressTracker)


def get_cache_manager() -> ICacheManager:
    """获取缓存管理器"""
    return get_service(ICacheManager)


def get_config_manager() -> IConfigManager:
    """获取配置管理器"""
    return get_service(IConfigManager)

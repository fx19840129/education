"""
依赖注入容器
提供服务的注册、解析和生命周期管理
"""

import threading
import inspect
from typing import Any, Dict, Type, Callable, Optional, Union, TypeVar
from enum import Enum
from dataclasses import dataclass

T = TypeVar('T')


class ServiceLifetime(Enum):
    """服务生命周期"""
    SINGLETON = "singleton"      # 单例
    TRANSIENT = "transient"      # 瞬态
    SCOPED = "scoped"           # 作用域


@dataclass
class ServiceDescriptor:
    """服务描述符"""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    dependencies: Optional[Dict[str, Type]] = None


class DIContainer:
    """
    依赖注入容器
    支持构造函数注入、属性注入和方法注入
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._lock = threading.RLock()
        self._current_scope = None
    
    def register_singleton(self, service_type: Type[T], implementation_type: Type[T] = None, 
                          factory: Callable[[], T] = None) -> 'DIContainer':
        """注册单例服务"""
        return self._register_service(service_type, implementation_type, factory, ServiceLifetime.SINGLETON)
    
    def register_transient(self, service_type: Type[T], implementation_type: Type[T] = None,
                          factory: Callable[[], T] = None) -> 'DIContainer':
        """注册瞬态服务"""
        return self._register_service(service_type, implementation_type, factory, ServiceLifetime.TRANSIENT)
    
    def register_scoped(self, service_type: Type[T], implementation_type: Type[T] = None,
                       factory: Callable[[], T] = None) -> 'DIContainer':
        """注册作用域服务"""
        return self._register_service(service_type, implementation_type, factory, ServiceLifetime.SCOPED)
    
    def _register_service(self, service_type: Type[T], implementation_type: Type[T] = None,
                         factory: Callable[[], T] = None, lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT) -> 'DIContainer':
        """注册服务"""
        with self._lock:
            if implementation_type is None and factory is None:
                implementation_type = service_type
            
            dependencies = self._analyze_dependencies(implementation_type or service_type)
            
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=implementation_type,
                factory=factory,
                lifetime=lifetime,
                dependencies=dependencies
            )
            
            self._services[service_type] = descriptor
            return self
    
    def _analyze_dependencies(self, service_type: Type) -> Dict[str, Type]:
        """分析服务依赖"""
        dependencies = {}
        
        try:
            signature = inspect.signature(service_type.__init__)
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    dependencies[param_name] = param.annotation
        except (ValueError, TypeError):
            # 无法分析构造函数，返回空依赖
            pass
        
        return dependencies
    
    def resolve(self, service_type: Type[T]) -> T:
        """解析服务"""
        with self._lock:
            if service_type not in self._services:
                raise ValueError(f"Service {service_type} not registered")
            
            descriptor = self._services[service_type]
            
            # 检查生命周期
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                if descriptor.instance is None:
                    descriptor.instance = self._create_instance(descriptor)
                return descriptor.instance
            
            elif descriptor.lifetime == ServiceLifetime.SCOPED:
                if self._current_scope is None:
                    # 如果没有活动作用域，创建瞬态实例
                    return self._create_instance(descriptor)
                
                # 使用当前作用域的实例
                if service_type not in self._current_scope._scoped_instances:
                    self._current_scope._scoped_instances[service_type] = self._create_instance(descriptor)
                return self._current_scope._scoped_instances[service_type]
            
            else:  # TRANSIENT
                return self._create_instance(descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """创建服务实例"""
        if descriptor.factory:
            return descriptor.factory()
        
        implementation_type = descriptor.implementation_type or descriptor.service_type
        
        # 解析依赖
        dependencies = {}
        if descriptor.dependencies:
            for dep_name, dep_type in descriptor.dependencies.items():
                dependencies[dep_name] = self.resolve(dep_type)
        
        # 创建实例
        try:
            return implementation_type(**dependencies)
        except Exception as e:
            raise RuntimeError(f"Failed to create instance of {implementation_type}: {e}")
    
    def create_scope(self) -> 'DIScope':
        """创建作用域"""
        return DIScope(self)
    
    def is_registered(self, service_type: Type) -> bool:
        """检查服务是否已注册"""
        return service_type in self._services
    
    def get_registered_services(self) -> Dict[Type, ServiceDescriptor]:
        """获取已注册的服务"""
        return self._services.copy()
    
    def clear(self):
        """清空容器"""
        with self._lock:
            self._services.clear()
            self._scoped_instances.clear()
            self._current_scope = None


class DIScope:
    """依赖注入作用域"""
    
    def __init__(self, container: DIContainer):
        self.container = container
        self._previous_scope = container._current_scope
        self._scoped_instances = {}  # 每个作用域维护自己的实例
    
    def __enter__(self):
        with self.container._lock:
            self.container._current_scope = self
            # 不清空现有实例，让每个作用域维护自己的实例
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.container._lock:
            self.container._current_scope = self._previous_scope
            # 不清空实例，让作用域自然结束


# 全局容器实例
_container = DIContainer()


def get_container() -> DIContainer:
    """获取全局容器实例"""
    return _container


def register_singleton(service_type: Type[T], implementation_type: Type[T] = None,
                      factory: Callable[[], T] = None) -> DIContainer:
    """注册单例服务（全局）"""
    return _container.register_singleton(service_type, implementation_type, factory)


def register_transient(service_type: Type[T], implementation_type: Type[T] = None,
                      factory: Callable[[], T] = None) -> DIContainer:
    """注册瞬态服务（全局）"""
    return _container.register_transient(service_type, implementation_type, factory)


def register_scoped(service_type: Type[T], implementation_type: Type[T] = None,
                   factory: Callable[[], T] = None) -> DIContainer:
    """注册作用域服务（全局）"""
    return _container.register_scoped(service_type, implementation_type, factory)


def resolve(service_type: Type[T]) -> T:
    """解析服务（全局）"""
    return _container.resolve(service_type)

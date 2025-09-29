"""
依赖注入装饰器
提供便捷的装饰器来标记和注册服务
"""

import functools
from typing import Type, Callable, Any
from .container import get_container, ServiceLifetime


def injectable(service_type: Type = None, lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
    """
    可注入装饰器
    标记类为可注入的服务
    
    Args:
        service_type: 服务类型，默认为被装饰的类
        lifetime: 服务生命周期
    """
    def decorator(cls: Type) -> Type:
        container = get_container()
        target_type = service_type or cls
        
        if lifetime == ServiceLifetime.SINGLETON:
            container.register_singleton(target_type, cls)
        elif lifetime == ServiceLifetime.SCOPED:
            container.register_scoped(target_type, cls)
        else:  # TRANSIENT
            container.register_transient(target_type, cls)
        
        return cls
    
    return decorator


def singleton(service_type: Type = None):
    """
    单例装饰器
    将类注册为单例服务
    """
    return injectable(service_type, ServiceLifetime.SINGLETON)


def transient(service_type: Type = None):
    """
    瞬态装饰器
    将类注册为瞬态服务
    """
    return injectable(service_type, ServiceLifetime.TRANSIENT)


def scoped(service_type: Type = None):
    """
    作用域装饰器
    将类注册为作用域服务
    """
    return injectable(service_type, ServiceLifetime.SCOPED)


def inject(service_type: Type):
    """
    注入装饰器
    用于方法参数注入
    
    Args:
        service_type: 要注入的服务类型
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            container = get_container()
            service_instance = container.resolve(service_type)
            
            # 将服务实例作为关键字参数注入
            kwargs[service_type.__name__.lower()] = service_instance
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def auto_inject(func: Callable) -> Callable:
    """
    自动注入装饰器
    自动解析函数参数中标注了类型的依赖
    """
    import inspect
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        container = get_container()
        signature = inspect.signature(func)
        
        # 获取函数参数
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # 检查每个参数是否有类型注解
        for param_name, param in signature.parameters.items():
            if param_name in bound_args.arguments:
                continue  # 参数已提供
            
            if param.annotation != inspect.Parameter.empty:
                try:
                    # 尝试解析依赖
                    service_instance = container.resolve(param.annotation)
                    bound_args.arguments[param_name] = service_instance
                except (ValueError, RuntimeError):
                    # 无法解析依赖，跳过
                    pass
        
        return func(*bound_args.args, **bound_args.kwargs)
    
    return wrapper


class ServiceProvider:
    """服务提供者基类"""
    
    def __init__(self, container=None):
        self.container = container or get_container()
    
    def get_service(self, service_type: Type) -> Any:
        """获取服务实例"""
        return self.container.resolve(service_type)
    
    def create_scope(self):
        """创建作用域"""
        return self.container.create_scope()


def service_provider(container=None):
    """
    服务提供者装饰器
    为类添加服务提供者功能
    """
    def decorator(cls: Type) -> Type:
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self._service_provider = ServiceProvider(container)
        
        cls.__init__ = new_init
        
        # 添加服务提供者方法
        cls.get_service = lambda self, service_type: self._service_provider.get_service(service_type)
        cls.create_scope = lambda self: self._service_provider.create_scope()
        
        return cls
    
    return decorator


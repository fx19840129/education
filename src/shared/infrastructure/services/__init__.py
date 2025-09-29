"""
服务管理模块
提供服务定位器、工厂模式和统一的服务管理
"""

from .service_locator import ServiceLocator, get_service_locator
from .factories import (
    AIClientFactory,
    DataProcessorFactory,
    DocumentGeneratorFactory,
    ContentGeneratorFactory,
    ProgressTrackerFactory,
    CacheManagerFactory,
    ConfigManagerFactory
)

__all__ = [
    'ServiceLocator',
    'get_service_locator',
    'AIClientFactory',
    'DataProcessorFactory', 
    'DocumentGeneratorFactory',
    'ContentGeneratorFactory',
    'ProgressTrackerFactory',
    'CacheManagerFactory',
    'ConfigManagerFactory'
]


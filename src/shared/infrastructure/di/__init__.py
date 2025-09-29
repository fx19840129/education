"""
依赖注入模块
提供依赖注入容器、接口抽象和装饰器支持
"""

from .container import DIContainer, ServiceLifetime
from .interfaces import (
    IAIClient,
    IDataProcessor, 
    IDocumentGenerator,
    IContentGenerator,
    IProgressTracker,
    ICacheManager,
    IConfigManager
)
from .decorators import injectable, singleton, transient, scoped

__all__ = [
    'DIContainer',
    'ServiceLifetime',
    'IAIClient',
    'IDataProcessor',
    'IDocumentGenerator', 
    'IContentGenerator',
    'IProgressTracker',
    'ICacheManager',
    'IConfigManager',
    'injectable',
    'singleton',
    'transient',
    'scoped'
]


"""
插件化架构模块
提供插件管理、动态加载和插件接口
"""

from .plugin_manager import PluginManager, get_plugin_manager
from .plugin_interface import (
    BasePlugin,
    PluginType,
    PluginStatus,
    ContentGeneratorPlugin,
    AIClientPlugin,
    DataProcessorPlugin,
    DocumentGeneratorPlugin
)
from .plugin_loader import PluginLoader
from .plugin_interface import PluginInfo

__all__ = [
    'PluginManager',
    'get_plugin_manager',
    'BasePlugin',
    'PluginType',
    'PluginStatus',
    'ContentGeneratorPlugin',
    'AIClientPlugin', 
    'DataProcessorPlugin',
    'DocumentGeneratorPlugin',
    'PluginLoader',
    'PluginInfo'
]

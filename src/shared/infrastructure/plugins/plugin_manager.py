"""
插件管理器
提供插件的注册、加载、激活、停用和卸载功能
"""

import os
import sys
import importlib
import threading
from typing import Any, Dict, List, Optional, Type, Union
from pathlib import Path

from .plugin_interface import BasePlugin, PluginInfo, PluginType, PluginStatus
from .plugin_loader import PluginLoader


class PluginManager:
    """
    插件管理器
    负责插件的生命周期管理和服务提供
    """
    
    def __init__(self, plugin_dirs: List[str] = None):
        self.plugin_dirs = plugin_dirs or ["plugins"]
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.loader = PluginLoader()
        self.lock = threading.RLock()
        self.initialized = False
    
    def initialize(self) -> bool:
        """初始化插件管理器"""
        with self.lock:
            if self.initialized:
                return True
            
            try:
                # 扫描插件目录
                self._scan_plugin_directories()
                self.initialized = True
                return True
            except Exception as e:
                print(f"插件管理器初始化失败: {e}")
                return False
    
    def _scan_plugin_directories(self):
        """扫描插件目录"""
        for plugin_dir in self.plugin_dirs:
            if os.path.exists(plugin_dir):
                self._load_plugins_from_directory(plugin_dir)
    
    def _load_plugins_from_directory(self, directory: str):
        """从目录加载插件"""
        plugin_path = Path(directory)
        
        for item in plugin_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                # 目录形式的插件
                self._load_plugin_from_path(str(item))
            elif item.is_file() and item.suffix == ".py":
                # 文件形式的插件
                self._load_plugin_from_path(str(item))
    
    def _load_plugin_from_path(self, plugin_path: str):
        """从路径加载插件"""
        try:
            plugin_info = self.loader.load_plugin(plugin_path)
            if plugin_info:
                self._register_plugin(plugin_info)
        except Exception as e:
            print(f"加载插件失败 {plugin_path}: {e}")
    
    def _register_plugin(self, plugin_info: PluginInfo):
        """注册插件信息"""
        with self.lock:
            self.plugin_info[plugin_info.name] = plugin_info
    
    def load_plugin(self, plugin_class: Type[BasePlugin], config: Dict[str, Any] = None) -> bool:
        """加载插件"""
        with self.lock:
            try:
                plugin_instance = plugin_class(config or {})
                plugin_info = plugin_instance.get_info()
                
                # 检查依赖
                if not self._check_dependencies(plugin_info.dependencies):
                    print(f"插件 {plugin_info.name} 依赖不满足")
                    return False
                
                # 初始化插件
                if not plugin_instance.initialize():
                    print(f"插件 {plugin_info.name} 初始化失败")
                    return False
                
                self.plugins[plugin_info.name] = plugin_instance
                self.plugin_info[plugin_info.name] = plugin_info
                
                print(f"插件 {plugin_info.name} 加载成功")
                return True
                
            except Exception as e:
                print(f"加载插件失败: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        with self.lock:
            if plugin_name not in self.plugins:
                return False
            
            try:
                plugin = self.plugins[plugin_name]
                
                # 停用插件
                if plugin.status == PluginStatus.ACTIVE:
                    plugin.deactivate()
                
                # 清理插件
                plugin.cleanup()
                
                # 移除插件
                del self.plugins[plugin_name]
                if plugin_name in self.plugin_info:
                    del self.plugin_info[plugin_name]
                
                print(f"插件 {plugin_name} 卸载成功")
                return True
                
            except Exception as e:
                print(f"卸载插件失败: {e}")
                return False
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """激活插件"""
        with self.lock:
            if plugin_name not in self.plugins:
                return False
            
            plugin = self.plugins[plugin_name]
            
            if plugin.status == PluginStatus.ACTIVE:
                return True
            
            try:
                if plugin.activate():
                    print(f"插件 {plugin_name} 激活成功")
                    return True
                else:
                    print(f"插件 {plugin_name} 激活失败")
                    return False
            except Exception as e:
                print(f"激活插件失败: {e}")
                return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """停用插件"""
        with self.lock:
            if plugin_name not in self.plugins:
                return False
            
            plugin = self.plugins[plugin_name]
            
            if plugin.status != PluginStatus.ACTIVE:
                return True
            
            try:
                if plugin.deactivate():
                    print(f"插件 {plugin_name} 停用成功")
                    return True
                else:
                    print(f"插件 {plugin_name} 停用失败")
                    return False
            except Exception as e:
                print(f"停用插件失败: {e}")
                return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        with self.lock:
            return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """根据类型获取插件"""
        with self.lock:
            result = []
            for plugin in self.plugins.values():
                if plugin.get_info().plugin_type == plugin_type:
                    result.append(plugin)
            return result
    
    def get_active_plugins(self) -> List[BasePlugin]:
        """获取活跃的插件"""
        with self.lock:
            return [plugin for plugin in self.plugins.values() 
                   if plugin.status == PluginStatus.ACTIVE]
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        with self.lock:
            return self.plugin_info.get(plugin_name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """列出所有插件"""
        with self.lock:
            return list(self.plugin_info.values())
    
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """检查依赖是否满足"""
        for dep in dependencies:
            if dep not in self.plugins:
                return False
        return True
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """重新加载插件"""
        with self.lock:
            if plugin_name not in self.plugins:
                return False
            
            # 先卸载
            if not self.unload_plugin(plugin_name):
                return False
            
            # 重新加载（这里需要重新获取插件类，实际实现会更复杂）
            # 简化实现，假设插件类可以重新获取
            return True
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """获取插件统计信息"""
        with self.lock:
            stats = {
                "total_plugins": len(self.plugins),
                "active_plugins": len(self.get_active_plugins()),
                "plugin_types": {},
                "status_counts": {}
            }
            
            for plugin in self.plugins.values():
                info = plugin.get_info()
                
                # 统计插件类型
                plugin_type = info.plugin_type.value
                stats["plugin_types"][plugin_type] = stats["plugin_types"].get(plugin_type, 0) + 1
                
                # 统计状态
                status = plugin.status.value
                stats["status_counts"][status] = stats["status_counts"].get(status, 0) + 1
            
            return stats
    
    def shutdown(self):
        """关闭插件管理器"""
        with self.lock:
            # 停用所有插件
            for plugin_name in list(self.plugins.keys()):
                self.deactivate_plugin(plugin_name)
                self.unload_plugin(plugin_name)
            
            self.plugins.clear()
            self.plugin_info.clear()
            self.initialized = False


# 全局插件管理器实例
_global_plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器"""
    return _global_plugin_manager


def load_plugin(plugin_class: Type[BasePlugin], config: Dict[str, Any] = None) -> bool:
    """加载插件（全局）"""
    return _global_plugin_manager.load_plugin(plugin_class, config)


def get_plugin(plugin_name: str) -> Optional[BasePlugin]:
    """获取插件（全局）"""
    return _global_plugin_manager.get_plugin(plugin_name)


def activate_plugin(plugin_name: str) -> bool:
    """激活插件（全局）"""
    return _global_plugin_manager.activate_plugin(plugin_name)


def deactivate_plugin(plugin_name: str) -> bool:
    """停用插件（全局）"""
    return _global_plugin_manager.deactivate_plugin(plugin_name)

"""
插件加载器
负责从文件系统加载插件并解析插件信息
"""

import os
import sys
import importlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from .plugin_interface import BasePlugin, PluginInfo, PluginType


class PluginLoader:
    """插件加载器"""
    
    def __init__(self):
        self.loaded_modules: Dict[str, Any] = {}
        self.plugin_metadata_cache: Dict[str, Dict[str, Any]] = {}
    
    def load_plugin(self, plugin_path: str) -> Optional[PluginInfo]:
        """
        加载插件
        
        Args:
            plugin_path: 插件路径（文件或目录）
            
        Returns:
            插件信息，如果加载失败返回None
        """
        try:
            plugin_path = Path(plugin_path)
            
            if plugin_path.is_file():
                return self._load_plugin_from_file(plugin_path)
            elif plugin_path.is_dir():
                return self._load_plugin_from_directory(plugin_path)
            else:
                print(f"无效的插件路径: {plugin_path}")
                return None
                
        except Exception as e:
            print(f"加载插件失败 {plugin_path}: {e}")
            return None
    
    def _load_plugin_from_file(self, plugin_file: Path) -> Optional[PluginInfo]:
        """从文件加载插件"""
        try:
            # 加载模块
            module_name = plugin_file.stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if spec is None:
                print(f"无法创建模块规范: {plugin_file}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                print(f"未找到插件类: {plugin_file}")
                return None
            
            # 创建插件实例获取信息
            plugin_instance = plugin_class()
            plugin_info = plugin_instance.get_info()
            
            # 缓存模块
            self.loaded_modules[plugin_info.name] = module
            
            return plugin_info
            
        except Exception as e:
            print(f"从文件加载插件失败 {plugin_file}: {e}")
            return None
    
    def _load_plugin_from_directory(self, plugin_dir: Path) -> Optional[PluginInfo]:
        """从目录加载插件"""
        try:
            # 查找插件入口文件
            entry_files = ["__init__.py", "main.py", "plugin.py"]
            entry_file = None
            
            for file_name in entry_files:
                file_path = plugin_dir / file_name
                if file_path.exists():
                    entry_file = file_path
                    break
            
            if entry_file is None:
                print(f"未找到插件入口文件: {plugin_dir}")
                return None
            
            # 检查是否有插件元数据文件
            metadata_file = plugin_dir / "plugin.json"
            metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except Exception as e:
                    print(f"读取插件元数据失败: {e}")
            
            # 加载模块
            module_name = plugin_dir.name
            spec = importlib.util.spec_from_file_location(module_name, entry_file)
            if spec is None:
                print(f"无法创建模块规范: {entry_file}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                print(f"未找到插件类: {plugin_dir}")
                return None
            
            # 创建插件实例获取信息
            plugin_instance = plugin_class()
            plugin_info = plugin_instance.get_info()
            
            # 合并元数据
            if metadata:
                plugin_info.metadata.update(metadata)
            
            # 缓存模块
            self.loaded_modules[plugin_info.name] = module
            
            return plugin_info
            
        except Exception as e:
            print(f"从目录加载插件失败 {plugin_dir}: {e}")
            return None
    
    def _find_plugin_class(self, module: Any) -> Optional[Type[BasePlugin]]:
        """查找插件类"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # 检查是否是BasePlugin的子类
            if (isinstance(attr, type) and 
                issubclass(attr, BasePlugin) and 
                attr != BasePlugin):
                return attr
        
        return None
    
    def get_plugin_class(self, plugin_name: str) -> Optional[Type[BasePlugin]]:
        """获取插件类"""
        if plugin_name not in self.loaded_modules:
            return None
        
        module = self.loaded_modules[plugin_name]
        return self._find_plugin_class(module)
    
    def create_plugin_instance(self, plugin_name: str, config: Dict[str, Any] = None) -> Optional[BasePlugin]:
        """创建插件实例"""
        plugin_class = self.get_plugin_class(plugin_name)
        if plugin_class is None:
            return None
        
        try:
            return plugin_class(config or {})
        except Exception as e:
            print(f"创建插件实例失败 {plugin_name}: {e}")
            return None
    
    def scan_plugin_directory(self, directory: str) -> List[PluginInfo]:
        """扫描插件目录"""
        plugin_infos = []
        plugin_dir = Path(directory)
        
        if not plugin_dir.exists():
            return plugin_infos
        
        for item in plugin_dir.iterdir():
            if item.is_file() and item.suffix == ".py":
                # Python文件
                plugin_info = self.load_plugin(str(item))
                if plugin_info:
                    plugin_infos.append(plugin_info)
            elif item.is_dir() and (item / "__init__.py").exists():
                # Python包
                plugin_info = self.load_plugin(str(item))
                if plugin_info:
                    plugin_infos.append(plugin_info)
        
        return plugin_infos
    
    def get_loaded_modules(self) -> Dict[str, Any]:
        """获取已加载的模块"""
        return self.loaded_modules.copy()
    
    def unload_module(self, module_name: str) -> bool:
        """卸载模块"""
        if module_name in self.loaded_modules:
            del self.loaded_modules[module_name]
            if module_name in sys.modules:
                del sys.modules[module_name]
            return True
        return False
    
    def clear_cache(self):
        """清空缓存"""
        self.loaded_modules.clear()
        self.plugin_metadata_cache.clear()


def create_plugin_metadata(plugin_info: PluginInfo, output_path: str) -> bool:
    """创建插件元数据文件"""
    try:
        metadata = {
            "name": plugin_info.name,
            "version": plugin_info.version,
            "description": plugin_info.description,
            "author": plugin_info.author,
            "plugin_type": plugin_info.plugin_type.value,
            "dependencies": plugin_info.dependencies,
            "config_schema": plugin_info.config_schema,
            "metadata": plugin_info.metadata
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"创建插件元数据文件失败: {e}")
        return False


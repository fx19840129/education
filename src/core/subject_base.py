#!/usr/bin/env python3
"""
学科基类定义
定义所有学科的通用接口和基础功能
"""

import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SubjectFunction:
    """学科功能配置"""
    name: str
    display_name: str
    description: str
    script_path: Optional[str] = None
    function_type: str = "script"  # script, menu, builtin
    enabled: bool = True

class SubjectBase(ABC):
    """学科基类"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.name = self.get_name()
        self.display_name = self.get_display_name()
        self.description = self.get_description()
        self.functions = self.initialize_functions()
    
    @abstractmethod
    def get_name(self) -> str:
        """获取学科名称"""
        pass
    
    @abstractmethod
    def get_display_name(self) -> str:
        """获取学科显示名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取学科描述"""
        pass
    
    @abstractmethod
    def initialize_functions(self) -> List[SubjectFunction]:
        """初始化学科功能列表"""
        pass
    
    def is_available(self) -> bool:
        """检查学科是否可用"""
        return any(func.enabled for func in self.functions)
    
    def get_enabled_functions(self) -> List[SubjectFunction]:
        """获取启用的功能列表"""
        return [func for func in self.functions if func.enabled]
    
    def execute_function(self, function_name: str, **kwargs) -> str:
        """执行学科功能"""
        # 处理通用的内置功能
        if function_name in ["back", "exit"]:
            return self._run_builtin(function_name, **kwargs)
        
        function = next((f for f in self.functions if f.name == function_name), None)
        if not function:
            raise ValueError(f"功能不存在: {function_name}")
        
        if not function.enabled:
            raise ValueError(f"功能已禁用: {function_name}")
        
        if function.function_type == "script":
            return self._run_script(function.script_path)
        elif function.function_type == "menu":
            return self._show_menu(function_name, **kwargs)
        elif function.function_type == "builtin":
            return self._run_builtin(function_name, **kwargs)
        else:
            raise ValueError(f"未知功能类型: {function.function_type}")
    
    def _run_script(self, script_path: str) -> str:
        """运行脚本"""
        if not script_path:
            return "error"
        
        print(f"\n🚀 启动 {script_path}...")
        print("-" * 50)
        
        script_full_path = self.project_root / script_path
        if not script_full_path.exists():
            print(f"❌ 脚本文件不存在: {script_full_path}")
            input("\n按Enter键继续...")
            return "error"
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_full_path)],
                cwd=str(self.project_root),
                check=False
            )
            
            if result.returncode == 0:
                print(f"\n✅ 操作完成!")
            else:
                print(f"\n⚠️  脚本执行完成，返回码: {result.returncode}")
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  用户中断操作")
        except Exception as e:
            print(f"\n❌ 运行脚本时出错: {e}")
        
        input("\n按Enter键继续...")
        return "continue"
    
    def _show_menu(self, function_name: str, **kwargs) -> str:
        """显示子菜单"""
        # 子类可以重写此方法来实现自定义菜单
        print(f"\n🚧 {function_name} 功能正在开发中...")
        input("\n按Enter键继续...")
        return "continue"
    
    def _run_builtin(self, function_name: str, **kwargs) -> str:
        """运行内置功能"""
        # 处理通用的内置功能
        if function_name == "back":
            return "back"
        elif function_name == "exit":
            return "exit"
        
        # 子类可以重写此方法来实现自定义内置功能
        print(f"\n🚧 {function_name} 功能正在开发中...")
        input("\n按Enter键继续...")
        return "continue"
    
    def display_functions_menu(self) -> List[Tuple[str, str]]:
        """显示功能菜单并返回功能映射"""
        print(f"\n{self.display_name} - 功能选择")
        print("=" * 60)
        
        enabled_functions = self.get_enabled_functions()
        function_map = []
        
        for i, function in enumerate(enabled_functions, 1):
            print(f"{i}. {function.display_name}")
            print(f"   {function.description}")
            function_map.append((function.name, function.function_type))
        
        # 添加通用选项
        print(f"{len(enabled_functions) + 1}. 🔙 返回学科选择")
        function_map.append(("back", "builtin"))
        
        print(f"{len(enabled_functions) + 2}. ❌ 退出系统")
        function_map.append(("exit", "builtin"))
        
        print("=" * 60)
        
        return function_map

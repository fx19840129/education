#!/usr/bin/env python3
"""
英语学科实现
包含英语学习的所有功能配置和特定实现
"""

import sys
from pathlib import Path
from typing import List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.subject_base import SubjectBase, SubjectFunction

class EnglishSubject(SubjectBase):
    """英语学科实现"""
    
    def get_name(self) -> str:
        return "english"
    
    def get_display_name(self) -> str:
        return "🇺🇸 英语学习"
    
    def get_description(self) -> str:
        return "英语词汇、语法、练习等学习内容"
    
    def initialize_functions(self) -> List[SubjectFunction]:
        """初始化英语学科功能"""
        return [
            SubjectFunction(
                name="create_plan",
                display_name="📋 创建学习计划",
                description="生成个性化的学习计划和FSRS模板",
                script_path="src/english/core/create_learning_plan.py",
                function_type="script"
            ),
            SubjectFunction(
                name="manage_plan",
                display_name="🗂️  管理学习计划",
                description="查看、搜索、删除、导出已有计划",
                script_path="src/english/core/manage_learning_plan.py",
                function_type="script"
            ),
            SubjectFunction(
                name="generate_content",
                display_name="📚 生成学习内容",
                description="生成每日学习内容（词汇、句子、练习、Word文档）",
                script_path="src/english/content_generators/daily_content_generator.py",
                function_type="script"
            )
        ]
    
    def _show_menu(self, function_name: str, **kwargs) -> str:
        """显示英语学科的自定义菜单"""
        return super()._show_menu(function_name, **kwargs)

#!/usr/bin/env python3
"""
学科管理器
负责加载和管理所有学科模块
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.subject_base import SubjectBase

class SubjectManager:
    """学科管理器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.subjects: Dict[str, SubjectBase] = {}
        self._load_subjects()
    
    def _load_subjects(self):
        """加载所有学科"""
        subject_configs = [
            ("english", "src.subjects.english_subject", "EnglishSubject"),
            ("chinese", "src.subjects.chinese_subject", "ChineseSubject"),
            ("math", "src.subjects.math_subject", "MathSubject"),
            # 可以继续添加其他学科
        ]
        
        for subject_name, module_path, class_name in subject_configs:
            try:
                # 动态导入学科模块
                module = importlib.import_module(module_path)
                subject_class = getattr(module, class_name)
                
                # 创建学科实例
                subject_instance = subject_class(self.project_root)
                self.subjects[subject_name] = subject_instance
                
                print(f"✅ 已加载学科: {subject_instance.display_name}")
            
            except Exception as e:
                print(f"⚠️  加载学科 {subject_name} 失败: {e}")
    
    def get_available_subjects(self) -> List[SubjectBase]:
        """获取可用的学科列表"""
        return [subject for subject in self.subjects.values() if subject.is_available()]
    
    def get_all_subjects(self) -> List[SubjectBase]:
        """获取所有学科列表"""
        return list(self.subjects.values())
    
    def get_subject(self, subject_name: str) -> SubjectBase:
        """根据名称获取学科"""
        return self.subjects.get(subject_name)
    
    def display_subjects_menu(self) -> List[str]:
        """显示学科选择菜单"""
        print("\n📖 请选择学科:")
        print("-" * 50)
        
        available_subjects = self.get_available_subjects()
        subject_names = []
        
        # 显示可用学科
        for i, subject in enumerate(available_subjects, 1):
            print(f"{i}. {subject.display_name}")
            print(f"   📝 {subject.description}")
            subject_names.append(subject.name)
        
        # 显示未开发的学科
        all_subjects = self.get_all_subjects()
        unavailable_subjects = [s for s in all_subjects if not s.is_available()]
        
        if unavailable_subjects:
            print(f"\n🚧 即将推出的学科:")
            for subject in unavailable_subjects:
                print(f"   {subject.display_name} - {subject.description}")
        
        print(f"\n{len(available_subjects) + 1}. ❌ 退出系统")
        print("-" * 50)
        
        return subject_names

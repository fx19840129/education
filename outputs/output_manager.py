#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出路径管理器
统一管理各科目的输出路径配置
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class OutputManager:
    """输出路径管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化输出管理器
        
        Args:
            config_path: 配置文件路径，默认为当前目录下的config.json
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载输出配置失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "output_paths": {
                "english": {
                    "learning_plans": "outputs/english/learning_plans",
                    "custom_plans": "outputs/english/custom_plans",
                    "word_plans": "outputs/english/word_plans",
                    "grammar_plans": "outputs/english/grammar_plans",
                    "reports": "outputs/english/reports",
                    "exports": "outputs/english/exports",
                    "word_learning_details": "outputs/english/word_learning_details"
                }
            },
            "default_subject": "english"
        }
    
    def get_output_path(self, subject: str, output_type: str) -> str:
        """
        获取指定科目和类型的输出路径
        
        Args:
            subject: 科目名称 (e.g., "english", "math")
            output_type: 输出类型 (e.g., "learning_plans", "custom_plans")
            
        Returns:
            str: 输出路径
        """
        try:
            path = self.config["output_paths"][subject][output_type]
            
            # 如果是相对路径，转换为绝对路径（相对于项目根目录）
            if not os.path.isabs(path):
                # 获取项目根目录（outputs目录的父目录）
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                path = os.path.join(project_root, path)
            
            # 确保路径存在
            os.makedirs(path, exist_ok=True)
            return path
        except KeyError:
            # 如果配置中不存在，使用默认路径
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            default_path = os.path.join(project_root, f"outputs/{subject}/{output_type}")
            os.makedirs(default_path, exist_ok=True)
            return default_path
    
    def get_english_paths(self) -> Dict[str, str]:
        """获取英语科目的所有输出路径"""
        return self.config["output_paths"].get("english", {})
    
    def get_subject_paths(self, subject: str) -> Dict[str, str]:
        """获取指定科目的所有输出路径"""
        return self.config["output_paths"].get(subject, {})
    
    def create_subject_structure(self, subject: str):
        """为指定科目创建输出目录结构"""
        subject_paths = self.get_subject_paths(subject)
        for output_type, path in subject_paths.items():
            os.makedirs(path, exist_ok=True)
            print(f"✅ 创建目录: {path}")
    
    def list_all_paths(self) -> Dict[str, Dict[str, str]]:
        """列出所有科目的输出路径"""
        return self.config["output_paths"]
    
    def add_subject(self, subject: str, paths: Dict[str, str]):
        """
        添加新科目的输出路径配置
        
        Args:
            subject: 科目名称
            paths: 输出路径字典
        """
        if "output_paths" not in self.config:
            self.config["output_paths"] = {}
        
        self.config["output_paths"][subject] = paths
        self._save_config()
    
    def update_path(self, subject: str, output_type: str, new_path: str):
        """
        更新指定科目和类型的输出路径
        
        Args:
            subject: 科目名称
            output_type: 输出类型
            new_path: 新路径
        """
        if "output_paths" not in self.config:
            self.config["output_paths"] = {}
        
        if subject not in self.config["output_paths"]:
            self.config["output_paths"][subject] = {}
        
        self.config["output_paths"][subject][output_type] = new_path
        self._save_config()
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
    
    def migrate_existing_files(self, old_path: str, new_path: str, subject: str, output_type: str):
        """
        迁移现有文件到新路径
        
        Args:
            old_path: 旧路径
            new_path: 新路径
            subject: 科目名称
            output_type: 输出类型
        """
        if not os.path.exists(old_path):
            print(f"⚠️ 旧路径不存在: {old_path}")
            return
        
        # 确保新路径存在
        os.makedirs(new_path, exist_ok=True)
        
        # 迁移文件
        import shutil
        try:
            for item in os.listdir(old_path):
                old_item_path = os.path.join(old_path, item)
                new_item_path = os.path.join(new_path, item)
                
                if os.path.isfile(old_item_path):
                    shutil.copy2(old_item_path, new_item_path)
                    print(f"📁 迁移文件: {item}")
                elif os.path.isdir(old_item_path):
                    shutil.copytree(old_item_path, new_item_path, dirs_exist_ok=True)
                    print(f"📁 迁移目录: {item}")
            
            print(f"✅ 迁移完成: {old_path} -> {new_path}")
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")


# 便捷函数
def get_output_path(subject: str, output_type: str) -> str:
    """获取输出路径的便捷函数"""
    manager = OutputManager()
    return manager.get_output_path(subject, output_type)


def get_english_paths() -> Dict[str, str]:
    """获取英语输出路径的便捷函数"""
    manager = OutputManager()
    return manager.get_english_paths()


# 使用示例
if __name__ == "__main__":
    print("输出路径管理器测试")
    print("=" * 50)
    
    # 创建管理器
    manager = OutputManager()
    
    # 获取英语输出路径
    english_paths = manager.get_english_paths()
    print("英语输出路径:")
    for output_type, path in english_paths.items():
        print(f"  {output_type}: {path}")
    
    # 获取特定路径
    learning_plans_path = manager.get_output_path("english", "learning_plans")
    print(f"\n学习计划路径: {learning_plans_path}")
    
    # 列出所有路径
    all_paths = manager.list_all_paths()
    print(f"\n所有科目路径:")
    for subject, paths in all_paths.items():
        print(f"  {subject}:")
        for output_type, path in paths.items():
            print(f"    {output_type}: {path}")
    
    print("\n✅ 输出路径管理器测试完成")

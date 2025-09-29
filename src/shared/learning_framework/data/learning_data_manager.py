#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习数据管理器
统一管理多学科的学习数据，支持按学习计划组织
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from pathlib import Path

class LearningDataManager:
    """学习数据管理器"""
    
    def __init__(self, project_root: str = None):
        """初始化学习数据管理器"""
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        
        self.project_root = Path(project_root)
        self.learning_data_dir = self.project_root / "learning_data"
        self.main_data_file = self.learning_data_dir / "learning_progress.json"
        self.fsrs_data_file = self.learning_data_dir / "fsrs_memory.json"
        
        # 确保目录存在
        self.learning_data_dir.mkdir(exist_ok=True)
        
        # 加载主数据文件
        self._load_main_data()
    
    def _load_main_data(self):
        """加载主学习数据文件"""
        try:
            if self.main_data_file.exists():
                with open(self.main_data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = self._create_default_data()
        except Exception as e:
            print(f"⚠️ 加载学习数据失败: {e}")
            self.data = self._create_default_data()
    
    def _create_default_data(self) -> Dict[str, Any]:
        """创建默认的学习数据结构"""
        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "2.0",
                "description": "按学习计划组织的多学科学习数据"
            },
            "subjects": {},
            "fsrs_memory": {},
            "shared": {
                "total_learned_items": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def get_subject_data(self, subject: str) -> Dict[str, Any]:
        """获取指定学科的学习数据"""
        return self.data.get("subjects", {}).get(subject, {})
    
    def get_learned_words(self, subject: str, plan: str = None) -> List[str]:
        """获取已学单词列表"""
        subject_data = self.get_subject_data(subject)
        
        if plan:
            # 按学习计划获取
            plans = subject_data.get("learning_plans", {})
            plan_data = plans.get(plan, {})
            return plan_data.get("learned_words", [])
        else:
            # 获取所有已学单词
            return subject_data.get("learned_words", [])
    
    def add_learned_word(self, subject: str, word: str, plan: str = None):
        """添加已学单词"""
        if not self.data.get("subjects"):
            self.data["subjects"] = {}
        
        if subject not in self.data["subjects"]:
            self.data["subjects"][subject] = {
                "learned_words": [],
                "total_words": 0,
                "learning_plans": {}
            }
        
        subject_data = self.data["subjects"][subject]
        
        # 添加到总列表
        if word not in subject_data.get("learned_words", []):
            subject_data.setdefault("learned_words", []).append(word)
            subject_data["total_words"] = len(subject_data["learned_words"])
        
        # 如果指定了学习计划，也添加到计划中
        if plan:
            if "learning_plans" not in subject_data:
                subject_data["learning_plans"] = {}
            
            if plan not in subject_data["learning_plans"]:
                subject_data["learning_plans"][plan] = {
                    "name": f"{subject} {plan} 学习计划",
                    "learned_words": [],
                    "target_words": [],
                    "progress": 0.0
                }
            
            plan_data = subject_data["learning_plans"][plan]
            if word not in plan_data.get("learned_words", []):
                plan_data.setdefault("learned_words", []).append(word)
                # 更新进度
                total_target = len(plan_data.get("target_words", []))
                if total_target > 0:
                    plan_data["progress"] = len(plan_data["learned_words"]) / total_target
        
        # 更新共享统计
        self._update_shared_stats()
    
    def get_fsrs_memory(self) -> Dict[str, Any]:
        """获取FSRS内存数据"""
        try:
            if self.fsrs_data_file.exists():
                with open(self.fsrs_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载FSRS数据失败: {e}")
        return {}
    
    def save_fsrs_memory(self, fsrs_data: Dict[str, Any]):
        """保存FSRS内存数据"""
        try:
            with open(self.fsrs_data_file, 'w', encoding='utf-8') as f:
                json.dump(fsrs_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存FSRS数据失败: {e}")
    
    def _update_shared_stats(self):
        """更新共享统计信息"""
        total_learned = 0
        for subject_data in self.data.get("subjects", {}).values():
            total_learned += len(subject_data.get("learned_words", []))
        
        self.data["shared"]["total_learned_items"] = total_learned
        self.data["shared"]["last_updated"] = datetime.now().isoformat()
    
    def save_data(self):
        """保存学习数据"""
        try:
            # 保存主数据文件
            with open(self.main_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # 保存各学科的数据文件
            for subject, subject_data in self.data.get("subjects", {}).items():
                subject_file = self.learning_data_dir / subject / "learning_progress.json"
                subject_file.parent.mkdir(exist_ok=True)
                
                with open(subject_file, 'w', encoding='utf-8') as f:
                    json.dump(subject_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"⚠️ 保存学习数据失败: {e}")
            return False
    
    def get_learning_plan_progress(self, subject: str, plan: str) -> Dict[str, Any]:
        """获取学习计划进度"""
        subject_data = self.get_subject_data(subject)
        plans = subject_data.get("learning_plans", {})
        plan_data = plans.get(plan, {})
        
        learned_count = len(plan_data.get("learned_words", []))
        target_count = len(plan_data.get("target_words", []))
        progress = plan_data.get("progress", 0.0)
        
        return {
            "plan_name": plan_data.get("name", f"{subject} {plan} 学习计划"),
            "learned_count": learned_count,
            "target_count": target_count,
            "progress": progress,
            "learned_words": plan_data.get("learned_words", []),
            "target_words": plan_data.get("target_words", [])
        }
    
    def set_learning_plan_targets(self, subject: str, plan: str, target_words: List[str]):
        """设置学习计划目标单词"""
        if not self.data.get("subjects"):
            self.data["subjects"] = {}
        
        if subject not in self.data["subjects"]:
            self.data["subjects"][subject] = {
                "learned_words": [],
                "total_words": 0,
                "learning_plans": {}
            }
        
        subject_data = self.data["subjects"][subject]
        
        if "learning_plans" not in subject_data:
            subject_data["learning_plans"] = {}
        
        if plan not in subject_data["learning_plans"]:
            subject_data["learning_plans"][plan] = {
                "name": f"{subject} {plan} 学习计划",
                "learned_words": [],
                "target_words": [],
                "progress": 0.0
            }
        
        plan_data = subject_data["learning_plans"][plan]
        plan_data["target_words"] = target_words
        
        # 更新进度
        learned_count = len(plan_data.get("learned_words", []))
        if len(target_words) > 0:
            plan_data["progress"] = learned_count / len(target_words)
    
    def get_subject_summary(self, subject: str) -> Dict[str, Any]:
        """获取学科学习摘要"""
        subject_data = self.get_subject_data(subject)
        
        total_learned = len(subject_data.get("learned_words", []))
        plans = subject_data.get("learning_plans", {})
        
        plan_summaries = {}
        for plan_name, plan_data in plans.items():
            plan_summaries[plan_name] = {
                "name": plan_data.get("name", f"{subject} {plan_name} 学习计划"),
                "learned_count": len(plan_data.get("learned_words", [])),
                "target_count": len(plan_data.get("target_words", [])),
                "progress": plan_data.get("progress", 0.0)
            }
        
        return {
            "subject": subject,
            "total_learned": total_learned,
            "plans": plan_summaries,
            "last_updated": subject_data.get("last_updated", "")
        }

# 全局实例
_learning_data_manager = None

def get_learning_data_manager() -> LearningDataManager:
    """获取学习数据管理器实例（单例模式）"""
    global _learning_data_manager
    if _learning_data_manager is None:
        _learning_data_manager = LearningDataManager()
    return _learning_data_manager

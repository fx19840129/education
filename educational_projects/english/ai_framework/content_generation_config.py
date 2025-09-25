#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI内容生成配置管理系统
支持保守、平衡、创新三种生成模式
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class GenerationMode(Enum):
    """内容生成模式"""
    CONSERVATIVE = "conservative"    # 保守模式：纯模板生成
    BALANCED = "balanced"           # 平衡模式：模板+AI优化
    INNOVATIVE = "innovative"       # 创新模式：AI主导生成

@dataclass
class GenerationConfig:
    """生成配置"""
    mode: GenerationMode
    temperature: float
    max_tokens: int
    use_cache: bool
    cache_ttl: int  # 缓存存活时间（秒）
    quality_threshold: float  # 质量阈值
    fallback_to_template: bool  # 是否允许降级到模板
    
    # AI增强比例（平衡模式用）
    ai_enhancement_ratio: float = 0.5
    
    # 个性化参数
    personalization_enabled: bool = True
    fsrs_integration: bool = True
    user_preference_weight: float = 0.3

@dataclass
class ContentTypeConfig:
    """内容类型配置"""
    sentences: GenerationConfig
    exercises: GenerationConfig
    explanations: GenerationConfig

class ContentGenerationConfigManager:
    """内容生成配置管理器"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), 'configs')
        
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        
        # 默认配置
        self.default_configs = self._create_default_configs()
        
        # 当前配置
        self.current_config = "balanced"  # 默认值
        self.current_config = self._load_or_create_config()
    
    def _create_default_configs(self) -> Dict[str, ContentTypeConfig]:
        """创建默认配置"""
        configs = {}
        
        # 保守模式配置
        conservative_sentence = GenerationConfig(
            mode=GenerationMode.CONSERVATIVE,
            temperature=0.0,
            max_tokens=100,
            use_cache=True,
            cache_ttl=86400,  # 24小时
            quality_threshold=0.0,  # 不需要质量检查
            fallback_to_template=False,  # 已经是模板模式
            ai_enhancement_ratio=0.0,
            personalization_enabled=False,
            fsrs_integration=True
        )
        
        conservative_exercise = GenerationConfig(
            mode=GenerationMode.CONSERVATIVE,
            temperature=0.0,
            max_tokens=200,
            use_cache=True,
            cache_ttl=86400,
            quality_threshold=0.0,
            fallback_to_template=False,
            ai_enhancement_ratio=0.0,
            personalization_enabled=False,
            fsrs_integration=True
        )
        
        conservative_explanation = GenerationConfig(
            mode=GenerationMode.CONSERVATIVE,
            temperature=0.0,
            max_tokens=150,
            use_cache=True,
            cache_ttl=86400,
            quality_threshold=0.0,
            fallback_to_template=False,
            ai_enhancement_ratio=0.0,
            personalization_enabled=False,
            fsrs_integration=False
        )
        
        configs["conservative"] = ContentTypeConfig(
            sentences=conservative_sentence,
            exercises=conservative_exercise,
            explanations=conservative_explanation
        )
        
        # 平衡模式配置
        balanced_sentence = GenerationConfig(
            mode=GenerationMode.BALANCED,
            temperature=0.5,
            max_tokens=150,
            use_cache=True,
            cache_ttl=3600,  # 1小时
            quality_threshold=0.7,
            fallback_to_template=True,
            ai_enhancement_ratio=0.5,
            personalization_enabled=True,
            fsrs_integration=True
        )
        
        balanced_exercise = GenerationConfig(
            mode=GenerationMode.BALANCED,
            temperature=0.6,
            max_tokens=300,
            use_cache=True,
            cache_ttl=3600,
            quality_threshold=0.8,
            fallback_to_template=True,
            ai_enhancement_ratio=0.6,
            personalization_enabled=True,
            fsrs_integration=True
        )
        
        balanced_explanation = GenerationConfig(
            mode=GenerationMode.BALANCED,
            temperature=0.4,
            max_tokens=250,
            use_cache=True,
            cache_ttl=3600,
            quality_threshold=0.7,
            fallback_to_template=True,
            ai_enhancement_ratio=0.4,
            personalization_enabled=False,
            fsrs_integration=False
        )
        
        configs["balanced"] = ContentTypeConfig(
            sentences=balanced_sentence,
            exercises=balanced_exercise,
            explanations=balanced_explanation
        )
        
        # 创新模式配置
        innovative_sentence = GenerationConfig(
            mode=GenerationMode.INNOVATIVE,
            temperature=0.8,
            max_tokens=200,
            use_cache=True,
            cache_ttl=1800,  # 30分钟
            quality_threshold=0.8,
            fallback_to_template=True,
            ai_enhancement_ratio=1.0,
            personalization_enabled=True,
            fsrs_integration=True
        )
        
        innovative_exercise = GenerationConfig(
            mode=GenerationMode.INNOVATIVE,
            temperature=0.7,
            max_tokens=400,
            use_cache=True,
            cache_ttl=1800,
            quality_threshold=0.8,
            fallback_to_template=True,
            ai_enhancement_ratio=1.0,
            personalization_enabled=True,
            fsrs_integration=True
        )
        
        innovative_explanation = GenerationConfig(
            mode=GenerationMode.INNOVATIVE,
            temperature=0.6,
            max_tokens=300,
            use_cache=True,
            cache_ttl=1800,
            quality_threshold=0.8,
            fallback_to_template=True,
            ai_enhancement_ratio=0.8,
            personalization_enabled=True,
            fsrs_integration=False
        )
        
        configs["innovative"] = ContentTypeConfig(
            sentences=innovative_sentence,
            exercises=innovative_exercise,
            explanations=innovative_explanation
        )
        
        return configs
    
    def _load_or_create_config(self) -> str:
        """加载或创建配置"""
        config_file = os.path.join(self.config_dir, "generation_config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("current_mode", "balanced")
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        # 创建默认配置文件
        self._save_all_configs()
        return "balanced"  # 默认使用平衡模式
    
    def _save_all_configs(self):
        """保存所有配置到文件"""
        config_data = {
            "current_mode": self.current_config,
            "modes": {}
        }
        
        for mode_name, type_config in self.default_configs.items():
            config_data["modes"][mode_name] = {
                "sentences": asdict(type_config.sentences),
                "exercises": asdict(type_config.exercises),
                "explanations": asdict(type_config.explanations)
            }
        
        config_file = os.path.join(self.config_dir, "generation_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"配置保存到: {config_file}")
    
    def get_config(self, content_type: str = "sentences") -> GenerationConfig:
        """
        获取当前配置
        
        Args:
            content_type: 内容类型 (sentences/exercises/explanations)
        """
        mode_config = self.default_configs.get(self.current_config)
        if not mode_config:
            mode_config = self.default_configs["balanced"]
        
        if content_type == "sentences":
            return mode_config.sentences
        elif content_type == "exercises":
            return mode_config.exercises
        elif content_type == "explanations":
            return mode_config.explanations
        else:
            return mode_config.sentences
    
    def set_mode(self, mode: str):
        """设置生成模式"""
        if mode in self.default_configs:
            self.current_config = mode
            self._save_current_mode()
            print(f"生成模式已切换到: {mode}")
        else:
            print(f"未知的生成模式: {mode}")
            print(f"可用模式: {list(self.default_configs.keys())}")
    
    def _save_current_mode(self):
        """保存当前模式"""
        config_file = os.path.join(self.config_dir, "generation_config.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data["current_mode"] = self.current_config
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            except Exception as e:
                print(f"保存模式失败: {e}")
    
    def get_current_mode(self) -> str:
        """获取当前模式"""
        return self.current_config
    
    def list_available_modes(self) -> List[str]:
        """列出可用模式"""
        return list(self.default_configs.keys())
    
    def get_mode_description(self, mode: str) -> str:
        """获取模式描述"""
        descriptions = {
            "conservative": "保守模式 - 使用预定义模板，稳定可靠，响应快速",
            "balanced": "平衡模式 - 模板+AI优化，兼顾质量与多样性（推荐）",
            "innovative": "创新模式 - AI主导生成，最高个性化和创新性"
        }
        return descriptions.get(mode, "未知模式")
    
    def update_config(self, content_type: str, **kwargs):
        """更新特定配置"""
        mode_config = self.default_configs.get(self.current_config)
        if not mode_config:
            return
        
        if content_type == "sentences":
            config_obj = mode_config.sentences
        elif content_type == "exercises":
            config_obj = mode_config.exercises
        elif content_type == "explanations":
            config_obj = mode_config.explanations
        else:
            return
        
        # 更新配置字段
        for key, value in kwargs.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
        
        self._save_all_configs()
    
    def create_user_profile_config(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """根据用户偏好创建个性化配置"""
        base_config = self.get_config()
        
        # 根据用户偏好调整参数
        custom_config = asdict(base_config)
        
        # 学习风格调整
        learning_style = user_preferences.get("learning_style", "balanced")
        if learning_style == "visual":
            custom_config["ai_enhancement_ratio"] *= 1.2  # 更多AI生成的视觉化内容
        elif learning_style == "conservative":
            custom_config["ai_enhancement_ratio"] *= 0.8  # 更倾向模板
        
        # 难度偏好调整
        difficulty_preference = user_preferences.get("difficulty_preference", "medium")
        if difficulty_preference == "challenging":
            custom_config["temperature"] += 0.1
        elif difficulty_preference == "simple":
            custom_config["temperature"] -= 0.1
        
        return custom_config
    
    def print_current_config(self):
        """打印当前配置信息"""
        print(f"\n当前生成模式: {self.current_config}")
        print(f"模式描述: {self.get_mode_description(self.current_config)}")
        print("\n配置详情:")
        
        for content_type in ["sentences", "exercises", "explanations"]:
            config = self.get_config(content_type)
            print(f"\n{content_type.upper()}:")
            print(f"  温度: {config.temperature}")
            print(f"  最大tokens: {config.max_tokens}")
            print(f"  AI增强比例: {config.ai_enhancement_ratio}")
            print(f"  个性化: {config.personalization_enabled}")
            print(f"  FSRS集成: {config.fsrs_integration}")
            print(f"  质量阈值: {config.quality_threshold}")

# 全局配置管理器
config_manager = ContentGenerationConfigManager()

if __name__ == "__main__":
    # 演示配置管理
    manager = ContentGenerationConfigManager()
    
    print("=== AI内容生成配置管理系统 ===")
    print(f"可用模式: {manager.list_available_modes()}")
    
    for mode in manager.list_available_modes():
        print(f"\n{mode}: {manager.get_mode_description(mode)}")
    
    # 显示当前配置
    manager.print_current_config()
    
    # 测试模式切换
    print(f"\n切换到创新模式...")
    manager.set_mode("innovative")
    manager.print_current_config()

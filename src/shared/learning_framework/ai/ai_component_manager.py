#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI组件管理器
提供单例模式的AI组件管理，避免重复初始化
"""

import os
import sys
from typing import Optional

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 从 educational_projects/shared/learning_framework/ai 回到项目根目录
# 需要向上5级: ai -> learning_framework -> shared -> educational_projects -> .. -> ..
project_root = os.path.join(current_dir, '..', '..', '..', '..', '..')
ai_models_path = os.path.join(project_root, 'ai_models')
ai_framework_path = os.path.join(project_root, 'educational_projects', 'shared', 'ai_framework')
ai_components_path = os.path.join(project_root, 'educational_projects', 'shared', 'learning_framework', 'ai')

sys.path.append(os.path.abspath(ai_models_path))
sys.path.append(os.path.abspath(ai_framework_path))
sys.path.append(os.path.abspath(ai_components_path))

class AIComponentManager:
    """AI组件管理器 - 单例模式"""
    
    _instance: Optional['AIComponentManager'] = None
    _ai_sentence_generator: Optional[object] = None
    _ai_content_generator: Optional[object] = None
    _config_loaded: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config_loaded:
            self._load_config()
            self._config_loaded = True
    
    def _load_config(self):
        """加载配置文件"""
        try:
            # 暂时禁用路由器，直接使用AI组件
            # from routers.smart_model_router import SmartModelRouter
            # self.router = SmartModelRouter()
            self.router = None
            print("✅ AI组件管理器配置加载完成（简化模式）")
        except Exception as e:
            print(f"⚠️ AI组件管理器配置加载失败: {e}")
            self.router = None
    
    def get_ai_sentence_generator(self):
        """获取AI句子生成器（延迟初始化）"""
        if self._ai_sentence_generator is None:
            try:
                from .ai_sentence_generator import AISentenceGenerator
                self._ai_sentence_generator = AISentenceGenerator()
                print("✅ AI句子生成器延迟初始化完成")
            except Exception as e:
                print(f"⚠️ AI句子生成器初始化失败: {e}")
                return None
        return self._ai_sentence_generator
    
    def get_ai_content_generator(self):
        """获取AI内容生成器（延迟初始化）"""
        if self._ai_content_generator is None:
            try:
                from .ai_content_generator import AIContentGenerator
                self._ai_content_generator = AIContentGenerator()
                print("✅ AI内容生成器延迟初始化完成")
            except Exception as e:
                print(f"⚠️ AI内容生成器初始化失败: {e}")
                return None
        return self._ai_content_generator
    
    def reset(self):
        """重置所有组件（用于测试）"""
        self._ai_sentence_generator = None
        self._ai_content_generator = None
        self._config_loaded = False

# 全局单例实例
ai_manager = AIComponentManager()

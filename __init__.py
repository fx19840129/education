"""
教育项目 - 多科目学习计划生成系统

这是一个综合性的教育学习计划生成系统，支持多个科目的学习计划创建和管理。
"""

__version__ = "1.0.0"
__author__ = "Education Team"
__email__ = "education@example.com"

# 导入主要模块
from src.english import EnglishLearningMain
from src.shared.learning_framework import LearningFramework

__all__ = [
    "EnglishLearningMain",
    "LearningFramework",
]


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义异常类
"""


class EducationSystemError(Exception):
    """教育系统基础异常"""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class WordDatabaseError(EducationSystemError):
    """单词数据库异常"""
    pass


class GrammarConfigError(EducationSystemError):
    """语法配置异常"""
    pass


class AIGenerationError(EducationSystemError):
    """AI生成异常"""
    pass


class ContentGenerationError(EducationSystemError):
    """内容生成异常"""
    pass


class PlanValidationError(EducationSystemError):
    """计划验证异常"""
    pass


class FileOperationError(EducationSystemError):
    """文件操作异常"""
    pass


class ConfigurationError(EducationSystemError):
    """配置异常"""
    pass


class NetworkError(EducationSystemError):
    """网络异常"""
    pass


class ValidationError(EducationSystemError):
    """验证异常"""
    pass


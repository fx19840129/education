#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一日志系统
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any


class EducationLogger:
    """教育系统日志器"""
    
    def __init__(self, name: str = "education_system", log_level: str = "INFO"):
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 创建日志目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{self.name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # 错误文件处理器
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{self.name}_error.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)
        
        return logger
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, extra=kwargs)
    
    def log_function_call(self, func_name: str, args: tuple = (), kwargs: dict = None):
        """记录函数调用"""
        kwargs = kwargs or {}
        self.debug(f"调用函数: {func_name}, 参数: {args}, 关键字参数: {kwargs}")
    
    def log_performance(self, operation: str, duration: float, **metrics):
        """记录性能指标"""
        self.info(f"性能指标 - 操作: {operation}, 耗时: {duration:.3f}s", **metrics)
    
    def log_ai_call(self, provider: str, model: str, tokens: int, cost: float = None):
        """记录AI调用"""
        log_data = {
            "provider": provider,
            "model": model,
            "tokens": tokens,
            "cost": cost
        }
        self.info(f"AI调用 - 提供商: {provider}, 模型: {model}, Token数: {tokens}", **log_data)


# 全局日志器实例
default_logger = EducationLogger()

def get_logger(name: str = None) -> EducationLogger:
    """获取日志器"""
    if name:
        return EducationLogger(name)
    return default_logger


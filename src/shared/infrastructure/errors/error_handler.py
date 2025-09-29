#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一错误处理器
"""

import logging
import traceback
from typing import Any, Dict, Optional
from functools import wraps

from .exceptions import EducationSystemError


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: str = "", **kwargs) -> Dict[str, Any]:
        """处理错误并返回错误信息"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": self._get_timestamp(),
            **kwargs
        }
        
        # 记录错误日志
        if isinstance(error, EducationSystemError):
            self.logger.error(f"系统错误 [{context}]: {error.message}", extra=error_info)
        else:
            self.logger.error(f"未知错误 [{context}]: {str(error)}", extra=error_info)
            self.logger.debug(f"错误堆栈: {traceback.format_exc()}")
        
        return error_info
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


def handle_exceptions(context: str = "", reraise: bool = True):
    """异常处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except EducationSystemError as e:
                # 系统已知错误，记录并重新抛出
                error_handler = ErrorHandler()
                error_handler.handle_error(e, context)
                if reraise:
                    raise
                return None
            except Exception as e:
                # 未知错误，记录并重新抛出
                error_handler = ErrorHandler()
                error_handler.handle_error(e, context)
                if reraise:
                    raise
                return None
        return wrapper
    return decorator


def safe_execute(func, *args, context: str = "", default_return=None, **kwargs):
    """安全执行函数"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler = ErrorHandler()
        error_handler.handle_error(e, context)
        return default_return


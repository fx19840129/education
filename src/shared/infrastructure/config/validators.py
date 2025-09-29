#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证器
"""

import re
from typing import Any, List
from ..errors.exceptions import ConfigurationError, ValidationError


class ConfigValidator:
    """配置验证器"""
    
    def validate_database_config(self, config) -> None:
        """验证数据库配置"""
        if not config.host:
            raise ValidationError("数据库主机不能为空")
        
        if not (1 <= config.port <= 65535):
            raise ValidationError("数据库端口必须在1-65535之间")
        
        if not config.name:
            raise ValidationError("数据库名称不能为空")
        
        if config.pool_size <= 0:
            raise ValidationError("连接池大小必须大于0")
        
        if config.max_overflow < 0:
            raise ValidationError("最大溢出连接数不能为负数")
    
    def validate_ai_config(self, config) -> None:
        """验证AI配置"""
        if not config.default_provider:
            raise ValidationError("AI默认提供商不能为空")
        
        if not config.default_model:
            raise ValidationError("AI默认模型不能为空")
        
        if config.timeout <= 0:
            raise ValidationError("AI超时时间必须大于0")
        
        if config.max_retries < 0:
            raise ValidationError("AI最大重试次数不能为负数")
        
        if config.rate_limit <= 0:
            raise ValidationError("AI速率限制必须大于0")
        
        if config.cache_ttl <= 0:
            raise ValidationError("AI缓存TTL必须大于0")
    
    def validate_logging_config(self, config) -> None:
        """验证日志配置"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config.level.upper() not in valid_levels:
            raise ValidationError(f"日志级别必须是: {', '.join(valid_levels)}")
        
        if config.max_file_size <= 0:
            raise ValidationError("日志文件最大大小必须大于0")
        
        if config.backup_count < 0:
            raise ValidationError("日志备份数量不能为负数")
    
    def validate_cache_config(self, config) -> None:
        """验证缓存配置"""
        valid_backends = ['memory', 'redis', 'memcached']
        if config.backend not in valid_backends:
            raise ValidationError(f"缓存后端必须是: {', '.join(valid_backends)}")
        
        if config.port <= 0 or config.port > 65535:
            raise ValidationError("缓存端口必须在1-65535之间")
        
        if config.default_ttl <= 0:
            raise ValidationError("缓存默认TTL必须大于0")
        
        if config.max_size <= 0:
            raise ValidationError("缓存最大大小必须大于0")
    
    def validate_security_config(self, config) -> None:
        """验证安全配置"""
        # 在开发环境中允许空密钥
        if config.secret_key and len(config.secret_key) < 32:
            raise ValidationError("安全密钥长度至少32个字符")
        
        if config.jwt_secret and len(config.jwt_secret) < 32:
            raise ValidationError("JWT密钥长度至少32个字符")
        
        if config.jwt_expiry <= 0:
            raise ValidationError("JWT过期时间必须大于0")
        
        if config.rate_limit_per_minute <= 0:
            raise ValidationError("速率限制必须大于0")
        
        # 验证允许的源
        for origin in config.allowed_origins:
            if not self._is_valid_url(origin):
                raise ValidationError(f"无效的允许源: {origin}")
    
    def validate_system_config(self, config) -> None:
        """验证系统配置"""
        if config.max_workers <= 0:
            raise ValidationError("最大工作线程数必须大于0")
        
        if config.metrics_port <= 0 or config.metrics_port > 65535:
            raise ValidationError("指标端口必须在1-65535之间")
        
        # 验证时区
        try:
            import pytz
            pytz.timezone(config.timezone)
        except Exception:
            raise ValidationError(f"无效的时区: {config.timezone}")
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return pattern.match(url) is not None
    
    def validate_api_key(self, api_key: str, provider: str) -> None:
        """验证API密钥"""
        if not api_key:
            raise ValidationError(f"{provider} API密钥不能为空")
        
        # 根据提供商验证密钥格式
        if provider.lower() == 'zhipu':
            if not api_key.startswith('sk-'):
                raise ValidationError("智谱AI API密钥格式不正确")
        elif provider.lower() == 'openai':
            if not api_key.startswith('sk-'):
                raise ValidationError("OpenAI API密钥格式不正确")
        elif provider.lower() == 'anthropic':
            if not api_key.startswith('sk-ant-'):
                raise ValidationError("Anthropic API密钥格式不正确")
    
    def validate_model_name(self, model_name: str, provider: str) -> None:
        """验证模型名称"""
        if not model_name:
            raise ValidationError("模型名称不能为空")
        
        # 根据提供商验证模型名称格式
        if provider.lower() == 'zhipu':
            valid_models = ['glm-4', 'glm-4-flash', 'glm-3-turbo']
            if model_name not in valid_models:
                raise ValidationError(f"无效的智谱AI模型: {model_name}")
        elif provider.lower() == 'openai':
            if not model_name.startswith('gpt-'):
                raise ValidationError("OpenAI模型名称格式不正确")
        elif provider.lower() == 'anthropic':
            if not model_name.startswith('claude-'):
                raise ValidationError("Anthropic模型名称格式不正确")
    
    def validate_learning_plan_config(self, config: dict) -> None:
        """验证学习计划配置"""
        required_fields = ['name', 'duration_days', 'daily_words', 'daily_exercises']
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"学习计划配置缺少必需字段: {field}")
        
        if config['duration_days'] <= 0:
            raise ValidationError("学习计划天数必须大于0")
        
        if config['daily_words'] <= 0:
            raise ValidationError("每日单词数必须大于0")
        
        if config['daily_exercises'] <= 0:
            raise ValidationError("每日练习题数必须大于0")
        
        # 验证难度级别
        valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
        if 'difficulty' in config and config['difficulty'] not in valid_difficulties:
            raise ValidationError(f"难度级别必须是: {', '.join(valid_difficulties)}")
        
        # 验证学习级别
        valid_levels = ['elementary', 'middle_school', 'high_school']
        if 'level' in config and config['level'] not in valid_levels:
            raise ValidationError(f"学习级别必须是: {', '.join(valid_levels)}")

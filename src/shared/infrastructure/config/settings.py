#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理系统
"""

import json
import os
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from .validators import ConfigValidator
from ..errors.exceptions import ConfigurationError


class Environment(Enum):
    """环境类型"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    name: str = "education_db"
    user: str = "education_user"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class AIModelConfig:
    """AI模型配置"""
    name: str = ""
    display_name: str = ""
    max_tokens: int = 8192
    supports_chat: bool = True
    supports_completion: bool = True
    supports_streaming: bool = False
    cost_per_token: float = 0.001
    temperature: float = 0.7
    timeout: int = 60
    description: str = ""

@dataclass
class AIProviderConfig:
    """AI提供商配置"""
    name: str = ""
    base_url: str = ""
    api_key: str = ""
    enabled: bool = True
    priority: int = 1
    models: Dict[str, AIModelConfig] = field(default_factory=dict)

@dataclass
class AIScenarioConfig:
    """AI场景配置"""
    name: str = ""
    description: str = ""
    preferred_models: List[str] = field(default_factory=list)
    fallback_models: List[str] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30

@dataclass
class AIConfig:
    """AI配置"""
    default_provider: str = "zhipu"
    default_model: str = "glm-4.5-turbo"
    timeout: int = 60
    max_retries: int = 3
    rate_limit: int = 100  # 每分钟最大请求数
    enable_streaming: bool = True
    cache_responses: bool = True
    cache_ttl: int = 3600  # 缓存生存时间（秒）
    load_balancing: bool = True
    cost_optimization: bool = True
    fallback_enabled: bool = True
    providers: Dict[str, AIProviderConfig] = field(default_factory=dict)
    scenarios: Dict[str, AIScenarioConfig] = field(default_factory=dict)
    routing_rules: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/education_system.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class CacheConfig:
    """缓存配置"""
    enable: bool = True
    backend: str = "memory"  # memory, redis, memcached
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0
    default_ttl: int = 3600
    max_size: int = 1000


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = ""
    jwt_secret: str = ""
    jwt_expiry: int = 3600
    enable_cors: bool = True
    allowed_origins: list = field(default_factory=list)
    rate_limit_per_minute: int = 60
    enable_encryption: bool = True


@dataclass
class SystemConfig:
    """系统配置"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    timezone: str = "Asia/Shanghai"
    language: str = "zh-CN"
    max_workers: int = 4
    enable_metrics: bool = True
    metrics_port: int = 9090


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json", env_file: str = ".env", ai_models_file: str = "ai_models.json"):
        self.config_file = config_file
        self.env_file = env_file
        self.ai_models_file = ai_models_file
        self.validator = ConfigValidator()
        
        # 配置对象
        self.database = DatabaseConfig()
        self.ai = AIConfig()
        self.logging = LoggingConfig()
        self.cache = CacheConfig()
        self.security = SecurityConfig()
        self.system = SystemConfig()
        
        # 加载配置
        self._load_config()
        self._load_ai_models_config()
        self._load_env_vars()
        self._validate_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._update_config_from_dict(config_data)
            else:
                print(f"⚠️ 配置文件 {self.config_file} 不存在，使用默认配置")
        except Exception as e:
            raise ConfigurationError(f"加载配置文件失败: {e}")
    
    def _load_ai_models_config(self):
        """加载AI模型配置文件"""
        try:
            ai_models_path = os.path.join(os.path.dirname(__file__), self.ai_models_file)
            if os.path.exists(ai_models_path):
                with open(ai_models_path, 'r', encoding='utf-8') as f:
                    ai_models_data = json.load(f)
                    self._update_ai_config_from_models(ai_models_data)
            else:
                print(f"⚠️ AI模型配置文件 {ai_models_path} 不存在，使用默认配置")
        except Exception as e:
            raise ConfigurationError(f"加载AI模型配置文件失败: {e}")
    
    def _update_ai_config_from_models(self, ai_models_data: Dict[str, Any]):
        """从AI模型配置更新AI配置"""
        # 更新LLM配置
        llm_config = ai_models_data.get("llm_config", {})
        if llm_config:
            self.ai.default_provider = llm_config.get("default_provider", self.ai.default_provider)
            self.ai.default_model = llm_config.get("default_model", self.ai.default_model)
            self.ai.timeout = llm_config.get("timeout", self.ai.timeout)
            self.ai.max_retries = llm_config.get("max_retries", self.ai.max_retries)
            self.ai.load_balancing = llm_config.get("load_balancing", self.ai.load_balancing)
            self.ai.cost_optimization = llm_config.get("cost_optimization", self.ai.cost_optimization)
            self.ai.fallback_enabled = llm_config.get("fallback_enabled", self.ai.fallback_enabled)
        
        # 更新提供商配置
        providers_data = ai_models_data.get("providers", {})
        for provider_name, provider_data in providers_data.items():
            provider_config = AIProviderConfig(
                name=provider_data.get("name", provider_name),
                base_url=provider_data.get("base_url", ""),
                api_key=provider_data.get("api_key", ""),
                enabled=provider_data.get("enabled", True),
                priority=provider_data.get("priority", 1)
            )
            
            # 更新模型配置
            models_data = provider_data.get("models", {})
            for model_name, model_data in models_data.items():
                model_config = AIModelConfig(
                    name=model_data.get("name", model_name),
                    display_name=model_data.get("display_name", model_name),
                    max_tokens=model_data.get("max_tokens", 8192),
                    supports_chat=model_data.get("supports_chat", True),
                    supports_completion=model_data.get("supports_completion", True),
                    supports_streaming=model_data.get("supports_streaming", False),
                    cost_per_token=model_data.get("cost_per_token", 0.001),
                    temperature=model_data.get("temperature", 0.7),
                    timeout=model_data.get("timeout", 60),
                    description=model_data.get("description", "")
                )
                provider_config.models[model_name] = model_config
            
            self.ai.providers[provider_name] = provider_config
        
        # 更新场景配置
        scenarios_data = ai_models_data.get("scenarios", {})
        for scenario_name, scenario_data in scenarios_data.items():
            scenario_config = AIScenarioConfig(
                name=scenario_data.get("name", scenario_name),
                description=scenario_data.get("description", ""),
                preferred_models=scenario_data.get("preferred_models", []),
                fallback_models=scenario_data.get("fallback_models", []),
                temperature=scenario_data.get("temperature", 0.7),
                max_tokens=scenario_data.get("max_tokens", 1000),
                timeout=scenario_data.get("timeout", 30)
            )
            self.ai.scenarios[scenario_name] = scenario_config
        
        # 更新路由规则和监控配置
        self.ai.routing_rules = ai_models_data.get("routing_rules", {})
        self.ai.monitoring = ai_models_data.get("monitoring", {})
    
    def _load_env_vars(self):
        """加载环境变量"""
        # 从环境变量更新配置
        env_mappings = {
            'EDUCATION_ENV': ('system', 'environment'),
            'EDUCATION_DEBUG': ('system', 'debug'),
            'DATABASE_HOST': ('database', 'host'),
            'DATABASE_PORT': ('database', 'port'),
            'DATABASE_NAME': ('database', 'name'),
            'DATABASE_USER': ('database', 'user'),
            'DATABASE_PASSWORD': ('database', 'password'),
            'AI_DEFAULT_PROVIDER': ('ai', 'default_provider'),
            'AI_DEFAULT_MODEL': ('ai', 'default_model'),
            'SECRET_KEY': ('security', 'secret_key'),
            'JWT_SECRET': ('security', 'jwt_secret'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_attr(section, key, value)
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """从字典更新配置"""
        for section, values in config_data.items():
            if hasattr(self, section):
                section_obj = getattr(self, section)
                for key, value in values.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    def _set_nested_attr(self, section: str, key: str, value: Any):
        """设置嵌套属性"""
        if hasattr(self, section):
            section_obj = getattr(self, section)
            if hasattr(section_obj, key):
                # 类型转换
                if key in ['port', 'pool_size', 'max_overflow', 'timeout', 'max_retries']:
                    value = int(value)
                elif key in ['debug', 'enable_streaming', 'cache_responses', 'enable_console', 'enable_file']:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif key == 'environment':
                    value = Environment(value)
                
                setattr(section_obj, key, value)
    
    def _validate_config(self):
        """验证配置"""
        try:
            self.validator.validate_database_config(self.database)
            self.validator.validate_ai_config(self.ai)
            self.validator.validate_logging_config(self.logging)
            self.validator.validate_cache_config(self.cache)
            self.validator.validate_security_config(self.security)
            self.validator.validate_system_config(self.system)
        except Exception as e:
            raise ConfigurationError(f"配置验证失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            return self._get_nested_attr(key)
        except AttributeError:
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._set_nested_attr(*key.split('.'), value)
    
    def _get_nested_attr(self, key: str) -> Any:
        """获取嵌套属性"""
        parts = key.split('.')
        obj = self
        for part in parts:
            obj = getattr(obj, part)
        return obj
    
    def save_config(self, file_path: str = None):
        """保存配置到文件"""
        file_path = file_path or self.config_file
        
        config_data = {
            'database': self._dataclass_to_dict(self.database),
            'ai': self._dataclass_to_dict(self.ai),
            'logging': self._dataclass_to_dict(self.logging),
            'cache': self._dataclass_to_dict(self.cache),
            'security': self._dataclass_to_dict(self.security),
            'system': self._dataclass_to_dict(self.system)
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ConfigurationError(f"保存配置文件失败: {e}")
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """将dataclass转换为字典"""
        if hasattr(obj, '__dataclass_fields__'):
            return {field.name: getattr(obj, field.name) for field in obj.__dataclass_fields__.values()}
        return {}
    
    def reload(self):
        """重新加载配置"""
        self._load_config()
        self._load_env_vars()
        self._validate_config()
    
    def get_ai_config(self) -> AIConfig:
        """获取AI配置"""
        return self.ai
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self.database
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        return self.logging
    
    def get_cache_config(self) -> CacheConfig:
        """获取缓存配置"""
        return self.cache
    
    def get_security_config(self) -> SecurityConfig:
        """获取安全配置"""
        return self.security
    
    def get_system_config(self) -> SystemConfig:
        """获取系统配置"""
        return self.system
    
    def get_ai_provider_config(self, provider_name: str) -> Optional[AIProviderConfig]:
        """获取AI提供商配置"""
        return self.ai.providers.get(provider_name)
    
    def get_ai_model_config(self, provider_name: str, model_name: str) -> Optional[AIModelConfig]:
        """获取AI模型配置"""
        provider = self.get_ai_provider_config(provider_name)
        if provider:
            return provider.models.get(model_name)
        return None
    
    def get_ai_scenario_config(self, scenario_name: str) -> Optional[AIScenarioConfig]:
        """获取AI场景配置"""
        return self.ai.scenarios.get(scenario_name)
    
    def get_available_models(self, provider_name: str = None) -> Dict[str, AIModelConfig]:
        """获取可用模型列表"""
        if provider_name:
            provider = self.get_ai_provider_config(provider_name)
            return provider.models if provider else {}
        
        all_models = {}
        for provider in self.ai.providers.values():
            if provider.enabled:
                all_models.update(provider.models)
        return all_models
    
    def get_enabled_providers(self) -> Dict[str, AIProviderConfig]:
        """获取启用的提供商"""
        return {name: provider for name, provider in self.ai.providers.items() if provider.enabled}
    
    def get_model_for_scenario(self, scenario_name: str) -> Optional[tuple]:
        """根据场景获取推荐模型"""
        scenario = self.get_ai_scenario_config(scenario_name)
        if not scenario:
            return None
        
        # 尝试首选模型
        for model_name in scenario.preferred_models:
            for provider_name, provider in self.get_enabled_providers().items():
                if model_name in provider.models:
                    return (provider_name, model_name)
        
        # 尝试备用模型
        for model_name in scenario.fallback_models:
            for provider_name, provider in self.get_enabled_providers().items():
                if model_name in provider.models:
                    return (provider_name, model_name)
        
        return None


# 全局配置实例
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """获取配置管理器实例"""
    return config_manager

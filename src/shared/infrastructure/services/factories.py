"""
工厂模式实现
为各种服务提供统一的创建接口
"""

from typing import Any, Dict, Optional, Type
from abc import ABC, abstractmethod
from ..di.interfaces import (
    IAIClient, IDataProcessor, IDocumentGenerator, IContentGenerator,
    IProgressTracker, ICacheManager, IConfigManager
)
from ..config.settings import ConfigManager
from ..cache.cache_manager import CacheManager
from ..monitoring.metrics import MetricsCollector
from ..ux.progress_tracker import ProgressTracker
from ..data.data_optimizer import DataOptimizer, DataConfig
from ..document.document_optimizer import DocumentGenerator, DocumentConfig
from ..ai.batch_processor import BatchProcessor, BatchConfig


class BaseFactory(ABC):
    """基础工厂类"""
    
    @abstractmethod
    def create(self, **kwargs) -> Any:
        """创建实例"""
        pass
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {}


class AIClientFactory(BaseFactory):
    """AI客户端工厂"""
    
    def create(self, provider: str = "zhipu", model: str = "glm-4.5-turbo", **kwargs) -> IAIClient:
        """创建AI客户端"""
        from ..ai.clients.zhipu_client import ZhipuAIClient
        from ..ai.clients.context7_client import Context7Client
        from ..ai.clients.deepseek_client import DeepSeekClient
        
        config = self.get_default_config()
        config.update(kwargs)
        
        if provider.lower() == "zhipu":
            return ZhipuAIClient(model=model, **config)
        elif provider.lower() == "context7":
            return Context7Client(model=model, **config)
        elif provider.lower() == "deepseek":
            return DeepSeekClient(model=model, **config)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "timeout": 60,
            "max_retries": 3,
            "temperature": 0.7,
            "max_tokens": 1000
        }


class DataProcessorFactory(BaseFactory):
    """数据处理器工厂"""
    
    def create(self, config: Optional[DataConfig] = None, **kwargs) -> IDataProcessor:
        """创建数据处理器"""
        if config is None:
            config = DataConfig(**self.get_default_config())
        
        config_dict = config.__dict__.copy()
        config_dict.update(kwargs)
        config = DataConfig(**config_dict)
        
        return DataOptimizer(config)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "cache_enabled": True,
            "cache_ttl": 3600,
            "max_cache_size": 1000,
            "enable_compression": True,
            "batch_size": 100,
            "max_workers": 4,
            "enable_indexing": True,
            "auto_save": True,
            "save_interval": 300.0
        }


class DocumentGeneratorFactory(BaseFactory):
    """文档生成器工厂"""
    
    def create(self, config: Optional[DocumentConfig] = None, **kwargs) -> IDocumentGenerator:
        """创建文档生成器"""
        if config is None:
            config = DocumentConfig(**self.get_default_config())
        
        config_dict = config.__dict__.copy()
        config_dict.update(kwargs)
        config = DocumentConfig(**config_dict)
        
        return DocumentGenerator(config)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "template_dir": "templates",
            "output_dir": "outputs",
            "default_format": "docx",
            "enable_batch": True,
            "max_batch_size": 50,
            "enable_caching": True,
            "cache_ttl": 3600
        }


class ContentGeneratorFactory(BaseFactory):
    """内容生成器工厂"""
    
    def create(self, ai_client: Optional[IAIClient] = None, **kwargs) -> IContentGenerator:
        """创建内容生成器"""
        from ...english.generators.english_content_generator import EnglishContentGenerator
        
        if ai_client is None:
            ai_client = AIClientFactory().create()
        
        return EnglishContentGenerator(ai_client=ai_client, **kwargs)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "enable_ai_generation": True,
            "fallback_to_template": True,
            "max_retries": 3,
            "timeout": 30
        }


class ProgressTrackerFactory(BaseFactory):
    """进度跟踪器工厂"""
    
    def create(self, **kwargs) -> IProgressTracker:
        """创建进度跟踪器"""
        return ProgressTracker()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {}


class CacheManagerFactory(BaseFactory):
    """缓存管理器工厂"""
    
    def create(self, **kwargs) -> ICacheManager:
        """创建缓存管理器"""
        config = self.get_default_config()
        config.update(kwargs)
        return CacheManager(**config)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "max_size": 1000,
            "default_ttl": 3600,
            "cleanup_interval": 300,
            "enable_compression": True
        }


class ConfigManagerFactory(BaseFactory):
    """配置管理器工厂"""
    
    def create(self, config_file: str = "config.json", **kwargs) -> IConfigManager:
        """创建配置管理器"""
        return ConfigManager(config_file=config_file, **kwargs)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "config_file": "config.json",
            "env_file": ".env",
            "ai_models_file": "ai_models.json"
        }


class BatchProcessorFactory(BaseFactory):
    """批处理器工厂"""
    
    def create(self, config: Optional[BatchConfig] = None, **kwargs) -> BatchProcessor:
        """创建批处理器"""
        if config is None:
            config = BatchConfig(**self.get_default_config())
        
        config_dict = config.__dict__.copy()
        config_dict.update(kwargs)
        config = BatchConfig(**config_dict)
        
        return BatchProcessor(config)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "max_batch_size": 10,
            "max_wait_time": 5.0,
            "max_concurrent_batches": 5,
            "enable_caching": True,
            "cache_ttl": 3600,
            "enable_metrics": True
        }


# 工厂注册表
FACTORY_REGISTRY = {
    IAIClient: AIClientFactory(),
    IDataProcessor: DataProcessorFactory(),
    IDocumentGenerator: DocumentGeneratorFactory(),
    IContentGenerator: ContentGeneratorFactory(),
    IProgressTracker: ProgressTrackerFactory(),
    ICacheManager: CacheManagerFactory(),
    IConfigManager: ConfigManagerFactory(),
    BatchProcessor: BatchProcessorFactory()
}


def get_factory(service_type: Type) -> Optional[BaseFactory]:
    """获取服务工厂"""
    return FACTORY_REGISTRY.get(service_type)


def create_service(service_type: Type, **kwargs) -> Any:
    """使用工厂创建服务"""
    factory = get_factory(service_type)
    if factory is None:
        raise ValueError(f"No factory found for service type: {service_type}")
    
    return factory.create(**kwargs)


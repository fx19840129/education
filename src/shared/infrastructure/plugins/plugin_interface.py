"""
插件接口定义
定义各种类型的插件接口
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass, field
from enum import Enum

from ..di.interfaces import (
    IAIClient, IDataProcessor, IDocumentGenerator, IContentGenerator,
    IProgressTracker, ICacheManager, IConfigManager
)


class PluginType(Enum):
    """插件类型"""
    AI_CLIENT = "ai_client"
    DATA_PROCESSOR = "data_processor"
    DOCUMENT_GENERATOR = "document_generator"
    CONTENT_GENERATOR = "content_generator"
    PROGRESS_TRACKER = "progress_tracker"
    CACHE_MANAGER = "cache_manager"
    CONFIG_MANAGER = "config_manager"
    CUSTOM = "custom"


class PluginStatus(Enum):
    """插件状态"""
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNLOADED = "unloaded"


@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    status: PluginStatus = PluginStatus.LOADED
    load_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.info: Optional[PluginInfo] = None
        self.status = PluginStatus.LOADED
        self.initialized = False
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def activate(self) -> bool:
        """激活插件"""
        pass
    
    @abstractmethod
    def deactivate(self) -> bool:
        """停用插件"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """清理插件"""
        pass
    
    def is_available(self) -> bool:
        """检查插件是否可用"""
        return self.status == PluginStatus.ACTIVE and self.initialized
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """设置配置"""
        self.config[key] = value


class AIClientPlugin(BasePlugin, IAIClient):
    """AI客户端插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name=self.__class__.__name__,
            version="1.0.0",
            description="AI客户端插件",
            author="Unknown",
            plugin_type=PluginType.AI_CLIENT
        )
    
    def initialize(self) -> bool:
        """初始化AI客户端插件"""
        try:
            self._initialize_ai_client()
            self.initialized = True
            return True
        except Exception as e:
            print(f"AI客户端插件初始化失败: {e}")
            return False
    
    def activate(self) -> bool:
        """激活AI客户端插件"""
        if not self.initialized:
            return False
        
        try:
            self._activate_ai_client()
            self.status = PluginStatus.ACTIVE
            return True
        except Exception as e:
            print(f"AI客户端插件激活失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用AI客户端插件"""
        try:
            self._deactivate_ai_client()
            self.status = PluginStatus.INACTIVE
            return True
        except Exception as e:
            print(f"AI客户端插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理AI客户端插件"""
        try:
            self._cleanup_ai_client()
            self.initialized = False
            self.status = PluginStatus.UNLOADED
            return True
        except Exception as e:
            print(f"AI客户端插件清理失败: {e}")
            return False
    
    @abstractmethod
    def _initialize_ai_client(self):
        """初始化AI客户端"""
        pass
    
    @abstractmethod
    def _activate_ai_client(self):
        """激活AI客户端"""
        pass
    
    @abstractmethod
    def _deactivate_ai_client(self):
        """停用AI客户端"""
        pass
    
    @abstractmethod
    def _cleanup_ai_client(self):
        """清理AI客户端"""
        pass


class DataProcessorPlugin(BasePlugin, IDataProcessor):
    """数据处理器插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name=self.__class__.__name__,
            version="1.0.0",
            description="数据处理器插件",
            author="Unknown",
            plugin_type=PluginType.DATA_PROCESSOR
        )
    
    def initialize(self) -> bool:
        """初始化数据处理器插件"""
        try:
            self._initialize_data_processor()
            self.initialized = True
            return True
        except Exception as e:
            print(f"数据处理器插件初始化失败: {e}")
            return False
    
    def activate(self) -> bool:
        """激活数据处理器插件"""
        if not self.initialized:
            return False
        
        try:
            self._activate_data_processor()
            self.status = PluginStatus.ACTIVE
            return True
        except Exception as e:
            print(f"数据处理器插件激活失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用数据处理器插件"""
        try:
            self._deactivate_data_processor()
            self.status = PluginStatus.INACTIVE
            return True
        except Exception as e:
            print(f"数据处理器插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理数据处理器插件"""
        try:
            self._cleanup_data_processor()
            self.initialized = False
            self.status = PluginStatus.UNLOADED
            return True
        except Exception as e:
            print(f"数据处理器插件清理失败: {e}")
            return False
    
    @abstractmethod
    def _initialize_data_processor(self):
        """初始化数据处理器"""
        pass
    
    @abstractmethod
    def _activate_data_processor(self):
        """激活数据处理器"""
        pass
    
    @abstractmethod
    def _deactivate_data_processor(self):
        """停用数据处理器"""
        pass
    
    @abstractmethod
    def _cleanup_data_processor(self):
        """清理数据处理器"""
        pass


class DocumentGeneratorPlugin(BasePlugin, IDocumentGenerator):
    """文档生成器插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name=self.__class__.__name__,
            version="1.0.0",
            description="文档生成器插件",
            author="Unknown",
            plugin_type=PluginType.DOCUMENT_GENERATOR
        )
    
    def initialize(self) -> bool:
        """初始化文档生成器插件"""
        try:
            self._initialize_document_generator()
            self.initialized = True
            return True
        except Exception as e:
            print(f"文档生成器插件初始化失败: {e}")
            return False
    
    def activate(self) -> bool:
        """激活文档生成器插件"""
        if not self.initialized:
            return False
        
        try:
            self._activate_document_generator()
            self.status = PluginStatus.ACTIVE
            return True
        except Exception as e:
            print(f"文档生成器插件激活失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用文档生成器插件"""
        try:
            self._deactivate_document_generator()
            self.status = PluginStatus.INACTIVE
            return True
        except Exception as e:
            print(f"文档生成器插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理文档生成器插件"""
        try:
            self._cleanup_document_generator()
            self.initialized = False
            self.status = PluginStatus.UNLOADED
            return True
        except Exception as e:
            print(f"文档生成器插件清理失败: {e}")
            return False
    
    @abstractmethod
    def _initialize_document_generator(self):
        """初始化文档生成器"""
        pass
    
    @abstractmethod
    def _activate_document_generator(self):
        """激活文档生成器"""
        pass
    
    @abstractmethod
    def _deactivate_document_generator(self):
        """停用文档生成器"""
        pass
    
    @abstractmethod
    def _cleanup_document_generator(self):
        """清理文档生成器"""
        pass


class ContentGeneratorPlugin(BasePlugin, IContentGenerator):
    """内容生成器插件"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name=self.__class__.__name__,
            version="1.0.0",
            description="内容生成器插件",
            author="Unknown",
            plugin_type=PluginType.CONTENT_GENERATOR
        )
    
    def initialize(self) -> bool:
        """初始化内容生成器插件"""
        try:
            self._initialize_content_generator()
            self.initialized = True
            return True
        except Exception as e:
            print(f"内容生成器插件初始化失败: {e}")
            return False
    
    def activate(self) -> bool:
        """激活内容生成器插件"""
        if not self.initialized:
            return False
        
        try:
            self._activate_content_generator()
            self.status = PluginStatus.ACTIVE
            return True
        except Exception as e:
            print(f"内容生成器插件激活失败: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用内容生成器插件"""
        try:
            self._deactivate_content_generator()
            self.status = PluginStatus.INACTIVE
            return True
        except Exception as e:
            print(f"内容生成器插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理内容生成器插件"""
        try:
            self._cleanup_content_generator()
            self.initialized = False
            self.status = PluginStatus.UNLOADED
            return True
        except Exception as e:
            print(f"内容生成器插件清理失败: {e}")
            return False
    
    @abstractmethod
    def _initialize_content_generator(self):
        """初始化内容生成器"""
        pass
    
    @abstractmethod
    def _activate_content_generator(self):
        """激活内容生成器"""
        pass
    
    @abstractmethod
    def _deactivate_content_generator(self):
        """停用内容生成器"""
        pass
    
    @abstractmethod
    def _cleanup_content_generator(self):
        """清理内容生成器"""
        pass


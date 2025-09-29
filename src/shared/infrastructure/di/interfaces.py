"""
抽象接口定义
定义系统中各个组件的抽象接口，实现依赖倒置原则
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """内容类型"""
    WORD = "word"
    GRAMMAR = "grammar"
    EXERCISE = "exercise"
    SENTENCE = "sentence"


class DifficultyLevel(Enum):
    """难度级别"""
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class GenerationRequest:
    """生成请求"""
    content_type: ContentType
    topic: str
    difficulty: DifficultyLevel
    count: int = 1
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResult:
    """生成结果"""
    success: bool
    content: List[Dict[str, Any]]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IAIClient(ABC):
    """AI客户端接口"""
    
    @abstractmethod
    async def generate_content(self, request: GenerationRequest) -> GenerationResult:
        """生成内容"""
        pass
    
    @abstractmethod
    async def generate_sentence(self, word: str, context: Optional[Dict[str, Any]] = None) -> str:
        """生成句子"""
        pass
    
    @abstractmethod
    async def generate_exercise(self, topic: str, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """生成练习"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查是否可用"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        pass


class IDataProcessor(ABC):
    """数据处理器接口"""
    
    @abstractmethod
    def process_data(self, data: Any) -> Any:
        """处理数据"""
        pass
    
    @abstractmethod
    def batch_process(self, data_list: List[Any], processor_func: Callable) -> List[Any]:
        """批量处理数据"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理资源"""
        pass


class IDocumentGenerator(ABC):
    """文档生成器接口"""
    
    @abstractmethod
    def generate_document(self, content: Dict[str, Any], output_path: str) -> bool:
        """生成文档"""
        pass
    
    @abstractmethod
    def batch_generate(self, content_list: List[Dict[str, Any]], output_dir: str) -> List[str]:
        """批量生成文档"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """获取支持的格式"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        pass


class IContentGenerator(ABC):
    """内容生成器接口"""
    
    @abstractmethod
    def generate_word_content(self, words: List[str], difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """生成单词内容"""
        pass
    
    @abstractmethod
    def generate_grammar_content(self, grammar_points: List[str], difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """生成语法内容"""
        pass
    
    @abstractmethod
    def generate_exercise_content(self, topics: List[str], difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """生成练习内容"""
        pass
    
    @abstractmethod
    def generate_daily_content(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """生成每日内容"""
        pass


class IProgressTracker(ABC):
    """进度跟踪器接口"""
    
    @abstractmethod
    def create_task(self, task_id: str, name: str, steps: List[str]) -> bool:
        """创建任务"""
        pass
    
    @abstractmethod
    def start_task(self, task_id: str) -> bool:
        """开始任务"""
        pass
    
    @abstractmethod
    def complete_step(self, task_id: str, step_name: str, error_message: str = None) -> bool:
        """完成步骤"""
        pass
    
    @abstractmethod
    def complete_task(self, task_id: str, error_message: str = None) -> bool:
        """完成任务"""
        pass
    
    @abstractmethod
    def get_task_status(self, task_id: str) -> Optional[str]:
        """获取任务状态"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        pass


class ICacheManager(ABC):
    """缓存管理器接口"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        pass


class IConfigManager(ABC):
    """配置管理器接口"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> bool:
        """设置配置"""
        pass
    
    @abstractmethod
    def reload(self) -> bool:
        """重新加载配置"""
        pass
    
    @abstractmethod
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        pass
    
    @abstractmethod
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        pass


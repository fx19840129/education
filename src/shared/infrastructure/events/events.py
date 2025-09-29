"""
事件定义
定义系统中使用的各种事件类型
"""

import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    """事件类型"""
    LEARNING_PLAN_CREATED = "learning_plan_created"
    CONTENT_GENERATED = "content_generated"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    PROGRESS_UPDATED = "progress_updated"
    ERROR_OCCURRED = "error_occurred"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"


@dataclass
class BaseEvent(ABC):
    """基础事件类"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = field(init=False)
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not hasattr(self, 'event_type'):
            self.event_type = self._get_event_type()
    
    @abstractmethod
    def _get_event_type(self) -> EventType:
        """获取事件类型"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEvent':
        """从字典创建事件"""
        event = cls()
        event.event_id = data.get("event_id", str(uuid.uuid4()))
        event.timestamp = data.get("timestamp", time.time())
        event.source = data.get("source", "")
        event.data = data.get("data", {})
        event.metadata = data.get("metadata", {})
        return event


@dataclass
class LearningPlanCreatedEvent(BaseEvent):
    """学习计划创建事件"""
    plan_id: str = ""
    plan_name: str = ""
    duration_days: int = 0
    daily_study_time: int = 0
    total_words: int = 0
    total_grammar_points: int = 0
    
    def _get_event_type(self) -> EventType:
        return EventType.LEARNING_PLAN_CREATED
    
    def __post_init__(self):
        super().__post_init__()
        self.data.update({
            "plan_id": self.plan_id,
            "plan_name": self.plan_name,
            "duration_days": self.duration_days,
            "daily_study_time": self.daily_study_time,
            "total_words": self.total_words,
            "total_grammar_points": self.total_grammar_points
        })


@dataclass
class ContentGeneratedEvent(BaseEvent):
    """内容生成事件"""
    content_type: str = ""  # word, grammar, exercise
    topic: str = ""
    difficulty: str = ""
    count: int = 0
    generation_time: float = 0.0
    success: bool = True
    
    def _get_event_type(self) -> EventType:
        return EventType.CONTENT_GENERATED
    
    def __post_init__(self):
        super().__post_init__()
        self.data.update({
            "content_type": self.content_type,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "count": self.count,
            "generation_time": self.generation_time,
            "success": self.success
        })


@dataclass
class TaskCompletedEvent(BaseEvent):
    """任务完成事件"""
    task_id: str = ""
    task_name: str = ""
    duration: float = 0.0
    result: Any = None
    
    def _get_event_type(self) -> EventType:
        return EventType.TASK_COMPLETED
    
    def __post_init__(self):
        super().__post_init__()
        self.data.update({
            "task_id": self.task_id,
            "task_name": self.task_name,
            "duration": self.duration,
            "result": self.result
        })


@dataclass
class TaskFailedEvent(BaseEvent):
    """任务失败事件"""
    task_id: str = ""
    task_name: str = ""
    error_message: str = ""
    error_type: str = ""
    duration: float = 0.0
    
    def _get_event_type(self) -> EventType:
        return EventType.TASK_FAILED
    
    def __post_init__(self):
        super().__post_init__()
        self.data.update({
            "task_id": self.task_id,
            "task_name": self.task_name,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "duration": self.duration
        })


@dataclass
class ProgressUpdatedEvent(BaseEvent):
    """进度更新事件"""
    task_id: str = ""
    step_name: str = ""
    progress: float = 0.0
    message: str = ""
    
    def _get_event_type(self) -> EventType:
        return EventType.PROGRESS_UPDATED
    
    def __post_init__(self):
        super().__post_init__()
        self.data.update({
            "task_id": self.task_id,
            "step_name": self.step_name,
            "progress": self.progress,
            "message": self.message
        })


@dataclass
class ErrorOccurredEvent(BaseEvent):
    """错误发生事件"""
    error_type: str = ""
    error_message: str = ""
    stack_trace: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    
    def _get_event_type(self) -> EventType:
        return EventType.ERROR_OCCURRED
    
    def __post_init__(self):
        super().__post_init__()
        self.data.update({
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "context": self.context
        })


@dataclass
class UserActionEvent(BaseEvent):
    """用户操作事件"""
    action: str = ""
    user_id: str = ""
    session_id: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def _get_event_type(self) -> EventType:
        return EventType.USER_ACTION
    
    def __post_init__(self):
        super().__post_init__()
        self.data.update({
            "action": self.action,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "parameters": self.parameters
        })


@dataclass
class SystemEvent(BaseEvent):
    """系统事件"""
    component: str = ""
    operation: str = ""
    status: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def _get_event_type(self) -> EventType:
        return EventType.SYSTEM_EVENT
    
    def __post_init__(self):
        super().__post_init__()
        self.data.update({
            "component": self.component,
            "operation": self.operation,
            "status": self.status,
            "details": self.details
        })


"""
事件驱动架构模块
提供事件总线、发布-订阅模式和事件处理机制
"""

from .event_bus import EventBus, get_event_bus, publish_event, subscribe_event
from .event_handlers import EventHandler, AsyncEventHandler, EventHandlerRegistry
from .events import (
    BaseEvent,
    EventType,
    LearningPlanCreatedEvent,
    ContentGeneratedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
    ProgressUpdatedEvent,
    ErrorOccurredEvent
)

__all__ = [
    'EventBus',
    'get_event_bus',
    'publish_event',
    'subscribe_event',
    'EventHandler',
    'AsyncEventHandler', 
    'EventHandlerRegistry',
    'BaseEvent',
    'EventType',
    'LearningPlanCreatedEvent',
    'ContentGeneratedEvent',
    'TaskCompletedEvent',
    'TaskFailedEvent',
    'ProgressUpdatedEvent',
    'ErrorOccurredEvent'
]

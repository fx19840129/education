"""
架构优化测试
测试依赖注入、服务定位器、事件总线、插件系统等功能
"""

import unittest
import time
import threading
import sys
import os
from unittest.mock import Mock, MagicMock

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.shared.infrastructure.di import (
    DIContainer, ServiceLifetime, IAIClient, IDataProcessor, IDocumentGenerator,
    injectable, singleton, transient, scoped
)
from src.shared.infrastructure.di.interfaces import (
    GenerationRequest, GenerationResult, ContentType, DifficultyLevel
)
from src.shared.infrastructure.services import (
    ServiceLocator, AIClientFactory, DataProcessorFactory
)
from src.shared.infrastructure.events import (
    EventBus, EventType, LearningPlanCreatedEvent, ContentGeneratedEvent,
    TaskCompletedEvent, publish_event, subscribe_event
)
from src.shared.infrastructure.plugins import (
    PluginManager, BasePlugin, PluginType, PluginStatus, PluginInfo
)


class TestDIContainer(unittest.TestCase):
    """依赖注入容器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.container = DIContainer()
    
    def test_register_singleton(self):
        """测试注册单例服务"""
        class TestService:
            def __init__(self):
                self.value = "test"
        
        self.container.register_singleton(TestService)
        
        # 获取两次实例，应该是同一个
        instance1 = self.container.resolve(TestService)
        instance2 = self.container.resolve(TestService)
        
        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.value, "test")
    
    def test_register_transient(self):
        """测试注册瞬态服务"""
        class TestService:
            def __init__(self):
                self.value = "test"
        
        self.container.register_transient(TestService)
        
        # 获取两次实例，应该是不同的
        instance1 = self.container.resolve(TestService)
        instance2 = self.container.resolve(TestService)
        
        self.assertIsNot(instance1, instance2)
        self.assertEqual(instance1.value, "test")
        self.assertEqual(instance2.value, "test")
    
    def test_register_with_factory(self):
        """测试使用工厂注册服务"""
        def create_service():
            return {"value": "factory_created"}
        
        self.container.register_singleton(dict, factory=create_service)
        
        instance = self.container.resolve(dict)
        self.assertEqual(instance["value"], "factory_created")
    
    def test_dependency_injection(self):
        """测试依赖注入"""
        class Dependency:
            def __init__(self):
                self.value = "dependency"
        
        class Service:
            def __init__(self, dependency: Dependency):
                self.dependency = dependency
        
        self.container.register_singleton(Dependency)
        self.container.register_singleton(Service)
        
        service = self.container.resolve(Service)
        self.assertIsInstance(service.dependency, Dependency)
        self.assertEqual(service.dependency.value, "dependency")
    
    def test_scope_management(self):
        """测试作用域管理"""
        class ScopedService:
            def __init__(self):
                self.value = "scoped"
        
        self.container.register_scoped(ScopedService)
        
        with self.container.create_scope() as scope1:
            instance1 = self.container.resolve(ScopedService)
            
            with self.container.create_scope() as scope2:
                instance2 = self.container.resolve(ScopedService)
                self.assertIsNot(instance1, instance2)
            
            instance3 = self.container.resolve(ScopedService)
            self.assertIs(instance1, instance3)


class TestServiceLocator(unittest.TestCase):
    """服务定位器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.locator = ServiceLocator()
    
    def test_register_and_get_service(self):
        """测试注册和获取服务"""
        class TestService:
            def __init__(self):
                self.value = "test"
        
        def create_service():
            return TestService()
        
        self.locator.register_service(TestService, factory=create_service)
        
        service = self.locator.get_service(TestService)
        self.assertIsInstance(service, TestService)
        self.assertEqual(service.value, "test")
    
    def test_register_instance(self):
        """测试注册实例"""
        instance = {"value": "instance"}
        self.locator.register_service(dict, instance=instance)
        
        service = self.locator.get_service(dict)
        self.assertIs(service, instance)
    
    def test_has_service(self):
        """测试检查服务是否存在"""
        class TestService:
            pass
        
        self.assertFalse(self.locator.has_service(TestService))
        
        self.locator.register_service(TestService)
        self.assertTrue(self.locator.has_service(TestService))
    
    def test_remove_service(self):
        """测试移除服务"""
        class TestService:
            pass
        
        self.locator.register_service(TestService)
        self.assertTrue(self.locator.has_service(TestService))
        
        self.assertTrue(self.locator.remove_service(TestService))
        self.assertFalse(self.locator.has_service(TestService))


class TestEventBus(unittest.TestCase):
    """事件总线测试"""
    
    def setUp(self):
        """测试前准备"""
        self.event_bus = EventBus()
        self.received_events = []
    
    def test_sync_event_handling(self):
        """测试同步事件处理"""
        def sync_handler(event):
            self.received_events.append(event)
        
        self.event_bus.subscribe(EventType.LEARNING_PLAN_CREATED, sync_handler)
        
        event = LearningPlanCreatedEvent(
            plan_id="test_plan",
            plan_name="测试计划",
            duration_days=30
        )
        
        self.event_bus.publish(event)
        
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].plan_id, "test_plan")
    
    def test_async_event_handling(self):
        """测试异步事件处理"""
        async def async_handler(event):
            self.received_events.append(event)
        
        self.event_bus.subscribe(EventType.CONTENT_GENERATED, async_handler)
        
        event = ContentGeneratedEvent(
            content_type="word",
            topic="测试主题",
            difficulty="elementary"
        )
        
        self.event_bus.publish(event)
        
        # 等待异步处理完成
        time.sleep(0.1)
        
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].content_type, "word")
    
    def test_event_filtering(self):
        """测试事件过滤"""
        def filtered_handler(event):
            self.received_events.append(event)
        
        def filter_func(event):
            return event.plan_id == "filtered_plan"
        
        self.event_bus.subscribe(
            EventType.LEARNING_PLAN_CREATED, 
            filtered_handler,
            filter_func=filter_func
        )
        
        # 发送应该被过滤的事件
        event1 = LearningPlanCreatedEvent(plan_id="other_plan")
        self.event_bus.publish(event1)
        
        # 发送应该被处理的事件
        event2 = LearningPlanCreatedEvent(plan_id="filtered_plan")
        self.event_bus.publish(event2)
        
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].plan_id, "filtered_plan")
    
    def test_priority_handling(self):
        """测试优先级处理"""
        execution_order = []
        
        def low_priority_handler(event):
            execution_order.append("low")
        
        def high_priority_handler(event):
            execution_order.append("high")
        
        self.event_bus.subscribe(EventType.TASK_COMPLETED, low_priority_handler, priority=10)
        self.event_bus.subscribe(EventType.TASK_COMPLETED, high_priority_handler, priority=1)
        
        event = TaskCompletedEvent(task_id="test_task")
        self.event_bus.publish(event)
        
        self.assertEqual(execution_order, ["high", "low"])
    
    def test_unsubscribe(self):
        """测试取消订阅"""
        def handler(event):
            self.received_events.append(event)
        
        self.event_bus.subscribe(EventType.LEARNING_PLAN_CREATED, handler)
        
        event = LearningPlanCreatedEvent(plan_id="test_plan")
        self.event_bus.publish(event)
        self.assertEqual(len(self.received_events), 1)
        
        # 取消订阅
        self.event_bus.unsubscribe(EventType.LEARNING_PLAN_CREATED, handler)
        
        event2 = LearningPlanCreatedEvent(plan_id="test_plan2")
        self.event_bus.publish(event2)
        self.assertEqual(len(self.received_events), 1)  # 应该没有增加


class TestPluginManager(unittest.TestCase):
    """插件管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.plugin_manager = PluginManager()
    
    def test_plugin_lifecycle(self):
        """测试插件生命周期"""
        class TestPlugin(BasePlugin):
            def __init__(self, config=None):
                super().__init__(config)
                self.initialized = False
            
            def get_info(self):
                return PluginInfo(
                    name="TestPlugin",
                    version="1.0.0",
                    description="测试插件",
                    author="Test",
                    plugin_type=PluginType.CUSTOM
                )
            
            def initialize(self):
                self.initialized = True
                return True
            
            def activate(self):
                self.status = PluginStatus.ACTIVE
                return True
            
            def deactivate(self):
                self.status = PluginStatus.INACTIVE
                return True
            
            def cleanup(self):
                self.initialized = False
                return True
        
        # 加载插件
        self.assertTrue(self.plugin_manager.load_plugin(TestPlugin))
        
        # 检查插件信息
        plugin_info = self.plugin_manager.get_plugin_info("TestPlugin")
        self.assertIsNotNone(plugin_info)
        self.assertEqual(plugin_info.name, "TestPlugin")
        
        # 激活插件
        self.assertTrue(self.plugin_manager.activate_plugin("TestPlugin"))
        
        # 检查插件状态
        plugin = self.plugin_manager.get_plugin("TestPlugin")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.status, PluginStatus.ACTIVE)
        
        # 停用插件
        self.assertTrue(self.plugin_manager.deactivate_plugin("TestPlugin"))
        self.assertEqual(plugin.status, PluginStatus.INACTIVE)
        
        # 卸载插件
        self.assertTrue(self.plugin_manager.unload_plugin("TestPlugin"))
        self.assertIsNone(self.plugin_manager.get_plugin("TestPlugin"))
    
    def test_plugin_by_type(self):
        """测试按类型获取插件"""
        class AIPlugin(BasePlugin):
            def __init__(self, config=None):
                super().__init__(config)
                self.initialized = False
            
            def get_info(self):
                return PluginInfo(
                    name="AIPlugin",
                    version="1.0.0",
                    description="AI插件",
                    author="Test",
                    plugin_type=PluginType.AI_CLIENT
                )
            
            def initialize(self): 
                self.initialized = True
                return True
            def activate(self): 
                self.status = PluginStatus.ACTIVE
                return True
            def deactivate(self): 
                self.status = PluginStatus.INACTIVE
                return True
            def cleanup(self): 
                self.initialized = False
                return True
        
        class DataPlugin(BasePlugin):
            def __init__(self, config=None):
                super().__init__(config)
                self.initialized = False
            
            def get_info(self):
                return PluginInfo(
                    name="DataPlugin",
                    version="1.0.0",
                    description="数据插件",
                    author="Test",
                    plugin_type=PluginType.DATA_PROCESSOR
                )
            
            def initialize(self): 
                self.initialized = True
                return True
            def activate(self): 
                self.status = PluginStatus.ACTIVE
                return True
            def deactivate(self): 
                self.status = PluginStatus.INACTIVE
                return True
            def cleanup(self): 
                self.initialized = False
                return True
        
        # 加载插件
        self.plugin_manager.load_plugin(AIPlugin)
        self.plugin_manager.load_plugin(DataPlugin)
        
        # 按类型获取插件
        ai_plugins = self.plugin_manager.get_plugins_by_type(PluginType.AI_CLIENT)
        data_plugins = self.plugin_manager.get_plugins_by_type(PluginType.DATA_PROCESSOR)
        
        self.assertEqual(len(ai_plugins), 1)
        self.assertEqual(len(data_plugins), 1)
        self.assertEqual(ai_plugins[0].get_info().name, "AIPlugin")
        self.assertEqual(data_plugins[0].get_info().name, "DataPlugin")
    
    def test_plugin_stats(self):
        """测试插件统计"""
        class TestPlugin(BasePlugin):
            def __init__(self, config=None):
                super().__init__(config)
                self.initialized = False
            
            def get_info(self):
                return PluginInfo(
                    name="TestPlugin",
                    version="1.0.0",
                    description="测试插件",
                    author="Test",
                    plugin_type=PluginType.CUSTOM
                )
            
            def initialize(self): 
                self.initialized = True
                return True
            def activate(self): 
                self.status = PluginStatus.ACTIVE
                return True
            def deactivate(self): 
                self.status = PluginStatus.INACTIVE
                return True
            def cleanup(self): 
                self.initialized = False
                return True
        
        # 加载并激活插件
        self.plugin_manager.load_plugin(TestPlugin)
        self.plugin_manager.activate_plugin("TestPlugin")
        
        stats = self.plugin_manager.get_plugin_stats()
        
        self.assertEqual(stats["total_plugins"], 1)
        self.assertEqual(stats["active_plugins"], 1)
        self.assertEqual(stats["plugin_types"]["custom"], 1)
        self.assertEqual(stats["status_counts"]["active"], 1)


class TestArchitectureIntegration(unittest.TestCase):
    """架构集成测试"""
    
    def test_di_with_service_locator(self):
        """测试依赖注入与服务定位器集成"""
        class TestService:
            def __init__(self):
                self.value = "test"
        
        # 使用DI容器注册服务
        container = DIContainer()
        container.register_singleton(TestService)
        
        # 使用服务定位器获取服务
        locator = ServiceLocator(container)
        service = locator.get_service(TestService)
        
        self.assertIsInstance(service, TestService)
        self.assertEqual(service.value, "test")
    
    def test_event_driven_architecture(self):
        """测试事件驱动架构"""
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        # 订阅事件
        subscribe_event(EventType.LEARNING_PLAN_CREATED, event_handler)
        
        # 发布事件
        event = LearningPlanCreatedEvent(plan_id="test_plan")
        publish_event(event)
        
        # 等待事件处理
        time.sleep(0.1)
        
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].plan_id, "test_plan")
    
    def test_plugin_with_di(self):
        """测试插件与依赖注入集成"""
        class TestDependency:
            def __init__(self):
                self.value = "dependency"
        
        class TestPlugin(BasePlugin):
            def __init__(self, config=None):
                super().__init__(config)
                self.dependency = None
                self.initialized = False
            
            def get_info(self):
                return PluginInfo(
                    name="TestPlugin",
                    version="1.0.0",
                    description="测试插件",
                    author="Test",
                    plugin_type=PluginType.CUSTOM
                )
            
            def initialize(self):
                # 在初始化时注入依赖
                container = DIContainer()
                container.register_singleton(TestDependency)
                self.dependency = container.resolve(TestDependency)
                self.initialized = True
                return True
            
            def activate(self): 
                self.status = PluginStatus.ACTIVE
                return True
            def deactivate(self): 
                self.status = PluginStatus.INACTIVE
                return True
            def cleanup(self): 
                self.initialized = False
                return True
        
        plugin_manager = PluginManager()
        plugin_manager.load_plugin(TestPlugin)
        
        plugin = plugin_manager.get_plugin("TestPlugin")
        self.assertIsNotNone(plugin.dependency)
        self.assertEqual(plugin.dependency.value, "dependency")


if __name__ == '__main__':
    unittest.main()

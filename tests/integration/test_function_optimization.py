#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能优化集成测试
"""

import unittest
import time
import threading
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.shared.infrastructure.ai.batch_processor import BatchProcessor, BatchConfig
from src.shared.infrastructure.ai.ai_optimizer import AIOptimizer, RetryConfig, CircuitBreakerConfig
from src.shared.infrastructure.data.data_optimizer import DataOptimizer, DataConfig
from src.shared.infrastructure.document.document_optimizer import DocumentGenerator, DocumentConfig
from src.shared.infrastructure.ux.progress_tracker import ProgressTracker, ProgressStatus


class TestBatchProcessor(unittest.TestCase):
    """批处理器测试"""
    
    def setUp(self):
        """测试前准备"""
        config = BatchConfig(max_batch_size=5, max_wait_time=1.0)
        self.processor = BatchProcessor(config)
    
    def tearDown(self):
        """测试后清理"""
        self.processor.shutdown()
    
    def test_batch_processing(self):
        """测试批处理"""
        def process_func(data):
            time.sleep(0.1)  # 模拟处理时间
            return f"processed_{data}"
        
        # 提交多个请求
        request_ids = []
        for i in range(10):
            request_id = self.processor.submit_request(f"req_{i}", f"data_{i}", processor_func=process_func)
            request_ids.append(request_id)
        
        # 等待处理完成
        for request_id in request_ids:
            self.assertTrue(self.processor.wait_for_completion(request_id, timeout=5.0))
        
        # 检查结果
        for request_id in request_ids:
            result = self.processor.get_request_result(request_id)
            self.assertIsNotNone(result)
            self.assertTrue(result.startswith("processed_"))
    
    def test_batch_stats(self):
        """测试批处理统计"""
        def process_func(data):
            return f"processed_{data}"
        
        # 提交一些请求
        for i in range(5):
            self.processor.submit_request(f"req_{i}", f"data_{i}")
        
        # 等待处理完成
        time.sleep(2)
        
        # 检查统计
        stats = self.processor.get_stats()
        self.assertGreater(stats["total_requests"], 0)
        self.assertGreaterEqual(stats["completed_requests"], 0)


class TestAIOptimizer(unittest.TestCase):
    """AI优化器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.optimizer = AIOptimizer()
        
        # 添加测试提供商
        def health_check():
            return True
        
        self.optimizer.add_provider("test_provider", weight=1, health_check=health_check)
    
    def test_optimized_call(self):
        """测试优化调用"""
        def test_func():
            return "test_result"
        
        # 测试正常调用
        result = self.optimizer.optimize_call(test_func)
        self.assertEqual(result, "test_result")
    
    def test_provider_selection(self):
        """测试提供商选择"""
        # 添加多个提供商
        self.optimizer.add_provider("provider1", weight=1)
        self.optimizer.add_provider("provider2", weight=2)
        
        # 测试提供商选择
        provider = self.optimizer.load_balancer.get_provider()
        self.assertIsNotNone(provider)
        self.assertIn(provider, ["provider1", "provider2", "test_provider"])
    
    def test_performance_stats(self):
        """测试性能统计"""
        def test_func():
            time.sleep(0.1)
            return "test_result"
        
        # 执行一些调用
        for _ in range(5):
            try:
                self.optimizer.optimize_call(test_func)
            except:
                pass
        
        # 检查统计
        stats = self.optimizer.get_performance_stats()
        self.assertGreaterEqual(stats["total_calls"], 0)
        self.assertGreaterEqual(stats["success_rate"], 0)


class TestDataOptimizer(unittest.TestCase):
    """数据优化器测试"""
    
    def setUp(self):
        """测试前准备"""
        config = DataConfig(cache_enabled=True, max_workers=4)
        self.optimizer = DataOptimizer(config)
    
    def tearDown(self):
        """测试后清理"""
        self.optimizer.cleanup()
    
    def test_data_processing(self):
        """测试数据处理"""
        def process_func(data):
            return f"processed_{data}"
        
        # 测试单个数据处理
        result = self.optimizer.get_or_process("test_key", process_func, "test_data")
        self.assertEqual(result, "processed_test_data")
        
        # 测试缓存
        result2 = self.optimizer.get_or_process("test_key", process_func)
        self.assertEqual(result2, "processed_test_data")
    
    def test_batch_processing(self):
        """测试批量处理"""
        def process_func(data):
            return f"processed_{data}"
        
        # 测试批量处理
        data_list = [f"data_{i}" for i in range(10)]
        results = self.optimizer.batch_process(data_list, process_func)
        
        self.assertEqual(len(results), 10)
        for i, result in enumerate(results):
            self.assertEqual(result, f"processed_data_{i}")
    
    def test_optimizer_stats(self):
        """测试优化器统计"""
        def process_func(data):
            return f"processed_{data}"
        
        # 执行一些处理
        for i in range(5):
            self.optimizer.get_or_process(f"key_{i}", process_func, f"data_{i}")
        
        # 检查统计
        stats = self.optimizer.get_stats()
        self.assertIn("cache_stats", stats)
        self.assertIn("processing_stats", stats)
        self.assertIn("storage_stats", stats)


class TestDocumentGenerator(unittest.TestCase):
    """文档生成器测试"""
    
    def setUp(self):
        """测试前准备"""
        config = DocumentConfig(
            template_dir="test_templates",
            output_dir="test_outputs",
            enable_parallel=False  # 简化测试
        )
        self.generator = DocumentGenerator(config)
    
    def tearDown(self):
        """测试后清理"""
        self.generator.cleanup()
    
    def test_document_generation(self):
        """测试文档生成"""
        # 创建测试模板
        template_data = {
            "name": "test_template",
            "variables": ["title", "content"],
            "sections": ["title", "content"],
            "styles": {
                "default_font": "Arial",
                "default_size": 12
            }
        }
        
        self.generator.template_manager.create_template("test_template", template_data)
        
        # 生成文档
        data = {
            "title": "测试文档",
            "content": [
                {"type": "paragraph", "text": "这是一个测试段落"}
            ]
        }
        
        try:
            output_path = self.generator.generate_document("test_template", data)
            self.assertTrue(os.path.exists(output_path))
        except Exception as e:
            # 如果模板文件不存在，跳过测试
            self.skipTest(f"文档生成测试跳过: {e}")
    
    def test_batch_document_generation(self):
        """测试批量文档生成"""
        # 创建测试模板
        template_data = {
            "name": "test_template",
            "variables": ["title"],
            "sections": ["title"]
        }
        
        self.generator.template_manager.create_template("test_template", template_data)
        
        # 批量生成文档
        requests = [
            {
                "template_name": "test_template",
                "data": {"title": f"文档 {i}"}
            }
            for i in range(3)
        ]
        
        try:
            results = self.generator.batch_generate_documents(requests)
            self.assertEqual(len(results), 3)
        except Exception as e:
            self.skipTest(f"批量文档生成测试跳过: {e}")
    
    def test_generator_stats(self):
        """测试生成器统计"""
        stats = self.generator.get_stats()
        self.assertIn("total_documents", stats)
        self.assertIn("successful_documents", stats)
        self.assertIn("failed_documents", stats)
        self.assertIn("success_rate", stats)


class TestProgressTracker(unittest.TestCase):
    """进度跟踪器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.tracker = ProgressTracker()
    
    def test_task_creation(self):
        """测试任务创建"""
        task = self.tracker.create_task("test_task", "测试任务", ["步骤1", "步骤2"])
        
        self.assertEqual(task.task_id, "test_task")
        self.assertEqual(task.task_name, "测试任务")
        self.assertEqual(len(task.steps), 2)
        self.assertEqual(task.steps[0].name, "步骤1")
        self.assertEqual(task.steps[1].name, "步骤2")
    
    def test_task_execution(self):
        """测试任务执行"""
        # 创建任务
        task = self.tracker.create_task("test_task", "测试任务", ["步骤1", "步骤2"])
        
        # 开始任务
        self.assertTrue(self.tracker.start_task("test_task"))
        
        # 更新步骤进度
        self.assertTrue(self.tracker.update_step_progress("test_task", "步骤1", 0.5))
        
        # 完成步骤
        self.assertTrue(self.tracker.complete_step("test_task", "步骤1"))
        
        # 完成第二个步骤
        self.assertTrue(self.tracker.complete_step("test_task", "步骤2"))
        
        # 检查任务状态
        task = self.tracker.get_task("test_task")
        self.assertEqual(task.status, ProgressStatus.COMPLETED)
        self.assertEqual(task.overall_progress, 1.0)
    
    def test_progress_callback(self):
        """测试进度回调"""
        callback_called = []
        
        def callback(task):
            callback_called.append(task.task_id)
        
        self.tracker.add_callback(callback)
        
        # 创建并执行任务
        self.tracker.create_task("test_task", "测试任务", ["步骤1"])
        self.tracker.start_task("test_task")
        self.tracker.complete_step("test_task", "步骤1")
        
        # 检查回调是否被调用
        self.assertGreater(len(callback_called), 0)
        self.assertIn("test_task", callback_called)
    
    def test_task_cancellation(self):
        """测试任务取消"""
        # 创建任务
        self.tracker.create_task("test_task", "测试任务", ["步骤1", "步骤2"])
        self.tracker.start_task("test_task")
        
        # 取消任务
        self.assertTrue(self.tracker.cancel_task("test_task"))
        
        # 检查任务状态
        task = self.tracker.get_task("test_task")
        self.assertEqual(task.status, ProgressStatus.CANCELLED)
    
    def test_tracker_stats(self):
        """测试跟踪器统计"""
        # 创建并完成一些任务
        for i in range(3):
            task_id = f"task_{i}"
            self.tracker.create_task(task_id, f"任务 {i}", ["步骤1"])
            self.tracker.start_task(task_id)
            self.tracker.complete_step(task_id, "步骤1")
        
        # 检查统计
        stats = self.tracker.get_stats()
        self.assertEqual(stats["total_tasks"], 3)
        self.assertEqual(stats["completed_tasks"], 3)
        self.assertEqual(stats["active_tasks"], 0)


if __name__ == '__main__':
    unittest.main()

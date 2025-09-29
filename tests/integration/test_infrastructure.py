#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础设施集成测试
"""

import unittest
import time
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.shared.infrastructure.config.settings import ConfigManager
from src.shared.infrastructure.monitoring.metrics import MetricsCollector
from src.shared.infrastructure.monitoring.health_check import HealthChecker
from src.shared.infrastructure.cache.cache_manager import CacheManager, MemoryCacheBackend
from src.shared.infrastructure.security.encryption import EncryptionManager, InputValidator


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config_manager = ConfigManager()
    
    def test_config_loading(self):
        """测试配置加载"""
        # 测试默认配置
        self.assertIsNotNone(self.config_manager.database)
        self.assertIsNotNone(self.config_manager.ai)
        self.assertIsNotNone(self.config_manager.logging)
        self.assertIsNotNone(self.config_manager.cache)
        self.assertIsNotNone(self.config_manager.security)
        self.assertIsNotNone(self.config_manager.system)
    
    def test_config_get_set(self):
        """测试配置获取和设置"""
        # 测试设置配置
        self.config_manager.set("ai.default_model", "glm-4-flash")
        
        # 测试获取配置
        model = self.config_manager.get("ai.default_model")
        self.assertEqual(model, "glm-4-flash")
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试无效配置
        with self.assertRaises(Exception):
            self.config_manager.database.port = -1
            self.config_manager._validate_config()


class TestMetricsCollector(unittest.TestCase):
    """指标收集器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.metrics = MetricsCollector()
    
    def test_counter_increment(self):
        """测试计数器增加"""
        self.metrics.increment_counter("test.counter")
        self.metrics.increment_counter("test.counter", 5)
        
        summary = self.metrics.get_metrics_summary()
        self.assertEqual(summary["counters"]["test.counter"], 6)
    
    def test_gauge_set(self):
        """测试仪表设置"""
        self.metrics.set_gauge("test.gauge", 42.5)
        
        summary = self.metrics.get_metrics_summary()
        self.assertEqual(summary["gauges"]["test.gauge"], 42.5)
    
    def test_timer_recording(self):
        """测试计时器记录"""
        self.metrics.record_timer("test.timer", 1.5)
        self.metrics.record_timer("test.timer", 2.0)
        
        summary = self.metrics.get_metrics_summary()
        timer_stats = summary["timer_stats"]["test.timer"]
        self.assertEqual(timer_stats["count"], 2)
        self.assertEqual(timer_stats["avg"], 1.75)
    
    def test_ai_call_recording(self):
        """测试AI调用记录"""
        self.metrics.record_ai_call("zhipu", "glm-4", 2.5, True, 100, 0.01)
        
        summary = self.metrics.get_metrics_summary()
        # 检查是否有AI调用相关的计数器
        ai_counters = {k: v for k, v in summary["counters"].items() if "ai_calls" in k}
        self.assertGreater(len(ai_counters), 0)
    
    def test_function_timing_decorator(self):
        """测试函数计时装饰器"""
        @self.metrics.time_function("test.function")
        def test_function():
            time.sleep(0.1)
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        
        summary = self.metrics.get_metrics_summary()
        self.assertGreater(summary["timer_stats"]["test.function"]["count"], 0)


class TestHealthChecker(unittest.TestCase):
    """健康检查器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.health_checker = HealthChecker()
    
    def test_health_check_registration(self):
        """测试健康检查注册"""
        def test_check():
            from src.shared.infrastructure.monitoring.health_check import HealthCheckResult, HealthStatus
            return HealthCheckResult(
                name="test",
                status=HealthStatus.HEALTHY,
                message="Test check passed",
                response_time=0.1,
                timestamp=time.time()
            )
        
        self.health_checker.register_check("test", test_check)
        result = self.health_checker.run_check("test")
        
        self.assertEqual(result.name, "test")
        self.assertEqual(result.status.value, "healthy")
    
    def test_overall_status(self):
        """测试整体状态"""
        status = self.health_checker.get_overall_status()
        self.assertIn(status.value, ["healthy", "degraded", "unhealthy", "unknown"])
    
    def test_health_summary(self):
        """测试健康摘要"""
        summary = self.health_checker.get_health_summary()
        
        self.assertIn("overall_status", summary)
        self.assertIn("total_checks", summary)
        self.assertIn("checks", summary)


class TestCacheManager(unittest.TestCase):
    """缓存管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.cache = CacheManager(MemoryCacheBackend(max_size=10))
    
    def test_basic_operations(self):
        """测试基本操作"""
        # 测试设置和获取
        self.cache.set("key1", "value1", ttl=60)
        value = self.cache.get("key1")
        self.assertEqual(value, "value1")
        
        # 测试存在检查
        self.assertTrue(self.cache.exists("key1"))
        self.assertFalse(self.cache.exists("key2"))
        
        # 测试删除
        self.cache.delete("key1")
        self.assertFalse(self.cache.exists("key1"))
    
    def test_ttl_expiration(self):
        """测试TTL过期"""
        self.cache.set("key1", "value1", ttl=1)  # 1秒过期
        self.assertEqual(self.cache.get("key1"), "value1")
        
        time.sleep(1.1)  # 等待过期
        self.assertIsNone(self.cache.get("key1"))
    
    def test_get_or_set(self):
        """测试获取或设置"""
        def factory():
            return "generated_value"
        
        # 第一次调用应该生成值
        value1 = self.cache.get_or_set("key1", factory)
        self.assertEqual(value1, "generated_value")
        
        # 第二次调用应该从缓存获取
        value2 = self.cache.get_or_set("key1", factory)
        self.assertEqual(value2, "generated_value")
    
    def test_cache_decorator(self):
        """测试缓存装饰器"""
        call_count = 0
        
        @self.cache.cache_result(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # 第一次调用
        result1 = expensive_function(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(call_count, 1)
        
        # 第二次调用（应该从缓存获取）
        result2 = expensive_function(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(call_count, 1)  # 不应该再次调用函数


class TestEncryptionManager(unittest.TestCase):
    """加密管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.encryption = EncryptionManager()
    
    def test_encrypt_decrypt(self):
        """测试加密解密"""
        original_data = "sensitive_data_123"
        
        encrypted = self.encryption.encrypt(original_data)
        self.assertNotEqual(encrypted, original_data)
        
        decrypted = self.encryption.decrypt(encrypted)
        self.assertEqual(decrypted, original_data)
    
    def test_password_hashing(self):
        """测试密码哈希"""
        password = "test_password_123"
        
        hash_info = self.encryption.hash_password(password)
        self.assertIn("hash", hash_info)
        self.assertIn("salt", hash_info)
        
        # 验证密码
        self.assertTrue(self.encryption.verify_password(password, hash_info))
        self.assertFalse(self.encryption.verify_password("wrong_password", hash_info))
    
    def test_api_key_generation(self):
        """测试API密钥生成"""
        api_key = self.encryption.generate_api_key()
        self.assertIsInstance(api_key, str)
        self.assertGreater(len(api_key), 20)
    
    def test_hmac_signature(self):
        """测试HMAC签名"""
        data = "test_data"
        secret = "test_secret"
        
        signature = self.encryption.create_hmac_signature(data, secret)
        self.assertTrue(self.encryption.verify_hmac_signature(data, signature, secret))
        self.assertFalse(self.encryption.verify_hmac_signature(data, signature, "wrong_secret"))


class TestInputValidator(unittest.TestCase):
    """输入验证器测试"""
    
    def test_email_validation(self):
        """测试邮箱验证"""
        self.assertTrue(InputValidator.validate_email("test@example.com"))
        self.assertTrue(InputValidator.validate_email("user.name@domain.co.uk"))
        self.assertFalse(InputValidator.validate_email("invalid_email"))
        self.assertFalse(InputValidator.validate_email("@example.com"))
        self.assertFalse(InputValidator.validate_email("test@"))
    
    def test_password_strength(self):
        """测试密码强度"""
        # 弱密码
        weak_result = InputValidator.validate_password_strength("123")
        self.assertFalse(weak_result["valid"])
        self.assertGreater(len(weak_result["issues"]), 0)
        
        # 强密码
        strong_result = InputValidator.validate_password_strength("StrongP@ssw0rd123")
        self.assertTrue(strong_result["valid"])
        self.assertEqual(strong_result["score"], 5)
    
    def test_input_sanitization(self):
        """测试输入清理"""
        dangerous_input = "<script>alert('xss')</script>Hello World"
        sanitized = InputValidator.sanitize_input(dangerous_input)
        self.assertNotIn("<script>", sanitized)
        # HTML转义后alert仍然存在，但被转义了
        self.assertIn("alert", sanitized)  # 这是预期的，因为HTML转义
    
    def test_api_key_format_validation(self):
        """测试API密钥格式验证"""
        # 智谱AI密钥
        self.assertTrue(InputValidator.validate_api_key_format("sk-1234567890abcdef123", "zhipu"))
        self.assertFalse(InputValidator.validate_api_key_format("invalid_key", "zhipu"))
        
        # OpenAI密钥
        self.assertTrue(InputValidator.validate_api_key_format("sk-1234567890abcdef123", "openai"))
        self.assertFalse(InputValidator.validate_api_key_format("invalid_key", "openai"))


if __name__ == '__main__':
    unittest.main()

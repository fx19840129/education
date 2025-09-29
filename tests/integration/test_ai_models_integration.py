#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模型配置集成测试
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.shared.infrastructure.config.settings import ConfigManager


class TestAIModelsIntegration(unittest.TestCase):
    """AI模型配置集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.config_manager = ConfigManager()
    
    def test_ai_models_config_loading(self):
        """测试AI模型配置加载"""
        # 检查是否成功加载了AI模型配置
        self.assertIsNotNone(self.config_manager.ai)
        self.assertGreater(len(self.config_manager.ai.providers), 0)
        self.assertGreater(len(self.config_manager.ai.scenarios), 0)
    
    def test_provider_config_loading(self):
        """测试提供商配置加载"""
        # 检查智谱AI配置
        zhipu_provider = self.config_manager.get_ai_provider_config("zhipu")
        self.assertIsNotNone(zhipu_provider)
        self.assertEqual(zhipu_provider.name, "智谱AI")
        self.assertTrue(zhipu_provider.enabled)
        self.assertGreater(len(zhipu_provider.models), 0)
        
        # 检查DeepSeek配置
        deepseek_provider = self.config_manager.get_ai_provider_config("deepseek")
        self.assertIsNotNone(deepseek_provider)
        self.assertEqual(deepseek_provider.name, "DeepSeek")
        self.assertTrue(deepseek_provider.enabled)
    
    def test_model_config_loading(self):
        """测试模型配置加载"""
        # 检查智谱AI模型
        glm4_model = self.config_manager.get_ai_model_config("zhipu", "glm-4.5")
        self.assertIsNotNone(glm4_model)
        self.assertEqual(glm4_model.name, "glm-4.5")
        self.assertEqual(glm4_model.display_name, "智谱AI GLM-4.5")
        self.assertGreater(glm4_model.max_tokens, 0)
        self.assertGreater(glm4_model.cost_per_token, 0)
        
        # 检查DeepSeek模型
        deepseek_chat = self.config_manager.get_ai_model_config("deepseek", "deepseek-chat")
        self.assertIsNotNone(deepseek_chat)
        self.assertEqual(deepseek_chat.name, "deepseek-chat")
        self.assertTrue(deepseek_chat.supports_streaming)
    
    def test_scenario_config_loading(self):
        """测试场景配置加载"""
        # 检查学习内容生成场景
        learning_scenario = self.config_manager.get_ai_scenario_config("learning_content")
        self.assertIsNotNone(learning_scenario)
        self.assertEqual(learning_scenario.name, "学习内容生成")
        self.assertGreater(len(learning_scenario.preferred_models), 0)
        self.assertGreater(len(learning_scenario.fallback_models), 0)
        
        # 检查语法解释场景
        grammar_scenario = self.config_manager.get_ai_scenario_config("grammar_explanation")
        self.assertIsNotNone(grammar_scenario)
        self.assertEqual(grammar_scenario.name, "语法解释")
    
    def test_available_models(self):
        """测试可用模型获取"""
        # 获取所有可用模型
        all_models = self.config_manager.get_available_models()
        self.assertGreater(len(all_models), 0)
        
        # 检查是否包含预期的模型
        model_names = list(all_models.keys())
        self.assertIn("glm-4.5", model_names)
        self.assertIn("glm-4.5-flash", model_names)
        self.assertIn("deepseek-chat", model_names)
        
        # 获取特定提供商的模型
        zhipu_models = self.config_manager.get_available_models("zhipu")
        self.assertGreater(len(zhipu_models), 0)
        self.assertIn("glm-4.5", zhipu_models)
    
    def test_enabled_providers(self):
        """测试启用的提供商"""
        enabled_providers = self.config_manager.get_enabled_providers()
        self.assertGreater(len(enabled_providers), 0)
        
        # 检查智谱AI是否启用
        self.assertIn("zhipu", enabled_providers)
        self.assertTrue(enabled_providers["zhipu"].enabled)
        
        # 检查DeepSeek是否启用
        self.assertIn("deepseek", enabled_providers)
        self.assertTrue(enabled_providers["deepseek"].enabled)
    
    def test_model_for_scenario(self):
        """测试根据场景获取模型"""
        # 测试学习内容生成场景
        model_info = self.config_manager.get_model_for_scenario("learning_content")
        self.assertIsNotNone(model_info)
        provider_name, model_name = model_info
        self.assertIn(provider_name, ["zhipu", "deepseek"])
        self.assertIn(model_name, ["glm-4.5-turbo", "glm-4.5-flash"])
        
        # 测试语法解释场景
        model_info = self.config_manager.get_model_for_scenario("grammar_explanation")
        self.assertIsNotNone(model_info)
        provider_name, model_name = model_info
        self.assertIn(provider_name, ["zhipu", "deepseek"])
    
    def test_default_configuration(self):
        """测试默认配置"""
        # 检查默认提供商和模型
        self.assertEqual(self.config_manager.ai.default_provider, "zhipu")
        self.assertEqual(self.config_manager.ai.default_model, "glm-4.5-turbo")
        
        # 检查其他默认配置
        self.assertEqual(self.config_manager.ai.timeout, 60)
        self.assertEqual(self.config_manager.ai.max_retries, 3)
        self.assertTrue(self.config_manager.ai.load_balancing)
        self.assertTrue(self.config_manager.ai.cost_optimization)
        self.assertTrue(self.config_manager.ai.fallback_enabled)
    
    def test_routing_rules_loading(self):
        """测试路由规则加载"""
        routing_rules = self.config_manager.ai.routing_rules
        self.assertIsNotNone(routing_rules)
        self.assertIn("by_cost", routing_rules)
        self.assertIn("by_performance", routing_rules)
        self.assertIn("by_quality", routing_rules)
        
        # 检查成本路由规则
        cost_rule = routing_rules["by_cost"]
        self.assertTrue(cost_rule["enabled"])
        self.assertIn("glm-4.5-flash", cost_rule["order"])
    
    def test_monitoring_config_loading(self):
        """测试监控配置加载"""
        monitoring = self.config_manager.ai.monitoring
        self.assertIsNotNone(monitoring)
        self.assertTrue(monitoring["enabled"])
        self.assertTrue(monitoring["log_requests"])
        self.assertTrue(monitoring["performance_tracking"])
        self.assertTrue(monitoring["cost_tracking"])


if __name__ == '__main__':
    unittest.main()


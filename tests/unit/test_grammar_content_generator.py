#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语法内容生成器单元测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.english.plan_modules.content.grammar_content_generator import GrammarContentGenerator


class TestGrammarContentGenerator(unittest.TestCase):
    """语法内容生成器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_grammar_loader = Mock()
        self.generator = GrammarContentGenerator(self.mock_grammar_loader)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.generator.grammar_loader)
    
    def test_generate_grammar_content_elementary(self):
        """测试小学语法内容生成"""
        # 准备测试数据
        phase = {
            "grammar_level": "elementary"
        }
        
        mock_grammar_config = {
            "topics": [
                {
                    "name": "be动词",
                    "description": "be动词的基本用法",
                    "rules": ["I am", "You are", "He/She/It is"],
                    "examples": ["I am a student.", "You are my friend."],
                    "difficulty": "beginner",
                    "category": "grammar"
                }
            ]
        }
        
        self.mock_grammar_loader.get_grammar_config.return_value = mock_grammar_config
        
        # 执行测试
        result = self.generator.generate_grammar_content(day=1, phase=phase)
        
        # 验证结果
        self.assertIn("topics", result)
        self.assertIn("level", result)
        self.assertIn("day", result)
        self.assertIn("total_topics", result)
        self.assertEqual(result["level"], "elementary")
        self.assertEqual(result["day"], 1)
        self.assertEqual(result["total_topics"], 1)
        self.assertEqual(len(result["topics"]), 1)
        
        # 验证主题内容
        topic = result["topics"][0]
        self.assertEqual(topic["name"], "be动词")
        self.assertEqual(topic["description"], "be动词的基本用法")
        self.assertEqual(topic["difficulty"], "beginner")
        self.assertEqual(topic["category"], "grammar")
    
    def test_generate_grammar_content_middle_school(self):
        """测试中学语法内容生成"""
        phase = {
            "grammar_level": "middle_school"
        }
        
        mock_grammar_config = {
            "topics": [
                {
                    "name": "现在完成时",
                    "description": "现在完成时的构成和用法",
                    "rules": ["have/has + 过去分词"],
                    "examples": ["I have finished my homework."],
                    "difficulty": "intermediate",
                    "category": "grammar"
                }
            ]
        }
        
        self.mock_grammar_loader.get_grammar_config.return_value = mock_grammar_config
        
        result = self.generator.generate_grammar_content(day=1, phase=phase)
        
        self.assertEqual(result["level"], "middle_school")
        self.assertEqual(result["total_topics"], 1)
        
        topic = result["topics"][0]
        self.assertEqual(topic["name"], "现在完成时")
        self.assertEqual(topic["difficulty"], "intermediate")
    
    def test_generate_grammar_content_with_plan_config(self):
        """测试带计划配置的语法内容生成"""
        phase = {
            "grammar_level": "elementary"
        }
        plan_config = {
            "learning_config": {
                "daily_grammar_topics": 2
            }
        }
        
        mock_grammar_config = {
            "topics": [
                {
                    "name": "be动词",
                    "description": "be动词的基本用法",
                    "rules": ["I am", "You are"],
                    "examples": ["I am a student."],
                    "difficulty": "beginner",
                    "category": "grammar"
                },
                {
                    "name": "名词单复数",
                    "description": "名词单复数的变化规则",
                    "rules": ["一般加s", "以s,x,ch,sh结尾加es"],
                    "examples": ["cat -> cats", "box -> boxes"],
                    "difficulty": "beginner",
                    "category": "grammar"
                }
            ]
        }
        
        self.mock_grammar_loader.get_grammar_config.return_value = mock_grammar_config
        
        result = self.generator.generate_grammar_content(day=1, phase=phase, plan_config=plan_config)
        
        # 目前实现中，计划配置不会影响语法主题数量，因为按天循环选择
        self.assertEqual(result["total_topics"], 1)
    
    def test_no_grammar_config(self):
        """测试没有语法配置的情况"""
        phase = {
            "grammar_level": "elementary"
        }
        
        self.mock_grammar_loader.get_grammar_config.return_value = None
        
        result = self.generator.generate_grammar_content(day=1, phase=phase)
        
        self.assertEqual(result["topics"], [])
        self.assertEqual(result["total_topics"], 0)
    
    def test_topic_cycling(self):
        """测试主题循环选择"""
        phase = {
            "grammar_level": "elementary"
        }
        
        mock_grammar_config = {
            "topics": [
                {"name": "主题1", "description": "描述1", "rules": [], "examples": [], "difficulty": "beginner", "category": "grammar"},
                {"name": "主题2", "description": "描述2", "rules": [], "examples": [], "difficulty": "beginner", "category": "grammar"},
                {"name": "主题3", "description": "描述3", "rules": [], "examples": [], "difficulty": "beginner", "category": "grammar"}
            ]
        }
        
        self.mock_grammar_loader.get_grammar_config.return_value = mock_grammar_config
        
        # 测试第1天选择第一个主题
        result1 = self.generator.generate_grammar_content(day=1, phase=phase)
        self.assertEqual(result1["topics"][0]["name"], "主题1")
        
        # 测试第2天选择第二个主题
        result2 = self.generator.generate_grammar_content(day=2, phase=phase)
        self.assertEqual(result2["topics"][0]["name"], "主题2")
        
        # 测试第4天循环回第一个主题
        result4 = self.generator.generate_grammar_content(day=4, phase=phase)
        self.assertEqual(result4["topics"][0]["name"], "主题1")


if __name__ == '__main__':
    unittest.main()


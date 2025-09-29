#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词内容生成器单元测试
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.english.plan_modules.content.word_content_generator import WordContentGenerator
from src.english.plan_modules.word_database import WordInfo


class TestWordContentGenerator(unittest.TestCase):
    """单词内容生成器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_word_db = Mock()
        self.mock_fsrs_scheduler = Mock()
        self.generator = WordContentGenerator(self.mock_word_db, self.mock_fsrs_scheduler)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.generator.word_db)
        self.assertIsNotNone(self.generator.fsrs_scheduler)
        self.assertIsInstance(self.generator.part_of_speech_map, dict)
    
    def test_generate_word_content_basic(self):
        """测试基本单词内容生成"""
        # 准备测试数据
        phase = {
            "level": "elementary",
            "daily_words": 5
        }
        
        # 模拟单词数据库返回
        mock_words = [
            WordInfo(word="hello", chinese_meaning="你好", part_of_speech="interjection", pronunciation="/həˈloʊ/"),
            WordInfo(word="world", chinese_meaning="世界", part_of_speech="noun", pronunciation="/wɜːrld/"),
            WordInfo(word="good", chinese_meaning="好的", part_of_speech="adjective", pronunciation="/ɡʊd/"),
            WordInfo(word="morning", chinese_meaning="早晨", part_of_speech="noun", pronunciation="/ˈmɔːrnɪŋ/"),
            WordInfo(word="beautiful", chinese_meaning="美丽的", part_of_speech="adjective", pronunciation="/ˈbjuːtɪfl/")
        ]
        
        self.mock_word_db.get_words_by_level.return_value = mock_words
        
        # 执行测试
        result = self.generator.generate_word_content(day=1, phase=phase)
        
        # 验证结果
        self.assertIn("words", result)
        self.assertIn("total_count", result)
        self.assertIn("level", result)
        self.assertIn("day", result)
        self.assertEqual(result["total_count"], 5)
        self.assertEqual(result["level"], "elementary")
        self.assertEqual(result["day"], 1)
        self.assertEqual(len(result["words"]), 5)
    
    def test_generate_word_content_with_plan_config(self):
        """测试带计划配置的单词内容生成"""
        phase = {
            "level": "elementary",
            "daily_words": 5
        }
        plan_config = {
            "learning_config": {
                "daily_words": 3
            }
        }
        
        mock_words = [
            WordInfo(word="hello", chinese_meaning="你好", part_of_speech="interjection", pronunciation="/həˈloʊ/"),
            WordInfo(word="world", chinese_meaning="世界", part_of_speech="noun", pronunciation="/wɜːrld/"),
            WordInfo(word="good", chinese_meaning="好的", part_of_speech="adjective", pronunciation="/ɡʊd/")
        ]
        
        self.mock_word_db.get_words_by_level.return_value = mock_words
        
        result = self.generator.generate_word_content(day=1, phase=phase, plan_config=plan_config)
        
        # 应该使用计划配置中的单词数量
        self.assertEqual(result["total_count"], 3)
        self.assertEqual(len(result["words"]), 3)
    
    def test_word_to_dict(self):
        """测试单词对象转字典"""
        word = WordInfo(
            word="hello",
            chinese_meaning="你好",
            part_of_speech="interjection",
            pronunciation="/həˈloʊ/",
            example_sentence="Hello, world!",
            difficulty="beginner"
        )
        
        result = self.generator._word_to_dict(word)
        
        self.assertEqual(result["word"], "hello")
        self.assertEqual(result["meaning"], "你好")
        self.assertEqual(result["part_of_speech"], "interjection")
        self.assertEqual(result["part_of_speech_cn"], "感叹词")
        self.assertEqual(result["part_of_speech_abbr"], "interj.")
        self.assertEqual(result["phonetic"], "/həˈloʊ/")
        self.assertEqual(result["example_sentence"], "Hello, world!")
        self.assertEqual(result["difficulty"], "beginner")
    
    def test_middle_school_level(self):
        """测试中学级别单词生成"""
        phase = {
            "level": "middle_school",
            "daily_words": 3
        }
        
        mock_words = [
            WordInfo(word="sophisticated", chinese_meaning="复杂的", part_of_speech="adjective", pronunciation="/səˈfɪstɪkeɪtɪd/"),
            WordInfo(word="comprehensive", chinese_meaning="全面的", part_of_speech="adjective", pronunciation="/ˌkɑːmprɪˈhensɪv/"),
            WordInfo(word="extraordinary", chinese_meaning="非凡的", part_of_speech="adjective", pronunciation="/ɪkˈstrɔːrdəneri/")
        ]
        
        self.mock_word_db.get_words_by_level.return_value = mock_words
        
        result = self.generator.generate_word_content(day=1, phase=phase)
        
        self.assertEqual(result["level"], "middle_school")
        self.assertEqual(result["total_count"], 3)


if __name__ == '__main__':
    unittest.main()

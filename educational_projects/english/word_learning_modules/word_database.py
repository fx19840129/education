#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语单词数据库模块
管理小学和初中英语单词数据
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class WordInfo:
    """单词信息数据类"""
    word: str
    pronunciation: str
    part_of_speech: str
    chinese_meaning: str
    english_meaning: str
    example_sentence: str
    difficulty: str
    grade_level: str
    category: str
    synonyms: List[str] = None
    antonyms: List[str] = None
    collocations: List[str] = None


class WordDatabase:
    """英语单词数据库管理类"""
    
    def __init__(self, config_dir: str = "word_configs"):
        self.config_dir = config_dir
        self.elementary_words: Dict[str, WordInfo] = {}
        self.middle_school_words: Dict[str, WordInfo] = {}
        self._load_word_data()
    
    def _load_word_data(self):
        """加载单词数据"""
        # 加载小学单词
        elementary_file = os.path.join(self.config_dir, "elementary_words.json")
        if os.path.exists(elementary_file):
            self.elementary_words = self._load_words_from_file(elementary_file)
        
        # 加载初中单词
        middle_school_file = os.path.join(self.config_dir, "middle_school_words.json")
        if os.path.exists(middle_school_file):
            self.middle_school_words = self._load_words_from_file(middle_school_file)
    
    def _load_words_from_file(self, file_path: str) -> Dict[str, WordInfo]:
        """从JSON文件加载单词数据"""
        words = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for word_data in data.get('words', []):
                    word_info = WordInfo(
                        word=word_data['word'],
                        pronunciation=word_data.get('pronunciation', ''),
                        part_of_speech=word_data.get('part_of_speech', ''),
                        chinese_meaning=word_data.get('chinese_meaning', ''),
                        english_meaning=word_data.get('english_meaning', ''),
                        example_sentence=word_data.get('example_sentence', ''),
                        difficulty=word_data.get('difficulty', 'easy'),
                        grade_level=word_data.get('grade_level', ''),
                        category=word_data.get('category', ''),
                        synonyms=word_data.get('synonyms', []),
                        antonyms=word_data.get('antonyms', []),
                        collocations=word_data.get('collocations', [])
                    )
                    words[word_info.word.lower()] = word_info
        except Exception as e:
            print(f"加载单词文件失败 {file_path}: {e}")
        return words
    
    def get_words_by_level(self, level: str) -> Dict[str, WordInfo]:
        """根据年级获取单词"""
        if level == "elementary":
            return self.elementary_words
        elif level == "middle_school":
            return self.middle_school_words
        else:
            return {}
    
    def get_words_by_difficulty(self, level: str, difficulty: str) -> Dict[str, WordInfo]:
        """根据难度获取单词"""
        words = self.get_words_by_level(level)
        return {word: info for word, info in words.items() 
                if info.difficulty == difficulty}
    
    def get_words_by_category(self, level: str, category: str) -> Dict[str, WordInfo]:
        """根据分类获取单词"""
        words = self.get_words_by_level(level)
        return {word: info for word, info in words.items() 
                if info.category == category}
    
    def get_random_words(self, level: str, count: int, difficulty: str = None, 
                        category: str = None) -> List[WordInfo]:
        """获取随机单词"""
        import random
        
        words = self.get_words_by_level(level)
        
        if difficulty:
            words = {word: info for word, info in words.items() 
                    if info.difficulty == difficulty}
        
        if category:
            words = {word: info for word, info in words.items() 
                    if info.category == category}
        
        word_list = list(words.values())
        return random.sample(word_list, min(count, len(word_list)))
    
    def search_words(self, level: str, keyword: str) -> List[WordInfo]:
        """搜索单词"""
        words = self.get_words_by_level(level)
        results = []
        keyword_lower = keyword.lower()
        
        for word_info in words.values():
            if (keyword_lower in word_info.word.lower() or
                keyword_lower in word_info.chinese_meaning.lower() or
                keyword_lower in word_info.english_meaning.lower()):
                results.append(word_info)
        
        return results
    
    def get_word_info(self, word: str, level: str = None) -> Optional[WordInfo]:
        """获取特定单词信息"""
        word_lower = word.lower()
        
        if level == "elementary" or level is None:
            if word_lower in self.elementary_words:
                return self.elementary_words[word_lower]
        
        if level == "middle_school" or level is None:
            if word_lower in self.middle_school_words:
                return self.middle_school_words[word_lower]
        
        return None
    
    def get_categories(self, level: str) -> List[str]:
        """获取分类列表"""
        words = self.get_words_by_level(level)
        categories = set()
        for word_info in words.values():
            if word_info.category:
                categories.add(word_info.category)
        return sorted(list(categories))
    
    def get_difficulties(self, level: str) -> List[str]:
        """获取难度列表"""
        words = self.get_words_by_level(level)
        difficulties = set()
        for word_info in words.values():
            if word_info.difficulty:
                difficulties.add(word_info.difficulty)
        return sorted(list(difficulties))
    
    def get_word_count(self, level: str) -> int:
        """获取单词总数"""
        return len(self.get_words_by_level(level))
    
    def get_word_count_by_difficulty(self, level: str, difficulty: str) -> int:
        """根据难度获取单词数量"""
        return len(self.get_words_by_difficulty(level, difficulty))
    
    def get_word_count_by_category(self, level: str, category: str) -> int:
        """根据分类获取单词数量"""
        return len(self.get_words_by_category(level, category))

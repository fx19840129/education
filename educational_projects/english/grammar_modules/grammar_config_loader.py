#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语法配置加载器
负责加载和管理语法配置文件
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class GrammarConfigLoader:
    """语法配置加载器"""
    
    def __init__(self, config_dir: str = "grammar_configs"):
        """
        初始化配置加载器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.elementary_dir = self.config_dir / "elementary"
        self.middle_school_dir = self.config_dir / "middle_school"
        
    def load_grammar_config(self, grammar_name: str, level: str = "elementary") -> Optional[Dict[str, Any]]:
        """
        加载指定语法点的配置
        
        Args:
            grammar_name: 语法点名称
            level: 年级级别 (elementary/middle_school)
            
        Returns:
            语法配置字典，如果未找到返回None
        """
        config_file = self._get_config_file(grammar_name, level)
        if not config_file or not config_file.exists():
            return None
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败 {config_file}: {e}")
            return None
    
    def load_all_grammar_configs(self, level: str = "elementary") -> Dict[str, Dict[str, Any]]:
        """
        加载指定级别的所有语法配置
        
        Args:
            level: 年级级别 (elementary/middle_school)
            
        Returns:
            所有语法配置的字典
        """
        configs = {}
        config_dir = self.elementary_dir if level == "elementary" else self.middle_school_dir
        
        if not config_dir.exists():
            return configs
            
        for config_file in config_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    grammar_name = config.get("grammar_name", config_file.stem)
                    configs[grammar_name] = config
            except Exception as e:
                print(f"加载配置文件失败 {config_file}: {e}")
                
        return configs
    
    def get_available_grammars(self, level: str = "elementary") -> List[str]:
        """
        获取可用的语法点列表
        
        Args:
            level: 年级级别 (elementary/middle_school)
            
        Returns:
            语法点名称列表
        """
        configs = self.load_all_grammar_configs(level)
        return list(configs.keys())
    
    def _get_config_file(self, grammar_name: str, level: str) -> Optional[Path]:
        """
        获取配置文件路径
        
        Args:
            grammar_name: 语法点名称
            level: 年级级别
            
        Returns:
            配置文件路径
        """
        # 将语法名称转换为文件名
        file_name = self._grammar_name_to_filename(grammar_name)
        
        if level == "elementary":
            return self.elementary_dir / f"{file_name}.json"
        elif level == "middle_school":
            return self.middle_school_dir / f"{file_name}.json"
        else:
            return None
    
    def _grammar_name_to_filename(self, grammar_name: str) -> str:
        """
        将语法名称转换为文件名
        
        Args:
            grammar_name: 语法名称
            
        Returns:
            文件名
        """
        # 简单的名称映射
        name_mapping = {
            "be动词用法": "be_verb",
            "名词单复数": "noun_plural",
            "名词单复数-基础规则": "noun_plural_basic",
            "名词单复数-es结尾": "noun_plural_es_ending",
            "名词单复数-y结尾": "noun_plural_y_ending",
            "名词单复数-f/-fe结尾": "noun_plural_f_fe_ending",
            "名词单复数-不规则变化": "noun_plural_irregular",
            "名词单复数-特殊情况": "noun_plural_special",
            "人称代词": "pronouns",
            "一般现在时": "present_simple",
            "一般现在时-基础用法": "present_simple_basic",
            "一般现在时-第三人称单数": "present_simple_third_person",
            "一般现在时-否定形式": "present_simple_negative",
            "一般现在时-疑问形式": "present_simple_questions",
            "一般现在时-频率副词": "present_simple_adverbs",
            "一般现在时-综合应用": "present_simple_comprehensive",
            "现在进行时": "present_continuous",
            "现在进行时-基础用法": "present_continuous_basic",
            "现在进行时-动词ing变化": "present_continuous_ing",
            "一般过去时": "past_simple",
            "一般过去时-基础用法": "past_simple_basic",
            "一般过去时-规则动词": "past_simple_regular",
            "一般过去时-不规则动词": "past_simple_irregular",
            "形容词比较级和最高级": "comparative_superlative",
            "形容词比较级-基础用法": "comparative_basic",
            "形容词最高级-基础用法": "superlative_basic",
            "there be句型": "there_be",
            "there be句型-基础用法": "there_be_basic",
            "there be句型-否定和疑问": "there_be_negative_questions",
            "现在完成时": "present_perfect",
            "现在完成时-基础用法": "present_perfect_basic",
            "现在完成时-持续用法": "present_perfect_continuous",
            "过去进行时": "past_continuous",
            "过去进行时-基础用法": "past_continuous_basic",
            "被动语态": "passive_voice",
            "被动语态-基础用法": "passive_voice_basic",
            "被动语态-时态变化": "passive_voice_tense",
            "情态动词": "modal_verbs",
            "情态动词-基础用法": "modal_verbs_basic",
            "情态动词-含义用法": "modal_verbs_meaning",
            "条件句": "conditional_sentences",
            "条件句-基础用法": "conditional_sentences_basic",
            "条件句-类型用法": "conditional_sentences_types",
            "定语从句": "relative_clauses",
            "定语从句-基础用法": "relative_clauses_basic",
            "定语从句-关系代词": "relative_clauses_pronouns",
            "状语从句": "adverbial_clauses",
            "间接引语": "reported_speech",
            "间接引语-基础用法": "reported_speech_basic",
            "间接引语-时态变化": "reported_speech_tense",
            "虚拟语气": "subjunctive_mood"
        }
        
        return name_mapping.get(grammar_name, grammar_name.replace(" ", "_").lower())
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置文件格式是否正确
        
        Args:
            config: 配置字典
            
        Returns:
            是否有效
        """
        required_fields = [
            "grammar_name", "level", "category", "difficulty", 
            "description", "explanation", "examples", "exercise_templates"
        ]
        
        for field in required_fields:
            if field not in config:
                print(f"配置文件缺少必需字段: {field}")
                return False
                
        return True
    
    def get_grammar_by_difficulty(self, level: str = "elementary", difficulty: str = "easy") -> List[Dict[str, Any]]:
        """
        根据难度获取语法点
        
        Args:
            level: 年级级别
            difficulty: 难度级别
            
        Returns:
            指定难度的语法点列表
        """
        configs = self.load_all_grammar_configs(level)
        return [config for config in configs.values() if config.get("difficulty") == difficulty]
    
    def search_grammar(self, keyword: str, level: str = "elementary") -> List[Dict[str, Any]]:
        """
        搜索包含关键词的语法点
        
        Args:
            keyword: 搜索关键词
            level: 年级级别
            
        Returns:
            匹配的语法点列表
        """
        configs = self.load_all_grammar_configs(level)
        results = []
        
        for config in configs.values():
            if (keyword.lower() in config.get("grammar_name", "").lower() or
                keyword.lower() in config.get("description", "").lower() or
                keyword.lower() in config.get("category", "").lower()):
                results.append(config)
                
        return results


if __name__ == "__main__":
    # 测试配置加载器
    loader = GrammarConfigLoader()
    
    # 测试加载所有小学语法配置
    print("=== 小学语法配置 ===")
    elementary_configs = loader.load_all_grammar_configs("elementary")
    for name, config in elementary_configs.items():
        print(f"- {name}: {config.get('description', '')}")
    
    # 测试加载所有初中语法配置
    print("\n=== 初中语法配置 ===")
    middle_school_configs = loader.load_all_grammar_configs("middle_school")
    for name, config in middle_school_configs.items():
        print(f"- {name}: {config.get('description', '')}")
    
    # 测试搜索功能
    print("\n=== 搜索'动词'相关语法 ===")
    verb_configs = loader.search_grammar("动词", "elementary")
    for config in verb_configs:
        print(f"- {config.get('grammar_name', '')}: {config.get('description', '')}")

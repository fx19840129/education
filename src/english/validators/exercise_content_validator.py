#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语练习题验证器
基于通用框架的英语学科特定实现
"""

import re
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加共享框架路径
import sys
import os

from src.shared.learning_framework.validation.base_exercise_validator import BaseExerciseValidator, ValidationRule


class EnglishExerciseValidator(BaseExerciseValidator):
    """英语练习题验证器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("english", config)
        
        # 英语特定的不可数名词
        self.uncountable_nouns = {
            'water', 'milk', 'juice', 'coffee', 'tea', 'oil', 'air', 
            'music', 'information', 'news', 'advice', 'money', 'time',
            'weather', 'homework', 'work', 'furniture', 'equipment',
            'bread', 'rice', 'sugar', 'salt', 'flour', 'meat', 'fish',
            'cheese', 'butter', 'honey', 'jam', 'soup', 'salad'
        }
        
        # 英语特定的不规则动词
        self.irregular_verbs = {
            'go': {'past': 'went', 'past_participle': 'gone', 'third_person': 'goes'},
            'have': {'past': 'had', 'past_participle': 'had', 'third_person': 'has'},
            'do': {'past': 'did', 'past_participle': 'done', 'third_person': 'does'},
            'make': {'past': 'made', 'past_participle': 'made', 'third_person': 'makes'},
            'take': {'past': 'took', 'past_participle': 'taken', 'third_person': 'takes'},
            'see': {'past': 'saw', 'past_participle': 'seen', 'third_person': 'sees'},
            'come': {'past': 'came', 'past_participle': 'come', 'third_person': 'comes'},
            'give': {'past': 'gave', 'past_participle': 'given', 'third_person': 'gives'},
            'write': {'past': 'wrote', 'past_participle': 'written', 'third_person': 'writes'},
            'read': {'past': 'read', 'past_participle': 'read', 'third_person': 'reads'},
            'speak': {'past': 'spoke', 'past_participle': 'spoken', 'third_person': 'speaks'},
            'break': {'past': 'broke', 'past_participle': 'broken', 'third_person': 'breaks'},
            'choose': {'past': 'chose', 'past_participle': 'chosen', 'third_person': 'chooses'},
            'drive': {'past': 'drove', 'past_participle': 'driven', 'third_person': 'drives'},
            'eat': {'past': 'ate', 'past_participle': 'eaten', 'third_person': 'eats'},
            'fall': {'past': 'fell', 'past_participle': 'fallen', 'third_person': 'falls'},
            'feel': {'past': 'felt', 'past_participle': 'felt', 'third_person': 'feels'},
            'find': {'past': 'found', 'past_participle': 'found', 'third_person': 'finds'},
            'get': {'past': 'got', 'past_participle': 'gotten', 'third_person': 'gets'},
            'know': {'past': 'knew', 'past_participle': 'known', 'third_person': 'knows'},
        }
    
    def _init_validation_rules(self):
        """初始化学科特定的验证规则"""
        self.validation_rules = [
            ValidationRule(
                name="uncountable_noun_article",
                pattern=r'\ba\s+(water|milk|air|music|information|news|advice|money|time|weather|homework|work|furniture|equipment|bread|rice|sugar|salt|flour|meat|fish|cheese|butter|honey|jam|soup|salad)\b',
                error_message="不可数名词不能使用不定冠词a",
                suggestion="使用some或直接使用名词，如：some water, music",
                weight=2.0
            ),
            ValidationRule(
                name="i_am_adjective",
                pattern=r'\bI\s+am\s+(nice|good|bad|happy|sad|tired|hungry|thirsty)\s*[^a-zA-Z]',
                error_message="I am + 形容词的表达不够自然",
                suggestion="使用更具体的表达，如：I feel tired, I look happy",
                weight=1.5
            ),
            ValidationRule(
                name="i_like_adjective",
                pattern=r'\bI\s+like\s+(nice|good|bad|happy|sad|big|small|tall|short)\s*[^a-zA-Z]',
                error_message="不能直接说I like + 形容词",
                suggestion="使用名词形式，如：I like nice things, I like big houses",
                weight=2.0
            ),
            ValidationRule(
                name="pronoun_article",
                pattern=r'\bThis\s+is\s+a\s+(they|we|you|I|he|she|it)\b',
                error_message="代词前不能使用冠词",
                suggestion="直接使用代词，如：This is he, This is she",
                weight=2.5
            ),
            ValidationRule(
                name="plural_subject_verb",
                pattern=r'\b(cat|dog|book|table|student|teacher|car|house)s\s+is\b',
                error_message="复数名词应该用are而不是is",
                suggestion="使用are，如：The cats are sleeping",
                weight=2.0
            ),
            ValidationRule(
                name="third_person_singular",
                pattern=r'\b(He|She|It)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s',
                error_message="第三人称单数后动词应该加-s或变形",
                suggestion="使用第三人称单数形式，如：He works, She studies",
                weight=2.0
            ),
            ValidationRule(
                name="there_are_verb",
                pattern=r'\bThere\s+are\s+many\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s+here\b',
                error_message="动词不能直接用在'There are many _____ here'句型中",
                suggestion="使用名词形式，如：There are many students here",
                weight=2.0
            ),
            ValidationRule(
                name="there_are_adjective",
                pattern=r'\bThere\s+are\s+many\s+(nice|good|bad|happy|sad|big|small|tall|short)\s+here\b',
                error_message="形容词不能直接用在'There are many _____ here'句型中",
                suggestion="使用名词形式，如：There are many nice books here",
                weight=2.0
            ),
            ValidationRule(
                name="double_negative",
                pattern=r'\b(doesn\'t|don\'t|won\'t|can\'t|shouldn\'t|wouldn\'t)\s+\w+\s+(no|not|never|nothing|nobody|nowhere)\b',
                error_message="英语中不能使用双重否定",
                suggestion="使用单重否定，如：I don't have any money",
                weight=2.5
            ),
            ValidationRule(
                name="incomplete_sentence",
                pattern=r'^[A-Z][^.!?]*$',
                error_message="句子不完整，缺少标点符号",
                suggestion="添加适当的标点符号",
                weight=1.0
            )
        ]
    
    def _init_hint_templates(self):
        """初始化学科特定的提示模板"""
        self.hint_templates = {
            "一般现在时": {
                "third_person": "提示：一般现在时第三人称单数，动词要加-s或变形",
                "negative": "提示：一般现在时否定句，用don't/doesn't + 动词原形",
                "question": "提示：一般现在时疑问句，用Do/Does + 主语 + 动词原形",
                "general": "提示：一般现在时表示经常性的动作或状态"
            },
            "名词单复数": {
                "plural": "提示：复数名词变化规则：一般加-s，以s/x/ch/sh结尾加-es",
                "countable": "提示：可数名词前可以用a/an，不可数名词不能用",
                "irregular": "提示：不规则复数变化：child→children, man→men, woman→women",
                "general": "提示：注意名词的单复数形式"
            },
            "一般过去时": {
                "regular": "提示：规则动词过去式加-ed",
                "irregular": "提示：不规则动词过去式变化：go→went, see→saw",
                "past_time": "提示：一般过去时常用yesterday, last等时间状语",
                "general": "提示：一般过去时表示过去发生的动作或状态"
            },
            "现在进行时": {
                "structure": "提示：现在进行时 = be + 动词-ing",
                "ing_rules": "提示：动词-ing变化规则：一般加-ing，以e结尾去e加-ing",
                "time": "提示：现在进行时常用now, at the moment等时间状语",
                "general": "提示：现在进行时表示正在进行的动作"
            },
            "现在完成时": {
                "structure": "提示：现在完成时 = have/has + 过去分词",
                "past_participle": "提示：过去分词变化规则：规则动词加-ed，不规则动词需记忆",
                "time": "提示：现在完成时常用already, just, ever等副词",
                "general": "提示：现在完成时表示过去发生但对现在有影响的动作"
            },
            "被动语态": {
                "structure": "提示：被动语态 = be + 过去分词",
                "agent": "提示：被动语态可以用by引出动作执行者",
                "general": "提示：被动语态强调动作的承受者"
            },
            "情态动词": {
                "structure": "提示：情态动词 + 动词原形",
                "meaning": "提示：不同情态动词表达不同语气和态度",
                "general": "提示：情态动词表示能力、可能性、必要性等"
            },
            "冠词": {
                "a_an": "提示：a用于辅音音素开头的词，an用于元音音素开头的词",
                "the": "提示：the用于特指或双方都知道的事物",
                "zero": "提示：零冠词用于复数名词、不可数名词等",
                "general": "提示：注意冠词的正确使用"
            }
        }
    
    def _init_error_patterns(self):
        """初始化学科特定的错误模式"""
        self.error_patterns = [
            (r'\ba\s+(water|milk|air|music|information|news|advice|money|time|weather|homework|work|furniture|equipment|bread|rice|sugar|salt|flour|meat|fish|cheese|butter|honey|jam|soup|salad)\b', '不可数名词不能使用不定冠词a', 2.0),
            (r'\bI\s+am\s+(nice|good|bad|happy|sad|tired|hungry|thirsty)\s*[^a-zA-Z]', 'I am + 形容词的表达不够自然', 1.5),
            (r'\bI\s+like\s+(nice|good|bad|happy|sad|big|small|tall|short)\s*[^a-zA-Z]', '不能直接说I like + 形容词', 2.0),
            (r'\bThis\s+is\s+a\s+(they|we|you|I|he|she|it)\b', '代词前不能使用冠词', 2.5),
            (r'\b(cat|dog|book|table|student|teacher|car|house)s\s+is\b', '复数名词应该用are而不是is', 2.0),
            (r'\b(He|She|It)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s', '第三人称单数后动词应该加-s或变形', 2.0),
            (r'\bThere\s+are\s+many\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s+here\b', '动词不能直接用在"There are many _____ here"句型中', 2.0),
            (r'\bThere\s+are\s+many\s+(nice|good|bad|happy|sad|big|small|tall|short)\s+here\b', '形容词不能直接用在"There are many _____ here"句型中，需要搭配名词', 2.0),
            (r'\b(doesn\'t|don\'t|won\'t|can\'t|shouldn\'t|wouldn\'t)\s+\w+\s+(no|not|never|nothing|nobody|nowhere)\b', '英语中不能使用双重否定', 2.5),
            (r'^[A-Z][^.!?]*$', '句子不完整，缺少标点符号', 1.0)
        ]
    
    def _validate_subject_specific(self, exercise: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证英语学科特定内容"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        question = exercise.get('question', '')
        answer = exercise.get('correct_answer', '')
        topic = exercise.get('topic', '')
        
        # 检查英语特定的语法规则
        for rule in self.validation_rules:
            if re.search(rule.pattern, question, re.IGNORECASE):
                issues.append(f"语法错误: {rule.error_message}")
                suggestions.append(rule.suggestion)
                penalty += rule.weight
            
            if re.search(rule.pattern, answer, re.IGNORECASE):
                issues.append(f"答案语法错误: {rule.error_message}")
                suggestions.append(rule.suggestion)
                penalty += rule.weight
        
        # 检查不可数名词使用
        uncountable_issues = self._check_uncountable_nouns(question, answer)
        issues.extend(uncountable_issues['issues'])
        suggestions.extend(uncountable_issues['suggestions'])
        penalty += uncountable_issues['penalty']
        
        # 检查动词时态一致性
        tense_issues = self._check_tense_consistency(question, answer, topic)
        issues.extend(tense_issues['issues'])
        suggestions.extend(tense_issues['suggestions'])
        penalty += tense_issues['penalty']
        
        # 检查冠词使用
        article_issues = self._check_article_usage(question, answer)
        issues.extend(article_issues['issues'])
        suggestions.extend(article_issues['suggestions'])
        penalty += article_issues['penalty']
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _check_uncountable_nouns(self, question: str, answer: str) -> Dict[str, Any]:
        """检查不可数名词使用"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        # 检查问题中的不可数名词
        for noun in self.uncountable_nouns:
            pattern = rf'\ba\s+{noun}\b'
            if re.search(pattern, question, re.IGNORECASE):
                issues.append(f"不可数名词'{noun}'不能使用不定冠词a")
                suggestions.append(f"使用some {noun}或直接使用{noun}")
                penalty += 2.0
            
            if re.search(pattern, answer, re.IGNORECASE):
                issues.append(f"答案中不可数名词'{noun}'不能使用不定冠词a")
                suggestions.append(f"使用some {noun}或直接使用{noun}")
                penalty += 2.0
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _check_tense_consistency(self, question: str, answer: str, topic: str) -> Dict[str, Any]:
        """检查时态一致性"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        # 根据语法主题检查时态一致性
        if "过去时" in topic:
            # 检查过去时标志词
            past_time_words = ['yesterday', 'last', 'ago', 'before', 'then']
            has_past_time = any(word in question.lower() for word in past_time_words)
            
            if not has_past_time and not any(word in answer.lower() for word in past_time_words):
                issues.append("过去时题目缺少时间标志词")
                suggestions.append("添加yesterday, last week等时间状语")
                penalty += 1.0
        
        elif "进行时" in topic:
            # 检查进行时标志词
            progressive_time_words = ['now', 'at the moment', 'currently', 'right now']
            has_progressive_time = any(word in question.lower() for word in progressive_time_words)
            
            if not has_progressive_time and not any(word in answer.lower() for word in progressive_time_words):
                issues.append("进行时题目缺少时间标志词")
                suggestions.append("添加now, at the moment等时间状语")
                penalty += 1.0
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _check_article_usage(self, question: str, answer: str) -> Dict[str, Any]:
        """检查冠词使用"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        # 检查a/an的使用
        a_pattern = r'\ba\s+[aeiouAEIOU]'
        an_pattern = r'\ban\s+[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]'
        
        if re.search(a_pattern, question, re.IGNORECASE):
            issues.append("a后跟元音音素开头的词，应使用an")
            suggestions.append("检查冠词a/an的使用规则")
            penalty += 1.5
        
        if re.search(an_pattern, question, re.IGNORECASE):
            issues.append("an后跟辅音音素开头的词，应使用a")
            suggestions.append("检查冠词a/an的使用规则")
            penalty += 1.5
        
        if re.search(a_pattern, answer, re.IGNORECASE):
            issues.append("答案中a后跟元音音素开头的词，应使用an")
            suggestions.append("检查冠词a/an的使用规则")
            penalty += 1.5
        
        if re.search(an_pattern, answer, re.IGNORECASE):
            issues.append("答案中an后跟辅音音素开头的词，应使用a")
            suggestions.append("检查冠词a/an的使用规则")
            penalty += 1.5
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _generate_hint(self, exercise: Dict[str, Any]) -> str:
        """生成英语特定的提示"""
        topic = exercise.get('topic', '')
        difficulty = exercise.get('difficulty', 'medium')
        
        # 从英语特定的提示模板中获取
        if topic in self.hint_templates:
            topic_hints = self.hint_templates[topic]
            if difficulty in topic_hints:
                return topic_hints[difficulty]
            elif 'general' in topic_hints:
                return topic_hints['general']
        
        # 默认英语提示
        return "请仔细阅读题目，注意英语语法规则和词汇用法。"
    
    def _generate_explanation(self, exercise: Dict[str, Any]) -> str:
        """生成英语特定的解释"""
        topic = exercise.get('topic', '')
        answer = exercise.get('correct_answer', '')
        
        if topic and answer:
            return f"正确答案是 {answer}。这涉及到{topic}的相关语法规则和词汇用法。"
        elif answer:
            return f"正确答案是 {answer}。请参考相关语法知识点进行解答。"
        else:
            return "请参考英语语法知识点进行解答。"

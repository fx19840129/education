#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语句子验证器
基于通用框架的英语学科特定实现
"""

import re
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加共享框架路径
import sys
import os

from src.shared.learning_framework.validation.base_sentence_validator import BaseSentenceValidator, SentenceTemplate, ValidationLevel


class EnglishSentenceValidator(BaseSentenceValidator):
    """英语句子验证器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("english", config)
        
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
        
        # 英语特定的不可数名词
        self.uncountable_nouns = {
            'water', 'milk', 'juice', 'coffee', 'tea', 'oil', 'air', 
            'music', 'information', 'news', 'advice', 'money', 'time',
            'weather', 'homework', 'work', 'furniture', 'equipment',
            'bread', 'rice', 'sugar', 'salt', 'flour', 'meat', 'fish',
            'cheese', 'butter', 'honey', 'jam', 'soup', 'salad'
        }
    
    def _init_templates(self):
        """初始化学科特定的模板"""
        self.templates = {
            "一般现在时": [
                SentenceTemplate(
                    pattern="I {verb} every day.",
                    chinese_pattern="我每天{verb_cn}。",
                    word_types=["verb"],
                    grammar_topics=["一般现在时-基础用法"],
                    difficulty="easy",
                    examples=[{"verb": "work", "verb_cn": "工作"}],
                    validation_rules=["verb_form", "tense_consistency"]
                ),
                SentenceTemplate(
                    pattern="He {verb_3rd} {noun} every morning.",
                    chinese_pattern="他每天早上{verb_cn}{noun_cn}。",
                    word_types=["verb", "noun"],
                    grammar_topics=["一般现在时-第三人称单数"],
                    difficulty="easy",
                    examples=[{"verb": "reads", "verb_cn": "读", "noun": "books", "noun_cn": "书"}],
                    validation_rules=["third_person_singular", "verb_form"]
                ),
                SentenceTemplate(
                    pattern="This is a {adjective} {noun}.",
                    chinese_pattern="这是一个{adjective_cn}的{noun_cn}。",
                    word_types=["adjective", "noun"],
                    grammar_topics=["一般现在时-基础用法"],
                    difficulty="easy",
                    examples=[{"adjective": "nice", "adjective_cn": "好", "noun": "book", "noun_cn": "书"}],
                    validation_rules=["article_usage", "adjective_noun_order"]
                )
            ],
            "名词单复数": [
                SentenceTemplate(
                    pattern="I have two {noun_plural}.",
                    chinese_pattern="我有两个{noun_cn}。",
                    word_types=["noun"],
                    grammar_topics=["名词单复数-基础规则"],
                    difficulty="easy",
                    examples=[{"noun_plural": "books", "noun_cn": "书"}],
                    validation_rules=["plural_form", "countable_noun"]
                ),
                SentenceTemplate(
                    pattern="There are many {noun_plural} in the {place}.",
                    chinese_pattern="{place_cn}里有很多{noun_cn}。",
                    word_types=["noun", "noun"],
                    grammar_topics=["名词单复数-基础规则"],
                    difficulty="medium",
                    examples=[{"noun_plural": "students", "noun_cn": "学生", "place": "school", "place_cn": "学校"}],
                    validation_rules=["plural_form", "there_be_structure"]
                )
            ],
            "一般过去时": [
                SentenceTemplate(
                    pattern="I {verb_past} yesterday.",
                    chinese_pattern="我昨天{verb_cn}了。",
                    word_types=["verb"],
                    grammar_topics=["一般过去时-基础用法"],
                    difficulty="easy",
                    examples=[{"verb_past": "worked", "verb_cn": "工作"}],
                    validation_rules=["past_tense", "time_marker"]
                ),
                SentenceTemplate(
                    pattern="We {verb_past} {noun} last week.",
                    chinese_pattern="我们上周{verb_cn}了{noun_cn}。",
                    word_types=["verb", "noun"],
                    grammar_topics=["一般过去时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_past": "saw", "verb_cn": "看见", "noun": "movies", "noun_cn": "电影"}],
                    validation_rules=["past_tense", "time_marker"]
                )
            ],
            "现在进行时": [
                SentenceTemplate(
                    pattern="I am {verb_ing} now.",
                    chinese_pattern="我现在正在{verb_cn}。",
                    word_types=["verb"],
                    grammar_topics=["现在进行时-基础用法"],
                    difficulty="easy",
                    examples=[{"verb_ing": "working", "verb_cn": "工作"}],
                    validation_rules=["present_continuous", "ing_form"]
                ),
                SentenceTemplate(
                    pattern="She is {verb_ing} {noun} in the {place}.",
                    chinese_pattern="她正在{place_cn}里{verb_cn}{noun_cn}。",
                    word_types=["verb", "noun", "noun"],
                    grammar_topics=["现在进行时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_ing": "reading", "verb_cn": "读", "noun": "books", "noun_cn": "书", "place": "library", "place_cn": "图书馆"}],
                    validation_rules=["present_continuous", "ing_form", "preposition_usage"]
                )
            ],
            "现在完成时": [
                SentenceTemplate(
                    pattern="I have {verb_past_participle} {noun}.",
                    chinese_pattern="我已经{verb_cn}了{noun_cn}。",
                    word_types=["verb", "noun"],
                    grammar_topics=["现在完成时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_past_participle": "finished", "verb_cn": "完成", "noun": "homework", "noun_cn": "作业"}],
                    validation_rules=["present_perfect", "past_participle"]
                ),
                SentenceTemplate(
                    pattern="She has {verb_past_participle} to {place}.",
                    chinese_pattern="她已经去过{place_cn}了。",
                    word_types=["verb", "noun"],
                    grammar_topics=["现在完成时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_past_participle": "been", "verb_cn": "去", "place": "London", "place_cn": "伦敦"}],
                    validation_rules=["present_perfect", "past_participle", "preposition_usage"]
                )
            ],
            "被动语态": [
                SentenceTemplate(
                    pattern="The {noun} is {verb_past_participle} by {agent}.",
                    chinese_pattern="{noun_cn}被{agent_cn}{verb_cn}了。",
                    word_types=["noun", "verb", "noun"],
                    grammar_topics=["被动语态-基础用法"],
                    difficulty="advanced",
                    examples=[{"noun": "book", "noun_cn": "书", "verb_past_participle": "written", "verb_cn": "写", "agent": "Shakespeare", "agent_cn": "莎士比亚"}],
                    validation_rules=["passive_voice", "past_participle", "by_phrase"]
                )
            ],
            "情态动词": [
                SentenceTemplate(
                    pattern="I {modal_verb} {verb} {noun}.",
                    chinese_pattern="我{modal_verb_cn}{verb_cn}{noun_cn}。",
                    word_types=["verb", "verb", "noun"],
                    grammar_topics=["情态动词-基础用法"],
                    difficulty="medium",
                    examples=[{"modal_verb": "can", "modal_verb_cn": "能", "verb": "speak", "verb_cn": "说", "noun": "English", "noun_cn": "英语"}],
                    validation_rules=["modal_verb", "base_verb_form"]
                )
            ]
        }
    
    def _init_validation_rules(self):
        """初始化学科特定的验证规则"""
        self.validation_rules = {
            "verb_form": [
                r'\b(He|She|It)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s',
                r'\bI\s+(works|studies|goes|plays|runs|jumps|dances|sings|reads|writes|eats|drinks|sleeps|thinks)\s'
            ],
            "tense_consistency": [
                r'\b(yesterday|last|ago|before|then)\s+\w+\s+(will|can|may|must)\b',
                r'\b(now|at the moment|currently)\s+\w+\s+(went|saw|did|had)\b'
            ],
            "third_person_singular": [
                r'\b(He|She|It)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s'
            ],
            "article_usage": [
                r'\ba\s+[aeiouAEIOU]',
                r'\ban\s+[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]',
                r'\ba\s+(water|milk|air|music|information|news|advice|money|time|weather|homework|work|furniture|equipment)'
            ],
            "adjective_noun_order": [
                r'\b(nice|good|bad|big|small|tall|short)\s+(I|you|he|she|it|we|they)\b'
            ],
            "plural_form": [
                r'\b(cat|dog|book|table|student|teacher|car|house)s\s+is\b',
                r'\b(man|woman|child|person)s\s+is\b'
            ],
            "countable_noun": [
                r'\ba\s+(water|milk|air|music|information|news|advice|money|time|weather|homework|work|furniture|equipment)'
            ],
            "there_be_structure": [
                r'\bThere\s+are\s+many\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s+here\b',
                r'\bThere\s+are\s+many\s+(nice|good|bad|happy|sad|big|small|tall|short)\s+here\b'
            ],
            "past_tense": [
                r'\bI\s+(go|see|do|have|make|take|come|give|write|read|speak|break|choose|drive|eat|fall|feel|find|get|know)\s',
                r'\b(He|She|It)\s+(go|see|do|have|make|take|come|give|write|read|speak|break|choose|drive|eat|fall|feel|find|get|know)\s'
            ],
            "time_marker": [
                r'\b(yesterday|last|ago|before|then)\b'
            ],
            "present_continuous": [
                r'\b(am|is|are)\s+\w+ing\b'
            ],
            "ing_form": [
                r'\b(am|is|are)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s'
            ],
            "preposition_usage": [
                r'\bin\s+the\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\b'
            ],
            "present_perfect": [
                r'\b(have|has)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s'
            ],
            "past_participle": [
                r'\b(have|has)\s+(go|see|do|have|make|take|come|give|write|read|speak|break|choose|drive|eat|fall|feel|find|get|know)\s'
            ],
            "passive_voice": [
                r'\b(am|is|are|was|were)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s'
            ],
            "by_phrase": [
                r'\bby\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\b'
            ],
            "modal_verb": [
                r'\b(can|could|may|might|must|should|would|will)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s'
            ],
            "base_verb_form": [
                r'\b(can|could|may|might|must|should|would|will)\s+(works|studies|goes|plays|runs|jumps|dances|sings|reads|writes|eats|drinks|sleeps|thinks)\s'
            ]
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
            (r'^[A-Z][^.!?]*$', '句子不完整，缺少标点符号', 1.0),
            (r'\ba\s+[aeiouAEIOU]', 'a后跟元音音素开头的词，应使用an', 1.5),
            (r'\ban\s+[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]', 'an后跟辅音音素开头的词，应使用a', 1.5),
            (r'\b(am|is|are)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s', '现在进行时动词应该加-ing', 2.0),
            (r'\b(have|has)\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s', '现在完成时动词应该用过去分词', 2.0),
            (r'\b(can|could|may|might|must|should|would|will)\s+(works|studies|goes|plays|runs|jumps|dances|sings|reads|writes|eats|drinks|sleeps|thinks)\s', '情态动词后应该用动词原形', 2.0)
        ]
    
    def _validate_subject_specific(self, sentence_data, level: ValidationLevel) -> Dict[str, Any]:
        """验证英语学科特定内容"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        sentence = sentence_data.sentence
        grammar_topic = sentence_data.grammar_topic or ""
        
        # 检查英语特定的语法规则
        for rule_name, patterns in self.validation_rules.items():
            for pattern in patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    issues.append(f"语法错误: {self._get_error_message(rule_name)}")
                    suggestions.append(self._get_suggestion(rule_name))
                    penalty += self._get_penalty(rule_name)
        
        # 检查不可数名词使用
        uncountable_issues = self._check_uncountable_nouns(sentence)
        issues.extend(uncountable_issues['issues'])
        suggestions.extend(uncountable_issues['suggestions'])
        penalty += uncountable_issues['penalty']
        
        # 检查动词时态一致性
        tense_issues = self._check_tense_consistency(sentence, grammar_topic)
        issues.extend(tense_issues['issues'])
        suggestions.extend(tense_issues['suggestions'])
        penalty += tense_issues['penalty']
        
        # 检查冠词使用
        article_issues = self._check_article_usage(sentence)
        issues.extend(article_issues['issues'])
        suggestions.extend(article_issues['suggestions'])
        penalty += article_issues['penalty']
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _check_uncountable_nouns(self, sentence: str) -> Dict[str, Any]:
        """检查不可数名词使用"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        for noun in self.uncountable_nouns:
            pattern = rf'\ba\s+{noun}\b'
            if re.search(pattern, sentence, re.IGNORECASE):
                issues.append(f"不可数名词'{noun}'不能使用不定冠词a")
                suggestions.append(f"使用some {noun}或直接使用{noun}")
                penalty += 2.0
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _check_tense_consistency(self, sentence: str, grammar_topic: str) -> Dict[str, Any]:
        """检查时态一致性"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        if "过去时" in grammar_topic:
            past_time_words = ['yesterday', 'last', 'ago', 'before', 'then']
            has_past_time = any(word in sentence.lower() for word in past_time_words)
            
            if not has_past_time:
                issues.append("过去时句子缺少时间标志词")
                suggestions.append("添加yesterday, last week等时间状语")
                penalty += 1.0
        
        elif "进行时" in grammar_topic:
            progressive_time_words = ['now', 'at the moment', 'currently', 'right now']
            has_progressive_time = any(word in sentence.lower() for word in progressive_time_words)
            
            if not has_progressive_time:
                issues.append("进行时句子缺少时间标志词")
                suggestions.append("添加now, at the moment等时间状语")
                penalty += 1.0
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _check_article_usage(self, sentence: str) -> Dict[str, Any]:
        """检查冠词使用"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        a_pattern = r'\ba\s+[aeiouAEIOU]'
        an_pattern = r'\ban\s+[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]'
        
        if re.search(a_pattern, sentence, re.IGNORECASE):
            issues.append("a后跟元音音素开头的词，应使用an")
            suggestions.append("检查冠词a/an的使用规则")
            penalty += 1.5
        
        if re.search(an_pattern, sentence, re.IGNORECASE):
            issues.append("an后跟辅音音素开头的词，应使用a")
            suggestions.append("检查冠词a/an的使用规则")
            penalty += 1.5
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _get_error_message(self, rule_name: str) -> str:
        """获取错误信息"""
        error_messages = {
            "verb_form": "动词形式错误",
            "tense_consistency": "时态不一致",
            "third_person_singular": "第三人称单数形式错误",
            "article_usage": "冠词使用错误",
            "adjective_noun_order": "形容词和名词顺序错误",
            "plural_form": "复数形式错误",
            "countable_noun": "可数名词使用错误",
            "there_be_structure": "There be句型结构错误",
            "past_tense": "过去时形式错误",
            "time_marker": "时间标志词缺失",
            "present_continuous": "现在进行时形式错误",
            "ing_form": "动词-ing形式错误",
            "preposition_usage": "介词使用错误",
            "present_perfect": "现在完成时形式错误",
            "past_participle": "过去分词形式错误",
            "passive_voice": "被动语态形式错误",
            "by_phrase": "by短语使用错误",
            "modal_verb": "情态动词使用错误",
            "base_verb_form": "动词原形使用错误"
        }
        return error_messages.get(rule_name, "语法错误")
    
    def _get_suggestion(self, rule_name: str) -> str:
        """获取建议"""
        suggestions = {
            "verb_form": "检查动词形式是否正确",
            "tense_consistency": "确保时态一致",
            "third_person_singular": "第三人称单数动词要加-s或变形",
            "article_usage": "检查冠词a/an的使用规则",
            "adjective_noun_order": "形容词通常放在名词前面",
            "plural_form": "检查复数形式是否正确",
            "countable_noun": "注意可数名词和不可数名词的区别",
            "there_be_structure": "There be句型中be动词要与后面的名词保持一致",
            "past_tense": "使用正确的过去时形式",
            "time_marker": "添加适当的时间标志词",
            "present_continuous": "现在进行时 = be + 动词-ing",
            "ing_form": "动词-ing形式变化规则",
            "preposition_usage": "检查介词的使用",
            "present_perfect": "现在完成时 = have/has + 过去分词",
            "past_participle": "使用正确的过去分词形式",
            "passive_voice": "被动语态 = be + 过去分词",
            "by_phrase": "被动语态可以用by引出动作执行者",
            "modal_verb": "情态动词 + 动词原形",
            "base_verb_form": "情态动词后使用动词原形"
        }
        return suggestions.get(rule_name, "请检查语法")
    
    def _get_penalty(self, rule_name: str) -> float:
        """获取惩罚分数"""
        penalties = {
            "verb_form": 2.0,
            "tense_consistency": 2.5,
            "third_person_singular": 2.0,
            "article_usage": 1.5,
            "adjective_noun_order": 1.0,
            "plural_form": 2.0,
            "countable_noun": 2.0,
            "there_be_structure": 2.0,
            "past_tense": 2.0,
            "time_marker": 1.0,
            "present_continuous": 2.0,
            "ing_form": 2.0,
            "preposition_usage": 1.5,
            "present_perfect": 2.0,
            "past_participle": 2.0,
            "passive_voice": 2.5,
            "by_phrase": 1.5,
            "modal_verb": 2.0,
            "base_verb_form": 2.0
        }
        return penalties.get(rule_name, 1.0)

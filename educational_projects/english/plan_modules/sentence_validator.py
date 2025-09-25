#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
句子校验和生成模块
确保练习句子的语法正确性、词汇针对性和翻译逻辑性
"""

import random
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class SentenceTemplate:
    """句子模板数据类"""
    pattern: str           # 句子模式，如 "I {verb} {object} {time}."
    chinese_pattern: str   # 中文模式，如 "我{time_cn}{verb_cn}{object_cn}。"
    word_types: List[str]  # 需要的词性，如 ["verb", "noun", "adverb"]
    grammar_topics: List[str]  # 适用的语法主题
    difficulty: str        # 难度级别
    examples: List[Dict[str, str]]  # 示例句子

class SentenceValidator:
    """句子校验和生成器"""
    
    def __init__(self):
        # 定义各种语法主题的句子模板
        self.templates = {
            "一般现在时": [
                SentenceTemplate(
                    pattern="I {verb} every day.",
                    chinese_pattern="我每天{verb_cn}。",
                    word_types=["verb"],
                    grammar_topics=["一般现在时-基础用法"],
                    difficulty="easy",
                    examples=[{"verb": "work", "verb_cn": "工作"}]
                ),
                SentenceTemplate(
                    pattern="He {verb_3rd} {noun} every morning.",
                    chinese_pattern="他每天早上{verb_cn}{noun_cn}。",
                    word_types=["verb", "noun"],
                    grammar_topics=["一般现在时-第三人称单数"],
                    difficulty="easy",
                    examples=[{"verb": "reads", "verb_cn": "读", "noun": "books", "noun_cn": "书"}]
                ),
                SentenceTemplate(
                    pattern="This is a {adjective} {noun}.",
                    chinese_pattern="这是一个{adjective_cn}的{noun_cn}。",
                    word_types=["adjective", "noun"],
                    grammar_topics=["一般现在时-基础用法"],
                    difficulty="easy",
                    examples=[{"adjective": "nice", "adjective_cn": "好", "noun": "book", "noun_cn": "书"}]
                )
            ],
            "名词单复数": [
                SentenceTemplate(
                    pattern="I have two {noun_plural}.",
                    chinese_pattern="我有两个{noun_cn}。",
                    word_types=["noun"],
                    grammar_topics=["名词单复数-基础规则"],
                    difficulty="easy",
                    examples=[{"noun_plural": "books", "noun_cn": "书"}]
                ),
                SentenceTemplate(
                    pattern="There are many {noun_plural} in the {place}.",
                    chinese_pattern="{place_cn}里有很多{noun_cn}。",
                    word_types=["noun", "noun"],
                    grammar_topics=["名词单复数-基础规则"],
                    difficulty="medium",
                    examples=[{"noun_plural": "students", "noun_cn": "学生", "place": "school", "place_cn": "学校"}]
                )
            ],
            "一般过去时": [
                SentenceTemplate(
                    pattern="I {verb_past} yesterday.",
                    chinese_pattern="我昨天{verb_cn}了。",
                    word_types=["verb"],
                    grammar_topics=["一般过去时-基础用法"],
                    difficulty="easy",
                    examples=[{"verb_past": "worked", "verb_cn": "工作"}]
                ),
                SentenceTemplate(
                    pattern="We {verb_past} {noun} last week.",
                    chinese_pattern="我们上周{verb_cn}了{noun_cn}。",
                    word_types=["verb", "noun"],
                    grammar_topics=["一般过去时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_past": "saw", "verb_cn": "看见", "noun": "movies", "noun_cn": "电影"}]
                )
            ],
            "现在进行时": [
                SentenceTemplate(
                    pattern="I am {verb_ing} now.",
                    chinese_pattern="我现在正在{verb_cn}。",
                    word_types=["verb"],
                    grammar_topics=["现在进行时-基础用法"],
                    difficulty="easy",
                    examples=[{"verb_ing": "working", "verb_cn": "工作"}]
                ),
                SentenceTemplate(
                    pattern="She is {verb_ing} {noun} in the {place}.",
                    chinese_pattern="她正在{place_cn}{verb_cn}{noun_cn}。",
                    word_types=["verb", "noun", "noun"],
                    grammar_topics=["现在进行时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_ing": "reading", "verb_cn": "读", "noun": "books", "noun_cn": "书", "place": "library", "place_cn": "图书馆"}]
                )
            ],
            "现在完成时": [
                SentenceTemplate(
                    pattern="I have {verb_pp} {noun} before.",
                    chinese_pattern="我以前{verb_cn}过{noun_cn}。",
                    word_types=["verb", "noun"],
                    grammar_topics=["现在完成时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_pp": "seen", "verb_cn": "看见", "noun": "movies", "noun_cn": "电影"}]
                ),
                SentenceTemplate(
                    pattern="He has {verb_pp} to {place} many times.",
                    chinese_pattern="他已经去过{place_cn}很多次了。",
                    word_types=["verb", "noun"],
                    grammar_topics=["现在完成时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_pp": "been", "verb_cn": "去", "place": "Beijing", "place_cn": "北京"}]
                )
            ],
            "被动语态": [
                SentenceTemplate(
                    pattern="The {noun} is {verb_pp} by {agent}.",
                    chinese_pattern="{noun_cn}被{agent_cn}{verb_cn}。",
                    word_types=["noun", "verb", "noun"],
                    grammar_topics=["被动语态-基础用法"],
                    difficulty="medium",
                    examples=[{"noun": "book", "noun_cn": "书", "verb_pp": "written", "verb_cn": "写", "agent": "students", "agent_cn": "学生"}]
                )
            ],
            "情态动词": [
                SentenceTemplate(
                    pattern="You {modal} {verb} {noun} every day.",
                    chinese_pattern="你{modal_cn}每天{verb_cn}{noun_cn}。",
                    word_types=["verb", "noun"],
                    grammar_topics=["情态动词-基础用法"],
                    difficulty="medium",
                    examples=[{"modal": "should", "modal_cn": "应该", "verb": "read", "verb_cn": "读", "noun": "books", "noun_cn": "书"}]
                )
            ],
            "过去进行时": [
                SentenceTemplate(
                    pattern="I was {verb_ing} at {time} yesterday.",
                    chinese_pattern="我昨天{time_cn}正在{verb_cn}。",
                    word_types=["verb"],
                    grammar_topics=["过去进行时-基础用法"],
                    difficulty="medium",
                    examples=[{"verb_ing": "studying", "verb_cn": "学习", "time": "8 o'clock", "time_cn": "8点"}]
                )
            ]
        }
        
        # 常用的语境词汇
        self.context_words = {
            "time_expressions": {
                "present": ["now", "today", "every day", "usually", "often", "sometimes"],
                "past": ["yesterday", "last week", "last month", "ago", "before"],
                "future": ["tomorrow", "next week", "soon", "later"]
            },
            "places": ["school", "home", "park", "library", "shop", "hospital", "office"],
            "people": ["students", "teachers", "friends", "family", "children", "parents"]
        }
    
    def generate_validated_sentence(self, word_info, grammar_topic: str) -> Dict[str, str]:
        """生成经过校验的练习句子"""
        # 根据语法主题选择合适的模板
        templates = self._get_templates_for_topic(grammar_topic)
        if not templates:
            return self._generate_fallback_sentence(word_info, grammar_topic)
        
        # 根据词性筛选合适的模板
        suitable_templates = self._filter_templates_by_word_type(templates, word_info.part_of_speech)
        if not suitable_templates:
            return self._generate_fallback_sentence(word_info, grammar_topic)
        
        # 随机选择一个模板
        template = random.choice(suitable_templates)
        
        # 生成句子
        return self._generate_sentence_from_template(template, word_info, grammar_topic)
    
    def _get_templates_for_topic(self, grammar_topic: str) -> List[SentenceTemplate]:
        """根据语法主题获取模板"""
        # 提取主要语法类型
        main_topic = self._extract_main_topic(grammar_topic)
        return self.templates.get(main_topic, [])
    
    def _extract_main_topic(self, grammar_topic: str) -> str:
        """提取主要语法主题"""
        if "一般现在时" in grammar_topic:
            return "一般现在时"
        elif "名词单复数" in grammar_topic:
            return "名词单复数"
        elif "一般过去时" in grammar_topic:
            return "一般过去时"
        elif "现在进行时" in grammar_topic:
            return "现在进行时"
        elif "现在完成时" in grammar_topic:
            return "现在完成时"
        elif "被动语态" in grammar_topic:
            return "被动语态"
        elif "情态动词" in grammar_topic:
            return "情态动词"
        elif "过去进行时" in grammar_topic:
            return "过去进行时"
        else:
            return "一般现在时"  # 默认
    
    def _filter_templates_by_word_type(self, templates: List[SentenceTemplate], word_type: str) -> List[SentenceTemplate]:
        """根据词性筛选模板"""
        return [t for t in templates if word_type in t.word_types]
    
    def _generate_sentence_from_template(self, template: SentenceTemplate, word_info, grammar_topic: str) -> Dict[str, str]:
        """根据模板生成句子"""
        # 准备词汇变换
        word_forms = self._get_word_forms(word_info, grammar_topic)
        
        # 填充模板
        try:
            # 构建替换字典
            replacements = self._build_replacements(template, word_info, word_forms, grammar_topic)
            
            # 生成英文句子
            english_sentence = template.pattern.format(**replacements)
            
            # 生成中文翻译
            chinese_sentence = template.chinese_pattern.format(**replacements)
            
            # 校验句子
            if self._validate_sentence(english_sentence, chinese_sentence, word_info):
                return {
                    "sentence": english_sentence,
                    "chinese": chinese_sentence,
                    "template_used": template.pattern,
                    "validation_status": "passed"
                }
            else:
                return self._generate_fallback_sentence(word_info, grammar_topic)
                
        except KeyError as e:
            # 模板填充失败，使用备用方案
            return self._generate_fallback_sentence(word_info, grammar_topic)
    
    def _get_word_forms(self, word_info, grammar_topic: str) -> Dict[str, str]:
        """获取单词的各种形式"""
        # 这里需要导入或复用 exercise_generator 的方法
        # 为了简化，先创建基本的形式
        word = word_info.word
        forms = {
            "base": word,
            "third_person": self._get_simple_third_person(word),
            "past": self._get_simple_past(word),
            "ing": self._get_simple_ing(word),
            "past_participle": self._get_simple_past_participle(word),
            "plural": self._get_simple_plural(word)
        }
        return forms
    
    def _get_simple_third_person(self, word: str) -> str:
        """简单的第三人称单数变化"""
        if word.endswith(('s', 'sh', 'ch', 'x', 'o')):
            return f"{word}es"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"{word[:-1]}ies"
        else:
            return f"{word}s"
    
    def _get_simple_past(self, word: str) -> str:
        """简单的过去式变化"""
        irregular_pasts = {
            'go': 'went', 'have': 'had', 'do': 'did', 'say': 'said',
            'get': 'got', 'make': 'made', 'see': 'saw', 'come': 'came'
        }
        if word in irregular_pasts:
            return irregular_pasts[word]
        elif word.endswith('e'):
            return f"{word}d"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"{word[:-1]}ied"
        else:
            return f"{word}ed"
    
    def _get_simple_ing(self, word: str) -> str:
        """简单的-ing形式变化"""
        if word.endswith('e') and len(word) > 2:
            return f"{word[:-1]}ing"
        else:
            return f"{word}ing"
    
    def _get_simple_past_participle(self, word: str) -> str:
        """简单的过去分词变化"""
        irregular_pps = {
            'go': 'gone', 'have': 'had', 'do': 'done', 'say': 'said',
            'get': 'gotten', 'make': 'made', 'see': 'seen', 'come': 'come'
        }
        if word in irregular_pps:
            return irregular_pps[word]
        else:
            return self._get_simple_past(word)
    
    def _get_simple_plural(self, word: str) -> str:
        """简单的复数形式"""
        if word.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return f"{word}es"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"{word[:-1]}ies"
        else:
            return f"{word}s"
    
    def _build_replacements(self, template: SentenceTemplate, word_info, word_forms: Dict[str, str], grammar_topic: str) -> Dict[str, str]:
        """构建模板替换字典"""
        replacements = {}
        
        # 根据词性填充对应的形式
        if word_info.part_of_speech == "verb":
            replacements.update({
                "verb": word_forms["base"],
                "verb_cn": word_info.chinese_meaning,
                "verb_3rd": word_forms["third_person"],
                "verb_past": word_forms["past"],
                "verb_ing": word_forms["ing"],
                "verb_pp": word_forms["past_participle"]
            })
        elif word_info.part_of_speech == "noun":
            replacements.update({
                "noun": word_forms["base"],
                "noun_cn": word_info.chinese_meaning,
                "noun_plural": word_forms["plural"]
            })
        elif word_info.part_of_speech == "adjective":
            replacements.update({
                "adjective": word_forms["base"],
                "adjective_cn": word_info.chinese_meaning
            })
        
        # 添加常用的语境词汇
        replacements.update({
            "place": "school",
            "place_cn": "学校",
            "time": "8 o'clock",
            "time_cn": "8点",
            "agent": "students",
            "agent_cn": "学生",
            "modal": "can",
            "modal_cn": "能够"
        })
        
        return replacements
    
    def _validate_sentence(self, english: str, chinese: str, word_info) -> bool:
        """校验句子的正确性"""
        # 1. 检查英文句子基本格式
        if not english or len(english.strip()) < 3:
            return False
        
        # 2. 检查句子是否包含目标单词
        if word_info.word.lower() not in english.lower():
            return False
        
        # 3. 检查中文翻译基本格式
        if not chinese or len(chinese.strip()) < 2:
            return False
        
        # 4. 检查中文翻译是否包含单词的中文含义
        if word_info.chinese_meaning not in chinese:
            return False
        
        # 5. 检查句子长度合理性
        if len(english.split()) > 15 or len(chinese) > 30:
            return False
        
        # 6. 检查是否有明显的语法错误模式
        invalid_patterns = [
            "I am nice.",  # 避免 "I am + 形容词" 的不自然表达
            "This is a water.",  # 避免不可数名词使用不定冠词
            "I like nice.",  # 避免动词后直接跟形容词
        ]
        
        if english in invalid_patterns:
            return False
        
        return True
    
    def _generate_fallback_sentence(self, word_info, grammar_topic: str) -> Dict[str, str]:
        """生成备用句子"""
        word = word_info.word
        chinese_meaning = word_info.chinese_meaning
        part_of_speech = word_info.part_of_speech
        
        # 根据词性和语法主题生成合适的备用句子
        if part_of_speech == "noun":
            # 避免不可数名词使用不定冠词的问题
            if word.lower() in ['water', 'milk', 'juice', 'air', 'music']:
                return {
                    "sentence": f"I like {word}.",
                    "chinese": f"我喜欢{chinese_meaning}。",
                    "template_used": "fallback_uncountable_noun",
                    "validation_status": "fallback"
                }
            else:
                return {
                    "sentence": f"I see a {word}.",
                    "chinese": f"我看见一个{chinese_meaning}。",
                    "template_used": "fallback_countable_noun",
                    "validation_status": "fallback"
                }
        elif part_of_speech == "verb":
            return {
                "sentence": f"I {word} every day.",
                "chinese": f"我每天{chinese_meaning}。",
                "template_used": "fallback_verb",
                "validation_status": "fallback"
            }
        elif part_of_speech == "adjective":
            # 避免"好的的"这种重复表达
            if chinese_meaning.endswith('的'):
                chinese_adj = chinese_meaning[:-1]  # 去掉末尾的"的"
            else:
                chinese_adj = chinese_meaning
            return {
                "sentence": f"The book is {word}.",
                "chinese": f"这本书很{chinese_adj}。",
                "template_used": "fallback_adjective",
                "validation_status": "fallback"
            }
        else:
            return {
                "sentence": f"I know about {word}.",
                "chinese": f"我了解{chinese_meaning}。",
                "template_used": "fallback_general",
                "validation_status": "fallback"
            }

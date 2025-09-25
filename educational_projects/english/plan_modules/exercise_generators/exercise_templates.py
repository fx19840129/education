#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
练习题模板模块
提供各种练习题类型的标准化模板
"""

from typing import Dict, List, Tuple
import random


class ExerciseTemplates:
    """练习题模板类"""
    
    def __init__(self):
        # 填空题模板
        self.fill_blank_templates = {
            "basic": [
                ("I _____ {word}.", "我_____。"),
                ("This is a _____.", "这是一个_____。"),
                ("She _____ every day.", "她每天_____。"),
                ("The _____ is nice.", "这个_____很好。"),
            ],
            "present_simple": [
                ("He _____ to school every day.", "他每天_____上学。"),
                ("I usually _____ at 7 AM.", "我通常早上7点_____。"),
                ("They _____ English every week.", "他们每周_____英语。"),
            ],
            "past_simple": [
                ("I _____ yesterday.", "我昨天_____了。"),
                ("She _____ last week.", "她上周_____了。"),
                ("We _____ there last month.", "我们上个月_____那里。"),
            ],
            "present_continuous": [
                ("I am _____ now.", "我现在正在_____。"),
                ("She is _____ at the moment.", "她此刻正在_____。"),
                ("They are _____ today.", "他们今天正在_____。"),
            ],
            "present_perfect": [
                ("I have _____ before.", "我以前_____过。"),
                ("She has already _____.", "她已经_____了。"),
                ("We have never _____.", "我们从未_____过。"),
            ],
            "passive_voice": [
                ("The book is _____ by many people.", "这本书被很多人_____。"),
                ("English is _____ all over the world.", "英语在世界各地被_____。"),
                ("The work was _____ yesterday.", "这项工作昨天被_____了。"),
            ],
            "comparative": [
                ("This book is _____ than that one.", "这本书比那本更_____。"),
                ("She is _____ than her sister.", "她比她姐姐更_____。"),
                ("The weather is getting _____.", "天气变得更_____了。"),
            ],
            "modal_verbs": [
                ("You _____ study hard.", "你_____努力学习。"),
                ("She _____ speak English well.", "她_____说好英语。"),
                ("We _____ go there tomorrow.", "我们明天_____去那里。"),
            ],
        }
        
        # 翻译题模板
        self.translation_templates = {
            "english_to_chinese": [
                "Please translate: '{sentence}'",
                "英译中：{sentence}",
                "将下面的句子翻译成中文：{sentence}",
            ],
            "chinese_to_english": [
                "请翻译：{sentence}",
                "中译英：{sentence}",
                "将下面的句子翻译成英文：{sentence}",
            ]
        }
        
        # 选择题模板
        self.choice_templates = [
            "Choose the correct answer:",
            "选择正确答案：",
            "从下面选项中选择正确答案：",
        ]
        
        # 句子完成题模板
        self.completion_templates = {
            "basic": [
                ("Complete the sentence: {start}", "完成句子：{start}"),
                ("Fill in the rest: {start}", "补充完整：{start}"),
            ],
            "conditional": [
                ("If you _____, you will succeed.", "如果你_____，你就会成功。"),
                ("If I had _____, I would be happy.", "如果我有_____，我会很高兴。"),
            ],
            "relative_clause": [
                ("The _____ that I like is very good.", "我喜欢的_____很好。"),
                ("This is the _____ which we need.", "这就是我们需要的_____。"),
            ]
        }
    
    def get_fill_blank_template(self, grammar_topic: str, word_pos: str) -> Tuple[str, str]:
        """获取填空题模板"""
        if "一般现在时" in grammar_topic:
            if word_pos == "verb":
                return random.choice(self.fill_blank_templates["present_simple"])
            else:
                return random.choice(self.fill_blank_templates["basic"])
        elif "一般过去时" in grammar_topic:
            return random.choice(self.fill_blank_templates["past_simple"])
        elif "现在进行时" in grammar_topic:
            return random.choice(self.fill_blank_templates["present_continuous"])
        elif "现在完成时" in grammar_topic:
            return random.choice(self.fill_blank_templates["present_perfect"])
        elif "被动语态" in grammar_topic:
            return random.choice(self.fill_blank_templates["passive_voice"])
        elif "比较级" in grammar_topic:
            return random.choice(self.fill_blank_templates["comparative"])
        elif "情态动词" in grammar_topic:
            return random.choice(self.fill_blank_templates["modal_verbs"])
        else:
            return random.choice(self.fill_blank_templates["basic"])
    
    def get_translation_template(self, direction: str = "english_to_chinese") -> str:
        """获取翻译题模板"""
        return random.choice(self.translation_templates[direction])
    
    def get_choice_template(self) -> str:
        """获取选择题模板"""
        return random.choice(self.choice_templates)
    
    def get_completion_template(self, grammar_topic: str) -> Tuple[str, str]:
        """获取句子完成题模板"""
        if "条件句" in grammar_topic:
            return random.choice(self.completion_templates["conditional"])
        elif "定语从句" in grammar_topic:
            return random.choice(self.completion_templates["relative_clause"])
        else:
            return random.choice(self.completion_templates["basic"])
    
    def generate_choice_options(self, correct_answer: str, word_pos: str, grammar_topic: str) -> List[str]:
        """生成选择题选项"""
        options = [correct_answer]
        
        # 根据词性和语法主题生成干扰项
        if word_pos == "verb":
            if "一般现在时" in grammar_topic and "第三人称单数" in grammar_topic:
                # 第三人称单数的干扰项
                base_verb = correct_answer.rstrip('s').rstrip('es').rstrip('ies')
                if base_verb.endswith('i'):
                    base_verb = base_verb + 'y'
                options.extend([
                    base_verb,  # 原形
                    f"{base_verb}ed",  # 过去式
                    f"{base_verb}ing"  # 现在分词
                ])
            elif "一般过去时" in grammar_topic:
                # 过去时的干扰项
                base_verb = correct_answer.rstrip('ed').rstrip('d')
                options.extend([
                    base_verb,  # 原形
                    f"{base_verb}s",  # 第三人称单数
                    f"{base_verb}ing"  # 现在分词
                ])
        elif word_pos == "noun":
            if "复数" in grammar_topic:
                # 名词复数的干扰项
                singular = correct_answer.rstrip('s').rstrip('es').rstrip('ies')
                if singular.endswith('i'):
                    singular = singular + 'y'
                options.extend([
                    singular,  # 单数
                    f"a {singular}",  # 带冠词的单数
                    f"the {correct_answer}"  # 带定冠词的复数
                ])
        elif word_pos == "adjective":
            if "比较级" in grammar_topic:
                # 形容词比较级的干扰项
                base_adj = correct_answer.replace('more ', '').rstrip('er').rstrip('r')
                options.extend([
                    base_adj,  # 原级
                    f"most {base_adj}",  # 最高级
                    f"very {base_adj}"  # 程度副词修饰
                ])
        
        # 确保有4个不同的选项
        while len(options) < 4:
            options.append(f"option_{len(options)}")
        
        # 去重并随机排序
        options = list(set(options))[:4]
        random.shuffle(options)
        
        return options
    
    def format_choice_question(self, question: str, options: List[str]) -> str:
        """格式化选择题"""
        formatted_question = f"{question}\n"
        for i, option in enumerate(options, 1):
            formatted_question += f"  {chr(64+i)}. {option}\n"
        return formatted_question.strip()
    
    def get_grammar_hint(self, grammar_topic: str, word_pos: str, word: str) -> str:
        """获取语法提示"""
        hints = {
            "一般现在时-第三人称单数": f"提示：第三人称单数动词需要变形",
            "一般过去时": f"提示：过去时动词需要变为过去式",
            "现在进行时": f"提示：现在进行时用be + 动词-ing形式",
            "现在完成时": f"提示：现在完成时用have/has + 过去分词",
            "被动语态": f"提示：被动语态用be + 过去分词",
            "名词单复数": f"提示：注意名词的单复数变化",
            "形容词比较级": f"提示：比较级表示两者之间的比较",
            "情态动词": f"提示：情态动词后接动词原形",
            "条件句": f"提示：条件句表示假设情况",
            "定语从句": f"提示：定语从句修饰名词",
        }
        
        for key, hint in hints.items():
            if key in grammar_topic:
                return hint
        
        return f"提示：注意{word}的正确用法"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能例句生成器
基于词汇和语法主题，使用GLM-4.5生成多样化、有趣的例句
"""

import json
import os
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from zhipu_ai_client import ai_client
from content_generation_config import config_manager, GenerationMode

@dataclass
class WordInfo:
    """单词信息"""
    word: str
    chinese_meaning: str
    part_of_speech: str
    difficulty: str
    grade_level: str
    category: str

@dataclass
class SentenceResult:
    """例句生成结果"""
    sentence: str
    chinese_translation: str
    grammar_focus: str
    difficulty: str
    is_ai_generated: bool
    template_used: Optional[str] = None
    quality_score: float = 0.0

class SmartSentenceGenerator:
    """智能例句生成器"""
    
    def __init__(self):
        self.ai_client = ai_client
        self.config_manager = config_manager
        
        # 基础模板（保守模式和降级时使用）
        self.basic_templates = {
            "noun": {
                "一般现在时": [
                    ("I have a {word}.", "我有一个{chinese}。"),
                    ("This is a {word}.", "这是一个{chinese}。"),
                    ("The {word} is nice.", "这个{chinese}很好。"),
                    ("I like this {word}.", "我喜欢这个{chinese}。"),
                ],
                "现在进行时": [
                    ("I am using a {word}.", "我正在使用一个{chinese}。"),
                    ("She is buying a {word}.", "她正在买一个{chinese}。"),
                ],
                "过去时": [
                    ("I bought a {word} yesterday.", "我昨天买了一个{chinese}。"),
                    ("We saw a {word} last week.", "我们上周看到了一个{chinese}。"),
                ]
            },
            "verb": {
                "一般现在时": [
                    ("I {word} every day.", "我每天{chinese}。"),
                    ("She {word}s in the morning.", "她在早上{chinese}。"),
                    ("We {word} together.", "我们一起{chinese}。"),
                ],
                "现在进行时": [
                    ("I am {word}ing now.", "我现在正在{chinese}。"),
                    ("They are {word}ing together.", "他们正在一起{chinese}。"),
                ],
                "过去时": [
                    ("I {word}ed yesterday.", "我昨天{chinese}了。"),
                    ("We {word}ed last week.", "我们上周{chinese}了。"),
                ]
            },
            "adjective": {
                "一般现在时": [
                    ("I am {word}.", "我很{chinese}。"),
                    ("This book is {word}.", "这本书很{chinese}。"),
                    ("The weather is {word}.", "天气很{chinese}。"),
                ],
                "比较级": [
                    ("This is {word}er than that.", "这个比那个更{chinese}。"),
                    ("I feel {word}er today.", "我今天感觉更{chinese}。"),
                ]
            }
        }
        
        # 场景化提示模板
        self.scenario_prompts = {
            "daily_life": "日常生活场景",
            "school": "学校学习场景", 
            "family": "家庭活动场景",
            "sports": "体育运动场景",
            "food": "饮食相关场景",
            "travel": "旅行出游场景",
            "technology": "科技生活场景"
        }
    
    def generate_sentence(self, word_info: WordInfo, grammar_topic: str, 
                         mode: str = None, scenario: str = None) -> SentenceResult:
        """
        生成智能例句
        
        Args:
            word_info: 单词信息
            grammar_topic: 语法主题
            mode: 生成模式 (conservative/balanced/innovative)
            scenario: 场景类型
        """
        # 获取配置
        if mode:
            self.config_manager.set_mode(mode)
        
        config = self.config_manager.get_config("sentences")
        
        # 根据模式选择生成策略
        if config.mode == GenerationMode.CONSERVATIVE:
            return self._generate_template_sentence(word_info, grammar_topic)
        elif config.mode == GenerationMode.BALANCED:
            return self._generate_balanced_sentence(word_info, grammar_topic, scenario, config)
        else:  # INNOVATIVE
            return self._generate_ai_sentence(word_info, grammar_topic, scenario, config)
    
    def _generate_template_sentence(self, word_info: WordInfo, 
                                  grammar_topic: str) -> SentenceResult:
        """生成模板例句（保守模式）"""
        pos = word_info.part_of_speech
        templates = self.basic_templates.get(pos, {}).get(grammar_topic, [])
        
        if not templates:
            # 使用通用模板
            if pos == "noun":
                sentence = f"This is a {word_info.word}."
                chinese = f"这是一个{word_info.chinese_meaning}。"
            elif pos == "verb":
                sentence = f"I {word_info.word} every day."
                chinese = f"我每天{word_info.chinese_meaning}。"
            elif pos == "adjective":
                sentence = f"I am {word_info.word}."
                chinese = f"我很{word_info.chinese_meaning}。"
            else:
                sentence = f"The {word_info.word} is important."
                chinese = f"{word_info.chinese_meaning}很重要。"
            
            template = "default"
        else:
            template_pattern, chinese_pattern = random.choice(templates)
            sentence = template_pattern.format(word=word_info.word)
            chinese = chinese_pattern.format(chinese=word_info.chinese_meaning)
            template = template_pattern
        
        return SentenceResult(
            sentence=sentence,
            chinese_translation=chinese,
            grammar_focus=grammar_topic,
            difficulty=word_info.difficulty,
            is_ai_generated=False,
            template_used=template,
            quality_score=0.8  # 模板质量稳定
        )
    
    def _generate_balanced_sentence(self, word_info: WordInfo, grammar_topic: str,
                                  scenario: str, config) -> SentenceResult:
        """生成平衡模式例句（模板+AI优化）"""
        # 先生成模板例句
        template_result = self._generate_template_sentence(word_info, grammar_topic)
        
        # 决定是否进行AI优化
        should_enhance = random.random() < config.ai_enhancement_ratio
        
        if not should_enhance:
            return template_result
        
        # AI优化例句
        try:
            ai_result = self._generate_ai_sentence(word_info, grammar_topic, scenario, config)
            # 如果AI生成质量高，使用AI结果；否则使用模板
            if ai_result.quality_score > 0.7:
                return ai_result
            else:
                return template_result
        except Exception as e:
            print(f"AI优化失败，使用模板: {e}")
            return template_result
    
    def _generate_ai_sentence(self, word_info: WordInfo, grammar_topic: str,
                            scenario: str, config) -> SentenceResult:
        """生成AI例句（创新模式）"""
        # 选择场景
        if not scenario:
            scenario = self._select_appropriate_scenario(word_info)
        
        scenario_desc = self.scenario_prompts.get(scenario, "日常生活场景")
        
        # 构建AI提示
        system_prompt = """你是一个专业的英语教育专家，擅长为中小学生创造生动有趣的英语例句。
你的任务是根据给定的单词、语法主题和场景，生成符合以下要求的例句：
1. 语法正确，完美体现指定的语法主题
2. 包含目标单词并突出其用法
3. 贴近指定场景，富有生活气息
4. 适合中小学生理解，有趣易记
5. 避免使用过于复杂的词汇和句式"""
        
        prompt = f"""请为以下条件生成一个优质的英语例句：

目标单词：{word_info.word} ({word_info.chinese_meaning})
词性：{word_info.part_of_speech}
语法主题：{grammar_topic}
场景设定：{scenario_desc}
难度级别：{word_info.difficulty}
年级水平：{word_info.grade_level}

特殊要求：
1. 例句必须完美体现{grammar_topic}的语法特点
2. 单词{word_info.word}必须在句子中自然出现
3. 场景要贴近{scenario_desc}，生动有趣
4. 适合{word_info.grade_level}学生的理解水平
5. 避免生硬的教科书式表达

请按以下格式返回：
英语例句：[生成的英语句子]
中文翻译：[对应的中文翻译]
语法重点：[简要说明体现的语法点]"""
        
        try:
            response = self.ai_client.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            if response.success:
                # 解析AI响应
                sentence, chinese, grammar_focus = self._parse_ai_response(response.content)
                
                # 评估质量
                quality_score = self._evaluate_sentence_quality(
                    sentence, word_info, grammar_topic
                )
                
                return SentenceResult(
                    sentence=sentence,
                    chinese_translation=chinese,
                    grammar_focus=grammar_focus,
                    difficulty=word_info.difficulty,
                    is_ai_generated=True,
                    quality_score=quality_score
                )
            else:
                raise Exception(f"AI生成失败: {response.error_message}")
                
        except Exception as e:
            print(f"AI生成异常: {e}")
            # 降级到模板
            if config.fallback_to_template:
                return self._generate_template_sentence(word_info, grammar_topic)
            else:
                raise e
    
    def _select_appropriate_scenario(self, word_info: WordInfo) -> str:
        """根据单词特征选择合适的场景"""
        word = word_info.word.lower()
        category = word_info.category.lower()
        
        # 基于单词内容选择场景
        if any(keyword in word for keyword in ['school', 'teacher', 'student', 'book', 'pen']):
            return "school"
        elif any(keyword in word for keyword in ['family', 'mother', 'father', 'sister', 'brother']):
            return "family"
        elif any(keyword in word for keyword in ['apple', 'banana', 'eat', 'drink', 'food']):
            return "food"
        elif any(keyword in word for keyword in ['run', 'play', 'jump', 'sport']):
            return "sports"
        elif any(keyword in word for keyword in ['computer', 'phone', 'internet']):
            return "technology"
        elif 'travel' in category or 'transport' in category:
            return "travel"
        else:
            return "daily_life"
    
    def _parse_ai_response(self, content: str) -> Tuple[str, str, str]:
        """解析AI响应内容"""
        lines = content.strip().split('\n')
        sentence = ""
        chinese = ""
        grammar_focus = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('英语例句：') or line.startswith('英语句子：'):
                sentence = line.split('：', 1)[1].strip()
            elif line.startswith('中文翻译：'):
                chinese = line.split('：', 1)[1].strip()
            elif line.startswith('语法重点：') or line.startswith('语法点：'):
                grammar_focus = line.split('：', 1)[1].strip()
        
        # 如果解析失败，尝试直接提取
        if not sentence:
            # 查找可能的英语句子
            for line in lines:
                if any(char.isalpha() for char in line) and '：' not in line and len(line) > 10:
                    sentence = line.strip()
                    break
        
        if not chinese:
            chinese = "请参考英语句子理解含义。"
        
        if not grammar_focus:
            grammar_focus = "语法应用"
        
        return sentence, chinese, grammar_focus
    
    def _evaluate_sentence_quality(self, sentence: str, word_info: WordInfo, 
                                 grammar_topic: str) -> float:
        """评估例句质量"""
        score = 0.0
        
        # 基础检查
        if not sentence or len(sentence) < 5:
            return 0.0
        
        # 检查是否包含目标单词
        if word_info.word.lower() in sentence.lower():
            score += 0.3
        
        # 检查句子长度合理性
        if 5 <= len(sentence.split()) <= 20:
            score += 0.2
        
        # 检查语法基础结构
        if sentence.endswith('.') or sentence.endswith('!') or sentence.endswith('?'):
            score += 0.1
        
        # 检查首字母大写
        if sentence[0].isupper():
            score += 0.1
        
        # 检查是否避免过于简单的句式
        if not sentence.startswith('This is') and not sentence.startswith('I am'):
            score += 0.2
        
        # 检查单词在句子中的自然性（避免生硬插入）
        if self._check_word_naturalness(sentence, word_info.word):
            score += 0.1
        
        return min(score, 1.0)
    
    def _check_word_naturalness(self, sentence: str, word: str) -> bool:
        """检查单词在句子中的自然性"""
        # 简单检查：单词前后应该有合理的语法结构
        sentence_lower = sentence.lower()
        word_lower = word.lower()
        
        if word_lower not in sentence_lower:
            return False
        
        # 检查单词前后的词汇是否合理（简化版）
        word_pos = sentence_lower.find(word_lower)
        
        # 检查前后是否有合理的空格或标点
        if word_pos > 0:
            prev_char = sentence_lower[word_pos - 1]
            if prev_char not in ' .,!?-(':
                return False
        
        if word_pos + len(word_lower) < len(sentence_lower):
            next_char = sentence_lower[word_pos + len(word_lower)]
            if next_char not in ' .,!?-)s':
                return False
        
        return True
    
    def generate_multiple_sentences(self, word_info: WordInfo, grammar_topic: str,
                                  count: int = 3, diverse_scenarios: bool = True) -> List[SentenceResult]:
        """生成多个例句"""
        sentences = []
        scenarios = list(self.scenario_prompts.keys()) if diverse_scenarios else [None]
        
        for i in range(count):
            scenario = scenarios[i % len(scenarios)] if diverse_scenarios else None
            
            try:
                sentence = self.generate_sentence(word_info, grammar_topic, scenario=scenario)
                sentences.append(sentence)
            except Exception as e:
                print(f"生成第{i+1}个例句失败: {e}")
                # 使用模板作为备选
                template_sentence = self._generate_template_sentence(word_info, grammar_topic)
                sentences.append(template_sentence)
        
        return sentences
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        current_mode = self.config_manager.get_current_mode()
        config = self.config_manager.get_config("sentences")
        
        return {
            "current_mode": current_mode,
            "mode_description": self.config_manager.get_mode_description(current_mode),
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "ai_enhancement_ratio": config.ai_enhancement_ratio,
            "fallback_enabled": config.fallback_to_template,
            "available_scenarios": list(self.scenario_prompts.keys())
        }

# 全局实例
sentence_generator = SmartSentenceGenerator()

if __name__ == "__main__":
    # 测试智能例句生成器
    print("=== 智能例句生成器测试 ===")
    
    # 测试单词
    test_word = WordInfo(
        word="apple",
        chinese_meaning="苹果",
        part_of_speech="noun",
        difficulty="easy",
        grade_level="elementary_1_2",
        category="food"
    )
    
    # 测试不同模式
    modes = ["conservative", "balanced", "innovative"]
    
    for mode in modes:
        print(f"\n--- {mode.upper()} 模式测试 ---")
        
        sentence = sentence_generator.generate_sentence(
            test_word, 
            "一般现在时", 
            mode=mode,
            scenario="daily_life"
        )
        
        print(f"例句: {sentence.sentence}")
        print(f"翻译: {sentence.chinese_translation}")
        print(f"语法重点: {sentence.grammar_focus}")
        print(f"AI生成: {sentence.is_ai_generated}")
        print(f"质量评分: {sentence.quality_score}")
        if sentence.template_used:
            print(f"模板: {sentence.template_used}")
    
    # 生成统计信息
    print(f"\n--- 生成器统计 ---")
    stats = sentence_generator.get_generation_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

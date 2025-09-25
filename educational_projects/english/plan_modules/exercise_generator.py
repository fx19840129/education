#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重构后的练习题生成器主调度器
保持向后兼容的API，但使用模块化的内部实现
"""

import random
import sys
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# 添加当前目录到路径，以便导入模块
sys.path.append(os.path.dirname(__file__))
from sentence_validator import SentenceValidator
from exercise_validator import ExerciseValidator

# 导入新的模块化生成器
from exercise_generators import (
    Exercise, TenseGenerators, NounGenerators, 
    AdjectiveGenerators, AdvancedGenerators
)


@dataclass
class ExerciseQuestion:
    """练习题数据类（保持向后兼容）"""
    question_type: str  # 题型：fill_blank, translation, choice, sentence_completion
    question: str  # 题目
    options: List[str] = None  # 选项（选择题用）
    correct_answer: str = None  # 正确答案
    explanation: str = None  # 解释
    difficulty: str = "easy"  # 难度


class ExerciseGenerator:
    """重构后的练习题生成器主调度器"""
    
    def __init__(self):
        self.part_of_speech_map = {
            "noun": {"chinese": "名词", "abbreviation": "n."},
            "verb": {"chinese": "动词", "abbreviation": "v."},
            "adjective": {"chinese": "形容词", "abbreviation": "adj."},
            "adverb": {"chinese": "副词", "abbreviation": "adv."},
            "pronoun": {"chinese": "代词", "abbreviation": "pron."},
            "preposition": {"chinese": "介词", "abbreviation": "prep."},
            "conjunction": {"chinese": "连词", "abbreviation": "conj."},
            "interjection": {"chinese": "感叹词", "abbreviation": "interj."},
            "article": {"chinese": "冠词", "abbreviation": "art."},
            "numeral": {"chinese": "数词", "abbreviation": "num."},
            "determiner": {"chinese": "限定词", "abbreviation": "det."}
        }
        
        # 初始化句子校验器和练习题校验器（保持兼容性）
        self.sentence_validator = SentenceValidator()
        self.exercise_validator = ExerciseValidator()
        
        # 初始化专门化的语法生成器
        self.tense_generator = TenseGenerators()
        self.noun_generator = NounGenerators()
        self.adjective_generator = AdjectiveGenerators()
        self.advanced_generator = AdvancedGenerators()
        
        # 语法主题到生成器的映射
        self.generator_mapping = self._build_generator_mapping()
    
    def _build_generator_mapping(self) -> Dict[str, Any]:
        """构建语法主题到生成器的映射"""
        mapping = {}
        
        # 时态语法映射
        for topic in self.tense_generator.supported_grammar_topics:
            mapping[topic] = self.tense_generator
        
        # 名词语法映射
        for topic in self.noun_generator.supported_grammar_topics:
            mapping[topic] = self.noun_generator
        
        # 形容词语法映射
        for topic in self.adjective_generator.supported_grammar_topics:
            mapping[topic] = self.adjective_generator
        
        # 高级语法映射
        for topic in self.advanced_generator.supported_grammar_topics:
            mapping[topic] = self.advanced_generator
        
        return mapping
    
    def _get_appropriate_generator(self, grammar_topic: str):
        """根据语法主题获取合适的生成器"""
        # 精确匹配
        if grammar_topic in self.generator_mapping:
            return self.generator_mapping[grammar_topic]
        
        # 模糊匹配
        for topic_key, generator in self.generator_mapping.items():
            if any(keyword in grammar_topic for keyword in topic_key.split('-')):
                return generator
        
        # 按语法类别匹配
        if any(keyword in grammar_topic for keyword in ["现在时", "过去时", "进行时", "完成时"]):
            return self.tense_generator
        elif any(keyword in grammar_topic for keyword in ["名词", "复数", "冠词"]):
            return self.noun_generator
        elif any(keyword in grammar_topic for keyword in ["形容词", "比较级", "最高级", "be动词"]):
            return self.adjective_generator
        elif any(keyword in grammar_topic for keyword in ["被动语态", "情态动词", "条件句", "定语从句", "间接引语", "人称代词"]):
            return self.advanced_generator
        
        # 默认使用时态生成器
        return self.tense_generator
    
    def generate_daily_exercises(self, word_list: List, grammar_topic: str, num_exercises: int = 4) -> List[ExerciseQuestion]:
        """生成每日练习题（保持向后兼容的API）"""
        exercises = []
        
        # 获取合适的生成器
        generator = self._get_appropriate_generator(grammar_topic)
        
        # 为每个单词生成练习题
        for word_info in word_list[:min(len(word_list), max(1, num_exercises // 4))]:
            try:
                # 使用新的模块化生成器生成练习题
                word_exercises = generator.generate_exercises(word_info, grammar_topic, 4)
                
                # 转换为旧格式（保持向后兼容）
                for exercise in word_exercises:
                    old_format_exercise = self._convert_to_old_format(exercise)
                    exercises.append(old_format_exercise)
                
            except Exception as e:
                # 如果新生成器失败，使用基础生成器作为后备
                print(f"警告：语法主题 '{grammar_topic}' 生成失败，使用基础生成器: {e}")
                fallback_exercise = self._generate_fallback_exercise(word_info, grammar_topic)
                exercises.append(fallback_exercise)
        
        # 确保返回指定数量的练习题
        while len(exercises) < num_exercises and word_list:
            word_info = random.choice(word_list)
            try:
                generator = self._get_appropriate_generator(grammar_topic)
                word_exercises = generator.generate_exercises(word_info, grammar_topic, 1)
                if word_exercises:
                    old_format_exercise = self._convert_to_old_format(word_exercises[0])
                    exercises.append(old_format_exercise)
            except:
                fallback_exercise = self._generate_fallback_exercise(word_info, grammar_topic)
                exercises.append(fallback_exercise)
        
        return exercises[:num_exercises]
    
    def _convert_to_old_format(self, exercise: Exercise) -> ExerciseQuestion:
        """将新格式的Exercise转换为旧格式的ExerciseQuestion"""
        # 处理选择题的选项
        options = None
        correct_answer = exercise.answer
        
        if exercise.exercise_type == "choice":
            # 从问题中提取选项
            lines = exercise.question.split('\n')
            question_text = lines[0]
            options = []
            for line in lines[1:]:
                if line.strip().startswith(('A.', 'B.', 'C.', 'D.')):
                    option = line.strip()[3:].strip()  # 去掉 "A. " 等前缀
                    options.append(option)
            
            # 如果没有提取到选项，创建基本选项
            if not options:
                options = [exercise.answer, "option1", "option2", "option3"]
                random.shuffle(options)
            
            # 更新问题文本（去掉选项部分）
            exercise.question = question_text
        
        return ExerciseQuestion(
            question_type=exercise.exercise_type,
            question=exercise.question,
            options=options,
            correct_answer=correct_answer,
            explanation=exercise.explanation,
            difficulty=exercise.difficulty
        )
    
    def _generate_fallback_exercise(self, word_info, grammar_topic: str) -> ExerciseQuestion:
        """生成后备练习题（简单的基础练习）"""
        question = f"I like _____.\n我喜欢{word_info.chinese_meaning}。"
        return ExerciseQuestion(
            question_type="fill_blank",
            question=question,
            correct_answer=word_info.word,
            explanation=f"基础句型：I like + 词语。{word_info.word}（{word_info.chinese_meaning}）。",
            difficulty="easy"
        )
    
    def get_exercise_type_name(self, exercise_type: str) -> str:
        """获取练习题类型的中文名称（保持向后兼容）"""
        type_names = {
            "fill_blank": "填空题",
            "translation": "翻译题", 
            "choice": "选择题",
            "completion": "句子完成题",
            "sentence_completion": "句子完成题"  # 向后兼容
        }
        return type_names.get(exercise_type, "练习题")
    
    def get_supported_grammar_topics(self) -> List[str]:
        """获取所有支持的语法主题"""
        all_topics = []
        all_topics.extend(self.tense_generator.supported_grammar_topics)
        all_topics.extend(self.noun_generator.supported_grammar_topics)
        all_topics.extend(self.adjective_generator.supported_grammar_topics)
        all_topics.extend(self.advanced_generator.supported_grammar_topics)
        return sorted(set(all_topics))
    
    def check_grammar_support(self, grammar_topic: str) -> Dict[str, Any]:
        """检查语法主题的支持情况"""
        generator = self._get_appropriate_generator(grammar_topic)
        return {
            "supported": True,
            "generator_type": generator.__class__.__name__,
            "confidence": "high" if grammar_topic in self.generator_mapping else "medium"
        }


# 保持向后兼容的辅助函数
def generate_exercises_for_topic(word_list: List, grammar_topic: str, num_exercises: int = 4) -> List[ExerciseQuestion]:
    """生成指定语法主题的练习题（向后兼容函数）"""
    generator = ExerciseGenerator()
    return generator.generate_daily_exercises(word_list, grammar_topic, num_exercises)


if __name__ == "__main__":
    # 简单的测试
    print("重构后的练习题生成器已就绪")
    print("支持的语法主题数量:", len(ExerciseGenerator().get_supported_grammar_topics()))

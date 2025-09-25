#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础练习题生成器抽象类
定义所有语法生成器的统一接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
import sys
import os

# 添加路径以便导入校验器
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


@dataclass
class Exercise:
    """练习题数据类"""
    question: str
    answer: str
    explanation: str
    hint: str
    exercise_type: str  # "fill_blank", "translation", "choice", "completion"
    difficulty: str = "medium"
    grammar_topic: str = ""
    word_focus: str = ""


class BaseGrammarGenerator(ABC):
    """基础语法生成器抽象类"""
    
    def __init__(self):
        self.supported_grammar_topics = []
        self.exercise_types = ["fill_blank", "translation", "choice", "completion"]
        
        # 初始化校验器（延迟导入避免循环依赖）
        self.exercise_validator = None
        self._init_validator()
    
    @abstractmethod
    def supports_grammar_topic(self, grammar_topic: str) -> bool:
        """检查是否支持指定的语法主题"""
        pass
    
    @abstractmethod
    def generate_fill_blank_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成填空题"""
        pass
    
    @abstractmethod
    def generate_translation_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成翻译题"""
        pass
    
    @abstractmethod
    def generate_choice_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成选择题"""
        pass
    
    @abstractmethod
    def generate_completion_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成句子完成题"""
        pass
    
    def _init_validator(self):
        """初始化校验器"""
        try:
            from exercise_validator import ExerciseValidator
            self.exercise_validator = ExerciseValidator()
        except ImportError:
            # 如果无法导入校验器，使用基础校验
            self.exercise_validator = None
    
    def _validate_and_improve_exercise(self, exercise: Exercise, word_info, grammar_topic: str) -> Exercise:
        """校验和改进练习题"""
        if self.exercise_validator is None:
            return exercise  # 无校验器时直接返回
        
        try:
            # 使用练习题校验器进行校验
            validation_result = self.exercise_validator.validate_exercise(
                exercise.question, exercise.answer, word_info, grammar_topic, 
                exercise.hint, exercise.explanation
            )
            
            # 如果有问题，使用改进版本
            if not validation_result.is_valid:
                improved_question = validation_result.improved_question or exercise.question
                improved_answer = validation_result.improved_answer or exercise.answer
                improved_hint = validation_result.improved_hint or exercise.hint
                improved_explanation = validation_result.improved_explanation or exercise.explanation
                
                return Exercise(
                    question=improved_question,
                    answer=improved_answer,
                    explanation=improved_explanation,
                    hint=improved_hint,
                    exercise_type=exercise.exercise_type,
                    difficulty=exercise.difficulty,
                    grammar_topic=exercise.grammar_topic,
                    word_focus=exercise.word_focus
                )
        except Exception as e:
            # 校验失败时，记录并返回原练习题
            print(f"警告：练习题校验失败: {e}")
        
        return exercise
    
    def generate_exercises(self, word_info, grammar_topic: str, num_exercises: int = 4) -> List[Exercise]:
        """生成指定数量的练习题"""
        exercises = []
        
        # 确保每种题型至少生成一道
        if num_exercises >= 4:
            ex1 = self.generate_fill_blank_exercise(word_info, grammar_topic)
            ex1 = self._validate_and_improve_exercise(ex1, word_info, grammar_topic)
            exercises.append(ex1)
            
            ex2 = self.generate_translation_exercise(word_info, grammar_topic)
            ex2 = self._validate_and_improve_exercise(ex2, word_info, grammar_topic)
            exercises.append(ex2)
            
            ex3 = self.generate_choice_exercise(word_info, grammar_topic)
            ex3 = self._validate_and_improve_exercise(ex3, word_info, grammar_topic)
            exercises.append(ex3)
            
            ex4 = self.generate_completion_exercise(word_info, grammar_topic)
            ex4 = self._validate_and_improve_exercise(ex4, word_info, grammar_topic)
            exercises.append(ex4)
            
            # 如果需要更多练习题，随机选择题型
            import random
            for _ in range(num_exercises - 4):
                exercise_type = random.choice(self.exercise_types)
                if exercise_type == "fill_blank":
                    ex = self.generate_fill_blank_exercise(word_info, grammar_topic)
                elif exercise_type == "translation":
                    ex = self.generate_translation_exercise(word_info, grammar_topic)
                elif exercise_type == "choice":
                    ex = self.generate_choice_exercise(word_info, grammar_topic)
                elif exercise_type == "completion":
                    ex = self.generate_completion_exercise(word_info, grammar_topic)
                
                ex = self._validate_and_improve_exercise(ex, word_info, grammar_topic)
                exercises.append(ex)
        else:
            # 如果练习题数量少于4，随机选择题型
            import random
            for i in range(num_exercises):
                exercise_type = self.exercise_types[i % len(self.exercise_types)]
                if exercise_type == "fill_blank":
                    ex = self.generate_fill_blank_exercise(word_info, grammar_topic)
                elif exercise_type == "translation":
                    ex = self.generate_translation_exercise(word_info, grammar_topic)
                elif exercise_type == "choice":
                    ex = self.generate_choice_exercise(word_info, grammar_topic)
                elif exercise_type == "completion":
                    ex = self.generate_completion_exercise(word_info, grammar_topic)
                
                ex = self._validate_and_improve_exercise(ex, word_info, grammar_topic)
                exercises.append(ex)
        
        return exercises
    
    def get_exercise_type_name(self, exercise_type: str) -> str:
        """获取练习题类型的中文名称"""
        type_names = {
            "fill_blank": "填空题",
            "translation": "翻译题", 
            "choice": "选择题",
            "completion": "句子完成题"
        }
        return type_names.get(exercise_type, "练习题")
    
    def validate_exercise(self, exercise: Exercise) -> bool:
        """验证练习题的基本格式"""
        if not exercise.question or not exercise.answer:
            return False
        if not exercise.hint or not exercise.explanation:
            return False
        return True
    
    def get_difficulty_level(self, grammar_topic: str) -> str:
        """根据语法主题判断难度等级"""
        basic_topics = [
            "be动词用法", "名词单复数", "人称代词", 
            "一般现在时-基础用法"
        ]
        intermediate_topics = [
            "一般现在时-第三人称单数", "一般过去时", "现在进行时",
            "形容词比较级", "情态动词-基础用法"
        ]
        advanced_topics = [
            "现在完成时", "被动语态", "定语从句", "间接引语",
            "条件句", "过去进行时"
        ]
        
        if any(topic in grammar_topic for topic in basic_topics):
            return "easy"
        elif any(topic in grammar_topic for topic in intermediate_topics):
            return "medium"
        elif any(topic in grammar_topic for topic in advanced_topics):
            return "hard"
        else:
            return "medium"

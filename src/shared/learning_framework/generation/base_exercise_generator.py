#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用练习题生成框架
提供练习题生成的通用接口和基础功能
"""

import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ExerciseType(Enum):
    """练习题类型枚举"""
    MULTIPLE_CHOICE = "multiple_choice"      # 选择题
    FILL_BLANK = "fill_blank"                # 填空题
    TRANSLATION = "translation"              # 翻译题
    SENTENCE_COMPLETION = "sentence_completion"  # 句子完成题
    MATCHING = "matching"                    # 匹配题
    TRUE_FALSE = "true_false"                # 判断题
    ESSAY = "essay"                          # 论述题


class DifficultyLevel(Enum):
    """难度级别枚举"""
    BEGINNER = "beginner"        # 初级
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"        # 高级
    EXPERT = "expert"            # 专家级


@dataclass
class Exercise:
    """练习题数据类"""
    exercise_id: str
    question_type: ExerciseType
    question: str
    correct_answer: str
    options: Optional[List[str]] = None  # 选择题选项
    explanation: Optional[str] = None    # 解释
    hint: Optional[str] = None          # 提示
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    topic: Optional[str] = None         # 主题
    tags: Optional[List[str]] = None    # 标签
    estimated_time: int = 60            # 预计完成时间（秒）
    metadata: Optional[Dict[str, Any]] = None  # 元数据


@dataclass
class GenerationRequest:
    """生成请求"""
    topic: str                          # 主题
    count: int = 5                      # 生成数量
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE  # 难度
    exercise_types: Optional[List[ExerciseType]] = None  # 题型
    content: Optional[Dict[str, Any]] = None  # 内容数据
    constraints: Optional[Dict[str, Any]] = None  # 约束条件


@dataclass
class GenerationResult:
    """生成结果"""
    exercises: List[Exercise]
    success: bool = True
    error_message: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None


class BaseExerciseGenerator(ABC):
    """通用练习题生成器基类"""
    
    def __init__(self, subject: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化生成器
        
        Args:
            subject: 学科名称
            config: 配置参数
        """
        self.subject = subject
        self.config = config or {}
        self.exercise_templates: Dict[str, Dict[str, Any]] = {}
        self.difficulty_settings: Dict[DifficultyLevel, Dict[str, Any]] = {}
        self._init_templates()
        self._init_difficulty_settings()
    
    @abstractmethod
    def _init_templates(self):
        """初始化学科特定的模板（抽象方法）"""
        pass
    
    @abstractmethod
    def _init_difficulty_settings(self):
        """初始化学科特定的难度设置（抽象方法）"""
        pass
    
    def generate_exercises(self, request: GenerationRequest) -> GenerationResult:
        """
        生成练习题
        
        Args:
            request: 生成请求
            
        Returns:
            GenerationResult: 生成结果
        """
        try:
            exercises = []
            
            # 确定题型
            exercise_types = request.exercise_types or self._get_default_exercise_types(request.difficulty)
            
            # 生成指定数量的练习题
            for i in range(request.count):
                exercise_type = random.choice(exercise_types)
                exercise = self._generate_single_exercise(
                    topic=request.topic,
                    exercise_type=exercise_type,
                    difficulty=request.difficulty,
                    content=request.content,
                    constraints=request.constraints
                )
                if exercise:
                    exercises.append(exercise)
            
            # 生成统计信息
            statistics = self._generate_statistics(exercises)
            
            return GenerationResult(
                exercises=exercises,
                success=True,
                statistics=statistics
            )
            
        except Exception as e:
            return GenerationResult(
                exercises=[],
                success=False,
                error_message=str(e)
            )
    
    @abstractmethod
    def _generate_single_exercise(self, topic: str, exercise_type: ExerciseType, 
                                 difficulty: DifficultyLevel, content: Optional[Dict[str, Any]] = None,
                                 constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成单个练习题（抽象方法）"""
        pass
    
    def _get_default_exercise_types(self, difficulty: DifficultyLevel) -> List[ExerciseType]:
        """获取默认题型"""
        if difficulty == DifficultyLevel.BEGINNER:
            return [ExerciseType.MULTIPLE_CHOICE, ExerciseType.TRUE_FALSE]
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            return [ExerciseType.MULTIPLE_CHOICE, ExerciseType.FILL_BLANK, ExerciseType.TRANSLATION]
        elif difficulty == DifficultyLevel.ADVANCED:
            return [ExerciseType.FILL_BLANK, ExerciseType.SENTENCE_COMPLETION, ExerciseType.MATCHING]
        else:  # EXPERT
            return [ExerciseType.ESSAY, ExerciseType.SENTENCE_COMPLETION, ExerciseType.MATCHING]
    
    def _generate_exercise_id(self, topic: str, exercise_type: ExerciseType) -> str:
        """生成练习题ID"""
        import time
        timestamp = int(time.time() * 1000)
        return f"{self.subject}_{topic}_{exercise_type.value}_{timestamp}"
    
    def _get_difficulty_settings(self, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """获取难度设置"""
        return self.difficulty_settings.get(difficulty, {})
    
    def _generate_multiple_choice(self, topic: str, difficulty: DifficultyLevel, 
                                 content: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成选择题"""
        # 基础实现，子类可以重写
        question = f"关于{topic}的问题"
        correct_answer = "正确答案"
        options = [correct_answer, "错误选项1", "错误选项2", "错误选项3"]
        random.shuffle(options)
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.MULTIPLE_CHOICE),
            question_type=ExerciseType.MULTIPLE_CHOICE,
            question=question,
            correct_answer=correct_answer,
            options=options,
            difficulty=difficulty,
            topic=topic
        )
    
    def _generate_fill_blank(self, topic: str, difficulty: DifficultyLevel,
                            content: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成填空题"""
        # 基础实现，子类可以重写
        question = f"请完成关于{topic}的句子：_____"
        correct_answer = "正确答案"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.FILL_BLANK),
            question_type=ExerciseType.FILL_BLANK,
            question=question,
            correct_answer=correct_answer,
            difficulty=difficulty,
            topic=topic
        )
    
    def _generate_translation(self, topic: str, difficulty: DifficultyLevel,
                             content: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成翻译题"""
        # 基础实现，子类可以重写
        question = f"请翻译以下关于{topic}的内容"
        correct_answer = "翻译答案"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.TRANSLATION),
            question_type=ExerciseType.TRANSLATION,
            question=question,
            correct_answer=correct_answer,
            difficulty=difficulty,
            topic=topic
        )
    
    def _generate_sentence_completion(self, topic: str, difficulty: DifficultyLevel,
                                     content: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成句子完成题"""
        # 基础实现，子类可以重写
        question = f"请完成关于{topic}的句子"
        correct_answer = "完成答案"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.SENTENCE_COMPLETION),
            question_type=ExerciseType.SENTENCE_COMPLETION,
            question=question,
            correct_answer=correct_answer,
            difficulty=difficulty,
            topic=topic
        )
    
    def _generate_matching(self, topic: str, difficulty: DifficultyLevel,
                          content: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成匹配题"""
        # 基础实现，子类可以重写
        question = f"请匹配以下关于{topic}的内容"
        correct_answer = "匹配答案"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.MATCHING),
            question_type=ExerciseType.MATCHING,
            question=question,
            correct_answer=correct_answer,
            difficulty=difficulty,
            topic=topic
        )
    
    def _generate_true_false(self, topic: str, difficulty: DifficultyLevel,
                            content: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成判断题"""
        # 基础实现，子类可以重写
        question = f"关于{topic}的陈述是否正确？"
        correct_answer = "True"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.TRUE_FALSE),
            question_type=ExerciseType.TRUE_FALSE,
            question=question,
            correct_answer=correct_answer,
            options=["True", "False"],
            difficulty=difficulty,
            topic=topic
        )
    
    def _generate_essay(self, topic: str, difficulty: DifficultyLevel,
                       content: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成论述题"""
        # 基础实现，子类可以重写
        question = f"请论述{topic}的相关内容"
        correct_answer = "论述要点"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.ESSAY),
            question_type=ExerciseType.ESSAY,
            question=question,
            correct_answer=correct_answer,
            difficulty=difficulty,
            topic=topic
        )
    
    def _generate_statistics(self, exercises: List[Exercise]) -> Dict[str, Any]:
        """生成统计信息"""
        if not exercises:
            return {}
        
        # 统计题型分布
        type_distribution = {}
        for exercise in exercises:
            exercise_type = exercise.question_type.value
            type_distribution[exercise_type] = type_distribution.get(exercise_type, 0) + 1
        
        # 统计难度分布
        difficulty_distribution = {}
        for exercise in exercises:
            difficulty = exercise.difficulty.value
            difficulty_distribution[difficulty] = difficulty_distribution.get(difficulty, 0) + 1
        
        # 计算平均时间
        total_time = sum(exercise.estimated_time for exercise in exercises)
        avg_time = total_time / len(exercises) if exercises else 0
        
        return {
            'total_exercises': len(exercises),
            'type_distribution': type_distribution,
            'difficulty_distribution': difficulty_distribution,
            'average_time': round(avg_time, 1),
            'total_time': total_time
        }
    
    def add_template(self, template_name: str, template: Dict[str, Any]):
        """添加模板"""
        self.exercise_templates[template_name] = template
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取模板"""
        return self.exercise_templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.exercise_templates.keys())
    
    def validate_exercise(self, exercise: Exercise) -> bool:
        """验证练习题"""
        # 基础验证
        if not exercise.question or not exercise.correct_answer:
            return False
        
        if exercise.question_type == ExerciseType.MULTIPLE_CHOICE:
            if not exercise.options or len(exercise.options) < 2:
                return False
            if exercise.correct_answer not in exercise.options:
                return False
        
        return True
    
    def export_exercises(self, exercises: List[Exercise], format: str = "json") -> str:
        """导出练习题"""
        if format == "json":
            import json
            return json.dumps([exercise.__dict__ for exercise in exercises], 
                            ensure_ascii=False, indent=2, default=str)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入标题行
            writer.writerow(['ID', 'Type', 'Question', 'Answer', 'Options', 'Difficulty', 'Topic'])
            
            # 写入数据行
            for exercise in exercises:
                options_str = '|'.join(exercise.options) if exercise.options else ''
                writer.writerow([
                    exercise.exercise_id,
                    exercise.question_type.value,
                    exercise.question,
                    exercise.correct_answer,
                    options_str,
                    exercise.difficulty.value,
                    exercise.topic or ''
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def get_supported_exercise_types(self) -> List[ExerciseType]:
        """获取支持的题型"""
        return list(ExerciseType)
    
    def get_supported_difficulty_levels(self) -> List[DifficultyLevel]:
        """获取支持的难度级别"""
        return list(DifficultyLevel)

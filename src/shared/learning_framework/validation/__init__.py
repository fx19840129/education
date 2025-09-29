#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证模块
提供内容验证的通用框架
"""

from .base_exercise_validator import (
    BaseExerciseValidator, ExerciseValidationResult, ValidationRule
)
from .base_sentence_validator import (
    BaseSentenceValidator, ValidationResult, SentenceTemplate, SentenceData, ValidationLevel
)

__all__ = [
    "BaseExerciseValidator", "ExerciseValidationResult", "ValidationRule",
    "BaseSentenceValidator", "ValidationResult", "SentenceTemplate", "SentenceData", "ValidationLevel"
]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成模块
提供内容生成的通用框架
"""

from .base_exercise_generator import (
    BaseExerciseGenerator, Exercise, GenerationRequest, GenerationResult, 
    ExerciseType, DifficultyLevel
)
from .base_document_generator import (
    BaseDocumentGenerator, DocumentConfig, DocumentSection, DocumentTable,
    DocumentFormat, DocumentStyle
)

__all__ = [
    "BaseExerciseGenerator", "Exercise", "GenerationRequest", "GenerationResult",
    "ExerciseType", "DifficultyLevel",
    "BaseDocumentGenerator", "DocumentConfig", "DocumentSection", "DocumentTable",
    "DocumentFormat", "DocumentStyle"
]

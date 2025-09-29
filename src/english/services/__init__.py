"""
英语服务层
提供英语学习相关的服务接口和实现
"""

from .morphology_service import (
    MorphologyService, MorphologyPoint
)
from .syntax_service import (
    SyntaxService, SyntaxPoint
)
from .simple_word_service import (
    SimpleWordService
)

__all__ = [
    # 词法服务
    'MorphologyService',
    'MorphologyPoint',
    # 句法服务
    'SyntaxService',
    'SyntaxPoint',
    # 简化单词服务
    'SimpleWordService',
]
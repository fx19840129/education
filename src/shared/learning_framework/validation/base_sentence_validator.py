#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用句子验证框架
提供句子验证的通用接口和基础功能
"""

import re
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """验证级别枚举"""
    BASIC = "basic"          # 基础验证
    INTERMEDIATE = "intermediate"  # 中级验证
    ADVANCED = "advanced"    # 高级验证
    EXPERT = "expert"        # 专家级验证


@dataclass
class SentenceTemplate:
    """句子模板数据类"""
    pattern: str                    # 句子模式
    chinese_pattern: str            # 中文模式
    word_types: List[str]          # 需要的词性
    grammar_topics: List[str]       # 适用的语法主题
    difficulty: str                 # 难度级别
    examples: List[Dict[str, str]]  # 示例句子
    validation_rules: List[str] = None  # 验证规则


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    score: float  # 验证分数 (0-100)
    issues: List[str]
    suggestions: List[str]
    corrected_sentence: Optional[str] = None
    confidence: float = 0.0  # 置信度 (0-1)


@dataclass
class SentenceData:
    """句子数据"""
    sentence: str
    chinese_translation: Optional[str] = None
    grammar_topic: Optional[str] = None
    difficulty: str = "medium"
    word_types: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseSentenceValidator(ABC):
    """通用句子验证器基类"""
    
    def __init__(self, subject: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化验证器
        
        Args:
            subject: 学科名称
            config: 配置参数
        """
        self.subject = subject
        self.config = config or {}
        self.templates: Dict[str, List[SentenceTemplate]] = {}
        self.validation_rules: Dict[str, List[str]] = {}
        self.error_patterns: List[Tuple[str, str, float]] = []  # (pattern, error_msg, weight)
        self._init_templates()
        self._init_validation_rules()
        self._init_error_patterns()
    
    @abstractmethod
    def _init_templates(self):
        """初始化学科特定的模板（抽象方法）"""
        pass
    
    @abstractmethod
    def _init_validation_rules(self):
        """初始化学科特定的验证规则（抽象方法）"""
        pass
    
    @abstractmethod
    def _init_error_patterns(self):
        """初始化学科特定的错误模式（抽象方法）"""
        pass
    
    def validate_sentence(self, sentence_data: SentenceData, 
                         level: ValidationLevel = ValidationLevel.INTERMEDIATE) -> ValidationResult:
        """
        验证句子
        
        Args:
            sentence_data: 句子数据
            level: 验证级别
            
        Returns:
            ValidationResult: 验证结果
        """
        issues = []
        suggestions = []
        score = 100.0
        
        # 基础验证
        basic_result = self._validate_basic_structure(sentence_data)
        issues.extend(basic_result['issues'])
        suggestions.extend(basic_result['suggestions'])
        score -= basic_result['penalty']
        
        # 语法验证
        grammar_result = self._validate_grammar(sentence_data, level)
        issues.extend(grammar_result['issues'])
        suggestions.extend(grammar_result['suggestions'])
        score -= grammar_result['penalty']
        
        # 内容验证
        content_result = self._validate_content(sentence_data, level)
        issues.extend(content_result['issues'])
        suggestions.extend(content_result['suggestions'])
        score -= content_result['penalty']
        
        # 学科特定验证
        subject_result = self._validate_subject_specific(sentence_data, level)
        issues.extend(subject_result['issues'])
        suggestions.extend(subject_result['suggestions'])
        score -= subject_result['penalty']
        
        # 计算置信度
        confidence = self._calculate_confidence(issues, level)
        
        # 生成修正建议
        corrected_sentence = None
        if issues:
            corrected_sentence = self._generate_correction(sentence_data, issues)
        
        is_valid = len(issues) == 0 and score >= 70.0
        
        return ValidationResult(
            is_valid=is_valid,
            score=max(0.0, score),
            issues=issues,
            suggestions=suggestions,
            corrected_sentence=corrected_sentence,
            confidence=confidence
        )
    
    def _validate_basic_structure(self, sentence_data: SentenceData) -> Dict[str, Any]:
        """验证基本结构"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        sentence = sentence_data.sentence.strip()
        
        # 检查句子长度
        if len(sentence) < 3:
            issues.append("句子过短")
            suggestions.append("句子应该包含至少3个字符")
            penalty += 20.0
        elif len(sentence) > 200:
            issues.append("句子过长")
            suggestions.append("句子应该控制在200个字符以内")
            penalty += 10.0
        
        # 检查标点符号
        if not sentence.endswith(('.', '!', '?', '。', '！', '？')):
            issues.append("句子缺少标点符号")
            suggestions.append("句子应该以适当的标点符号结尾")
            penalty += 5.0
        
        # 检查首字母大写
        if sentence and not sentence[0].isupper():
            issues.append("句子首字母未大写")
            suggestions.append("句子首字母应该大写")
            penalty += 5.0
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _validate_grammar(self, sentence_data: SentenceData, level: ValidationLevel) -> Dict[str, Any]:
        """验证语法"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        sentence = sentence_data.sentence
        
        # 使用错误模式检查
        for pattern, error_msg, weight in self.error_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                issues.append(f"语法错误: {error_msg}")
                suggestions.append("请检查语法结构")
                penalty += weight
        
        # 根据验证级别进行更深入的检查
        if level in [ValidationLevel.ADVANCED, ValidationLevel.EXPERT]:
            advanced_result = self._validate_advanced_grammar(sentence_data)
            issues.extend(advanced_result['issues'])
            suggestions.extend(advanced_result['suggestions'])
            penalty += advanced_result['penalty']
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _validate_content(self, sentence_data: SentenceData, level: ValidationLevel) -> Dict[str, Any]:
        """验证内容质量"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        sentence = sentence_data.sentence
        
        # 检查内容重复
        words = sentence.split()
        if len(set(words)) < len(words) * 0.7:  # 重复词过多
            issues.append("句子中重复词过多")
            suggestions.append("建议使用更多样化的词汇")
            penalty += 10.0
        
        # 检查词汇丰富度
        if len(set(words)) < 3:
            issues.append("词汇过于简单")
            suggestions.append("建议使用更丰富的词汇")
            penalty += 15.0
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    @abstractmethod
    def _validate_subject_specific(self, sentence_data: SentenceData, level: ValidationLevel) -> Dict[str, Any]:
        """验证学科特定内容（抽象方法）"""
        pass
    
    def _validate_advanced_grammar(self, sentence_data: SentenceData) -> Dict[str, Any]:
        """高级语法验证"""
        issues = []
        suggestions = []
        penalty = 0.0
        
        sentence = sentence_data.sentence
        
        # 检查句子结构复杂度
        if len(sentence.split()) < 5:
            issues.append("句子结构过于简单")
            suggestions.append("建议使用更复杂的句子结构")
            penalty += 5.0
        
        # 检查从句使用
        if not any(keyword in sentence.lower() for keyword in ['that', 'which', 'who', 'when', 'where', 'why']):
            if sentence_data.difficulty in ['advanced', 'expert']:
                issues.append("高级句子建议使用从句")
                suggestions.append("可以尝试使用定语从句或状语从句")
                penalty += 3.0
        
        return {'issues': issues, 'suggestions': suggestions, 'penalty': penalty}
    
    def _calculate_confidence(self, issues: List[str], level: ValidationLevel) -> float:
        """计算验证置信度"""
        if not issues:
            return 1.0
        
        # 基础置信度
        base_confidence = 0.8
        
        # 根据问题数量调整
        issue_penalty = min(len(issues) * 0.1, 0.5)
        
        # 根据验证级别调整
        level_multiplier = {
            ValidationLevel.BASIC: 1.0,
            ValidationLevel.INTERMEDIATE: 0.9,
            ValidationLevel.ADVANCED: 0.8,
            ValidationLevel.EXPERT: 0.7
        }.get(level, 0.9)
        
        final_confidence = max(0.0, (base_confidence - issue_penalty) * level_multiplier)
        return round(final_confidence, 2)
    
    def _generate_correction(self, sentence_data: SentenceData, issues: List[str]) -> str:
        """生成修正建议"""
        sentence = sentence_data.sentence
        
        # 基础修正
        corrected = sentence.strip()
        
        # 首字母大写
        if corrected and not corrected[0].isupper():
            corrected = corrected[0].upper() + corrected[1:]
        
        # 添加标点符号
        if not corrected.endswith(('.', '!', '?', '。', '！', '？')):
            corrected += '.'
        
        return corrected
    
    def generate_sentence_from_template(self, template_name: str, 
                                      word_data: Dict[str, str]) -> Optional[str]:
        """根据模板生成句子"""
        if template_name not in self.templates:
            return None
        
        templates = self.templates[template_name]
        if not templates:
            return None
        
        # 选择适合的模板
        template = random.choice(templates)
        
        # 生成句子
        sentence = template.pattern
        for key, value in word_data.items():
            sentence = sentence.replace(f"{{{key}}}", value)
        
        return sentence
    
    def get_matching_templates(self, grammar_topic: str, 
                             difficulty: str = "medium") -> List[SentenceTemplate]:
        """获取匹配的模板"""
        matching_templates = []
        
        for topic, templates in self.templates.items():
            if grammar_topic in topic or any(gt in topic for gt in grammar_topic.split('-')):
                for template in templates:
                    if template.difficulty == difficulty or difficulty == "any":
                        matching_templates.append(template)
        
        return matching_templates
    
    def add_template(self, topic: str, template: SentenceTemplate):
        """添加模板"""
        if topic not in self.templates:
            self.templates[topic] = []
        self.templates[topic].append(template)
    
    def add_validation_rule(self, rule_name: str, patterns: List[str]):
        """添加验证规则"""
        self.validation_rules[rule_name] = patterns
    
    def validate_batch(self, sentences: List[SentenceData], 
                      level: ValidationLevel = ValidationLevel.INTERMEDIATE) -> List[ValidationResult]:
        """批量验证句子"""
        return [self.validate_sentence(sentence, level) for sentence in sentences]
    
    def get_validation_statistics(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """获取验证统计信息"""
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid
        
        avg_score = sum(r.score for r in results) / total if total > 0 else 0
        avg_confidence = sum(r.confidence for r in results) / total if total > 0 else 0
        
        # 统计问题类型
        issue_types = {}
        for result in results:
            for issue in result.issues:
                issue_type = issue.split(':')[0] if ':' in issue else '其他'
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            'total_sentences': total,
            'valid_sentences': valid,
            'invalid_sentences': invalid,
            'validation_rate': valid / total if total > 0 else 0,
            'average_score': round(avg_score, 2),
            'average_confidence': round(avg_confidence, 2),
            'issue_types': issue_types
        }
    
    def export_templates(self, format: str = "json") -> str:
        """导出模板"""
        if format == "json":
            import json
            # 转换为可序列化的格式
            serializable_templates = {}
            for topic, templates in self.templates.items():
                serializable_templates[topic] = [
                    {
                        'pattern': t.pattern,
                        'chinese_pattern': t.chinese_pattern,
                        'word_types': t.word_types,
                        'grammar_topics': t.grammar_topics,
                        'difficulty': t.difficulty,
                        'examples': t.examples,
                        'validation_rules': t.validation_rules or []
                    }
                    for t in templates
                ]
            return json.dumps(serializable_templates, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的导出格式: {format}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用练习题验证框架
提供练习题验证的通用接口和基础功能
"""

import re
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass
class ExerciseValidationResult:
    """练习题验证结果"""
    is_valid: bool
    issues: List[str]
    suggestions: List[str]
    improved_question: Optional[str] = None
    improved_answer: Optional[str] = None
    improved_hint: Optional[str] = None
    improved_explanation: Optional[str] = None
    confidence_score: float = 0.0  # 验证置信度 (0-1)


@dataclass
class ValidationRule:
    """验证规则"""
    name: str
    pattern: str
    error_message: str
    suggestion: str
    weight: float = 1.0  # 规则权重


class BaseExerciseValidator(ABC):
    """通用练习题验证器基类"""
    
    def __init__(self, subject: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化验证器
        
        Args:
            subject: 学科名称
            config: 配置参数
        """
        self.subject = subject
        self.config = config or {}
        self.validation_rules: List[ValidationRule] = []
        self.hint_templates: Dict[str, Dict[str, str]] = {}
        self.error_patterns: List[Tuple[str, str]] = []
        self._init_validation_rules()
        self._init_hint_templates()
        self._init_error_patterns()
    
    @abstractmethod
    def _init_validation_rules(self):
        """初始化学科特定的验证规则（抽象方法）"""
        pass
    
    @abstractmethod
    def _init_hint_templates(self):
        """初始化学科特定的提示模板（抽象方法）"""
        pass
    
    @abstractmethod
    def _init_error_patterns(self):
        """初始化学科特定的错误模式（抽象方法）"""
        pass
    
    def validate_exercise(self, exercise: Dict[str, Any]) -> ExerciseValidationResult:
        """
        验证练习题
        
        Args:
            exercise: 练习题数据
            
        Returns:
            ExerciseValidationResult: 验证结果
        """
        issues = []
        suggestions = []
        improved_question = exercise.get('question', '')
        improved_answer = exercise.get('correct_answer', '')
        improved_hint = exercise.get('hint', '')
        improved_explanation = exercise.get('explanation', '')
        
        # 基础验证
        basic_validation = self._validate_basic_structure(exercise)
        issues.extend(basic_validation['issues'])
        suggestions.extend(basic_validation['suggestions'])
        
        # 内容验证
        content_validation = self._validate_content(exercise)
        issues.extend(content_validation['issues'])
        suggestions.extend(content_validation['suggestions'])
        
        # 语法验证
        grammar_validation = self._validate_grammar(exercise)
        issues.extend(grammar_validation['issues'])
        suggestions.extend(grammar_validation['suggestions'])
        
        # 难度验证
        difficulty_validation = self._validate_difficulty(exercise)
        issues.extend(difficulty_validation['issues'])
        suggestions.extend(difficulty_validation['suggestions'])
        
        # 学科特定验证
        subject_validation = self._validate_subject_specific(exercise)
        issues.extend(subject_validation['issues'])
        suggestions.extend(subject_validation['suggestions'])
        
        # 计算置信度
        confidence_score = self._calculate_confidence_score(exercise, issues)
        
        # 生成改进建议
        if issues:
            improvements = self._generate_improvements(exercise, issues)
            improved_question = improvements.get('question', improved_question)
            improved_answer = improvements.get('answer', improved_answer)
            improved_hint = improvements.get('hint', improved_hint)
            improved_explanation = improvements.get('explanation', improved_explanation)
        
        is_valid = len(issues) == 0
        
        return ExerciseValidationResult(
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions,
            improved_question=improved_question,
            improved_answer=improved_answer,
            improved_hint=improved_hint,
            improved_explanation=improved_explanation,
            confidence_score=confidence_score
        )
    
    def _validate_basic_structure(self, exercise: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证基本结构"""
        issues = []
        suggestions = []
        
        # 检查必需字段
        required_fields = ['question', 'correct_answer']
        for field in required_fields:
            if field not in exercise or not exercise[field]:
                issues.append(f"缺少必需字段: {field}")
                suggestions.append(f"请添加{field}字段")
        
        # 检查题目长度
        question = exercise.get('question', '')
        if len(question) < 10:
            issues.append("题目过短，可能不够清晰")
            suggestions.append("建议增加题目描述，使其更加清晰")
        elif len(question) > 200:
            issues.append("题目过长，可能影响理解")
            suggestions.append("建议简化题目描述")
        
        # 检查答案长度
        answer = exercise.get('correct_answer', '')
        if len(answer) < 1:
            issues.append("答案不能为空")
            suggestions.append("请提供正确答案")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _validate_content(self, exercise: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证内容质量"""
        issues = []
        suggestions = []
        
        question = exercise.get('question', '')
        answer = exercise.get('correct_answer', '')
        
        # 检查内容重复
        if question and answer and question.lower() == answer.lower():
            issues.append("题目和答案相同")
            suggestions.append("题目和答案应该有所区别")
        
        # 检查选项质量（如果是选择题）
        if exercise.get('type') == 'multiple_choice':
            options = exercise.get('options', [])
            if len(options) < 2:
                issues.append("选择题选项数量不足")
                suggestions.append("选择题至少需要2个选项")
            elif len(options) > 6:
                issues.append("选择题选项过多")
                suggestions.append("选择题建议不超过6个选项")
            
            # 检查选项重复
            if len(set(options)) != len(options):
                issues.append("选择题选项有重复")
                suggestions.append("请确保所有选项都是唯一的")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _validate_grammar(self, exercise: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证语法正确性"""
        issues = []
        suggestions = []
        
        question = exercise.get('question', '')
        answer = exercise.get('correct_answer', '')
        
        # 使用错误模式检查
        for pattern, error_msg in self.error_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                issues.append(f"题目语法错误: {error_msg}")
                suggestions.append("请检查题目语法")
            
            if re.search(pattern, answer, re.IGNORECASE):
                issues.append(f"答案语法错误: {error_msg}")
                suggestions.append("请检查答案语法")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _validate_difficulty(self, exercise: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证难度设置"""
        issues = []
        suggestions = []
        
        difficulty = exercise.get('difficulty', 'medium')
        question = exercise.get('question', '')
        
        # 根据题目长度判断难度
        if len(question) < 20 and difficulty in ['hard', 'advanced']:
            issues.append("题目长度与难度不匹配")
            suggestions.append("高难度题目应该有更详细的描述")
        elif len(question) > 100 and difficulty in ['easy', 'beginner']:
            issues.append("题目长度与难度不匹配")
            suggestions.append("简单题目应该更加简洁")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    @abstractmethod
    def _validate_subject_specific(self, exercise: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证学科特定内容（抽象方法）"""
        pass
    
    def _calculate_confidence_score(self, exercise: Dict[str, Any], issues: List[str]) -> float:
        """计算验证置信度"""
        if not issues:
            return 1.0
        
        # 基础分数
        base_score = 1.0
        
        # 根据问题数量扣分
        issue_penalty = min(len(issues) * 0.1, 0.8)
        
        # 根据问题严重程度扣分
        severity_penalty = 0.0
        for issue in issues:
            if any(keyword in issue.lower() for keyword in ['错误', '错误', 'invalid', 'missing']):
                severity_penalty += 0.2
            elif any(keyword in issue.lower() for keyword in ['建议', '建议', 'suggestion', 'improve']):
                severity_penalty += 0.1
        
        final_score = max(0.0, base_score - issue_penalty - severity_penalty)
        return round(final_score, 2)
    
    def _generate_improvements(self, exercise: Dict[str, Any], issues: List[str]) -> Dict[str, str]:
        """生成改进建议"""
        improvements = {}
        
        question = exercise.get('question', '')
        answer = exercise.get('correct_answer', '')
        hint = exercise.get('hint', '')
        explanation = exercise.get('explanation', '')
        
        # 改进题目
        if any('题目' in issue for issue in issues):
            improvements['question'] = self._improve_question(question, issues)
        
        # 改进答案
        if any('答案' in issue for issue in issues):
            improvements['answer'] = self._improve_answer(answer, issues)
        
        # 改进提示
        if not hint or any('提示' in issue for issue in issues):
            improvements['hint'] = self._generate_hint(exercise)
        
        # 改进解释
        if not explanation or any('解释' in issue for issue in issues):
            improvements['explanation'] = self._generate_explanation(exercise)
        
        return improvements
    
    def _improve_question(self, question: str, issues: List[str]) -> str:
        """改进题目"""
        # 基础改进逻辑
        improved = question
        
        # 添加标点符号
        if not improved.endswith(('?', '!', '.')):
            improved += '?'
        
        # 首字母大写
        if improved and not improved[0].isupper():
            improved = improved[0].upper() + improved[1:]
        
        return improved
    
    def _improve_answer(self, answer: str, issues: List[str]) -> str:
        """改进答案"""
        # 基础改进逻辑
        improved = answer.strip()
        
        # 首字母大写
        if improved and not improved[0].isupper():
            improved = improved[0].upper() + improved[1:]
        
        return improved
    
    def _generate_hint(self, exercise: Dict[str, Any]) -> str:
        """生成提示"""
        topic = exercise.get('topic', '')
        difficulty = exercise.get('difficulty', 'medium')
        
        # 从提示模板中获取
        if topic in self.hint_templates:
            topic_hints = self.hint_templates[topic]
            if difficulty in topic_hints:
                return topic_hints[difficulty]
            elif 'general' in topic_hints:
                return topic_hints['general']
        
        # 默认提示
        return "请仔细思考，选择最合适的答案。"
    
    def _generate_explanation(self, exercise: Dict[str, Any]) -> str:
        """生成解释"""
        topic = exercise.get('topic', '')
        answer = exercise.get('correct_answer', '')
        
        if topic and answer:
            return f"正确答案是 {answer}。这涉及到{topic}的相关知识。"
        elif answer:
            return f"正确答案是 {answer}。"
        else:
            return "请参考相关知识点进行解答。"
    
    def add_validation_rule(self, rule: ValidationRule):
        """添加验证规则"""
        self.validation_rules.append(rule)
    
    def remove_validation_rule(self, rule_name: str):
        """移除验证规则"""
        self.validation_rules = [rule for rule in self.validation_rules if rule.name != rule_name]
    
    def get_validation_rules(self) -> List[ValidationRule]:
        """获取所有验证规则"""
        return self.validation_rules.copy()
    
    def validate_batch(self, exercises: List[Dict[str, Any]]) -> List[ExerciseValidationResult]:
        """批量验证练习题"""
        return [self.validate_exercise(exercise) for exercise in exercises]
    
    def get_validation_statistics(self, results: List[ExerciseValidationResult]) -> Dict[str, Any]:
        """获取验证统计信息"""
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid
        
        avg_confidence = sum(r.confidence_score for r in results) / total if total > 0 else 0
        
        # 统计问题类型
        issue_types = {}
        for result in results:
            for issue in result.issues:
                issue_type = issue.split(':')[0] if ':' in issue else '其他'
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            'total_exercises': total,
            'valid_exercises': valid,
            'invalid_exercises': invalid,
            'validation_rate': valid / total if total > 0 else 0,
            'average_confidence': round(avg_confidence, 2),
            'issue_types': issue_types
        }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量评分系统
建立内容质量评分机制，支持自动质量控制和人工审核
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from ai_content_validator import AIContentValidator, ValidationResult
from enhanced_rule_validator import EnhancedRuleValidator, RuleViolation, Severity

class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"      # 优秀 (90-100)
    GOOD = "good"               # 良好 (75-89)
    FAIR = "fair"               # 一般 (60-74)
    POOR = "poor"               # 较差 (40-59)
    UNACCEPTABLE = "unacceptable"  # 不可接受 (0-39)

@dataclass
class QualityMetrics:
    """质量指标"""
    grammar_score: float = 0.0
    vocabulary_score: float = 0.0
    structure_score: float = 0.0
    content_score: float = 0.0
    style_score: float = 0.0
    educational_score: float = 0.0
    overall_score: float = 0.0

@dataclass
class QualityAssessment:
    """质量评估结果"""
    content_id: str
    content_type: str
    content: str
    metrics: QualityMetrics
    quality_level: QualityLevel
    violations: List[RuleViolation]
    improvement_suggestions: List[str] = None
    confidence: float = 0.0
    assessed_at: datetime = None
    
    def __post_init__(self):
        if self.assessed_at is None:
            self.assessed_at = datetime.now()
        if self.improvement_suggestions is None:
            self.improvement_suggestions = []

class QualityScoringSystem:
    """质量评分系统"""
    
    def __init__(self):
        self.ai_validator = AIContentValidator()
        self.rule_validator = EnhancedRuleValidator()
        
        # 评分权重配置
        self.scoring_weights = {
            'grammar': 0.25,
            'vocabulary': 0.15,
            'structure': 0.20,
            'content': 0.25,
            'style': 0.10,
            'educational': 0.05
        }
        
        # 违规严重程度扣分
        self.violation_penalties = {
            Severity.CRITICAL: 20.0,
            Severity.HIGH: 10.0,
            Severity.MEDIUM: 5.0,
            Severity.LOW: 2.0
        }
        
        # 评分历史存储
        self.assessment_history = []
    
    def assess_content_quality(self, content: str, content_type: str = "sentence",
                             context: Dict[str, Any] = None) -> QualityAssessment:
        """评估内容质量"""
        content_id = f"{content_type}_{hash(content) % 10000:04d}"
        context = context or {}
        
        # 规则验证
        violations = self.rule_validator.validate_content(content, context)
        
        # 计算质量指标
        metrics = self._calculate_quality_metrics(content, violations, context)
        
        # 确定质量等级
        quality_level = self._determine_quality_level(metrics.overall_score)
        
        # 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(violations, metrics)
        
        # 计算置信度
        confidence = self._calculate_confidence(violations, metrics)
        
        assessment = QualityAssessment(
            content_id=content_id,
            content_type=content_type,
            content=content,
            metrics=metrics,
            quality_level=quality_level,
            violations=violations,
            improvement_suggestions=improvement_suggestions,
            confidence=confidence
        )
        
        # 记录评估历史
        self.assessment_history.append(assessment)
        
        return assessment
    
    def _calculate_quality_metrics(self, content: str, violations: List[RuleViolation],
                                 context: Dict[str, Any]) -> QualityMetrics:
        """计算质量指标"""
        
        # 基础分数（满分100）
        base_scores = {
            'grammar': 100.0,
            'vocabulary': 100.0,
            'structure': 100.0,
            'content': 100.0,
            'style': 100.0,
            'educational': 100.0
        }
        
        # 根据违规扣分
        for violation in violations:
            penalty = self.violation_penalties.get(violation.severity, 0.0)
            category = self._map_violation_to_category(violation)
            
            if category in base_scores:
                base_scores[category] -= penalty * violation.confidence
                base_scores[category] = max(0.0, base_scores[category])
        
        # 计算加权总分
        overall_score = sum(
            base_scores[category] * self.scoring_weights.get(category, 0)
            for category in base_scores
        )
        
        return QualityMetrics(
            grammar_score=base_scores['grammar'],
            vocabulary_score=base_scores['vocabulary'],
            structure_score=base_scores['structure'],
            content_score=base_scores['content'],
            style_score=base_scores['style'],
            educational_score=base_scores['educational'],
            overall_score=overall_score
        )
    
    def _map_violation_to_category(self, violation: RuleViolation) -> str:
        """将违规映射到评分类别"""
        if violation.rule_type.value == "grammar":
            return "grammar"
        elif violation.rule_type.value == "vocabulary":
            return "vocabulary"
        elif violation.rule_type.value == "structure":
            return "structure"
        elif violation.rule_type.value == "content":
            return "content"
        elif violation.rule_type.value == "style":
            return "style"
        else:
            return "grammar"
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """确定质量等级"""
        if overall_score >= 90:
            return QualityLevel.EXCELLENT
        elif overall_score >= 75:
            return QualityLevel.GOOD
        elif overall_score >= 60:
            return QualityLevel.FAIR
        elif overall_score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE
    
    def _generate_improvement_suggestions(self, violations: List[RuleViolation],
                                        metrics: QualityMetrics) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于违规的建议
        critical_violations = [v for v in violations if v.severity == Severity.CRITICAL]
        high_violations = [v for v in violations if v.severity == Severity.HIGH]
        
        if critical_violations:
            suggestions.append("🚨 存在严重错误，必须立即修正")
        
        if high_violations:
            suggestions.append("⚠️  需要修正以下高优先级问题")
        
        # 基于评分的建议
        if metrics.grammar_score < 70:
            suggestions.append("📝 建议重点关注语法准确性")
        
        if metrics.overall_score < 60:
            suggestions.append("🔧 建议进行全面修订以提高整体质量")
        
        return suggestions
    
    def _calculate_confidence(self, violations: List[RuleViolation],
                            metrics: QualityMetrics) -> float:
        """计算评估置信度"""
        base_confidence = 0.8
        
        # 基于违规数量调整置信度
        violation_count = len(violations)
        if violation_count == 0:
            base_confidence = 0.95
        elif violation_count <= 2:
            base_confidence = 0.85
        elif violation_count <= 5:
            base_confidence = 0.75
        else:
            base_confidence = 0.6
        
        return min(1.0, base_confidence)
    
    def generate_quality_report(self, assessments: List[QualityAssessment] = None) -> Dict[str, Any]:
        """生成质量报告"""
        if assessments is None:
            assessments = self.assessment_history
        
        if not assessments:
            return {'message': '暂无评估数据'}
        
        # 基础统计
        total_count = len(assessments)
        avg_score = sum(a.metrics.overall_score for a in assessments) / total_count
        
        # 质量等级分布
        quality_distribution = {}
        for level in QualityLevel:
            count = sum(1 for a in assessments if a.quality_level == level)
            quality_distribution[level.value] = {
                'count': count,
                'percentage': (count / total_count) * 100
            }
        
        return {
            'summary': {
                'total_assessments': total_count,
                'average_score': round(avg_score, 2),
            },
            'quality_distribution': quality_distribution,
        }

# 全局质量评分系统实例
quality_scorer = QualityScoringSystem()

if __name__ == "__main__":
    # 测试质量评分系统
    print("=== 质量评分系统测试 ===")
    
    # 测试内容
    test_contents = [
        {
            'content': "I eat an apple every day.",
            'type': 'sentence',
            'context': {
                'target_word': 'apple',
                'grammar_topic': '一般现在时',
            }
        },
        {
            'content': "I eat a apple.",  # 语法错误
            'type': 'sentence',
            'context': {
                'target_word': 'apple',
                'grammar_topic': '一般现在时',
            }
        },
    ]
    
    print("\n--- 内容评估测试 ---")
    assessments = []
    
    for i, item in enumerate(test_contents, 1):
        print(f"\n测试 {i}: {item['content']}")
        
        assessment = quality_scorer.assess_content_quality(
            item['content'],
            item['type'],
            item['context']
        )
        
        assessments.append(assessment)
        
        print(f"质量等级: {assessment.quality_level.value}")
        print(f"总体得分: {assessment.metrics.overall_score:.1f}")
        print(f"置信度: {assessment.confidence:.2f}")
        
        if assessment.violations:
            print(f"发现问题 ({len(assessment.violations)}个):")
            for violation in assessment.violations:
                print(f"  - [{violation.severity.value}] {violation.description}")
    
    # 生成质量报告
    print(f"\n--- 质量报告 ---")
    report = quality_scorer.generate_quality_report(assessments)
    
    print(f"评估摘要:")
    summary = report['summary']
    print(f"  总评估数: {summary['total_assessments']}")
    print(f"  平均得分: {summary['average_score']}")
    
    print(f"\n质量分布:")
    for level, data in report['quality_distribution'].items():
        print(f"  {level}: {data['count']} 个 ({data['percentage']:.1f}%)")
    
    print("\n质量评分系统测试完成！")
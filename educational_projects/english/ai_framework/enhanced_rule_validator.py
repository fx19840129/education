#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强规则验证器
升级现有的规则验证器，与AI验证形成双重保障
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

class RuleType(Enum):
    """规则类型"""
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    STYLE = "style"
    STRUCTURE = "structure"
    CONTENT = "content"

class Severity(Enum):
    """严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class RuleViolation:
    """规则违反"""
    rule_id: str
    rule_type: RuleType
    severity: Severity
    description: str
    suggestion: str
    position: Tuple[int, int] = (0, 0)
    context: str = ""
    confidence: float = 1.0

@dataclass
class ValidationRule:
    """验证规则"""
    id: str
    name: str
    description: str
    rule_type: RuleType
    severity: Severity
    pattern: str = ""
    checker_function: Optional[str] = None
    enabled: bool = True

class EnhancedRuleValidator:
    """增强规则验证器"""
    
    def __init__(self):
        self.rules = {}
        self.load_default_rules()
        self.common_words = self._load_common_words()
    
    def load_default_rules(self):
        """加载默认验证规则"""
        
        # 语法规则
        grammar_rules = [
            ValidationRule(
                id="G001", name="冠词-元音", description="元音前应使用'an'",
                rule_type=RuleType.GRAMMAR, severity=Severity.HIGH,
                pattern=r'\ba\s+([aeiouAEIOU])'
            ),
            ValidationRule(
                id="G002", name="冠词-辅音", description="辅音前应使用'a'",
                rule_type=RuleType.GRAMMAR, severity=Severity.HIGH,
                pattern=r'\ban\s+([bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ])'
            ),
            ValidationRule(
                id="G003", name="be动词-现在分词", description="be动词后跟动词原形错误",
                rule_type=RuleType.GRAMMAR, severity=Severity.CRITICAL,
                pattern=r'\b(am|is|are)\s+(go|come|play|study|work|eat|drink|run|walk)\b'
            ),
        ]
        
        # 文体规则
        style_rules = [
            ValidationRule(
                id="S001", name="句首大写", description="句子应以大写字母开头",
                rule_type=RuleType.STYLE, severity=Severity.MEDIUM,
                pattern=r'^[a-z]'
            ),
            ValidationRule(
                id="S002", name="句末标点", description="句子应以适当标点结尾",
                rule_type=RuleType.STYLE, severity=Severity.MEDIUM,
                pattern=r'[^.!?]\s*$'
            ),
        ]
        
        # 注册所有规则
        all_rules = grammar_rules + style_rules
        for rule in all_rules:
            self.rules[rule.id] = rule
    
    def validate_content(self, text: str, context: Dict[str, Any] = None) -> List[RuleViolation]:
        """验证内容"""
        violations = []
        context = context or {}
        
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                if rule.pattern:
                    # 基于正则表达式的规则
                    rule_violations = self._check_pattern_rule(text, rule, context)
                    violations.extend(rule_violations)
                
            except Exception as e:
                print(f"规则 {rule_id} 检查失败: {e}")
        
        return violations
    
    def _check_pattern_rule(self, text: str, rule: ValidationRule, context: Dict[str, Any]) -> List[RuleViolation]:
        """检查基于模式的规则"""
        violations = []
        
        try:
            pattern = re.compile(rule.pattern, re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                violation = RuleViolation(
                    rule_id=rule.id,
                    rule_type=rule.rule_type,
                    severity=rule.severity,
                    description=rule.description,
                    suggestion=self._get_pattern_suggestion(rule.id, match.group()),
                    position=(match.start(), match.end()),
                    context=text[max(0, match.start()-10):match.end()+10],
                    confidence=0.9
                )
                violations.append(violation)
                
        except re.error as e:
            print(f"正则表达式错误 {rule.id}: {e}")
        
        return violations
    
    def _get_pattern_suggestion(self, rule_id: str, matched_text: str) -> str:
        """获取模式规则的修改建议"""
        suggestions = {
            "G001": f"将 'a' 改为 'an'：{matched_text.replace('a ', 'an ', 1)}",
            "G002": f"将 'an' 改为 'a'：{matched_text.replace('an ', 'a ', 1)}",
            "G003": f"在 be 动词后使用 -ing 形式或去掉 be 动词",
            "S001": "将首字母改为大写",
            "S002": "在句末添加标点符号（. ! ?）",
        }
        return suggestions.get(rule_id, "请修正此处")
    
    def _load_common_words(self) -> Set[str]:
        """加载常见词汇集合"""
        basic_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'you', 'your', 'have', 'had', 'this',
            'they', 'we', 'what', 'when', 'where', 'who', 'how', 'there', 'their',
        }
        return basic_words
    
    def get_rule_summary(self) -> Dict[str, Any]:
        """获取规则摘要"""
        summary = {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for rule in self.rules.values() if rule.enabled),
            'rules_by_type': {},
            'rules_by_severity': {}
        }
        
        for rule in self.rules.values():
            # 按类型统计
            rule_type = rule.rule_type.value
            summary['rules_by_type'][rule_type] = summary['rules_by_type'].get(rule_type, 0) + 1
            
            # 按严重程度统计
            severity = rule.severity.value
            summary['rules_by_severity'][severity] = summary['rules_by_severity'].get(severity, 0) + 1
        
        return summary

# 全局增强规则验证器实例
enhanced_validator = EnhancedRuleValidator()

if __name__ == "__main__":
    # 测试增强规则验证器
    print("=== 增强规则验证器测试 ===")
    
    test_texts = [
        "I eat a apple every day.",  # 冠词错误
        "this is good",             # 首字母小写，缺少标点
        "I am go home now.",        # be动词后跟动词原形错误
    ]
    
    test_context = {
        'target_word': 'apple',
        'grammar_topic': '一般现在时',
        'target_level': 'elementary_3_4'
    }
    
    print("\n--- 验证测试 ---")
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试 {i}: {text}")
        violations = enhanced_validator.validate_content(text, test_context)
        
        if violations:
            print(f"发现 {len(violations)} 个问题:")
            for violation in violations:
                print(f"  - [{violation.severity.value}] {violation.rule_type.value}: {violation.description}")
                print(f"    建议: {violation.suggestion}")
        else:
            print("✓ 未发现问题")
    
    # 获取规则摘要
    print(f"\n--- 规则摘要 ---")
    rule_summary = enhanced_validator.get_rule_summary()
    print(f"总规则数: {rule_summary['total_rules']}")
    print(f"启用规则数: {rule_summary['enabled_rules']}")
    print(f"按类型分布: {rule_summary['rules_by_type']}")
    print(f"按严重程度分布: {rule_summary['rules_by_severity']}")
    
    print("\n增强规则验证器测试完成！")
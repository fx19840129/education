#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI内容验证器
使用GLM-4.5对生成内容进行语法、逻辑、教育适用性验证
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from zhipu_ai_client import ai_client
from content_generation_config import config_manager

class ValidationLevel(Enum):
    """验证级别"""
    BASIC = "basic"           # 基础验证（语法、拼写）
    STANDARD = "standard"     # 标准验证（逻辑、一致性）
    COMPREHENSIVE = "comprehensive"  # 全面验证（教育适用性、文化敏感性）

class ValidationResult(Enum):
    """验证结果"""
    PASS = "pass"             # 通过
    WARNING = "warning"       # 警告（有问题但可接受）
    FAIL = "fail"            # 失败（需要修正）

@dataclass
class ValidationIssue:
    """验证问题"""
    type: str                 # 问题类型
    severity: str            # 严重程度
    description: str         # 问题描述
    suggestion: str          # 修改建议
    location: str = ""       # 问题位置
    
@dataclass
class ContentValidation:
    """内容验证结果"""
    result: ValidationResult
    score: float             # 质量评分 (0-1)
    issues: List[ValidationIssue]
    improved_content: Optional[str] = None
    validation_details: Dict[str, Any] = None

class AIContentValidator:
    """AI内容验证器"""
    
    def __init__(self):
        self.ai_client = ai_client
        self.config_manager = config_manager
        
        # 验证规则配置
        self.validation_rules = {
            "grammar": {
                "patterns": [
                    (r'\ba\s+([aeiou])', '冠词使用错误：应使用"an"而不是"a"'),
                    (r'\ban\s+([bcdfghjklmnpqrstvwxyz])', '冠词使用错误：应使用"a"而不是"an"'),
                    (r'\b(am|is|are)\s+(go|come|play|study)', '动词形式错误：be动词后不能直接跟动词原形'),
                ],
                "severity": "high"
            }
        }
    
    def validate_sentence(self, sentence: str, word_info: Dict[str, Any], 
                         grammar_topic: str, target_level: str = "elementary_3_4",
                         validation_level: ValidationLevel = ValidationLevel.STANDARD) -> ContentValidation:
        """验证例句质量"""
        
        issues = []
        score = 1.0
        
        # 基础验证
        basic_issues, basic_score = self._validate_basic_grammar(sentence)
        issues.extend(basic_issues)
        score *= basic_score
        
        # 确定验证结果
        result = self._determine_validation_result(score, issues)
        
        return ContentValidation(
            result=result,
            score=score,
            issues=issues,
            improved_content=None,
            validation_details={
                "original_sentence": sentence,
                "target_word": word_info.get("word", ""),
                "grammar_topic": grammar_topic,
                "target_level": target_level
            }
        )
    
    def validate_exercise(self, exercise: Dict[str, Any], word_info: Dict[str, Any],
                         grammar_topic: str, target_level: str = "elementary_3_4",
                         validation_level: ValidationLevel = ValidationLevel.STANDARD) -> ContentValidation:
        """验证练习题质量"""
        
        issues = []
        score = 1.0
        
        # 基础验证 - 检查必要字段
        if not exercise.get("question"):
            issues.append(ValidationIssue(
                type="structure", severity="high",
                description="练习题缺少题目", suggestion="添加题目内容"
            ))
            score *= 0.5
        
        # 确定验证结果
        result = self._determine_validation_result(score, issues)
        
        return ContentValidation(
            result=result,
            score=score,
            issues=issues,
            improved_content=None,
            validation_details={
                "original_exercise": exercise,
                "target_word": word_info.get("word", ""),
                "grammar_topic": grammar_topic,
                "target_level": target_level
            }
        )
    
    def _validate_basic_grammar(self, text: str) -> Tuple[List[ValidationIssue], float]:
        """基础语法验证"""
        issues = []
        score = 1.0
        
        for category, rules in self.validation_rules.items():
            for pattern, description in rules["patterns"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    severity = rules["severity"]
                    issues.append(ValidationIssue(
                        type=category,
                        severity=severity,
                        description=description,
                        suggestion=f"修正位置：{match.start()}-{match.end()}",
                        location=f"字符{match.start()}-{match.end()}"
                    ))
                    
                    if severity == "high":
                        score *= 0.8
        
        return issues, score
    
    def _determine_validation_result(self, score: float, issues: List[ValidationIssue]) -> ValidationResult:
        """确定验证结果"""
        high_severity_count = sum(1 for issue in issues if issue.severity == "high")
        
        if score >= 0.8 and high_severity_count == 0:
            return ValidationResult.PASS
        elif score >= 0.6 or high_severity_count <= 1:
            return ValidationResult.WARNING
        else:
            return ValidationResult.FAIL

# 全局验证器实例
content_validator = AIContentValidator()

if __name__ == "__main__":
    # 测试AI内容验证器
    print("=== AI内容验证器测试 ===")
    
    test_word_info = {
        "word": "apple",
        "chinese_meaning": "苹果",
        "part_of_speech": "noun"
    }
    
    test_sentences = [
        "I eat a apple every day.",  # 语法错误
        "This is an apple.",         # 正确例句
    ]
    
    print("\n--- 例句验证测试 ---")
    for sentence in test_sentences:
        validation = content_validator.validate_sentence(
            sentence, test_word_info, "一般现在时"
        )
        
        print(f"\n例句: {sentence}")
        print(f"结果: {validation.result.value}")
        print(f"评分: {validation.score:.2f}")
        if validation.issues:
            print("问题:")
            for issue in validation.issues:
                print(f"  - {issue.type} ({issue.severity}): {issue.description}")
    
    print("\n验证器测试完成！")
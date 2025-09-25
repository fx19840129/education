#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模式生成集成器
在daily_content_generator中集成三种生成模式，支持动态切换
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# 添加路径以导入现有模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'plan_modules'))
sys.path.append(os.path.dirname(__file__))

# 导入AI框架组件
from smart_sentence_generator import sentence_generator
from smart_exercise_generator import exercise_generator
from context_aware_generator import context_generator
from content_cache_manager import cache_manager
from fsrs_ai_integration import fsrs_ai_integration

# 导入质量验证组件
from ai_content_validator import content_validator
from enhanced_rule_validator import enhanced_validator
from quality_scoring_system import quality_scorer
from fallback_protection_system import fallback_system

class GenerationMode(Enum):
    """生成模式"""
    TEMPLATE_ONLY = "template_only"     # 纯模板模式
    AI_ENHANCED = "ai_enhanced"         # AI增强模式
    ADAPTIVE_AI = "adaptive_ai"         # 自适应AI模式

class ContentType(Enum):
    """内容类型"""
    SENTENCE = "sentence"
    EXERCISE = "exercise"
    EXPLANATION = "explanation"
    REVIEW = "review"

@dataclass
class GenerationConfig:
    """生成配置"""
    mode: GenerationMode
    quality_threshold: float = 0.7
    fallback_enabled: bool = True
    cache_enabled: bool = True
    validation_level: str = "standard"  # basic, standard, comprehensive
    personalization_enabled: bool = True

@dataclass
class ContentResult:
    """内容结果"""
    content: str
    metadata: Dict[str, Any]
    quality_score: float
    generation_mode: GenerationMode
    is_fallback: bool = False
    cache_hit: bool = False

class MultiModeIntegration:
    """多模式生成集成器"""
    
    def __init__(self):
        # AI框架组件
        self.sentence_gen = sentence_generator
        self.exercise_gen = exercise_generator
        self.context_gen = context_generator
        self.cache = cache_manager
        self.fsrs_integration = fsrs_ai_integration
        
        # 质量验证组件
        self.content_validator = content_validator
        self.rule_validator = enhanced_validator
        self.quality_scorer = quality_scorer
        self.fallback_system = fallback_system
        
        # 当前配置
        self.current_config = GenerationConfig(
            mode=GenerationMode.AI_ENHANCED,
            quality_threshold=0.7,
            fallback_enabled=True,
            cache_enabled=True
        )
        
        # 模式特定配置
        self.mode_configs = {
            GenerationMode.TEMPLATE_ONLY: {
                "ai_ratio": 0.0,
                "validation_required": False,
                "cache_ttl": 3600,
                "quality_check": "basic"
            },
            GenerationMode.AI_ENHANCED: {
                "ai_ratio": 0.6,
                "validation_required": True,
                "cache_ttl": 1800,
                "quality_check": "standard"
            },
            GenerationMode.ADAPTIVE_AI: {
                "ai_ratio": "dynamic",
                "validation_required": True,
                "cache_ttl": 900,
                "quality_check": "comprehensive"
            }
        }
        
        # 性能统计
        self.generation_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "fallback_used": 0,
            "ai_generations": 0,
            "template_generations": 0,
            "quality_failures": 0
        }
    
    def set_generation_mode(self, mode: GenerationMode, **kwargs):
        """设置生成模式"""
        self.current_config.mode = mode
        
        # 更新配置参数
        for key, value in kwargs.items():
            if hasattr(self.current_config, key):
                setattr(self.current_config, key, value)
        
        print(f"生成模式已切换到: {mode.value}")
    
    def generate_content(self, content_type: ContentType, word_info: Dict[str, Any],
                        grammar_topic: str, context: Dict[str, Any] = None) -> ContentResult:
        """统一内容生成接口"""
        self.generation_stats["total_requests"] += 1
        context = context or {}
        
        # 检查降级状态
        if not self.fallback_system.is_feature_enabled("ai_generation"):
            return self._generate_fallback_content(content_type, word_info, grammar_topic, context)
        
        # 检查缓存
        if self.current_config.cache_enabled:
            cache_key = self._generate_cache_key(content_type, word_info, grammar_topic, context)
            cached_result = self._try_get_cached_content(cache_key)
            if cached_result:
                self.generation_stats["cache_hits"] += 1
                return cached_result
        
        # 根据模式生成内容
        try:
            if self.current_config.mode == GenerationMode.TEMPLATE_ONLY:
                result = self._generate_template_content(content_type, word_info, grammar_topic, context)
            elif self.current_config.mode == GenerationMode.AI_ENHANCED:
                result = self._generate_ai_enhanced_content(content_type, word_info, grammar_topic, context)
            elif self.current_config.mode == GenerationMode.ADAPTIVE_AI:
                result = self._generate_adaptive_content(content_type, word_info, grammar_topic, context)
            else:
                raise ValueError(f"未知生成模式: {self.current_config.mode}")
            
            # 质量验证
            if self.current_config.quality_threshold > 0:
                result = self._validate_and_improve_content(result, word_info, grammar_topic)
            
            # 存储到缓存
            if self.current_config.cache_enabled and result.quality_score >= self.current_config.quality_threshold:
                self._store_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            print(f"内容生成失败: {e}")
            if self.current_config.fallback_enabled:
                self.generation_stats["fallback_used"] += 1
                return self._generate_fallback_content(content_type, word_info, grammar_topic, context)
            else:
                raise e
    
    def _generate_template_content(self, content_type: ContentType, word_info: Dict[str, Any],
                                 grammar_topic: str, context: Dict[str, Any]) -> ContentResult:
        """生成模板内容"""
        self.generation_stats["template_generations"] += 1
        
        word = word_info.get("word", "example")
        chinese = word_info.get("chinese_meaning", "示例")
        
        if content_type == ContentType.SENTENCE:
            content = f"This is a {word}."
            metadata = {
                "translation": f"这是一个{chinese}。",
                "template": "basic_sentence",
                "complexity": "simple"
            }
        elif content_type == ContentType.EXERCISE:
            content = f"Fill in the blank: This is a _____."
            metadata = {
                "answer": word,
                "hint": f"Use the word '{word}'",
                "type": "fill_blank"
            }
        else:
            content = f"Learn the word: {word} ({chinese})"
            metadata = {"type": "basic_explanation"}
        
        return ContentResult(
            content=content,
            metadata=metadata,
            quality_score=0.7,
            generation_mode=GenerationMode.TEMPLATE_ONLY
        )
    
    def _generate_ai_enhanced_content(self, content_type: ContentType, word_info: Dict[str, Any],
                                    grammar_topic: str, context: Dict[str, Any]) -> ContentResult:
        """生成AI增强内容"""
        self.generation_stats["ai_generations"] += 1
        
        # 创建WordInfo对象
        from word_learning_modules.word_database import WordInfo
        word_obj = WordInfo(
            word=word_info.get("word", ""),
            pronunciation=word_info.get("pronunciation", ""),
            part_of_speech=word_info.get("part_of_speech", ""),
            chinese_meaning=word_info.get("chinese_meaning", ""),
            english_meaning=word_info.get("english_meaning", ""),
            example_sentence=word_info.get("example_sentence", ""),
            difficulty=word_info.get("difficulty", "medium"),
            grade_level=word_info.get("grade_level", "elementary"),
            category=word_info.get("category", "general")
        )
        
        if content_type == ContentType.SENTENCE:
            # 使用AI增强例句生成
            sentence_result = self.sentence_gen.generate_sentence(
                word_obj, grammar_topic, mode="balanced"
            )
            
            return ContentResult(
                content=sentence_result.sentence,
                metadata={
                    "translation": sentence_result.chinese_translation,
                    "grammar_focus": sentence_result.grammar_focus,
                    "ai_generated": sentence_result.is_ai_generated,
                    "template_used": sentence_result.template_used
                },
                quality_score=sentence_result.quality_score,
                generation_mode=GenerationMode.AI_ENHANCED
            )
        
        elif content_type == ContentType.EXERCISE:
            # 使用AI增强练习题生成
            from smart_exercise_generator import ExerciseType
            exercise = self.exercise_gen.generate_exercise(
                word_obj, grammar_topic, ExerciseType.FILL_BLANK, mode="balanced"
            )
            
            return ContentResult(
                content=exercise.question,
                metadata={
                    "answer": exercise.answer,
                    "hint": exercise.hint,
                    "explanation": exercise.explanation,
                    "type": exercise.exercise_type.value,
                    "ai_generated": exercise.is_ai_generated
                },
                quality_score=exercise.quality_score,
                generation_mode=GenerationMode.AI_ENHANCED
            )
        
        else:
            # 默认使用模板
            return self._generate_template_content(content_type, word_info, grammar_topic, context)
    
    def _generate_adaptive_content(self, content_type: ContentType, word_info: Dict[str, Any],
                                 grammar_topic: str, context: Dict[str, Any]) -> ContentResult:
        """生成自适应内容"""
        self.generation_stats["ai_generations"] += 1
        
        # 创建WordInfo对象
        from word_learning_modules.word_database import WordInfo
        word_obj = WordInfo(
            word=word_info.get("word", ""),
            pronunciation=word_info.get("pronunciation", ""),
            part_of_speech=word_info.get("part_of_speech", ""),
            chinese_meaning=word_info.get("chinese_meaning", ""),
            english_meaning=word_info.get("english_meaning", ""),
            example_sentence=word_info.get("example_sentence", ""),
            difficulty=word_info.get("difficulty", "medium"),
            grade_level=word_info.get("grade_level", "elementary"),
            category=word_info.get("category", "general")
        )
        
        # 获取用户档案
        user_profile = context.get("user_profile")
        if not user_profile:
            user_profile = self.context_gen.load_user_profile("default")
        
        # 使用FSRS集成生成自适应内容
        adaptive_content = self.fsrs_integration.generate_adaptive_content(
            word_obj, grammar_topic, user_profile
        )
        
        if content_type == ContentType.SENTENCE:
            # 返回第一个例句
            sentences = adaptive_content.get("sentences", [])
            if sentences:
                sentence = sentences[0]
                return ContentResult(
                    content=sentence["content"],
                    metadata={
                        "translation": sentence["translation"],
                        "complexity": sentence["complexity"],
                        "ai_generated": sentence["ai_generated"],
                        "adaptive_config": adaptive_content.get("adaptive_config")
                    },
                    quality_score=sentence["quality_score"],
                    generation_mode=GenerationMode.ADAPTIVE_AI
                )
        
        elif content_type == ContentType.EXERCISE:
            # 返回第一个练习题
            exercises = adaptive_content.get("exercises", [])
            if exercises:
                exercise = exercises[0]
                return ContentResult(
                    content=exercise["question"],
                    metadata={
                        "answer": exercise["answer"],
                        "hint": exercise["hint"],
                        "explanation": exercise["explanation"],
                        "type": exercise["type"],
                        "difficulty": exercise["difficulty"],
                        "ai_generated": exercise["ai_generated"]
                    },
                    quality_score=exercise["quality_score"],
                    generation_mode=GenerationMode.ADAPTIVE_AI
                )
        
        # 默认返回模板内容
        return self._generate_template_content(content_type, word_info, grammar_topic, context)
    
    def _validate_and_improve_content(self, result: ContentResult, word_info: Dict[str, Any],
                                    grammar_topic: str) -> ContentResult:
        """验证并改进内容质量"""
        
        # 规则验证
        violations = self.rule_validator.validate_content(
            result.content, 
            {
                "target_word": word_info.get("word", ""),
                "grammar_topic": grammar_topic
            }
        )
        
        # 质量评分
        assessment = self.quality_scorer.assess_content_quality(
            result.content,
            result.metadata.get("type", "sentence"),
            {
                "word_info": word_info,
                "grammar_topic": grammar_topic
            }
        )
        
        # 更新质量评分
        result.quality_score = min(result.quality_score, assessment.metrics.overall_score / 100)
        
        # 如果质量不达标，尝试改进
        if result.quality_score < self.current_config.quality_threshold:
            self.generation_stats["quality_failures"] += 1
            
            # 简单的改进策略：如果有违规，降级到模板
            if violations:
                print(f"内容质量不达标，降级到模板模式")
                return self._generate_template_content(
                    ContentType.SENTENCE if "answer" not in result.metadata else ContentType.EXERCISE,
                    word_info, grammar_topic, {}
                )
        
        return result
    
    def _generate_fallback_content(self, content_type: ContentType, word_info: Dict[str, Any],
                                 grammar_topic: str, context: Dict[str, Any]) -> ContentResult:
        """生成降级内容"""
        safe_content = self.fallback_system.get_fallback_safe_content(
            content_type.value, 
            {
                "target_word": word_info.get("word", ""),
                "chinese_meaning": word_info.get("chinese_meaning", "")
            }
        )
        
        return ContentResult(
            content=safe_content["content"],
            metadata=safe_content,
            quality_score=safe_content.get("quality_score", 0.6),
            generation_mode=self.current_config.mode,
            is_fallback=True
        )
    
    def _generate_cache_key(self, content_type: ContentType, word_info: Dict[str, Any],
                          grammar_topic: str, context: Dict[str, Any]) -> str:
        """生成缓存键"""
        key_parts = [
            content_type.value,
            word_info.get("word", ""),
            grammar_topic,
            self.current_config.mode.value,
            str(int(self.current_config.quality_threshold * 100))
        ]
        return "_".join(key_parts)
    
    def _try_get_cached_content(self, cache_key: str) -> Optional[ContentResult]:
        """尝试获取缓存内容"""
        cached_data = self.cache.get_cached_content(cache_key)
        if cached_data:
            try:
                return ContentResult(
                    content=cached_data.get("content", ""),
                    metadata=cached_data.get("metadata", {}),
                    quality_score=cached_data.get("quality_score", 0.7),
                    generation_mode=GenerationMode(cached_data.get("generation_mode", "template_only")),
                    cache_hit=True
                )
            except Exception as e:
                print(f"缓存数据解析失败: {e}")
        
        return None
    
    def _store_to_cache(self, cache_key: str, result: ContentResult):
        """存储内容到缓存"""
        cache_data = {
            "content": result.content,
            "metadata": result.metadata,
            "quality_score": result.quality_score,
            "generation_mode": result.generation_mode.value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.cache.store_content(cache_key, json.dumps(cache_data), "multi_mode_content")
    
    def batch_generate_content(self, requests: List[Dict[str, Any]]) -> List[ContentResult]:
        """批量生成内容"""
        results = []
        
        for request in requests:
            try:
                result = self.generate_content(
                    ContentType(request["content_type"]),
                    request["word_info"],
                    request["grammar_topic"],
                    request.get("context", {})
                )
                results.append(result)
                
            except Exception as e:
                print(f"批量生成失败: {e}")
                # 添加错误结果
                results.append(ContentResult(
                    content="Generation failed",
                    metadata={"error": str(e)},
                    quality_score=0.0,
                    generation_mode=self.current_config.mode
                ))
        
        return results
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        total = max(self.generation_stats["total_requests"], 1)
        
        return {
            "current_mode": self.current_config.mode.value,
            "total_requests": self.generation_stats["total_requests"],
            "cache_hit_rate": (self.generation_stats["cache_hits"] / total) * 100,
            "fallback_rate": (self.generation_stats["fallback_used"] / total) * 100,
            "ai_generation_rate": (self.generation_stats["ai_generations"] / total) * 100,
            "template_generation_rate": (self.generation_stats["template_generations"] / total) * 100,
            "quality_failure_rate": (self.generation_stats["quality_failures"] / total) * 100,
            "quality_threshold": self.current_config.quality_threshold,
            "fallback_enabled": self.current_config.fallback_enabled,
            "cache_enabled": self.current_config.cache_enabled
        }
    
    def optimize_generation_mode(self) -> GenerationMode:
        """基于统计数据优化生成模式"""
        stats = self.get_generation_statistics()
        
        # 如果降级使用率过高，切换到更保守的模式
        if stats["fallback_rate"] > 20:
            recommended_mode = GenerationMode.TEMPLATE_ONLY
        elif stats["quality_failure_rate"] > 15:
            recommended_mode = GenerationMode.AI_ENHANCED
        elif stats["cache_hit_rate"] > 80:
            # 缓存命中率高，可以尝试更高级的模式
            recommended_mode = GenerationMode.ADAPTIVE_AI
        else:
            recommended_mode = self.current_config.mode
        
        if recommended_mode != self.current_config.mode:
            print(f"建议切换生成模式: {self.current_config.mode.value} -> {recommended_mode.value}")
        
        return recommended_mode

# 全局多模式集成器实例
multi_mode_integration = MultiModeIntegration()

if __name__ == "__main__":
    # 测试多模式生成集成
    print("=== 多模式生成集成测试 ===")
    
    # 测试单词信息
    test_word_info = {
        "word": "apple",
        "chinese_meaning": "苹果",
        "part_of_speech": "noun",
        "difficulty": "easy",
        "grade_level": "elementary_1_2",
        "category": "food"
    }
    
    # 测试不同生成模式
    modes = [GenerationMode.TEMPLATE_ONLY, GenerationMode.AI_ENHANCED, GenerationMode.ADAPTIVE_AI]
    
    for mode in modes:
        print(f"\n--- {mode.value.upper()} 模式测试 ---")
        
        # 设置模式
        multi_mode_integration.set_generation_mode(mode)
        
        # 生成例句
        try:
            sentence_result = multi_mode_integration.generate_content(
                ContentType.SENTENCE,
                test_word_info,
                "一般现在时"
            )
            
            print(f"例句: {sentence_result.content}")
            print(f"质量评分: {sentence_result.quality_score:.2f}")
            print(f"是否降级: {sentence_result.is_fallback}")
            print(f"缓存命中: {sentence_result.cache_hit}")
            
            if "translation" in sentence_result.metadata:
                print(f"翻译: {sentence_result.metadata['translation']}")
        
        except Exception as e:
            print(f"例句生成失败: {e}")
        
        # 生成练习题
        try:
            exercise_result = multi_mode_integration.generate_content(
                ContentType.EXERCISE,
                test_word_info,
                "一般现在时"
            )
            
            print(f"练习题: {exercise_result.content}")
            if "answer" in exercise_result.metadata:
                print(f"答案: {exercise_result.metadata['answer']}")
        
        except Exception as e:
            print(f"练习题生成失败: {e}")
    
    # 获取统计信息
    print(f"\n--- 生成统计 ---")
    stats = multi_mode_integration.get_generation_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.1f}%")
        else:
            print(f"{key}: {value}")
    
    # 优化建议
    recommended_mode = multi_mode_integration.optimize_generation_mode()
    print(f"\n推荐生成模式: {recommended_mode.value}")
    
    print("\n多模式生成集成测试完成！")

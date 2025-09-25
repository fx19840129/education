#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FSRS与AI生成集成器
基于FSRS记忆数据调整AI生成策略，实现个性化难度控制
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import sys

# 添加路径以导入现有模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'plan_modules'))

# 导入现有组件
from smart_sentence_generator import sentence_generator, WordInfo
from smart_exercise_generator import exercise_generator, ExerciseType
from context_aware_generator import context_generator, UserProfile
from content_cache_manager import cache_manager

class DifficultyLevel(Enum):
    """难度级别"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class GenerationStrategy(Enum):
    """生成策略"""
    REINFORCEMENT = "reinforcement"    # 强化记忆
    CHALLENGE = "challenge"           # 挑战提升
    REVIEW = "review"                # 复习巩固
    INTRODUCTION = "introduction"     # 初次学习

@dataclass
class FSRSMemoryState:
    """FSRS记忆状态"""
    word: str
    stability: float           # 稳定性
    difficulty: float         # 难度
    retrievability: float     # 可提取性
    last_review: datetime
    review_count: int
    grade_history: List[int]  # 评分历史

@dataclass
class AdaptiveGenerationConfig:
    """自适应生成配置"""
    difficulty_level: DifficultyLevel
    generation_strategy: GenerationStrategy
    ai_enhancement_ratio: float
    sentence_complexity: str     # simple, moderate, complex
    exercise_types: List[ExerciseType]
    context_richness: str       # minimal, standard, rich
    personalization_weight: float

class FSRSAIIntegration:
    """FSRS与AI生成集成器"""
    
    def __init__(self):
        self.sentence_gen = sentence_generator
        self.exercise_gen = exercise_generator
        self.context_gen = context_generator
        self.cache = cache_manager
        
        # 难度映射配置
        self.difficulty_thresholds = {
            DifficultyLevel.VERY_EASY: (0.0, 3.0),
            DifficultyLevel.EASY: (3.0, 5.0),
            DifficultyLevel.MEDIUM: (5.0, 7.0),
            DifficultyLevel.HARD: (7.0, 9.0),
            DifficultyLevel.VERY_HARD: (9.0, 10.0)
        }
        
        # 策略配置
        self.strategy_configs = {
            GenerationStrategy.INTRODUCTION: {
                "ai_enhancement": 0.3,
                "sentence_complexity": "simple",
                "exercise_types": [ExerciseType.FILL_BLANK],
                "context_richness": "minimal"
            },
            GenerationStrategy.REINFORCEMENT: {
                "ai_enhancement": 0.6,
                "sentence_complexity": "moderate", 
                "exercise_types": [ExerciseType.FILL_BLANK, ExerciseType.TRANSLATION],
                "context_richness": "standard"
            },
            GenerationStrategy.REVIEW: {
                "ai_enhancement": 0.4,
                "sentence_complexity": "simple",
                "exercise_types": [ExerciseType.MULTIPLE_CHOICE, ExerciseType.FILL_BLANK],
                "context_richness": "standard"
            },
            GenerationStrategy.CHALLENGE: {
                "ai_enhancement": 0.9,
                "sentence_complexity": "complex",
                "exercise_types": [ExerciseType.SENTENCE_COMPLETION, ExerciseType.GRAMMAR_CORRECTION],
                "context_richness": "rich"
            }
        }
        
        # 记忆状态存储
        self.memory_states: Dict[str, FSRSMemoryState] = {}
        self.load_memory_states()
    
    def load_memory_states(self, file_path: str = "../plan_modules/learning_data/fsrs_memory.json"):
        """加载FSRS记忆状态"""
        try:
            abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), file_path))
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for word, state_data in data.get('memory_cards', {}).items():
                    self.memory_states[word] = FSRSMemoryState(
                        word=word,
                        stability=state_data.get('stability', 1.0),
                        difficulty=state_data.get('difficulty', 5.0),
                        retrievability=state_data.get('retrievability', 0.9),
                        last_review=datetime.fromisoformat(state_data.get('last_review', datetime.now().isoformat())),
                        review_count=state_data.get('review_count', 0),
                        grade_history=state_data.get('grade_history', [3])
                    )
                    
                print(f"加载了 {len(self.memory_states)} 个单词的FSRS记忆状态")
            else:
                print(f"FSRS记忆文件不存在: {abs_path}")
                
        except Exception as e:
            print(f"加载FSRS记忆状态失败: {e}")
    
    def analyze_memory_state(self, word: str) -> Tuple[DifficultyLevel, GenerationStrategy]:
        """分析单词的记忆状态并确定生成策略"""
        if word not in self.memory_states:
            # 新单词，使用介绍策略
            return DifficultyLevel.EASY, GenerationStrategy.INTRODUCTION
        
        state = self.memory_states[word]
        
        # 根据FSRS参数确定难度级别
        difficulty_level = self._determine_difficulty_level(state)
        
        # 根据记忆状态确定生成策略
        generation_strategy = self._determine_generation_strategy(state)
        
        return difficulty_level, generation_strategy
    
    def _determine_difficulty_level(self, state: FSRSMemoryState) -> DifficultyLevel:
        """根据FSRS状态确定难度级别"""
        # 综合考虑difficulty和retrievability
        combined_difficulty = state.difficulty * (1 - state.retrievability) * 2
        
        for level, (min_val, max_val) in self.difficulty_thresholds.items():
            if min_val <= combined_difficulty < max_val:
                return level
        
        return DifficultyLevel.MEDIUM
    
    def _determine_generation_strategy(self, state: FSRSMemoryState) -> GenerationStrategy:
        """根据FSRS状态确定生成策略"""
        # 新单词（复习次数少）
        if state.review_count <= 2:
            return GenerationStrategy.INTRODUCTION
        
        # 基于可提取性确定策略
        if state.retrievability < 0.5:
            # 遗忘风险高，需要强化
            return GenerationStrategy.REINFORCEMENT
        elif state.retrievability > 0.8:
            # 记忆良好，可以挑战
            return GenerationStrategy.CHALLENGE
        else:
            # 中等状态，适合复习
            return GenerationStrategy.REVIEW
    
    def create_adaptive_config(self, word: str, grammar_topic: str,
                             user_profile: UserProfile = None) -> AdaptiveGenerationConfig:
        """创建自适应生成配置"""
        difficulty_level, strategy = self.analyze_memory_state(word)
        
        # 获取基础策略配置
        base_config = self.strategy_configs[strategy]
        
        # 根据用户档案调整
        if user_profile:
            ai_enhancement = base_config["ai_enhancement"]
            
            # 根据用户学习风格调整AI增强比例
            if user_profile.learning_style == "visual":
                ai_enhancement *= 1.2  # 视觉学习者受益于更丰富的内容
            elif user_profile.learning_style == "kinesthetic":
                ai_enhancement *= 1.1  # 动觉学习者需要更多样化的练习
            
            # 根据用户难度偏好调整
            if user_profile.difficulty_preference == "easy":
                ai_enhancement *= 0.8
            elif user_profile.difficulty_preference == "hard":
                ai_enhancement *= 1.3
            
            ai_enhancement = min(1.0, max(0.1, ai_enhancement))
        else:
            ai_enhancement = base_config["ai_enhancement"]
        
        # 根据语法主题调整练习类型
        exercise_types = list(base_config["exercise_types"])
        if grammar_topic in ["形容词比较级", "被动语态", "定语从句"]:
            # 复杂语法主题需要更多样化的练习
            if strategy == GenerationStrategy.CHALLENGE:
                exercise_types.append(ExerciseType.GRAMMAR_CORRECTION)
        
        return AdaptiveGenerationConfig(
            difficulty_level=difficulty_level,
            generation_strategy=strategy,
            ai_enhancement_ratio=ai_enhancement,
            sentence_complexity=base_config["sentence_complexity"],
            exercise_types=exercise_types,
            context_richness=base_config["context_richness"],
            personalization_weight=self._calculate_personalization_weight(word)
        )
    
    def _calculate_personalization_weight(self, word: str) -> float:
        """计算个性化权重"""
        if word not in self.memory_states:
            return 0.5  # 新单词的中等权重
        
        state = self.memory_states[word]
        
        # 基于复习次数和表现计算权重
        avg_grade = sum(state.grade_history) / len(state.grade_history) if state.grade_history else 3
        
        # 表现差的单词需要更高的个性化
        if avg_grade < 2.5:
            return 0.9
        elif avg_grade > 3.5:
            return 0.3
        else:
            return 0.6
    
    def generate_adaptive_content(self, word_info: WordInfo, grammar_topic: str,
                                user_profile: UserProfile = None) -> Dict[str, Any]:
        """生成自适应内容"""
        # 创建自适应配置
        config = self.create_adaptive_config(word_info.word, grammar_topic, user_profile)
        
        # 检查缓存
        cache_key = self._generate_cache_key(word_info, grammar_topic, config)
        cached_content = self.cache.get_cached_content(cache_key)
        
        if cached_content:
            print(f"使用缓存内容: {word_info.word}")
            return cached_content
        
        # 生成例句
        sentences = self._generate_adaptive_sentences(word_info, grammar_topic, config)
        
        # 生成练习题
        exercises = self._generate_adaptive_exercises(word_info, grammar_topic, config)
        
        # 生成学习建议
        learning_suggestions = self._generate_learning_suggestions(config, word_info)
        
        content = {
            "word": word_info.word,
            "sentences": sentences,
            "exercises": exercises,
            "learning_suggestions": learning_suggestions,
            "adaptive_config": asdict(config),
            "generation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "strategy": config.generation_strategy.value,
                "difficulty": config.difficulty_level.value,
                "personalization_weight": config.personalization_weight
            }
        }
        
        # 存储到缓存
        self.cache.store_content(cache_key, json.dumps(content), "adaptive_content")
        
        return content
    
    def _generate_adaptive_sentences(self, word_info: WordInfo, grammar_topic: str,
                                   config: AdaptiveGenerationConfig) -> List[Dict[str, Any]]:
        """生成自适应例句"""
        sentences = []
        
        # 根据复杂程度确定例句数量
        sentence_count = {
            "simple": 2,
            "moderate": 3,
            "complex": 4
        }.get(config.sentence_complexity, 3)
        
        for i in range(sentence_count):
            try:
                # 根据配置选择生成模式
                if config.ai_enhancement_ratio > 0.7:
                    mode = "innovative"
                elif config.ai_enhancement_ratio > 0.4:
                    mode = "balanced"
                else:
                    mode = "conservative"
                
                # 根据上下文丰富度选择场景
                scenario = self._select_scenario_by_richness(config.context_richness, word_info)
                
                sentence_result = self.sentence_gen.generate_sentence(
                    word_info, grammar_topic, mode=mode, scenario=scenario
                )
                
                sentences.append({
                    "content": sentence_result.sentence,
                    "translation": sentence_result.chinese_translation,
                    "complexity": config.sentence_complexity,
                    "ai_generated": sentence_result.is_ai_generated,
                    "quality_score": sentence_result.quality_score
                })
                
            except Exception as e:
                print(f"生成自适应例句失败: {e}")
                # 使用模板作为备选
                sentences.append({
                    "content": f"This is a {word_info.word}.",
                    "translation": f"这是一个{word_info.chinese_meaning}。",
                    "complexity": "simple",
                    "ai_generated": False,
                    "quality_score": 0.7
                })
        
        return sentences
    
    def _generate_adaptive_exercises(self, word_info: WordInfo, grammar_topic: str,
                                   config: AdaptiveGenerationConfig) -> List[Dict[str, Any]]:
        """生成自适应练习题"""
        exercises = []
        
        for exercise_type in config.exercise_types:
            try:
                # 根据难度级别调整练习复杂度
                exercise_context = {
                    "difficulty_level": config.difficulty_level.value,
                    "strategy": config.generation_strategy.value
                }
                
                exercise = self.exercise_gen.generate_exercise(
                    word_info, grammar_topic, exercise_type
                )
                
                exercises.append({
                    "type": exercise_type.value,
                    "question": exercise.question,
                    "answer": exercise.answer,
                    "hint": exercise.hint,
                    "explanation": exercise.explanation,
                    "difficulty": config.difficulty_level.value,
                    "ai_generated": exercise.is_ai_generated,
                    "quality_score": exercise.quality_score
                })
                
            except Exception as e:
                print(f"生成自适应练习题失败 {exercise_type}: {e}")
        
        return exercises
    
    def _select_scenario_by_richness(self, richness: str, word_info: WordInfo) -> str:
        """根据上下文丰富度选择场景"""
        scenarios = {
            "minimal": ["daily_life"],
            "standard": ["daily_life", "school", "family"],
            "rich": ["daily_life", "school", "family", "sports", "food", "travel", "technology"]
        }
        
        available_scenarios = scenarios.get(richness, scenarios["standard"])
        
        # 根据单词类别选择最合适的场景
        word_category = word_info.category.lower()
        
        if "food" in word_category and "food" in available_scenarios:
            return "food"
        elif "sport" in word_category and "sports" in available_scenarios:
            return "sports"
        elif "school" in word_category and "school" in available_scenarios:
            return "school"
        else:
            return available_scenarios[0]
    
    def _generate_learning_suggestions(self, config: AdaptiveGenerationConfig,
                                     word_info: WordInfo) -> List[str]:
        """生成学习建议"""
        suggestions = []
        
        # 基于生成策略的建议
        if config.generation_strategy == GenerationStrategy.INTRODUCTION:
            suggestions.append("🆕 这是一个新单词，建议多次重复练习")
            suggestions.append("📝 重点关注单词的基本含义和发音")
        
        elif config.generation_strategy == GenerationStrategy.REINFORCEMENT:
            suggestions.append("💪 这个单词需要加强记忆，增加练习频率")
            suggestions.append("🔄 建议结合不同场景多次练习")
        
        elif config.generation_strategy == GenerationStrategy.REVIEW:
            suggestions.append("📚 定期复习这个单词，保持记忆新鲜")
            suggestions.append("🎯 重点练习在句子中的应用")
        
        elif config.generation_strategy == GenerationStrategy.CHALLENGE:
            suggestions.append("🚀 你已经掌握得很好，可以挑战更复杂的用法")
            suggestions.append("🌟 尝试在写作中主动使用这个单词")
        
        # 基于难度级别的建议
        if config.difficulty_level in [DifficultyLevel.HARD, DifficultyLevel.VERY_HARD]:
            suggestions.append("⚡ 这个单词有一定难度，不要着急，慢慢来")
            suggestions.append("🧠 可以联想记忆法或词根分析来帮助记忆")
        
        return suggestions
    
    def _generate_cache_key(self, word_info: WordInfo, grammar_topic: str,
                          config: AdaptiveGenerationConfig) -> str:
        """生成缓存键"""
        key_components = [
            word_info.word,
            grammar_topic,
            config.difficulty_level.value,
            config.generation_strategy.value,
            str(int(config.ai_enhancement_ratio * 10))
        ]
        return "_".join(key_components)
    
    def update_memory_performance(self, word: str, performance_grade: int):
        """更新单词的学习表现"""
        if word in self.memory_states:
            state = self.memory_states[word]
            state.grade_history.append(performance_grade)
            state.last_review = datetime.now()
            state.review_count += 1
            
            # 限制历史记录长度
            if len(state.grade_history) > 20:
                state.grade_history = state.grade_history[-20:]
            
            print(f"更新单词 {word} 的学习表现: {performance_grade}")
    
    def get_adaptation_statistics(self) -> Dict[str, Any]:
        """获取自适应统计信息"""
        if not self.memory_states:
            return {"message": "暂无FSRS记忆数据"}
        
        # 策略分布统计
        strategy_counts = {}
        difficulty_counts = {}
        
        for word in self.memory_states.keys():
            difficulty, strategy = self.analyze_memory_state(word)
            
            strategy_counts[strategy.value] = strategy_counts.get(strategy.value, 0) + 1
            difficulty_counts[difficulty.value] = difficulty_counts.get(difficulty.value, 0) + 1
        
        # 平均记忆参数
        total_stability = sum(s.stability for s in self.memory_states.values())
        total_difficulty = sum(s.difficulty for s in self.memory_states.values())
        total_retrievability = sum(s.retrievability for s in self.memory_states.values())
        
        count = len(self.memory_states)
        
        return {
            "total_words": count,
            "strategy_distribution": strategy_counts,
            "difficulty_distribution": difficulty_counts,
            "average_memory_params": {
                "stability": total_stability / count,
                "difficulty": total_difficulty / count,
                "retrievability": total_retrievability / count
            },
            "adaptation_enabled": True
        }

# 全局FSRS-AI集成器实例
fsrs_ai_integration = FSRSAIIntegration()

if __name__ == "__main__":
    # 测试FSRS-AI集成
    print("=== FSRS-AI集成测试 ===")
    
    # 创建测试单词
    test_word = WordInfo(
        word="computer",
        chinese_meaning="电脑",
        part_of_speech="noun",
        difficulty="medium",
        grade_level="elementary_5_6",
        category="technology"
    )
    
    # 创建测试用户档案
    test_profile = UserProfile(
        user_id="test_user",
        learning_style="visual",
        difficulty_preference="medium",
        interests=["technology"]
    )
    
    print(f"\n--- 内存状态分析 ---")
    difficulty, strategy = fsrs_ai_integration.analyze_memory_state(test_word.word)
    print(f"单词: {test_word.word}")
    print(f"难度级别: {difficulty.value}")
    print(f"生成策略: {strategy.value}")
    
    print(f"\n--- 自适应配置创建 ---")
    config = fsrs_ai_integration.create_adaptive_config(
        test_word.word, "一般现在时", test_profile
    )
    print(f"AI增强比例: {config.ai_enhancement_ratio:.2f}")
    print(f"句子复杂度: {config.sentence_complexity}")
    print(f"练习类型: {[t.value for t in config.exercise_types]}")
    print(f"个性化权重: {config.personalization_weight:.2f}")
    
    print(f"\n--- 自适应内容生成 ---")
    try:
        adaptive_content = fsrs_ai_integration.generate_adaptive_content(
            test_word, "一般现在时", test_profile
        )
        
        print(f"生成例句数: {len(adaptive_content['sentences'])}")
        print(f"生成练习数: {len(adaptive_content['exercises'])}")
        print(f"学习建议数: {len(adaptive_content['learning_suggestions'])}")
        
        print(f"\n例句示例:")
        for i, sentence in enumerate(adaptive_content['sentences'][:2], 1):
            print(f"  {i}. {sentence['content']}")
            print(f"     {sentence['translation']}")
            print(f"     复杂度: {sentence['complexity']}, AI生成: {sentence['ai_generated']}")
        
        print(f"\n学习建议:")
        for suggestion in adaptive_content['learning_suggestions']:
            print(f"  • {suggestion}")
            
    except Exception as e:
        print(f"自适应内容生成失败: {e}")
    
    # 获取统计信息
    print(f"\n--- 自适应统计 ---")
    stats = fsrs_ai_integration.get_adaptation_statistics()
    print(f"总单词数: {stats.get('total_words', 0)}")
    print(f"策略分布: {stats.get('strategy_distribution', {})}")
    print(f"难度分布: {stats.get('difficulty_distribution', {})}")
    
    print("\nFSRS-AI集成测试完成！")

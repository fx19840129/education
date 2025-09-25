#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文感知内容生成器
结合FSRS学习数据和用户历史，生成个性化学习内容
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from zhipu_ai_client import ai_client
from content_generation_config import config_manager
from smart_sentence_generator import sentence_generator, WordInfo, SentenceResult
from smart_exercise_generator import exercise_generator, Exercise, ExerciseType

@dataclass
class UserProfile:
    """用户学习档案"""
    user_id: str
    learning_style: str = "balanced"  # visual, auditory, kinesthetic, balanced
    difficulty_preference: str = "medium"  # easy, medium, hard, adaptive
    interests: List[str] = None
    weak_grammar_topics: List[str] = None
    strong_grammar_topics: List[str] = None
    learning_pace: str = "normal"  # slow, normal, fast
    preferred_exercise_types: List[str] = None
    
    def __post_init__(self):
        if self.interests is None:
            self.interests = []
        if self.weak_grammar_topics is None:
            self.weak_grammar_topics = []
        if self.strong_grammar_topics is None:
            self.strong_grammar_topics = []
        if self.preferred_exercise_types is None:
            self.preferred_exercise_types = []

@dataclass
class LearningContext:
    """学习上下文"""
    current_day: int
    recent_words: List[str]
    recent_grammar_topics: List[str]
    user_performance: Dict[str, float]
    fsrs_memory_state: Dict[str, Any]
    learning_session_count: int
    last_session_date: Optional[datetime] = None

@dataclass
class PersonalizedContent:
    """个性化内容"""
    sentences: List[SentenceResult]
    exercises: List[Exercise]
    difficulty_adjustment: str
    content_reasoning: str
    personalization_factors: List[str]

class ContextAwareGenerator:
    """上下文感知生成器"""
    
    def __init__(self):
        self.ai_client = ai_client
        self.config_manager = config_manager
        self.sentence_gen = sentence_generator
        self.exercise_gen = exercise_generator
        
        # 用户档案存储
        self.profiles_dir = "user_profiles"
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # 学习风格对应的生成策略
        self.learning_style_strategies = {
            "visual": {
                "description": "视觉学习者",
                "sentence_preferences": ["descriptive", "concrete", "image_rich"],
                "exercise_preferences": [ExerciseType.MULTIPLE_CHOICE, ExerciseType.FILL_BLANK],
                "ai_enhancement": 0.7,
                "scenario_bias": ["daily_life", "school", "visual_scenes"]
            },
            "auditory": {
                "description": "听觉学习者", 
                "sentence_preferences": ["rhythmic", "conversational", "dialogue"],
                "exercise_preferences": [ExerciseType.TRANSLATION, ExerciseType.SENTENCE_COMPLETION],
                "ai_enhancement": 0.8,
                "scenario_bias": ["conversation", "music", "storytelling"]
            },
            "kinesthetic": {
                "description": "动觉学习者",
                "sentence_preferences": ["action_oriented", "hands_on", "movement"],
                "exercise_preferences": [ExerciseType.SENTENCE_COMPLETION, ExerciseType.GRAMMAR_CORRECTION],
                "ai_enhancement": 0.9,
                "scenario_bias": ["sports", "activities", "experiments"]
            },
            "balanced": {
                "description": "平衡学习者",
                "sentence_preferences": ["varied", "comprehensive"],
                "exercise_preferences": [ExerciseType.FILL_BLANK, ExerciseType.TRANSLATION, ExerciseType.MULTIPLE_CHOICE],
                "ai_enhancement": 0.6,
                "scenario_bias": ["daily_life", "school", "family"]
            }
        }
        
        # 兴趣主题映射
        self.interest_scenarios = {
            "sports": ["sports", "outdoor_activities"],
            "music": ["entertainment", "arts"],
            "technology": ["technology", "science"],
            "animals": ["nature", "pets"],
            "travel": ["travel", "culture"],
            "food": ["food", "cooking"],
            "reading": ["school", "literature"],
            "games": ["entertainment", "fun_activities"]
        }
    
    def load_user_profile(self, user_id: str) -> UserProfile:
        """加载用户档案"""
        profile_file = os.path.join(self.profiles_dir, f"{user_id}_profile.json")
        
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return UserProfile(**data)
            except Exception as e:
                print(f"加载用户档案失败: {e}")
        
        # 创建默认档案
        return UserProfile(user_id=user_id)
    
    def save_user_profile(self, profile: UserProfile):
        """保存用户档案"""
        profile_file = os.path.join(self.profiles_dir, f"{profile.user_id}_profile.json")
        
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(profile), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户档案失败: {e}")
    
    def analyze_learning_context(self, user_id: str, 
                                fsrs_memory_state: Dict[str, Any] = None) -> LearningContext:
        """分析学习上下文"""
        # 从FSRS状态提取信息
        recent_words = []
        user_performance = {"accuracy": 0.7, "consistency": 0.6}
        
        if fsrs_memory_state:
            # 提取最近学习的单词
            memory_cards = fsrs_memory_state.get("memory_cards", {})
            sorted_cards = sorted(
                memory_cards.items(),
                key=lambda x: x[1].get("last_review", "2024-01-01"),
                reverse=True
            )
            recent_words = [word for word, _ in sorted_cards[:10]]
            
            # 计算用户表现
            total_reviews = sum(card.get("review_count", 0) for card in memory_cards.values())
            avg_difficulty = sum(card.get("difficulty", 5.0) for card in memory_cards.values()) / max(len(memory_cards), 1)
            
            # 根据难度和复习次数评估表现
            if avg_difficulty < 3.0:  # 难度较低但学得好
                user_performance["accuracy"] = 0.8
            elif avg_difficulty > 7.0:  # 难度较高
                user_performance["accuracy"] = 0.5
        
        return LearningContext(
            current_day=1,  # 这里应该从实际系统获取
            recent_words=recent_words,
            recent_grammar_topics=["一般现在时", "名词单复数"],  # 应该从实际数据获取
            user_performance=user_performance,
            fsrs_memory_state=fsrs_memory_state or {},
            learning_session_count=1,
            last_session_date=datetime.now()
        )
    
    def generate_personalized_content(self, word_info: WordInfo, grammar_topic: str,
                                    user_profile: UserProfile, 
                                    learning_context: LearningContext) -> PersonalizedContent:
        """生成个性化学习内容"""
        
        # 分析个性化因素
        personalization_factors = self._analyze_personalization_factors(
            word_info, grammar_topic, user_profile, learning_context
        )
        
        # 调整生成策略
        generation_strategy = self._determine_generation_strategy(
            user_profile, learning_context, personalization_factors
        )
        
        # 生成个性化例句
        sentences = self._generate_personalized_sentences(
            word_info, grammar_topic, generation_strategy, user_profile
        )
        
        # 生成个性化练习题
        exercises = self._generate_personalized_exercises(
            word_info, grammar_topic, generation_strategy, user_profile, learning_context
        )
        
        # 生成内容推理说明
        content_reasoning = self._generate_content_reasoning(
            personalization_factors, generation_strategy, user_profile
        )
        
        return PersonalizedContent(
            sentences=sentences,
            exercises=exercises,
            difficulty_adjustment=generation_strategy["difficulty"],
            content_reasoning=content_reasoning,
            personalization_factors=personalization_factors
        )
    
    def _analyze_personalization_factors(self, word_info: WordInfo, grammar_topic: str,
                                       user_profile: UserProfile, 
                                       learning_context: LearningContext) -> List[str]:
        """分析个性化因素"""
        factors = []
        
        # 学习风格因素
        factors.append(f"学习风格: {user_profile.learning_style}")
        
        # 难度偏好
        if user_profile.difficulty_preference != "medium":
            factors.append(f"难度偏好: {user_profile.difficulty_preference}")
        
        # 兴趣相关性
        word_category = word_info.category.lower()
        for interest in user_profile.interests:
            if interest.lower() in word_category or word_category in interest.lower():
                factors.append(f"兴趣匹配: {interest}")
        
        # 语法主题强弱
        if grammar_topic in user_profile.weak_grammar_topics:
            factors.append(f"薄弱语法: {grammar_topic}")
        elif grammar_topic in user_profile.strong_grammar_topics:
            factors.append(f"强项语法: {grammar_topic}")
        
        # 用户表现
        accuracy = learning_context.user_performance.get("accuracy", 0.5)
        if accuracy < 0.4:
            factors.append("需要加强练习")
        elif accuracy > 0.8:
            factors.append("可以增加难度")
        
        # FSRS记忆状态
        if word_info.word in learning_context.recent_words:
            factors.append("最近学习过")
        
        return factors
    
    def _determine_generation_strategy(self, user_profile: UserProfile,
                                     learning_context: LearningContext,
                                     personalization_factors: List[str]) -> Dict[str, Any]:
        """确定生成策略"""
        strategy = {
            "mode": "balanced",
            "difficulty": "medium",
            "scenario_preference": [],
            "exercise_types": [],
            "ai_enhancement": 0.6,
            "content_style": "standard"
        }
        
        # 基于学习风格调整
        style_config = self.learning_style_strategies.get(user_profile.learning_style, {})
        strategy["ai_enhancement"] = style_config.get("ai_enhancement", 0.6)
        strategy["scenario_preference"] = style_config.get("scenario_bias", ["daily_life"])
        strategy["exercise_types"] = style_config.get("exercise_preferences", [ExerciseType.FILL_BLANK])
        
        # 基于难度偏好调整
        if user_profile.difficulty_preference == "easy":
            strategy["mode"] = "conservative"
            strategy["difficulty"] = "easy"
        elif user_profile.difficulty_preference == "hard":
            strategy["mode"] = "innovative"
            strategy["difficulty"] = "hard"
        
        # 基于用户表现调整
        accuracy = learning_context.user_performance.get("accuracy", 0.5)
        if accuracy < 0.4:
            strategy["mode"] = "conservative"
            strategy["difficulty"] = "easy"
        elif accuracy > 0.8:
            strategy["mode"] = "innovative"
            strategy["difficulty"] = "hard"
        
        # 基于兴趣调整场景偏好
        for interest in user_profile.interests:
            if interest in self.interest_scenarios:
                strategy["scenario_preference"].extend(self.interest_scenarios[interest])
        
        return strategy
    
    def _generate_personalized_sentences(self, word_info: WordInfo, grammar_topic: str,
                                       strategy: Dict[str, Any], 
                                       user_profile: UserProfile) -> List[SentenceResult]:
        """生成个性化例句"""
        sentences = []
        
        # 设置生成模式
        self.config_manager.set_mode(strategy["mode"])
        
        # 根据学习风格选择场景
        scenarios = strategy["scenario_preference"][:3]  # 最多3个场景
        
        for scenario in scenarios:
            try:
                sentence = self.sentence_gen.generate_sentence(
                    word_info, grammar_topic, mode=strategy["mode"], scenario=scenario
                )
                sentences.append(sentence)
            except Exception as e:
                print(f"生成个性化例句失败: {e}")
        
        # 确保至少有一个例句
        if not sentences:
            sentence = self.sentence_gen.generate_sentence(
                word_info, grammar_topic, mode="conservative"
            )
            sentences.append(sentence)
        
        return sentences
    
    def _generate_personalized_exercises(self, word_info: WordInfo, grammar_topic: str,
                                       strategy: Dict[str, Any], user_profile: UserProfile,
                                       learning_context: LearningContext) -> List[Exercise]:
        """生成个性化练习题"""
        exercises = []
        
        # 基于用户偏好选择练习类型
        exercise_types = strategy["exercise_types"]
        if user_profile.preferred_exercise_types:
            # 用户有明确偏好
            preferred_types = [ExerciseType(t) for t in user_profile.preferred_exercise_types 
                             if t in [et.value for et in ExerciseType]]
            if preferred_types:
                exercise_types = preferred_types
        
        # 生成不同类型的练习题
        for exercise_type in exercise_types[:3]:  # 最多3种类型
            try:
                # 使用自适应生成考虑用户表现
                exercise = self.exercise_gen.generate_adaptive_exercise(
                    word_info, grammar_topic, learning_context.user_performance
                )
                exercises.append(exercise)
            except Exception as e:
                print(f"生成个性化练习题失败: {e}")
        
        # 确保至少有一道练习题
        if not exercises:
            exercise = self.exercise_gen.generate_exercise(
                word_info, grammar_topic, ExerciseType.FILL_BLANK, mode="conservative"
            )
            exercises.append(exercise)
        
        return exercises
    
    def _generate_content_reasoning(self, personalization_factors: List[str],
                                  strategy: Dict[str, Any], 
                                  user_profile: UserProfile) -> str:
        """生成内容推理说明"""
        reasoning_parts = []
        
        # 解释个性化选择
        if user_profile.learning_style != "balanced":
            style_desc = self.learning_style_strategies[user_profile.learning_style]["description"]
            reasoning_parts.append(f"根据您的{style_desc}特点")
        
        # 解释难度调整
        if strategy["difficulty"] != "medium":
            reasoning_parts.append(f"调整为{strategy['difficulty']}难度")
        
        # 解释内容选择
        if "兴趣匹配" in str(personalization_factors):
            reasoning_parts.append("结合您的兴趣爱好")
        
        if "薄弱语法" in str(personalization_factors):
            reasoning_parts.append("针对薄弱语法点加强练习")
        
        if "需要加强练习" in personalization_factors:
            reasoning_parts.append("提供基础练习帮助巩固")
        
        if reasoning_parts:
            return "本次内容" + "，".join(reasoning_parts) + "，提供个性化学习体验。"
        else:
            return "基于您的学习档案，为您定制合适的学习内容。"
    
    def update_user_profile_from_feedback(self, user_id: str, 
                                        feedback: Dict[str, Any]):
        """基于反馈更新用户档案"""
        profile = self.load_user_profile(user_id)
        
        # 根据练习结果调整档案
        if "exercise_results" in feedback:
            results = feedback["exercise_results"]
            accuracy = sum(results) / len(results) if results else 0.5
            
            # 调整难度偏好
            if accuracy > 0.9 and profile.difficulty_preference != "hard":
                if profile.difficulty_preference == "easy":
                    profile.difficulty_preference = "medium"
                elif profile.difficulty_preference == "medium":
                    profile.difficulty_preference = "hard"
            elif accuracy < 0.3 and profile.difficulty_preference != "easy":
                if profile.difficulty_preference == "hard":
                    profile.difficulty_preference = "medium"
                elif profile.difficulty_preference == "medium":
                    profile.difficulty_preference = "easy"
        
        # 更新偏好练习类型
        if "preferred_exercises" in feedback:
            profile.preferred_exercise_types = feedback["preferred_exercises"]
        
        # 更新兴趣
        if "interests" in feedback:
            profile.interests = feedback["interests"]
        
        self.save_user_profile(profile)
    
    def generate_learning_recommendation(self, user_id: str, 
                                       learning_context: LearningContext) -> Dict[str, Any]:
        """生成学习建议"""
        profile = self.load_user_profile(user_id)
        
        recommendations = {
            "study_schedule": "建议每天学习15-20分钟",
            "focus_areas": [],
            "suggested_activities": [],
            "difficulty_adjustment": "maintain"
        }
        
        # 基于用户表现给出建议
        accuracy = learning_context.user_performance.get("accuracy", 0.5)
        
        if accuracy < 0.4:
            recommendations["focus_areas"].append("基础语法复习")
            recommendations["suggested_activities"].append("增加填空题练习")
            recommendations["difficulty_adjustment"] = "decrease"
        elif accuracy > 0.8:
            recommendations["focus_areas"].append("挑战性练习")
            recommendations["suggested_activities"].append("尝试语法改错题")
            recommendations["difficulty_adjustment"] = "increase"
        
        # 基于薄弱领域给出建议
        if profile.weak_grammar_topics:
            recommendations["focus_areas"].extend(
                [f"重点练习{topic}" for topic in profile.weak_grammar_topics[:2]]
            )
        
        return recommendations

# 全局实例
context_generator = ContextAwareGenerator()

if __name__ == "__main__":
    # 测试上下文感知生成器
    print("=== 上下文感知生成器测试 ===")
    
    # 创建测试用户档案
    test_profile = UserProfile(
        user_id="test_user",
        learning_style="visual",
        difficulty_preference="medium",
        interests=["sports", "technology"],
        weak_grammar_topics=["一般现在时"],
        preferred_exercise_types=["fill_blank", "multiple_choice"]
    )
    
    # 创建学习上下文
    test_context = LearningContext(
        current_day=5,
        recent_words=["apple", "book", "run"],
        recent_grammar_topics=["一般现在时"],
        user_performance={"accuracy": 0.6, "consistency": 0.7},
        fsrs_memory_state={},
        learning_session_count=5
    )
    
    # 测试单词
    test_word = WordInfo(
        word="computer",
        chinese_meaning="电脑",
        part_of_speech="noun",
        difficulty="medium",
        grade_level="elementary_5_6",
        category="technology"
    )
    
    # 保存测试档案
    context_generator.save_user_profile(test_profile)
    
    # 生成个性化内容
    print("生成个性化内容...")
    personalized_content = context_generator.generate_personalized_content(
        test_word, "一般现在时", test_profile, test_context
    )
    
    print(f"\n个性化因素: {personalized_content.personalization_factors}")
    print(f"内容推理: {personalized_content.content_reasoning}")
    print(f"难度调整: {personalized_content.difficulty_adjustment}")
    
    print(f"\n生成例句 ({len(personalized_content.sentences)}个):")
    for i, sentence in enumerate(personalized_content.sentences, 1):
        print(f"{i}. {sentence.sentence}")
        print(f"   翻译: {sentence.chinese_translation}")
        print(f"   AI生成: {sentence.is_ai_generated}")
    
    print(f"\n生成练习题 ({len(personalized_content.exercises)}个):")
    for i, exercise in enumerate(personalized_content.exercises, 1):
        print(f"{i}. {exercise.question}")
        print(f"   答案: {exercise.answer}")
        print(f"   类型: {exercise.exercise_type.value}")
    
    # 生成学习建议
    print(f"\n学习建议:")
    recommendations = context_generator.generate_learning_recommendation("test_user", test_context)
    for key, value in recommendations.items():
        print(f"{key}: {value}")

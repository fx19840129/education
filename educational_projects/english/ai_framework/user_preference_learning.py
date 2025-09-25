#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户偏好学习系统
分析用户学习模式和偏好，优化AI生成参数
"""

import json
import os
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

class LearningPattern(Enum):
    """学习模式"""
    CONSISTENT = "consistent"       # 一致性学习者
    SPORADIC = "sporadic"          # 间歇性学习者
    INTENSIVE = "intensive"        # 集中式学习者
    CASUAL = "casual"              # 休闲式学习者

class ContentPreference(Enum):
    """内容偏好"""
    SIMPLE = "simple"              # 简单内容
    BALANCED = "balanced"          # 平衡内容
    CHALLENGING = "challenging"    # 挑战性内容
    VARIED = "varied"              # 多样化内容

class ExercisePreference(Enum):
    """练习偏好"""
    REPETITIVE = "repetitive"      # 重复练习
    DIVERSE = "diverse"            # 多样化练习
    CONTEXTUAL = "contextual"      # 情境化练习
    ANALYTICAL = "analytical"      # 分析性练习

@dataclass
class LearningSession:
    """学习会话记录"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    words_studied: List[str]
    exercises_completed: int
    correct_answers: int
    content_ratings: Dict[str, int]  # 内容评分 1-5
    difficulty_feedback: Dict[str, str]  # 难度反馈

@dataclass
class UserBehaviorAnalysis:
    """用户行为分析"""
    learning_pattern: LearningPattern
    content_preference: ContentPreference
    exercise_preference: ExercisePreference
    optimal_session_duration: int
    preferred_difficulty: str
    strong_grammar_topics: List[str]
    weak_grammar_topics: List[str]
    engagement_score: float
    consistency_score: float
    improvement_trend: str  # improving, stable, declining

@dataclass
class PreferenceWeights:
    """偏好权重"""
    ai_enhancement: float
    content_complexity: float
    exercise_variety: float
    personalization: float
    challenge_level: float

class UserPreferenceLearning:
    """用户偏好学习系统"""
    
    def __init__(self):
        # 数据存储
        self.user_sessions: Dict[str, List[LearningSession]] = defaultdict(list)
        self.user_analyses: Dict[str, UserBehaviorAnalysis] = {}
        self.preference_weights: Dict[str, PreferenceWeights] = {}
        
        # 配置
        self.analysis_window_days = 30  # 分析窗口期
        self.min_sessions_for_analysis = 5  # 最少会话数
        self.preference_decay_factor = 0.95  # 偏好衰减因子
        
        # 行为模式识别规则
        self.pattern_rules = {
            LearningPattern.CONSISTENT: {
                "min_sessions_per_week": 4,
                "max_session_gap_days": 2,
                "duration_variance": 0.3
            },
            LearningPattern.INTENSIVE: {
                "min_session_duration": 30,
                "sessions_cluster_ratio": 0.7,
                "max_sessions_per_day": 3
            },
            LearningPattern.SPORADIC: {
                "max_sessions_per_week": 2,
                "min_session_gap_days": 3,
                "duration_variance": 0.6
            },
            LearningPattern.CASUAL: {
                "max_session_duration": 15,
                "min_sessions_per_week": 1,
                "low_intensity": True
            }
        }
        
        # 加载现有数据
        self.load_user_data()
    
    def record_learning_session(self, session: LearningSession):
        """记录学习会话"""
        self.user_sessions[session.user_id].append(session)
        
        # 限制历史记录长度
        max_sessions = 100
        if len(self.user_sessions[session.user_id]) > max_sessions:
            self.user_sessions[session.user_id] = self.user_sessions[session.user_id][-max_sessions:]
        
        # 更新用户分析
        self._update_user_analysis(session.user_id)
        
        # 保存数据
        self.save_user_data()
        
        print(f"记录用户 {session.user_id} 的学习会话: {session.duration_minutes}分钟")
    
    def _update_user_analysis(self, user_id: str):
        """更新用户行为分析"""
        sessions = self.user_sessions[user_id]
        
        if len(sessions) < self.min_sessions_for_analysis:
            return
        
        # 获取最近的会话
        recent_sessions = self._get_recent_sessions(sessions, self.analysis_window_days)
        
        if not recent_sessions:
            return
        
        # 分析学习模式
        learning_pattern = self._analyze_learning_pattern(recent_sessions)
        
        # 分析内容偏好
        content_preference = self._analyze_content_preference(recent_sessions)
        
        # 分析练习偏好
        exercise_preference = self._analyze_exercise_preference(recent_sessions)
        
        # 计算其他指标
        optimal_duration = self._calculate_optimal_duration(recent_sessions)
        preferred_difficulty = self._analyze_difficulty_preference(recent_sessions)
        grammar_analysis = self._analyze_grammar_performance(recent_sessions)
        engagement_score = self._calculate_engagement_score(recent_sessions)
        consistency_score = self._calculate_consistency_score(recent_sessions)
        improvement_trend = self._analyze_improvement_trend(recent_sessions)
        
        # 更新分析结果
        self.user_analyses[user_id] = UserBehaviorAnalysis(
            learning_pattern=learning_pattern,
            content_preference=content_preference,
            exercise_preference=exercise_preference,
            optimal_session_duration=optimal_duration,
            preferred_difficulty=preferred_difficulty,
            strong_grammar_topics=grammar_analysis["strong"],
            weak_grammar_topics=grammar_analysis["weak"],
            engagement_score=engagement_score,
            consistency_score=consistency_score,
            improvement_trend=improvement_trend
        )
        
        # 更新偏好权重
        self._update_preference_weights(user_id)
    
    def _get_recent_sessions(self, sessions: List[LearningSession], days: int) -> List[LearningSession]:
        """获取最近的学习会话"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [s for s in sessions if s.start_time >= cutoff_date]
    
    def _analyze_learning_pattern(self, sessions: List[LearningSession]) -> LearningPattern:
        """分析学习模式"""
        if not sessions:
            return LearningPattern.CASUAL
        
        # 计算学习频率
        total_days = (sessions[-1].start_time - sessions[0].start_time).days + 1
        sessions_per_week = len(sessions) * 7 / max(total_days, 1)
        
        # 计算会话间隔
        intervals = []
        for i in range(1, len(sessions)):
            gap = (sessions[i].start_time - sessions[i-1].start_time).days
            intervals.append(gap)
        
        avg_gap = sum(intervals) / len(intervals) if intervals else 0
        
        # 计算时长方差
        durations = [s.duration_minutes for s in sessions]
        avg_duration = sum(durations) / len(durations)
        duration_variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
        duration_cv = (duration_variance ** 0.5) / avg_duration if avg_duration > 0 else 0
        
        # 判断模式
        if sessions_per_week >= 4 and avg_gap <= 2 and duration_cv <= 0.3:
            return LearningPattern.CONSISTENT
        elif avg_duration >= 30 and sessions_per_week >= 3:
            return LearningPattern.INTENSIVE
        elif sessions_per_week <= 2 or avg_gap >= 3:
            return LearningPattern.SPORADIC
        else:
            return LearningPattern.CASUAL
    
    def _analyze_content_preference(self, sessions: List[LearningSession]) -> ContentPreference:
        """分析内容偏好"""
        if not sessions:
            return ContentPreference.BALANCED
        
        # 分析内容评分
        total_ratings = defaultdict(list)
        for session in sessions:
            for content_type, rating in session.content_ratings.items():
                total_ratings[content_type].append(rating)
        
        # 计算偏好倾向
        simple_score = 0
        complex_score = 0
        variety_score = 0
        
        for content_type, ratings in total_ratings.items():
            avg_rating = sum(ratings) / len(ratings)
            
            if "simple" in content_type.lower() or "basic" in content_type.lower():
                simple_score += avg_rating
            elif "complex" in content_type.lower() or "advanced" in content_type.lower():
                complex_score += avg_rating
            
            variety_score += len(set(ratings))  # 评分多样性
        
        # 判断偏好
        if simple_score > complex_score and simple_score > 3.5:
            return ContentPreference.SIMPLE
        elif complex_score > simple_score and complex_score > 3.5:
            return ContentPreference.CHALLENGING
        elif variety_score > len(total_ratings) * 2:
            return ContentPreference.VARIED
        else:
            return ContentPreference.BALANCED
    
    def _analyze_exercise_preference(self, sessions: List[LearningSession]) -> ExercisePreference:
        """分析练习偏好"""
        if not sessions:
            return ExercisePreference.DIVERSE
        
        # 分析练习完成情况和反馈
        exercise_variety = set()
        context_feedback = 0
        repetition_tolerance = 0
        analytical_preference = 0
        
        for session in sessions:
            # 练习多样性
            if hasattr(session, 'exercise_types'):
                exercise_variety.update(session.exercise_types)
            
            # 基于反馈分析偏好
            for feedback_type, feedback in session.difficulty_feedback.items():
                if "context" in feedback.lower() or "situation" in feedback.lower():
                    context_feedback += 1
                elif "repeat" in feedback.lower() or "again" in feedback.lower():
                    repetition_tolerance += 1
                elif "analysis" in feedback.lower() or "explain" in feedback.lower():
                    analytical_preference += 1
        
        # 判断偏好
        total_feedback = len(sessions)
        if context_feedback / total_feedback > 0.3:
            return ExercisePreference.CONTEXTUAL
        elif analytical_preference / total_feedback > 0.3:
            return ExercisePreference.ANALYTICAL
        elif repetition_tolerance / total_feedback > 0.4:
            return ExercisePreference.REPETITIVE
        else:
            return ExercisePreference.DIVERSE
    
    def _calculate_optimal_duration(self, sessions: List[LearningSession]) -> int:
        """计算最佳学习时长"""
        if not sessions:
            return 15
        
        # 分析时长与表现的关系
        duration_performance = []
        for session in sessions:
            if session.exercises_completed > 0:
                accuracy = session.correct_answers / session.exercises_completed
                duration_performance.append((session.duration_minutes, accuracy))
        
        if not duration_performance:
            # 使用平均时长
            durations = [s.duration_minutes for s in sessions]
            return int(sum(durations) / len(durations))
        
        # 找到表现最好的时长范围
        best_duration = 15
        best_performance = 0
        
        for duration_range in [10, 15, 20, 25, 30, 40, 50]:
            performances = []
            for duration, performance in duration_performance:
                if abs(duration - duration_range) <= 5:
                    performances.append(performance)
            
            if performances:
                avg_performance = sum(performances) / len(performances)
                if avg_performance > best_performance:
                    best_performance = avg_performance
                    best_duration = duration_range
        
        return best_duration
    
    def _analyze_difficulty_preference(self, sessions: List[LearningSession]) -> str:
        """分析难度偏好"""
        if not sessions:
            return "medium"
        
        difficulty_feedback = defaultdict(int)
        for session in sessions:
            for feedback in session.difficulty_feedback.values():
                if "easy" in feedback.lower():
                    difficulty_feedback["easy"] += 1
                elif "hard" in feedback.lower() or "difficult" in feedback.lower():
                    difficulty_feedback["hard"] += 1
                elif "medium" in feedback.lower() or "moderate" in feedback.lower():
                    difficulty_feedback["medium"] += 1
        
        if not difficulty_feedback:
            return "medium"
        
        return max(difficulty_feedback.items(), key=lambda x: x[1])[0]
    
    def _analyze_grammar_performance(self, sessions: List[LearningSession]) -> Dict[str, List[str]]:
        """分析语法主题表现"""
        topic_performance = defaultdict(list)
        
        for session in sessions:
            if hasattr(session, 'grammar_performance'):
                for topic, accuracy in session.grammar_performance.items():
                    topic_performance[topic].append(accuracy)
        
        strong_topics = []
        weak_topics = []
        
        for topic, accuracies in topic_performance.items():
            avg_accuracy = sum(accuracies) / len(accuracies)
            if avg_accuracy > 0.8:
                strong_topics.append(topic)
            elif avg_accuracy < 0.6:
                weak_topics.append(topic)
        
        return {"strong": strong_topics, "weak": weak_topics}
    
    def _calculate_engagement_score(self, sessions: List[LearningSession]) -> float:
        """计算参与度评分"""
        if not sessions:
            return 0.5
        
        # 考虑多个因素
        factors = []
        
        # 会话完成率
        completed_sessions = sum(1 for s in sessions if s.duration_minutes >= 5)
        completion_rate = completed_sessions / len(sessions)
        factors.append(completion_rate)
        
        # 平均会话时长
        avg_duration = sum(s.duration_minutes for s in sessions) / len(sessions)
        duration_score = min(avg_duration / 30, 1.0)  # 30分钟为满分
        factors.append(duration_score)
        
        # 练习完成情况
        if sessions:
            avg_exercises = sum(s.exercises_completed for s in sessions) / len(sessions)
            exercise_score = min(avg_exercises / 10, 1.0)  # 10个练习为满分
            factors.append(exercise_score)
        
        # 内容评分
        all_ratings = []
        for session in sessions:
            all_ratings.extend(session.content_ratings.values())
        
        if all_ratings:
            avg_rating = sum(all_ratings) / len(all_ratings)
            rating_score = (avg_rating - 1) / 4  # 1-5分转换为0-1
            factors.append(rating_score)
        
        return sum(factors) / len(factors) if factors else 0.5
    
    def _calculate_consistency_score(self, sessions: List[LearningSession]) -> float:
        """计算一致性评分"""
        if len(sessions) < 2:
            return 0.5
        
        # 计算时间间隔的一致性
        intervals = []
        for i in range(1, len(sessions)):
            gap = (sessions[i].start_time - sessions[i-1].start_time).total_seconds() / 3600  # 小时
            intervals.append(gap)
        
        if not intervals:
            return 0.5
        
        # 计算间隔的变异系数
        avg_interval = sum(intervals) / len(intervals)
        if avg_interval == 0:
            return 1.0
        
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        cv = (variance ** 0.5) / avg_interval
        
        # 转换为0-1分数（变异系数越小，一致性越高）
        consistency = max(0, 1 - cv)
        return min(consistency, 1.0)
    
    def _analyze_improvement_trend(self, sessions: List[LearningSession]) -> str:
        """分析改进趋势"""
        if len(sessions) < 3:
            return "stable"
        
        # 计算准确率趋势
        accuracies = []
        for session in sessions:
            if session.exercises_completed > 0:
                accuracy = session.correct_answers / session.exercises_completed
                accuracies.append(accuracy)
        
        if len(accuracies) < 3:
            return "stable"
        
        # 简单线性趋势分析
        n = len(accuracies)
        x_avg = (n - 1) / 2
        y_avg = sum(accuracies) / n
        
        slope_num = sum((i - x_avg) * (accuracies[i] - y_avg) for i in range(n))
        slope_den = sum((i - x_avg) ** 2 for i in range(n))
        
        if slope_den == 0:
            return "stable"
        
        slope = slope_num / slope_den
        
        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _update_preference_weights(self, user_id: str):
        """更新偏好权重"""
        if user_id not in self.user_analyses:
            return
        
        analysis = self.user_analyses[user_id]
        
        # 基于分析结果计算权重
        weights = PreferenceWeights(
            ai_enhancement=self._calculate_ai_weight(analysis),
            content_complexity=self._calculate_complexity_weight(analysis),
            exercise_variety=self._calculate_variety_weight(analysis),
            personalization=self._calculate_personalization_weight(analysis),
            challenge_level=self._calculate_challenge_weight(analysis)
        )
        
        self.preference_weights[user_id] = weights
    
    def _calculate_ai_weight(self, analysis: UserBehaviorAnalysis) -> float:
        """计算AI增强权重"""
        base_weight = 0.6
        
        # 根据内容偏好调整
        if analysis.content_preference == ContentPreference.CHALLENGING:
            base_weight += 0.2
        elif analysis.content_preference == ContentPreference.SIMPLE:
            base_weight -= 0.2
        
        # 根据参与度调整
        base_weight += (analysis.engagement_score - 0.5) * 0.4
        
        return max(0.1, min(1.0, base_weight))
    
    def _calculate_complexity_weight(self, analysis: UserBehaviorAnalysis) -> float:
        """计算复杂度权重"""
        if analysis.content_preference == ContentPreference.SIMPLE:
            return 0.3
        elif analysis.content_preference == ContentPreference.CHALLENGING:
            return 0.9
        elif analysis.content_preference == ContentPreference.VARIED:
            return 0.7
        else:
            return 0.5
    
    def _calculate_variety_weight(self, analysis: UserBehaviorAnalysis) -> float:
        """计算多样性权重"""
        if analysis.exercise_preference == ExercisePreference.DIVERSE:
            return 0.9
        elif analysis.exercise_preference == ExercisePreference.REPETITIVE:
            return 0.3
        else:
            return 0.6
    
    def _calculate_personalization_weight(self, analysis: UserBehaviorAnalysis) -> float:
        """计算个性化权重"""
        base_weight = 0.5
        
        # 根据学习模式调整
        if analysis.learning_pattern == LearningPattern.CONSISTENT:
            base_weight += 0.3
        elif analysis.learning_pattern == LearningPattern.SPORADIC:
            base_weight += 0.4  # 间歇性学习者需要更多个性化
        
        # 根据改进趋势调整
        if analysis.improvement_trend == "declining":
            base_weight += 0.2
        
        return max(0.2, min(1.0, base_weight))
    
    def _calculate_challenge_weight(self, analysis: UserBehaviorAnalysis) -> float:
        """计算挑战权重"""
        if analysis.preferred_difficulty == "easy":
            return 0.3
        elif analysis.preferred_difficulty == "hard":
            return 0.9
        else:
            return 0.6
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        if user_id not in self.user_analyses:
            return self._get_default_preferences()
        
        analysis = self.user_analyses[user_id]
        weights = self.preference_weights.get(user_id, self._get_default_weights())
        
        return {
            "analysis": asdict(analysis),
            "weights": asdict(weights),
            "recommendations": self._generate_recommendations(analysis),
            "adaptation_suggestions": self._generate_adaptation_suggestions(analysis)
        }
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """获取默认偏好"""
        return {
            "analysis": {
                "learning_pattern": "casual",
                "content_preference": "balanced", 
                "exercise_preference": "diverse",
                "optimal_session_duration": 15,
                "preferred_difficulty": "medium"
            },
            "weights": asdict(self._get_default_weights()),
            "recommendations": ["建议保持规律学习", "尝试不同类型的练习"],
            "adaptation_suggestions": ["系统将根据您的学习表现逐步优化"]
        }
    
    def _get_default_weights(self) -> PreferenceWeights:
        """获取默认权重"""
        return PreferenceWeights(
            ai_enhancement=0.6,
            content_complexity=0.5,
            exercise_variety=0.6,
            personalization=0.5,
            challenge_level=0.5
        )
    
    def _generate_recommendations(self, analysis: UserBehaviorAnalysis) -> List[str]:
        """生成学习建议"""
        recommendations = []
        
        # 基于学习模式的建议
        if analysis.learning_pattern == LearningPattern.SPORADIC:
            recommendations.append("建议制定固定的学习时间表，提高学习一致性")
        elif analysis.learning_pattern == LearningPattern.INTENSIVE:
            recommendations.append("注意劳逸结合，避免学习疲劳")
        
        # 基于表现趋势的建议
        if analysis.improvement_trend == "declining":
            recommendations.append("建议降低学习难度，重点巩固基础知识")
        elif analysis.improvement_trend == "improving":
            recommendations.append("学习进步明显，可以尝试更有挑战性的内容")
        
        # 基于参与度的建议
        if analysis.engagement_score < 0.5:
            recommendations.append("尝试更多样化的学习内容，提高学习兴趣")
        
        return recommendations
    
    def _generate_adaptation_suggestions(self, analysis: UserBehaviorAnalysis) -> List[str]:
        """生成适配建议"""
        suggestions = []
        
        if analysis.content_preference == ContentPreference.CHALLENGING:
            suggestions.append("系统将提供更复杂的例句和练习题")
        elif analysis.content_preference == ContentPreference.SIMPLE:
            suggestions.append("系统将优先提供简单易懂的学习内容")
        
        if analysis.exercise_preference == ExercisePreference.CONTEXTUAL:
            suggestions.append("练习题将更注重实际应用场景")
        
        return suggestions
    
    def save_user_data(self, file_path: str = "user_preference_data.json"):
        """保存用户数据"""
        try:
            data = {
                "sessions": {},
                "analyses": {},
                "weights": {}
            }
            
            # 序列化会话数据
            for user_id, sessions in self.user_sessions.items():
                data["sessions"][user_id] = []
                for session in sessions:
                    session_dict = asdict(session)
                    session_dict["start_time"] = session.start_time.isoformat()
                    session_dict["end_time"] = session.end_time.isoformat()
                    data["sessions"][user_id].append(session_dict)
            
            # 序列化分析数据
            for user_id, analysis in self.user_analyses.items():
                data["analyses"][user_id] = asdict(analysis)
                # 转换枚举为字符串
                data["analyses"][user_id]["learning_pattern"] = analysis.learning_pattern.value
                data["analyses"][user_id]["content_preference"] = analysis.content_preference.value
                data["analyses"][user_id]["exercise_preference"] = analysis.exercise_preference.value
            
            # 序列化权重数据
            for user_id, weights in self.preference_weights.items():
                data["weights"][user_id] = asdict(weights)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存用户数据失败: {e}")
    
    def load_user_data(self, file_path: str = "user_preference_data.json"):
        """加载用户数据"""
        try:
            if not os.path.exists(file_path):
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载会话数据
            for user_id, sessions_data in data.get("sessions", {}).items():
                sessions = []
                for session_dict in sessions_data:
                    session_dict["start_time"] = datetime.fromisoformat(session_dict["start_time"])
                    session_dict["end_time"] = datetime.fromisoformat(session_dict["end_time"])
                    sessions.append(LearningSession(**session_dict))
                self.user_sessions[user_id] = sessions
            
            # 加载分析数据
            for user_id, analysis_data in data.get("analyses", {}).items():
                analysis_data["learning_pattern"] = LearningPattern(analysis_data["learning_pattern"])
                analysis_data["content_preference"] = ContentPreference(analysis_data["content_preference"])
                analysis_data["exercise_preference"] = ExercisePreference(analysis_data["exercise_preference"])
                self.user_analyses[user_id] = UserBehaviorAnalysis(**analysis_data)
            
            # 加载权重数据
            for user_id, weights_data in data.get("weights", {}).items():
                self.preference_weights[user_id] = PreferenceWeights(**weights_data)
            
            print(f"加载了 {len(self.user_sessions)} 个用户的偏好数据")
            
        except Exception as e:
            print(f"加载用户数据失败: {e}")

# 全局用户偏好学习系统实例
preference_learning = UserPreferenceLearning()

if __name__ == "__main__":
    # 测试用户偏好学习系统
    print("=== 用户偏好学习系统测试 ===")
    
    # 创建测试学习会话
    test_sessions = [
        LearningSession(
            session_id="session_1",
            user_id="test_user",
            start_time=datetime.now() - timedelta(days=7),
            end_time=datetime.now() - timedelta(days=7) + timedelta(minutes=20),
            duration_minutes=20,
            words_studied=["apple", "book", "cat"],
            exercises_completed=8,
            correct_answers=6,
            content_ratings={"simple_sentence": 4, "exercise": 3},
            difficulty_feedback={"session": "good difficulty"}
        ),
        LearningSession(
            session_id="session_2", 
            user_id="test_user",
            start_time=datetime.now() - timedelta(days=5),
            end_time=datetime.now() - timedelta(days=5) + timedelta(minutes=25),
            duration_minutes=25,
            words_studied=["dog", "house", "tree"],
            exercises_completed=10,
            correct_answers=8,
            content_ratings={"complex_sentence": 5, "exercise": 4},
            difficulty_feedback={"session": "challenging but good"}
        ),
        LearningSession(
            session_id="session_3",
            user_id="test_user", 
            start_time=datetime.now() - timedelta(days=3),
            end_time=datetime.now() - timedelta(days=3) + timedelta(minutes=18),
            duration_minutes=18,
            words_studied=["car", "water", "sun"],
            exercises_completed=7,
            correct_answers=7,
            content_ratings={"varied_content": 5, "exercise": 5},
            difficulty_feedback={"session": "perfect difficulty"}
        )
    ]
    
    # 记录学习会话
    print("\n--- 记录学习会话 ---")
    for session in test_sessions:
        preference_learning.record_learning_session(session)
    
    # 获取用户偏好
    print("\n--- 用户偏好分析 ---")
    preferences = preference_learning.get_user_preferences("test_user")
    
    print("学习模式分析:")
    analysis = preferences["analysis"]
    print(f"  学习模式: {analysis.get('learning_pattern', 'unknown')}")
    print(f"  内容偏好: {analysis.get('content_preference', 'unknown')}")
    print(f"  练习偏好: {analysis.get('exercise_preference', 'unknown')}")
    print(f"  最佳时长: {analysis.get('optimal_session_duration', 15)}分钟")
    print(f"  偏好难度: {analysis.get('preferred_difficulty', 'medium')}")
    print(f"  参与度评分: {analysis.get('engagement_score', 0.5):.2f}")
    print(f"  一致性评分: {analysis.get('consistency_score', 0.5):.2f}")
    print(f"  改进趋势: {analysis.get('improvement_trend', 'stable')}")
    
    print("\n偏好权重:")
    weights = preferences["weights"]
    for key, value in weights.items():
        print(f"  {key}: {value:.2f}")
    
    print("\n学习建议:")
    for rec in preferences["recommendations"]:
        print(f"  • {rec}")
    
    print("\n适配建议:")
    for suggestion in preferences["adaptation_suggestions"]:
        print(f"  • {suggestion}")
    
    # 保存数据
    preference_learning.save_user_data("test_user_preferences.json")
    print("\n用户偏好数据已保存")
    
    print("\n用户偏好学习系统测试完成！")

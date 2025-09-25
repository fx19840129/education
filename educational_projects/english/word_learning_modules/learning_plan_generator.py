#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词学习计划生成器
生成个性化的单词学习计划
"""

import random
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from word_database import WordInfo


@dataclass
class LearningPlan:
    """学习计划数据类"""
    title: str
    description: str
    duration: int  # 天数
    daily_words: int  # 每天学习单词数
    total_words: int  # 总单词数
    difficulty: str
    level: str
    categories: List[str]
    learning_objectives: List[str]
    study_schedule: List[Dict[str, Any]]
    assessment_criteria: Dict[str, str]


class WordLearningPlanGenerator:
    """单词学习计划生成器"""
    
    def __init__(self, word_database):
        self.word_database = word_database
        self.learning_methods = [
            "词汇卡片法",
            "联想记忆法",
            "语境学习法",
            "词根词缀法",
            "重复记忆法",
            "分类记忆法",
            "故事记忆法",
            "图像记忆法"
        ]
    
    def generate_learning_plan(self, level: str, difficulty: str = None, 
                             duration: int = 30, daily_words: int = 10,
                             categories: List[str] = None) -> LearningPlan:
        """生成学习计划"""
        # 获取单词
        if difficulty:
            words = list(self.word_database.get_words_by_difficulty(level, difficulty).values())
        else:
            words = list(self.word_database.get_words_by_level(level).values())
        
        if categories:
            words = [w for w in words if w.category in categories]
        
        # 计算总单词数
        total_words = min(len(words), duration * daily_words)
        selected_words = random.sample(words, total_words)
        
        # 生成学习目标
        learning_objectives = self._generate_learning_objectives(level, difficulty, total_words)
        
        # 生成学习计划
        study_schedule = self._generate_study_schedule(selected_words, duration, daily_words)
        
        # 生成评估标准
        assessment_criteria = self._generate_assessment_criteria(level, difficulty)
        
        # 生成计划标题和描述
        title = self._generate_plan_title(level, difficulty, duration)
        description = self._generate_plan_description(level, difficulty, total_words, duration)
        
        return LearningPlan(
            title=title,
            description=description,
            duration=duration,
            daily_words=daily_words,
            total_words=total_words,
            difficulty=difficulty or "mixed",
            level=level,
            categories=categories or [],
            learning_objectives=learning_objectives,
            study_schedule=study_schedule,
            assessment_criteria=assessment_criteria
        )
    
    def _generate_learning_objectives(self, level: str, difficulty: str, total_words: int) -> List[str]:
        """生成学习目标"""
        objectives = []
        
        if level == "elementary":
            objectives.extend([
                f"掌握{total_words}个小学英语单词",
                "能够正确拼写和发音",
                "理解单词的基本含义",
                "能够在简单句子中使用单词",
                "建立英语学习兴趣"
            ])
        else:
            objectives.extend([
                f"掌握{total_words}个初中英语单词",
                "能够正确拼写、发音和使用",
                "理解单词的深层含义和用法",
                "能够在复杂句子中正确使用单词",
                "提高英语词汇量和表达能力"
            ])
        
        if difficulty == "easy":
            objectives.append("重点掌握基础词汇")
        elif difficulty == "medium":
            objectives.append("掌握中等难度词汇")
        elif difficulty == "hard":
            objectives.append("挑战高难度词汇")
        
        return objectives
    
    def _generate_study_schedule(self, words: List[WordInfo], duration: int, daily_words: int) -> List[Dict[str, Any]]:
        """生成学习计划表"""
        schedule = []
        
        for day in range(1, duration + 1):
            start_idx = (day - 1) * daily_words
            end_idx = min(start_idx + daily_words, len(words))
            day_words = words[start_idx:end_idx]
            
            if not day_words:
                break
            
            # 选择学习方法
            learning_method = random.choice(self.learning_methods)
            
            # 生成每日学习内容
            daily_content = {
                "day": day,
                "words": [{"word": w.word, "meaning": w.chinese_meaning, "pronunciation": w.pronunciation} for w in day_words],
                "learning_method": learning_method,
                "focus_skills": self._get_focus_skills(day_words),
                "practice_activities": self._get_practice_activities(day_words),
                "review_words": self._get_review_words(words, day, daily_words)
            }
            
            schedule.append(daily_content)
        
        return schedule
    
    def _get_focus_skills(self, words: List[WordInfo]) -> List[str]:
        """获取重点技能"""
        skills = []
        
        # 根据单词类型确定重点技能
        word_types = set(w.part_of_speech for w in words)
        
        if "noun" in word_types:
            skills.append("名词单复数变化")
        if "verb" in word_types:
            skills.append("动词时态变化")
        if "adjective" in word_types:
            skills.append("形容词比较级和最高级")
        
        # 添加通用技能
        skills.extend(["拼写", "发音", "词义理解"])
        
        return skills[:3]  # 限制在3个技能内
    
    def _get_practice_activities(self, words: List[WordInfo]) -> List[str]:
        """获取练习活动"""
        activities = [
            "单词卡片练习",
            "拼写练习",
            "发音练习",
            "造句练习",
            "翻译练习",
            "填空练习",
            "选择题练习",
            "匹配练习"
        ]
        
        return random.sample(activities, min(4, len(activities)))
    
    def _get_review_words(self, all_words: List[WordInfo], current_day: int, daily_words: int) -> List[str]:
        """获取复习单词"""
        if current_day <= 3:
            return []
        
        # 复习前几天的单词
        review_days = min(3, current_day - 1)
        review_words = []
        
        for day in range(max(1, current_day - review_days), current_day):
            start_idx = (day - 1) * daily_words
            end_idx = min(start_idx + daily_words, len(all_words))
            day_words = all_words[start_idx:end_idx]
            review_words.extend([w.word for w in day_words])
        
        # 随机选择一些单词进行复习
        return random.sample(review_words, min(5, len(review_words)))
    
    def _generate_assessment_criteria(self, level: str, difficulty: str) -> Dict[str, str]:
        """生成评估标准"""
        if level == "elementary":
            return {
                "excellent": "能够正确拼写、发音和使用90%以上的单词",
                "good": "能够正确拼写、发音和使用80-89%的单词",
                "satisfactory": "能够正确拼写、发音和使用70-79%的单词",
                "needs_improvement": "能够正确拼写、发音和使用70%以下的单词"
            }
        else:
            return {
                "excellent": "能够正确拼写、发音、理解和使用90%以上的单词",
                "good": "能够正确拼写、发音、理解和使用80-89%的单词",
                "satisfactory": "能够正确拼写、发音、理解和使用70-79%的单词",
                "needs_improvement": "能够正确拼写、发音、理解和使用70%以下的单词"
            }
    
    def _generate_plan_title(self, level: str, difficulty: str, duration: int) -> str:
        """生成计划标题"""
        level_name = "小学" if level == "elementary" else "初中"
        difficulty_name = {
            "easy": "基础",
            "medium": "进阶",
            "hard": "高级"
        }.get(difficulty, "综合")
        
        return f"{level_name}英语单词{difficulty_name}学习计划（{duration}天）"
    
    def _generate_plan_description(self, level: str, difficulty: str, total_words: int, duration: int) -> str:
        """生成计划描述"""
        level_name = "小学" if level == "elementary" else "初中"
        difficulty_name = {
            "easy": "基础",
            "medium": "进阶",
            "hard": "高级"
        }.get(difficulty, "综合")
        
        return f"这是一个为期{duration}天的{level_name}英语单词{difficulty_name}学习计划，共包含{total_words}个单词。通过系统性的学习和练习，帮助学生掌握英语单词的拼写、发音、含义和用法，提高英语词汇量和语言表达能力。"
    
    def generate_category_plan(self, level: str, category: str, duration: int = 14) -> LearningPlan:
        """生成分类学习计划"""
        words = list(self.word_database.get_words_by_category(level, category).values())
        
        if not words:
            return None
        
        # 根据单词数量调整学习计划
        total_words = len(words)
        daily_words = max(5, min(15, total_words // duration))
        actual_duration = max(duration, total_words // daily_words)
        
        return self.generate_learning_plan(
            level=level,
            difficulty=None,
            duration=actual_duration,
            daily_words=daily_words,
            categories=[category]
        )
    
    def generate_difficulty_plan(self, level: str, difficulty: str, duration: int = 21) -> LearningPlan:
        """生成难度学习计划"""
        return self.generate_learning_plan(
            level=level,
            difficulty=difficulty,
            duration=duration,
            daily_words=10
        )
    
    def generate_comprehensive_plan(self, level: str, duration: int = 30) -> LearningPlan:
        """生成综合学习计划"""
        return self.generate_learning_plan(
            level=level,
            difficulty=None,
            duration=duration,
            daily_words=15
        )

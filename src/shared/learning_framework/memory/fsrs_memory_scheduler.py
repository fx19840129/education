#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于FSRS算法的记忆调度器
FSRS (Free Spaced Repetition Scheduler) - 最新的间隔重复算法
"""

import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import json
import os

@dataclass
class MemoryCard:
    """记忆卡片 - 基于FSRS的单词学习状态"""
    word: str
    stability: float = 1.0  # 稳定性 (S) - 记忆保持时间
    difficulty: float = 5.0  # 难度 (D) - 学习难度 (1-10)
    last_review: Optional[datetime] = None
    review_count: int = 0
    grade_history: List[int] = None  # 评分历史 [1-4]
    interval: float = 1.0  # 复习间隔（天）
    
    def __post_init__(self):
        if self.grade_history is None:
            self.grade_history = []
        if self.last_review is None:
            self.last_review = datetime.now()

@dataclass 
class FSRSParameters:
    """FSRS算法参数 - 基于最新研究优化"""
    # 21个FSRS核心参数
    w: List[float] = None
    
    def __post_init__(self):
        if self.w is None:
            # FSRS-6默认参数（经过大量数据训练）
            self.w = [
                0.2172, 1.1771, 3.2602, 16.1507, 7.0114, 0.57, 2.0966,
                0.0069, 1.5261, 0.112, 1.0178, 1.849, 0.1133, 0.3127,
                2.2934, 0.2191, 3.0004, 0.7536, 0.3332, 0.1437, 0.2
            ]

class FSRSMemoryScheduler:
    """基于FSRS算法的记忆调度器"""
    
    def __init__(self, desired_retention: float = 0.9):
        """
        初始化FSRS调度器
        
        Args:
            desired_retention: 期望保持率 (0.8-0.95)
        """
        self.params = FSRSParameters()
        self.desired_retention = desired_retention
        self.memory_cards: Dict[str, MemoryCard] = {}
        
    def calculate_retrievability(self, card: MemoryCard, elapsed_days: float) -> float:
        """
        计算可提取性 (Retrievability) - 当前能回忆起来的概率
        
        基于FSRS公式: R = (1 + FACTOR * t / S) ^ DECAY
        """
        if elapsed_days <= 0:
            return 1.0
            
        factor = 19 / 81  # FSRS-6优化因子
        decay = -0.5      # 遗忘曲线衰减指数
        
        retrievability = (1 + factor * elapsed_days / card.stability) ** decay
        return max(0.01, min(1.0, retrievability))
    
    def update_stability(self, card: MemoryCard, grade: int) -> float:
        """
        更新稳定性 (Stability) - 记忆保持时间
        
        Args:
            card: 记忆卡片
            grade: 评分 (1=Again, 2=Hard, 3=Good, 4=Easy)
        """
        w = self.params.w
        
        if card.review_count == 0:
            # 初次学习稳定性
            if grade == 1:  # Again
                return w[0]
            elif grade == 2:  # Hard  
                return w[1]
            elif grade == 3:  # Good
                return w[2]
            else:  # Easy
                return w[3]
        else:
            # 后续复习稳定性更新
            elapsed_days = (datetime.now() - card.last_review).days
            retrievability = self.calculate_retrievability(card, elapsed_days)
            
            # FSRS-6稳定性增长公式
            if grade == 1:  # Again - 遗忘
                new_stability = w[11] * card.difficulty ** (-w[12]) * \
                               ((card.stability + 1) ** w[13] - 1) * \
                               math.exp(w[14] * (1 - retrievability))
            else:  # 记住了
                hard_penalty = 1 if grade == 2 else 0
                easy_bonus = 1 if grade == 4 else 0
                
                new_stability = card.stability * (
                    math.exp(w[8]) * 
                    (11 - card.difficulty) *
                    card.stability ** (-w[9]) *
                    (math.exp(w[10] * (1 - retrievability)) - 1) *
                    hard_penalty * w[15] + 1 +
                    easy_bonus * w[16]
                )
            
            return max(0.01, new_stability)
    
    def update_difficulty(self, card: MemoryCard, grade: int) -> float:
        """
        更新难度 (Difficulty) - 单词学习难度
        
        Args:
            card: 记忆卡片  
            grade: 评分 (1=Again, 2=Hard, 3=Good, 4=Easy)
        """
        w = self.params.w
        
        if card.review_count == 0:
            # 初始难度基于首次评分
            return max(1.0, min(10.0, w[4] - w[5] * (grade - 3)))
        else:
            # 难度更新：基于遗忘/记住调整
            if grade == 1:  # Again - 增加难度
                delta_d = -w[6] * (grade - 3)
            else:  # 其他 - 略微降低难度
                delta_d = -w[6] * (grade - 3)
            
            # 应用线性阻尼和均值回归
            mean_reversion = w[7]
            default_difficulty = w[4]
            
            new_difficulty = card.difficulty + delta_d
            new_difficulty = new_difficulty * (1 - mean_reversion) + \
                           default_difficulty * mean_reversion
            
            return max(1.0, min(10.0, new_difficulty))
    
    def calculate_interval(self, card: MemoryCard) -> float:
        """
        计算下次复习间隔
        
        基于FSRS公式: I = S * ln(desired_retention) / ln(0.9)
        """
        if self.desired_retention >= 0.99:
            return card.stability
            
        interval = card.stability * math.log(self.desired_retention) / math.log(0.9)
        
        # 应用模糊化避免复习堆积
        fuzz_range = max(1, interval * 0.05)  # 5%模糊范围
        fuzzed_interval = interval + random.uniform(-fuzz_range, fuzz_range)
        
        return max(0.1, fuzzed_interval)
    
    def review_word(self, word: str, grade: int) -> MemoryCard:
        """
        复习单词并更新记忆状态
        
        Args:
            word: 单词
            grade: 评分 (1=Again, 2=Hard, 3=Good, 4=Easy)
        """
        if word not in self.memory_cards:
            self.memory_cards[word] = MemoryCard(word=word)
        
        card = self.memory_cards[word]
        
        # 更新稳定性和难度
        card.stability = self.update_stability(card, grade)
        card.difficulty = self.update_difficulty(card, grade)
        
        # 计算下次复习间隔
        card.interval = self.calculate_interval(card)
        
        # 更新复习记录
        card.last_review = datetime.now()
        card.review_count += 1
        card.grade_history.append(grade)
        
        return card
    
    def get_due_words(self, words: List[str], target_count: int = 8) -> List[str]:
        """
        获取到期需要复习的单词
        
        Args:
            words: 候选单词列表
            target_count: 目标单词数量
        """
        due_words = []
        new_words = []
        
        for word in words:
            if word not in self.memory_cards:
                new_words.append(word)
            else:
                card = self.memory_cards[word]
                elapsed = (datetime.now() - card.last_review).days
                retrievability = self.calculate_retrievability(card, elapsed)
                
                # 可提取性低于期望保持率时需要复习
                if retrievability < self.desired_retention:
                    due_words.append((word, retrievability))
        
        # 按可提取性排序，优先复习最容易忘记的
        due_words.sort(key=lambda x: x[1])
        
        # 组合新单词和复习单词
        result = []
        review_count = min(len(due_words), int(target_count * 0.4))  # 40%复习
        new_count = target_count - review_count
        
        # 添加最需要复习的单词
        result.extend([word for word, _ in due_words[:review_count]])
        
        # 添加新单词
        result.extend(new_words[:new_count])
        
        # 如果不够，补充剩余的复习单词
        if len(result) < target_count:
            remaining = target_count - len(result)
            result.extend([word for word, _ in due_words[review_count:review_count + remaining]])
        
        return result[:target_count]
    
    def get_learning_statistics(self) -> Dict:
        """获取学习统计信息"""
        if not self.memory_cards:
            return {"total_words": 0, "average_stability": 0, "average_difficulty": 0}
        
        total_words = len(self.memory_cards)
        avg_stability = sum(card.stability for card in self.memory_cards.values()) / total_words
        avg_difficulty = sum(card.difficulty for card in self.memory_cards.values()) / total_words
        
        # 按难度分组统计
        difficulty_distribution = {"easy": 0, "medium": 0, "hard": 0}
        for card in self.memory_cards.values():
            if card.difficulty <= 3.5:
                difficulty_distribution["easy"] += 1
            elif card.difficulty <= 6.5:
                difficulty_distribution["medium"] += 1
            else:
                difficulty_distribution["hard"] += 1
        
        return {
            "total_words": total_words,
            "average_stability": round(avg_stability, 2),
            "average_difficulty": round(avg_difficulty, 2),
            "difficulty_distribution": difficulty_distribution,
            "retention_rate": self.desired_retention
        }
    
    def save_memory_state(self, filepath: str):
        """保存记忆状态到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 转换为可序列化格式
        data = {
            "desired_retention": self.desired_retention,
            "parameters": asdict(self.params),
            "memory_cards": {}
        }
        
        for word, card in self.memory_cards.items():
            card_data = asdict(card)
            # 转换datetime为字符串
            if card_data["last_review"]:
                card_data["last_review"] = card_data["last_review"].isoformat()
            data["memory_cards"][word] = card_data
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_memory_state(self, filepath: str):
        """从文件加载记忆状态"""
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.desired_retention = data.get("desired_retention", 0.9)
            
            # 加载参数
            if "parameters" in data:
                self.params = FSRSParameters(**data["parameters"])
            
            # 加载记忆卡片
            self.memory_cards = {}
            for word, card_data in data.get("memory_cards", {}).items():
                # 转换字符串回datetime
                if card_data["last_review"]:
                    card_data["last_review"] = datetime.fromisoformat(card_data["last_review"])
                
                self.memory_cards[word] = MemoryCard(**card_data)
                
        except Exception as e:
            print(f"加载记忆状态失败: {e}")
            # 重置为默认状态
            self.__init__(self.desired_retention)

    def simulate_learning_performance(self, word: str, days: int = 30) -> List[float]:
        """模拟单词在未来N天的记忆表现"""
        if word not in self.memory_cards:
            return [1.0] * days  # 新单词假设完全记住
        
        card = self.memory_cards[word]
        performance = []
        
        for day in range(1, days + 1):
            retrievability = self.calculate_retrievability(card, day)
            performance.append(retrievability)
        
        return performance

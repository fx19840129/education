import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.services.vocab_selector import VocabSelector


class FSRSLearningGenerator:
    """基于FSRS算法的学习内容生成器"""
    
    def __init__(self, config_dir: str = "src/english/config", fsrs_file: str = "learning_data/fsrs_memory.json"):
        self.config_dir = Path(config_dir)
        self.fsrs_file = Path(fsrs_file)
        self.vocab_selector = VocabSelector(self.config_dir)
        self.fsrs_data = self._load_fsrs_data()
        
    def _load_fsrs_data(self) -> Dict:
        """加载FSRS数据"""
        try:
            with open(self.fsrs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载FSRS数据失败: {e}")
            return {"desired_retention": 0.85, "parameters": {"w": []}, "memory_cards": {}}
    
    def _fsrs_schedule(self, stability: float, difficulty: float, grade: int, 
                      desired_retention: float = 0.85) -> Tuple[float, float, float]:
        """
        FSRS算法核心调度函数
        
        Args:
            stability: 稳定性
            difficulty: 难度
            grade: 评分 (0-4)
            desired_retention: 期望保持率
            
        Returns:
            (new_stability, new_difficulty, interval)
        """
        w = self.fsrs_data.get("parameters", {}).get("w", [])
        if len(w) < 21:
            # 使用默认参数
            w = [0.2172, 1.1771, 3.2602, 16.1507, 7.0114, 0.57, 2.0966, 0.0069, 
                 1.5261, 0.112, 1.0178, 1.849, 0.1133, 0.3127, 2.2934, 0.2191, 
                 3.0004, 0.7536, 0.3332, 0.1437, 0.2]
        
        # 计算新的稳定性
        if grade >= 3:
            new_stability = stability * (1 + w[0] * (math.exp(w[1] * (1 - desired_retention)) - 1))
        else:
            new_stability = stability * w[2] * math.exp(w[3] * (1 - desired_retention))
        
        # 计算新的难度
        if grade >= 3:
            new_difficulty = difficulty + w[4] * (1 - desired_retention)
        else:
            new_difficulty = difficulty + w[5] * (1 - desired_retention)
        
        # 计算间隔
        interval = new_stability * math.exp(w[6] * (1 - desired_retention))
        
        return new_stability, new_difficulty, interval
    
    def _get_word_difficulty(self, word: str) -> float:
        """获取单词的初始难度"""
        # 基于单词长度和复杂度估算难度
        word_len = len(word)
        if word_len <= 3:
            return 2.0
        elif word_len <= 5:
            return 3.0
        elif word_len <= 7:
            return 4.0
        else:
            return 5.0
    
    def _get_word_stability(self, word: str) -> float:
        """获取单词的初始稳定性"""
        # 新单词的初始稳定性
        return 2.5
    
    def generate_daily_learning_content(self, learning_plan: Dict, target_date: str = None) -> Dict:
        """
        生成指定日期的学习内容
        
        Args:
            learning_plan: 学习计划
            target_date: 目标日期 (YYYY-MM-DD格式)，默认为今天
            
        Returns:
            包含学习内容的字典
        """
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        stage = learning_plan.get("metadata", {}).get("stage", "")
        study_plan = learning_plan.get("learning_plan", {}).get("study_plan", {})
        
        daily_content = {
            "date": target_date,
            "stage": stage,
            "total_words": 0,
            "pos_content": {},
            "morphology": [],
            "syntax": []
        }
        
        # 为每个词性生成学习内容
        for pos, plan in study_plan.items():
            if plan.get("daily_learn_count", 0) > 0:
                pos_words = self._generate_pos_learning_content(
                    stage, pos, plan, target_dt
                )
                daily_content["pos_content"][pos] = pos_words
                daily_content["total_words"] += len(pos_words)
        
        # 生成词法和句法内容
        morphology_plan = learning_plan.get("learning_plan", {}).get("morphology", {})
        if morphology_plan.get("daily_learn_count", 0) > 0:
            daily_content["morphology"] = self._generate_morphology_content(
                stage, morphology_plan, target_dt
            )
        
        syntax_plan = learning_plan.get("learning_plan", {}).get("syntax", {})
        if syntax_plan.get("daily_learn_count", 0) > 0:
            daily_content["syntax"] = self._generate_syntax_content(
                stage, syntax_plan, target_dt
            )
        
        return daily_content
    
    def _generate_pos_learning_content(self, stage: str, pos: str, plan: Dict, 
                                     target_dt: datetime) -> List[Dict]:
        """生成指定词性的学习内容"""
        daily_count = plan.get("daily_learn_count", 0)
        total_cycles = plan.get("total_study_cycles", 0)
        
        if daily_count <= 0:
            return []
        
        # 加载该词性的所有单词
        all_words = self.vocab_selector.load_pos_words(stage, pos)
        if not all_words:
            return []
        
        # 根据FSRS算法选择需要学习的单词
        selected_words = self._select_words_by_fsrs(
            all_words, daily_count, total_cycles, target_dt
        )
        
        # 为每个单词生成学习内容
        learning_words = []
        for word_data in selected_words:
            learning_word = {
                "word": word_data.get("word", ""),
                "translation": word_data.get("chinese", ""),  # 使用chinese字段作为翻译
                "pos": pos,
                "difficulty": self._get_word_difficulty(word_data.get("word", "")),
                "stability": self._get_word_stability(word_data.get("word", "")),
                "review_count": 0,
                "last_review": None,
                "next_review": target_dt.strftime("%Y-%m-%d"),
                "grade_history": [],
                "learning_phase": "new"  # new, learning, reviewing
            }
            learning_words.append(learning_word)
        
        return learning_words
    
    def _select_words_by_fsrs(self, all_words: List[Dict], daily_count: int, 
                            total_cycles: int, target_dt: datetime) -> List[Dict]:
        """使用FSRS算法选择需要学习的单词"""
        if len(all_words) <= daily_count:
            return all_words
        
        # 获取需要复习的单词
        review_words = self.get_review_words(target_dt.strftime("%Y-%m-%d"))
        review_word_set = {word_data["word"] for word_data in review_words}
        
        # 分离新单词和需要复习的单词
        new_words = []
        words_to_review = []
        
        for word_data in all_words:
            word = word_data.get("word", "")
            if word in review_word_set:
                words_to_review.append(word_data)
            else:
                new_words.append(word_data)
        
        selected_words = []
        
        # 优先选择需要复习的单词
        if words_to_review and len(selected_words) < daily_count:
            review_count = min(len(words_to_review), daily_count - len(selected_words))
            selected_words.extend(words_to_review[:review_count])
        
        # 如果还需要更多单词，从新单词中选择
        if len(selected_words) < daily_count:
            remaining_count = daily_count - len(selected_words)
            if len(new_words) >= remaining_count:
                # 按难度排序，优先选择中等难度的单词
                new_words.sort(key=lambda x: self._get_word_difficulty(x.get("word", "")))
                start_idx = max(0, len(new_words) // 3)  # 从1/3处开始选择
                end_idx = min(len(new_words), start_idx + remaining_count)
                selected_words.extend(new_words[start_idx:end_idx])
            else:
                selected_words.extend(new_words)
        
        return selected_words[:daily_count]
    
    def _generate_morphology_content(self, stage: str, plan: Dict, 
                                   target_dt: datetime) -> List[Dict]:
        """生成词法学习内容"""
        daily_count = plan.get("daily_learn_count", 0)
        if daily_count <= 0:
            return []
        
        # 这里可以加载词法文件并选择内容
        # 暂时返回空列表，后续实现
        return []
    
    def _generate_syntax_content(self, stage: str, plan: Dict, 
                               target_dt: datetime) -> List[Dict]:
        """生成句法学习内容"""
        daily_count = plan.get("daily_learn_count", 0)
        if daily_count <= 0:
            return []
        
        # 这里可以加载句法文件并选择内容
        # 暂时返回空列表，后续实现
        return []
    
    def generate_learning_schedule(self, learning_plan: Dict, start_date: str = None) -> Dict:
        """
        生成完整的学习计划表
        
        Args:
            learning_plan: 学习计划
            start_date: 开始日期 (YYYY-MM-DD格式)，默认为今天
            
        Returns:
            包含完整学习计划的字典
        """
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        total_days = learning_plan.get("learning_plan", {}).get("learning_cycle_days", 60)
        
        schedule = {
            "start_date": start_date,
            "total_days": total_days,
            "daily_schedule": []
        }
        
        # 生成每一天的学习内容
        for day in range(total_days):
            current_date = (start_dt + timedelta(days=day)).strftime("%Y-%m-%d")
            daily_content = self.generate_daily_learning_content(learning_plan, current_date)
            schedule["daily_schedule"].append(daily_content)
        
        return schedule
    
    def update_word_progress(self, word: str, grade: int, current_date: str = None) -> Dict:
        """
        更新单词学习进度
        
        Args:
            word: 单词
            grade: 评分 (0-4)
            current_date: 当前日期
            
        Returns:
            更新后的单词状态
        """
        if current_date is None:
            current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 从FSRS数据中获取单词状态
        memory_cards = self.fsrs_data.get("memory_cards", {})
        word_data = memory_cards.get(word, {})
        
        if not word_data:
            # 新单词
            stability = self._get_word_stability(word)
            difficulty = self._get_word_difficulty(word)
        else:
            stability = word_data.get("stability", 2.5)
            difficulty = word_data.get("difficulty", 3.0)
        
        # 使用FSRS算法计算新的状态
        new_stability, new_difficulty, interval = self._fsrs_schedule(
            stability, difficulty, grade, self.fsrs_data.get("desired_retention", 0.85)
        )
        
        # 计算下次复习时间
        next_review = datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=interval)
        
        # 更新单词状态
        updated_word_data = {
            "word": word,
            "stability": new_stability,
            "difficulty": new_difficulty,
            "last_review": current_date,
            "review_count": word_data.get("review_count", 0) + 1,
            "grade_history": word_data.get("grade_history", []) + [grade],
            "interval": interval,
            "next_review": next_review.strftime("%Y-%m-%d")
        }
        
        return updated_word_data
    
    def get_review_words(self, target_date: str = None) -> List[Dict]:
        """
        获取需要复习的单词
        
        Args:
            target_date: 目标日期
            
        Returns:
            需要复习的单词列表
        """
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        review_words = []
        
        memory_cards = self.fsrs_data.get("memory_cards", {})
        for word, data in memory_cards.items():
            next_review = data.get("next_review")
            if next_review:
                next_review_dt = datetime.strptime(next_review, "%Y-%m-%d")
                if next_review_dt <= target_dt:
                    review_words.append({
                        "word": word,
                        "data": data
                    })
        
        return review_words
    
    def save_learning_progress(self, progress_data: Dict, filename: str = None) -> str:
        """
        保存学习进度到文件
        
        Args:
            progress_data: 学习进度数据
            filename: 文件名，默认为时间戳
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"learning_progress_{timestamp}.json"
        
        progress_dir = Path("learning_data/english")
        progress_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = progress_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def load_learning_progress(self, filename: str) -> Dict:
        """
        加载学习进度文件
        
        Args:
            filename: 文件名
            
        Returns:
            学习进度数据
        """
        progress_dir = Path("learning_data/english")
        filepath = progress_dir / filename
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载学习进度失败: {e}")
            return {}
    
    def get_learning_statistics(self, learning_plan: Dict, target_date: str = None) -> Dict:
        """
        获取学习统计信息
        
        Args:
            learning_plan: 学习计划
            target_date: 目标日期
            
        Returns:
            学习统计信息
        """
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        stage = learning_plan.get("metadata", {}).get("stage", "")
        study_plan = learning_plan.get("learning_plan", {}).get("study_plan", {})
        
        stats = {
            "date": target_date,
            "stage": stage,
            "total_words_learned": 0,
            "total_words_reviewed": 0,
            "pos_statistics": {},
            "learning_efficiency": 0.0
        }
        
        # 统计各词性的学习情况
        for pos, plan in study_plan.items():
            daily_count = plan.get("daily_learn_count", 0)
            total_count = plan.get("total_count", 0)
            
            # 计算学习进度
            progress = min(1.0, daily_count / max(total_count, 1))
            
            stats["pos_statistics"][pos] = {
                "daily_count": daily_count,
                "total_count": total_count,
                "progress": progress,
                "remaining": max(0, total_count - daily_count)
            }
            
            stats["total_words_learned"] += daily_count
        
        # 计算学习效率
        total_planned = sum(plan.get("total_count", 0) for plan in study_plan.values())
        if total_planned > 0:
            stats["learning_efficiency"] = stats["total_words_learned"] / total_planned
        
        return stats
    
    def generate_adaptive_schedule(self, learning_plan: Dict, current_progress: Dict) -> Dict:
        """
        生成自适应学习计划
        
        Args:
            learning_plan: 原始学习计划
            current_progress: 当前学习进度
            
        Returns:
            调整后的学习计划
        """
        # 基于当前进度调整每日学习量
        adjusted_plan = learning_plan.copy()
        study_plan = adjusted_plan.get("learning_plan", {}).get("study_plan", {})
        
        for pos, plan in study_plan.items():
            current_progress_pos = current_progress.get("pos_statistics", {}).get(pos, {})
            progress = current_progress_pos.get("progress", 0)
            
            # 如果进度落后，增加每日学习量
            if progress < 0.5:  # 进度低于50%
                plan["daily_learn_count"] = int(plan["daily_learn_count"] * 1.2)
            # 如果进度超前，适当减少每日学习量
            elif progress > 0.8:  # 进度高于80%
                plan["daily_learn_count"] = int(plan["daily_learn_count"] * 0.9)
            
            # 确保每日学习量不为0
            plan["daily_learn_count"] = max(1, plan["daily_learn_count"])
        
        return adjusted_plan

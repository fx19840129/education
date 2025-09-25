#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日学习内容生成器
将单词、语法和句子有机结合，加强记忆效果
"""

import random
import os
import sys
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'word_learning_modules'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'grammar_modules'))
sys.path.append(os.path.dirname(__file__))

from word_database import WordDatabase, WordInfo
from grammar_config_loader import GrammarConfigLoader
from exercise_generator import ExerciseGenerator
from sentence_validator import SentenceValidator
from fsrs_memory_scheduler import FSRSMemoryScheduler
from ai_sentence_generator import AISentenceGenerator, SentenceRequest
from ai_content_generator import AIContentGenerator, DailyContentRequest


class DailyContentGenerator:
    """每日学习内容生成器"""
    
    def __init__(self, use_ai_sentences=True):
        self.word_db = WordDatabase("word_configs")
        self.grammar_loader = GrammarConfigLoader("grammar_configs")
        self.exercise_generator = ExerciseGenerator()
        self.sentence_validator = SentenceValidator()
        self.use_ai_sentences = use_ai_sentences
        if use_ai_sentences:
            self.ai_sentence_generator = AISentenceGenerator()
            self.ai_content_generator = AIContentGenerator()
        else:
            self.ai_sentence_generator = None
            self.ai_content_generator = None
        
        # 词性映射表
        self.part_of_speech_map = {
            "noun": {"chinese": "名词", "abbreviation": "n."},
            "verb": {"chinese": "动词", "abbreviation": "v."},
            "adjective": {"chinese": "形容词", "abbreviation": "adj."},
            "adverb": {"chinese": "副词", "abbreviation": "adv."},
            "pronoun": {"chinese": "代词", "abbreviation": "pron."},
            "preposition": {"chinese": "介词", "abbreviation": "prep."},
            "conjunction": {"chinese": "连词", "abbreviation": "conj."},
            "interjection": {"chinese": "感叹词", "abbreviation": "interj."},
            "article": {"chinese": "冠词", "abbreviation": "art."},
            "numeral": {"chinese": "数词", "abbreviation": "num."},
            "determiner": {"chinese": "限定词", "abbreviation": "det."}
        }
        
        # 学习阶段配置
        self.phases = self._init_learning_phases()
        
        # FSRS记忆调度器 - 基于最新算法
        self.fsrs_scheduler = FSRSMemoryScheduler(desired_retention=0.85)
        
        # 学习进度跟踪（保留兼容性）
        self.progress_file = "learning_data/learning_progress.json"
        self.learned_words = set()  # 已学过的单词
        self.word_learning_history = {}  # 单词学习历史 {word: [day1, day2, ...]}
        self.daily_word_pools = {}  # 每个难度级别的单词池 {level_difficulty: [words...]}
        
        # 加载学习进度和FSRS状态
        self._load_learning_progress()
        self.fsrs_scheduler.load_memory_state("learning_data/fsrs_memory.json")
    
    def _get_part_of_speech_display(self, part_of_speech: str) -> str:
        """获取词性的中文和简写显示"""
        if part_of_speech in self.part_of_speech_map:
            mapping = self.part_of_speech_map[part_of_speech]
            return f"{mapping['chinese']} ({mapping['abbreviation']})"
        else:
            return f"{part_of_speech} ({part_of_speech[0]}. )"
        
    def _init_learning_phases(self) -> List[Dict[str, Any]]:
        """初始化学习阶段配置"""
        return [
            {
                "phase": 1,
                "name": "基础建立阶段",
                "duration": 30,
                "word_level": "elementary",
                "word_difficulty": "easy",
                "grammar_level": "elementary",
                "daily_words": 8,
                "exercises_per_day": 15,
                "grammar_topics": [
                    "be动词用法", "名词单复数-基础规则", "人称代词", 
                    "一般现在时-基础用法", "一般现在时-第三人称单数"
                ]
            },
            {
                "phase": 2,
                "name": "巩固提升阶段", 
                "duration": 30,
                "word_level": "elementary",
                "word_difficulty": "medium",
                "grammar_level": "elementary",
                "daily_words": 10,
                "exercises_per_day": 18,
                "grammar_topics": [
                    "一般现在时-否定形式", "一般现在时-疑问形式", "现在进行时-基础用法",
                    "一般过去时-基础用法", "形容词比较级-基础用法"
                ]
            },
            {
                "phase": 3,
                "name": "扩展应用阶段",
                "duration": 30,
                "word_level": "middle_school",
                "word_difficulty": "easy",
                "grammar_level": "middle_school",
                "daily_words": 12,
                "exercises_per_day": 20,
                "grammar_topics": [
                    "现在完成时-基础用法", "被动语态-基础用法", "情态动词-基础用法",
                    "条件句-基础用法", "定语从句-基础用法"
                ]
            },
            {
                "phase": 4,
                "name": "进阶挑战阶段",
                "duration": 30,
                "word_level": "middle_school",
                "word_difficulty": "medium",
                "grammar_level": "middle_school",
                "daily_words": 15,
                "exercises_per_day": 25,
                "grammar_topics": [
                    "定语从句-关系代词", "间接引语-基础用法", "过去进行时-基础用法",
                    "现在完成时-持续用法", "被动语态-时态变化"
                ]
            },
            {
                "phase": 5,
                "name": "综合强化阶段",
                "duration": 30,
                "word_level": "mixed",
                "word_difficulty": "mixed",
                "grammar_level": "mixed",
                "daily_words": 12,
                "exercises_per_day": 22,
                "grammar_topics": [
                    "综合语法复习", "语法应用练习", "语法错误纠正", "语法综合测试"
                ]
            },
            {
                "phase": 6,
                "name": "冲刺巩固阶段",
                "duration": 30,
                "word_level": "mixed",
                "word_difficulty": "mixed",
                "grammar_level": "mixed",
                "daily_words": 10,
                "exercises_per_day": 30,
                "grammar_topics": [
                    "全面语法复习", "语法实战应用", "综合能力测试", "学习成果评估"
                ]
            }
        ]
    
    def generate_daily_content(self, day: int) -> Dict[str, Any]:
        """生成指定日期的学习内容"""
        # 确定当前阶段
        current_phase = self._get_current_phase(day)
        
        # 生成单词内容
        word_content = self._generate_word_content(day, current_phase)
        
        # 生成语法内容
        grammar_content = self._generate_grammar_content(day, current_phase)
        
        # 生成综合练习句子和练习题
        if self.use_ai_sentences and self.ai_content_generator:
            # 使用AI一次性生成句子和练习题
            ai_content = self._generate_ai_integrated_content(word_content, grammar_content)
            integrated_sentences = ai_content.sentences
            exercises = ai_content.exercises
        else:
            # 使用原有方法分别生成
            integrated_sentences = self._generate_integrated_sentences(word_content, grammar_content)
            exercise_count = self._get_exercise_count_for_phase(grammar_content)
            exercises = self.exercise_generator.generate_daily_exercises(
                word_content["words"], 
                grammar_content["topic"], 
                exercise_count
            )
        
        # 保存学习进度
        self._save_learning_progress()
        
        return {
            "day": day,
            "phase": current_phase,
            "word_content": word_content,
            "grammar_content": grammar_content,
            "integrated_sentences": integrated_sentences,
            "exercises": exercises
        }
    
    def _get_current_phase(self, day: int) -> Dict[str, Any]:
        """获取当前学习阶段"""
        cumulative_days = 0
        for phase in self.phases:
            cumulative_days += phase["duration"]
            if day <= cumulative_days:
                return phase
        return self.phases[-1]  # 返回最后一个阶段
    
    def _generate_word_content(self, day: int, phase: Dict[str, Any]) -> Dict[str, Any]:
        """生成单词学习内容"""
        # 获取单词
        if phase["word_level"] == "mixed":
            # 混合阶段，随机选择小学或初中单词
            level = random.choice(["elementary", "middle_school"])
        else:
            level = phase["word_level"]
        
        if phase["word_difficulty"] == "mixed":
            # 混合难度，随机选择难度
            difficulty = random.choice(["easy", "medium", "hard"])
        else:
            difficulty = phase["word_difficulty"]
        
        words = self._get_words_for_day_fsrs(level, difficulty, phase["daily_words"], day)
        
        return {
            "level": level,
            "difficulty": difficulty,
            "count": len(words),
            "words": words
        }
    
    def _generate_grammar_content(self, day: int, phase: Dict[str, Any]) -> Dict[str, Any]:
        """生成语法学习内容"""
        # 选择当天的语法主题
        if phase["grammar_level"] == "mixed":
            # 混合阶段，随机选择语法主题
            grammar_topic = random.choice([
                "一般现在时-基础用法", "现在进行时-基础用法", "现在完成时-基础用法",
                "被动语态-基础用法", "定语从句-基础用法"
            ])
        else:
            grammar_topic = random.choice(phase["grammar_topics"])
        
        # 获取语法配置
        grammar_config = self.grammar_loader.load_grammar_config(grammar_topic)
        
        return {
            "topic": grammar_topic,
            "level": phase["grammar_level"],
            "config": grammar_config,
            "phase": phase,  # 包含完整的阶段信息
            "is_weekend": self._is_weekend(day)
        }
    
    def _generate_integrated_sentences(self, word_content: Dict[str, Any], 
                                     grammar_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成综合练习句子（将单词和语法结合）"""
        words = word_content["words"]
        grammar_topic = grammar_content["topic"]
        grammar_level = grammar_content["level"]
        
        # 准备单词数据
        word_data_list = []
        for word_info in words:
            word_data_list.append({
                "word": word_info.word,
                "chinese_meaning": word_info.chinese_meaning,
                "part_of_speech": word_info.part_of_speech,
                "pronunciation": word_info.pronunciation,
                "difficulty": word_info.difficulty
            })
        
        # 使用AI句子生成器（如果启用）
        if self.use_ai_sentences and self.ai_sentence_generator:
            request = SentenceRequest(
                words=word_data_list,
                grammar_topic=grammar_topic,
                grammar_level=grammar_level,
                sentence_count=len(words),
                difficulty="medium"
            )
            
            try:
                ai_sentences = self.ai_sentence_generator.generate_sentences(request)
                if ai_sentences:
                    # 转换为原有格式
                    sentences = []
                    for ai_sentence in ai_sentences:
                        sentences.append({
                            "word": ai_sentence.word,
                            "word_meaning": ai_sentence.word_meaning,
                            "part_of_speech": ai_sentence.part_of_speech,
                            "grammar_topic": ai_sentence.grammar_topic,
                            "sentence": ai_sentence.sentence,
                            "chinese_translation": ai_sentence.chinese_translation,
                            "grammar_explanation": ai_sentence.grammar_explanation,
                            "practice_tips": ai_sentence.practice_tips,
                            "ai_generated": ai_sentence.ai_generated
                        })
                    return sentences
            except Exception as e:
                print(f"⚠️ AI句子生成失败: {e}")
                print("回退到模板生成")
        
        # 回退到原有方法
        sentences = []
        for word_info in words:
            sentence = self._create_integrated_sentence(word_info, grammar_topic)
            if sentence:
                sentences.append(sentence)
        
        return sentences
    
    def _generate_ai_integrated_content(self, word_content: Dict[str, Any], 
                                      grammar_content: Dict[str, Any]) -> Any:
        """使用AI一次性生成句子和练习题"""
        words = word_content["words"]
        grammar_topic = grammar_content["topic"]
        grammar_level = grammar_content["level"]
        
        # 准备单词数据
        word_data_list = []
        for word_info in words:
            word_data_list.append({
                "word": word_info.word,
                "chinese_meaning": word_info.chinese_meaning,
                "part_of_speech": word_info.part_of_speech,
                "pronunciation": word_info.pronunciation,
                "difficulty": word_info.difficulty
            })
        
        # 使用AI内容生成器
        # 根据阶段设置练习题数量
        exercise_count = self._get_exercise_count_for_phase(grammar_content)
        
        request = DailyContentRequest(
            words=word_data_list,
            grammar_topic=grammar_topic,
            grammar_level=grammar_level,
            sentence_count=len(words),
            exercise_count=exercise_count,
            difficulty="medium"
        )
        
        try:
            ai_content = self.ai_content_generator.generate_daily_content(request)
            return ai_content
        except Exception as e:
            print(f"⚠️ AI内容生成失败: {e}")
            print("回退到原有方法")
            # 回退到原有方法
            integrated_sentences = self._generate_integrated_sentences(word_content, grammar_content)
            exercise_count = self._get_exercise_count_for_phase(grammar_content)
            exercises = self.exercise_generator.generate_daily_exercises(
                word_content["words"], 
                grammar_content["topic"], 
                exercise_count
            )
            return type('obj', (object,), {'sentences': integrated_sentences, 'exercises': exercises})()
    
    def _get_exercise_count_for_phase(self, grammar_content: Dict[str, Any]) -> int:
        """根据阶段获取练习题数量"""
        # 从语法内容中获取阶段信息
        phase = grammar_content.get("phase", {})
        exercises_per_day = phase.get("exercises_per_day", 10)
        
        # 根据是否为周末调整练习题数量
        is_weekend = grammar_content.get("is_weekend", False)
        if is_weekend:
            exercises_per_day = max(5, exercises_per_day // 2)
        
        return exercises_per_day
    
    def _is_weekend(self, day: int) -> bool:
        """判断是否为周末"""
        # 假设第1天是周一，第7天是周日
        return (day % 7) in [0, 6]  # 周六和周日
    
    def _create_integrated_sentence(self, word_info: WordInfo, grammar_topic: str) -> Dict[str, Any]:
        """创建包含单词和语法的综合句子"""
        
        # 首先尝试使用句子校验器生成经过校验的句子
        try:
            sentence_result = self.sentence_validator.generate_validated_sentence(word_info, grammar_topic)
            sentence = sentence_result["sentence"]
            chinese = sentence_result["chinese"]
            
            # 如果校验通过，直接使用
            if sentence_result.get("validation_status") != "fallback":
                return {
                    "word": word_info.word,
                    "word_meaning": word_info.chinese_meaning,
                    "part_of_speech": self._get_part_of_speech_display(word_info.part_of_speech),
                    "grammar_topic": grammar_topic,
                    "sentence": sentence,
                    "chinese_translation": chinese,
                    "grammar_explanation": self._get_grammar_explanation(grammar_topic),
                    "practice_tips": self._get_practice_tips(word_info, grammar_topic)
                }
        except:
            # 如果句子校验器失败，继续使用原来的逻辑
            pass
        
        # 根据语法主题生成相应的句子
        if "be动词用法" in grammar_topic:
            if word_info.part_of_speech == "adjective":
                sentence = f"I am {word_info.word} today."
                chinese = f"我今天{word_info.chinese_meaning}。"
            elif word_info.part_of_speech == "noun":
                sentence = f"This is a {word_info.word}."
                chinese = f"这是一个{word_info.chinese_meaning}。"
            else:
                sentence = f"I am {word_info.word}."
                chinese = f"我是{word_info.chinese_meaning}。"
        elif "一般现在时" in grammar_topic:
            if "第三人称单数" in grammar_topic:
                if word_info.part_of_speech == "verb":
                    sentence = f"He {word_info.word}s every day."
                    chinese = f"他每天{word_info.chinese_meaning}。"
                else:
                    sentence = f"He likes {word_info.word}."
                    chinese = f"他喜欢{word_info.chinese_meaning}。"
            elif "否定形式" in grammar_topic:
                if word_info.part_of_speech == "verb":
                    sentence = f"I don't {word_info.word} on weekends."
                    chinese = f"我周末不{word_info.chinese_meaning}。"
                else:
                    sentence = f"I don't like {word_info.word}."
                    chinese = f"我不喜欢{word_info.chinese_meaning}。"
            elif "疑问形式" in grammar_topic:
                if word_info.part_of_speech == "verb":
                    sentence = f"Do you {word_info.word} in the morning?"
                    chinese = f"你早上{word_info.chinese_meaning}吗？"
                else:
                    sentence = f"Do you like {word_info.word}?"
                    chinese = f"你喜欢{word_info.chinese_meaning}吗？"
            else:
                if word_info.part_of_speech == "verb":
                    sentence = f"I {word_info.word} every day."
                    chinese = f"我每天{word_info.chinese_meaning}。"
                else:
                    sentence = f"I like {word_info.word}."
                    chinese = f"我喜欢{word_info.chinese_meaning}。"
        
        elif "现在进行时" in grammar_topic:
            if word_info.part_of_speech == "verb":
                sentence = f"I am {word_info.word}ing now."
                chinese = f"我现在正在{word_info.chinese_meaning}。"
            else:
                sentence = f"I am looking at the {word_info.word}."
                chinese = f"我正在看{word_info.chinese_meaning}。"
        
        elif "一般过去时" in grammar_topic:
            if word_info.part_of_speech == "verb":
                sentence = f"I {word_info.word}ed yesterday."
                chinese = f"我昨天{word_info.chinese_meaning}了。"
            else:
                sentence = f"I saw a {word_info.word} yesterday."
                chinese = f"我昨天看到了一个{word_info.chinese_meaning}。"
        
        elif "现在完成时" in grammar_topic:
            if word_info.part_of_speech == "verb":
                sentence = f"I have {word_info.word}ed before."
                chinese = f"我以前{word_info.chinese_meaning}过。"
            else:
                sentence = f"I have seen a {word_info.word} before."
                chinese = f"我以前见过{word_info.chinese_meaning}。"
        
        elif "被动语态" in grammar_topic:
            sentence = f"The {word_info.word} is used by students."
            chinese = f"这个{word_info.chinese_meaning}被学生使用。"
        
        elif "定语从句" in grammar_topic:
            sentence = f"The {word_info.word} that I like is very good."
            chinese = f"我喜欢的那个{word_info.chinese_meaning}很好。"
        
        else:
            # 默认be动词用法
            if word_info.part_of_speech == "adjective":
                sentence = f"I am {word_info.word} today."
                chinese = f"我今天{word_info.chinese_meaning}。"
            elif word_info.part_of_speech == "noun":
                sentence = f"This is a {word_info.word}."
                chinese = f"这是一个{word_info.chinese_meaning}。"
            elif word_info.part_of_speech == "verb":
                sentence = f"I can {word_info.word}."
                chinese = f"我能{word_info.chinese_meaning}。"
            else:
                sentence = f"I like {word_info.word}."
                chinese = f"我喜欢{word_info.chinese_meaning}。"
        
        return {
            "word": word_info.word,
            "word_meaning": word_info.chinese_meaning,
            "part_of_speech": self._get_part_of_speech_display(word_info.part_of_speech),
            "grammar_topic": grammar_topic,
            "sentence": sentence,
            "chinese_translation": chinese,
            "grammar_explanation": self._get_grammar_explanation(grammar_topic),
            "practice_tips": self._get_practice_tips(word_info, grammar_topic)
        }
    
    def _get_grammar_explanation(self, grammar_topic: str) -> str:
        """获取语法解释"""
        explanations = {
            "一般现在时-基础用法": "表示经常性、习惯性的动作或状态",
            "一般现在时-第三人称单数": "第三人称单数主语后，动词要加-s或-es",
            "一般现在时-否定形式": "在动词前加don't或doesn't",
            "一般现在时-疑问形式": "在句首加Do或Does",
            "现在进行时-基础用法": "表示正在进行的动作，用be动词+动词ing",
            "一般过去时-基础用法": "表示过去发生的动作，动词用过去式",
            "现在完成时-基础用法": "表示过去发生但对现在有影响的动作，用have/has+过去分词",
            "被动语态-基础用法": "表示主语是动作的承受者，用be动词+过去分词",
            "定语从句-基础用法": "用来修饰名词的从句，用关系代词连接"
        }
        return explanations.get(grammar_topic, "语法规则说明")
    
    def _get_practice_tips(self, word_info: WordInfo, grammar_topic: str) -> List[str]:
        """获取练习建议"""
        tips = [
            f"多读几遍单词 '{word_info.word}' 和句子",
            f"注意单词的发音：{word_info.pronunciation}",
            f"理解句子中的语法结构",
            f"尝试用 '{word_info.word}' 造其他句子",
            f"复习相关的语法规则"
        ]
        return tips
    
    def _get_words_for_day(self, level: str, difficulty: str, count: int, day: int = 1) -> List[WordInfo]:
        """获取指定日期的单词，避免重复"""
        # 构建单词池的键
        pool_key = f"{level}_{difficulty}"
        
        # 初始化单词池（如果还没有初始化）
        if pool_key not in self.daily_word_pools:
            if level == "elementary":
                all_words = list(self.word_db.get_words_by_level("elementary").values())
            else:
                all_words = list(self.word_db.get_words_by_level("middle_school").values())
            
            if difficulty != "mixed":
                all_words = [w for w in all_words if w.difficulty == difficulty]
            
            # 打乱顺序，为循序渐进学习做准备
            random.shuffle(all_words)
            self.daily_word_pools[pool_key] = all_words
        
        words_pool = self.daily_word_pools[pool_key]
        
        # 实现单词选择策略：
        # 1. 优先选择从未学过的单词
        # 2. 适量加入需要复习的单词（滚动复习机制）
        
        new_words = []
        review_words = []
        
        # 获取可选的新单词（从未学过的）
        available_new_words = [w for w in words_pool if w.word not in self.learned_words]
        
        # 确定新单词和复习单词的比例 - 滚动式复习策略
        if day <= 3:
            review_ratio = 0  # 前3天纯学新单词，建立基础
        elif day <= 7:
            review_ratio = 0.125  # 第4-7天，12.5%复习（1个单词）
        elif day <= 14:
            review_ratio = 0.25   # 第8-14天，25%复习（2个单词）
        else:
            review_ratio = 0.375  # 第15天后，37.5%复习（3个单词）
        
        new_count = max(1, int(count * (1 - review_ratio)))
        review_count = count - new_count
        
        # 选择新单词（确保按顺序选择，避免重复）
        if available_new_words:
            selected_new = available_new_words[:min(new_count, len(available_new_words))]
            new_words.extend(selected_new)
            
            # 记录到学习历史
            for word in selected_new:
                self.learned_words.add(word.word)
                if word.word not in self.word_learning_history:
                    self.word_learning_history[word.word] = []
                self.word_learning_history[word.word].append(day)
                
            # 不从单词池中移除，允许后续按复习机制重新出现
        
        # 选择复习单词（根据遗忘曲线）
        if review_count > 0 and self.word_learning_history:
            review_candidates = self._get_review_candidates(day)
            if review_candidates:
                selected_review_words = review_candidates[:min(review_count, len(review_candidates))]
                review_words.extend(selected_review_words)
                
                # 更新学习历史
                for word in selected_review_words:
                    self.word_learning_history[word.word].append(day)
        
        # 如果单词不够，补充新单词
        total_selected = len(new_words) + len(review_words)
        if total_selected < count and available_new_words:
            remaining_new = available_new_words[len(new_words):len(new_words) + (count - total_selected)]
            new_words.extend(remaining_new)
            
            # 记录到学习历史
            for word in remaining_new:
                self.learned_words.add(word.word)
                if word.word not in self.word_learning_history:
                    self.word_learning_history[word.word] = []
                self.word_learning_history[word.word].append(day)
        
        # 合并新单词和复习单词
        selected_words = new_words + review_words
        
        # 如果还是不够（词库用完了），从所有单词中随机选择
        if len(selected_words) < count:
            remaining_needed = count - len(selected_words)
            additional_words = random.sample(words_pool, min(remaining_needed, len(words_pool)))
            selected_words.extend(additional_words)
        
        # 打乱顺序，避免总是新单词在前
        random.shuffle(selected_words)
        
        return selected_words[:count]
    
    def _get_words_for_day_fsrs(self, level: str, difficulty: str, count: int, day: int = 1) -> List[WordInfo]:
        """使用FSRS算法获取指定日期的单词（智能复习调度）"""
        # 构建单词池的键
        pool_key = f"{level}_{difficulty}"
        
        # 初始化单词池（如果还没有初始化）
        if pool_key not in self.daily_word_pools:
            if level == "elementary":
                all_words = list(self.word_db.get_words_by_level("elementary").values())
            else:
                all_words = list(self.word_db.get_words_by_level("middle_school").values())
            
            if difficulty != "mixed":
                all_words = [w for w in all_words if w.difficulty == difficulty]
            
            # 打乱顺序，为循序渐进学习做准备
            random.shuffle(all_words)
            self.daily_word_pools[pool_key] = all_words
        
        words_pool = self.daily_word_pools[pool_key]
        
        # 使用FSRS调度器智能选择单词
        word_list = [w.word for w in words_pool]
        selected_word_names = self.fsrs_scheduler.get_due_words(word_list, count)
        
        # 转换回WordInfo对象
        word_name_to_info = {w.word: w for w in words_pool}
        selected_words = []
        
        for word_name in selected_word_names:
            if word_name in word_name_to_info:
                word_info = word_name_to_info[word_name]
                selected_words.append(word_info)
                
                # 更新传统学习记录（保持兼容性）
                self.learned_words.add(word_name)
                if word_name not in self.word_learning_history:
                    self.word_learning_history[word_name] = []
                self.word_learning_history[word_name].append(day)
                
                # 基于单词特征估算学习效果并更新FSRS状态
                grade = self._estimate_learning_grade(word_info, day)
                self.fsrs_scheduler.review_word(word_name, grade)
        
        # 如果选中的单词不够，用传统方法补充
        if len(selected_words) < count:
            remaining_count = count - len(selected_words)
            selected_word_set = {w.word for w in selected_words}
            additional_words = [w for w in words_pool if w.word not in selected_word_set][:remaining_count]
            selected_words.extend(additional_words)
            
            # 记录补充的单词
            for word in additional_words:
                self.learned_words.add(word.word)
                if word.word not in self.word_learning_history:
                    self.word_learning_history[word.word] = []
                self.word_learning_history[word.word].append(day)
                
                # 为新单词初始化FSRS记录
                grade = self._estimate_learning_grade(word, day)
                self.fsrs_scheduler.review_word(word.word, grade)
        
        # 保存FSRS状态
        self.fsrs_scheduler.save_memory_state("learning_data/fsrs_memory.json")
        
        return selected_words[:count]
    
    def _estimate_learning_grade(self, word_info: WordInfo, day: int) -> int:
        """估算学习效果评分（用于FSRS调度）
        
        基于单词难度、词性复杂度等因素进行智能评估
        实际使用中应该由用户反馈替代
        """
        # 基础评分：根据单词难度
        if word_info.difficulty == "easy":
            base_grade = 4  # Easy - 简单单词容易记住
        elif word_info.difficulty == "medium":
            base_grade = 3  # Good - 中等难度需要一些努力
        else:  # hard
            base_grade = 2  # Hard - 困难单词需要更多练习
        
        # 词性复杂度调整
        complex_pos = ["conjunction", "preposition", "interjection"]
        if word_info.part_of_speech in complex_pos:
            base_grade = max(1, base_grade - 1)
        
        # 单词长度调整（长单词通常更难记）
        if len(word_info.word) >= 8:
            base_grade = max(1, base_grade - 1)
        elif len(word_info.word) <= 4:
            base_grade = min(4, base_grade + 1)
        
        # 学习阶段调整（前期学习效果可能不稳定）
        if day <= 7:
            # 前期学习有随机波动
            fluctuation = random.choices([-1, 0, 1], weights=[0.2, 0.6, 0.2])[0]
        else:
            # 后期学习更稳定
            fluctuation = random.choices([-1, 0, 1], weights=[0.1, 0.7, 0.2])[0]
        
        final_grade = max(1, min(4, base_grade + fluctuation))
        
        return final_grade
    
    def get_fsrs_statistics(self) -> Dict:
        """获取FSRS学习统计信息"""
        return self.fsrs_scheduler.get_learning_statistics()
    
    def _get_review_candidates(self, current_day: int) -> List[WordInfo]:
        """根据遗忘曲线获取需要复习的单词"""
        # 艾宾浩斯遗忘曲线：1天、2天、4天、7天、15天
        review_intervals = [1, 2, 4, 7, 15]
        candidates = []
        
        for word, learning_days in self.word_learning_history.items():
            last_learned_day = max(learning_days)
            days_since_last_learned = current_day - last_learned_day
            
            # 计算复习权重（越接近复习时间点，权重越高）
            review_weight = 0
            for interval in review_intervals:
                if abs(days_since_last_learned - interval) <= 1:  # 允许±1天的误差
                    # 根据学习次数调整权重（学过越多次，权重越低）
                    learning_times = len(learning_days)
                    base_weight = 10 - min(learning_times, 8)  # 基础权重2-10
                    review_weight = base_weight * (interval / 15)  # 时间间隔权重
                    break
            
            if review_weight > 0:
                word_info = self._find_word_info(word)
                if word_info:
                    candidates.append((word_info, review_weight))
        
        # 按权重排序，选择最需要复习的单词
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [word_info for word_info, weight in candidates]
    
    def _find_word_info(self, word: str) -> WordInfo:
        """根据单词找到WordInfo对象"""
        # 在小学词库中查找
        elementary_words = self.word_db.get_words_by_level("elementary")
        if word in elementary_words:
            return elementary_words[word]
        
        # 在中学词库中查找
        middle_school_words = self.word_db.get_words_by_level("middle_school")
        if word in middle_school_words:
            return middle_school_words[word]
        
        return None
    
    def _load_learning_progress(self):
        """加载学习进度"""
        import json
        import os
        
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learned_words = set(data.get('learned_words', []))
                    self.word_learning_history = data.get('word_learning_history', {})
                    
                    # 恢复单词池
                    saved_pools = data.get('daily_word_pools', {})
                    for pool_key, word_list in saved_pools.items():
                        self.daily_word_pools[pool_key] = [
                            WordInfo(w['word'], w['pronunciation'], w['part_of_speech'], 
                                   w['chinese_meaning'], w['english_meaning'], w['example_sentence'],
                                   w['difficulty'], w['grade_level'], w['category'])
                            for w in word_list
                        ]
                    
                    print(f"已加载学习进度：{len(self.learned_words)}个已学单词，{len(self.daily_word_pools)}个单词池")
        except Exception as e:
            print(f"加载学习进度失败：{e}")
    
    def _save_learning_progress(self):
        """保存学习进度"""
        import json
        import os
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            
            data = {
                'learned_words': list(self.learned_words),
                'word_learning_history': self.word_learning_history,
                'daily_word_pools': {k: [{'word': w.word, 'pronunciation': w.pronunciation, 'part_of_speech': w.part_of_speech, 'chinese_meaning': w.chinese_meaning, 'english_meaning': w.english_meaning, 'example_sentence': w.example_sentence, 'difficulty': w.difficulty, 'grade_level': w.grade_level, 'category': w.category} for w in v] for k, v in self.daily_word_pools.items()}
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存学习进度失败：{e}")
    
    def _generate_word_exercises(self, words: List[WordInfo]) -> List[Dict[str, Any]]:
        """生成单词练习"""
        exercises = []
        for word_info in words:
            exercise = {
                "word": word_info.word,
                "pronunciation": word_info.pronunciation,
                "meaning": word_info.chinese_meaning,
                "part_of_speech": word_info.part_of_speech,
                "example_sentence": word_info.example_sentence,
                "practice_questions": [
                    f"请拼写单词：{word_info.chinese_meaning}",
                    f"请说出单词 '{word_info.word}' 的发音",
                    f"请用 '{word_info.word}' 造一个句子",
                    f"请说出 '{word_info.word}' 的词性"
                ]
            }
            exercises.append(exercise)
        return exercises
    
    def _generate_grammar_exercises(self, grammar_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成语法练习"""
        if not grammar_config:
            return []
        
        exercises = []
        # 这里可以根据语法配置生成具体的练习
        # 简化处理，返回基本练习
        exercises.append({
            "topic": grammar_config.get("grammar_name", "语法练习"),
            "rules": grammar_config.get("explanation", {}).get("basic_rules", []),
            "examples": grammar_config.get("examples", {}).get("basic", []),
            "practice_questions": [
                "请写出这个语法规则",
                "请用这个语法造一个句子",
                "请找出句子中的语法错误",
                "请转换句子的语法结构"
            ]
        })
        return exercises
    
    def _generate_review_content(self, day: int) -> Dict[str, Any]:
        """生成复习内容"""
        review_words = []
        review_grammar = []
        
        # 根据复习间隔获取需要复习的内容
        review_intervals = [1, 3, 7, 14, 30]
        for interval in review_intervals:
            review_day = day - interval
            if review_day > 0:
                # 这里应该根据实际的学习记录来获取复习内容
                # 简化处理，返回示例内容
                review_words.extend([f"review_word_{review_day}_{i}" for i in range(2)])
                review_grammar.extend([f"review_grammar_{review_day}_{i}" for i in range(1)])
        
        return {
            "words": review_words[:5],  # 限制复习单词数量
            "grammar": review_grammar[:3],  # 限制复习语法数量
            "review_activities": [
                "快速复习单词卡片",
                "回顾语法规则",
                "重做之前的练习",
                "检查学习笔记"
            ]
        }
    
    def _get_word_activities(self, phase: int) -> List[str]:
        """获取单词学习活动"""
        activities = [
            "词汇卡片练习",
            "拼写练习", 
            "发音练习",
            "造句练习",
            "翻译练习",
            "填空练习",
            "选择题练习",
            "匹配练习"
        ]
        
        if phase <= 2:
            return activities[:4]
        elif phase <= 4:
            return activities[:6]
        else:
            return activities
    
    def _get_grammar_activities(self, phase: int) -> List[str]:
        """获取语法学习活动"""
        activities = [
            "语法规则学习",
            "例句分析",
            "语法练习",
            "改错练习",
            "转换练习",
            "综合应用",
            "语法测试",
            "口语练习"
        ]
        
        if phase <= 2:
            return activities[:3]
        elif phase <= 4:
            return activities[:5]
        else:
            return activities
    
    def _get_learning_tips(self, phase: int) -> List[str]:
        """获取学习建议"""
        tips = [
            "保持学习连续性，每天坚持15分钟",
            "多听多说，提高口语能力",
            "制作学习笔记，记录重点内容",
            "寻找学习伙伴，互相督促",
            "利用碎片时间，随时随地学习",
            "定期复习，巩固学习成果"
        ]
        
        if phase <= 2:
            tips.extend([
                "重点掌握基础词汇和语法",
                "多练习发音和拼写",
                "通过游戏增加学习趣味性"
            ])
        elif phase <= 4:
            tips.extend([
                "注重语法规则的理解和应用",
                "多读英文文章，提高语感",
                "练习写作，巩固语法知识"
            ])
        else:
            tips.extend([
                "综合运用所学知识",
                "进行模拟测试，检验学习效果",
                "寻找实际应用机会，提高实践能力"
            ])
        
        return tips

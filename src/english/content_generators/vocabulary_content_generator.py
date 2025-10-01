#!/usr/bin/env python3
"""
词汇内容生成器 - 重构后的核心模块
负责词汇内容的生成和管理
"""

import json
import sys
import os
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.services.fsrs_learning_service import FSRSLearningGenerator
from src.english.content_generators.coordinate_learning_content import LearningContentGenerator
from src.english.services.vocabulary_selection_service import VocabSelector
from src.english.services.word_morphology_service import MorphologyService
from src.english.services.sentence_syntax_service import SyntaxService
from src.english.utils.ai_prompt_builder import EnglishLearningPromptGenerator
from src.shared.ai_framework.unified_ai_client import UnifiedAIClient, AIModel


class VocabularyContentGenerator:
    """词汇内容生成器 - 核心功能"""
    
    def __init__(self):
        self.fsrs_generator = FSRSLearningGenerator()
        self.plan_reader = LearningContentGenerator()
        self.vocab_selector = VocabSelector()
        self.morphology_service = MorphologyService()
        self.syntax_service = SyntaxService()
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.plans_dir = self.project_root / "outputs" / "english" / "plans"
        
        # AI相关组件
        self.prompt_generator = EnglishLearningPromptGenerator()
        self.openai_client = UnifiedAIClient(default_model=AIModel.OPENAI_GPT4O_MINI)
        self.ai_client = UnifiedAIClient(default_model=AIModel.GLM_45)
        
        # 词汇分类到词性的映射
        self.category_pos_mapping = {
            "core_functional": ["noun", "verb", "adjective"],
            "connectors_relational": ["adverb", "preposition", "conjunction", "pronoun", "determiner", "article", "numeral"],
            "auxiliary_supplemental": ["interjection", "modal", "auxiliary", "phrase"]
        }
        
        # 学习进度跟踪
        self.learned_words_tracker = set()
        self.learning_progress = self._load_learning_progress()

    def _load_learning_progress(self) -> Dict:
        """加载学习进度"""
        progress_file = self.project_root / "learning_data" / "english" / "learning_progress.json"
        if progress_file.exists():
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    # 加载已学词汇到跟踪器
                    if 'learned_words' in progress:
                        self.learned_words_tracker.update(progress['learned_words'])
                    return progress
            except Exception as e:
                print(f"⚠️ 加载学习进度失败: {e}")
        return {"learned_words": [], "total_days": 0, "last_update": None}

    def _save_learning_progress(self):
        """保存学习进度"""
        progress_file = self.project_root / "learning_data" / "english" / "learning_progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.learning_progress.update({
            "learned_words": list(self.learned_words_tracker),
            "total_learned": len(self.learned_words_tracker),
            "last_update": datetime.now().isoformat()
        })
        
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存学习进度失败: {e}")

    def get_latest_plan(self) -> Optional[Dict]:
        """获取最新的学习计划"""
        fsrs_template_dir = self.plans_dir / "fsrs_templates"
        if not fsrs_template_dir.exists():
            print(f"❌ FSRS模板目录不存在: {fsrs_template_dir}")
            return None
        
        # 查找最新的模板文件
        template_files = list(fsrs_template_dir.glob("fsrs_template_*.json"))
        if not template_files:
            print(f"❌ 未找到FSRS模板文件")
            return None
        
        # 按文件名排序，获取最新的
        latest_file = sorted(template_files, key=lambda x: x.name)[-1]
        print(f"✅ 加载最新计划: {latest_file.name}")
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 读取计划文件失败: {e}")
            return None

    def parse_plan_requirements(self, plan_data: Dict) -> Dict:
        """解析计划要求"""
        try:
            metadata = plan_data.get('metadata', {})
            card_template = plan_data.get('card_template', {})
            
            # 提取基本信息
            stage = metadata.get('stage', '第一阶段：基础巩固')
            total_days = metadata.get('total_days', 30)
            daily_new_words = metadata.get('daily_new_words', 10)
            daily_review_words = metadata.get('daily_review_words', 10)
            
            # 提取词汇分类权重
            vocabulary_distribution = card_template.get('vocabulary_distribution', {})
            core_weight = vocabulary_distribution.get('core_functional', 0.7)
            connectors_weight = vocabulary_distribution.get('connectors_relational', 0.2)
            auxiliary_weight = vocabulary_distribution.get('auxiliary_supplemental', 0.1)
            
            print(f"📋 计划解析完成:")
            print(f"   阶段: {stage}")
            print(f"   总天数: {total_days}天")
            print(f"   每日新词: {daily_new_words}个")
            print(f"   每日复习: {daily_review_words}个")
            print(f"   词汇分类: 核心{core_weight*100:.1f}% | 连接{connectors_weight*100:.2f}% | 辅助{auxiliary_weight*100:.2f}%")
            
            return {
                'stage': stage,
                'total_days': total_days,
                'daily_new_words': daily_new_words,
                'daily_review_words': daily_review_words,
                'vocabulary_distribution': {
                    'core_functional': core_weight,
                    'connectors_relational': connectors_weight,
                    'auxiliary_supplemental': auxiliary_weight
                }
            }
            
        except Exception as e:
            print(f"❌ 解析计划要求失败: {e}")
            # 返回默认配置
            return {
                'stage': '第一阶段：基础巩固',
                'total_days': 30,
                'daily_new_words': 10,
                'daily_review_words': 10,
                'vocabulary_distribution': {
                    'core_functional': 0.7,
                    'connectors_relational': 0.2,
                    'auxiliary_supplemental': 0.1
                }
            }

    def load_vocabulary_by_pos(self, stage_key: str, pos: str) -> List[Dict]:
        """根据词性加载词汇"""
        try:
            vocab_file = self.project_root / "src" / "english" / "config" / "word_configs" / "classified_by_pos" / f"{stage_key}_{pos}_words.json"
            if vocab_file.exists():
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 提取words数组，并转换格式
                    words = data.get('words', [])
                    # 转换为统一格式
                    formatted_words = []
                    for word in words:
                        formatted_words.append({
                            'word': word.get('word', ''),
                            'part_of_speech': word.get('pos', pos),
                            'definition': word.get('chinese', ''),
                            'difficulty_level': 'elementary'
                        })
                    return formatted_words
            else:
                print(f"⚠️ 词汇文件不存在: {vocab_file}")
                return []
        except Exception as e:
            print(f"❌ 加载词汇失败 ({stage_key}_{pos}): {e}")
            return []

    def get_vocabulary_for_category(self, category: str, stage_key: str, count: int, day: int) -> List[Dict]:
        """为指定分类获取词汇"""
        print(f"✅ 选择{category}词汇: {count}个")
        
        # 获取该分类对应的词性列表
        pos_list = self.category_pos_mapping.get(category, ["noun"])
        selected_words = []
        
        for pos in pos_list:
            if len(selected_words) >= count:
                break
                
            print(f"✅ 加载词汇库: {stage_key}_{pos} ({len(self.load_vocabulary_by_pos(stage_key, pos))}个词汇)")
            pos_words = self.load_vocabulary_by_pos(stage_key, pos)
            
            # 过滤已学词汇
            available_words = [w for w in pos_words if w.get('word', '') not in self.learned_words_tracker]
            
            # 根据需要的数量选择词汇
            needed = min(count - len(selected_words), len(available_words))
            if needed > 0:
                # 使用day作为随机种子，确保相同天数生成相同结果
                random.seed(day * 1000 + hash(category) % 1000)
                selected = random.sample(available_words, needed)
                selected_words.extend(selected)
                
                # 添加到已学词汇跟踪器
                for word in selected:
                    self.learned_words_tracker.add(word.get('word', ''))
        
        return selected_words[:count]

    def _map_stage_to_key(self, stage: str) -> str:
        """将阶段名称映射到文件键"""
        if "小学" in stage or "基础" in stage:
            return "小学"
        elif "初中" in stage or "进阶" in stage:
            return "初中"
        elif "高中" in stage or "高级" in stage:
            return "高中"
        else:
            return "小学"  # 默认

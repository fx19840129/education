#!/usr/bin/env python3
"""
练习句子生成器
根据学习计划生成练习句子
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.content_generators.coordinate_learning_content import LearningContentGenerator
from src.english.services.fsrs_learning_service import FSRSLearningGenerator
from src.english.services.word_morphology_service import MorphologyService
from src.english.services.sentence_syntax_service import SyntaxService
from src.english.utils.ai_prompt_builder import EnglishLearningPromptGenerator
from src.shared.ai_framework.unified_ai_client import UnifiedAIClient, AIModel


class PracticeSentencesGenerator:
    """练习句子生成器"""
    
    def __init__(self):
        self.plan_reader = LearningContentGenerator()
        self.fsrs_service = FSRSLearningGenerator()
        self.morphology_service = MorphologyService()
        self.syntax_service = SyntaxService()
        self.prompt_generator = EnglishLearningPromptGenerator()
        self.ai_client = UnifiedAIClient(default_model=AIModel.GLM_45)
    
    def generate_daily_sentences(self, learning_plan: Dict, target_date: str = None, vocabulary_content: Dict = None) -> Dict:
        """生成指定日期的练习句子"""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        stage = learning_plan.get("metadata", {}).get("stage", "")
        
        # 从词汇内容中提取新学词汇和复习词汇
        new_words_data = {}
        review_words = []
        
        if vocabulary_content and 'vocabulary' in vocabulary_content:
            vocab = vocabulary_content['vocabulary']
            
            # 提取新学词汇
            new_words_categories = vocab.get('new_words', {})
            all_new_words = []
            
            for category, words_list in new_words_categories.items():
                for word_data in words_list:
                    all_new_words.append({
                        'word': word_data.get('word', ''),
                        'translation': word_data.get('definition', ''),
                        'pos': word_data.get('part_of_speech', 'unknown'),
                        'difficulty': word_data.get('difficulty_level', 'medium'),
                        'category': category
                    })
            
            # 按词性分组新学词汇
            pos_content = {}
            for word in all_new_words:
                pos = word['pos']
                if pos not in pos_content:
                    pos_content[pos] = []
                pos_content[pos].append(word)
            
            new_words_data = {
                "pos_content": pos_content
            }
            
            # 提取复习词汇
            review_words = vocab.get('review_words', [])
        
        # 获取词法和句法内容
        morphology_points = self.morphology_service.get_morphology_points(stage)
        syntax_points = self.syntax_service.get_syntax_points(stage)
        
        # 转换为所需格式
        daily_morphology = {
            "morphology_items": [
                {
                    "name": point.name,
                    "type": point.category,
                    "description": point.description,
                    "rules": point.examples[:3] if point.examples else []
                }
                for point in morphology_points[:2]  # 只取前2个
            ]
        }
        
        daily_syntax = {
            "syntax_items": [
                {
                    "name": point.name,
                    "type": point.category,
                    "structure": f"{point.name} - {point.description}",
                    "examples": point.examples[:2] if point.examples else []
                }
                for point in syntax_points[:2]  # 只取前2个
            ]
        }
        
        # 生成AI提示词
        prompt = self.prompt_generator.generate_practice_sentences_prompt(
            new_words_data, daily_morphology, daily_syntax, stage, review_words
        )
        
        # 调用AI生成练习句子
        try:
            ai_response = self.ai_client.generate_content(prompt)
            # 检查响应类型
            if hasattr(ai_response, 'content'):
                response_text = ai_response.content
            else:
                response_text = str(ai_response)
            
            practice_data = self._parse_ai_response(response_text)
            practice_sentences = practice_data.get('practice_sentences', [])
        except Exception as e:
            print(f"⚠️ AI生成练习句子失败: {e}")
            # 使用备用方法生成简单句子
            practice_sentences = self._generate_fallback_sentences(daily_words, stage)
        
        return {
            "date": target_date,
            "stage": stage,
            "total_sentences": len(practice_sentences),
            "practice_sentences": practice_sentences,
            "source": "ai_generated" if practice_sentences else "fallback"
        }
    
    def _parse_ai_response(self, ai_response: str) -> Dict:
        """解析AI响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(ai_response)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                print(f"⚠️ 无法解析AI响应: {ai_response[:200]}...")
                return {"practice_sentences": []}
    
    def _generate_fallback_sentences(self, daily_words: Dict, stage: str) -> List[Dict]:
        """备用方法：生成简单练习句子"""
        sentences = []
        
        # 收集所有单词
        all_words = []
        for pos, words in daily_words.get('pos_content', {}).items():
            for word in words:
                all_words.append({
                    'word': word['word'],
                    'pos': pos,
                    'translation': word.get('translation', ''),
                    'difficulty': word.get('difficulty', 3.0)
                })
        
        # 为每个单词生成一个简单句子
        for word in all_words[:8]:  # 最多8个句子
            sentence = self._create_simple_sentence(word, stage)
            if sentence:
                sentences.append(sentence)
        
        return sentences
    
    def _create_simple_sentence(self, word: Dict, stage: str) -> Dict:
        """创建简单句子"""
        word_text = word['word']
        pos = word['pos']
        translation = word['translation']
        
        # 根据词性生成不同类型的句子
        if pos == 'noun':
            sentence = f"I have a {word_text}."
            chinese = f"我有一个{translation}。"
        elif pos == 'verb':
            sentence = f"I {word_text} every day."
            chinese = f"我每天{translation}。"
        elif pos == 'adjective':
            sentence = f"This is a {word_text} book."
            chinese = f"这是一本{translation}的书。"
        elif pos == 'adverb':
            sentence = f"She runs {word_text}."
            chinese = f"她{translation}地跑步。"
        else:
            sentence = f"I use {word_text} in my work."
            chinese = f"我在工作中使用{translation}。"
        
        return {
            "sentence": sentence,
            "translation": chinese,
            "target_words": [word_text],
            "morphology_points": [],
            "syntax_structure": "简单句",
            "difficulty": word['difficulty'],
            "exercise_type": "translation",
            "explanation": f"练习{pos}的用法"
        }
    
    def _generate_sentences_from_words(self, daily_words: Dict, stage: str) -> List[Dict]:
        """根据单词生成练习句子"""
        sentences = []
        
        # 收集所有单词
        all_words = []
        for pos, words in daily_words.get('pos_content', {}).items():
            for word in words:
                all_words.append({
                    'word': word['word'],
                    'pos': pos,
                    'difficulty': word['difficulty']
                })
        
        # 按词性分组生成句子
        pos_groups = {}
        for word in all_words:
            pos = word['pos']
            if pos not in pos_groups:
                pos_groups[pos] = []
            pos_groups[pos].append(word)
        
        # 为每个词性生成练习句子
        for pos, words in pos_groups.items():
            if words:
                pos_sentences = self._generate_pos_sentences(pos, words, stage)
                sentences.extend(pos_sentences)
        
        return sentences
    
    def _generate_pos_sentences(self, pos: str, words: List[Dict], stage: str) -> List[Dict]:
        """为特定词性生成练习句子"""
        sentences = []
        
        # 根据词性生成不同类型的句子
        if pos == 'noun':
            sentences.extend(self._generate_noun_sentences(words, stage))
        elif pos == 'verb':
            sentences.extend(self._generate_verb_sentences(words, stage))
        elif pos == 'adjective':
            sentences.extend(self._generate_adjective_sentences(words, stage))
        elif pos == 'adverb':
            sentences.extend(self._generate_adverb_sentences(words, stage))
        else:
            sentences.extend(self._generate_general_sentences(pos, words, stage))
        
        return sentences
    
    def _generate_noun_sentences(self, words: List[Dict], stage: str) -> List[Dict]:
        """生成名词练习句子"""
        sentences = []
        
        for word in words[:3]:  # 每个词性最多3个句子
            sentence_templates = [
                f"I have a {word['word']}.",
                f"The {word['word']} is beautiful.",
                f"This is my {word['word']}.",
                f"I like the {word['word']}.",
                f"Where is the {word['word']}?"
            ]
            
            sentence = {
                "sentence": sentence_templates[0],
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "translation": f"我有一个{word['word']}。",
                "exercise_type": "translation"
            }
            sentences.append(sentence)
        
        return sentences
    
    def _generate_verb_sentences(self, words: List[Dict], stage: str) -> List[Dict]:
        """生成动词练习句子"""
        sentences = []
        
        for word in words[:3]:
            sentence_templates = [
                f"I {word['word']} every day.",
                f"She {word['word']}s well.",
                f"We can {word['word']} together.",
                f"Please {word['word']} this.",
                f"I will {word['word']} tomorrow."
            ]
            
            sentence = {
                "sentence": sentence_templates[0],
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "translation": f"我每天{word['word']}。",
                "exercise_type": "translation"
            }
            sentences.append(sentence)
        
        return sentences
    
    def _generate_adjective_sentences(self, words: List[Dict], stage: str) -> List[Dict]:
        """生成形容词练习句子"""
        sentences = []
        
        for word in words[:3]:
            sentence_templates = [
                f"This is a {word['word']} book.",
                f"The weather is {word['word']} today.",
                f"She looks {word['word']}.",
                f"I feel {word['word']}.",
                f"That's very {word['word']}."
            ]
            
            sentence = {
                "sentence": sentence_templates[0],
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "translation": f"这是一本{word['word']}的书。",
                "exercise_type": "translation"
            }
            sentences.append(sentence)
        
        return sentences
    
    def _generate_adverb_sentences(self, words: List[Dict], stage: str) -> List[Dict]:
        """生成副词练习句子"""
        sentences = []
        
        for word in words[:3]:
            sentence_templates = [
                f"She runs {word['word']}.",
                f"I work {word['word']}.",
                f"He speaks {word['word']}.",
                f"We study {word['word']}.",
                f"They play {word['word']}."
            ]
            
            sentence = {
                "sentence": sentence_templates[0],
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "translation": f"她{word['word']}地跑步。",
                "exercise_type": "translation"
            }
            sentences.append(sentence)
        
        return sentences
    
    def _generate_general_sentences(self, pos: str, words: List[Dict], stage: str) -> List[Dict]:
        """生成通用练习句子"""
        sentences = []
        
        for word in words[:2]:  # 其他词性最多2个句子
            sentence_templates = [
                f"I use {word['word']} in my work.",
                f"This is about {word['word']}.",
                f"We need {word['word']} here.",
                f"Can you find {word['word']}?",
                f"I know {word['word']} well."
            ]
            
            sentence = {
                "sentence": sentence_templates[0],
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "translation": f"我在工作中使用{word['word']}。",
                "exercise_type": "translation"
            }
            sentences.append(sentence)
        
        return sentences
    
    def generate_sentences_schedule(self, learning_plan: Dict, days: int = 7) -> Dict:
        """生成练习句子学习计划"""
        stage = learning_plan.get("metadata", {}).get("stage", "")
        plan_name = learning_plan.get("learning_plan", {}).get("learning_plan_name", "")
        
        start_date = datetime.now().strftime("%Y-%m-%d")
        daily_schedule = []
        
        for day in range(days):
            current_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day)).strftime("%Y-%m-%d")
            daily_content = self.generate_daily_sentences(learning_plan, current_date)
            daily_schedule.append(daily_content)
        
        return {
            "plan_name": plan_name,
            "stage": stage,
            "start_date": start_date,
            "days": days,
            "daily_schedule": daily_schedule
        }
    
    def display_sentences_content(self, schedule: Dict) -> None:
        """显示练习句子内容"""
        if not schedule:
            print("❌ 没有练习句子计划数据")
            return
        
        print("📚 练习句子学习计划")
        print("=" * 80)
        print(f"计划名称: {schedule['plan_name']}")
        print(f"学习阶段: {schedule['stage']}")
        print(f"开始日期: {schedule['start_date']}")
        print(f"生成天数: {schedule['days']}天")
        print()
        
        for i, daily in enumerate(schedule['daily_schedule'], 1):
            print(f"📅 第{i}天 - {daily['date']}")
            print(f"   总句子数: {daily['total_sentences']}个")
            print()
            
            if daily['practice_sentences']:
                for j, sentence in enumerate(daily['practice_sentences'], 1):
                    print(f"   📖 {j}. {sentence['sentence']}")
                    print(f"      翻译: {sentence['translation']}")
                    if sentence.get('target_words'):
                        print(f"      目标单词: {', '.join(sentence['target_words'])}")
                    if sentence.get('morphology_points'):
                        print(f"      词法点: {', '.join(sentence['morphology_points'])}")
                    if sentence.get('syntax_structure'):
                        print(f"      句法结构: {sentence['syntax_structure']}")
                    print(f"      难度: {sentence['difficulty']:.1f}")
                    print(f"      练习类型: {sentence['exercise_type']}")
                    if sentence.get('explanation'):
                        print(f"      解释: {sentence['explanation']}")
                    print()
            else:
                print("   今天没有练习句子")
            
            print("-" * 80)
            print()
    
    def generate_and_display(self, learning_plan: Dict, days: int = 7) -> None:
        """生成并显示练习句子内容"""
        print(f"📋 使用学习计划: {learning_plan.get('id', '未知')}")
        print(f"📋 学习阶段: {learning_plan['metadata']['stage']}")
        print()
        
        # 生成练习句子学习计划
        schedule = self.generate_sentences_schedule(learning_plan, days)
        
        # 显示学习内容
        self.display_sentences_content(schedule)
        
        # 显示统计信息
        total_sentences = sum(daily['total_sentences'] for daily in schedule['daily_schedule'])
        avg_daily = total_sentences / days if days > 0 else 0
        
        print("📊 练习句子统计:")
        print(f"   总句子数: {total_sentences}个")
        print(f"   学习天数: {days}天")
        print(f"   平均每天: {avg_daily:.1f}个句子")
        print()


def main():
    """主函数"""
    generator = PracticeSentencesGenerator()
    plan_reader = LearningContentGenerator()
    
    print("🔍 练习句子生成器")
    print("=" * 50)
    
    # 获取用户输入
    plan_id = input("请输入学习计划ID (按回车使用最新计划): ").strip()
    if not plan_id:
        plans = plan_reader.list_plans()
        if plans:
            plan_id = plans[0]['id']
        else:
            print("❌ 没有找到学习计划")
            return
    
    try:
        days = int(input("请输入生成天数 (默认7天): ").strip() or "7")
    except ValueError:
        days = 7
    
    print()
    
    # 读取学习计划
    learning_plan = plan_reader.read_plan(plan_id=plan_id)
    if not learning_plan:
        print(f"❌ 无法读取学习计划: {plan_id}")
        return
    
    # 生成并显示练习句子内容
    generator.generate_and_display(learning_plan, days)
    
    print("\n✅ 练习句子生成完成!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
练习题生成器
根据学习计划生成练习题
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.english.learning_content_generator import LearningContentGenerator
from src.english.services.fsrs_learning_generator import FSRSLearningGenerator
from src.english.generate_morphology_content import MorphologyContentGenerator
from src.english.generate_syntax_content import SyntaxContentGenerator
from src.english.english_prompt_generator import EnglishLearningPromptGenerator
from src.shared.ai_framework.unified_ai_client import UnifiedAIClient, AIModel


class PracticeExercisesGenerator:
    """练习题生成器"""
    
    def __init__(self):
        self.plan_reader = LearningContentGenerator()
        self.fsrs_generator = FSRSLearningGenerator()
        self.morphology_generator = MorphologyContentGenerator()
        self.syntax_generator = SyntaxContentGenerator()
        self.prompt_generator = EnglishLearningPromptGenerator()
        self.ai_client = UnifiedAIClient(default_model=AIModel.GLM_45)
    
    def generate_daily_exercises(self, learning_plan: Dict, target_date: str = None) -> Dict:
        """生成指定日期的练习题"""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        stage = learning_plan.get("metadata", {}).get("stage", "")
        
        # 获取当天的学习内容
        daily_words = self.fsrs_generator.generate_daily_learning_content(learning_plan, target_date)
        daily_morphology = self.morphology_generator.generate_daily_morphology(learning_plan, target_date)
        daily_syntax = self.syntax_generator.generate_daily_syntax(learning_plan, target_date)
        
        # 生成AI提示词
        prompt = self.prompt_generator.generate_practice_exercises_prompt(
            daily_words, daily_morphology, daily_syntax, stage
        )
        
        # 调用AI生成练习题
        try:
            ai_response = self.ai_client.generate_content(prompt)
            # 检查响应类型
            if hasattr(ai_response, 'content'):
                response_text = ai_response.content
            else:
                response_text = str(ai_response)
            
            practice_data = self._parse_ai_response(response_text)
            practice_exercises = practice_data.get('practice_exercises', [])
        except Exception as e:
            print(f"⚠️ AI生成练习题失败: {e}")
            # 使用备用方法生成简单练习题
            practice_exercises = self._generate_fallback_exercises(daily_words, stage)
        
        return {
            "date": target_date,
            "stage": stage,
            "total_exercises": len(practice_exercises),
            "practice_exercises": practice_exercises,
            "source": "ai_generated" if practice_exercises else "fallback"
        }
    
    def _parse_ai_response(self, ai_response: str) -> Dict:
        """解析AI响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(ai_response)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析失败: {e}")
            # 如果直接解析失败，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError as e2:
                    print(f"⚠️ 提取的JSON解析失败: {e2}")
                    print(f"⚠️ 原始响应: {ai_response[:300]}...")
                    return {"practice_exercises": []}
            else:
                print(f"⚠️ 无法找到JSON格式: {ai_response[:200]}...")
                return {"practice_exercises": []}
    
    def _generate_fallback_exercises(self, daily_words: Dict, stage: str) -> List[Dict]:
        """备用方法：生成简单练习题"""
        exercises = []
        
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
        
        # 生成选择题
        for i, word in enumerate(all_words[:3], 1):
            exercise = {
                "id": i,
                "type": "choice",
                "question": f"以下哪个是 '{word['word']}' 的中文意思？",
                "options": [
                    word['translation'],
                    f"错误的选项1",
                    f"错误的选项2", 
                    f"错误的选项3"
                ],
                "correct_answer": "A",
                "explanation": f"'{word['word']}' 的中文意思是 '{word['translation']}'",
                "target_words": [word['word']],
                "morphology_points": [],
                "syntax_structure": "",
                "difficulty": word['difficulty']
            }
            exercises.append(exercise)
        
        # 生成翻译题
        for i, word in enumerate(all_words[3:6], 4):
            exercise = {
                "id": i,
                "type": "translation",
                "question": "请将以下中文翻译成英文：",
                "chinese_text": f"我有一个{word['translation']}。",
                "english_text": f"I have a {word['word']}.",
                "explanation": f"这是一个简单的名词翻译练习，{word['word']} 是 {word['translation']} 的英文表达。",
                "target_words": [word['word']],
                "morphology_points": [],
                "syntax_structure": "主谓宾结构",
                "difficulty": word['difficulty']
            }
            exercises.append(exercise)
        
        # 生成填空题
        for i, word in enumerate(all_words[6:9], 7):
            exercise = {
                "id": i,
                "type": "fill_blank",
                "question": "请填入适当的单词：",
                "sentence": f"I ___ a {word['word']}.",
                "answer": "have",
                "explanation": f"这里需要填入动词 'have'，表示拥有的意思。",
                "target_words": [word['word']],
                "morphology_points": [],
                "syntax_structure": "主谓宾结构",
                "difficulty": word['difficulty']
            }
            exercises.append(exercise)
        
        return exercises
    
    def _generate_exercises_from_words(self, daily_words: Dict, stage: str) -> List[Dict]:
        """根据单词生成练习题"""
        exercises = []
        
        # 收集所有单词
        all_words = []
        for pos, words in daily_words.get('pos_content', {}).items():
            for word in words:
                all_words.append({
                    'word': word['word'],
                    'pos': pos,
                    'difficulty': word['difficulty']
                })
        
        # 生成不同类型的练习题
        exercises.extend(self._generate_word_choice_exercises(all_words))
        exercises.extend(self._generate_fill_blank_exercises(all_words))
        exercises.extend(self._generate_translation_exercises(all_words))
        exercises.extend(self._generate_sentence_completion_exercises(all_words))
        
        return exercises
    
    def _generate_word_choice_exercises(self, words: List[Dict]) -> List[Dict]:
        """生成选择题"""
        exercises = []
        
        for word in words[:5]:  # 最多5个选择题
            # 生成干扰选项
            distractors = self._generate_distractors(word)
            options = [word['word']] + distractors
            
            exercise = {
                "type": "word_choice",
                "question": f"请选择正确的单词：",
                "options": options,
                "correct_answer": word['word'],
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "explanation": f"正确答案是 {word['word']}，这是一个{word['pos']}。"
            }
            exercises.append(exercise)
        
        return exercises
    
    def _generate_fill_blank_exercises(self, words: List[Dict]) -> List[Dict]:
        """生成填空题"""
        exercises = []
        
        for word in words[:5]:  # 最多5个填空题
            sentence_templates = [
                f"I have a _____ book.",
                f"She _____ every day.",
                f"This is a _____ day.",
                f"He runs _____.",
                f"We need _____ here."
            ]
            
            # 根据词性选择合适的句子模板
            if word['pos'] == 'noun':
                sentence = "I have a _____ book."
            elif word['pos'] == 'verb':
                sentence = "She _____ every day."
            elif word['pos'] == 'adjective':
                sentence = "This is a _____ day."
            elif word['pos'] == 'adverb':
                sentence = "He runs _____."
            else:
                sentence = "We need _____ here."
            
            exercise = {
                "type": "fill_blank",
                "question": f"请填入正确的单词：{sentence}",
                "correct_answer": word['word'],
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "explanation": f"正确答案是 {word['word']}。"
            }
            exercises.append(exercise)
        
        return exercises
    
    def _generate_translation_exercises(self, words: List[Dict]) -> List[Dict]:
        """生成翻译题"""
        exercises = []
        
        for word in words[:5]:  # 最多5个翻译题
            exercise = {
                "type": "translation",
                "question": f"请翻译以下单词：{word['word']}",
                "correct_answer": f"翻译答案",
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "explanation": f"{word['word']} 是一个{word['pos']}，意思是...。"
            }
            exercises.append(exercise)
        
        return exercises
    
    def _generate_sentence_completion_exercises(self, words: List[Dict]) -> List[Dict]:
        """生成句子完成题"""
        exercises = []
        
        for word in words[:3]:  # 最多3个句子完成题
            sentence_templates = {
                'noun': f"I bought a new _____ yesterday.",
                'verb': f"She _____ to school every morning.",
                'adjective': f"The weather is _____ today.",
                'adverb': f"He speaks English _____."
            }
            
            sentence = sentence_templates.get(word['pos'], f"I use _____ in my work.")
            
            exercise = {
                "type": "sentence_completion",
                "question": f"请完成句子：{sentence}",
                "correct_answer": word['word'],
                "target_word": word['word'],
                "pos": word['pos'],
                "difficulty": word['difficulty'],
                "explanation": f"正确答案是 {word['word']}，这样句子就完整了。"
            }
            exercises.append(exercise)
        
        return exercises
    
    def _generate_distractors(self, target_word: Dict) -> List[str]:
        """生成干扰选项"""
        # 简单的干扰选项生成
        distractors = []
        
        # 基于词性生成相似的干扰选项
        pos = target_word['pos']
        word = target_word['word']
        
        if pos == 'noun':
            distractors = ['book', 'table', 'chair', 'door']
        elif pos == 'verb':
            distractors = ['go', 'come', 'see', 'know']
        elif pos == 'adjective':
            distractors = ['big', 'small', 'good', 'bad']
        elif pos == 'adverb':
            distractors = ['quickly', 'slowly', 'well', 'badly']
        else:
            distractors = ['the', 'and', 'or', 'but']
        
        # 确保不包含正确答案
        distractors = [d for d in distractors if d != word]
        
        # 返回3个干扰选项
        return distractors[:3]
    
    def generate_exercises_schedule(self, learning_plan: Dict, days: int = 7) -> Dict:
        """生成练习题学习计划"""
        stage = learning_plan.get("metadata", {}).get("stage", "")
        plan_name = learning_plan.get("learning_plan", {}).get("learning_plan_name", "")
        
        start_date = datetime.now().strftime("%Y-%m-%d")
        daily_schedule = []
        
        for day in range(days):
            current_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day)).strftime("%Y-%m-%d")
            daily_content = self.generate_daily_exercises(learning_plan, current_date)
            daily_schedule.append(daily_content)
        
        return {
            "plan_name": plan_name,
            "stage": stage,
            "start_date": start_date,
            "days": days,
            "daily_schedule": daily_schedule
        }
    
    def display_exercises_content(self, schedule: Dict) -> None:
        """显示练习题内容"""
        if not schedule:
            print("❌ 没有练习题计划数据")
            return
        
        print("📚 练习题学习计划")
        print("=" * 80)
        print(f"计划名称: {schedule['plan_name']}")
        print(f"学习阶段: {schedule['stage']}")
        print(f"开始日期: {schedule['start_date']}")
        print(f"生成天数: {schedule['days']}天")
        print()
        
        for i, daily in enumerate(schedule['daily_schedule'], 1):
            print(f"📅 第{i}天 - {daily['date']}")
            print(f"   总练习题数: {daily['total_exercises']}个")
            print()
            
            if daily['practice_exercises']:
                # 按类型分组显示
                type_groups = {}
                for exercise in daily['practice_exercises']:
                    ex_type = exercise['type']
                    if ex_type not in type_groups:
                        type_groups[ex_type] = []
                    type_groups[ex_type].append(exercise)
                
                for ex_type, exercises in type_groups.items():
                    type_name = {"choice": "选择题", "translation": "翻译题", "fill_blank": "填空题"}.get(ex_type, ex_type)
                    print(f"   📖 {type_name} ({len(exercises)}个):")
                    for j, exercise in enumerate(exercises[:2], 1):  # 只显示前2个
                        print(f"      {j}. {exercise['question']}")
                        if exercise['type'] == 'choice':
                            print(f"         选项: {', '.join(exercise['options'])}")
                            print(f"         答案: {exercise['correct_answer']}")
                        elif exercise['type'] == 'translation':
                            print(f"         中文: {exercise['chinese_text']}")
                            print(f"         英文: {exercise['english_text']}")
                        elif exercise['type'] == 'fill_blank':
                            print(f"         句子: {exercise['sentence']}")
                            print(f"         答案: {exercise['answer']}")
                        
                        if exercise.get('target_words'):
                            print(f"         目标单词: {', '.join(exercise['target_words'])}")
                        if exercise.get('morphology_points'):
                            print(f"         词法点: {', '.join(exercise['morphology_points'])}")
                        if exercise.get('syntax_structure'):
                            print(f"         句法结构: {exercise['syntax_structure']}")
                        
                        print(f"         解析: {exercise['explanation']}")
                        print(f"         难度: {exercise['difficulty']:.1f}")
                        print()
                    if len(exercises) > 2:
                        print(f"      ... 还有{len(exercises) - 2}个{type_name}")
                    print()
            else:
                print("   今天没有练习题")
            
            print("-" * 80)
            print()
    
    def generate_and_display(self, learning_plan: Dict, days: int = 7) -> None:
        """生成并显示练习题内容"""
        print(f"📋 使用学习计划: {learning_plan.get('id', '未知')}")
        print(f"📋 学习阶段: {learning_plan['metadata']['stage']}")
        print()
        
        # 生成练习题学习计划
        schedule = self.generate_exercises_schedule(learning_plan, days)
        
        # 显示学习内容
        self.display_exercises_content(schedule)
        
        # 显示统计信息
        total_exercises = sum(daily['total_exercises'] for daily in schedule['daily_schedule'])
        avg_daily = total_exercises / days if days > 0 else 0
        
        print("📊 练习题统计:")
        print(f"   总练习题数: {total_exercises}个")
        print(f"   学习天数: {days}天")
        print(f"   平均每天: {avg_daily:.1f}个练习题")
        print()


def main():
    """主函数"""
    generator = PracticeExercisesGenerator()
    plan_reader = LearningContentGenerator()
    
    print("🔍 练习题生成器")
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
    
    # 生成并显示练习题内容
    generator.generate_and_display(learning_plan, days)
    
    print("\n✅ 练习题生成完成!")


if __name__ == "__main__":
    main()

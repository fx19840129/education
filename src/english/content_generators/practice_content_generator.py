#!/usr/bin/env python3
"""
练习内容生成器 - 专门负责练习句子和练习题的生成
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.utils.ai_prompt_builder import EnglishLearningPromptGenerator
from src.shared.ai_framework.unified_ai_client import UnifiedAIClient, AIModel


class PracticeContentGenerator:
    """练习内容生成器 - 新策略：句子优先，题目跟随"""
    
    def __init__(self):
        self.prompt_generator = EnglishLearningPromptGenerator()
        self.openai_client = UnifiedAIClient(default_model=AIModel.OPENAI_GPT4O_MINI)

    def generate_practice_content(self, daily_words: Dict, daily_morphology: Dict, daily_syntax: Dict, stage: str, review_words: List[Dict]) -> Dict:
        """
        生成练习内容 - 新策略：先确保练习句子100%使用新学单词，然后基于句子生成练习题
        """
        try:
            print(f"🎯 使用新策略生成练习内容：句子优先，题目跟随")
            
            # 第一步：生成100%覆盖新学单词的练习句子
            practice_sentences_result = self._generate_practice_sentences_v2(
                daily_words, daily_morphology, daily_syntax, stage, review_words
            )
            
            # 第二步：基于练习句子生成练习题
            practice_exercises_result = self._generate_exercises_from_sentences(
                practice_sentences_result['practice_sentences'], stage
            )
            
            return {
                "practice_sentences": practice_sentences_result,
                "practice_exercises": practice_exercises_result,
                "generated_at": datetime.now().isoformat(),
                "generation_strategy": "sentences_first_exercises_follow"
            }
            
        except Exception as e:
            print(f"❌ 新策略练习内容生成失败: {e}")
            raise ValueError(f"新策略练习内容生成失败：{str(e)}")

    def _generate_practice_sentences_v2(self, daily_words: Dict, daily_morphology: Dict, daily_syntax: Dict, stage: str, review_words: List[Dict]) -> Dict:
        """生成练习句子 - 100%新学单词覆盖策略"""
        try:
            # 转换daily_words格式为提示词生成器期望的格式
            pos_content = {}
            if 'new_words' in daily_words:
                for category, words in daily_words['new_words'].items():
                    for word in words:
                        pos = word.get('part_of_speech', 'noun').split('/')[0]  # 取第一个词性
                        if pos not in pos_content:
                            pos_content[pos] = []
                        pos_content[pos].append({
                            'word': word['word'],
                            'translation': word.get('definition', ''),
                            'difficulty': word.get('difficulty_level', 'medium')
                        })
            
            formatted_daily_words = {'pos_content': pos_content}
            
            print(f"🎯 使用100%覆盖策略生成练习句子")
            print(f"   新学单词: {[word['word'] for category, words in daily_words['new_words'].items() for word in words]}")
            print(f"   复习单词: {[word['word'] if isinstance(word, dict) else word for word in review_words]}")
            
            # 使用新的100%覆盖策略生成提示词
            try:
                chinese_prompt = self.prompt_generator.generate_practice_sentences_prompt_v2(
                    formatted_daily_words, daily_morphology, daily_syntax, stage, review_words
                )
            except Exception as e:
                print(f"❌ 提示词生成失败: {e}")
                print(f"   daily_morphology类型: {type(daily_morphology)}")
                print(f"   daily_syntax类型: {type(daily_syntax)}")
                print(f"   review_words类型: {type(review_words)}")
                if review_words:
                    print(f"   review_words前3个元素: {review_words[:3]}")
                raise
            
            print(f"📝 100%覆盖策略提示词长度: {len(chinese_prompt)} 字符")
            
            # 使用OpenAI GPT-4o生成练习句子 (增加max_tokens提升成功率)
            response = self.openai_client.generate_content(
                prompt=chinese_prompt,
                model=AIModel.OPENAI_GPT4O_MINI,
                temperature=0.7,
                max_tokens=4000  # 增加到4000，给模型更多思考和输出空间
            )
            
            # 提取响应内容
            if hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)
            
            print(f"📄 OpenAI GPT-4o响应内容长度: {len(response_content)} 字符")
            
            # 解析JSON响应
            practice_sentences_data = self._extract_json_from_response(response_content)
            
            if not practice_sentences_data or 'practice_sentences' not in practice_sentences_data:
                raise ValueError("练习句子生成失败：JSON解析错误")
            
            practice_sentences = practice_sentences_data['practice_sentences']
            if not practice_sentences:
                raise ValueError("练习句子生成失败：生成的句子为空")
            
            print(f"✅ 成功生成 {len(practice_sentences)} 个练习句子")
            
            return {
                "practice_sentences": practice_sentences,
                "generated_at": datetime.now().isoformat(),
                "generation_method": "openai_gpt4o_100_coverage"
            }
            
        except Exception as e:
            print(f"❌ 练习句子生成失败: {e}")
            raise ValueError(f"练习句子生成失败：{str(e)}")
    
    def _generate_exercises_from_sentences(self, practice_sentences: list, stage: str) -> dict:
        """基于练习句子生成练习题"""
        try:
            print(f"🎯 基于练习句子生成练习题")
            print(f"   源句子数量: {len(practice_sentences)}")
            
            # 使用基于句子的练习题生成提示词
            chinese_prompt = self.prompt_generator.generate_exercises_from_sentences(
                practice_sentences, stage
            )
            
            print(f"📝 基于句子的练习题提示词长度: {len(chinese_prompt)} 字符")
            
            # 使用OpenAI GPT-4o生成练习题 (增加max_tokens提升成功率)
            response = self.openai_client.generate_content(
                prompt=chinese_prompt,
                model=AIModel.OPENAI_GPT4O_MINI,
                temperature=0.7,
                max_tokens=5000  # 练习题需要更多空间：题目+选项+解析
            )
            
            # 提取响应内容
            if hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)
            
            print(f"📄 OpenAI GPT-4o响应内容长度: {len(response_content)} 字符")
            
            # 解析JSON响应
            practice_exercises_data = self._extract_json_from_response(response_content)
            
            if not practice_exercises_data or 'practice_exercises' not in practice_exercises_data:
                raise ValueError("练习题生成失败：JSON解析错误")
            
            practice_exercises = practice_exercises_data['practice_exercises']
            if not practice_exercises:
                raise ValueError("练习题生成失败：生成的练习题为空")
            
            print(f"✅ 成功生成 {len(practice_exercises)} 道练习题")
            
            return {
                "practice_exercises": practice_exercises,
                "generated_at": datetime.now().isoformat(),
                "generation_method": "openai_gpt4o_from_sentences"
            }
            
        except Exception as e:
            print(f"❌ 练习题生成失败: {e}")
            raise ValueError(f"练习题生成失败：{str(e)}")

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """从AI响应中提取JSON内容"""
        try:
            # 尝试直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # 尝试从markdown代码块中提取
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试查找第一个完整的JSON对象
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        print(f"❌ 无法从响应中提取有效JSON")
        return None



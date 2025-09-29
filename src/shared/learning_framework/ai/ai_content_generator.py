#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI内容生成器
将当日学习单词和语法一起推送给大模型，一次性生成练习语句和练习题
"""

import sys
import os
import json
import random
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 添加AI框架路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 使用绝对路径到AI框架
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))))
ai_framework_path = os.path.join(project_root, 'educational_projects', 'shared', 'ai_framework')
sys.path.append(os.path.abspath(ai_framework_path))

try:
    from src.shared.ai_framework.clients.context7_zhipu_client import Context7ZhipuClient as ZhipuAIClient
except ImportError:
    try:
        from src.shared.ai_framework.clients.zhipu_client import ZhipuAIClient
    except ImportError:
        print("⚠️ 智谱AI客户端未找到，将使用模板生成内容")
        ZhipuAIClient = None

@dataclass
class DailyContentRequest:
    """每日内容生成请求"""
    words: List[Dict[str, Any]]  # 当日学习单词列表
    grammar_topic: str  # 当日语法主题
    grammar_level: str  # 语法级别
    sentence_count: int = 8  # 生成句子数量
    exercise_count: int = 10  # 生成练习题数量
    difficulty: str = "medium"  # 难度级别

@dataclass
class GeneratedContent:
    """生成的内容"""
    sentences: List[Dict[str, Any]]  # 练习句子
    exercises: List[Dict[str, Any]]  # 练习题
    ai_generated: bool = True

class AIContentGenerator:
    """AI内容生成器"""
    
    def __init__(self, config_path: str = None, ai_client=None):
        """初始化AI内容生成器"""
        self.ai_client = ai_client
        self.fallback_mode = True
        self.content_cache = {}  # 内容缓存
        
        # 如果传入了AI客户端，直接使用
        if ai_client:
            self.fallback_mode = False
            print("✅ AI内容生成器使用共享客户端初始化成功")
        # 否则尝试初始化AI客户端
        elif ZhipuAIClient:
            try:
                # 直接使用Context7ZhipuClient，不指定模型，让客户端从配置文件读取默认模型
                self.ai_client = ZhipuAIClient()
                self.fallback_mode = False
                print("✅ AI内容生成器初始化成功")
            except Exception as e:
                print(f"⚠️ AI客户端初始化失败: {e}")
                print("将使用模板生成内容")
                self.fallback_mode = True
        else:
            print("⚠️ 智谱AI客户端未安装，将使用模板生成内容")
            self.fallback_mode = True
    
    def generate_daily_content(self, request: DailyContentRequest) -> GeneratedContent:
        """生成每日学习内容（句子+练习题）"""
        if self.fallback_mode or not self.ai_client:
            return self._generate_template_content(request)
        
        try:
            # 检查缓存
            cache_key = self._get_cache_key(request)
            if cache_key in self.content_cache:
                print(f"📋 使用缓存内容 for {request.grammar_topic}")
                return self.content_cache[cache_key]
            
            # 使用AI生成内容
            content = self._generate_ai_content(request)
            
            # 缓存结果
            self.content_cache[cache_key] = content
            
            return content
        except Exception as e:
            print(f"⚠️ AI生成失败: {e}")
            print("回退到模板生成")
            return self._generate_template_content(request)
    
    def _generate_ai_content(self, request: DailyContentRequest) -> GeneratedContent:
        """使用AI生成内容"""
        try:
            # 构建综合提示词
            prompt = self._build_comprehensive_prompt(request)
            
            # 调用AI生成（使用普通调用，参数从配置文件读取）
            response = self.ai_client.generate_content(
                prompt=prompt
                # system_prompt, temperature, max_tokens 都从配置文件读取
            )
            
            # 解析AI响应
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, dict):
                content = response.get('content', '')
            else:
                content = str(response)
            
            # 如果content为空，尝试从reasoning_content获取
            if not content or content.strip() == "":
                if hasattr(response, 'reasoning_content'):
                    content = response.reasoning_content
                elif isinstance(response, dict):
                    content = response.get('reasoning_content', '')
                print(f"🔍 从reasoning_content获取内容: {len(content)} 字符")
            
            # 如果content仍然为空，尝试从reasoning_content中提取JSON
            if not content or content.strip() == "":
                if hasattr(response, 'reasoning_content') and response.reasoning_content:
                    reasoning_content = response.reasoning_content
                    # 查找JSON部分
                    json_start = reasoning_content.find('{')
                    json_end = reasoning_content.rfind('}')
                    if json_start >= 0 and json_end > json_start:
                        content = reasoning_content[json_start:json_end+1]
                        print(f"🔍 从reasoning_content提取JSON: {len(content)} 字符")
            
            # 如果content仍然为空，尝试从reasoning_content中提取完整的JSON
            if not content or content.strip() == "":
                if hasattr(response, 'reasoning_content') and response.reasoning_content:
                    reasoning_content = response.reasoning_content
                    # 查找```json标记
                    json_start = reasoning_content.find('```json')
                    if json_start >= 0:
                        json_start += 7  # 跳过```json
                        json_end = reasoning_content.find('```', json_start)
                        if json_end > json_start:
                            content = reasoning_content[json_start:json_end].strip()
                            print(f"🔍 从reasoning_content提取```json内容: {len(content)} 字符")
                    else:
                        # 如果没有```json标记，查找JSON部分
                        json_start = reasoning_content.find('{')
                        json_end = reasoning_content.rfind('}')
                        if json_start >= 0 and json_end > json_start:
                            content = reasoning_content[json_start:json_end+1]
                            print(f"🔍 从reasoning_content提取JSON: {len(content)} 字符")
            
            if not content or content.strip() == "":
                print("⚠️ AI返回空内容，回退到模板生成")
                return self._generate_template_content(request)
            
            print(f"🔍 AI返回内容长度: {len(content)} 字符")
            print(f"🔍 内容预览: {content[:200]}...")
            
            # 解析生成的内容
            return self._parse_ai_response(content, request)
            
        except Exception as e:
            print(f"⚠️ AI内容生成失败: {e}")
            print("🔄 回退到模板生成模式")
            return self._generate_template_content(request)
    
    def _build_comprehensive_prompt(self, request: DailyContentRequest) -> str:
        """构建综合提示词"""
        # 准备单词列表
        word_list = []
        for word_data in request.words:
            word_list.append(f"- {word_data['word']}（{word_data.get('meaning', word_data.get('chinese_meaning', ''))}，{word_data['part_of_speech']}）")
        
        word_text = "\n".join(word_list)
        grammar_explanation = self._get_grammar_explanation(request.grammar_topic)
        
        prompt = f"""生成英语练习JSON：

单词：{word_text}
语法：{request.grammar_topic}

要求：每词一句+一道题


JSON格式：
{{
  "sentences": [{{"word": "词", "sentence": "句", "chinese_translation": "译"}}],
  "exercises": [{{"type": "fill_blank", "question": "题", "answer": "答", "explanation": "解"}}]
}}"""
        return prompt
    
    def _parse_ai_response(self, content: str, request: DailyContentRequest) -> GeneratedContent:
        """解析AI响应"""
        try:
            # 清理内容
            cleaned_content = content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            # 如果内容被截断，尝试修复JSON
            if cleaned_content and not cleaned_content.endswith('}'):
                # 查找最后一个完整的句子或练习
                last_complete_sentence = cleaned_content.rfind('},')
                if last_complete_sentence > 0:
                    # 截取到最后一个完整的句子
                    cleaned_content = cleaned_content[:last_complete_sentence + 1]
                    # 添加结束标记
                    if '"sentences"' in cleaned_content and '"exercises"' in cleaned_content:
                        cleaned_content += '], "exercises": []}'
                    elif '"sentences"' in cleaned_content:
                        cleaned_content += ']}'
                    else:
                        cleaned_content += '}'
            
            # 尝试修复常见的JSON格式问题
            cleaned_content = self._fix_json_format(cleaned_content)
            
            # 解析JSON
            if cleaned_content.startswith('{'):
                try:
                    data = json.loads(cleaned_content)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON解析失败: {e}")
                    print(f"内容预览: {cleaned_content[:200]}...")
                    # 尝试提取部分内容
                    return self._extract_partial_content(cleaned_content, request)
                
                # 解析句子
                sentences = []
                for item in data.get('sentences', []):
                    sentence = {
                        "word": item.get('word', ''),
                        "word_meaning": self._get_word_meaning(item.get('word', ''), request.words),
                        "part_of_speech": self._get_part_of_speech_display(self._get_word_part_of_speech(item.get('word', ''), request.words)),
                        "grammar_topic": request.grammar_topic,
                        "sentence": item.get('sentence', ''),
                        "chinese_translation": item.get('chinese_translation', ''),
                        "grammar_explanation": item.get('grammar_explanation', ''),
                        "practice_tips": item.get('practice_tips', ''),
                        "ai_generated": True
                    }
                    sentences.append(sentence)
                
                # 解析练习题
                exercises = []
                for item in data.get('exercises', []):
                    exercise = {
                        "type": item.get('type', 'fill_blank'),
                        "question": item.get('question', ''),
                        "options": item.get('options', []),
                        "answer": item.get('answer', ''),
                        "explanation": item.get('explanation', ''),
                        "ai_generated": True
                    }
                    exercises.append(exercise)
                
                return GeneratedContent(sentences=sentences, exercises=exercises, ai_generated=True)
            else:
                # 回退到模板生成
                return self._generate_template_content(request)
                
        except Exception as e:
            print(f"⚠️ AI响应解析失败: {e}")
            return self._generate_template_content(request)
    
    def _fix_json_format(self, content: str) -> str:
        """修复常见的JSON格式问题"""
        # 移除控制字符（除了换行符和制表符）
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        # 修复JSON数组中的换行问题
        content = re.sub(r'\[\s*\n\s*{', '[{', content)
        content = re.sub(r'}\s*\n\s*\]', '}]', content)
        
        # 修复对象中的换行问题
        content = re.sub(r'{\s*\n\s*"', '{"', content)
        content = re.sub(r'"\s*\n\s*}', '"}', content)
        
        # 修复属性名和值之间的换行
        content = re.sub(r'"\s*\n\s*:', '":', content)
        content = re.sub(r':\s*\n\s*"', ':"', content)
        
        # 修复数组元素之间的换行
        content = re.sub(r'}\s*\n\s*{', '},{', content)
        
        # 修复字符串值中的换行符
        content = re.sub(r'"([^"]*?)\n([^"]*?)"', r'"\1\\n\2"', content)
        
        # 修复缺少引号的键
        content = re.sub(r'(\w+):', r'"\1":', content)
        
        # 修复缺少逗号的情况
        content = re.sub(r'"\s*\n\s*"', '",\n"', content)
        
        # 修复多余的逗号
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        
        # 修复未终止的字符串
        content = re.sub(r'"([^"]*?)\s*$', r'"\1"', content, flags=re.MULTILINE)
        
        return content
    
    def _extract_partial_content(self, content: str, request: DailyContentRequest) -> GeneratedContent:
        """从部分内容中提取句子和练习题"""
        sentences = []
        exercises = []
        
        try:
            # 尝试提取句子
            sentence_matches = re.findall(r'"sentence":\s*"([^"]*)"', content)
            chinese_matches = re.findall(r'"chinese_translation":\s*"([^"]*)"', content)
            word_matches = re.findall(r'"word":\s*"([^"]*)"', content)
            
            for i, (sentence, chinese, word) in enumerate(zip(sentence_matches, chinese_matches, word_matches)):
                if i < len(request.words):
                    word_data = request.words[i]
                    sentences.append({
                        "word": word,
                        "word_meaning": word_data.get('meaning', word_data.get('chinese_meaning', '')),
                        "part_of_speech": self._get_part_of_speech_display(word_data['part_of_speech']),
                        "grammar_topic": request.grammar_topic,
                        "sentence": sentence,
                        "chinese_translation": chinese,
                        "grammar_explanation": self._get_grammar_explanation(request.grammar_topic),
                        "practice_tips": f"多练习{word}的用法",
                        "ai_generated": True
                    })
            
            # 尝试提取练习题
            exercise_matches = re.findall(r'"question":\s*"([^"]*)"', content)
            answer_matches = re.findall(r'"answer":\s*"([^"]*)"', content)
            type_matches = re.findall(r'"type":\s*"([^"]*)"', content)
            
            for i, (question, answer, ex_type) in enumerate(zip(exercise_matches, answer_matches, type_matches)):
                if i < request.exercise_count:
                    exercises.append({
                        "type": ex_type,
                        "question": question,
                        "options": [],
                        "answer": answer,
                        "explanation": f"正确答案是{answer}",
                        "ai_generated": True
                    })
            
            # 如果提取的内容不够，用模板补充
            while len(sentences) < len(request.words):
                word_data = request.words[len(sentences)]
                sentence = self._generate_template_sentence(word_data, request)
                if sentence:
                    sentences.append(sentence)
            
            while len(exercises) < request.exercise_count:
                exercise = self._generate_template_exercise(request)
                if exercise:
                    exercises.append(exercise)
            
            return GeneratedContent(sentences=sentences, exercises=exercises, ai_generated=True)
            
        except Exception as e:
            print(f"⚠️ 部分内容提取失败: {e}")
            return self._generate_template_content(request)
    
    def _get_word_meaning(self, word: str, words: List[Dict[str, Any]]) -> str:
        """获取单词中文意思"""
        for word_data in words:
            if word_data['word'] == word:
                return word_data.get('meaning', word_data.get('chinese_meaning', word))
        return word
    
    def _get_word_part_of_speech(self, word: str, words: List[Dict[str, Any]]) -> str:
        """获取单词词性"""
        for word_data in words:
            if word_data['word'] == word:
                return word_data['part_of_speech']
        return 'noun'
    
    def _get_part_of_speech_display(self, part_of_speech: str) -> str:
        """获取词性显示"""
        pos_map = {
            "noun": "名词 (n.)",
            "verb": "动词 (v.)",
            "adjective": "形容词 (adj.)",
            "adverb": "副词 (adv.)",
            "pronoun": "代词 (pron.)",
            "preposition": "介词 (prep.)",
            "conjunction": "连词 (conj.)",
            "interjection": "感叹词 (interj.)",
            "article": "冠词 (art.)",
            "numeral": "数词 (num.)",
            "determiner": "限定词 (det.)"
        }
        return pos_map.get(part_of_speech, f"{part_of_speech}")
    
    def _get_grammar_explanation(self, grammar_topic: str) -> str:
        """获取语法说明"""
        explanations = {
            "be动词用法": "be动词用于表示状态、身份、特征等",
            "一般现在时-基础用法": "一般现在时表示经常性、习惯性的动作或状态",
            "一般现在时-第三人称单数": "第三人称单数时，动词要加-s或-es",
            "一般现在时-否定形式": "否定形式用don't/doesn't + 动词原形",
            "一般现在时-疑问形式": "疑问形式用Do/Does + 主语 + 动词原形",
            "现在进行时-基础用法": "现在进行时表示正在进行的动作",
            "一般过去时-基础用法": "一般过去时表示过去发生的动作或状态",
            "现在完成时-基础用法": "现在完成时表示过去发生但对现在有影响的动作",
            "名词单复数-基础规则": "名词复数通常在词尾加-s或-es",
            "形容词比较级-基础规则": "形容词比较级用于比较两个事物的程度"
        }
        return explanations.get(grammar_topic, "语法规则说明")
    
    def _generate_template_content(self, request: DailyContentRequest) -> GeneratedContent:
        """使用模板生成内容（回退方案）"""
        sentences = []
        exercises = []
        
        # 生成句子
        for word_data in request.words:
            sentence = self._generate_template_sentence(word_data, request)
            if sentence:
                sentences.append(sentence)
        
        # 生成练习题
        for i in range(request.exercise_count):
            exercise = self._generate_template_exercise(request)
            if exercise:
                exercises.append(exercise)
        
        return GeneratedContent(sentences=sentences, exercises=exercises, ai_generated=False)
    
    def _generate_template_sentence(self, word_data: Dict[str, Any], request: DailyContentRequest) -> Dict[str, Any]:
        """使用模板生成句子"""
        word = word_data['word']
        word_meaning = word_data.get('meaning', word_data.get('chinese_meaning', ''))
        part_of_speech = word_data['part_of_speech']
        grammar_topic = request.grammar_topic
        
        # 根据语法主题生成句子
        sentence, chinese = self._generate_sentence_by_grammar(word, word_meaning, part_of_speech, grammar_topic)
        
        if not sentence:
            return None
        
        return {
            "word": word,
            "word_meaning": word_meaning,
            "part_of_speech": self._get_part_of_speech_display(part_of_speech),
            "grammar_topic": grammar_topic,
            "sentence": sentence,
            "chinese_translation": chinese,
            "grammar_explanation": self._get_grammar_explanation(grammar_topic),
            "practice_tips": f"多练习{word}的用法",
            "ai_generated": False
        }
    
    def _generate_sentence_by_grammar(self, word: str, word_meaning: str, part_of_speech: str, grammar_topic: str) -> tuple:
        """根据语法主题生成句子"""
        if "be动词用法" in grammar_topic:
            if part_of_speech == "adjective":
                return f"I am {word} today.", f"我今天{word_meaning}。"
            elif part_of_speech == "noun":
                return f"This is a {word}.", f"这是一个{word_meaning}。"
            else:
                return f"I am {word}.", f"我是{word_meaning}。"
        
        elif "一般现在时" in grammar_topic:
            if "第三人称单数" in grammar_topic:
                if part_of_speech == "verb":
                    return f"He {word}s every day.", f"他每天{word_meaning}。"
                else:
                    return f"He likes {word}.", f"他喜欢{word_meaning}。"
            else:
                if part_of_speech == "verb":
                    return f"I {word} every day.", f"我每天{word_meaning}。"
                else:
                    return f"I like {word}.", f"我喜欢{word_meaning}。"
        
        elif "现在进行时" in grammar_topic:
            if part_of_speech == "verb":
                return f"I am {word}ing now.", f"我现在正在{word_meaning}。"
            else:
                return f"I am looking at the {word}.", f"我正在看{word_meaning}。"
        
        elif "一般过去时" in grammar_topic:
            if part_of_speech == "verb":
                return f"I {word}ed yesterday.", f"我昨天{word_meaning}了。"
            else:
                return f"I saw a {word} yesterday.", f"我昨天看到了一个{word_meaning}。"
        
        elif "名词单复数" in grammar_topic:
            if part_of_speech == "noun":
                return f"There are many {word}s here.", f"这里有很多{word_meaning}。"
            else:
                return f"I like {word} things.", f"我喜欢{word_meaning}的事物。"
        
        else:
            # 默认句子
            if part_of_speech == "verb":
                return f"I {word} every day.", f"我每天{word_meaning}。"
            elif part_of_speech == "noun":
                return f"This is a {word}.", f"这是一个{word_meaning}。"
            elif part_of_speech == "adjective":
                return f"I am {word}.", f"我很{word_meaning}。"
            else:
                return f"I like {word}.", f"我喜欢{word_meaning}。"
    
    def _generate_template_exercise(self, request: DailyContentRequest) -> Dict[str, Any]:
        """使用模板生成练习题"""
        exercise_types = ["fill_blank", "translation", "choice", "sentence_completion"]
        exercise_type = random.choice(exercise_types)
        
        # 检查是否有单词数据
        if not request.words:
            return {
                "type": "fill_blank",
                "question": "请完成句子：I am learning English.",
                "options": [],
                "answer": "learning",
                "explanation": "这里需要填入动词",
                "ai_generated": False
            }
        
        # 随机选择一个单词
        word_data = random.choice(request.words)
        word = word_data['word']
        word_meaning = word_data.get('meaning', word_data.get('chinese_meaning', ''))
        
        if exercise_type == "fill_blank":
            return {
                "type": "fill_blank",
                "question": f"请填入正确的单词：I like _____. (我喜欢{word_meaning}。)",
                "options": [],
                "answer": word,
                "explanation": f"这里需要填入名词{word}",
                "ai_generated": False
            }
        elif exercise_type == "translation":
            return {
                "type": "translation",
                "question": f"请翻译：{word_meaning}",
                "options": [],
                "answer": word,
                "explanation": f"{word_meaning}的英文是{word}",
                "ai_generated": False
            }
        elif exercise_type == "choice":
            return {
                "type": "choice",
                "question": f"选择正确的单词：我喜欢{word_meaning}。",
                "options": [word, f"{word}s", f"{word}ing", f"{word}ed"],
                "answer": word,
                "explanation": f"正确答案是{word}",
                "ai_generated": False
            }
        else:  # sentence_completion
            return {
                "type": "sentence_completion",
                "question": f"完成句子：I _____ every day.",
                "options": [],
                "answer": word,
                "explanation": f"根据语法规则，这里应该填入{word}",
                "ai_generated": False
            }
    
    def _get_cache_key(self, request: DailyContentRequest) -> str:
        """生成缓存键"""
        words_key = "_".join([f"{w['word']}_{w['part_of_speech']}" for w in request.words])
        return f"{request.grammar_topic}_{request.grammar_level}_{words_key}_{request.exercise_count}"


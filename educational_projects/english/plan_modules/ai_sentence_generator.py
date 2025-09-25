#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI句子生成器
使用大模型生成结合当日学习单词和语法的练习句子
"""

import sys
import os
import json
import random
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 添加AI框架路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai_framework'))

try:
    from zhipu_ai_client import ZhipuAIClient
except ImportError:
    print("⚠️ 智谱AI客户端未找到，将使用模板生成句子")
    ZhipuAIClient = None

@dataclass
class SentenceRequest:
    """句子生成请求"""
    words: List[Dict[str, Any]]  # 当日学习单词列表
    grammar_topic: str  # 当日语法主题
    grammar_level: str  # 语法级别
    sentence_count: int = 8  # 生成句子数量
    difficulty: str = "medium"  # 难度级别

@dataclass
class GeneratedSentence:
    """生成的句子"""
    word: str
    word_meaning: str
    part_of_speech: str
    grammar_topic: str
    sentence: str
    chinese_translation: str
    grammar_explanation: str
    practice_tips: str
    ai_generated: bool = True

class AISentenceGenerator:
    """AI句子生成器"""
    
    def __init__(self, config_path: str = "../../llm_framework/config.json"):
        """初始化AI句子生成器"""
        self.ai_client = None
        self.fallback_mode = True
        self.sentence_cache = {}  # 句子缓存
        self.batch_size = 4  # 批量生成大小
        
        # 尝试初始化AI客户端
        if ZhipuAIClient:
            try:
                self.ai_client = ZhipuAIClient(config_path)
                self.fallback_mode = False
                print("✅ AI句子生成器初始化成功")
            except Exception as e:
                print(f"⚠️ AI客户端初始化失败: {e}")
                print("将使用模板生成句子")
                self.fallback_mode = True
        else:
            print("⚠️ 智谱AI客户端未安装，将使用模板生成句子")
            self.fallback_mode = True
    
    def generate_sentences(self, request: SentenceRequest) -> List[GeneratedSentence]:
        """生成练习句子"""
        if self.fallback_mode or not self.ai_client:
            return self._generate_template_sentences(request)
        
        try:
            # 检查缓存
            cache_key = self._get_cache_key(request)
            if cache_key in self.sentence_cache:
                print(f"📋 使用缓存句子 for {request.grammar_topic}")
                return self.sentence_cache[cache_key]
            
            # 批量生成句子
            sentences = self._generate_ai_sentences_batch(request)
            
            # 缓存结果
            self.sentence_cache[cache_key] = sentences
            
            return sentences
        except Exception as e:
            print(f"⚠️ AI生成失败: {e}")
            print("回退到模板生成")
            return self._generate_template_sentences(request)
    
    def _generate_ai_sentences(self, request: SentenceRequest) -> List[GeneratedSentence]:
        """使用AI生成句子"""
        sentences = []
        
        # 为每个单词生成句子
        for word_data in request.words:
            try:
                sentence = self._generate_single_ai_sentence(word_data, request)
                if sentence:
                    sentences.append(sentence)
            except Exception as e:
                print(f"⚠️ 生成单词 {word_data.get('word', 'unknown')} 的句子失败: {e}")
                # 回退到模板生成
                sentence = self._generate_template_sentence(word_data, request)
                if sentence:
                    sentences.append(sentence)
        
        return sentences
    
    def _generate_ai_sentences_batch(self, request: SentenceRequest) -> List[GeneratedSentence]:
        """批量生成AI句子（优化性能）"""
        sentences = []
        words = request.words
        
        # 分批处理单词
        for i in range(0, len(words), self.batch_size):
            batch_words = words[i:i + self.batch_size]
            
            if len(batch_words) == 1:
                # 单个单词，使用原有方法
                sentence = self._generate_single_ai_sentence(batch_words[0], request)
                if sentence:
                    sentences.append(sentence)
            else:
                # 批量生成
                batch_sentences = self._generate_batch_ai_sentences(batch_words, request)
                sentences.extend(batch_sentences)
        
        return sentences
    
    def _generate_batch_ai_sentences(self, words: List[Dict[str, Any]], request: SentenceRequest) -> List[GeneratedSentence]:
        """批量生成多个单词的句子"""
        try:
            # 构建批量提示词
            prompt = self._build_batch_sentence_prompt(words, request)
            
            # 调用AI生成
            response = self.ai_client.generate_content(
                prompt=prompt,
                system_prompt="你是一个专业的英语教学助手，擅长生成自然、有意义的英语练习句子。",
                temperature=0.7,
                max_tokens=2000
            )
            
            # 解析AI响应
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, dict):
                content = response.get('content', '')
            else:
                content = str(response)
            
            if not content:
                return []
            
            # 解析批量响应
            sentences = self._parse_batch_ai_response(content, words, request)
            return sentences
            
        except Exception as e:
            print(f"⚠️ 批量AI生成失败: {e}")
            # 回退到单个生成
            sentences = []
            for word_data in words:
                sentence = self._generate_single_ai_sentence(word_data, request)
                if sentence:
                    sentences.append(sentence)
            return sentences
    
    def _build_batch_sentence_prompt(self, words: List[Dict[str, Any]], request: SentenceRequest) -> str:
        """构建批量句子生成提示词"""
        word_list = []
        for word_data in words:
            word_list.append(f"- {word_data['word']}（{word_data['chinese_meaning']}，{word_data['part_of_speech']}）")
        
        word_text = "\n".join(word_list)
        
        prompt = f"""请为英语学习生成练习句子。

单词列表：
{word_text}

语法：{request.grammar_topic}

要求：
1. 为每个单词生成一个包含该单词的句子
2. 句子必须体现"{request.grammar_topic}"语法规则
3. 句子自然有意义，适合练习

请返回JSON数组格式：
[
  {{"word": "单词1", "sentence": "英语句子1", "chinese_translation": "中文翻译1", "grammar_explanation": "语法说明1", "practice_tips": "练习建议1"}},
  {{"word": "单词2", "sentence": "英语句子2", "chinese_translation": "中文翻译2", "grammar_explanation": "语法说明2", "practice_tips": "练习建议2"}}
]"""
        return prompt
    
    def _parse_batch_ai_response(self, content: str, words: List[Dict[str, Any]], request: SentenceRequest) -> List[GeneratedSentence]:
        """解析批量AI响应"""
        try:
            # 清理内容
            cleaned_content = content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            # 解析JSON数组
            if cleaned_content.startswith('['):
                data_list = json.loads(cleaned_content)
                sentences = []
                
                for item in data_list:
                    word = item.get('word', '')
                    word_data = next((w for w in words if w['word'] == word), words[0])
                    
                    sentence = GeneratedSentence(
                        word=word,
                        word_meaning=word_data['chinese_meaning'],
                        part_of_speech=self._get_part_of_speech_display(word_data['part_of_speech']),
                        grammar_topic=request.grammar_topic,
                        sentence=item.get('sentence', ''),
                        chinese_translation=item.get('chinese_translation', ''),
                        grammar_explanation=item.get('grammar_explanation', ''),
                        practice_tips=item.get('practice_tips', ''),
                        ai_generated=True
                    )
                    sentences.append(sentence)
                
                return sentences
            else:
                # 回退到单个解析
                return []
                
        except Exception as e:
            print(f"⚠️ 批量响应解析失败: {e}")
            return []
    
    def _get_cache_key(self, request: SentenceRequest) -> str:
        """生成缓存键"""
        words_key = "_".join([f"{w['word']}_{w['part_of_speech']}" for w in request.words])
        return f"{request.grammar_topic}_{request.grammar_level}_{words_key}"
    
    def _generate_single_ai_sentence(self, word_data: Dict[str, Any], request: SentenceRequest) -> Optional[GeneratedSentence]:
        """为单个单词生成AI句子"""
        word = word_data.get('word', '')
        word_meaning = word_data.get('chinese_meaning', '')
        part_of_speech = word_data.get('part_of_speech', '')
        
        try:
            # 构建提示词
            prompt = self._build_sentence_prompt(word, word_meaning, part_of_speech, request)
            # 调用AI生成
            response = self.ai_client.generate_content(
                prompt=prompt,
                system_prompt="你是一个专业的英语教学助手，擅长生成自然、有意义的英语练习句子。",
                temperature=0.7,
                max_tokens=1000
            )
            
            # 解析AI响应
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, dict):
                content = response.get('content', '')
            else:
                content = str(response)
            
            if not content:
                return None
            
            # 解析生成的句子
            sentence_data = self._parse_ai_response(content, word, word_meaning, part_of_speech, request)
            return sentence_data
            
        except Exception as e:
            print(f"⚠️ AI生成句子失败 for {word}: {e}")
            return None
    
    def _build_sentence_prompt(self, word: str, word_meaning: str, part_of_speech: str, request: SentenceRequest) -> str:
        """构建句子生成提示词"""
        grammar_explanation = self._get_grammar_explanation(request.grammar_topic)
        
        prompt = f"""请为英语学习生成一个练习句子。

单词：{word}（{word_meaning}，{part_of_speech}）
语法：{request.grammar_topic}

要求：
1. 句子包含单词"{word}"
2. 体现"{request.grammar_topic}"语法规则
3. 句子自然有意义

请返回JSON格式：
{{"sentence": "英语句子", "chinese_translation": "中文翻译", "grammar_explanation": "语法说明", "practice_tips": "练习建议"}}"""
        return prompt
    
    def _parse_ai_response(self, content: str, word: str, word_meaning: str, part_of_speech: str, request: SentenceRequest) -> Optional[GeneratedSentence]:
        """解析AI响应"""
        try:
            # 清理内容，移除代码块标记
            cleaned_content = content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # 移除 ```json
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # 移除 ```
            cleaned_content = cleaned_content.strip()
            
            # 尝试解析JSON
            if cleaned_content.startswith('{'):
                try:
                    data = json.loads(cleaned_content)
                except json.JSONDecodeError:
                    # 尝试提取部分JSON
                    data = self._extract_partial_json(cleaned_content)
                    if not data:
                        data = self._extract_sentence_info(content)
            else:
                # 如果不是JSON格式，尝试提取信息
                data = self._extract_sentence_info(content)
            
            return GeneratedSentence(
                word=word,
                word_meaning=word_meaning,
                part_of_speech=self._get_part_of_speech_display(part_of_speech),
                grammar_topic=request.grammar_topic,
                sentence=data.get('sentence', ''),
                chinese_translation=data.get('chinese_translation', ''),
                grammar_explanation=data.get('grammar_explanation', ''),
                practice_tips=data.get('practice_tips', ''),
                ai_generated=True
            )
        except Exception as e:
            print(f"⚠️ 解析AI响应失败: {e}")
            return None
    
    def _extract_partial_json(self, content: str) -> Dict[str, str]:
        """从部分JSON中提取信息"""
        data = {}
        
        # 尝试提取sentence
        sentence_match = re.search(r'"sentence":\s*"([^"]*)"', content)
        if sentence_match:
            data['sentence'] = sentence_match.group(1)
        
        # 尝试提取chinese_translation
        translation_match = re.search(r'"chinese_translation":\s*"([^"]*)"', content)
        if translation_match:
            data['chinese_translation'] = translation_match.group(1)
        
        # 尝试提取grammar_explanation
        explanation_match = re.search(r'"grammar_explanation":\s*"([^"]*)"', content)
        if explanation_match:
            data['grammar_explanation'] = explanation_match.group(1)
        
        # 尝试提取practice_tips
        tips_match = re.search(r'"practice_tips":\s*"([^"]*)"', content)
        if tips_match:
            data['practice_tips'] = tips_match.group(1)
        
        return data
    
    def _extract_sentence_info(self, content: str) -> Dict[str, str]:
        """从非JSON格式中提取句子信息"""
        lines = content.strip().split('\n')
        data = {}
        
        for line in lines:
            if 'sentence:' in line.lower():
                data['sentence'] = line.split(':', 1)[1].strip()
            elif 'translation:' in line.lower() or '翻译:' in line:
                data['chinese_translation'] = line.split(':', 1)[1].strip()
            elif 'explanation:' in line.lower() or '说明:' in line:
                data['grammar_explanation'] = line.split(':', 1)[1].strip()
            elif 'tips:' in line.lower() or '建议:' in line:
                data['practice_tips'] = line.split(':', 1)[1].strip()
        
        return data
    
    def _generate_template_sentences(self, request: SentenceRequest) -> List[GeneratedSentence]:
        """使用模板生成句子（回退方案）"""
        sentences = []
        
        for word_data in request.words:
            sentence = self._generate_template_sentence(word_data, request)
            if sentence:
                sentences.append(sentence)
        
        return sentences
    
    def _generate_template_sentence(self, word_data: Dict[str, Any], request: SentenceRequest) -> Optional[GeneratedSentence]:
        """使用模板生成单个句子"""
        word = word_data.get('word', '')
        word_meaning = word_data.get('chinese_meaning', '')
        part_of_speech = word_data.get('part_of_speech', '')
        grammar_topic = request.grammar_topic
        
        # 根据语法主题生成句子
        sentence, chinese = self._generate_sentence_by_grammar(word, word_meaning, part_of_speech, grammar_topic)
        
        if not sentence:
            return None
        
        return GeneratedSentence(
            word=word,
            word_meaning=word_meaning,
            part_of_speech=self._get_part_of_speech_display(part_of_speech),
            grammar_topic=grammar_topic,
            sentence=sentence,
            chinese_translation=chinese,
            grammar_explanation=self._get_grammar_explanation(grammar_topic),
            practice_tips=self._get_practice_tips(word, part_of_speech, grammar_topic),
            ai_generated=False
        )
    
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
            elif "否定形式" in grammar_topic:
                if part_of_speech == "verb":
                    return f"I don't {word} on weekends.", f"我周末不{word_meaning}。"
                else:
                    return f"I don't like {word}.", f"我不喜欢{word_meaning}。"
            elif "疑问形式" in grammar_topic:
                if part_of_speech == "verb":
                    return f"Do you {word} in the morning?", f"你早上{word_meaning}吗？"
                else:
                    return f"Do you like {word}?", f"你喜欢{word_meaning}吗？"
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
        
        elif "现在完成时" in grammar_topic:
            if part_of_speech == "verb":
                return f"I have {word}ed before.", f"我以前{word_meaning}过。"
            else:
                return f"I have seen the {word}.", f"我见过{word_meaning}。"
        
        elif "名词单复数" in grammar_topic:
            if part_of_speech == "noun":
                return f"There are many {word}s here.", f"这里有很多{word_meaning}。"
            else:
                return f"I like {word} things.", f"我喜欢{word_meaning}的事物。"
        
        elif "形容词比较级" in grammar_topic:
            if part_of_speech == "adjective":
                return f"This is {word}er than that.", f"这个比那个更{word_meaning}。"
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
    
    def _get_practice_tips(self, word: str, part_of_speech: str, grammar_topic: str) -> str:
        """获取练习建议"""
        tips = {
            "be动词用法": f"注意be动词与{word}的搭配使用",
            "一般现在时-基础用法": f"练习{word}在一般现在时中的用法",
            "一般现在时-第三人称单数": f"注意{word}在第三人称单数时的变化",
            "现在进行时-基础用法": f"练习{word}的现在分词形式",
            "一般过去时-基础用法": f"练习{word}的过去式变化",
            "名词单复数-基础规则": f"练习{word}的复数形式",
            "形容词比较级-基础规则": f"练习{word}的比较级和最高级"
        }
        return tips.get(grammar_topic, f"多练习{word}的用法")
    
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

def test_ai_sentence_generator():
    """测试AI句子生成器"""
    generator = AISentenceGenerator()
    
    # 测试数据
    request = SentenceRequest(
        words=[
            {"word": "apple", "chinese_meaning": "苹果", "part_of_speech": "noun"},
            {"word": "run", "chinese_meaning": "跑步", "part_of_speech": "verb"},
            {"word": "happy", "chinese_meaning": "快乐的", "part_of_speech": "adjective"}
        ],
        grammar_topic="一般现在时-基础用法",
        grammar_level="elementary",
        sentence_count=3
    )
    
    # 生成句子
    sentences = generator.generate_sentences(request)
    
    print("=== AI句子生成器测试 ===")
    for i, sentence in enumerate(sentences, 1):
        print(f"\n句子 {i}:")
        print(f"单词: {sentence.word} - {sentence.word_meaning}")
        print(f"词性: {sentence.part_of_speech}")
        print(f"语法: {sentence.grammar_topic}")
        print(f"句子: {sentence.sentence}")
        print(f"翻译: {sentence.chinese_translation}")
        print(f"说明: {sentence.grammar_explanation}")
        print(f"建议: {sentence.practice_tips}")
        print(f"AI生成: {sentence.ai_generated}")

if __name__ == "__main__":
    test_ai_sentence_generator()

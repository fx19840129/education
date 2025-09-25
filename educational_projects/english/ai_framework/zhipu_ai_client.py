#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱AI客户端
基于GLM-4.5模型的内容生成接口
"""

import json
import requests
import time
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os

@dataclass
class AIResponse:
    """AI响应数据类"""
    content: str
    usage: Dict[str, int]
    model: str
    success: bool
    error_message: Optional[str] = None

class ZhipuAIClient:
    """智谱AI客户端"""
    
    def __init__(self, config_path: str = None):
        """
        初始化智谱AI客户端
        
        Args:
            config_path: 配置文件路径，默认使用项目根目录的配置
        """
        if config_path is None:
            # 使用项目根目录的配置
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'llm_framework', 'config.json')
        
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        
        # API配置
        self.base_url = self.config["llm_config"]["base_url"]
        self.api_key = self.config["llm_config"]["api_key"] 
        self.model = self.config["llm_config"]["model"]
        self.timeout = self.config["llm_config"]["timeout"]
        self.max_retries = self.config["llm_config"]["max_retries"]
        self.default_temperature = self.config["llm_config"]["temperature"]
        self.default_max_tokens = self.config["llm_config"]["max_tokens"]
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"加载配置失败: {e}")
    
    def _make_request(self, messages: List[Dict[str, str]], 
                     temperature: float = None, 
                     max_tokens: int = None) -> AIResponse:
        """发送API请求"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.default_temperature,
            "max_tokens": max_tokens or self.default_max_tokens,
            "stream": False
        }
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    url, 
                    headers=headers, 
                    json=payload, 
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        usage = data.get("usage", {})
                        
                        return AIResponse(
                            content=content,
                            usage=usage,
                            model=self.model,
                            success=True
                        )
                    else:
                        return AIResponse(
                            content="",
                            usage={},
                            model=self.model,
                            success=False,
                            error_message="响应格式错误"
                        )
                else:
                    error_msg = f"API请求失败，状态码: {response.status_code}"
                    if attempt == self.max_retries - 1:
                        return AIResponse(
                            content="",
                            usage={},
                            model=self.model,
                            success=False,
                            error_message=error_msg
                        )
                    
                    # 重试前等待
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                error_msg = f"请求异常: {str(e)}"
                if attempt == self.max_retries - 1:
                    return AIResponse(
                        content="",
                        usage={},
                        model=self.model,
                        success=False,
                        error_message=error_msg
                    )
                
                # 重试前等待
                time.sleep(2 ** attempt)
        
        return AIResponse(
            content="",
            usage={},
            model=self.model,
            success=False,
            error_message="达到最大重试次数"
        )
    
    def generate_content(self, prompt: str, 
                        system_prompt: str = None,
                        temperature: float = None, 
                        max_tokens: int = None) -> AIResponse:
        """
        生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数（0-1）
            max_tokens: 最大生成tokens数
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self._make_request(messages, temperature, max_tokens)
    
    def generate_educational_content(self, word: str, word_meaning: str, 
                                   part_of_speech: str, grammar_topic: str,
                                   content_type: str = "sentence",
                                   difficulty: str = "medium") -> AIResponse:
        """
        生成教育内容（例句、练习题等）
        
        Args:
            word: 目标单词
            word_meaning: 单词中文含义
            part_of_speech: 词性
            grammar_topic: 语法主题
            content_type: 内容类型 (sentence/exercise/explanation)
            difficulty: 难度级别 (easy/medium/hard)
        """
        
        if content_type == "sentence":
            system_prompt = """你是一个专业的英语教育专家，擅长为中小学生创造有趣、实用的英语学习内容。
你的任务是根据给定的单词和语法主题，生成符合以下要求的例句：
1. 语法正确，符合指定的语法主题
2. 包含目标单词并突出其用法
3. 适合中小学生理解，贴近生活场景
4. 富有趣味性，能激发学习兴趣
5. 提供准确的中文翻译"""
            
            prompt = f"""请为以下信息生成一个优质的英语例句：
- 目标单词：{word} ({word_meaning})
- 词性：{part_of_speech}
- 语法主题：{grammar_topic}
- 难度级别：{difficulty}

要求：
1. 生成一个包含目标单词的英语句子
2. 句子必须体现指定的语法主题
3. 提供准确的中文翻译
4. 句子要生动有趣，适合学生记忆

请按以下格式返回：
英语句子：[生成的英语句子]
中文翻译：[对应的中文翻译]"""

        elif content_type == "exercise":
            system_prompt = """你是一个专业的英语练习题设计专家，擅长为中小学生设计高质量的英语练习题。
你的任务是根据给定的单词和语法主题，生成符合教学要求的练习题。"""
            
            prompt = f"""请为以下信息生成一道英语练习题：
- 目标单词：{word} ({word_meaning})
- 词性：{part_of_speech} 
- 语法主题：{grammar_topic}
- 难度级别：{difficulty}

要求：
1. 题目要突出目标单词的用法
2. 体现指定的语法主题
3. 适合中小学生水平
4. 包含答案和解释

请按以下格式返回：
题目：[练习题题目]
答案：[正确答案]
解释：[答案解释]"""

        else:  # explanation
            system_prompt = """你是一个专业的英语语法教学专家，擅长用简单易懂的方式解释英语语法知识。"""
            
            prompt = f"""请为以下语法主题生成一个简洁的解释：
- 语法主题：{grammar_topic}
- 结合单词：{word} ({word_meaning})
- 难度级别：{difficulty}

要求：
1. 解释要通俗易懂，适合中小学生
2. 结合给定单词举例说明
3. 重点突出语法规则
4. 篇幅控制在100字以内

请按以下格式返回：
语法解释：[简洁的语法解释]
举例说明：[使用目标单词的例子]"""
        
        return self.generate_content(prompt, system_prompt, temperature=0.7)
    
    def validate_content(self, content: str, word: str, 
                        grammar_topic: str) -> AIResponse:
        """
        验证生成内容的质量
        
        Args:
            content: 要验证的内容
            word: 目标单词
            grammar_topic: 语法主题
        """
        system_prompt = """你是一个专业的英语教育内容质量检查专家。
你的任务是评估给定的英语学习内容是否符合教育标准。"""
        
        prompt = f"""请检查以下英语学习内容的质量：

内容：{content}
目标单词：{word}
语法主题：{grammar_topic}

请从以下维度进行评估（评分0-10）：
1. 语法正确性
2. 单词使用准确性
3. 语法主题符合度
4. 教育适用性
5. 整体质量

请按以下格式返回：
语法正确性：[评分]/10
单词使用：[评分]/10
语法符合度：[评分]/10
教育适用性：[评分]/10
整体评分：[评分]/10
改进建议：[具体的改进建议]"""
        
        return self.generate_content(prompt, system_prompt, temperature=0.3)
    
    def get_cache_key(self, prompt: str, system_prompt: str = None) -> str:
        """生成缓存键"""
        content = f"{system_prompt or ''}{prompt}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

# 全局AI客户端实例
ai_client = ZhipuAIClient()

if __name__ == "__main__":
    # 测试AI客户端
    print("测试智谱AI客户端...")
    
    # 测试基础内容生成
    response = ai_client.generate_content("请用简单的话介绍一下人工智能。")
    print(f"基础测试 - 成功: {response.success}")
    if response.success:
        print(f"生成内容: {response.content[:100]}...")
        print(f"Token使用: {response.usage}")
    else:
        print(f"错误: {response.error_message}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试教育内容生成
    response = ai_client.generate_educational_content(
        word="apple", 
        word_meaning="苹果", 
        part_of_speech="noun",
        grammar_topic="一般现在时", 
        content_type="sentence"
    )
    print(f"教育内容测试 - 成功: {response.success}")
    if response.success:
        print(f"生成例句: {response.content}")
    else:
        print(f"错误: {response.error_message}")

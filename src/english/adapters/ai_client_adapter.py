"""
AI客户端适配器
将现有的AI客户端适配到新的接口
"""

import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加路径以导入现有AI客户端
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.shared.infrastructure.di.interfaces import (
    IAIClient, GenerationRequest, GenerationResult, ContentType, DifficultyLevel
)
from src.shared.ai_framework.clients.zhipu_client import ZhipuAIClient, AIResponse


class ZhipuAIClientAdapter(IAIClient):
    """智谱AI客户端适配器"""
    
    def __init__(self, config_path: str = None):
        """初始化适配器"""
        self.zhipu_client = ZhipuAIClient(config_path)
    
    def generate_content(self, request: GenerationRequest) -> GenerationResult:
        """生成内容"""
        try:
            # 构建提示词
            prompt = self._build_prompt(request)
            
            # 调用智谱AI
            response = self.zhipu_client.generate_content(prompt)
            
            if response.success:
                # 解析响应内容
                content = self._parse_response(response.content, request)
                return GenerationResult(
                    success=True,
                    content=content,
                    metadata={
                        "model": response.model,
                        "usage": response.usage
                    }
                )
            else:
                return GenerationResult(
                    success=False,
                    content=[],
                    error_message=response.error_message
                )
                
        except Exception as e:
            return GenerationResult(
                success=False,
                content=[],
                error_message=f"AI客户端调用失败: {str(e)}"
            )
    
    def generate_sentence(self, words: List[str], difficulty: str = "elementary") -> List[Dict[str, Any]]:
        """生成句子"""
        try:
            # 构建句子生成提示词
            prompt = self._build_sentence_prompt(words, difficulty)
            
            # 调用智谱AI
            response = self.zhipu_client.generate_content(prompt)
            
            if response.success:
                # 解析句子
                sentences = self._parse_sentences(response.content, words)
                return sentences
            else:
                return []
                
        except Exception as e:
            print(f"生成句子失败: {e}")
            return []
    
    def generate_exercise(self, topic: str, difficulty: str = "elementary", count: int = 5) -> List[Dict[str, Any]]:
        """生成练习"""
        try:
            # 构建练习生成提示词
            prompt = self._build_exercise_prompt(topic, difficulty, count)
            
            # 调用智谱AI
            response = self.zhipu_client.generate_content(prompt)
            
            if response.success:
                # 解析练习
                exercises = self._parse_exercises(response.content)
                return exercises
            else:
                return []
                
        except Exception as e:
            print(f"生成练习失败: {e}")
            return []
    
    def _build_prompt(self, request: GenerationRequest) -> str:
        """构建提示词"""
        if request.content_type == ContentType.WORD:
            return f"请为{request.difficulty.value}级别生成{request.count}个关于'{request.topic}'的英语单词，包含中文释义、词性、例句。"
        elif request.content_type == ContentType.GRAMMAR:
            return f"请为{request.difficulty.value}级别生成{request.count}个关于'{request.topic}'的英语语法点，包含规则、例句、练习。"
        elif request.content_type == ContentType.EXERCISE:
            return f"请为{request.difficulty.value}级别生成{request.count}个关于'{request.topic}'的英语练习，包含选择题、填空题。"
        elif request.content_type == ContentType.SENTENCE:
            return f"请为{request.difficulty.value}级别生成{request.count}个关于'{request.topic}'的英语句子，包含中文翻译。"
        else:
            return f"请为{request.difficulty.value}级别生成{request.count}个关于'{request.topic}'的英语学习内容。"
    
    def _build_sentence_prompt(self, words: List[str], difficulty: str) -> str:
        """构建句子生成提示词"""
        words_str = ", ".join(words)
        return f"请为{difficulty}级别生成包含以下单词的英语句子：{words_str}。每个单词生成一个句子，包含中文翻译。"
    
    def _build_exercise_prompt(self, topic: str, difficulty: str, count: int) -> str:
        """构建练习生成提示词"""
        return f"请为{difficulty}级别生成{count}个关于'{topic}'的英语练习，包含选择题、填空题、翻译题。"
    
    def _parse_response(self, content: str, request: GenerationRequest) -> List[Dict[str, Any]]:
        """解析AI响应"""
        try:
            # 尝试解析JSON
            import json
            data = json.loads(content)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'content' in data:
                return data['content']
            else:
                return [{"content": content, "type": request.content_type.value}]
        except:
            # 如果解析失败，返回原始内容
            return [{"content": content, "type": request.content_type.value}]
    
    def _parse_sentences(self, content: str, words: List[str]) -> List[Dict[str, Any]]:
        """解析句子"""
        try:
            import json
            data = json.loads(content)
            if isinstance(data, list):
                return data
            else:
                return [{"sentence": content, "translation": "", "words": words}]
        except:
            return [{"sentence": content, "translation": "", "words": words}]
    
    def _parse_exercises(self, content: str) -> List[Dict[str, Any]]:
        """解析练习"""
        try:
            import json
            data = json.loads(content)
            if isinstance(data, list):
                return data
            else:
                return [{"question": content, "type": "exercise"}]
        except:
            return [{"question": content, "type": "exercise"}]
    
    def is_available(self) -> bool:
        """检查AI客户端是否可用"""
        try:
            # 尝试调用一个简单的请求
            response = self.zhipu_client.generate_content("测试")
            return response.success
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": "zhipu",
            "model": getattr(self.zhipu_client, 'model', 'glm-4.5'),
            "available": self.is_available()
        }


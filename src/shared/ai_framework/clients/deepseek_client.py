#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek AI客户端
支持DeepSeek Chat和DeepSeek Coder模型
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

class DeepSeekAIClient:
    """DeepSeek AI客户端"""
    
    def __init__(self, config_path: str = None):
        """
        初始化DeepSeek AI客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.base_url = self.config.get('base_url', 'https://api.deepseek.com/v1')
        self.api_key = self.config.get('api_key')
        self.timeout = self.config.get('timeout', 60)
        
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置")
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '..', '..', 'infrastructure', 'config', 'ai_models.json')
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 获取DeepSeek配置
            providers = config.get('providers', {})
            deepseek_config = providers.get('deepseek', {})
            
            return deepseek_config
        except Exception as e:
            print(f"⚠️ 加载DeepSeek配置失败: {e}")
            return {}
    
    def generate_content(self, 
                        prompt: str, 
                        system_prompt: str = None,
                        temperature: float = 0.7, 
                        max_tokens: int = 2000,
                        model: str = "deepseek-chat",
                        timeout: Optional[float] = None) -> AIResponse:
        """
        生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            model: 模型名称
            timeout: 超时时间（秒），None表示使用默认超时
            
        Returns:
            AIResponse: 响应结果
        """
        try:
            # 构建消息
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # 构建请求数据
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # 设置请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求
            actual_timeout = timeout if timeout is not None else self.timeout
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=actual_timeout
            )
            
            # 检查响应状态
            if response.status_code != 200:
                return AIResponse(
                    content="",
                    usage={},
                    model=model,
                    success=False,
                    error_message=f"API请求失败: {response.status_code} - {response.text}"
                )
            
            # 解析响应
            result = response.json()
            
            if "error" in result:
                return AIResponse(
                    content="",
                    usage={},
                    model=model,
                    success=False,
                    error_message=f"API错误: {result['error']}"
                )
            
            # 提取内容
            content = ""
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
            
            # 提取使用情况
            usage = result.get("usage", {})
            
            return AIResponse(
                content=content,
                usage=usage,
                model=model,
                success=True
            )
            
        except requests.exceptions.Timeout:
            return AIResponse(
                content="",
                usage={},
                model=model,
                success=False,
                error_message="请求超时"
            )
        except requests.exceptions.RequestException as e:
            return AIResponse(
                content="",
                usage={},
                model=model,
                success=False,
                error_message=f"网络请求失败: {e}"
            )
        except Exception as e:
            return AIResponse(
                content="",
                usage={},
                model=model,
                success=False,
                error_message=f"生成内容失败: {e}"
            )


def main():
    """测试函数"""
    print("🧪 测试DeepSeek AI客户端...")
    
    try:
        client = DeepSeekAIClient()
        print("✅ 客户端初始化成功")
        
        # 测试生成内容
        response = client.generate_content(
            prompt="请用一句话介绍Python编程语言的特点。",
            temperature=0.7,
            max_tokens=100
        )
        
        if response.success:
            print(f"✅ 生成成功!")
            print(f"   模型: {response.model}")
            print(f"   内容: {response.content}")
            print(f"   使用情况: {response.usage}")
        else:
            print(f"❌ 生成失败: {response.error_message}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    main()

import json
import requests
import time
from typing import Optional, Dict, Any, List
import os
import logging

class LLMClient:
    """大模型API客户端框架"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化LLM客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.base_url = self.config["llm_config"]["base_url"]
        self.api_key = self.config["llm_config"]["api_key"]
        self.model = self.config["llm_config"]["model"]
        self.timeout = self.config["llm_config"]["timeout"]
        self.max_retries = self.config["llm_config"]["max_retries"]
        self.temperature = self.config["llm_config"]["temperature"]
        self.max_tokens = self.config["llm_config"]["max_tokens"]
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 设置请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件 {config_path} 未找到")
        except json.JSONDecodeError:
            raise ValueError(f"配置文件 {config_path} 格式错误")
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送HTTP请求到LLM API
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.logger.error(f"请求失败: {e}")
                    raise
                self.logger.warning(f"请求失败，重试 {attempt + 1}/{self.max_retries}: {e}")
                time.sleep(2 ** attempt)  # 指数退避
    
    def chat_completion(self, 
                      messages: List[Dict[str, str]], 
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        发送聊天完成请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "Hello"}]
            temperature: 温度参数，控制随机性
            max_tokens: 最大令牌数
            
        Returns:
            API响应
        """
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        
        return self._make_request("chat/completions", data)
    
    def completion(self, 
                  prompt: str,
                  temperature: Optional[float] = None,
                  max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        发送文本完成请求
        
        Args:
            prompt: 输入提示
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            API响应
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, temperature, max_tokens)
    
    def get_models(self) -> Dict[str, Any]:
        """
        获取可用模型列表
        
        Returns:
            模型列表
        """
        return self._make_request("models", {})
    
    def update_config(self, **kwargs):
        """
        更新配置参数
        
        Args:
            **kwargs: 要更新的配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.logger.info(f"配置已更新: {key} = {value}")
    
    def __str__(self):
        return f"LLMClient(model={self.model}, base_url={self.base_url})"


# 使用示例
if __name__ == "__main__":
    # 创建客户端实例
    client = LLMClient()
    
    # 发送聊天请求
    try:
        response = client.chat_completion([
            {"role": "user", "content": "你好，请介绍一下你自己。"}
        ])
        
        # 提取回复内容
        if "choices" in response and len(response["choices"]) > 0:
            reply = response["choices"][0]["message"]["content"]
            print(f"AI回复: {reply}")
        else:
            print("API响应格式错误")
            
    except Exception as e:
        print(f"请求失败: {e}")

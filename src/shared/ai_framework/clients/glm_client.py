#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLM客户端
支持智谱AI的GLM系列模型（GLM-4.5、GLM-4.5-Flash、GLM-4.5-Turbo等）
"""

import json
import requests
import time
import hashlib
from typing import Dict, List, Any, Optional, Generator
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
    finish_reason: Optional[str] = None


@dataclass
class StreamChunk:
    """流式输出数据块"""
    content: str
    delta: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None

class GLMClient:
    """GLM客户端"""
    
    def __init__(self, config_path: str = None):
        """
        初始化GLM客户端
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.base_url = self.config.get('base_url', 'https://open.bigmodel.cn/api/paas/v4')
        self.api_key = self.config.get('api_key')
        self.timeout = self.config.get('timeout', 60)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1)
        
        if not self.api_key:
            raise ValueError("GLM API密钥未配置")
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '..', '..', 'infrastructure', 'config', 'ai_models.json')
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 获取智谱AI配置
            providers = config.get('providers', {})
            zhipu_config = providers.get('zhipu', {})
            
            # 获取LLM配置
            llm_config = config.get('llm_config', {})
            
            # 合并配置
            merged_config = {**zhipu_config, **llm_config}
            
            return merged_config
        except Exception as e:
            print(f"⚠️ 加载GLM配置失败: {e}")
            return {}
    
    def _get_model_config(self, model: str) -> Dict[str, Any]:
        """获取模型配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            providers = config.get('providers', {})
            zhipu_models = providers.get('zhipu', {}).get('models', {})
            
            # 查找匹配的模型配置
            for model_name, model_config in zhipu_models.items():
                if model_name.lower() == model.lower() or model in model_name.lower():
                    return model_config
            
            # 返回默认配置
            return {
                "max_tokens": 8192,
                "temperature": 0.7,
                "timeout": 60
            }
        except:
            return {
                "max_tokens": 8192,
                "temperature": 0.7,
                "timeout": 60
            }
    
    def _generate_signature(self, timestamp: str, method: str, url: str, body: str) -> str:
        """生成签名"""
        # 智谱AI的签名算法
        string_to_sign = f"{method}\n{url}\n{timestamp}\n{body}"
        import hmac
        import base64
        signature = hmac.new(
            self.api_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    def generate_content(self, 
                        prompt: str, 
                        system_prompt: str = None,
                        temperature: float = 0.7, 
                        max_tokens: int = 2000,
                        model: str = "glm-4.5-flash",
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
        # 获取模型配置
        model_config = self._get_model_config(model)
        actual_max_tokens = min(max_tokens, model_config.get('max_tokens', 8192))
        actual_temperature = temperature if temperature is not None else model_config.get('temperature', 0.7)
        actual_timeout = timeout if timeout is not None else model_config.get('timeout', self.timeout)
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # 构建请求数据
        data = {
            "model": model,
            "messages": messages,
            "temperature": actual_temperature,
            "max_tokens": actual_max_tokens,
            "stream": False
        }
        
        # 生成时间戳和签名
        timestamp = str(int(time.time() * 1000))
        method = "POST"
        url = "/api/paas/v4/chat/completions"
        body = json.dumps(data, separators=(',', ':'))
        
        signature = self._generate_signature(timestamp, method, url, body)
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }
        
        # 重试机制
        last_error = None
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 GLM API调用 (尝试 {attempt + 1}/{self.max_retries})")
                print(f"   模型: {model}")
                print(f"   温度: {actual_temperature}")
                print(f"   最大tokens: {actual_max_tokens}")
                print(f"   超时: {actual_timeout}秒")
                print(f"   提示词长度: {len(prompt)} 字符")
                
                # 发送请求
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    json=data,
                    headers=headers,
                    timeout=actual_timeout
                )
                
                print(f"📡 API响应状态: {response.status_code}")
                
                # 检查响应状态
                if response.status_code == 200:
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
                    
                    # 提取完成原因
                    finish_reason = None
                    if "choices" in result and len(result["choices"]) > 0:
                        finish_reason = result["choices"][0].get("finish_reason")
                    
                    return AIResponse(
                        content=content,
                        usage=usage,
                        model=model,
                        success=True,
                        finish_reason=finish_reason
                    )
                
                elif response.status_code == 429:
                    # 频率限制，等待后重试
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"⚠️ 频率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    if attempt == self.max_retries - 1:
                        # 最后一次重试失败，抛出异常
                        raise Exception(f"GLM API频率限制，重试{self.max_retries}次后仍然失败")
                    continue
                
                else:
                    last_error = f"API请求失败: {response.status_code} - {response.text}"
                    print(f"❌ API请求失败: {last_error}")
                    if attempt < self.max_retries - 1:
                        print(f"🔄 等待 {self.retry_delay} 秒后重试...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        # 最后一次重试失败，抛出异常
                        raise Exception(f"GLM API请求失败: {last_error}")
                        
            except requests.exceptions.Timeout:
                last_error = "请求超时"
                print(f"⏰ 请求超时: {last_error}")
                if attempt < self.max_retries - 1:
                    print(f"🔄 等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # 最后一次重试失败，抛出异常
                    raise Exception(f"GLM API请求超时: {last_error}")
                    
            except requests.exceptions.RequestException as e:
                last_error = f"网络请求失败: {e}"
                print(f"🌐 网络请求异常: {last_error}")
                if attempt < self.max_retries - 1:
                    print(f"🔄 等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # 最后一次重试失败，抛出异常
                    raise Exception(f"GLM API网络请求异常: {last_error}")
                    
            except Exception as e:
                last_error = f"生成内容失败: {e}"
                print(f"❓ 未知错误: {last_error}")
                if attempt < self.max_retries - 1:
                    print(f"🔄 等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    # 最后一次重试失败，抛出异常
                    raise Exception(f"GLM API未知错误: {last_error}")
        
        # 所有重试都失败
        return AIResponse(
            content="",
            usage={},
            model=model,
            success=False,
            error_message=f"重试 {self.max_retries} 次后仍然失败: {last_error}"
        )
    
    def generate_content_stream(self, 
                               prompt: str, 
                               system_prompt: str = None,
                               temperature: float = 0.7, 
                               max_tokens: int = 2000,
                               model: str = "glm-4.5-flash",
                               timeout: Optional[float] = None) -> Generator[StreamChunk, None, None]:
        """
        流式生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            model: 模型名称
            timeout: 超时时间（秒），None表示使用默认超时
            
        Yields:
            StreamChunk: 流式输出数据块
        """
        if not self.api_key:
            yield StreamChunk(
                content="",
                delta="",
                model=model,
                finish_reason="error"
            )
            return
        
        # 获取模型配置
        model_config = self._get_model_config(model)
        actual_temperature = min(max(temperature, 0.1), 2.0)
        actual_max_tokens = min(max_tokens, model_config.get('max_tokens', 8192))
        actual_timeout = timeout or model_config.get('timeout', self.timeout)
        
        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # 构建请求数据（启用流式输出）
        data = {
            "model": model,
            "messages": messages,
            "temperature": actual_temperature,
            "max_tokens": actual_max_tokens,
            "stream": True
        }
        
        # 生成时间戳和签名
        timestamp = str(int(time.time() * 1000))
        method = "POST"
        url = "/api/paas/v4/chat/completions"
        body = json.dumps(data, separators=(',', ':'))
        
        signature = self._generate_signature(timestamp, method, url, body)
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }
        
        try:
            print(f"🚀 GLM 流式API调用开始")
            print(f"   模型: {model}")
            print(f"   温度: {actual_temperature}")
            print(f"   最大tokens: {actual_max_tokens}")
            print(f"   提示词长度: {len(prompt)} 字符")
            
            # 发送流式请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=actual_timeout,
                stream=True
            )
            
            if response.status_code == 200:
                print(f"✅ GLM 流式响应开始")
                
                full_content = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        line_str = line.strip()
                        
                        # 处理SSE格式数据
                        if line_str.startswith('data: '):
                            data_str = line_str[6:].strip()  # 去掉 'data: ' 前缀
                            
                            if data_str == '[DONE]':
                                # 流式输出结束
                                yield StreamChunk(
                                    content=full_content,
                                    delta="",
                                    model=model,
                                    finish_reason="stop"
                                )
                                break
                            
                            if data_str:  # 确保不是空字符串
                                try:
                                    chunk_data = json.loads(data_str)
                                    
                                    if 'choices' in chunk_data and chunk_data['choices']:
                                        choice = chunk_data['choices'][0]
                                        
                                        # 检查delta结构
                                        if 'delta' in choice:
                                            delta = choice['delta']
                                            delta_content = ""
                                            
                                            # 智谱AI的流式响应可能在content或reasoning_content字段中
                                            if 'content' in delta and delta['content']:
                                                delta_content = delta['content']
                                            elif 'reasoning_content' in delta and delta['reasoning_content']:
                                                delta_content = delta['reasoning_content']
                                            
                                            if delta_content:  # 只有当有实际内容时才处理
                                                full_content += delta_content
                                                
                                                yield StreamChunk(
                                                    content=full_content,
                                                    delta=delta_content,
                                                    model=model,
                                                    finish_reason=choice.get('finish_reason')
                                                )
                                            
                                            # 检查是否完成
                                            if choice.get('finish_reason'):
                                                yield StreamChunk(
                                                    content=full_content,
                                                    delta="",
                                                    model=model,
                                                    finish_reason=choice.get('finish_reason')
                                                )
                                                break
                                                
                                except json.JSONDecodeError:
                                    # 忽略JSON解析错误，继续处理下一行
                                    continue
                
                print(f"✅ GLM 流式输出完成，总长度: {len(full_content)} 字符")
            else:
                print(f"❌ GLM 流式API调用失败: {response.status_code}")
                error_msg = f"HTTP {response.status_code}: {response.text}"
                yield StreamChunk(
                    content="",
                    delta="",
                    model=model,
                    finish_reason="error"
                )
                
        except Exception as e:
            print(f"❌ GLM 流式调用异常: {e}")
            yield StreamChunk(
                content="",
                delta="",
                model=model,
                finish_reason="error"
            )
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            providers = config.get('providers', {})
            zhipu_models = providers.get('zhipu', {}).get('models', {})
            
            return list(zhipu_models.keys())
        except:
            return ["glm-4.5-flash", "glm-4.5-turbo", "GLM-4.5"]
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """获取模型信息"""
        return self._get_model_config(model)


def main():
    """测试函数"""
    print("🧪 测试GLM客户端...")
    
    try:
        client = GLMClient()
        print("✅ 客户端初始化成功")
        
        # 获取可用模型
        models = client.get_available_models()
        print(f"📋 可用模型: {models}")
        
        # 测试生成内容
        response = client.generate_content(
            prompt="请用一句话介绍GLM大模型的特点。",
            temperature=0.7,
            max_tokens=100,
            model="glm-4.5-flash"
        )
        
        if response.success:
            print(f"✅ 生成成功!")
            print(f"   模型: {response.model}")
            print(f"   内容: {response.content}")
            print(f"   使用情况: {response.usage}")
            print(f"   完成原因: {response.finish_reason}")
        else:
            print(f"❌ 生成失败: {response.error_message}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    main()

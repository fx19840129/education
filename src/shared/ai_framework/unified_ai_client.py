#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一AI模型调用接口
支持多种AI模型，提供统一的调用方法
"""

import os
import sys
import json
import time
from typing import Optional, Dict, Any, List, Union, Generator, Iterator
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

# 导入现有客户端
from src.shared.ai_framework.clients.glm_client import GLMClient, AIResponse as GLMResponse
from src.shared.ai_framework.clients.deepseek_client import DeepSeekAIClient, AIResponse as DeepSeekResponse
from src.shared.ai_framework.clients.openai_client import OpenAIClient, AIResponse as OpenAIResponse


class AIModel(Enum):
    """支持的AI模型枚举"""
    # GLM模型（智谱AI）
    GLM_45 = "glm_45"
    GLM_45_FLASH = "glm_45_flash"
    GLM_45_TURBO = "glm_45_turbo"
    
    # DeepSeek模型
    DEEPSEEK_CHAT = "deepseek_chat"
    DEEPSEEK_CODER = "deepseek_coder"
    
    # OpenAI模型
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT35_TURBO = "openai_gpt35_turbo"


@dataclass
class UnifiedAIResponse:
    """统一AI响应数据类"""
    content: str
    model: str
    success: bool
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    error_message: Optional[str] = None
    response_time: Optional[float] = None


@dataclass
class StreamChunk:
    """流式输出数据块"""
    content: str
    delta: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None


@dataclass
class GenerationRequest:
    """生成请求数据类"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    model: Optional[str] = None
    timeout: Optional[float] = None
    stream: bool = False


class BaseAIClient(ABC):
    """AI客户端基类"""
    
    @abstractmethod
    def generate_content(self, request: GenerationRequest) -> UnifiedAIResponse:
        """生成内容"""
        pass
    
    @abstractmethod
    def generate_content_stream(self, request: GenerationRequest) -> Generator[StreamChunk, None, None]:
        """流式生成内容"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查客户端是否可用"""
        pass


class DeepSeekAIClientWrapper(BaseAIClient):
    """DeepSeek AI客户端包装器"""
    
    def __init__(self, config_path: str = None):
        self.client = DeepSeekAIClient(config_path)
        self.model_name = "DeepSeek"
    
    def generate_content(self, request: GenerationRequest) -> UnifiedAIResponse:
        """生成内容"""
        start_time = time.time()
        
        try:
            # 根据模型类型选择具体的模型名称
            model_name = "deepseek-chat"
            if "coder" in str(request.model).lower():
                model_name = "deepseek-coder"
            
            response = self.client.generate_content(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                model=model_name,
                timeout=request.timeout
            )
            
            response_time = time.time() - start_time
            
            return UnifiedAIResponse(
                content=response.content,
                model=f"{self.model_name}-{model_name}",
                success=response.success,
                usage=response.usage,
                finish_reason=None,
                error_message=response.error_message,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return UnifiedAIResponse(
                content="",
                model=self.model_name,
                success=False,
                error_message=str(e),
                response_time=response_time
            )
    
    def generate_content_stream(self, request: GenerationRequest) -> Generator[StreamChunk, None, None]:
        """流式生成内容"""
        try:
            # 根据模型类型选择具体的模型名称
            model_name = "deepseek-chat"
            if "coder" in str(request.model).lower():
                model_name = "deepseek-coder"
            
            # DeepSeekAIClient需要先实现流式输出，这里暂时返回空流
            yield StreamChunk(
                content="DeepSeek流式输出暂未实现",
                delta="DeepSeek流式输出暂未实现",
                model=f"{self.model_name}-{model_name}",
                finish_reason="not_implemented"
            )
            
        except Exception as e:
            yield StreamChunk(
                content="",
                delta="",
                model=self.model_name,
                finish_reason="error"
            )
    
    def is_available(self) -> bool:
        """检查客户端是否可用"""
        try:
            return self.client is not None
        except:
            return False


class OpenAIClientWrapper(BaseAIClient):
    """OpenAI客户端包装器"""
    
    def __init__(self, config_path: str = None):
        self.client = OpenAIClient(config_path)
        self.model_name = "OpenAI"
    
    def generate_content(self, request: GenerationRequest) -> UnifiedAIResponse:
        """生成内容"""
        start_time = time.time()
        
        try:
            # 根据模型类型选择具体的模型名称
            model_name = "gpt-3.5-turbo"
            if "gpt4" in str(request.model).lower():
                model_name = "gpt-4"
            
            response = self.client.generate_content(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                model=model_name,
                timeout=request.timeout
            )
            
            response_time = time.time() - start_time
            
            return UnifiedAIResponse(
                content=response.content,
                model=f"{self.model_name}-{model_name}",
                success=response.success,
                usage=response.usage,
                finish_reason=None,
                error_message=response.error_message,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return UnifiedAIResponse(
                content="",
                model=self.model_name,
                success=False,
                error_message=str(e),
                response_time=response_time
            )
    
    def generate_content_stream(self, request: GenerationRequest) -> Generator[StreamChunk, None, None]:
        """流式生成内容"""
        try:
            # 根据模型类型选择具体的模型名称
            model_name = "gpt-3.5-turbo"
            if "gpt4" in str(request.model).lower():
                model_name = "gpt-4"
            
            # OpenAIClient需要先实现流式输出，这里暂时返回空流
            yield StreamChunk(
                content="OpenAI流式输出暂未实现",
                delta="OpenAI流式输出暂未实现",
                model=f"{self.model_name}-{model_name}",
                finish_reason="not_implemented"
            )
            
        except Exception as e:
            yield StreamChunk(
                content="",
                delta="",
                model=self.model_name,
                finish_reason="error"
            )
    
    def is_available(self) -> bool:
        """检查客户端是否可用"""
        try:
            return self.client is not None
        except:
            return False


class GLMClientWrapper(BaseAIClient):
    """GLM客户端包装器"""
    
    def __init__(self, config_path: str = None):
        self.client = GLMClient(config_path)
        self.model_name = "GLM"
    
    def generate_content(self, request: GenerationRequest) -> UnifiedAIResponse:
        """生成内容"""
        start_time = time.time()
        
        try:
            # 根据模型类型选择具体的模型名称
            model_name = "glm-4.5-flash"  # 默认值
            model_str = str(request.model).lower()
            
            print(f"🔍 GLM模型映射:")
            print(f"   请求模型: {request.model}")
            print(f"   模型字符串: {model_str}")
            
            if "turbo" in model_str:
                model_name = "glm-4.5-turbo"
                print(f"   → 映射到: {model_name} (turbo匹配)")
            elif "glm_45" in model_str and "flash" not in model_str and "turbo" not in model_str:
                model_name = "GLM-4.5"
                print(f"   → 映射到: {model_name} (glm_45匹配)")
            elif "glm_45_flash" in model_str:
                model_name = "glm-4.5-flash"
                print(f"   → 映射到: {model_name} (glm_45_flash匹配)")
            elif "glm_45_turbo" in model_str:
                model_name = "glm-4.5-turbo"
                print(f"   → 映射到: {model_name} (glm_45_turbo匹配)")
            else:
                print(f"   → 使用默认: {model_name}")
            
            response = self.client.generate_content(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                model=model_name,
                timeout=request.timeout
            )
            
            response_time = time.time() - start_time
            
            return UnifiedAIResponse(
                content=response.content,
                model=f"{self.model_name}-{model_name}",
                success=response.success,
                usage=response.usage,
                finish_reason=response.finish_reason,
                error_message=response.error_message,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return UnifiedAIResponse(
                content="",
                model=self.model_name,
                success=False,
                error_message=str(e),
                response_time=response_time
            )
    
    def generate_content_stream(self, request: GenerationRequest) -> Generator[StreamChunk, None, None]:
        """流式生成内容"""
        try:
            # 根据模型类型选择具体的模型名称
            model_name = "glm-4.5-flash"  # 默认值
            model_str = str(request.model).lower()
            
            if "turbo" in model_str:
                model_name = "glm-4.5-turbo"
            elif "glm_45" in model_str and "flash" not in model_str and "turbo" not in model_str:
                model_name = "GLM-4.5"
            elif "glm_45_flash" in model_str:
                model_name = "glm-4.5-flash"
            elif "glm_45_turbo" in model_str:
                model_name = "glm-4.5-turbo"
            
            # 调用GLMClient的流式方法
            for chunk in self.client.generate_content_stream(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                model=model_name,
                timeout=request.timeout
            ):
                # 转换为统一的StreamChunk格式
                yield StreamChunk(
                    content=chunk.content,
                    delta=chunk.delta,
                    model=f"{self.model_name}-{model_name}",
                    finish_reason=chunk.finish_reason,
                    usage=chunk.usage
                )
                
        except Exception as e:
            yield StreamChunk(
                content="",
                delta="",
                model=self.model_name,
                finish_reason="error"
            )
    
    def is_available(self) -> bool:
        """检查客户端是否可用"""
        try:
            return self.client is not None
        except:
            return False


class UnifiedAIClient:
    """统一AI客户端"""
    
    def __init__(self, default_model: AIModel = AIModel.GLM_45_FLASH, config_path: str = None):
        """
        初始化统一AI客户端
        
        Args:
            default_model: 默认使用的模型
            config_path: 配置文件路径
        """
        self.default_model = default_model
        self.config_path = config_path
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化所有客户端"""
        try:
            # 初始化GLM客户端（智谱AI）
            self.clients[AIModel.GLM_45] = GLMClientWrapper(self.config_path)
            self.clients[AIModel.GLM_45_FLASH] = GLMClientWrapper(self.config_path)
            self.clients[AIModel.GLM_45_TURBO] = GLMClientWrapper(self.config_path)
            
            # 初始化DeepSeek客户端
            self.clients[AIModel.DEEPSEEK_CHAT] = DeepSeekAIClientWrapper(self.config_path)
            self.clients[AIModel.DEEPSEEK_CODER] = DeepSeekAIClientWrapper(self.config_path)
            
            # 初始化OpenAI客户端
            self.clients[AIModel.OPENAI_GPT4] = OpenAIClientWrapper(self.config_path)
            self.clients[AIModel.OPENAI_GPT35_TURBO] = OpenAIClientWrapper(self.config_path)
            
            print(f"✅ 统一AI客户端初始化完成，支持模型: {list(self.clients.keys())}")
            
        except Exception as e:
            print(f"⚠️ AI客户端初始化失败: {e}")
    
    def generate_content(self, 
                        prompt: str, 
                        system_prompt: str = None,
                        temperature: float = 0.7, 
                        max_tokens: int = 2000,
                        model: Optional[AIModel] = None,
                        timeout: Optional[float] = None) -> UnifiedAIResponse:
        """
        生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            model: 指定模型，None则使用默认模型
            timeout: 超时时间（秒），None表示无超时限制
            
        Returns:
            UnifiedAIResponse: 统一格式的响应
        """
        # 使用指定模型或默认模型
        target_model = model or self.default_model
        
        if target_model not in self.clients:
            return UnifiedAIResponse(
                content="",
                model=str(target_model),
                success=False,
                error_message=f"不支持的模型: {target_model}"
            )
        
        client = self.clients[target_model]
        
        # 检查客户端是否可用
        if not client.is_available():
            return UnifiedAIResponse(
                content="",
                model=str(target_model),
                success=False,
                error_message=f"模型 {target_model} 不可用"
            )
        
        # 创建请求
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            model=str(target_model),
            timeout=timeout
        )
        
        # 生成内容
        try:
            print(f"🚀 调用AI模型: {target_model}")
            print(f"   提示词长度: {len(prompt)} 字符")
            print(f"   温度: {temperature}")
            print(f"   最大tokens: {max_tokens}")
            print(f"   超时: {timeout}秒")
            
            response = client.generate_content(request)
            
            print(f"✅ AI模型调用成功: {response.success}")
            if response.success:
                print(f"   响应内容长度: {len(response.content)} 字符")
                print(f"   使用情况: {response.usage}")
            else:
                print(f"   错误信息: {response.error_message}")
            
            return response
            
        except Exception as e:
            print(f"❌ AI模型调用异常: {e}")
            # 将异常重新抛出，让上层处理
            raise Exception(f"统一AI客户端调用失败: {e}")
    
    def generate_content_stream(self, 
                               prompt: str, 
                               system_prompt: str = None,
                               temperature: float = 0.7, 
                               max_tokens: int = 2000,
                               model: Optional[AIModel] = None,
                               timeout: Optional[float] = None) -> Generator[StreamChunk, None, None]:
        """
        流式生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            model: 指定模型，None则使用默认模型
            timeout: 超时时间（秒），None表示无超时限制
            
        Yields:
            StreamChunk: 流式输出数据块
        """
        # 使用指定模型或默认模型
        target_model = model or self.default_model
        
        if target_model not in self.clients:
            yield StreamChunk(
                content="",
                delta="",
                model=str(target_model),
                finish_reason="error"
            )
            return
        
        client = self.clients[target_model]
        
        # 检查客户端是否可用
        if not client.is_available():
            yield StreamChunk(
                content="",
                delta="",
                model=str(target_model),
                finish_reason="error"
            )
            return
        
        # 创建请求
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            model=str(target_model),
            timeout=timeout,
            stream=True
        )
        
        # 流式生成内容
        try:
            print(f"🚀 流式调用AI模型: {target_model}")
            print(f"   提示词长度: {len(prompt)} 字符")
            print(f"   温度: {temperature}")
            print(f"   最大tokens: {max_tokens}")
            print(f"   超时: {timeout}秒")
            
            for chunk in client.generate_content_stream(request):
                yield chunk
                
        except Exception as e:
            print(f"❌ AI模型流式调用异常: {e}")
            yield StreamChunk(
                content="",
                delta="",
                model=str(target_model),
                finish_reason="error"
            )
    
    def generate_stream_with_fallback(self, 
                                     prompt: str, 
                                     system_prompt: str = None,
                                     temperature: float = 0.7, 
                                     max_tokens: int = 2000,
                                     preferred_models: List[AIModel] = None) -> Generator[StreamChunk, None, None]:
        """
        使用回退机制流式生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            preferred_models: 优先使用的模型列表
            
        Yields:
            StreamChunk: 流式输出数据块
        """
        if preferred_models is None:
            preferred_models = [self.default_model, AIModel.GLM_45_FLASH, AIModel.GLM_45_TURBO]
        
        for model in preferred_models:
            try:
                # 尝试流式生成
                chunk_count = 0
                for chunk in self.generate_content_stream(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model
                ):
                    chunk_count += 1
                    if chunk.finish_reason == "error":
                        # 如果出错，尝试下一个模型
                        break
                    yield chunk
                    
                    # 如果成功生成了内容，就不需要fallback了
                    if chunk.finish_reason == "stop":
                        print(f"✅ 使用模型 {model} 流式生成成功，共 {chunk_count} 个数据块")
                        return
                        
            except Exception as e:
                print(f"⚠️ 模型 {model} 流式调用异常: {e}")
                continue
        
        # 所有模型都失败
        print("❌ 所有模型流式调用都失败")
        yield StreamChunk(
            content="",
            delta="",
            model="fallback",
            finish_reason="error"
        )
    
    def generate_with_fallback(self, 
                              prompt: str, 
                              system_prompt: str = None,
                              temperature: float = 0.7, 
                              max_tokens: int = 2000,
                              preferred_models: List[AIModel] = None) -> UnifiedAIResponse:
        """
        使用回退机制生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            preferred_models: 优先使用的模型列表
            
        Returns:
            UnifiedAIResponse: 统一格式的响应
        """
        if preferred_models is None:
            preferred_models = [self.default_model, AIModel.GLM_45_FLASH, AIModel.GLM_45_TURBO]
        
        last_error = None
        
        for model in preferred_models:
            try:
                response = self.generate_content(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model
                )
                
                if response.success:
                    print(f"✅ 使用模型 {model} 生成成功")
                    return response
                else:
                    last_error = response.error_message
                    print(f"⚠️ 模型 {model} 生成失败: {response.error_message}")
                    
            except Exception as e:
                last_error = str(e)
                print(f"⚠️ 模型 {model} 调用异常: {e}")
        
        # 所有模型都失败
        return UnifiedAIResponse(
            content="",
            model="fallback",
            success=False,
            error_message=f"所有模型都失败，最后错误: {last_error}"
        )
    
    def get_available_models(self) -> List[AIModel]:
        """获取可用的模型列表"""
        available = []
        for model, client in self.clients.items():
            if client.is_available():
                available.append(model)
        return available
    
    def test_connection(self) -> Dict[str, bool]:
        """测试所有模型的连接状态"""
        results = {}
        for model, client in self.clients.items():
            results[str(model)] = client.is_available()
        return results


# 全局实例
_unified_client = None

def get_unified_ai_client() -> UnifiedAIClient:
    """获取全局统一AI客户端实例"""
    global _unified_client
    if _unified_client is None:
        _unified_client = UnifiedAIClient()
    return _unified_client


def generate_content(prompt: str, 
                    system_prompt: str = None,
                    temperature: float = 0.7, 
                    max_tokens: int = 2000,
                    model: Optional[AIModel] = None) -> UnifiedAIResponse:
    """
    便捷函数：生成内容
    
    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词
        temperature: 温度参数
        max_tokens: 最大token数
        model: 指定模型
        
    Returns:
        UnifiedAIResponse: 统一格式的响应
    """
    client = get_unified_ai_client()
    return client.generate_content(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        model=model
    )


def generate_content_stream(prompt: str, 
                           system_prompt: str = None,
                           temperature: float = 0.7, 
                           max_tokens: int = 2000,
                           model: Optional[AIModel] = None) -> Generator[StreamChunk, None, None]:
    """
    便捷函数：流式生成内容
    
    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词
        temperature: 温度参数
        max_tokens: 最大token数
        model: 指定模型
        
    Yields:
        StreamChunk: 流式输出数据块
    """
    client = get_unified_ai_client()
    for chunk in client.generate_content_stream(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        model=model
    ):
        yield chunk


def generate_stream_with_fallback(prompt: str, 
                                 system_prompt: str = None,
                                 temperature: float = 0.7, 
                                 max_tokens: int = 2000) -> Generator[StreamChunk, None, None]:
    """
    便捷函数：使用回退机制流式生成内容
    
    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词
        temperature: 温度参数
        max_tokens: 最大token数
        
    Yields:
        StreamChunk: 流式输出数据块
    """
    client = get_unified_ai_client()
    for chunk in client.generate_stream_with_fallback(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    ):
        yield chunk


def generate_with_fallback(prompt: str, 
                          system_prompt: str = None,
                          temperature: float = 0.7, 
                          max_tokens: int = 2000) -> UnifiedAIResponse:
    """
    便捷函数：使用回退机制生成内容
    
    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词
        temperature: 温度参数
        max_tokens: 最大token数
        
    Returns:
        UnifiedAIResponse: 统一格式的响应
    """
    client = get_unified_ai_client()
    return client.generate_with_fallback(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )


def main():
    """测试函数"""
    print("🧪 测试统一AI客户端...")
    
    # 获取客户端
    client = get_unified_ai_client()
    
    # 测试连接
    print("\n📡 测试模型连接状态:")
    connection_status = client.test_connection()
    for model, status in connection_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {model}: {'可用' if status else '不可用'}")
    
    # 获取可用模型
    available_models = client.get_available_models()
    print(f"\n🎯 可用模型: {[str(m) for m in available_models]}")
    
    if available_models:
        # 测试生成内容
        print("\n🤖 测试内容生成...")
        test_prompt = "请用一句话介绍英语学习的重要性。"
        
        response = client.generate_with_fallback(
            prompt=test_prompt,
            temperature=0.7,
            max_tokens=100
        )
        
        if response.success:
            print(f"✅ 生成成功!")
            print(f"   模型: {response.model}")
            print(f"   内容: {response.content}")
            print(f"   响应时间: {response.response_time:.2f}秒")
        else:
            print(f"❌ 生成失败: {response.error_message}")
    else:
        print("⚠️ 没有可用的模型")


if __name__ == "__main__":
    main()

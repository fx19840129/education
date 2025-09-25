#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM框架使用示例
"""

from llm_client import LLMClient
import json

def main():
    """主函数：演示LLM客户端的各种用法"""
    
    print("=== LLM框架使用示例 ===\n")
    
    # 1. 创建客户端实例
    print("1. 创建LLM客户端...")
    client = LLMClient()
    print(f"客户端信息: {client}\n")
    
    # 2. 简单文本完成
    print("2. 简单文本完成示例:")
    try:
        response = client.completion("请用一句话描述什么是人工智能。")
        if "choices" in response and len(response["choices"]) > 0:
            reply = response["choices"][0]["message"]["content"]
            print(f"AI回复: {reply}\n")
        else:
            print("API响应格式错误\n")
    except Exception as e:
        print(f"请求失败: {e}\n")
    
    # 3. 聊天对话
    print("3. 聊天对话示例:")
    try:
        messages = [
            {"role": "user", "content": "你好，我想学习Python编程。"},
            {"role": "assistant", "content": "你好！Python是一门很好的编程语言，适合初学者。"},
            {"role": "user", "content": "请给我一些学习Python的建议。"}
        ]
        
        response = client.chat_completion(messages)
        if "choices" in response and len(response["choices"]) > 0:
            reply = response["choices"][0]["message"]["content"]
            print(f"AI回复: {reply}\n")
        else:
            print("API响应格式错误\n")
    except Exception as e:
        print(f"请求失败: {e}\n")
    
    # 4. 自定义参数
    print("4. 自定义参数示例:")
    try:
        response = client.completion(
            prompt="请写一首关于春天的短诗。",
            temperature=0.8,  # 更高的创造性
            max_tokens=200   # 限制输出长度
        )
        
        if "choices" in response and len(response["choices"]) > 0:
            reply = response["choices"][0]["message"]["content"]
            print(f"AI回复: {reply}\n")
        else:
            print("API响应格式错误\n")
    except Exception as e:
        print(f"请求失败: {e}\n")
    
    # 5. 获取模型列表
    print("5. 获取可用模型列表:")
    try:
        models = client.get_models()
        print("可用模型:")
        if "data" in models:
            for model in models["data"]:
                print(f"  - {model.get('id', 'Unknown')}")
        print()
    except Exception as e:
        print(f"获取模型列表失败: {e}\n")
    
    # 6. 配置更新
    print("6. 配置更新示例:")
    try:
        # 更新温度参数
        client.update_config(temperature=0.5)
        print("温度参数已更新为 0.5")
        
        # 使用新配置发送请求
        response = client.completion("现在请用更严谨的语调解释什么是机器学习。")
        if "choices" in response and len(response["choices"]) > 0:
            reply = response["choices"][0]["message"]["content"]
            print(f"AI回复: {reply}\n")
        else:
            print("API响应格式错误\n")
    except Exception as e:
        print(f"请求失败: {e}\n")

def advanced_example():
    """高级使用示例：批量处理和错误处理"""
    
    print("=== 高级使用示例 ===\n")
    
    client = LLMClient()
    
    # 批量处理问题
    questions = [
        "什么是深度学习？",
        "Python和Java有什么区别？",
        "如何提高编程技能？"
    ]
    
    print("批量处理问题:")
    for i, question in enumerate(questions, 1):
        try:
            print(f"问题 {i}: {question}")
            response = client.completion(question, max_tokens=150)
            
            if "choices" in response and len(response["choices"]) > 0:
                reply = response["choices"][0]["message"]["content"]
                print(f"回答 {i}: {reply}\n")
            else:
                print(f"问题 {i} 的API响应格式错误\n")
                
        except Exception as e:
            print(f"问题 {i} 处理失败: {e}\n")

def config_example():
    """配置文件示例"""
    
    print("=== 配置文件示例 ===\n")
    
    # 显示当前配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            print("当前配置:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
            print("\n注意：请将 'your_api_key_here' 替换为您的实际API密钥\n")
    except Exception as e:
        print(f"读取配置文件失败: {e}\n")

if __name__ == "__main__":
    # 运行基本示例
    main()
    
    # 运行高级示例
    advanced_example()
    
    # 显示配置信息
    config_example()

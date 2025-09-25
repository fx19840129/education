# LLM调用框架

一个简单易用的Python框架，用于调用大模型API。通过配置文件管理API密钥和参数，支持多种大模型服务。

## 功能特性

- 🚀 **简单易用**：几行代码即可调用大模型API
- ⚙️ **配置灵活**：通过JSON配置文件管理所有参数
- 🔒 **安全可靠**：支持重试机制和错误处理
- 📝 **完整日志**：详细的日志记录和调试信息
- 🎯 **多种接口**：支持聊天完成、文本完成等多种API调用方式

## 安装

1. 克隆或下载项目文件
2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 配置设置

编辑 `config.json` 文件，填入您的API密钥和配置：

```json
{
  "llm_config": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "your_api_key_here",
    "model": "gpt-3.5-turbo",
    "timeout": 30,
    "max_retries": 3,
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

### 2. 基本使用

```python
from llm_client import LLMClient

# 创建客户端
client = LLMClient()

# 简单文本完成
response = client.completion("你好，请介绍一下人工智能。")
print(response["choices"][0]["message"]["content"])

# 聊天对话
messages = [
    {"role": "user", "content": "我想学习Python编程。"},
    {"role": "assistant", "content": "Python是一门很好的编程语言。"},
    {"role": "user", "content": "请给我一些建议。"}
]
response = client.chat_completion(messages)
print(response["choices"][0]["message"]["content"])
```

## API文档

### LLMClient类

#### 初始化

```python
client = LLMClient(config_path="config.json")
```

**参数：**
- `config_path` (str): 配置文件路径，默认为"config.json"

#### 主要方法

##### completion(prompt, temperature=None, max_tokens=None)

发送文本完成请求

**参数：**
- `prompt` (str): 输入提示文本
- `temperature` (float, optional): 温度参数，控制随机性
- `max_tokens` (int, optional): 最大令牌数

**返回：**
- `dict`: API响应数据

**示例：**
```python
response = client.completion("什么是机器学习？")
```

##### chat_completion(messages, temperature=None, max_tokens=None)

发送聊天完成请求

**参数：**
- `messages` (list): 消息列表，格式为 `[{"role": "user", "content": "Hello"}]`
- `temperature` (float, optional): 温度参数
- `max_tokens` (int, optional): 最大令牌数

**返回：**
- `dict`: API响应数据

**示例：**
```python
messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！很高兴见到你。"},
    {"role": "user", "content": "今天天气怎么样？"}
]
response = client.chat_completion(messages)
```

##### get_models()

获取可用模型列表

**返回：**
- `dict`: 模型列表数据

**示例：**
```python
models = client.get_models()
for model in models["data"]:
    print(model["id"])
```

##### update_config(**kwargs)

更新配置参数

**参数：**
- `**kwargs`: 要更新的配置参数

**示例：**
```python
client.update_config(temperature=0.5, max_tokens=500)
```

## 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `base_url` | str | "https://api.openai.com/v1" | API基础URL |
| `api_key` | str | "your_api_key_here" | API密钥 |
| `model` | str | "gpt-3.5-turbo" | 使用的模型名称 |
| `timeout` | int | 30 | 请求超时时间（秒） |
| `max_retries` | int | 3 | 最大重试次数 |
| `temperature` | float | 0.7 | 温度参数（0-2） |
| `max_tokens` | int | 1000 | 最大令牌数 |

## 支持的大模型服务

框架支持任何兼容OpenAI API格式的大模型服务，包括：

- OpenAI (GPT-3.5, GPT-4等)
- Anthropic Claude
- 本地部署的模型（通过兼容API）
- 其他第三方大模型服务

只需修改 `config.json` 中的 `base_url` 和 `model` 参数即可切换不同的服务。

## 错误处理

框架内置了完善的错误处理机制：

- **自动重试**：网络错误时自动重试，使用指数退避策略
- **超时处理**：支持请求超时设置
- **日志记录**：详细的错误日志和调试信息
- **异常抛出**：清晰的异常类型和错误信息

## 示例代码

查看 `example.py` 文件获取更多使用示例，包括：

- 基本文本完成
- 聊天对话
- 自定义参数
- 批量处理
- 错误处理

运行示例：

```bash
python example.py
```

## 最佳实践

### 1. API密钥安全

- 不要将API密钥硬编码在代码中
- 使用配置文件或环境变量管理密钥
- 将配置文件添加到 `.gitignore` 中

### 2. 错误处理

```python
try:
    response = client.completion("你的问题")
    # 处理响应
except Exception as e:
    print(f"请求失败: {e}")
    # 处理错误
```

### 3. 参数调优

- `temperature`：创造性任务使用较高值（0.8-1.2），事实性任务使用较低值（0.1-0.5）
- `max_tokens`：根据需要设置合适的值，避免不必要的token消耗
- `timeout`：根据网络环境和任务复杂度调整

### 4. 批量处理

```python
questions = ["问题1", "问题2", "问题3"]
for question in questions:
    try:
        response = client.completion(question)
        # 处理每个问题的响应
    except Exception as e:
        print(f"处理问题失败: {question}, 错误: {e}")
```

## 常见问题

### Q: 如何切换到其他大模型服务？

A: 修改 `config.json` 中的 `base_url` 和 `model` 参数。例如：

```json
{
  "llm_config": {
    "base_url": "https://api.anthropic.com/v1",
    "api_key": "your_anthropic_key",
    "model": "claude-3-sonnet-20240229"
  }
}
```

### Q: 如何处理API限制？

A: 框架内置了重试机制，您也可以：

1. 调整 `max_retries` 参数
2. 在代码中添加延迟
3. 实现请求队列

### Q: 如何自定义请求头？

A: 可以继承 `LLMClient` 类并重写 `__init__` 方法：

```python
class CustomLLMClient(LLMClient):
    def __init__(self, config_path="config.json"):
        super().__init__(config_path)
        self.headers["Custom-Header"] = "value"
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的聊天完成和文本完成功能
- 配置文件管理
- 错误处理和重试机制

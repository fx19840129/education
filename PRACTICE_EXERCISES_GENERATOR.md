# 练习题生成器实现文档

## 概述

练习题生成器通过AI根据每日学习的单词、词法、句法生成包含选择题、翻译题、填空题的练习题，为学习者提供多样化的练习内容。

## 核心功能

### 1. AI驱动的练习题生成

- **智能内容生成**: 根据当日学习内容生成相关练习题
- **多种题型**: 支持选择题、翻译题、填空题三种题型
- **难度适配**: 根据学习阶段调整题目难度
- **内容关联**: 每道题都关联当日学习的单词、词法、句法

### 2. 统一提示词管理

所有AI提示词在 `src/english/english_prompt_generator.py` 中统一管理：

```python
def generate_practice_exercises_prompt(self, daily_words, daily_morphology, daily_syntax, stage):
    """生成练习题的AI提示词"""
    # 收集学习内容信息
    # 生成结构化提示词
    # 要求AI返回JSON格式的练习题
```

### 3. 题型支持

#### 选择题 (Choice)
```json
{
  "id": 1,
  "type": "choice",
  "question": "题目内容",
  "options": ["选项A", "选项B", "选项C", "选项D"],
  "correct_answer": "A",
  "explanation": "题目解析",
  "target_words": ["相关单词"],
  "morphology_points": ["相关词法点"],
  "syntax_structure": "相关句法结构",
  "difficulty": 3.0
}
```

#### 翻译题 (Translation)
```json
{
  "id": 2,
  "type": "translation",
  "question": "请将以下中文翻译成英文：",
  "chinese_text": "中文句子",
  "english_text": "English sentence",
  "explanation": "翻译要点",
  "target_words": ["相关单词"],
  "morphology_points": ["相关词法点"],
  "syntax_structure": "相关句法结构",
  "difficulty": 3.0
}
```

#### 填空题 (Fill Blank)
```json
{
  "id": 3,
  "type": "fill_blank",
  "question": "请填入适当的单词：",
  "sentence": "I ___ to school every day.",
  "answer": "go",
  "explanation": "填空解析",
  "target_words": ["相关单词"],
  "morphology_points": ["相关词法点"],
  "syntax_structure": "相关句法结构",
  "difficulty": 3.0
}
```

## 技术实现

### 1. 生成流程

```python
def generate_daily_exercises(self, learning_plan, target_date):
    # 1. 获取当日学习内容
    daily_words = self.fsrs_generator.generate_daily_learning_content(learning_plan, target_date)
    daily_morphology = self.morphology_generator.generate_daily_morphology(learning_plan, target_date)
    daily_syntax = self.syntax_generator.generate_daily_syntax(learning_plan, target_date)
    
    # 2. 生成AI提示词
    prompt = self.prompt_generator.generate_practice_exercises_prompt(
        daily_words, daily_morphology, daily_syntax, stage
    )
    
    # 3. 调用AI生成练习题
    ai_response = self.ai_client.generate_content(prompt)
    practice_data = self._parse_ai_response(ai_response)
    
    # 4. 备用机制
    if not practice_data.get('practice_exercises'):
        practice_exercises = self._generate_fallback_exercises(daily_words, stage)
    
    return practice_exercises
```

### 2. AI响应解析

```python
def _parse_ai_response(self, ai_response):
    """解析AI响应"""
    try:
        # 尝试直接解析JSON
        return json.loads(ai_response)
    except json.JSONDecodeError:
        # 提取JSON部分
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"practice_exercises": []}
```

### 3. 备用生成机制

当AI调用失败时，使用模板生成简单练习题：

```python
def _generate_fallback_exercises(self, daily_words, stage):
    """备用方法：生成简单练习题"""
    exercises = []
    
    # 生成选择题
    for word in all_words[:3]:
        exercise = {
            "type": "choice",
            "question": f"以下哪个是 '{word['word']}' 的中文意思？",
            "options": [word['translation'], "错误选项1", "错误选项2", "错误选项3"],
            "correct_answer": "A",
            "explanation": f"'{word['word']}' 的中文意思是 '{word['translation']}'"
        }
        exercises.append(exercise)
    
    # 生成翻译题和填空题...
    return exercises
```

## 使用示例

### 1. 基本使用

```python
from generate_practice_exercises import PracticeExercisesGenerator
from learning_content_generator import LearningContentGenerator

# 创建生成器
generator = PracticeExercisesGenerator()
plan_reader = LearningContentGenerator()

# 获取学习计划
learning_plan = plan_reader.read_plan(plan_id="latest")

# 生成练习题
daily_exercises = generator.generate_daily_exercises(learning_plan, "2025-09-28")
```

### 2. 生成学习计划

```python
# 生成多天练习题
schedule = generator.generate_exercises_schedule(learning_plan, days=7)

# 显示内容
generator.display_exercises_content(schedule)
```

## 显示格式

### 1. 按题型分组显示

```
📚 练习题学习计划
================================================================================
计划名称: 第一阶段：基础巩固 (小学中高年级)
学习阶段: 第一阶段：基础巩固 (小学中高年级)
开始日期: 2025-09-28
生成天数: 7天

📅 第1天 - 2025-09-28
   总练习题数: 9个

   📖 选择题 (3个):
      1. 以下哪个是 'sound' 的中文意思？
         选项: 声音, 错误的选项1, 错误的选项2, 错误的选项3
         答案: A
         目标单词: sound
         解析: 'sound' 的中文意思是 '声音'
         难度: 3.0

   📖 翻译题 (3个):
      1. 请将以下中文翻译成英文：
         中文: 我有一个机器人。
         英文: I have a robot.
         目标单词: robot
         解析: 这是一个简单的名词翻译练习
         难度: 3.0

   📖 填空题 (3个):
      1. 请填入适当的单词：
         句子: I ___ a house.
         答案: have
         目标单词: house
         解析: 这里需要填入动词 'have'
         难度: 3.0
```

## 配置要求

### 1. AI模型配置

- 使用 `UnifiedAIClient` 统一AI调用接口
- 默认使用 `AIModel.GLM_45` 模型
- 支持多种AI模型切换

### 2. 提示词配置

- 提示词长度: 约3500字符
- 温度设置: 0.7
- 最大tokens: 2000
- 超时设置: 60秒

### 3. 备用机制

- AI调用失败时自动启用
- 生成基础题型练习
- 确保系统稳定性

## 文件结构

```
generate_practice_exercises.py          # 练习题生成器主文件
src/english/english_prompt_generator.py  # AI提示词管理
learning_data/english/                  # 学习进度存储
├── morphology_progress.json           # 词法学习进度
├── syntax_progress.json               # 句法学习进度
└── learning_progress.json             # 单词学习进度
```

## 优势特点

1. **AI驱动**: 智能生成与学习内容相关的练习题
2. **题型丰富**: 支持选择题、翻译题、填空题三种题型
3. **内容关联**: 每道题都关联当日学习内容
4. **难度适配**: 根据学习阶段调整题目难度
5. **备用机制**: AI调用失败时使用模板生成
6. **统一管理**: 提示词在统一位置管理
7. **错误处理**: 完善的异常处理和日志记录

## 扩展性

- 支持添加新的题型
- 支持自定义题目模板
- 支持多种AI模型
- 支持自定义难度等级
- 支持批量生成和导出

这个练习题生成器为英语学习系统提供了完整的练习内容生成解决方案，通过AI智能生成与学习内容高度相关的练习题，提升学习效果。


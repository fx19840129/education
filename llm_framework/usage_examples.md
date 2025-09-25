# 学习计划生成器使用指南

## 概述

本框架提供了一个强大的学习计划生成器，可以根据孩子的薄弱项自动生成个性化的学习计划和练习题。通过调用大模型API，系统能够为不同年级、不同学科的学生量身定制学习内容。

## 快速开始

### 1. 配置设置

首先，确保 `config.json` 文件中配置了正确的大模型API信息：

```json
{
  "llm_config": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "your_actual_api_key_here",
    "model": "gpt-3.5-turbo",
    "timeout": 30,
    "max_retries": 3,
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

**重要提示**：请将 `your_actual_api_key_here` 替换为您的实际API密钥。

### 2. 基本使用

```python
from learning_plan_generator import LearningPlanGenerator

# 创建生成器实例
generator = LearningPlanGenerator()

# 生成学习计划
plan_data = generator.generate_learning_plan(
    subject="数学",
    weakness_area="分数运算",
    grade_level="小学三年级",
    duration_days=30
)

# 保存计划到文件
if plan_data:
    generator.save_plan_to_files(plan_data)
```

## 详细使用示例

### 示例1：生成数学学习计划

```python
from learning_plan_generator import LearningPlanGenerator

generator = LearningPlanGenerator()

# 生成小学三年级数学分数运算学习计划
plan_data = generator.generate_learning_plan(
    subject="数学",
    weakness_area="分数运算",
    grade_level="小学三年级",
    duration_days=30
)

if plan_data:
    print(f"计划生成成功！共{plan_data['duration_days']}天")
    print(f"计划概述：{plan_data['plan_summary']}")
    
    # 保存计划
    generator.save_plan_to_files(plan_data)
    
    # 查看第一天内容
    first_day = plan_data['daily_plans'][0]
    print(f"\n第一天学习目标：{first_day['learning_objective']}")
    print(f"练习题数量：{len(first_day['exercises'])}")
```

### 示例2：生成英语学习计划

```python
# 生成初中一年级英语阅读理解学习计划
plan_data = generator.generate_learning_plan(
    subject="英语",
    weakness_area="阅读理解",
    grade_level="初中一年级",
    duration_days=21
)

if plan_data:
    generator.save_plan_to_files(plan_data)
    print("英语学习计划已生成并保存")
```

### 示例3：生成特定天数的练习题

```python
# 为第5天生成额外的练习题
exercise_data = generator.generate_exercise_for_day(
    subject="数学",
    weakness_area="分数运算",
    grade_level="小学三年级",
    day_number=5,
    difficulty="较难"
)

if exercise_data:
    print(f"第{exercise_data['day']}天练习题生成成功")
    print(f"难度：{exercise_data['difficulty']}")
    print(f"练习题数量：{len(exercise_data['exercises'])}")
    
    # 显示第一道题
    first_exercise = exercise_data['exercises'][0]
    print(f"\n第一道题：")
    print(f"类型：{first_exercise['type']}")
    print(f"题目：{first_exercise['question']}")
    print(f"答案：{first_exercise['answer']}")
```

### 示例4：批量生成多个学科的学习计划

```python
def generate_multiple_subjects_plans():
    """批量生成多个学科的学习计划"""
    
    generator = LearningPlanGenerator()
    
    # 定义要生成的学习计划
    plans_config = [
        {
            "subject": "数学",
            "weakness_area": "分数运算",
            "grade_level": "小学三年级",
            "duration_days": 30
        },
        {
            "subject": "英语",
            "weakness_area": "阅读理解",
            "grade_level": "初中一年级",
            "duration_days": 21
        },
        {
            "subject": "语文",
            "weakness_area": "作文写作",
            "grade_level": "小学五年级",
            "duration_days": 15
        }
    ]
    
    for config in plans_config:
        print(f"正在生成{config['subject']}学习计划...")
        plan_data = generator.generate_learning_plan(**config)
        
        if plan_data:
            generator.save_plan_to_files(plan_data)
            print(f"✓ {config['subject']}学习计划生成成功")
        else:
            print(f"✗ {config['subject']}学习计划生成失败")
        
        print("-" * 50)

generate_multiple_subjects_plans()
```

## 输出文件结构

生成的学习计划会保存在 `learning_plans` 目录下，结构如下：

```
learning_plans/
├── 数学/
│   ├── 数学_分数运算_20240101_120000_plan.json    # 完整计划JSON
│   ├── 数学_分数运算_20240101_120000_day01.json   # 第1天计划
│   ├── 数学_分数运算_20240101_120000_day02.json   # 第2天计划
│   └── 数学_分数运算_20240101_120000_plan.txt    # 可读文本格式
├── 英语/
│   ├── 英语_阅读理解_20240101_120500_plan.json
│   ├── 英语_阅读理解_20240101_120500_day01.json
│   └── 英语_阅读理解_20240101_120500_plan.txt
└── 语文/
    ├── 语文_作文写作_20240101_121000_plan.json
    ├── 语文_作文写作_20240101_121000_day01.json
    └── 语文_作文写作_20240101_121000_plan.txt
```

## 生成的学习计划内容示例

### JSON格式结构

```json
{
  "subject": "数学",
  "weakness_area": "分数运算",
  "grade_level": "小学三年级",
  "duration_days": 7,
  "plan_summary": "本计划针对小学三年级学生在分数运算方面的薄弱环节设计...",
  "daily_plans": [
    {
      "day": 1,
      "date": "2024-01-01",
      "learning_objective": "理解分数的基本概念",
      "knowledge_points": "分数是表示部分与整体关系的数...",
      "exercises": [
        {
          "type": "选择题",
          "question": "下列哪个图形表示1/2？",
          "options": ["A. 圆形的一半", "B. 圆形的1/3", "C. 圆形的1/4", "D. 整个圆形"],
          "answer": "A",
          "explanation": "1/2表示将整体平均分成2份，取其中的1份..."
        }
      ]
    }
  ]
}
```

### 文本格式示例

```
============================================================
学习计划：数学 - 分数运算
============================================================

年级：小学三年级
计划天数：7天

计划概述：
本计划针对小学三年级学生在分数运算方面的薄弱环节设计...

============================================================
每日学习计划
============================================================

第1天 (2024-01-01)
----------------------------------------
学习目标：理解分数的基本概念

知识点讲解：
分数是表示部分与整体关系的数...

练习题：
1. [选择题] 下列哪个图形表示1/2？
   选项：
   A. 圆形的一半
   B. 圆形的1/3
   C. 圆形的1/4
   D. 整个圆形
   答案：A
   解析：1/2表示将整体平均分成2份，取其中的1份...
```

## 高级功能

### 1. 更新特定天数的练习题

```python
# 更新第3天的练习题
new_exercise_data = generator.generate_exercise_for_day(
    subject="数学",
    weakness_area="分数运算",
    grade_level="小学三年级",
    day_number=3,
    difficulty="中等"
)

if new_exercise_data:
    # 假设计划文件路径
    plan_file_path = "learning_plans/数学/数学_分数运算_20240101_120000_plan.json"
    generator.update_daily_exercise(plan_file_path, 3, new_exercise_data)
```

### 2. 自定义生成参数

```python
# 创建生成器时指定不同的配置文件
generator = LearningPlanGenerator("custom_config.json")

# 生成计划时使用更低的temperature以获得更一致的结果
plan_data = generator.generate_learning_plan(
    subject="数学",
    weakness_area="分数运算",
    grade_level="小学三年级",
    duration_days=30
)
```

### 3. 错误处理和重试

```python
def safe_generate_plan(generator, subject, weakness_area, grade_level, duration_days):
    """安全地生成学习计划，包含错误处理"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            plan_data = generator.generate_learning_plan(
                subject, weakness_area, grade_level, duration_days
            )
            
            if plan_data:
                generator.save_plan_to_files(plan_data)
                return True
            else:
                print(f"第{attempt + 1}次尝试：生成计划失败")
                
        except Exception as e:
            print(f"第{attempt + 1}次尝试出错：{e}")
        
        if attempt < max_retries - 1:
            print("等待5秒后重试...")
            time.sleep(5)
    
    print("所有尝试都失败了")
    return False

# 使用安全生成函数
success = safe_generate_plan(
    generator,
    subject="数学",
    weakness_area="分数运算",
    grade_level="小学三年级",
    duration_days=30
)
```

## 最佳实践

### 1. API密钥安全

- 不要将API密钥硬编码在代码中
- 使用配置文件管理密钥
- 将配置文件添加到 `.gitignore` 中
- 考虑使用环境变量存储敏感信息

### 2. 生成参数优化

- **duration_days**：根据薄弱项的复杂程度调整，简单的薄弱项15-20天，复杂的薄弱项30-45天
- **temperature**：使用默认值0.7可以获得平衡的创造性和一致性
- **max_tokens**：确保足够的token来生成完整的学习计划

### 3. 内容质量控制

- 生成后检查学习计划的质量和适用性
- 根据实际情况调整练习题的难度
- 定期更新学习计划以适应孩子的进步

### 4. 性能优化

- 批量生成多个计划时，添加适当的延迟以避免API限制
- 缓存已生成的计划，避免重复生成
- 使用异步处理提高效率（对于大规模应用）

## 常见问题解答

### Q: 如何处理API调用失败的情况？

A: 框架内置了重试机制，您也可以：
1. 增加重试次数
2. 延长超时时间
3. 实现更复杂的错误处理逻辑

### Q: 生成的练习题太难或太简单怎么办？

A: 可以：
1. 调整生成练习题时的difficulty参数
2. 手动编辑生成的练习题
3. 重新生成特定天数的练习题

### Q: 如何自定义学习计划的格式？

A: 您可以：
1. 修改`_generate_readable_plan`方法来自定义文本格式
2. 创建新的导出格式（如HTML、Markdown等）
3. 自定义JSON结构以满足特定需求

### Q: 支持哪些学科和年级？

A: 理论上支持所有学科和年级，只要在调用时正确指定：
- subject: 任意学科名称
- weakness_area: 任意薄弱项描述
- grade_level: 任意年级描述

## 扩展功能建议

1. **进度跟踪**：添加学习进度跟踪功能
2. **性能分析**：记录孩子完成练习题的表现
3. **自适应学习**：根据孩子的表现自动调整难度
4. **多语言支持**：支持生成其他语言的学习计划
5. **家长报告**：生成家长可读的学习报告

通过这个框架，您可以轻松为孩子生成个性化的学习计划，帮助他们针对性地提高薄弱环节。

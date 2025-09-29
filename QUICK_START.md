# 快速开始指南

## 项目概述

这是一个英语学习内容生成系统，通过AI技术生成个性化的学习计划、单词、词法、句法、练习句子和练习题等内容。

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+和必要的依赖包：

```bash
pip install -r requirements.txt  # 如果有requirements.txt文件
```

### 2. 生成学习计划

```bash
# 使用独立版本生成学习计划
python english_learning_plan_standalone.py
```

### 3. 生成学习内容

```bash
# 使用新的统一入口生成各种学习内容
python english_learning_content_generator.py
```

## 主要功能

### 1. 学习计划生成
- 根据学习阶段、天数、每日学习时间生成个性化学习计划
- 支持小学、初中、高中不同阶段
- 包含词汇、词法、句法的详细规划

### 2. 每日单词学习
- 基于FSRS算法生成每日学习单词
- 按词性分类学习
- 智能复习安排

### 3. 词法学习
- 每日不同的词法内容
- 包含规则、示例、练习
- 进度跟踪确保内容不重复

### 4. 句法学习
- 每日不同的句法内容
- 包含结构、示例、练习
- 进度跟踪确保内容不重复

### 5. 练习句子生成
- AI生成基于当日学习内容的练习句子
- 包含目标单词、词法、句法
- 中英文对照

### 6. 练习题生成
- AI生成选择题、翻译题、填空题
- 基于当日学习内容
- 包含详细解析

## 使用示例

### 生成学习计划
```bash
python english_learning_plan_standalone.py
```
按提示输入：
- 学习阶段：第一阶段：基础巩固 (小学中高年级)
- 学习天数：60
- 每日学习时间：15分钟

### 生成学习内容
```bash
python english_learning_content_generator.py
```
选择要生成的内容类型：
1. 生成学习计划
2. 生成每日单词
3. 生成词法内容
4. 生成句法内容
5. 生成练习句子
6. 生成练习题
7. 查看学习计划
8. 退出

### 直接调用特定功能
```python
# 生成每日单词
from src.english.generate_daily_words import DailyWordsGenerator
generator = DailyWordsGenerator()
generator.generate_and_display()

# 生成词法内容
from src.english.generate_morphology_content import MorphologyContentGenerator
generator = MorphologyContentGenerator()
generator.generate_and_display()

# 生成句法内容
from src.english.generate_syntax_content import SyntaxContentGenerator
generator = SyntaxContentGenerator()
generator.generate_and_display()

# 生成练习句子
from src.english.generate_practice_sentences import PracticeSentencesGenerator
generator = PracticeSentencesGenerator()
generator.generate_and_display()

# 生成练习题
from src.english.generate_practice_exercises import PracticeExercisesGenerator
generator = PracticeExercisesGenerator()
generator.generate_and_display()
```

## 输出文件

### 学习计划
- 位置：`outputs/english/`
- 格式：`english_learning_plan_YYYYMMDD_HHMMSS.json`

### 学习进度
- 位置：`learning_data/english/`
- 文件：
  - `learning_progress.json` - 单词学习进度
  - `morphology_progress.json` - 词法学习进度
  - `syntax_progress.json` - 句法学习进度

## 配置说明

### 学习阶段配置
- 文件：`src/english/config/stage.md`
- 内容：各阶段词汇、词法、句法占比

### 词库配置
- 位置：`src/english/config/word_configs/`
- 包含：小学、初中、高中词汇库

### 词法配置
- 位置：`src/english/config/morphology_configs/`
- 包含：各阶段词法规则

### 句法配置
- 位置：`src/english/config/grammar_configs/`
- 包含：各阶段句法结构

## 故障排除

### 1. 导入错误
确保在项目根目录下运行脚本，或正确设置Python路径。

### 2. AI调用失败
检查AI API密钥配置，系统会自动使用备用方法生成内容。

### 3. 文件路径错误
确保输出目录存在，系统会自动创建必要的目录。

### 4. 学习进度问题
删除 `learning_data/english/` 下的进度文件可重置学习进度。

## 高级用法

### 自定义学习计划
修改 `src/english/config/stage.md` 文件调整各阶段内容占比。

### 添加新词库
在 `src/english/config/word_configs/` 目录下添加新的词库文件。

### 自定义AI提示词
修改 `src/english/english_prompt_generator.py` 文件调整AI提示词。

## 技术支持

如有问题，请查看：
1. `README.md` - 项目说明
2. `PROJECT_STRUCTURE.md` - 项目结构
3. `PRACTICE_EXERCISES_GENERATOR.md` - 练习题生成器文档
4. `DAILY_CONTENT_DIFFERENTIATION.md` - 每日内容差异化机制

## 更新日志

- 2025-01-28: 完成项目结构重组，所有脚本移至 `src/english/` 目录
- 2025-01-28: 实现AI驱动的练习题生成
- 2025-01-28: 实现AI驱动的练习句子生成
- 2025-01-28: 实现每日内容差异化机制
- 2025-01-28: 完成FSRS学习算法集成


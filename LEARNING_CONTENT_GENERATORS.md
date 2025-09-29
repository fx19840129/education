# 学习内容生成器系统

## 概述

本系统将原来的 `read_learning_plan.py` 重构为学习内容生成的主入口，并将各种学习内容生成功能分离成独立的脚本。每个生成器都按照学习计划中的具体配置来生成相应的学习内容。

## 文件结构

### 主入口脚本
- **`learning_content_generator.py`** - 学习内容生成器主入口，提供统一的菜单和调用接口

### 独立生成器脚本
- **`generate_daily_words.py`** - 每日单词学习内容生成器（基于FSRS算法）
- **`generate_morphology_content.py`** - 词法学习内容生成器
- **`generate_syntax_content.py`** - 句法学习内容生成器
- **`generate_practice_sentences.py`** - 练习句子生成器
- **`generate_practice_exercises.py`** - 练习题生成器

## 功能特点

### 1. 学习内容生成器主入口 (`learning_content_generator.py`)

**主要功能：**
- 列出所有可用的学习计划
- 查看学习计划摘要和词库来源信息
- 调用各种独立的内容生成器
- 提供统一的用户界面

**菜单选项：**
1. 列出所有学习计划
2. 查看计划摘要
3. 查看词库来源
4. 生成单词学习内容
5. 生成词法学习内容
6. 生成句法学习内容
7. 生成练习句子
8. 生成练习题
9. 退出

### 2. 每日单词生成器 (`generate_daily_words.py`)

**功能特点：**
- 基于FSRS算法生成每日单词学习内容
- 按词性分类显示学习内容
- 支持复习词和新词混合学习
- 显示单词难度和稳定性信息
- 支持导出学习计划到文件
- 提供词性学习摘要统计

**学习计划配置：**
- 每天学习数量：根据学习计划中的 `daily_learn_count` 配置
- 总学习数量：根据学习计划中的 `total_count` 配置
- 学习周期：根据学习计划中的 `total_study_cycles` 配置

### 3. 词法学习内容生成器 (`generate_morphology_content.py`)

**功能特点：**
- 按照学习计划中的词法配置生成学习内容
- 解析词法配置文件（`morphology_configs/`）
- 显示词法项目的规则、例句和学习重点
- 支持不同学习阶段的比例配置

**学习计划配置：**
- 每天学习数量：根据学习计划中的 `morphology.daily_learn_count` 配置
- 总学习数量：根据学习计划中的 `morphology.total_count` 配置
- 学习周期：根据学习计划中的 `morphology.total_study_cycles` 配置
- 比例配置：显示小学、初中、高中的比例分配

### 4. 句法学习内容生成器 (`generate_syntax_content.py`)

**功能特点：**
- 按照学习计划中的句法配置生成学习内容
- 解析句法配置文件（`grammar_configs/`）
- 显示句法结构的组件、例句和使用规则
- 支持不同学习阶段的比例配置

**学习计划配置：**
- 每天学习数量：根据学习计划中的 `syntax.daily_learn_count` 配置
- 总学习数量：根据学习计划中的 `syntax.total_count` 配置
- 学习周期：根据学习计划中的 `syntax.total_study_cycles` 配置
- 比例配置：显示小学、初中、高中的比例分配

### 5. 练习句子生成器 (`generate_practice_sentences.py`)

**功能特点：**
- 基于每日单词学习内容生成练习句子
- 按词性生成不同类型的句子模板
- 提供中英文对照
- 支持不同难度的句子生成

### 6. 练习题生成器 (`generate_practice_exercises.py`)

**功能特点：**
- 基于每日单词学习内容生成练习题
- 支持多种题型：选择题、填空题、翻译题、句子完成题
- 提供干扰选项和答案解析
- 按难度分级

## 使用方法

### 启动主入口
```bash
python learning_content_generator.py
```

### 直接使用独立生成器
```bash
# 生成单词学习内容
python generate_daily_words.py

# 生成词法学习内容
python generate_morphology_content.py

# 生成句法学习内容
python generate_syntax_content.py

# 生成练习句子
python generate_practice_sentences.py

# 生成练习题
python generate_practice_exercises.py
```

## 配置文件

### 学习计划文件
位置：`outputs/english/english_learning_plan_*.json`

包含以下配置：
- 各词性的学习配置（`study_plan`）
- 词法学习配置（`morphology`）
- 句法学习配置（`syntax`）
- 每个配置包含：`daily_learn_count`、`total_count`、`total_study_cycles`、比例信息

### 词法配置文件
位置：`src/english/config/morphology_configs/`
- `小学词法.json`
- `初中词法.json`
- `高中词法.json`

### 句法配置文件
位置：`src/english/config/grammar_configs/`
- `小学句法.json`
- `初中句法.json`
- `高中句法.json`

## 技术特点

1. **模块化设计**：每个生成器都是独立的脚本，可以单独使用
2. **配置驱动**：所有生成器都严格按照学习计划中的配置生成内容
3. **数据解析**：正确解析不同格式的配置文件（词法、句法）
4. **比例支持**：支持不同学习阶段的比例配置
5. **FSRS算法**：单词生成器使用FSRS算法进行智能复习安排
6. **统一接口**：主入口提供统一的调用接口和用户界面

## 输出示例

### 词法学习内容示例
```
📅 第1天 - 2025-09-28
   总词法项目: 2个
   学习配置: 每天2个，总计13个，学习周期7次
   比例配置: 小学100% + 初中0% + 高中0%

   📖 1. 连词 (Conjunction) (连接词、短语或句子的词。)
      描述: 连接词、短语或句子的词。
      难度: 3.0
      学习周期: 7次
      规则:
        - 学习并列连词 (and, but, or) 的基本用法。
        - 初步接触从属连词 (because, when - 初步)。
      例句:
        - and
        - but
        - or
```

### 句法学习内容示例
```
📅 第1天 - 2025-09-28
   总句法项目: 2个
   学习配置: 每天2个，总计16个，学习周期8次
   比例配置: 小学100% + 初中0% + 高中0%

   📖 1. 主谓宾结构 (Subject-Verb-Object) (包含主语、及物动词和直接宾语。)
      描述: 包含主语、及物动词和直接宾语。
      难度: 2.2
      学习周期: 8次
      结构: Subject (S), Verb (V - Transitive Verb), Object (O)
      例句:
        - I eat bread. (S V O)
        - They play football. (S V O)
```

## 总结

本系统成功将学习内容生成功能模块化，每个生成器都能按照学习计划中的具体配置生成相应的学习内容，提供了完整的学习内容生成解决方案。所有生成器都支持不同学习阶段的比例配置，确保学习内容的针对性和有效性。


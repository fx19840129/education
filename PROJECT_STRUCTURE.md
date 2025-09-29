# 项目结构说明

## 概述

本项目是一个英语学习内容生成系统，通过AI技术生成个性化的学习计划、单词、词法、句法、练习句子和练习题等内容。

## 目录结构

```
/Users/fengxiao/project/education/
├── README.md                                    # 项目说明文档
├── README_LEARNING_PLAN.md                     # 学习计划说明
├── README_SCRIPTS.md                           # 脚本使用说明
├── PRACTICE_EXERCISES_GENERATOR.md             # 练习题生成器文档
├── DAILY_CONTENT_DIFFERENTIATION.md            # 每日内容差异化机制文档
├── LEARNING_CONTENT_GENERATORS.md              # 学习内容生成器文档
├── PROJECT_STRUCTURE.md                        # 项目结构说明（本文件）
├── pyproject.toml                              # 项目配置
├── LICENSE                                      # 许可证
├── MANIFEST.in                                 # 包清单
│
├── 入口脚本/
│   ├── english_learning_plan_standalone.py     # 学习计划生成入口（独立版本）
│   └── english_learning_content_generator.py   # 学习内容生成入口（新版本）
│
├── src/                                        # 源代码目录
│   ├── __init__.py
│   ├── shared/                                 # 共享模块
│   │   ├── ai_framework/                       # AI框架
│   │   │   ├── unified_ai_client.py           # 统一AI客户端
│   │   │   ├── ai_model.py                    # AI模型定义
│   │   │   ├── prompt_template.py             # 提示词模板
│   │   │   ├── response_parser.py              # 响应解析器
│   │   │   ├── error_handler.py               # 错误处理
│   │   │   └── config.py                      # AI配置
│   │   ├── infrastructure/                     # 基础设施
│   │   └── learning_framework/                 # 学习框架
│   │
│   └── english/                                # 英语学习模块
│       ├── __init__.py
│       ├── english_prompt_generator.py         # 英语提示词生成器
│       │
│       ├── 内容生成脚本/                        # 移动后的脚本
│       │   ├── learning_content_generator.py  # 学习内容生成器主入口
│       │   ├── generate_daily_words.py        # 每日单词生成器
│       │   ├── generate_morphology_content.py # 词法内容生成器
│       │   ├── generate_syntax_content.py     # 句法内容生成器
│       │   ├── generate_practice_sentences.py # 练习句子生成器
│       │   ├── generate_practice_exercises.py # 练习题生成器
│       │   └── read_learning_plan.py          # 学习计划读取器
│       │
│       ├── services/                           # 服务层
│       │   ├── fsrs_learning_generator.py     # FSRS学习生成器
│       │   ├── vocab_selector.py              # 词库选择器
│       │   ├── simple_word_service.py         # 单词服务
│       │   ├── morphology_service.py          # 词法服务
│       │   └── syntax_service.py              # 句法服务
│       │
│       ├── config/                             # 配置文件
│       │   ├── stage.md                       # 学习阶段配置
│       │   ├── word_configs/                  # 单词库配置
│       │   │   ├── 小学英语单词.json
│       │   │   ├── 初中英语单词.json
│       │   │   ├── 高中英语单词.json
│       │   │   └── classified_by_pos/         # 按词性分类的单词
│       │   ├── morphology_configs/            # 词法配置
│       │   │   ├── 小学词法.json
│       │   │   ├── 初中词法.json
│       │   │   └── 高中词法.json
│       │   └── grammar_configs/               # 句法配置
│       │       ├── 小学句法.json
│       │       ├── 初中句法.json
│       │       └── 高中句法.json
│       │
│       ├── adapters/                          # 适配器
│       ├── generators/                        # 生成器
│       └── validators/                        # 验证器
│
├── learning_data/                              # 学习数据
│   ├── english/                               # 英语学习数据
│   │   ├── learning_progress.json            # 学习进度
│   │   ├── morphology_progress.json          # 词法学习进度
│   │   └── syntax_progress.json              # 句法学习进度
│   └── [其他学科]/                            # 其他学科数据
│
├── outputs/                                    # 输出目录
│   ├── english/                               # 英语输出
│   │   ├── english_learning_plan_*.json      # 学习计划文件
│   │   ├── learning_plans/                   # 学习计划目录
│   │   ├── word_plans/                       # 单词计划
│   │   ├── grammar_plans/                    # 语法计划
│   │   ├── reports/                          # 报告
│   │   └── exports/                          # 导出文件
│   └── [其他学科]/                            # 其他学科输出
│
└── tests/                                      # 测试目录
    ├── unit/                                  # 单元测试
    ├── integration/                           # 集成测试
    └── e2e/                                   # 端到端测试
```

## 核心模块说明

### 1. 入口脚本

#### `english_learning_plan_standalone.py`
- **功能**: 学习计划生成入口（独立版本）
- **特点**: 避免模块导入问题，直接集成所有功能
- **用途**: 生成英语学习计划JSON文件

#### `english_learning_content_generator.py`
- **功能**: 学习内容生成入口（新版本）
- **特点**: 调用位于 `src/english/` 目录下的各种内容生成脚本
- **用途**: 提供统一的学习内容生成界面

### 2. 内容生成脚本（位于 `src/english/`）

#### `learning_content_generator.py`
- **功能**: 学习内容生成器主入口
- **特点**: 提供学习计划管理、内容生成调度
- **依赖**: 其他所有生成器脚本

#### `generate_daily_words.py`
- **功能**: 每日单词生成器
- **特点**: 基于FSRS算法生成每日学习单词
- **输出**: 按词性分类的每日单词列表

#### `generate_morphology_content.py`
- **功能**: 词法内容生成器
- **特点**: 生成每日不同的词法学习内容
- **输出**: 词法规则、示例、练习

#### `generate_syntax_content.py`
- **功能**: 句法内容生成器
- **特点**: 生成每日不同的句法学习内容
- **输出**: 句法结构、示例、练习

#### `generate_practice_sentences.py`
- **功能**: 练习句子生成器
- **特点**: 通过AI生成基于当日学习内容的练习句子
- **输出**: 包含目标单词、词法、句法的练习句子

#### `generate_practice_exercises.py`
- **功能**: 练习题生成器
- **特点**: 通过AI生成选择题、翻译题、填空题
- **输出**: 多样化的练习题集合

#### `read_learning_plan.py`
- **功能**: 学习计划读取器
- **特点**: 提供学习计划查看和分析功能
- **输出**: 学习计划统计和详细信息

### 3. 服务层（位于 `src/english/services/`）

#### `fsrs_learning_generator.py`
- **功能**: FSRS学习生成器
- **特点**: 实现间隔重复学习算法
- **用途**: 智能安排单词复习时间

#### `vocab_selector.py`
- **功能**: 词库选择器
- **特点**: 根据学习阶段选择适当的词库
- **用途**: 管理词汇资源选择

#### `simple_word_service.py`
- **功能**: 单词服务
- **特点**: 提供单词统计和查询功能
- **用途**: 单词数据管理

### 4. 配置管理

#### `stage.md`
- **功能**: 学习阶段配置
- **内容**: 各阶段词汇、词法、句法占比
- **用途**: 指导内容生成比例

#### 词库配置文件
- **位置**: `src/english/config/word_configs/`
- **内容**: 小学、初中、高中词汇库
- **特点**: 按词性分类存储

## 使用方式

### 1. 生成学习计划
```bash
python english_learning_plan_standalone.py
```

### 2. 生成学习内容
```bash
python english_learning_content_generator.py
```

### 3. 直接调用特定生成器
```bash
# 生成每日单词
python -c "from src.english.generate_daily_words import DailyWordsGenerator; DailyWordsGenerator().generate_and_display()"

# 生成词法内容
python -c "from src.english.generate_morphology_content import MorphologyContentGenerator; MorphologyContentGenerator().generate_and_display()"
```

## 项目优势

1. **模块化设计**: 各功能模块独立，便于维护和扩展
2. **AI驱动**: 智能生成个性化学习内容
3. **统一接口**: 提供一致的使用体验
4. **灵活配置**: 支持多种学习阶段和内容类型
5. **进度跟踪**: 实现学习进度的持久化存储
6. **错误处理**: 完善的异常处理和备用机制

## 扩展性

- **新学科支持**: 可轻松添加其他学科的学习内容生成
- **新题型支持**: 可扩展更多练习题型
- **新AI模型**: 支持多种AI模型的切换
- **新学习算法**: 可替换或扩展学习算法

这个项目结构为英语学习系统提供了完整、灵活、可扩展的解决方案。


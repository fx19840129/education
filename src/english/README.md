# 🇺🇸 英语学科模块详细文档

## 📋 项目概述

英语学科模块是多学科智能学习系统的核心组成部分，采用模块化架构设计，基于FSRS算法和AI技术，提供完整的英语学习内容生成和管理功能。

### 🎯 核心功能
- **🧠 FSRS学习计划生成**: 基于遗忘曲线的智能学习计划
- **📚 AI内容生成**: GPT-4o-mini驱动的学习内容生成
- **📄 Word文档输出**: 专业格式的学习材料
- **🔄 学习进度跟踪**: 智能的学习进度管理
- **🎯 多阶段支持**: 小学、初中、高中学习阶段

## 📁 目录结构详解

```
src/english/
├── 📂 adapters/                    # 适配器层
│   ├── __init__.py                 # 包初始化文件
│   └── ai_client_adapter.py        # AI客户端适配器
├── 📂 config/                      # 配置文件目录
│   ├── 📂 grammar_configs/         # 语法配置文件
│   │   ├── 小学句法.json           # 小学语法规则配置
│   │   ├── 初中句法.json           # 初中语法规则配置
│   │   └── 高中句法.json           # 高中语法规则配置
│   ├── 📂 morphology_configs/      # 词法配置文件
│   │   ├── 小学词法.json           # 小学词法规则配置
│   │   ├── 初中词法.json           # 初中词法规则配置
│   │   └── 高中词法.json           # 高中词法规则配置
│   ├── 📂 word_configs/            # 词汇配置文件
│   │   ├── 小学英语单词.json       # 小学词汇表 (710个单词)
│   │   ├── 初中英语单词.json       # 初中词汇表 (2292个单词)
│   │   ├── 高中英语单词.json       # 高中词汇表
│   │   └── 📂 classified_by_pos/   # 按词性分类的词汇
│   │       ├── 小学_按词性分类.json
│   │       ├── 初中_按词性分类.json
│   │       └── 高中_按词性分类.json
│   ├── README.md                   # 配置说明文档
│   └── stage.md                    # 学习阶段定义文档
├── 📂 content_generators/          # 内容生成器模块
│   ├── __init__.py                 # 包初始化文件
│   ├── coordinate_learning_content.py  # 学习内容协调器
│   ├── daily_content_generator.py  # 每日内容生成器 (主要脚本)
│   ├── document_generator.py       # Word文档生成器
│   ├── generate_daily_content.py   # 每日内容生成脚本
│   ├── generate_grammar_content.py # 语法内容生成器
│   ├── generate_practice_exercises.py # 练习题生成器
│   ├── practice_content_generator.py  # 练习内容生成器
│   └── vocabulary_content_generator.py # 词汇内容生成器
├── 📂 core/                        # 核心功能模块
│   ├── __init__.py                 # 包初始化文件
│   ├── create_learning_plan.py     # 学习计划创建器 (主要脚本)
│   ├── generate_fsrs_template.py   # FSRS模板生成器
│   └── manage_learning_plan.py     # 学习计划管理器 (主要脚本)
├── 📂 docs/                        # 文档目录
│   ├── 小学                        # 小学学习文档
│   ├── 初中                        # 初中学习文档
│   └── 高中                        # 高中学习文档
├── 📂 generators/                  # 生成器模块
│   ├── __init__.py                 # 包初始化文件
│   ├── document_content_generator.py  # 文档内容生成器
│   └── exercise_content_generator.py  # 练习内容生成器
├── 📂 services/                    # 服务层模块
│   ├── __init__.py                 # 包初始化文件
│   ├── fsrs_learning_service.py    # FSRS学习服务
│   ├── sentence_syntax_service.py  # 句法服务
│   ├── vocabulary_selection_service.py # 词汇选择服务
│   ├── word_data_service.py        # 词汇数据服务
│   └── word_morphology_service.py  # 词法服务
├── 📂 utils/                       # 工具模块
│   ├── __init__.py                 # 包初始化文件
│   ├── ai_prompt_builder.py        # AI提示词构建器
│   ├── learning_plan_reader.py     # 学习计划读取器
│   └── word_data_loader.py         # 词汇数据加载器
├── 📂 validators/                  # 验证器模块
│   ├── __init__.py                 # 包初始化文件
│   ├── content_validator.py        # 内容验证器
│   ├── exercise_validator.py       # 练习题验证器
│   └── sentence_validator.py       # 句子验证器
├── __init__.py                     # 包初始化文件
└── README.md                       # 本文档
```

## 🔧 核心脚本详解

### 📂 core/ - 核心功能模块

#### 1. `create_learning_plan.py` - 学习计划创建器
**作用**: AI驱动的学习计划生成器，支持交互式创建FSRS学习计划

**主要类**: `EnglishLearningPlanAI`

**核心方法**:
- `__init__()`: 初始化AI学习计划生成器
- `_extract_json_from_content(content: str)`: 从AI响应中提取JSON内容
- `interactive_input()`: 交互式用户输入界面
- `convert_to_fsrs_standard_format(template: Dict)`: 将模板转换为FSRS标准格式
- `_print_fsrs_template_with_annotations(full_template: Dict)`: 打印带注释的FSRS模板
- `generate_fsrs_template(stage, days, minutes, ...)`: 生成FSRS学习计划模板
- `save_plan(plan: Dict, filename: str)`: 保存学习计划到文件
- `run()`: 运行交互式学习计划创建流程

**使用场景**: 
- 创建新的学习计划
- 设置学习参数（阶段、天数、时间）
- 生成FSRS算法模板

#### 2. `manage_learning_plan.py` - 学习计划管理器
**作用**: 管理已创建的学习计划，提供CRUD操作

**主要类**: `EnglishPlanManager`

**核心方法**:
- `__init__(base_dir)`: 初始化计划管理器
- `scan_plans()`: 扫描所有学习计划
- `_extract_plan_info(file_path, plan_type)`: 提取计划信息
- `create_index()`: 创建计划索引
- `list_plans(plan_type, limit)`: 列出学习计划
- `get_plan(plan_id, plan_type)`: 获取特定计划
- `delete_plan(plan_id, plan_type)`: 删除学习计划
- `export_plan(plan_id, plan_type, output_dir)`: 导出学习计划
- `batch_export(plan_ids, plan_type, output_dir)`: 批量导出计划
- `search_plans(query, search_fields)`: 搜索学习计划

**使用场景**:
- 查看现有学习计划
- 删除不需要的计划
- 导出计划数据
- 搜索特定计划

### 📂 content_generators/ - 内容生成器模块

#### 1. `daily_content_generator.py` - 每日内容生成器 ⭐
**作用**: 整合各个组件，生成完整的每日学习内容

**主要类**: `DailyContentGenerator`

**核心方法**:
- `__init__()`: 初始化每日内容生成器
- `_load_learning_plan(plan_file)`: 加载学习计划
- `_generate_daily_vocabulary(day, plan_data)`: 生成每日词汇内容
- `_generate_review_words(day, plan_data)`: 生成复习单词列表
- `_generate_daily_morphology(day, plan_data)`: 生成每日词法内容
- `_generate_daily_syntax(day, plan_data)`: 生成每日句法内容
- `_generate_practice_content(vocabulary, morphology, syntax)`: 生成练习内容
- `_generate_word_document(day, content)`: 生成Word文档
- `generate_daily_learning_content(days, start_day)`: 生成每日学习内容 (主要方法)
- `generate_single_day_content(day)`: 生成单天学习内容

**使用场景**:
- 生成每日学习材料
- 批量生成多天内容
- 输出Word文档

#### 2. `vocabulary_content_generator.py` - 词汇内容生成器
**作用**: 基于FSRS算法生成词汇学习内容

**主要类**: `VocabularyContentGenerator`

**核心方法**:
- `__init__()`: 初始化词汇内容生成器
- `_load_vocabulary_data(stage)`: 加载词汇数据
- `_calculate_daily_words(plan_data, day)`: 计算每日单词
- `_select_new_words(available_words, count, pos_distribution)`: 选择新学单词
- `_select_review_words(learned_words, day, count)`: 选择复习单词
- `generate_vocabulary_content(day, plan_data)`: 生成词汇内容 (主要方法)

#### 3. `practice_content_generator.py` - 练习内容生成器
**作用**: 生成练习句子和练习题

**主要类**: `PracticeContentGenerator`

**核心方法**:
- `__init__()`: 初始化练习内容生成器
- `_generate_practice_sentences_v2(vocabulary, morphology, syntax)`: 生成练习句子 (v2版本)
- `_generate_exercises_from_sentences(sentences, vocabulary)`: 从句子生成练习题
- `_validate_and_fix_exercises(exercises)`: 验证和修复练习题
- `generate_practice_content(vocabulary, morphology, syntax)`: 生成练习内容 (主要方法)

#### 4. `document_generator.py` - Word文档生成器
**作用**: 生成专业格式的Word学习文档

**主要类**: `DocumentGenerator`

**核心方法**:
- `__init__()`: 初始化文档生成器
- `_set_paragraph_spacing(paragraph)`: 设置段落间距
- `_add_header(doc, day, stage)`: 添加文档标题
- `_add_vocabulary_section(doc, vocabulary)`: 添加词汇部分
- `_add_morphology_section(doc, morphology)`: 添加词法部分
- `_add_syntax_section(doc, syntax)`: 添加句法部分
- `_add_practice_section(doc, practice)`: 添加练习部分
- `_add_answers_page(doc, practice)`: 添加答案页面
- `generate_word_document(day, content)`: 生成Word文档 (主要方法)

### 📂 services/ - 服务层模块

#### 1. `vocabulary_selection_service.py` - 词汇选择服务
**作用**: 提供智能的词汇选择算法

**主要类**: `VocabSelector`

**核心方法**:
- `__init__()`: 初始化词汇选择器
- `load_vocabulary_data(stage)`: 加载词汇数据
- `select_words_by_pos(words, pos_distribution)`: 按词性分布选择单词
- `calculate_pos_distribution(total_words)`: 计算词性分布
- `get_word_difficulty(word)`: 获取单词难度

#### 2. `word_morphology_service.py` - 词法服务
**作用**: 管理词法学习点数据

**主要类**: `MorphologyService`

**核心方法**:
- `__init__()`: 初始化词法服务
- `load_morphology_data(stage)`: 加载词法数据
- `get_morphology_content(stage, day, count)`: 获取词法内容
- `get_morphology_by_category(stage, category)`: 按类别获取词法点

#### 3. `sentence_syntax_service.py` - 句法服务
**作用**: 管理句法学习点数据

**主要类**: `SyntaxService`

**核心方法**:
- `__init__()`: 初始化句法服务
- `load_syntax_data(stage)`: 加载句法数据
- `get_syntax_content(stage, day, count)`: 获取句法内容
- `get_syntax_by_category(stage, category)`: 按类别获取句法点

### 📂 utils/ - 工具模块

#### 1. `ai_prompt_builder.py` - AI提示词构建器
**作用**: 构建各种AI任务的提示词

**主要类**: `EnglishLearningPromptGenerator`

**核心方法**:
- `__init__()`: 初始化提示词生成器
- `generate_practice_sentences_prompt_v2(vocabulary, morphology, syntax)`: 生成练习句子提示词 (v2版本)
- `generate_exercises_prompt(sentences, vocabulary)`: 生成练习题提示词
- `generate_validation_prompt(content, content_type)`: 生成验证提示词

#### 2. `learning_plan_reader.py` - 学习计划读取器
**作用**: 读取和解析学习计划文件

**主要功能**:
- 解析JSON格式的学习计划
- 提取计划统计信息
- 验证计划完整性

## 🚀 使用指南

### 1. 快速开始

#### 通过多学科系统使用 (推荐)
```bash
# 启动主系统
python main.py

# 选择: 1. 多学科系统
# 选择: 1. 🇺🇸 英语学习
# 选择功能:
# - 📋 创建学习计划
# - 🗂️ 管理学习计划  
# - 📚 生成学习内容
```

#### 直接调用脚本
```bash
# 创建学习计划
python src/english/core/create_learning_plan.py

# 管理学习计划
python src/english/core/manage_learning_plan.py

# 生成学习内容
python src/english/content_generators/daily_content_generator.py
```

### 2. 典型工作流程

#### 完整学习流程
1. **计划创建**: `create_learning_plan.py`
2. **内容生成**: `daily_content_generator.py`
3. **计划管理**: `manage_learning_plan.py`

### 3. 配置说明

#### 学习阶段配置
- **小学**: 基础词汇710个，简单语法
- **初中**: 进阶词汇2292个，复杂语法
- **高中**: 高级词汇，高级语法结构

#### AI模型配置
- **默认模型**: GPT-4o-mini
- **最大令牌**: 4000-5000
- **重试机制**: 3次重试
- **超时设置**: 60秒

## 📊 输出文件说明

### 学习计划文件
- **位置**: `outputs/english/plans/`
- **格式**: JSON
- **内容**: FSRS模板、学习参数、进度跟踪

### 学习内容文件
- **位置**: `outputs/english/vocabulary_content/`
- **格式**: JSON
- **内容**: 每日词汇、练习句子、练习题

### Word文档
- **位置**: `outputs/english/word_documents/`
- **格式**: .docx
- **内容**: 完整的学习材料，包含答案页

## 🔧 开发说明

### 添加新功能
1. 在相应的模块中添加新类或方法
2. 更新相关的服务层接口
3. 添加必要的验证逻辑
4. 更新文档说明

### 扩展AI功能
1. 在`ai_prompt_builder.py`中添加新的提示词
2. 在内容生成器中调用AI服务
3. 添加内容验证逻辑

### 自定义学习阶段
1. 在`config/`目录中添加新的配置文件
2. 更新`stage.md`文档
3. 修改相关的服务类

## 🐛 常见问题

### Q: 如何修改AI模型？
A: 修改`src/shared/infrastructure/config/ai_models.json`配置文件

### Q: 如何添加新的词汇？
A: 编辑`config/word_configs/`目录下的相应JSON文件

### Q: 如何自定义练习题类型？
A: 修改`practice_content_generator.py`中的练习题生成逻辑

### Q: Word文档格式如何调整？
A: 修改`document_generator.py`中的格式设置

---

**📚 祝您使用愉快！如有问题请参考各脚本的详细注释或联系开发团队。** ✨🎓📖

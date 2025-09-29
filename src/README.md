# 教育项目资源库

## 项目概述
本资源库包含多个学科的教育项目，每个项目都专注于特定的教育内容生成和管理。

## 学科分类
- **语文** (chinese) - 语文学习相关项目
- **数学** (math) - 数学学习相关项目  
- **英语** (english) - 英语学习相关项目
- **物理** (physics) - 物理学习相关项目
- **化学** (chemistry) - 化学学习相关项目
- **生物** (biology) - 生物学习相关项目
- **历史** (history) - 历史学习相关项目
- **地理** (geography) - 地理学习相关项目
- **道德法制** (ethics) - 道德法制学习相关项目

## 核心工具
所有项目都基于 `core_utils.py` 模块，提供以下核心功能：

### 文件管理 (FileManager)
- 目录创建和文件操作
- JSON和文本文件的读写
- 路径管理

### Prompt管理 (PromptManager)
- Prompt模板管理
- Prompt生成和历史记录
- 模板参数化

### 数据处理 (DataProcessor)
- 文本清理和格式化
- 关键词提取
- 表格数据格式化
- 文本分块处理

### 随机生成 (RandomGenerator)
- 随机数生成和列表操作
- 可重现的随机序列

### 项目基类 (EducationalProjectBase)
- 统一的项目管理接口
- 日志记录和报告生成
- 数据持久化

## 项目结构
```
educational_projects/
├── core_utils.py                    # 核心工具模块
├── README.md                        # 项目说明
├── chinese/                         # 语文学科
│   ├── reading_plan/               # 阅读计划项目
│   ├── writing_practice/           # 写作练习项目
│   └── ...
├── math/                           # 数学学科
│   ├── problem_generator/          # 题目生成器
│   ├── concept_explainer/          # 概念解释器
│   └── ...
├── english/                        # 英语学科
│   ├── learning_plan_generator/    # 学习计划生成器
│   ├── grammar_generator/          # 语法生成器
│   └── ...
├── physics/                        # 物理学科
│   ├── experiment_simulator/       # 实验模拟器
│   ├── formula_explainer/          # 公式解释器
│   └── ...
├── chemistry/                      # 化学学科
│   ├── reaction_simulator/        # 反应模拟器
│   ├── element_explorer/           # 元素探索器
│   └── ...
├── biology/                        # 生物学科
│   ├── species_classifier/         # 物种分类器
│   ├── ecosystem_simulator/        # 生态系统模拟器
│   └── ...
├── history/                        # 历史学科
│   ├── timeline_generator/         # 时间线生成器
│   ├── event_analyzer/             # 事件分析器
│   └── ...
├── geography/                      # 地理学科
│   ├── map_generator/              # 地图生成器
│   ├── location_explorer/          # 地点探索器
│   └── ...
└── ethics/                         # 道德法制学科
    ├── case_analyzer/              # 案例分析器
    ├── rule_explainer/             # 规则解释器
    └── ...
```

## 使用方法
1. 每个学科项目都继承自 `EducationalProjectBase` 基类
2. 项目专注于特定的prompt管理和数据处理
3. 使用统一的文件结构和命名规范
4. 支持独立运行和模块化调用

## 开发指南
1. 创建新项目时，继承 `EducationalProjectBase` 类
2. 实现 `_init_prompt_templates()` 方法定义项目特定的prompt模板
3. 使用核心工具类进行文件操作、数据处理等
4. 遵循统一的目录结构和命名规范

## 扩展性
- 支持添加新的学科和项目
- 模块化设计，易于维护和扩展
- 核心功能可复用，减少重复开发

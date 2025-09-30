# 英语目录结构重构计划

## 📋 项目概述

**目标**: 重新规划和规范化英语学习模块的目录结构，为后续其他科目的开发建立标准化模板。

**当前问题**:
1. 根目录下脚本过多，缺乏组织
2. 命名不一致，功能分类不清晰
3. 没有统一的架构模式
4. 不便于其他学科复用

## 🎯 新目录结构设计

### 目标结构
```
src/english/
├── core/                           # 🎯 核心功能模块
│   ├── __init__.py
│   ├── plan_manager.py            # 计划管理
│   ├── plan_creator.py            # 计划创建
│   └── fsrs_generator.py          # FSRS生成器
│
├── content_generators/             # 📝 内容生成器模块
│   ├── __init__.py
│   ├── daily_content_generator.py # 日常内容生成
│   ├── vocabulary_generator.py    # 词汇生成
│   ├── grammar_generator.py       # 语法生成（合并morphology+syntax）
│   ├── exercise_generator.py      # 练习生成
│   ├── sentence_generator.py      # 句子生成
│   └── content_coordinator.py     # 内容协调器
│
├── utils/                         # 🛠️ 工具模块
│   ├── __init__.py
│   ├── prompt_generator.py       # 提示词生成器
│   └── plan_reader.py            # 计划读取器
│
├── adapters/                     # 🔌 适配器（保持不变）
├── services/                     # 🏢 服务层（保持不变）
├── validators/                   # ✅ 验证器（保持不变）
├── config/                       # ⚙️ 配置（保持不变）
├── docs/                         # 📚 文档（保持不变）
└── README.md                     # 📖 文档（更新路径引用）
```

## 🔄 文件重命名映射表

| 当前文件名 | 新文件名 | 新路径 | 功能描述 |
|-----------|---------|--------|----------|
| `english_learning_plan_standalone.py` | `plan_creator.py` | `core/plan_creator.py` | 学习计划创建 |
| `english_plan_manager.py` | `plan_manager.py` | `core/plan_manager.py` | 学习计划管理 |
| `fsrs_template_generator.py` | `fsrs_generator.py` | `core/fsrs_generator.py` | FSRS模板生成 |
| `generate_daily_learning_document.py` | `daily_content_generator.py` | `content_generators/daily_content_generator.py` | 日常学习内容 |
| `generate_daily_words.py` | `vocabulary_generator.py` | `content_generators/vocabulary_generator.py` | 词汇内容生成 |
| `generate_morphology_content.py` | `grammar_generator.py` | `content_generators/grammar_generator.py` | 语法内容生成（合并） |
| `generate_syntax_content.py` | → 合并到 `grammar_generator.py` | `content_generators/grammar_generator.py` | 语法内容生成（合并） |
| `generate_practice_exercises.py` | `exercise_generator.py` | `content_generators/exercise_generator.py` | 练习题生成 |
| `generate_practice_sentences.py` | `sentence_generator.py` | `content_generators/sentence_generator.py` | 句子练习生成 |
| `learning_content_generator.py` | `content_coordinator.py` | `content_generators/content_coordinator.py` | 内容生成协调 |
| `english_prompt_generator.py` | `prompt_generator.py` | `utils/prompt_generator.py` | AI提示词生成 |
| `read_learning_plan.py` | `plan_reader.py` | `utils/plan_reader.py` | 学习计划读取 |

## 📝 命名规范

### 文件命名规范
- 使用 `snake_case`（下划线分隔）
- 功能清晰的 `动词+名词` 组合
- 避免冗余前缀（如 `english_`）
- 文件名应该明确表达功能

### 目录分组逻辑
- **core/**: 核心业务逻辑（计划相关的主要功能）
- **content_generators/**: 各种学习内容生成功能
- **utils/**: 工具和辅助功能
- **adapters/**, **services/**, **validators/**: 架构层（保持现有结构）

## 🚀 实施计划

### 阶段1: 准备工作
1. ✅ 分析当前结构和依赖关系
2. ✅ 设计新的目录结构
3. ✅ 制定重命名映射表
4. 🔲 创建新目录结构

### 阶段2: 核心模块重构
1. 🔲 创建 `core/` 目录
2. 🔲 移动和重命名核心脚本
3. 🔲 更新核心脚本的内部导入

### 阶段3: 内容生成器重构
1. 🔲 创建 `content_generators/` 目录
2. 🔲 移动和重命名内容生成脚本
3. 🔲 合并 morphology 和 syntax 生成器
4. 🔲 更新内部导入路径

### 阶段4: 工具模块重构
1. 🔲 创建 `utils/` 目录
2. 🔲 移动工具脚本
3. 🔲 更新导入路径

### 阶段5: 系统集成更新
1. 🔲 更新 `education_manager.py` 中的引用
2. 🔲 更新 `subjects/english_subject.py` 中的脚本路径
3. 🔲 更新所有 `__init__.py` 文件

### 阶段6: 文档和测试
1. 🔲 更新 `README.md` 文档
2. 🔲 更新使用示例和路径引用
3. 🔲 测试所有功能模块
4. 🔲 验证系统完整性

### 阶段7: 模板化
1. 🔲 创建其他学科的结构模板指南
2. 🔲 文档化最佳实践

## 📋 需要更新的外部引用

### 1. education_manager.py
- `subjects/english_subject.py` 中的 `script_path` 配置

### 2. 配置文件
- 检查是否有硬编码的脚本路径

### 3. 文档文件
- `README.md` 中的所有脚本路径引用
- 使用示例和命令行说明

## 🎯 预期收益

### 直接收益
1. **清晰的代码组织**: 按功能分类，易于维护
2. **一致的命名规范**: 提高代码可读性
3. **模块化设计**: 便于单独测试和开发

### 长期收益
1. **可复用的架构模式**: 其他学科可以直接复制此结构
2. **便于扩展**: 新功能可以清晰地归类
3. **降低维护成本**: 结构清晰减少查找时间

## 🧪 测试策略

### 功能测试
1. 测试所有重命名脚本的基本功能
2. 验证导入路径的正确性
3. 确保 education_manager 正常工作

### 集成测试
1. 测试完整的学习计划创建流程
2. 测试内容生成功能
3. 验证所有模块间的协作

## 🔄 回滚计划

如果重构过程中出现问题：
1. 保留原始文件的备份
2. 使用 git 版本控制跟踪每个步骤
3. 准备回滚脚本恢复原始结构

## 📚 其他学科模板

重构完成后，其他学科可以使用相同的结构：

```
src/{subject}/
├── core/                    # 核心功能（计划管理等）
├── content_generators/      # 内容生成器
├── utils/                   # 工具模块
├── adapters/               # 适配器
├── services/               # 服务层
├── validators/             # 验证器
├── config/                 # 配置
└── docs/                   # 文档
```

---

**开始实施**: 准备就绪，可以开始执行重构计划！ 🚀

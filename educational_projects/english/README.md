# 英语学习系统

## 项目概述

这是一个完整的英语学习系统，包含单词学习、语法学习和综合学习计划功能。系统采用模块化设计，支持生成Word文档，提供滚动式复习和个性化学习计划。

## 主要功能

### 1. 增强版6个月学习计划
- **特点**：单词、语法、句子有机结合，加强记忆效果
- **功能**：生成每日学习计划，包含具体单词和句子
- **练习题**：包含填空、翻译、选择题、句子完成等多种题型
- **滚动复习**：按照遗忘曲线安排复习内容

### 1.1 按阶段生成学习计划
- **特点**：支持生成指定阶段的完整学习计划
- **功能**：每个阶段4周，包含详细的周计划和日安排
- **输出**：Word文档、JSON数据文件、文本总结
- **阶段**：6个学习阶段，从基础到高级

### 1.2 自定义学习计划生成器
- **特点**：完全自定义的学习计划制定
- **功能**：用户指定计划时长、每日学习时间，系统自动规划学习内容
- **智能分配**：根据学习时间自动选择学习模式（强化/标准/轻松）
- **详细统计**：告知计划时长内会学习到多少单词、语法点、练习题

### 1.3 学习计划管理器
- **特点**：完整的计划生命周期管理
- **功能**：创建、保存、列出、选择计划并生成具体学习内容
- **多格式输出**：支持控制台显示和Word文档输出
- **计划管理**：支持删除、导出等管理操作

### 2. 语法学习系统
- **特点**：模块化设计，支持10种题型
- **功能**：生成语法练习和Word文档
- **覆盖范围**：小学和初中语法点

### 3. 单词学习系统
- **特点**：多样化练习，智能随机化
- **功能**：生成单词练习和学习计划
- **数据库**：小学710个单词，初中2292个单词

## 脚本命令总览

### 学习计划相关脚本

#### 增强版6个月学习计划
```bash
# 生成单日学习计划
python enhanced_plan_main.py --day 1
python enhanced_plan_main.py --day 50

# 生成多日学习计划
python enhanced_plan_main.py --days 7
python enhanced_plan_main.py --days 30

# 生成所有180天学习计划
python enhanced_plan_main.py --all
```

#### 按阶段生成学习计划
```bash
# 生成指定阶段计划
python generate_phase_plan.py --phase 1
python generate_phase_plan.py --phase 3

# 列出所有可用阶段
python generate_phase_plan.py --list-phases
```

#### 自定义学习计划生成器
```bash
# 基础使用
python custom_plan_generator.py --days 30 --minutes 30

# 指定学习阶段
python custom_plan_generator.py --days 60 --minutes 20 --stage beginner
python custom_plan_generator.py --days 30 --minutes 45 --stage advanced

# 完全自定义
python custom_plan_generator.py --days 14 --minutes 20 --words 8 --grammar 2 --exercises 15

# 查看所有可用阶段
python custom_plan_generator.py --list-stages
```

#### 学习计划管理器
```bash
# 创建学习计划
python plan_manager.py create --name "我的30天计划" --days 30 --minutes 30

# 管理学习计划
python plan_manager.py list
python plan_manager.py show --id <计划ID>
python plan_manager.py delete --id <计划ID>
python plan_manager.py export --id <计划ID> --output my_plan.json

# 生成学习内容
python plan_manager.py daily --id <计划ID> --day 1
python plan_manager.py daily --id <计划ID> --day 1 --format word
python plan_manager.py multi --id <计划ID> --start-day 1 --days 7
```

### 语法学习相关脚本

#### 生成语法练习
```bash
# 生成单个语法点练习
python improved_grammar_main.py --grammar "一般现在时-基础用法" --level elementary --format word --exercises 30
python improved_grammar_main.py --grammar "被动语态-基础用法" --level middle_school --format word --exercises 30

# 生成所有语法练习
python improved_grammar_main.py --all --level elementary --format word --exercises 30
python improved_grammar_main.py --all --level middle_school --format word --exercises 30

# 按难度生成语法练习
python improved_grammar_main.py --by-difficulty --level elementary --difficulty easy --format word --exercises 30
python improved_grammar_main.py --by-difficulty --level middle_school --difficulty medium --format word --exercises 30

# 搜索和查看语法点
python improved_grammar_main.py --list
python improved_grammar_main.py --search "动词"
```

### 单词学习相关脚本

#### 生成单词练习
```bash
# 生成单词练习
python word_learning_main.py --level elementary --count 20 --format word
python word_learning_main.py --level middle_school --count 30 --format word

# 生成单词学习计划
python word_learning_main.py --action plan --level elementary --duration 30 --daily-words 10
python word_learning_main.py --action plan --level middle_school --duration 60 --daily-words 15

# 搜索单词
python word_learning_main.py --action search --keyword "apple"
python word_learning_main.py --action list --level elementary
```

## 使用说明

### 快速开始

#### 1. 基础学习计划（推荐新手）
```bash
# 创建30天学习计划
python plan_manager.py create --name "我的第一个计划" --days 30 --minutes 30 --stage beginner

# 查看计划
python plan_manager.py list

# 生成第1天学习内容
python plan_manager.py daily --id <计划ID> --day 1
```

#### 2. 进阶学习计划（有基础用户）
```bash
# 创建60天综合计划
python plan_manager.py create --name "进阶计划" --days 60 --minutes 45 --stage intermediate

# 生成一周学习内容（Word文档）
python plan_manager.py multi --id <计划ID> --start-day 1 --days 7 --format word
```

#### 3. 高级学习计划（基础较好用户）
```bash
# 创建90天强化计划
python plan_manager.py create --name "强化计划" --days 90 --minutes 60 --stage advanced

# 生成单天Word文档
python plan_manager.py daily --id <计划ID> --day 1 --format word
```

### 学习阶段说明

| 阶段 | 内容比例 | 适合人群 | 学习目标 |
|------|----------|----------|----------|
| **beginner** | 100%小学内容 | 零基础学习者 | 掌握基础词汇500-800个，学会基本语法结构 |
| **intermediate** | 50%小学+50%初中 | 有一定基础的学习者 | 平衡发展，巩固基础，提升能力 |
| **advanced** | 100%初中内容 | 基础较好的学习者 | 掌握高级语法，扩大词汇量 |
| **comprehensive** | 40%小学+60%初中 | 全面复习的学习者 | 综合复习，查漏补缺 |

### 学习模式说明

| 每日时间 | 学习模式 | 特点 | 适用场景 |
|----------|----------|------|----------|
| **≥50分钟** | 强化学习 | 高强度，快速提升 | 假期集中学习 |
| **25-49分钟** | 标准学习 | 平衡发展，稳步提升 | 日常学习 |
| **<25分钟** | 轻松学习 | 轻松愉快，保持兴趣 | 忙碌时期 |

### 输出格式说明

| 格式 | 特点 | 适用场景 |
|------|------|----------|
| **console** | 控制台显示，快速查看 | 日常学习，快速浏览 |
| **word** | Word文档，专业排版 | 打印学习，长期保存 |

## 参数说明

### 学习计划管理器参数

#### 创建计划 (create)
- `--name`: 计划名称（必需）
- `--days, -d`: 计划时长（天数，必需）
- `--minutes, -m`: 每日学习时间（分钟，必需）
- `--stage`: 学习阶段 (beginner/intermediate/advanced/comprehensive，默认intermediate)
- `--words`: 自定义每日单词数
- `--grammar`: 自定义每日语法点数
- `--exercises`: 自定义每日练习题数
- `--start-date, -s`: 开始日期 (YYYY-MM-DD)

#### 管理计划
- `list`: 列出所有已保存的计划
- `show --id <计划ID>`: 显示计划详细信息
- `delete --id <计划ID>`: 删除计划
- `export --id <计划ID> --output <文件路径>`: 导出计划

#### 生成内容
- `daily --id <计划ID> --day <天数> [--format console/word]`: 生成单天学习内容
- `multi --id <计划ID> --start-day <开始天数> --days <天数> [--format console/word]`: 生成多天学习内容

### 语法学习参数
- `--grammar`: 指定语法点名称
- `--level`: 年级级别 (elementary/middle_school)
- `--difficulty`: 难度级别 (easy/medium/hard)
- `--format, -f`: 输出格式 (markdown/word，默认markdown)
- `--exercises`: 练习题数量（默认30）
- `--all, -a`: 生成所有语法点
- `--by-difficulty`: 根据难度生成语法点
- `--list`: 列出可用的语法点
- `--search, -s`: 搜索包含关键词的语法点

### 单词学习参数
- `--level, -l`: 年级级别 (elementary/middle_school)
- `--difficulty, -d`: 难度级别 (easy/medium/hard)
- `--category, -c`: 单词分类
- `--count, -n`: 单词数量（默认30）
- `--format, -f`: 输出格式 (markdown/word，默认word)
- `--action, -a`: 操作类型 (exercises/plan/list/search，默认exercises)
- `--duration`: 学习计划天数（默认30）
- `--daily-words`: 每日学习单词数（默认10）
- `--keyword, -k`: 搜索关键词

## 学习策略

### 1. 滚动式记忆
- 按照遗忘曲线规律安排复习
- 复习间隔：1天、3天、7天、14天、30天
- 定期回顾已学内容，巩固记忆

### 2. 单词与语法结合
- 每个单词都生成包含相应语法的句子
- 在语境中学习单词，加深理解
- 通过语法规则巩固单词记忆

### 3. 多感官学习
- 视觉：看单词和句子
- 听觉：读出发音
- 触觉：手写练习
- 口语：大声朗读

### 4. 渐进式难度
- 从基础单词和语法开始
- 逐步增加难度和复杂度
- 保持学习的连续性

## 输出文档

### Word文档格式
- **专业排版**：使用Word格式，支持专业排版
- **完整内容**：包含单词列表、练习题、学习计划等
- **分离答案**：练习题和答案分别生成文档
- **优化布局**：紧凑排版，节省纸张

### 文档内容
1. **学习内容概览**：阶段信息、单词统计、语法主题
2. **今日单词**：单词列表、音标、词性、中文释义
3. **今日语法**：语法主题、级别、学习重点
4. **综合句子**：结合单词和语法的实用句子
5. **练习题**：填空、翻译、选择题、句子完成等多种题型
6. **练习题答案**：所有练习题的答案和详细解释（单独一页）

## 文件结构

```
educational_projects/english/
├── plan_manager.py              # 学习计划管理器
├── custom_plan_generator.py     # 自定义计划生成器
├── generate_phase_plan.py       # 阶段计划生成器
├── enhanced_plan_main.py        # 增强版6个月计划
├── improved_grammar_main.py     # 语法学习主程序
├── word_learning_main.py        # 单词学习主程序
├── plan_modules/                # 计划生成模块
├── grammar_modules/             # 语法学习模块
├── word_learning_modules/       # 单词学习模块
├── word_configs/                # 单词配置文件
├── grammar_configs/             # 语法配置文件
├── saved_plans/                 # 保存的学习计划
└── word_learning_details/       # 学习计划输出目录
```

## 常见问题

### Q: 如何选择合适的计划？
A: 根据您的英语基础选择学习阶段：
- 零基础：选择 beginner 阶段
- 有基础：选择 intermediate 阶段
- 基础较好：选择 advanced 阶段
- 全面复习：选择 comprehensive 阶段

### Q: 计划可以修改吗？
A: 目前计划创建后不能直接修改，但可以：
- 删除旧计划，创建新计划
- 使用自定义参数创建符合需求的计划

### Q: 如何查看学习进度？
A: 使用 `python plan_manager.py show --id <计划ID>` 查看计划统计信息，包括总词汇量、语法点、练习题等。

### Q: 生成的Word文档在哪里？
A: Word文档默认保存在 `word_learning_details/` 目录下，文件名包含日期和天数信息。

### Q: 如何备份学习计划？
A: 使用 `python plan_manager.py export --id <计划ID> --output <文件名>.json` 导出计划数据。

## 技术支持

如有问题或建议，请查看：
1. 本README文档的详细说明
2. 各脚本的 `--help` 参数
3. 系统生成的错误信息

---

**祝您学习愉快！** 🎓📚✨
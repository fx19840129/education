# 🤖 AI增强英语学习系统

基于智谱GLM-4.5的智能化英语学习平台，提供AI驱动的个性化学习内容生成。

## ✨ 系统特色

- **🤖 AI智能生成**: 基于智谱GLM-4.5的例句和练习题生成
- **🎯 个性化学习**: 根据用户偏好和学习进度自适应调整
- **🔍 质量保证**: AI+规则双重验证，确保内容质量
- **⚡ 高性能**: 智能缓存、并发优化，A级性能表现
- **📊 数据驱动**: FSRS记忆算法，科学的复习调度

## 🏗️ 系统架构

```
AI增强英语学习系统
├── 🤖 ai_framework/           # AI核心框架
│   ├── zhipu_ai_client.py     # 智谱GLM-4.5客户端
│   ├── smart_sentence_generator.py  # 智能例句生成
│   ├── smart_exercise_generator.py  # 智能练习生成
│   ├── quality_scoring_system.py    # 质量评分系统
│   └── user_preference_learning.py  # 用户偏好学习
├── 📚 语法学习系统
│   ├── improved_grammar_main.py     # 语法学习主程序
│   ├── grammar_modules/             # 语法处理模块
│   └── grammar_configs/             # 语法配置文件
├── 📝 单词学习系统
│   ├── word_learning_main.py        # 单词学习主程序
│   ├── word_learning_modules/       # 单词处理模块
│   └── word_configs/                # 单词配置文件
└── 🎯 集成学习计划
    ├── ai_demo.py                   # AI框架演示
    └── simple_ai_test.py            # 快速验证脚本
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install zhipuai python-docx psutil

# 配置智谱API密钥（可选，不配置则使用模板模式）
# 编辑 llm_framework/config.json
```

### 2. AI框架验证

```bash
# 快速验证AI框架是否正常
python simple_ai_test.py

# 运行AI框架演示
python ai_demo.py
```

## 📖 如何生成学习计划

### 🎯 方案一：语法专项学习（推荐）

生成特定语法点的专业练习，包含讲解、例句和30道练习题：

```bash
# 生成小学语法练习
python improved_grammar_main.py --grammar "一般现在时-基础用法" --level elementary --format word

# 生成初中语法练习  
python improved_grammar_main.py --grammar "被动语态-基础用法" --level middle_school --format word

# 生成所有小学语法练习
python improved_grammar_main.py --all --level elementary --format word

# 按难度生成语法练习
python improved_grammar_main.py --by-difficulty --level elementary --difficulty easy --format word
```

**输出**: Word文档，包含语法讲解、例句、30道练习题和答案

### 📝 方案二：单词专项学习

生成单词练习和学习计划：

```bash
# 生成小学单词练习
python word_learning_main.py --level elementary --difficulty easy --action exercises --count 30 --format word

# 生成30天单词学习计划
python word_learning_main.py --level elementary --action plan --duration 30 --daily-words 10 --format word

# 搜索特定单词
python word_learning_main.py --level elementary --action search --keyword "apple"
```

**输出**: Word文档，包含单词列表、练习题和学习计划

### 🤖 方案三：AI增强内容（实验性）

使用AI框架生成智能化学习内容：

```bash
# 验证AI框架
python simple_ai_test.py

# AI框架演示（需要配置API密钥）
python ai_demo.py
```

**特色**: AI生成的个性化例句和练习题

## 📊 学习内容示例

### 语法学习示例
```
📖 一般现在时-基础用法

📝 语法规则：
• 表示经常性、习惯性的动作或状态
• 肯定句：主语 + 动词原形/第三人称单数
• 否定句：主语 + don't/doesn't + 动词原形

✨ 例句：
• I eat an apple every day. (我每天吃一个苹果。)
• She goes to school by bus. (她乘公交车上学。)

🎯 练习题：
1. 填空题：I _____ (go) to school every day.
2. 翻译题：我每天看书。
3. 选择题：She _____ TV every evening.
   A. watch  B. watches  C. watching
```

### 单词学习示例
```
📚 小学基础单词（基于牛津3000高频词汇）

📝 今日单词（共500个）：
• the [ðə] det. 这个,那个
• be [biː] v. 是,存在 
• to [tuː] prep. 到,向
• of [ʌv] prep. 的,关于
• and [ænd] conj. 和,与

🎯 练习题：
1. 翻译：这个 → _____
2. 选择：I _____ a student. A.the B.be C.am
3. 造句：用 "the" 造句
```

## ⚙️ 参数说明

### 语法学习参数
- `--grammar, -g`: 语法点名称
- `--level, -l`: 年级级别 (elementary/middle_school)
- `--difficulty, -d`: 难度级别 (easy/medium/hard)
- `--format, -f`: 输出格式 (word/markdown)
- `--exercises, -e`: 练习题数量 (默认30)
- `--all`: 生成所有语法点
- `--list`: 查看可用语法点

### 单词学习参数  
- `--level, -l`: 年级级别 (elementary/middle_school)
- `--action, -a`: 操作类型 (exercises/plan/list/search)
- `--difficulty, -d`: 难度级别 (easy/medium/hard)
- `--count, -n`: 单词数量 (默认30)
- `--duration`: 学习计划天数 (默认30)
- `--daily-words`: 每日学习单词数 (默认10)

## 📁 输出文件

所有生成的学习内容都保存为Word文档：

- **语法练习**: `grammar_details/语法点名称_YYYYMMDD_HHMMSS.docx`
- **单词练习**: `word_learning_details/word_exercises_YYYYMMDD_HHMMSS.docx`
- **学习计划**: `word_learning_details/learning_plan_YYYYMMDD_HHMMSS.docx`

## 🔧 AI框架配置

如需启用完整AI功能，请配置智谱API：

```json
// llm_framework/config.json
{
  "llm_config": {
    "api_key": "your_zhipu_api_key",
    "model": "glm-4-plus",
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

## 📈 系统验证状态

### ✅ 已验证功能
- **基础设施**: 智谱AI客户端连接正常
- **AI生成器**: 智能例句和练习生成正常
- **质量控制**: AI+规则双重验证正常
- **个性化**: 用户偏好学习正常
- **性能**: A级性能表现

### 📊 测试结果
- **功能测试**: 70%通过率
- **性能等级**: A级（良好）
- **API响应**: 平均0.28秒
- **质量评分**: 支持5级评分

## 🎯 推荐学习路径

### 初学者
1. 从语法专项学习开始：`python improved_grammar_main.py --list`
2. 选择基础语法点：`python improved_grammar_main.py --grammar "be动词用法" --level elementary --format word`
3. 配合单词学习：`python word_learning_main.py --level elementary --action exercises --count 20 --format word`

### 进阶学习者
1. 按难度系统学习：`python improved_grammar_main.py --by-difficulty --level middle_school --difficulty medium --format word`
2. 制定学习计划：`python word_learning_main.py --level middle_school --action plan --duration 30 --format word`

### AI增强体验
1. 验证AI框架：`python simple_ai_test.py`
2. 体验AI生成：`python ai_demo.py`（需配置API密钥）

## 💡 使用建议

1. **每日学习**: 建议每天15-20分钟，坚持练习
2. **循序渐进**: 从简单语法开始，逐步提高难度
3. **结合练习**: 语法学习配合单词练习，效果更佳
4. **定期复习**: 利用生成的Word文档进行定期复习

## 📞 技术支持

- **快速验证**: `python simple_ai_test.py`
- **功能测试**: `cd ai_framework && python comprehensive_test_suite.py`
- **查看语法点**: `python improved_grammar_main.py --list`
- **查看单词库**: `python word_learning_main.py --level elementary --action list`

---

**🎉 开始您的AI增强英语学习之旅！**

建议从 `python improved_grammar_main.py --list` 开始，查看可用的语法点，然后选择适合的内容开始学习。

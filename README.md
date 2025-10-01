# 🎓 多学科智能学习系统

基于AI技术和FSRS算法的个性化多学科学习内容生成平台，支持英语、中文、数学等多个学科的智能化学习。

## ✨ 系统特色

- **🏗️ 模块化架构**: 支持多学科扩展的统一框架
- **🤖 AI智能生成**: GPT-4o-mini驱动的个性化学习内容
- **🧠 FSRS算法**: 基于遗忘曲线的科学复习调度
- **📄 专业输出**: Word文档格式的学习材料
- **🎯 多阶段支持**: 小学、初中、高中学习阶段
- **📊 进度跟踪**: 智能的学习进度管理系统

## 🏗️ 系统架构

```
多学科智能学习系统
├── 🎯 main.py                     # 统一入口脚本
├── 📂 src/                        # 源代码目录
│   ├── 🏗️ core/                   # 核心框架
│   │   ├── subject_base.py         # 学科基类
│   │   └── subject_manager.py      # 学科管理器
│   ├── 📚 subjects/                # 学科模块
│   │   ├── english_subject.py      # 🇺🇸 英语学科
│   │   ├── chinese_subject.py      # 🇨🇳 中文学科 (开发中)
│   │   └── math_subject.py         # 🔢 数学学科 (开发中)
│   ├── 🇺🇸 english/               # 英语学科实现
│   │   ├── core/                   # 核心功能
│   │   ├── content_generators/     # 内容生成器
│   │   ├── services/               # 服务层
│   │   ├── utils/                  # 工具模块
│   │   └── config/                 # 配置文件
│   └── 🔧 shared/                  # 共享框架
│       ├── ai_framework/           # AI框架
│       ├── learning_framework/     # 学习框架
│       └── infrastructure/         # 基础设施
├── 📁 outputs/                    # 输出文件目录
├── 💾 learning_data/              # 学习数据
└── 🧪 tests/                      # 测试目录
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/fx19840129/education.git
cd education

# 安装依赖
pip install -r requirements.txt

# 或手动安装主要依赖
pip install python-docx psutil openai
```

### 2. 启动系统

```bash
# 启动多学科学习系统
python main.py
```

### 3. 使用流程

1. **选择学科**: 从可用学科中选择（目前支持英语学科）
2. **选择功能**: 
   - 📋 创建学习计划
   - 🗂️ 管理学习计划
   - 📚 生成学习内容
3. **开始学习**: 按照生成的学习材料进行学习

## 📚 支持的学科

### 🇺🇸 英语学科 (完整功能)

**核心功能**:
- **FSRS学习计划**: 基于遗忘曲线的智能学习计划
- **AI内容生成**: GPT-4o-mini生成练习句子和题目
- **Word文档输出**: 专业格式的学习材料
- **多阶段支持**: 小学、初中、高中词汇和语法

**主要特性**:
- 📚 词汇学习: 710个小学词汇 + 2292个初中词汇
- 📝 练习生成: 100%新词覆盖的练习句子
- 🎯 练习题: 选择题、翻译题、填空题
- 📄 文档格式: 单倍行距、A/B/C/D选项、答案分页

**使用示例**:
```bash
# 通过主系统使用
python main.py
# 选择: 1. 多学科系统 → 1. 🇺🇸 英语学习 → 选择功能

# 或直接调用英语模块
python src/english/core/create_learning_plan.py      # 创建学习计划
python src/english/core/manage_learning_plan.py      # 管理学习计划
python src/english/content_generators/daily_content_generator.py  # 生成学习内容
```

### 🇨🇳 中文学科 (开发中)

**规划功能**:
- 📖 古诗词学习
- ✍️ 写作能力训练
- 📚 阅读理解练习
- 🎭 文言文学习

### 🔢 数学学科 (开发中)

**规划功能**:
- 🧮 公式推导练习
- 📐 几何图形生成
- 📊 数据分析训练
- 🎯 个性化习题生成

## 🎯 英语学科详细功能

### 📋 学习计划创建

**功能**: 创建基于FSRS算法的个性化学习计划

**特性**:
- 🎯 多阶段支持: 小学、初中、高中
- ⏰ 自定义学习时间: 每日学习时间设置
- 📊 智能词汇分配: 基于词性和难度的智能分配
- 🧠 FSRS算法: 科学的复习间隔计算

**使用方法**:
```bash
# 交互式创建学习计划
python src/english/core/create_learning_plan.py

# 按提示选择:
# 1. 学习阶段 (小学/初中/高中)
# 2. 学习天数 (建议30-90天)
# 3. 每日学习时间 (建议20-60分钟)
```

### 📚 学习内容生成

**功能**: 生成完整的每日学习内容

**生成内容**:
- 📝 每日词汇: 新学单词 + 复习单词
- 🔤 词法内容: 词汇变化规则和用法
- 📖 句法内容: 语法结构和句型
- 💬 练习句子: 100%新词覆盖的实用句子
- 🎯 练习题: 多样化的练习题型
- 📄 Word文档: 专业格式的学习材料

**使用方法**:
```bash
# 生成学习内容
python src/english/content_generators/daily_content_generator.py

# 功能选项:
# - 生成单天内容
# - 批量生成多天内容
# - 自定义生成参数
```

### 🗂️ 学习计划管理

**功能**: 管理已创建的学习计划

**管理功能**:
- 📊 查看现有计划
- 🔍 搜索特定计划
- 📤 导出计划数据
- 🗑️ 删除不需要的计划
- 📈 计划统计分析

**使用方法**:
```bash
# 管理学习计划
python src/english/core/manage_learning_plan.py

# 管理选项:
# - 列出所有计划
# - 查看计划详情
# - 导出计划数据
# - 删除计划
```

## 📊 输出文件说明

### 学习计划文件
- **位置**: `outputs/english/plans/`
- **格式**: JSON
- **内容**: FSRS模板、学习参数、词汇分配

### 学习内容文件
- **位置**: `outputs/english/vocabulary_content/`
- **格式**: JSON
- **内容**: 每日词汇、练习句子、练习题数据

### Word学习文档
- **位置**: `outputs/english/word_documents/`
- **格式**: .docx
- **内容**: 
  - 📚 今日词汇 (音标、词性、释义)
  - 📝 词法内容 (词汇变化规则)
  - 📖 句法内容 (语法结构)
  - 💬 练习句子 (结合词汇和语法)
  - 🎯 练习题 (选择题、翻译题、填空题)
  - 📋 答案页面 (独立答案页)

## ⚙️ 系统配置

### AI模型配置
- **默认模型**: GPT-4o-mini
- **配置文件**: `src/shared/infrastructure/config/ai_models.json`
- **主要参数**:
  - 最大令牌: 4000-5000
  - 重试次数: 3次
  - 超时时间: 60秒

### 学习阶段配置
- **小学阶段**: 710个基础词汇，简单语法结构
- **初中阶段**: 2292个进阶词汇，复杂语法规则
- **高中阶段**: 高级词汇，高级语法结构

## 🔧 开发指南

### 添加新学科

1. **创建学科类**:
```python
# src/subjects/new_subject.py
from src.core.subject_base import SubjectBase, SubjectFunction

class NewSubject(SubjectBase):
    def get_name(self) -> str:
        return "new_subject"
    
    def initialize_functions(self) -> List[SubjectFunction]:
        return [
            SubjectFunction(
                name="create_plan",
                display_name="📋 创建学习计划",
                description="生成个性化学习计划",
                script_path="src/new_subject/core/create_plan.py"
            )
        ]
```

2. **注册学科**:
```python
# src/core/subject_manager.py
subject_configs = [
    ("english", "src.subjects.english_subject", "EnglishSubject"),
    ("new_subject", "src.subjects.new_subject", "NewSubject"),  # 添加新学科
]
```

### 扩展英语功能

1. **添加新的内容生成器**:
   - 在 `src/english/content_generators/` 中添加新模块
   - 实现相应的生成逻辑
   - 更新 `daily_content_generator.py` 集成新功能

2. **添加新的服务**:
   - 在 `src/english/services/` 中添加新服务
   - 实现业务逻辑
   - 在相关生成器中调用服务

## 📈 性能特性

### 生成效率
- **单天内容**: 约30秒生成完整学习材料
- **Word文档**: 专业格式，包含完整答案页
- **批量生成**: 支持多天内容批量生成

### 内容质量
- **新词覆盖**: 100%新词在练习句子中出现
- **复习词覆盖**: 80%复习词在练习中出现
- **练习题质量**: AI生成，人工验证逻辑

### 系统稳定性
- **错误处理**: 完善的异常处理机制
- **重试机制**: AI调用失败自动重试
- **数据验证**: 多层数据验证确保质量

## 🐛 常见问题

### Q: 如何修改AI模型？
A: 编辑 `src/shared/infrastructure/config/ai_models.json` 配置文件，修改默认模型设置。

### Q: 如何添加新词汇？
A: 编辑 `src/english/config/word_configs/` 目录下的相应JSON文件，添加新词汇。

### Q: 如何自定义练习题类型？
A: 修改 `src/english/content_generators/practice_content_generator.py` 中的练习题生成逻辑。

### Q: Word文档格式如何调整？
A: 修改 `src/english/content_generators/document_generator.py` 中的格式设置。

### Q: 如何查看生成的学习计划？
A: 使用学习计划管理功能，或直接查看 `outputs/english/plans/` 目录下的JSON文件。

## 🔗 相关链接

- **GitHub仓库**: [https://github.com/fx19840129/education.git](https://github.com/fx19840129/education.git)
- **英语模块文档**: [src/english/README.md](src/english/README.md)
- **开发文档**: [docs/](docs/) (待完善)

## 📞 技术支持

### 快速诊断
```bash
# 测试系统功能
python main.py

# 测试英语模块
python -c "from src.core.subject_manager import SubjectManager; print('✅ 系统正常')"

# 查看系统状态
python main.py  # 选择: 2. 系统信息
```

### 日志和调试
- **日志位置**: 控制台输出
- **调试模式**: 修改脚本中的日志级别
- **错误报告**: 查看控制台错误信息

## 🎯 推荐学习路径

### 🔰 初学者路径
1. **启动系统**: `python main.py`
2. **创建计划**: 选择英语学科 → 创建学习计划
3. **生成内容**: 生成学习内容 → 开始学习
4. **管理进度**: 使用计划管理功能跟踪进度

### 🚀 高级用户路径
1. **自定义配置**: 修改AI模型和学习参数
2. **批量生成**: 生成多天学习内容
3. **扩展功能**: 添加新的学科或功能模块
4. **性能优化**: 调整生成参数和缓存策略

### 👨‍💻 开发者路径
1. **了解架构**: 阅读源码和文档
2. **添加学科**: 实现新的学科模块
3. **扩展功能**: 为现有学科添加新功能
4. **贡献代码**: 提交Pull Request

---

## 🎉 开始您的智能学习之旅！

```bash
# 一键启动
python main.py
```

**选择您感兴趣的学科，开始个性化的AI辅助学习体验！** 🚀📚✨

---

*本项目基于模块化架构设计，支持多学科扩展。目前英语学科功能完整，其他学科正在开发中。欢迎贡献代码和建议！* 💡🤝
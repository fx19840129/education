# 学科模块结构模板指南

## 📋 概述

基于英语学习模块的成功重构，本文档提供了一个标准化的学科模块结构模板，供其他学科（数学、物理、化学等）开发时参考使用。

## 🎯 设计原则

### 1. **模块化设计**
- 按功能分类组织代码
- 清晰的职责分离
- 便于维护和扩展

### 2. **命名规范**
- 使用 `snake_case` 命名文件
- 功能明确的 `动词+名词` 组合
- 避免学科前缀冗余

### 3. **结构一致性**
- 所有学科使用相同的目录结构
- 统一的导入路径模式
- 标准化的配置管理

## 📂 标准目录结构

```
src/{subject}/
├── # === 核心功能模块 ===
├── core/                               # 🎯 核心功能
│   ├── __init__.py
│   ├── create_learning_plan.py         # 学习计划创建器
│   ├── manage_learning_plan.py         # 学习计划管理器
│   └── generate_{subject}_template.py  # 学科特定生成器
├── 
├── # === 内容生成器模块 ===
├── content_generators/                 # 📝 内容生成器
│   ├── __init__.py
│   ├── coordinate_learning_content.py  # 内容生成协调器
│   ├── generate_{type}_content.py      # 各类型内容生成器
│   ├── generate_practice_exercises.py  # 练习题生成器
│   ├── generate_practice_content.py    # 练习内容生成器
│   └── generate_daily_learning_doc.py  # 日常学习文档生成器
├── 
├── # === 工具模块 ===
├── utils/                              # 🛠️ 工具模块
│   ├── __init__.py
│   ├── ai_prompt_builder.py            # AI提示词构建器
│   ├── learning_plan_reader.py         # 学习计划读取器
│   └── {subject}_utils.py              # 学科特定工具
├──
├── # === 架构层（保持不变）===
├── adapters/                           # 🔌 适配器层
│   ├── __init__.py
│   └── ai_client_adapter.py            # AI客户端适配器
├── services/                           # 🏢 服务层
│   ├── __init__.py
│   ├── {concept}_service.py            # 概念服务
│   └── {feature}_service.py            # 功能服务
├── validators/                         # ✅ 验证器
│   ├── __init__.py
│   └── {subject}_validator.py          # 学科验证器
├── config/                             # ⚙️ 配置
│   ├── README.md
│   └── {type}_configs/                 # 各类型配置
├── docs/                               # 📚 文档
│   └── {level}/                        # 学习阶段文档
├── generators/                         # 🏭 生成器（已有架构）
└── README.md                           # 📖 学科文档
```

## 🔧 实施步骤

### 步骤1: 创建基础目录结构
```bash
# 在 src/ 目录下创建新学科目录
mkdir -p src/{subject}/{core,content_generators,utils,adapters,services,validators,config,docs,generators}

# 创建 __init__.py 文件
touch src/{subject}/__init__.py
touch src/{subject}/core/__init__.py
touch src/{subject}/content_generators/__init__.py
touch src/{subject}/utils/__init__.py
touch src/{subject}/adapters/__init__.py
touch src/{subject}/services/__init__.py
touch src/{subject}/validators/__init__.py
```

### 步骤2: 创建核心脚本
基于学科特点创建核心功能脚本：

#### plan_creator.py 模板
```python
#!/usr/bin/env python3
"""
{学科名称}学习计划创建器
生成个性化的{学科}学习计划和模板
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入统一AI客户端
from src.shared.ai_framework.unified_ai_client import UnifiedAIClient, AIModel

# 导入提示词生成器
from src.{subject}.utils.prompt_generator import {Subject}PromptGenerator

class {Subject}PlanCreator:
    """
    {学科名称}学习计划创建器
    """
    def __init__(self):
        self.ai_client = UnifiedAIClient()
        self.prompt_generator = {Subject}PromptGenerator()
    
    def create_plan(self, **kwargs):
        """创建学习计划"""
        # 实现学科特定的计划创建逻辑
        pass

def main():
    """主程序入口"""
    creator = {Subject}PlanCreator()
    creator.create_plan()

if __name__ == "__main__":
    main()
```

### 步骤3: 配置学科注册
在 `src/subjects/{subject}_subject.py` 中注册学科：

```python
#!/usr/bin/env python3
"""
{学科名称}学科实现
包含{学科}学习的所有功能配置和特定实现
"""

from src.core.subject_base import SubjectBase, SubjectFunction

class {Subject}Subject(SubjectBase):
    """
    {学科名称}学科实现
    """
    
    def get_name(self) -> str:
        return "{subject}"
    
    def get_display_name(self) -> str:
        return "{emoji} {学科名称}学习"
    
    def get_description(self) -> str:
        return "{学科描述}"
    
    def initialize_functions(self) -> List[SubjectFunction]:
        """初始化{学科}功能"""
        return [
            SubjectFunction(
                name="create_plan",
                display_name="📋 创建学习计划",
                description="生成个性化的学习计划",
                script_path="src/{subject}/core/plan_creator.py",
                function_type="script"
            ),
            SubjectFunction(
                name="manage_plan",
                display_name="🗂️  管理学习计划",
                description="查看、搜索、删除、导出已有计划",
                script_path="src/{subject}/core/plan_manager.py",
                function_type="script"
            ),
            # 添加更多功能...
        ]
```

### 步骤4: 更新主系统注册
在 `src/core/subject_manager.py` 中添加新学科：

```python
# 在 _load_subject_modules 方法中添加
from src.subjects.{subject}_subject import {Subject}Subject

def _load_subject_modules(self):
    """加载所有学科模块"""
    try:
        # 现有学科...
        
        # 新学科
        {subject}_subject = {Subject}Subject(self.project_root)
        self.subjects[{subject}_subject.get_name()] = {subject}_subject
        print(f"✅ 已加载学科: {{{subject}_subject.get_display_name()}}")
        
    except Exception as e:
        print(f"⚠️  加载{学科}模块失败: {e}")
```

## 📝 学科特定适配

### 数学学科示例
```
src/math/
├── core/
│   ├── plan_creator.py                 # 数学学习计划创建器
│   ├── plan_manager.py                 # 数学计划管理器
│   └── formula_generator.py            # 公式生成器
├── content_generators/
│   ├── problem_generator.py            # 数学题目生成器
│   ├── solution_generator.py           # 解答生成器
│   ├── concept_generator.py            # 概念讲解生成器
│   └── visualization_generator.py      # 可视化内容生成器
├── utils/
│   ├── math_prompt_generator.py        # 数学AI提示词生成器
│   ├── formula_parser.py               # 公式解析器
│   └── graph_utils.py                  # 图形工具
├── services/
│   ├── algebra_service.py              # 代数服务
│   ├── geometry_service.py             # 几何服务
│   └── calculus_service.py             # 微积分服务
└── config/
    ├── formula_configs/                # 公式配置
    ├── problem_configs/                # 题目配置
    └── visualization_configs/          # 可视化配置
```

### 物理学科示例
```
src/physics/
├── core/
│   ├── plan_creator.py                 # 物理学习计划创建器
│   ├── experiment_designer.py          # 实验设计器
│   └── simulation_generator.py         # 模拟生成器
├── content_generators/
│   ├── concept_generator.py            # 物理概念生成器
│   ├── experiment_generator.py         # 实验内容生成器
│   ├── calculation_generator.py        # 计算题生成器
│   └── diagram_generator.py            # 物理图解生成器
├── services/
│   ├── mechanics_service.py            # 力学服务
│   ├── thermodynamics_service.py       # 热力学服务
│   └── electromagnetism_service.py     # 电磁学服务
└── config/
    ├── formula_configs/                # 物理公式配置
    ├── experiment_configs/             # 实验配置
    └── unit_configs/                   # 单位配置
```

## 🎯 最佳实践

### 1. **导入路径规范**
```python
# 标准导入模式
project_root = Path(__file__).parent.parent.parent.parent  # 根据文件深度调整
sys.path.insert(0, str(project_root))

# 统一AI客户端导入
from src.shared.ai_framework.unified_ai_client import UnifiedAIClient, AIModel

# 学科内部模块导入
from src.{subject}.utils.prompt_generator import {Subject}PromptGenerator
from src.{subject}.services.{service}_service import {Service}Service
```

### 2. **配置文件管理**
- 所有配置文件放在 `config/` 目录下
- 按类型分子目录组织
- 使用JSON格式便于AI处理
- 提供README说明配置结构

### 3. **AI提示词设计**
- 每个学科创建专门的提示词生成器
- 结合学科特点优化提示词
- 支持多种AI模型适配
- 包含学科特定的验证规则

### 4. **测试策略**
```python
# 在 tests/ 目录下创建学科测试
tests/{subject}/
├── unit/
│   ├── test_{subject}_plan_creator.py
│   └── test_{subject}_generators.py
├── integration/
│   └── test_{subject}_workflow.py
└── e2e/
    └── test_{subject}_complete_flow.py
```

## 🚀 快速开始新学科

### 使用脚本自动化创建（推荐）
```bash
# 创建新学科结构脚本
./scripts/create_subject.sh math "数学学习" "🔢" "数学概念、公式、习题等学习内容"
```

### 手动创建步骤
1. **复制英语模板**：将英语目录复制为新学科目录
2. **批量重命名**：使用查找替换工具更新所有文件中的引用
3. **学科定制**：根据学科特点修改具体实现
4. **系统注册**：在主系统中注册新学科
5. **测试验证**：确保所有功能正常工作

## 📋 检查清单

### ✅ 结构创建
- [ ] 创建标准目录结构
- [ ] 创建所有 `__init__.py` 文件
- [ ] 复制并修改核心脚本模板

### ✅ 系统集成
- [ ] 创建学科类并继承 `SubjectBase`
- [ ] 在 `SubjectManager` 中注册学科
- [ ] 更新主入口程序显示

### ✅ 功能实现
- [ ] 实现学科特定的计划创建逻辑
- [ ] 创建内容生成器
- [ ] 配置AI提示词生成器
- [ ] 设置学科配置文件

### ✅ 测试验证
- [ ] 单元测试覆盖核心功能
- [ ] 集成测试验证工作流
- [ ] 端到端测试完整流程
- [ ] 文档更新和维护

## 🔄 持续改进

### 版本控制
- 为每个学科模块建立独立的版本控制
- 使用语义化版本号
- 维护变更日志

### 性能优化
- 监控各学科模块的性能
- 优化AI调用频率和效率
- 缓存常用配置和数据

### 用户反馈
- 收集各学科的使用反馈
- 持续优化学习体验
- 定期更新学科内容

---

**注意**：本模板基于英语学习模块的成功实践，为其他学科提供了标准化的开发框架。请根据具体学科特点进行适当调整和定制。

## 📚 相关文档

- [英语学习模块重构总结](ENGLISH_STRUCTURE_REFACTOR_PLAN.md)
- [教育管理系统架构指南](MODULAR_SYSTEM_GUIDE.md)
- [统一AI框架使用指南](src/shared/ai_framework/README.md)

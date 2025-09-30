# 🎓 模块化教育管理系统指南

## 📋 系统概述

教育管理系统已成功重构为模块化架构，各学科功能独立管理，便于扩展和维护。

## 🏗️ 系统架构

### 核心架构
```
education_manager.py          # 🎓 主入口程序
├── src/core/
│   ├── subject_base.py       # 📋 学科基类定义
│   └── subject_manager.py    # 🗂️  学科管理器
├── src/subjects/
│   ├── english_subject.py    # 🇺🇸 英语学科实现
│   ├── chinese_subject.py    # 🇨🇳 中文学科实现
│   └── math_subject.py       # 🔢 数学学科实现
└── [现有功能模块保持不变]
```

### 模块职责

#### 1. **SubjectBase** (学科基类)
- 定义所有学科的通用接口
- 提供脚本执行、菜单显示等基础功能
- 支持三种功能类型：script、menu、builtin

#### 2. **SubjectManager** (学科管理器)  
- 动态加载所有学科模块
- 管理学科列表和可用性
- 提供统一的学科访问接口

#### 3. **具体学科实现**
- 继承SubjectBase基类
- 定义学科特有的功能列表
- 实现自定义的菜单和内置功能

## 🚀 使用方法

### 启动系统
```bash
python education_manager.py
```

### 系统流程
1. **学科选择** - 选择要学习的学科
2. **功能选择** - 选择具体的学习功能
3. **执行操作** - 系统自动调用相应模块
4. **循环操作** - 可在不同学科间自由切换

## 🔧 扩展新学科

### 1. 创建学科实现文件
在`src/subjects/`目录下创建新文件：
```python
# src/subjects/new_subject.py
from src.core.subject_base import SubjectBase, SubjectFunction

class NewSubject(SubjectBase):
    def get_name(self) -> str:
        return "new_subject"
    
    def get_display_name(self) -> str:
        return "🆕 新学科"
    
    def get_description(self) -> str:
        return "新学科描述"
    
    def initialize_functions(self) -> List[SubjectFunction]:
        return [
            SubjectFunction(
                name="create_plan",
                display_name="📋 创建学习计划",
                description="生成学习计划",
                script_path="new_subject_plan.py",
                function_type="script"
            )
        ]
```

### 2. 注册到学科管理器
在`src/core/subject_manager.py`中添加：
```python
subject_configs = [
    # ... 现有学科
    ("new_subject", "src.subjects.new_subject", "NewSubject"),
]
```

## 📊 当前学科状态

### ✅ 已实现学科
- **🇺🇸 英语学习** - 完整功能支持
  - 📋 创建学习计划
  - 🗂️  管理学习计划  
  - 📚 生成学习内容
  - 🛠️  FSRS模板生成器
  - 📊 查看学习进度
  - ⚙️  系统设置

### 🚧 开发中学科
- **🇨🇳 中文学习** - 框架已建立
- **🔢 数学学习** - 框架已建立
- **其他学科** - 待添加

## 🎯 功能类型说明

### 1. **Script类型**
- 直接执行Python脚本
- 适用于独立的功能模块
- 示例：计划创建、内容生成

### 2. **Menu类型**  
- 显示子菜单界面
- 适用于多选项功能
- 示例：内容生成器选择

### 3. **Builtin类型**
- 内置功能实现
- 适用于简单交互功能
- 示例：进度查看、系统设置

## 🔄 优势特点

### 1. **模块化设计**
- 各学科独立管理
- 便于功能扩展
- 代码结构清晰

### 2. **动态加载**
- 自动发现学科模块
- 支持热插拔扩展
- 错误隔离机制

### 3. **统一接口**
- 一致的用户体验
- 标准化的功能定义
- 简化的扩展流程

### 4. **向后兼容**
- 现有脚本无需修改
- 保持原有功能完整
- 平滑的升级路径

## 📝 开发指南

### 添加新功能到现有学科
1. 在对应学科类的`initialize_functions()`中添加功能定义
2. 如需自定义逻辑，重写`_show_menu()`或`_run_builtin()`方法
3. 创建对应的脚本文件（如果是script类型）

### 最佳实践
- 功能描述要清晰明确
- 错误处理要完善
- 用户交互要友好
- 代码要有良好的注释

## 🎉 总结

模块化重构成功实现了：
- ✅ **代码组织优化** - 从单一大文件拆分为多个专业模块
- ✅ **扩展性提升** - 新增学科只需添加一个文件
- ✅ **维护性增强** - 各学科功能独立，互不影响
- ✅ **用户体验一致** - 统一的界面和交互流程

系统现在具备了良好的可扩展性，可以轻松添加新的学科和功能！🚀

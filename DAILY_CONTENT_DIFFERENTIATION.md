# 每日学习内容差异化机制

## 概述

本文档说明词法和句法生成器如何确保每天生成不同的学习内容，避免重复学习相同的知识点。

## 核心机制

### 1. 学习进度跟踪

每个生成器都维护一个学习进度系统：

```python
self.learning_progress = {
    'stage_name': {
        'learned_items': set(),  # 已学过的项目ID集合
        'current_day': 0,        # 当前学习天数
        'last_date': '2025-09-28'  # 最后学习日期
    }
}
```

### 2. 项目唯一标识

每个学习项目都有唯一的ID：

- **词法项目**: `{category}_{pos_name}`
- **句法项目**: `{category}_{structure_name}`

### 3. 内容选择流程

```python
def _select_items(self, all_items, daily_count, stage, target_date):
    # 1. 获取学习进度
    progress = self.learning_progress[stage]
    
    # 2. 检查是否是新日期
    if progress['last_date'] != target_date:
        progress['current_day'] += 1
        progress['last_date'] = target_date
    
    # 3. 过滤已学过的项目
    available_items = [item for item in all_items 
                      if item['item_id'] not in progress['learned_items']]
    
    # 4. 如果可用项目不足，重新开始一轮学习
    if len(available_items) < daily_count:
        progress['learned_items'].clear()
        available_items = all_items
    
    # 5. 随机选择新项目
    selected = random.sample(available_items, daily_count)
    
    # 6. 更新学习进度
    for item in selected:
        progress['learned_items'].add(item['item_id'])
    
    return selected
```

## 具体实现

### 词法生成器 (`generate_morphology_content.py`)

- **进度文件**: `learning_data/english/morphology_progress.json`
- **项目ID格式**: `{category}_{pos_name}`
- **示例**: `"parts_of_speech_名词"`

### 句法生成器 (`generate_syntax_content.py`)

- **进度文件**: `learning_data/english/syntax_progress.json`
- **项目ID格式**: `{category}_{structure_name}`
- **示例**: `"basic_structures_基本语序"`

## 进度管理功能

### 1. 自动保存进度

每次生成内容后自动保存到JSON文件：

```python
def _save_progress(self):
    # 转换set为list（JSON不支持set）
    data = {}
    for key, progress in self.learning_progress.items():
        data[key] = {
            'learned_items': list(progress['learned_items']),
            'current_day': progress['current_day'],
            'last_date': progress['last_date']
        }
    
    with open(self.progress_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

### 2. 进度重置功能

```python
def reset_progress(self, stage: str = None):
    """重置学习进度"""
    if stage:
        if stage in self.learning_progress:
            del self.learning_progress[stage]
    else:
        self.learning_progress.clear()
    
    self._save_progress()
```

### 3. 进度查询功能

```python
def get_progress_info(self, stage: str) -> Dict:
    """获取学习进度信息"""
    if stage in self.learning_progress:
        progress = self.learning_progress[stage]
        return {
            'learned_count': len(progress['learned_items']),
            'current_day': progress['current_day'],
            'last_date': progress['last_date']
        }
    return {'learned_count': 0, 'current_day': 0, 'last_date': None}
```

## 练习句子生成器

### AI生成机制

练习句子生成器通过AI根据每日学习的单词、词法、句法生成练习句子：

1. **收集学习内容**: 获取当天的单词、词法、句法学习内容
2. **生成AI提示词**: 使用 `EnglishLearningPromptGenerator` 生成结构化提示词
3. **调用AI模型**: 通过 `UnifiedAIClient` 调用AI生成练习句子
4. **解析响应**: 解析AI返回的JSON格式练习句子
5. **备用机制**: 如果AI调用失败，使用简单模板生成句子

### 提示词管理

所有AI提示词在 `src/english/english_prompt_generator.py` 中统一管理：

```python
def generate_practice_sentences_prompt(self, daily_words, daily_morphology, daily_syntax, stage):
    """生成练习句子的AI提示词"""
    # 收集单词、词法、句法信息
    # 生成结构化提示词
    # 要求AI返回JSON格式的练习句子
```

## 测试验证

### 词法生成器测试

```bash
# 生成3天的词法内容，验证每天不同
python -c "
from generate_morphology_content import MorphologyContentGenerator
generator = MorphologyContentGenerator()
# 生成3天内容，每天2个词法项目
for i in range(3):
    daily_content = generator.generate_daily_morphology(learning_plan, f'2025-09-{28+i}')
    print(f'第{i+1}天: {[item[\"name\"] for item in daily_content[\"morphology_items\"]]}')
"
```

### 句法生成器测试

```bash
# 生成3天的句法内容，验证每天不同
python -c "
from generate_syntax_content import SyntaxContentGenerator
generator = SyntaxContentGenerator()
# 生成3天内容，每天2个句法项目
for i in range(3):
    daily_content = generator.generate_daily_syntax(learning_plan, f'2025-09-{28+i}')
    print(f'第{i+1}天: {[item[\"name\"] for item in daily_content[\"syntax_items\"]]}')
"
```

## 优势特点

1. **避免重复**: 确保每天学习不同的内容
2. **进度跟踪**: 持久化保存学习进度
3. **智能循环**: 完成一轮学习后自动重新开始
4. **灵活管理**: 支持重置进度和查询状态
5. **AI集成**: 练习句子通过AI智能生成
6. **统一管理**: 提示词在统一位置管理

## 文件结构

```
learning_data/english/
├── morphology_progress.json    # 词法学习进度
├── syntax_progress.json        # 句法学习进度
└── learning_progress.json      # 单词学习进度

src/english/
└── english_prompt_generator.py  # AI提示词管理

generate_morphology_content.py   # 词法生成器
generate_syntax_content.py       # 句法生成器
generate_practice_sentences.py   # 练习句子生成器
```

这种机制确保了学习内容的多样性和连续性，为学习者提供了系统化的学习体验。


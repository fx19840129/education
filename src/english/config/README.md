# English Learning Configuration Files

## 📁 目录结构

```text
config/
├── grammar_configs/          # 句法配置文件
│   ├── 小学句法.json
│   ├── 初中句法.json
│   └── 高中句法.json
├── morphology_configs/       # 词法配置文件
│   ├── 小学词法.json
│   ├── 初中词法.json
│   └── 高中词法.json
└── word_configs/            # 词库配置文件
    ├── 小学英语单词.json
    ├── 初中英语单词.json
    ├── 高中英语单词.json
    └── classified_by_pos/   # 按词性分类的词库
        ├── 小学_*.json
        ├── 初中_*.json
        └── 高中_*.json
```

## 📋 配置文件说明

### 1. 句法配置文件 (Grammar Configs)

**位置**: `grammar_configs/`  
**用途**: 定义各学习阶段的英语句法结构和句型模式

#### 📄 JSON 结构

```json
{
  "小学英语句法": {
    "title": "该阶段句法学习的总标题",
    "description": "对该阶段句法学习的整体描述",
    "sentence_structures": [
      {
        "structure_name": "结构的名称（如 SVO, SVOC）",
        "description": "结构的基本解释",
        "components": ["组成结构的成分（如 Subject, Verb）"],
        "details": "对结构更深入的解释（小学阶段）",
        "advanced_usage": "对结构更深入的解释（初中阶段）",
        "forms": "对结构更深入的解释（高中阶段）",
        "examples": [
          {
            "sentence": "例句",
            "analysis": "简单分析"
          }
        ]
      }
    ],
    "common_sentence_patterns": [
      {
        "pattern_name": "句型名称",
        "type": "句型分类（陈述句、疑问句、祈使句、复合句等）",
        "description": "句型用途",
        "components": "构成句型的核心元素",
        "examples": [
          {
            "sentence": "例句",
            "answer_type": "答案类型或分析"
          }
        ]
      }
    ],
    "key_concepts": [
      {
        "concept_name": "概念名称",
        "description": "对该概念的解释",
        "level": "学习深度（基础、深化、引入、掌握、熟练）"
      }
    ]
  }
}
```

#### 🎯 句法学习阶段特点

- **小学阶段**: 使用 `details` 字段，注重基础结构
- **初中阶段**: 使用 `advanced_usage` 字段，扩展应用
- **高中阶段**: 使用 `forms` 或 `types` 字段，深入分析

### 2. 词法配置文件 (Morphology Configs)

**位置**: `morphology_configs/`  
**用途**: 定义各学习阶段的英语词法和构词规则

#### 📄 词法 JSON 结构

```json
{
  "小学英语词法": {
    "title": "该阶段词法学习的总标题",
    "description": "对该阶段词法学习的整体描述",
    "parts_of_speech": [
      {
        "pos_name": "词类名称（如 Noun, Verb）",
        "pos_description": "该词类在小学阶段的整体功能描述",
        "learning_focus": [
          "该词类在小学阶段的学习重点"
        ],
        "form_changes": [
          {
            "change_type": "变化的类型（如 Plural, Tense）",
            "description": "变化规则或常见例子",
            "rules_examples": [
              "具体的变化规则"
            ]
          }
        ],
        "examples": ["常见示例词汇"]
      }
    ],
    "word_formation": [
      {
        "formation_type": "构词法的类型（如 Derivation, Compounding）",
        "description": "该类型构词法的基本介绍",
        "focus_elements": "学习的重点（如常见前缀、后缀）",
        "examples": ["构词法的常见例子"]
      }
    ],
    "key_concepts": [
      {
        "concept_name": "概念名称",
        "description": "对该概念的解释",
        "level": "学习深度（基础、深化、引入、掌握、熟练）"
      }
    ]
  }
}
```

#### 🎯 词法学习阶段特点

- **小学阶段**: 基础词性识别，简单变化规则
- **初中阶段**: 扩展词性用法，复杂变化形式
- **高中阶段**: 深入构词法，语境化理解

### 3. 词库配置文件 (Word Configs)

**位置**: `word_configs/`  
**用途**: 存储各学习阶段的英语单词数据

#### 📄 主词库 JSON 结构

```json
{
  "metadata": {
    "title": "词库标题",
    "description": "词库描述",
    "word_count": 849,
    "unique_word_count": 849,
    "multi_pos_words": 133,
    "pos_distribution": {
      "noun": 341,
      "verb": 88,
      "adjective": 70
    }
  },
  "words": [
    {
      "word": "单词",
      "pos": "词性",
      "chinese": "中文释义",
      "pos_list": ["词性列表"]
    }
  ]
}
```

#### 📄 分类词库 JSON 结构

```json
{
  "metadata": {
    "title": "词性 词库",
    "description": "从文档中提取的词性单词",
    "part_of_speech": "noun",
    "chinese_name": "名词",
    "word_count": 411,
    "creation_date": "2025-09-27 14:25:21",
    "source": "process_elementary_words.py"
  },
  "words": [
    {
      "word": "balloon",
      "pos": "noun",
      "chinese": "气球",
      "pos_list": ["noun"]
    }
  ]
}
```

#### 🎯 词库分类

**按学习阶段**:

- `小学英语单词.json` - 小学阶段单词
- `初中英语单词.json` - 初中阶段单词  
- `高中英语单词.json` - 高中阶段单词

**按词性分类** (`classified_by_pos/`):

- `*_noun_words.json` - 名词
- `*_verb_words.json` - 动词
- `*_adjective_words.json` - 形容词
- `*_adverb_words.json` - 副词
- `*_preposition_words.json` - 介词
- `*_pronoun_words.json` - 代词
- `*_conjunction_words.json` - 连词
- `*_article_words.json` - 冠词
- `*_modal_words.json` - 情态动词
- `*_auxiliary_words.json` - 助动词
- `*_determiner_words.json` - 限定词
- `*_numeral_words.json` - 数词
- `*_interjection_words.json` - 感叹词
- `*_phrase_words.json` - 短语

## 🔧 使用方式

### 加载句法配置

```python
from src.english.plan_modules.grammar_config_loader import GrammarConfigLoader

loader = GrammarConfigLoader('src/english/config/grammar_configs')
config = loader.load_grammar_config('小学句法', 'elementary')
```

### 加载词法配置

```python
import json

with open('src/english/config/morphology_configs/小学词法.json', 'r', encoding='utf-8') as f:
    morphology_config = json.load(f)
```

### 加载词库

```python
import json

# 加载主词库
with open('src/english/config/word_configs/小学英语单词.json', 'r', encoding='utf-8') as f:
    word_data = json.load(f)

# 加载分类词库
with open('src/english/config/word_configs/classified_by_pos/小学_noun_words.json', 'r', encoding='utf-8') as f:
    noun_words = json.load(f)
```

## 📊 数据统计

### 词库规模

| 学习阶段 | 总单词数 | 唯一单词数 | 多词性单词数 |
|---------|---------|-----------|------------|
| 小学    | 849     | 849       | 133        |
| 初中    | 1,906   | 1,906     | 361        |
| 高中    | 2,255   | 2,255     | 774        |
| **总计** | **5,010** | **5,010** | **1,268** |

### 主要词性统计

| 词性 | 小学 | 初中 | 高中 | 总计 |
|------|------|------|------|------|
| 名词 | 341 | 917 | 857 | 2,115 |
| 动词 | 88 | 212 | 180 | 480 |
| 形容词 | 70 | 208 | 258 | 536 |
| 副词 | 23 | 66 | 102 | 191 |
| 介词 | 13 | 20 | 11 | 44 |
| 代词 | 14 | 44 | 33 | 91 |
| 连词 | 3 | 12 | 5 | 20 |
| 冠词 | 2 | 3 | 1 | 6 |
| 情态动词 | 5 | 5 | 2 | 12 |
| 助动词 | 0 | 0 | 2 | 2 |
| 限定词 | 7 | 2 | 1 | 10 |
| 数词 | 29 | 40 | 14 | 83 |
| 感叹词 | 8 | 7 | 6 | 21 |
| 短语 | 111 | 6 | 1 | 118 |

### 各阶段详细统计

#### 小学阶段 (849个单词)
- **多词性单词**: 133个 (15.7%)
- **主要复合词性**:
  - `verb/noun`: 29个
  - `noun/verb`: 18个
  - `adjective/adverb`: 12个
  - `verb/auxiliary`: 7个

#### 初中阶段 (1,906个单词)
- **多词性单词**: 361个 (18.9%)
- **主要复合词性**:
  - `noun/verb`: 129个
  - `verb/noun`: 57个
  - `adjective/noun`: 26个
  - `noun/adjective`: 20个

#### 高中阶段 (2,255个单词)
- **多词性单词**: 774个 (34.3%)
- **主要复合词性**:
  - `noun/verb`: 308个
  - `verb/noun`: 130个
  - `adjective/noun`: 79个
  - `noun/adjective`: 43个

### 学习阶段特点分析

| 特点 | 小学 | 初中 | 高中 |
|------|------|------|------|
| 单词总数 | 849 | 1,906 | 2,255 |
| 多词性比例 | 15.7% | 18.9% | 34.3% |
| 名词占比 | 40.2% | 48.1% | 38.0% |
| 动词占比 | 10.4% | 11.1% | 8.0% |
| 形容词占比 | 8.2% | 10.9% | 11.4% |

## 🎯 配置特点

### 1. 分层设计

- **句法层**: 句子结构和句型模式
- **词法层**: 词性规则和构词法
- **词汇层**: 具体单词和短语

### 2. 阶段递进

- **小学**: 基础认知，简单规则
- **初中**: 扩展应用，复杂形式
- **高中**: 深入理解，灵活运用

### 3. 结构化存储

- **统一格式**: 所有配置文件遵循相同的JSON结构
- **元数据**: 包含创建时间、来源、统计信息
- **分类管理**: 按学习阶段和词性双重分类

### 4. 可扩展性

- **模块化**: 各配置文件独立，便于维护
- **标准化**: 统一的字段命名和数据结构
- **兼容性**: 支持不同学习阶段的特点差异

## 🔄 维护说明

### 添加新词库

1. 在 `word_configs/` 目录下创建新的JSON文件
2. 按照标准结构填写元数据和单词数据
3. 如需按词性分类，在 `classified_by_pos/` 下创建对应文件

### 更新句法/词法配置

1. 修改对应阶段的JSON文件
2. 保持字段结构的一致性
3. 注意不同学习阶段的字段差异（details/advanced_usage/forms）

### 数据验证

- 确保JSON格式正确
- 验证必填字段完整性
- 检查数据统计信息准确性

---

*最后更新: 2025-01-27*  
*维护者: English Learning System*

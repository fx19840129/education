#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的语法文档生成器
支持单一语法点生成和批量生成
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from grammar_config_loader import GrammarConfigLoader
from exercise_generator import ImprovedExerciseGenerator


class ImprovedGrammarDocumentGenerator:
    """改进的语法文档生成器"""
    
    def __init__(self, config_dir: str = "grammar_configs"):
        """
        初始化文档生成器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_loader = GrammarConfigLoader(config_dir)
        self.exercise_generator = ImprovedExerciseGenerator()
        self.output_dir = Path("improved_grammar_details")
        
    def generate_single_grammar_document(self, grammar_name: str, 
                                        level: str = "elementary",
                                        num_exercises: int = 30,
                                        difficulty_level: str = "medium") -> bool:
        """
        生成单个语法点的文档
        
        Args:
            grammar_name: 语法点名称
            level: 年级级别
            num_exercises: 练习题数量
            difficulty_level: 难度级别
            
        Returns:
            是否生成成功
        """
        # 加载语法配置
        config = self.config_loader.load_grammar_config(grammar_name, level)
        if not config:
            print(f"未找到语法配置：{grammar_name}")
            return False
        
        # 验证配置
        if not self.config_loader.validate_config(config):
            print(f"语法配置无效：{grammar_name}")
            return False
        
        # 生成练习题
        exercises = self.exercise_generator.generate_exercises(
            config, num_exercises, difficulty_level
        )
        
        # 创建输出目录
        category_dir = self.output_dir / f"{config['category']}"
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成主文档
        main_doc = self._generate_main_document(config, exercises)
        main_file = category_dir / f"{grammar_name}_语法详解_{datetime.datetime.now().strftime('%Y%m%d')}.md"
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_doc)
        
        # 生成答案文档
        answer_doc = self._generate_answer_document(config, exercises)
        answer_file = category_dir / f"{grammar_name}_练习题答案_{datetime.datetime.now().strftime('%Y%m%d')}.md"
        
        with open(answer_file, 'w', encoding='utf-8') as f:
            f.write(answer_doc)
        
        print(f"✓ {grammar_name} 语法文档已生成")
        print(f"  📄 主文档: {main_file}")
        print(f"  📋 答案文档: {answer_file}")
        
        return True
    
    def generate_all_grammar_documents(self, level: str = "elementary",
                                      num_exercises: int = 30,
                                      difficulty_level: str = "medium") -> bool:
        """
        生成所有语法点的文档
        
        Args:
            level: 年级级别
            num_exercises: 练习题数量
            difficulty_level: 难度级别
            
        Returns:
            是否生成成功
        """
        # 获取所有语法配置
        configs = self.config_loader.load_all_grammar_configs(level)
        
        if not configs:
            print(f"未找到{level}级别的语法配置")
            return False
        
        print(f"开始生成{level}级别的语法文档...")
        
        success_count = 0
        for grammar_name, config in configs.items():
            if self.generate_single_grammar_document(grammar_name, level, num_exercises, difficulty_level):
                success_count += 1
        
        print(f"\n✓ 共生成 {success_count}/{len(configs)} 个语法文档")
        return success_count > 0
    
    def generate_grammar_by_difficulty(self, level: str = "elementary",
                                      difficulty: str = "easy",
                                      num_exercises: int = 30) -> bool:
        """
        根据难度生成语法文档
        
        Args:
            level: 年级级别
            difficulty: 难度级别
            num_exercises: 练习题数量
            
        Returns:
            是否生成成功
        """
        # 获取指定难度的语法配置
        configs = self.config_loader.get_grammar_by_difficulty(level, difficulty)
        
        if not configs:
            print(f"未找到{level}级别{difficulty}难度的语法配置")
            return False
        
        print(f"开始生成{level}级别{difficulty}难度的语法文档...")
        
        success_count = 0
        for config in configs:
            grammar_name = config.get("grammar_name", "")
            if self.generate_single_grammar_document(grammar_name, level, num_exercises, difficulty):
                success_count += 1
        
        print(f"\n✓ 共生成 {success_count}/{len(configs)} 个{difficulty}难度语法文档")
        return success_count > 0
    
    def _generate_main_document(self, config: Dict[str, Any], 
                               exercises: List[Dict[str, Any]]) -> str:
        """生成主文档内容"""
        
        content = f"""# {config['grammar_name']} - 详细语法讲解

## 适用年级
{config['level']}

## 难度级别
{config['difficulty'].upper()}

## 语法分类
{config['category']}

## 语法描述
{config['description']}

## 语法讲解

### 基本规则
"""
        
        # 添加基本规则
        explanation = config.get('explanation', {})
        if 'basic_rules' in explanation:
            for i, rule in enumerate(explanation['basic_rules'], 1):
                content += f"{i}. {rule}\n"
        
        # 添加其他规则
        for key, value in explanation.items():
            if key not in ['basic_rules', 'common_errors', 'usage_tips'] and isinstance(value, str):
                content += f"\n### {key.replace('_', ' ').title()}\n{value}\n"
        
        # 添加常见错误
        if 'common_errors' in explanation:
            content += "\n### 常见错误\n"
            for i, error in enumerate(explanation['common_errors'], 1):
                content += f"{i}. {error}\n"
        
        # 添加使用技巧
        if 'usage_tips' in explanation:
            content += "\n### 使用技巧\n"
            for i, tip in enumerate(explanation['usage_tips'], 1):
                content += f"{i}. {tip}\n"
        
        # 添加例句
        content += "\n## 例句\n"
        examples = config.get('examples', {})
        for category, example_list in examples.items():
            if isinstance(example_list, list) and example_list:
                content += f"\n### {category.replace('_', ' ').title()}\n"
                for i, example in enumerate(example_list, 1):
                    content += f"{i}. {example}\n"
        
        # 添加练习题
        content += f"\n## 练习题（共{len(exercises)}道）\n\n"
        
        for i, exercise in enumerate(exercises, 1):
            content += f"### 第{i}题 [{exercise['type']}]\n"
            content += f"**题目：** {exercise['question']}\n"
            
            if exercise.get('options'):
                content += "**选项：**\n"
                for option in exercise['options']:
                    content += f"{option}\n"
            
            content += "\n"
        
        # 添加学习目标
        if 'learning_objectives' in config:
            content += "\n## 学习目标\n"
            for i, objective in enumerate(config['learning_objectives'], 1):
                content += f"{i}. {objective}\n"
        
        # 添加评估标准
        if 'assessment_criteria' in config:
            content += "\n## 评估标准\n"
            for level, criteria in config['assessment_criteria'].items():
                content += f"- **{level}**: {criteria}\n"
        
        return content
    
    def _generate_answer_document(self, config: Dict[str, Any], 
                                 exercises: List[Dict[str, Any]]) -> str:
        """生成答案文档内容"""
        
        content = f"""# {config['grammar_name']} - 练习题答案

## 适用年级
{config['level']}

## 难度级别
{config['difficulty'].upper()}

## 答案详解

"""
        
        for i, exercise in enumerate(exercises, 1):
            content += f"### 第{i}题答案\n"
            content += f"**题型：** {exercise['type']}\n"
            content += f"**题目：** {exercise['question']}\n"
            content += f"**答案：** {exercise['answer']}\n"
            content += f"**解析：** {exercise['explanation']}\n"
            content += f"**难度：** {exercise.get('difficulty', 'medium')}\n"
            content += "\n---\n"
        
        return content
    
    def generate_summary_document(self, level: str = "elementary") -> bool:
        """生成总结文档"""
        
        configs = self.config_loader.load_all_grammar_configs(level)
        
        if not configs:
            print(f"未找到{level}级别的语法配置")
            return False
        
        content = f"""# {level.title()}英语语法详解总结

## 文档说明
本套语法详解文档涵盖了{level}阶段的所有重要语法点，每个语法点都包含：
- 详细的语法讲解
- 丰富的例句展示
- 多样化的练习题
- 单独的答案文档

## 语法点分类

"""
        
        # 按分类组织语法点
        categories = {}
        for config in configs.values():
            category = config.get('category', '其他')
            if category not in categories:
                categories[category] = []
            categories[category].append(config)
        
        for category, grammar_list in categories.items():
            content += f"### {category}（{len(grammar_list)}个）\n"
            for i, grammar in enumerate(grammar_list, 1):
                content += f"{i}. **{grammar['grammar_name']}** - {grammar['level']}\n"
                content += f"   - 难度：{grammar.get('difficulty', 'medium')}\n"
                content += f"   - 描述：{grammar.get('description', '')}\n"
                content += "\n"
        
        # 添加学习建议
        content += """## 学习建议
1. **系统学习**：按照语法点的难易程度循序渐进学习
2. **理论结合实践**：先理解语法规则，再通过练习巩固
3. **自我检测**：先做练习题，再对照答案文档检查
4. **反复练习**：对于掌握不好的语法点，多次练习巩固
5. **实际应用**：在写作和口语中主动运用所学语法

## 文件结构
```
improved_grammar_details/
├── 基础语法/
│   ├── be动词用法_语法详解_YYYYMMDD.md
│   ├── be动词用法_练习题答案_YYYYMMDD.md
│   └── ...
├── 进阶语法/
│   ├── 现在完成时_语法详解_YYYYMMDD.md
│   ├── 现在完成时_练习题答案_YYYYMMDD.md
│   └── ...
└── 语法学习总结.md
```

## 学习效果
通过本套语法详解文档的学习，学生将能够：
- 系统掌握{level}阶段的所有重要语法点
- 理解语法规则的实际应用场景
- 通过大量练习提高语法应用能力
- 培养自我检测和纠错能力
- 为英语写作和口语打下坚实基础

## 更新说明
本套文档基于最新的英语教学大纲编写，内容全面、讲解详细、练习丰富，适合{level}学生以及英语学习者使用。
"""
        
        summary_file = self.output_dir / f"{level}_语法学习总结.md"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ {level}语法学习总结文档已生成：{summary_file}")
        return True


if __name__ == "__main__":
    # 测试文档生成器
    generator = ImprovedGrammarDocumentGenerator()
    
    # 测试生成单个语法文档
    print("=== 测试生成单个语法文档 ===")
    generator.generate_single_grammar_document("be动词用法", "elementary", 10, "easy")
    
    # 测试生成所有语法文档
    print("\n=== 测试生成所有语法文档 ===")
    generator.generate_all_grammar_documents("elementary", 5, "medium")
    
    # 测试生成总结文档
    print("\n=== 测试生成总结文档 ===")
    generator.generate_summary_document("elementary")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语文档生成器
基于通用框架的英语学科特定实现
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# 使用相对导入
import sys

from src.shared.learning_framework.generation.base_document_generator import (
    BaseDocumentGenerator, DocumentConfig, DocumentSection, DocumentTable,
    DocumentFormat, DocumentStyle
)


class EnglishDocumentGenerator(BaseDocumentGenerator):
    """英语文档生成器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("english", config)
        
        # 英语特定的样式设置
        self.english_styles = {
            DocumentStyle.SIMPLE: {
                "font_family": "Arial",
                "font_size": 12,
                "line_spacing": 1.2,
                "margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                "colors": {"primary": "#000000", "secondary": "#666666", "accent": "#0066CC"}
            },
            DocumentStyle.PROFESSIONAL: {
                "font_family": "Times New Roman",
                "font_size": 12,
                "line_spacing": 1.5,
                "margins": {"top": 1.0, "bottom": 1.0, "left": 1.25, "right": 1.0},
                "colors": {"primary": "#000000", "secondary": "#333333", "accent": "#1E3A8A"}
            },
            DocumentStyle.COLORFUL: {
                "font_family": "Calibri",
                "font_size": 11,
                "line_spacing": 1.3,
                "margins": {"top": 0.8, "bottom": 0.8, "left": 0.8, "right": 0.8},
                "colors": {"primary": "#2D3748", "secondary": "#4A5568", "accent": "#E53E3E"}
            },
            DocumentStyle.MINIMAL: {
                "font_family": "Helvetica",
                "font_size": 11,
                "line_spacing": 1.4,
                "margins": {"top": 1.5, "bottom": 1.5, "left": 1.5, "right": 1.5},
                "colors": {"primary": "#000000", "secondary": "#666666", "accent": "#000000"}
            }
        }
        
        # 英语学习计划模板
        self.learning_plan_templates = {
            "daily_plan": {
                "sections": [
                    "学习目标", "单词学习", "语法学习", "练习句子", "综合练习", "复习总结"
                ],
                "structure": "sequential"
            },
            "weekly_plan": {
                "sections": [
                    "周学习目标", "每日安排", "重点语法", "词汇积累", "练习计划", "测试安排"
                ],
                "structure": "hierarchical"
            },
            "monthly_plan": {
                "sections": [
                    "月学习目标", "学习进度", "重点内容", "难点突破", "能力提升", "考试准备"
                ],
                "structure": "comprehensive"
            }
        }
    
    def _init_templates(self):
        """初始化学科特定的模板"""
        self.templates = {
            "learning_plan": {
                "title_template": "英语学习计划 - {level}",
                "sections": [
                    "学习目标", "学习内容", "学习安排", "练习计划", "评估标准"
                ],
                "content_structure": "hierarchical"
            },
            "exercise_sheet": {
                "title_template": "英语练习题 - {topic}",
                "sections": [
                    "题目说明", "练习题", "答案", "解析"
                ],
                "content_structure": "sequential"
            },
            "vocabulary_list": {
                "title_template": "英语词汇表 - {level}",
                "sections": [
                    "词汇分类", "词汇列表", "例句", "练习"
                ],
                "content_structure": "categorical"
            },
            "grammar_guide": {
                "title_template": "英语语法指南 - {topic}",
                "sections": [
                    "语法规则", "用法说明", "例句分析", "练习题目"
                ],
                "content_structure": "explanatory"
            }
        }
    
    def _init_styles(self):
        """初始化学科特定的样式"""
        self.styles = self.english_styles
    
    def generate_learning_plan_document(self, plan_data: Dict[str, Any], 
                                      output_path: Optional[str] = None) -> str:
        """生成英语学习计划文档"""
        
        # 创建文档配置
        config = DocumentConfig(
            title=f"英语学习计划 - {plan_data.get('level', '初级')}",
            author="英语学习系统",
            subject="英语学习",
            output_format=DocumentFormat.DOCX,
            style=DocumentStyle.PROFESSIONAL
        )
        
        # 创建文档章节
        sections = self._create_learning_plan_sections(plan_data)
        
        # 生成文档
        return self.generate_document(sections, config, output_path)
    
    def generate_exercise_sheet(self, exercise_data: Dict[str, Any], 
                               output_path: Optional[str] = None) -> str:
        """生成英语练习题文档"""
        
        # 创建文档配置
        config = DocumentConfig(
            title=f"英语练习题 - {exercise_data.get('topic', '综合练习')}",
            author="英语学习系统",
            subject="英语练习",
            output_format=DocumentFormat.DOCX,
            style=DocumentStyle.SIMPLE
        )
        
        # 创建文档章节
        sections = self._create_exercise_sheet_sections(exercise_data)
        
        # 生成文档
        return self.generate_document(sections, config, output_path)
    
    def generate_vocabulary_list(self, vocabulary_data: Dict[str, Any], 
                                output_path: Optional[str] = None) -> str:
        """生成英语词汇表文档"""
        
        # 创建文档配置
        config = DocumentConfig(
            title=f"英语词汇表 - {vocabulary_data.get('level', '初级')}",
            author="英语学习系统",
            subject="英语词汇",
            output_format=DocumentFormat.DOCX,
            style=DocumentStyle.COLORFUL
        )
        
        # 创建文档章节
        sections = self._create_vocabulary_list_sections(vocabulary_data)
        
        # 生成文档
        return self.generate_document(sections, config, output_path)
    
    def generate_grammar_guide(self, grammar_data: Dict[str, Any], 
                              output_path: Optional[str] = None) -> str:
        """生成英语语法指南文档"""
        
        # 创建文档配置
        config = DocumentConfig(
            title=f"英语语法指南 - {grammar_data.get('topic', '基础语法')}",
            author="英语学习系统",
            subject="英语语法",
            output_format=DocumentFormat.DOCX,
            style=DocumentStyle.PROFESSIONAL
        )
        
        # 创建文档章节
        sections = self._create_grammar_guide_sections(grammar_data)
        
        # 生成文档
        return self.generate_document(sections, config, output_path)
    
    def _create_learning_plan_sections(self, plan_data: Dict[str, Any]) -> List[DocumentSection]:
        """创建学习计划章节"""
        sections = []
        
        # 学习目标
        sections.append(DocumentSection(
            title="学习目标",
            content=self._format_learning_objectives(plan_data.get('objectives', [])),
            level=1
        ))
        
        # 学习内容
        sections.append(DocumentSection(
            title="学习内容",
            content=self._format_learning_content(plan_data.get('content', {})),
            level=1
        ))
        
        # 学习安排
        sections.append(DocumentSection(
            title="学习安排",
            content=self._format_learning_schedule(plan_data.get('schedule', {})),
            level=1
        ))
        
        # 练习计划
        sections.append(DocumentSection(
            title="练习计划",
            content=self._format_practice_plan(plan_data.get('practice', {})),
            level=1
        ))
        
        # 评估标准
        sections.append(DocumentSection(
            title="评估标准",
            content=self._format_assessment_criteria(plan_data.get('assessment', {})),
            level=1
        ))
        
        return sections
    
    def _create_exercise_sheet_sections(self, exercise_data: Dict[str, Any]) -> List[DocumentSection]:
        """创建练习题文档章节"""
        sections = []
        
        # 题目说明
        sections.append(DocumentSection(
            title="题目说明",
            content=self._format_exercise_instructions(exercise_data.get('instructions', '')),
            level=1
        ))
        
        # 练习题
        sections.append(DocumentSection(
            title="练习题",
            content=self._format_exercises(exercise_data.get('exercises', [])),
            level=1
        ))
        
        # 答案
        sections.append(DocumentSection(
            title="答案",
            content=self._format_answers(exercise_data.get('answers', [])),
            level=1
        ))
        
        # 解析
        sections.append(DocumentSection(
            title="解析",
            content=self._format_explanations(exercise_data.get('explanations', [])),
            level=1
        ))
        
        return sections
    
    def _create_vocabulary_list_sections(self, vocabulary_data: Dict[str, Any]) -> List[DocumentSection]:
        """创建词汇表章节"""
        sections = []
        
        # 词汇分类
        sections.append(DocumentSection(
            title="词汇分类",
            content=self._format_vocabulary_categories(vocabulary_data.get('categories', {})),
            level=1
        ))
        
        # 词汇列表
        sections.append(DocumentSection(
            title="词汇列表",
            content=self._format_vocabulary_list(vocabulary_data.get('words', [])),
            level=1
        ))
        
        # 例句
        sections.append(DocumentSection(
            title="例句",
            content=self._format_example_sentences(vocabulary_data.get('examples', [])),
            level=1
        ))
        
        # 练习
        sections.append(DocumentSection(
            title="练习",
            content=self._format_vocabulary_exercises(vocabulary_data.get('exercises', [])),
            level=1
        ))
        
        return sections
    
    def _create_grammar_guide_sections(self, grammar_data: Dict[str, Any]) -> List[DocumentSection]:
        """创建语法指南章节"""
        sections = []
        
        # 语法规则
        sections.append(DocumentSection(
            title="语法规则",
            content=self._format_grammar_rules(grammar_data.get('rules', [])),
            level=1
        ))
        
        # 用法说明
        sections.append(DocumentSection(
            title="用法说明",
            content=self._format_usage_explanations(grammar_data.get('usage', [])),
            level=1
        ))
        
        # 例句分析
        sections.append(DocumentSection(
            title="例句分析",
            content=self._format_example_analysis(grammar_data.get('examples', [])),
            level=1
        ))
        
        # 练习题目
        sections.append(DocumentSection(
            title="练习题目",
            content=self._format_grammar_exercises(grammar_data.get('exercises', [])),
            level=1
        ))
        
        return sections
    
    def _format_learning_objectives(self, objectives: List[str]) -> str:
        """格式化学习目标"""
        if not objectives:
            return "暂无学习目标"
        
        formatted = "本阶段学习目标：\n\n"
        for i, objective in enumerate(objectives, 1):
            formatted += f"{i}. {objective}\n"
        
        return formatted
    
    def _format_learning_content(self, content: Dict[str, Any]) -> str:
        """格式化学习内容"""
        if not content:
            return "暂无学习内容"
        
        formatted = "学习内容安排：\n\n"
        
        if 'vocabulary' in content:
            formatted += f"词汇学习：{content['vocabulary']}\n"
        
        if 'grammar' in content:
            formatted += f"语法学习：{content['grammar']}\n"
        
        if 'reading' in content:
            formatted += f"阅读练习：{content['reading']}\n"
        
        if 'writing' in content:
            formatted += f"写作练习：{content['writing']}\n"
        
        return formatted
    
    def _format_learning_schedule(self, schedule: Dict[str, Any]) -> str:
        """格式化学习安排"""
        if not schedule:
            return "暂无学习安排"
        
        formatted = "学习时间安排：\n\n"
        
        for day, activities in schedule.items():
            formatted += f"{day}：\n"
            if isinstance(activities, list):
                for activity in activities:
                    formatted += f"  - {activity}\n"
            else:
                formatted += f"  - {activities}\n"
            formatted += "\n"
        
        return formatted
    
    def _format_practice_plan(self, practice: Dict[str, Any]) -> str:
        """格式化练习计划"""
        if not practice:
            return "暂无练习计划"
        
        formatted = "练习计划：\n\n"
        
        if 'daily_practice' in practice:
            formatted += f"每日练习：{practice['daily_practice']}\n"
        
        if 'weekly_test' in practice:
            formatted += f"周测试：{practice['weekly_test']}\n"
        
        if 'monthly_review' in practice:
            formatted += f"月复习：{practice['monthly_review']}\n"
        
        return formatted
    
    def _format_assessment_criteria(self, assessment: Dict[str, Any]) -> str:
        """格式化评估标准"""
        if not assessment:
            return "暂无评估标准"
        
        formatted = "评估标准：\n\n"
        
        if 'vocabulary_test' in assessment:
            formatted += f"词汇测试：{assessment['vocabulary_test']}\n"
        
        if 'grammar_test' in assessment:
            formatted += f"语法测试：{assessment['grammar_test']}\n"
        
        if 'comprehensive_test' in assessment:
            formatted += f"综合测试：{assessment['comprehensive_test']}\n"
        
        return formatted
    
    def _format_exercise_instructions(self, instructions: str) -> str:
        """格式化题目说明"""
        if not instructions:
            return "请仔细阅读题目，选择正确答案。"
        
        return f"题目说明：\n\n{instructions}"
    
    def _format_exercises(self, exercises: List[Dict[str, Any]]) -> str:
        """格式化练习题"""
        if not exercises:
            return "暂无练习题"
        
        formatted = "练习题：\n\n"
        
        for i, exercise in enumerate(exercises, 1):
            formatted += f"{i}. {exercise.get('question', '')}\n"
            
            if 'options' in exercise and exercise['options']:
                for j, option in enumerate(exercise['options'], 1):
                    formatted += f"   {chr(64+j)}. {option}\n"
            
            formatted += "\n"
        
        return formatted
    
    def _format_answers(self, answers: List[str]) -> str:
        """格式化答案"""
        if not answers:
            return "暂无答案"
        
        formatted = "答案：\n\n"
        
        for i, answer in enumerate(answers, 1):
            formatted += f"{i}. {answer}\n"
        
        return formatted
    
    def _format_explanations(self, explanations: List[str]) -> str:
        """格式化解析"""
        if not explanations:
            return "暂无解析"
        
        formatted = "解析：\n\n"
        
        for i, explanation in enumerate(explanations, 1):
            formatted += f"{i}. {explanation}\n"
        
        return formatted
    
    def _format_vocabulary_categories(self, categories: Dict[str, List[str]]) -> str:
        """格式化词汇分类"""
        if not categories:
            return "暂无词汇分类"
        
        formatted = "词汇分类：\n\n"
        
        for category, words in categories.items():
            formatted += f"{category}：\n"
            for word in words:
                formatted += f"  - {word}\n"
            formatted += "\n"
        
        return formatted
    
    def _format_vocabulary_list(self, words: List[Dict[str, str]]) -> str:
        """格式化词汇列表"""
        if not words:
            return "暂无词汇列表"
        
        formatted = "词汇列表：\n\n"
        
        for word_info in words:
            word = word_info.get('word', '')
            meaning = word_info.get('meaning', '')
            part_of_speech = word_info.get('part_of_speech', '')
            
            formatted += f"{word} ({part_of_speech}) - {meaning}\n"
        
        return formatted
    
    def _format_example_sentences(self, examples: List[Dict[str, str]]) -> str:
        """格式化例句"""
        if not examples:
            return "暂无例句"
        
        formatted = "例句：\n\n"
        
        for example in examples:
            word = example.get('word', '')
            sentence = example.get('sentence', '')
            translation = example.get('translation', '')
            
            formatted += f"• {word}: {sentence}\n"
            if translation:
                formatted += f"  翻译：{translation}\n"
            formatted += "\n"
        
        return formatted
    
    def _format_vocabulary_exercises(self, exercises: List[Dict[str, Any]]) -> str:
        """格式化词汇练习"""
        if not exercises:
            return "暂无词汇练习"
        
        formatted = "词汇练习：\n\n"
        
        for i, exercise in enumerate(exercises, 1):
            formatted += f"{i}. {exercise.get('question', '')}\n"
            formatted += f"   答案：{exercise.get('answer', '')}\n\n"
        
        return formatted
    
    def _format_grammar_rules(self, rules: List[Dict[str, str]]) -> str:
        """格式化语法规则"""
        if not rules:
            return "暂无语法规则"
        
        formatted = "语法规则：\n\n"
        
        for rule in rules:
            title = rule.get('title', '')
            description = rule.get('description', '')
            
            formatted += f"• {title}\n"
            formatted += f"  {description}\n\n"
        
        return formatted
    
    def _format_usage_explanations(self, usage: List[Dict[str, str]]) -> str:
        """格式化用法说明"""
        if not usage:
            return "暂无用法说明"
        
        formatted = "用法说明：\n\n"
        
        for item in usage:
            context = item.get('context', '')
            explanation = item.get('explanation', '')
            
            formatted += f"• {context}\n"
            formatted += f"  {explanation}\n\n"
        
        return formatted
    
    def _format_example_analysis(self, examples: List[Dict[str, str]]) -> str:
        """格式化例句分析"""
        if not examples:
            return "暂无例句分析"
        
        formatted = "例句分析：\n\n"
        
        for example in examples:
            sentence = example.get('sentence', '')
            analysis = example.get('analysis', '')
            
            formatted += f"例句：{sentence}\n"
            formatted += f"分析：{analysis}\n\n"
        
        return formatted
    
    def _format_grammar_exercises(self, exercises: List[Dict[str, Any]]) -> str:
        """格式化语法练习"""
        if not exercises:
            return "暂无语法练习"
        
        formatted = "语法练习：\n\n"
        
        for i, exercise in enumerate(exercises, 1):
            formatted += f"{i}. {exercise.get('question', '')}\n"
            formatted += f"   答案：{exercise.get('answer', '')}\n"
            if 'explanation' in exercise:
                formatted += f"   解析：{exercise['explanation']}\n"
            formatted += "\n"
        
        return formatted

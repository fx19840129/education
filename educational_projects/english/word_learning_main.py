#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语单词学习主程序
支持小学和初中英语单词学习
"""

import argparse
import sys
import os
from typing import List, Dict, Any

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'word_learning_modules'))

from word_database import WordDatabase
from exercise_generator import WordExerciseGenerator
from learning_plan_generator import WordLearningPlanGenerator
from word_document_generator import WordDocumentGenerator


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="英语单词学习系统")
    parser.add_argument("--level", "-l", choices=["elementary", "middle_school"], 
                       required=True, help="年级级别")
    parser.add_argument("--difficulty", "-d", choices=["easy", "medium", "hard"], 
                       help="难度级别")
    parser.add_argument("--category", "-c", help="单词分类")
    parser.add_argument("--count", "-n", type=int, default=30, help="单词数量")
    parser.add_argument("--format", "-f", choices=["markdown", "word"], 
                       default="word", help="输出格式")
    parser.add_argument("--action", "-a", choices=["exercises", "plan", "list", "search"], 
                       default="exercises", help="操作类型")
    parser.add_argument("--duration", type=int, default=30, help="学习计划天数")
    parser.add_argument("--daily-words", type=int, default=10, help="每日学习单词数")
    parser.add_argument("--keyword", "-k", help="搜索关键词")
    
    args = parser.parse_args()
    
    # 初始化组件
    word_db = WordDatabase("word_configs")
    exercise_generator = WordExerciseGenerator(word_db)
    plan_generator = WordLearningPlanGenerator(word_db)
    doc_generator = WordDocumentGenerator()
    
    print("=== 英语单词学习系统 ===")
    
    try:
        if args.action == "list":
            list_words(word_db, args.level)
        elif args.action == "search":
            search_words(word_db, args.level, args.keyword)
        elif args.action == "exercises":
            generate_exercises(word_db, exercise_generator, doc_generator, args)
        elif args.action == "plan":
            generate_learning_plan(word_db, plan_generator, doc_generator, args)
        else:
            print("无效的操作类型")
            return 1
    
    except Exception as e:
        print(f"错误：{e}")
        return 1
    
    return 0


def list_words(word_db: WordDatabase, level: str):
    """列出单词"""
    words = word_db.get_words_by_level(level)
    
    print(f"\n{level} 单词列表：")
    print(f"总单词数：{len(words)}")
    
    # 按分类显示
    categories = word_db.get_categories(level)
    for category in categories:
        category_words = word_db.get_words_by_category(level, category)
        print(f"\n{category} ({len(category_words)}个单词)：")
        for word, info in list(category_words.items())[:10]:  # 只显示前10个
            print(f"  {word} - {info.chinese_meaning}")
        if len(category_words) > 10:
            print(f"  ... 还有{len(category_words) - 10}个单词")


def search_words(word_db: WordDatabase, level: str, keyword: str):
    """搜索单词"""
    if not keyword:
        print("请提供搜索关键词")
        return
    
    results = word_db.search_words(level, keyword)
    
    print(f"\n搜索结果（关键词：{keyword}）：")
    print(f"找到 {len(results)} 个单词")
    
    for word_info in results:
        print(f"\n{word_info.word}")
        print(f"  发音：{word_info.pronunciation}")
        print(f"  词性：{word_info.part_of_speech}")
        print(f"  中文：{word_info.chinese_meaning}")
        print(f"  英文：{word_info.english_meaning}")
        print(f"  例句：{word_info.example_sentence}")


def generate_exercises(word_db: WordDatabase, exercise_generator: WordExerciseGenerator, 
                      doc_generator: WordDocumentGenerator, args):
    """生成练习题"""
    print(f"\n开始生成{args.level}单词练习题...")
    
    # 获取单词
    if args.category:
        words = list(word_db.get_words_by_category(args.level, args.category).values())
    elif args.difficulty:
        words = list(word_db.get_words_by_difficulty(args.level, args.difficulty).values())
    else:
        words = list(word_db.get_words_by_level(args.level).values())
    
    if not words:
        print("未找到符合条件的单词")
        return
    
    # 随机选择单词
    import random
    selected_words = random.sample(words, min(args.count, len(words)))
    
    # 生成练习题
    exercises = exercise_generator.generate_exercises(selected_words, args.count, args.difficulty)
    
    if args.format == "word":
        # 生成Word文档
        main_doc = doc_generator.generate_word_exercises_document(
            selected_words, exercises, args.level, args.difficulty
        )
        answer_doc = doc_generator.generate_word_answers_document(exercises, args.level)
        
        print(f"✅ 练习题文档生成完成！")
        print(f"📄 主文档: {main_doc}")
        print(f"📋 答案文档: {answer_doc}")
    else:
        # 生成Markdown文档
        generate_markdown_exercises(selected_words, exercises, args.level, args.difficulty)


def generate_learning_plan(word_db: WordDatabase, plan_generator: WordLearningPlanGenerator,
                          doc_generator: WordDocumentGenerator, args):
    """生成学习计划"""
    print(f"\n开始生成{args.level}单词学习计划...")
    
    # 生成学习计划
    if args.category:
        plan = plan_generator.generate_category_plan(args.level, args.category, args.duration)
    elif args.difficulty:
        plan = plan_generator.generate_difficulty_plan(args.level, args.difficulty, args.duration)
    else:
        plan = plan_generator.generate_comprehensive_plan(args.level, args.duration)
    
    if not plan:
        print("无法生成学习计划")
        return
    
    if args.format == "word":
        # 生成Word文档
        doc_path = doc_generator.generate_learning_plan_document(plan)
        print(f"✅ 学习计划文档生成完成！")
        print(f"📄 文档路径: {doc_path}")
    else:
        # 生成Markdown文档
        generate_markdown_plan(plan)


def generate_markdown_exercises(words, exercises, level, difficulty):
    """生成Markdown练习题文档"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{level}_word_exercises_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {'小学' if level == 'elementary' else '初中'}英语单词练习\n\n")
        
        if difficulty:
            difficulty_name = {"easy": "基础", "medium": "进阶", "hard": "高级"}.get(difficulty, difficulty)
            f.write(f"**难度级别：** {difficulty_name}\n\n")
        
        f.write(f"**单词数量：** {len(words)}\n\n")
        f.write(f"**生成时间：** {datetime.now().strftime('%Y年%m月%d日')}\n\n")
        
        # 单词列表
        f.write("## 单词列表\n\n")
        f.write("| 单词 | 发音 | 词性 | 中文意思 | 例句 |\n")
        f.write("|------|------|------|----------|------|\n")
        
        for word in words:
            f.write(f"| {word.word} | {word.pronunciation} | {word.part_of_speech} | {word.chinese_meaning} | {word.example_sentence} |\n")
        
        f.write("\n## 练习题\n\n")
        
        # 练习题
        for i, exercise in enumerate(exercises, 1):
            f.write(f"### 第{i}题\n\n")
            f.write(f"**题目：** {exercise.question}\n\n")
            
            if exercise.options:
                f.write("**选项：**\n")
                for j, option in enumerate(exercise.options):
                    f.write(f"{chr(65+j)}. {option}\n")
                f.write("\n")
            
            f.write("**答案：** ___________\n\n")
            f.write("---\n\n")
    
    print(f"✅ Markdown练习题文档生成完成！")
    print(f"📄 文档路径: {filename}")


def generate_markdown_plan(plan):
    """生成Markdown学习计划文档"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{plan.level}_learning_plan_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {plan.title}\n\n")
        f.write(f"{plan.description}\n\n")
        
        # 计划统计
        f.write("## 计划统计\n\n")
        f.write(f"- **学习时长：** {plan.duration}天\n")
        f.write(f"- **每日单词数：** {plan.daily_words}个\n")
        f.write(f"- **总单词数：** {plan.total_words}个\n")
        f.write(f"- **难度级别：** {plan.difficulty}\n")
        f.write(f"- **学习分类：** {', '.join(plan.categories) if plan.categories else '综合'}\n\n")
        
        # 学习目标
        f.write("## 学习目标\n\n")
        for objective in plan.learning_objectives:
            f.write(f"- {objective}\n")
        f.write("\n")
        
        # 学习计划表
        f.write("## 学习计划表\n\n")
        for day_plan in plan.study_schedule:
            f.write(f"### 第{day_plan['day']}天\n\n")
            f.write(f"**学习方法：** {day_plan['learning_method']}\n\n")
            
            if day_plan['focus_skills']:
                f.write(f"**重点技能：** {', '.join(day_plan['focus_skills'])}\n\n")
            
            if day_plan['practice_activities']:
                f.write("**练习活动：**\n")
                for activity in day_plan['practice_activities']:
                    f.write(f"- {activity}\n")
                f.write("\n")
            
            f.write("**今日单词：**\n")
            for word_info in day_plan['words']:
                f.write(f"- {word_info['word']} - {word_info['meaning']} ({word_info['pronunciation']})\n")
            
            if day_plan['review_words']:
                f.write(f"\n**复习单词：** {', '.join(day_plan['review_words'])}\n")
            
            f.write("\n---\n\n")
        
        # 评估标准
        f.write("## 评估标准\n\n")
        for level, criteria in plan.assessment_criteria.items():
            f.write(f"**{level}：** {criteria}\n\n")
    
    print(f"✅ Markdown学习计划文档生成完成！")
    print(f"📄 文档路径: {filename}")


if __name__ == "__main__":
    from datetime import datetime
    sys.exit(main())

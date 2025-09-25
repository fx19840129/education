#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速学习计划管理器
禁用AI句子生成，使用模板生成，大幅提升生成速度
"""

import sys
import os
import argparse
from datetime import datetime

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'plan_modules'))

from plan_manager import PlanManager
from custom_plan_generator import CustomPlanGenerator
from daily_content_generator import DailyContentGenerator
from plan_document_generator import PlanDocumentGenerator

class FastPlanManager(PlanManager):
    """快速学习计划管理器"""
    
    def __init__(self):
        # 调用父类初始化
        super().__init__()
        
        # 重新初始化生成器（禁用AI句子生成）
        self.daily_generator = DailyContentGenerator(use_ai_sentences=False)  # 禁用AI
        
        print("⚡ 快速学习计划管理器初始化完成（模板模式）")
    
    def generate_multi_day_content(self, plan_id: str, start_day: int, days: int, output_format: str = "console"):
        """生成多天学习内容（快速版本）"""
        if plan_id not in self.saved_plans:
            print(f"❌ 未找到计划ID: {plan_id}")
            return
        
        plan_info = self.saved_plans[plan_id]
        
        if start_day < 1 or start_day + days - 1 > plan_info['total_days']:
            print(f"❌ 天数超出范围，计划总天数为 {plan_info['total_days']} 天")
            return
        
        print(f"📅 生成第{start_day}-{start_day + days - 1}天学习内容")
        print(f"📝 计划: {plan_info['name']}")
        print(f"🎯 阶段: {plan_info['stage_info']['name']}")
        
        if output_format == "console":
            for day in range(start_day, start_day + days):
                print(f"\n{'='*60}")
                print(f"📅 第{day}天学习内容")
                print(f"{'='*60}")
                
                daily_content = self.daily_generator.generate_daily_content(day=day)
                self._display_daily_content(daily_content, day)
        elif output_format == "word":
            # 生成多天Word文档
            for day in range(start_day, start_day + days):
                doc_file = self.doc_generator.generate_enhanced_daily_plan(day=day)
                print(f"📄 第{day}天Word文档: {doc_file}")
        elif output_format == "txt":
            # 生成多天文本文件
            self._generate_multi_day_txt(plan_id, start_day, days)
        else:
            print("❌ 不支持的输出格式")
    
    def _generate_multi_day_txt(self, plan_id: str, start_day: int, days: int):
        """生成多天文本文件（超快速）"""
        plan_info = self.saved_plans[plan_id]
        
        # 创建输出目录
        output_dir = "fast_plans"
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fast_plan_{plan_id}_{start_day}-{start_day + days - 1}days_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        print(f"📝 生成文本文件: {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"学习计划: {plan_info['name']}\n")
            f.write(f"学习阶段: {plan_info['stage_info']['name']}\n")
            f.write(f"计划天数: {days} 天 (第{start_day}-{start_day + days - 1}天)\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for day in range(start_day, start_day + days):
                f.write(f"第{day}天学习内容\n")
                f.write("-" * 40 + "\n")
                
                # 生成日常内容
                daily_content = self.daily_generator.generate_daily_content(day=day)
                
                # 写入单词
                if 'word_content' in daily_content:
                    word_content = daily_content['word_content']
                    f.write(f"\n📖 今日单词 ({len(word_content['words'])} 个):\n")
                    for i, word in enumerate(word_content['words'], 1):
                        f.write(f"   {i:2d}. {word.word} - {word.chinese_meaning} ({word.part_of_speech})\n")
                
                # 写入语法
                if 'grammar_content' in daily_content:
                    grammar_content = daily_content['grammar_content']
                    f.write(f"\n📝 今日语法: {grammar_content['topic']}\n")
                    f.write(f"   级别: {grammar_content['level']}\n")
                
                # 写入句子
                if 'integrated_sentences' in daily_content:
                    f.write(f"\n💬 综合句子 ({len(daily_content['integrated_sentences'])} 个):\n")
                    for i, sentence in enumerate(daily_content['integrated_sentences'], 1):
                        f.write(f"   {i}. {sentence.get('sentence', 'N/A')}\n")
                        if 'chinese_translation' in sentence:
                            f.write(f"      翻译: {sentence['chinese_translation']}\n")
                
                # 写入练习题
                if 'exercises' in daily_content:
                    f.write(f"\n✏️ 今日练习 ({len(daily_content['exercises'])} 题):\n")
                    for i, exercise in enumerate(daily_content['exercises'][:5], 1):  # 只显示前5题
                        if hasattr(exercise, 'type') and hasattr(exercise, 'question'):
                            f.write(f"   {i}. {exercise.type}: {exercise.question}\n")
                        elif isinstance(exercise, dict):
                            f.write(f"   {i}. {exercise.get('type', 'N/A')}: {exercise.get('question', 'N/A')}\n")
                    if len(daily_content['exercises']) > 5:
                        f.write(f"   ... 还有 {len(daily_content['exercises']) - 5} 道练习题\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
        
        print(f"✅ 文本文件生成完成: {filepath}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="快速学习计划管理器")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建计划
    create_parser = subparsers.add_parser('create', help='创建学习计划')
    create_parser.add_argument('--name', required=True, help='计划名称')
    create_parser.add_argument('--days', type=int, required=True, help='计划天数')
    create_parser.add_argument('--minutes', type=int, required=True, help='每日学习时间（分钟）')
    create_parser.add_argument('--stage', default='beginner', help='学习阶段')
    create_parser.add_argument('--words', type=int, help='每日单词数量')
    create_parser.add_argument('--grammar', type=int, help='每日语法点数量')
    create_parser.add_argument('--exercises', type=int, help='每日练习题数量')
    
    # 列出计划
    subparsers.add_parser('list', help='列出所有计划')
    
    # 显示计划详情
    show_parser = subparsers.add_parser('show', help='显示计划详情')
    show_parser.add_argument('--id', required=True, help='计划ID')
    
    # 生成单天内容
    daily_parser = subparsers.add_parser('daily', help='生成单天学习内容')
    daily_parser.add_argument('--id', required=True, help='计划ID')
    daily_parser.add_argument('--day', type=int, required=True, help='天数')
    daily_parser.add_argument('--format', choices=['console', 'word'], default='console', help='输出格式')
    
    # 生成多天内容
    multi_parser = subparsers.add_parser('multi', help='生成多天学习内容')
    multi_parser.add_argument('--id', required=True, help='计划ID')
    multi_parser.add_argument('--start-day', type=int, required=True, help='开始天数')
    multi_parser.add_argument('--days', type=int, required=True, help='生成天数')
    multi_parser.add_argument('--format', choices=['console', 'word', 'txt'], default='console', help='输出格式')
    
    # 删除计划
    delete_parser = subparsers.add_parser('delete', help='删除计划')
    delete_parser.add_argument('--id', required=True, help='计划ID')
    
    # 导出计划
    export_parser = subparsers.add_parser('export', help='导出计划')
    export_parser.add_argument('--id', required=True, help='计划ID')
    export_parser.add_argument('--format', choices=['json', 'txt'], default='json', help='导出格式')
    export_parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建管理器实例
    manager = FastPlanManager()
    
    # 执行命令
    if args.command == 'create':
        manager.create_plan(
            name=args.name,
            days=args.days,
            minutes=args.minutes,
            stage=args.stage,
            daily_words=args.words,
            daily_grammar=args.grammar,
            daily_exercises=args.exercises
        )
    elif args.command == 'list':
        manager.list_plans()
    elif args.command == 'show':
        manager.show_plan_details(args.id)
    elif args.command == 'daily':
        manager.generate_daily_content(args.id, args.day, args.format)
    elif args.command == 'multi':
        manager.generate_multi_day_content(args.id, args.start_day, args.days, args.format)
    elif args.command == 'delete':
        manager.delete_plan(args.id)
    elif args.command == 'export':
        manager.export_plan(args.id, args.format, args.output)

if __name__ == "__main__":
    main()

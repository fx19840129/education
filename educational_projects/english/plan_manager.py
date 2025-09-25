#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习计划管理器
支持保存、列出、选择计划并输出具体学习内容
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'plan_modules'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'word_learning_modules'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'grammar_modules'))

try:
    from daily_content_generator import DailyContentGenerator
    from plan_document_generator import PlanDocumentGenerator
    from custom_plan_generator import CustomPlanGenerator
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    print("请确保在正确的目录下运行此脚本")
    sys.exit(1)

class PlanManager:
    """学习计划管理器"""
    
    def __init__(self, plans_dir="saved_plans"):
        """初始化计划管理器"""
        self.plans_dir = plans_dir
        self.plans_file = os.path.join(plans_dir, "plans_index.json")
        
        # 确保目录存在
        os.makedirs(plans_dir, exist_ok=True)
        
        # 初始化生成器
        self.custom_generator = CustomPlanGenerator()
        self.daily_generator = DailyContentGenerator()
        self.doc_generator = PlanDocumentGenerator()
        
        # 加载已保存的计划
        self.saved_plans = self._load_saved_plans()
        
        print("📚 学习计划管理器初始化完成")
    
    def _load_saved_plans(self) -> Dict:
        """加载已保存的计划索引"""
        if os.path.exists(self.plans_file):
            try:
                with open(self.plans_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载计划索引失败: {e}")
                return {}
        return {}
    
    def _save_plans_index(self):
        """保存计划索引"""
        try:
            with open(self.plans_file, 'w', encoding='utf-8') as f:
                json.dump(self.saved_plans, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存计划索引失败: {e}")
    
    def create_plan(self, plan_name: str, total_days: int, daily_minutes: int, 
                   stage: str = "intermediate", custom_words: Optional[int] = None,
                   custom_grammar: Optional[int] = None, custom_exercises: Optional[int] = None,
                   start_date: Optional[str] = None) -> str:
        """创建并保存学习计划"""
        print(f"📝 创建学习计划: {plan_name}")
        
        # 生成计划
        result = self.custom_generator.generate_custom_plan(
            total_days=total_days,
            daily_minutes=daily_minutes,
            start_date=start_date,
            custom_words=custom_words,
            custom_grammar=custom_grammar,
            custom_exercises=custom_exercises,
            stage=stage,
            output_dir=self.plans_dir
        )
        
        plan_data = result["plan_data"]
        files = result["files"]
        
        # 生成计划ID
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存计划信息到索引
        self.saved_plans[plan_id] = {
            "id": plan_id,
            "name": plan_name,
            "created_time": datetime.now().isoformat(),
            "total_days": total_days,
            "daily_minutes": daily_minutes,
            "stage": stage,
            "start_date": plan_data["metadata"]["start_date"],
            "end_date": plan_data["metadata"]["end_date"],
            "files": {
                "json_file": files["json_file"],
                "word_file": files["word_file"],
                "txt_file": files["txt_file"]
            },
            "statistics": plan_data["statistics"],
            "stage_info": plan_data["stage_info"]
        }
        
        # 保存计划详细数据
        plan_detail_file = os.path.join(self.plans_dir, f"{plan_id}_detail.json")
        with open(plan_detail_file, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2)
        
        self.saved_plans[plan_id]["detail_file"] = plan_detail_file
        
        # 保存索引
        self._save_plans_index()
        
        print(f"✅ 计划创建成功！")
        print(f"   计划ID: {plan_id}")
        print(f"   计划名称: {plan_name}")
        print(f"   计划时长: {total_days} 天")
        print(f"   学习阶段: {plan_data['stage_info']['name']}")
        print(f"   总词汇量: {plan_data['statistics']['total_words']} 个")
        print(f"   总语法点: {plan_data['statistics']['total_grammar_points']} 个")
        
        return plan_id
    
    def list_plans(self):
        """列出所有已保存的计划"""
        if not self.saved_plans:
            print("📋 暂无已保存的学习计划")
            return
        
        print("📋 已保存的学习计划:")
        print("-" * 80)
        
        for plan_id, plan_info in self.saved_plans.items():
            print(f"🆔 计划ID: {plan_id}")
            print(f"📝 计划名称: {plan_info['name']}")
            print(f"📅 创建时间: {plan_info['created_time'][:19]}")
            print(f"⏱️ 计划时长: {plan_info['total_days']} 天")
            print(f"🕐 每日学习: {plan_info['daily_minutes']} 分钟")
            print(f"🎯 学习阶段: {plan_info['stage_info']['name']}")
            print(f"📚 总词汇量: {plan_info['statistics']['total_words']} 个")
            print(f"📝 总语法点: {plan_info['statistics']['total_grammar_points']} 个")
            print(f"📅 开始日期: {plan_info['start_date']}")
            print(f"📅 结束日期: {plan_info['end_date']}")
            print("-" * 80)
    
    def show_plan_detail(self, plan_id: str):
        """显示计划详细信息"""
        if plan_id not in self.saved_plans:
            print(f"❌ 未找到计划ID: {plan_id}")
            return
        
        plan_info = self.saved_plans[plan_id]
        
        print(f"📋 计划详细信息: {plan_info['name']}")
        print("=" * 60)
        
        print(f"🆔 计划ID: {plan_id}")
        print(f"📝 计划名称: {plan_info['name']}")
        print(f"📅 创建时间: {plan_info['created_time'][:19]}")
        print(f"⏱️ 计划时长: {plan_info['total_days']} 天")
        print(f"🕐 每日学习: {plan_info['daily_minutes']} 分钟")
        print(f"🎯 学习阶段: {plan_info['stage_info']['name']}")
        print(f"📅 开始日期: {plan_info['start_date']}")
        print(f"📅 结束日期: {plan_info['end_date']}")
        
        print(f"\n📚 学习内容统计:")
        stats = plan_info['statistics']
        print(f"   总词汇量: {stats['total_words']} 个")
        print(f"   总语法点: {stats['total_grammar_points']} 个")
        print(f"   总练习题: {stats['total_exercises']} 题")
        print(f"   总学习时间: {stats['total_study_time_hours']} 小时")
        print(f"   日均单词: {stats['average_words_per_day']} 个")
        print(f"   日均语法: {stats['average_grammar_per_day']} 个")
        print(f"   日均练习: {stats['average_exercises_per_day']} 题")
        
        print(f"\n🎯 学习目标:")
        for goal in plan_info['stage_info']['learning_goals']:
            print(f"   • {goal}")
        
        print(f"\n📁 相关文件:")
        files = plan_info['files']
        print(f"   📄 Word文档: {files['word_file']}")
        print(f"   📊 JSON数据: {files['json_file']}")
        print(f"   📋 文本总结: {files['txt_file']}")
    
    def generate_daily_content(self, plan_id: str, day: int, output_format: str = "console"):
        """生成指定天的学习内容"""
        if plan_id not in self.saved_plans:
            print(f"❌ 未找到计划ID: {plan_id}")
            return
        
        plan_info = self.saved_plans[plan_id]
        
        if day < 1 or day > plan_info['total_days']:
            print(f"❌ 天数超出范围，计划总天数为 {plan_info['total_days']} 天")
            return
        
        print(f"📅 生成第{day}天学习内容")
        print(f"📝 计划: {plan_info['name']}")
        print(f"🎯 阶段: {plan_info['stage_info']['name']}")
        
        # 生成日常内容
        daily_content = self.daily_generator.generate_daily_content(day=day)
        
        if output_format == "console":
            self._display_daily_content(daily_content, day)
        elif output_format == "word":
            # 生成Word文档
            doc_file = self.doc_generator.generate_enhanced_daily_plan(day=day)
            print(f"📄 已生成Word文档: {doc_file}")
        else:
            print("❌ 不支持的输出格式")
    
    def generate_multi_day_content(self, plan_id: str, start_day: int, days: int, output_format: str = "console"):
        """生成多天学习内容"""
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
        else:
            print("❌ 不支持的输出格式")
    
    def _display_daily_content(self, daily_content: Dict, day: int):
        """显示日常学习内容"""
        print(f"\n📚 第{day}天学习内容:")
        print("-" * 40)
        
        # 显示阶段信息
        if 'phase' in daily_content:
            phase = daily_content['phase']
            print(f"🎯 学习阶段: {phase['name']}")
            print(f"📚 词汇级别: {phase['word_level']}")
            print(f"📝 语法级别: {phase['grammar_level']}")
            print(f"📊 每日单词: {phase['daily_words']} 个")
        
        # 显示单词内容
        if 'word_content' in daily_content:
            word_content = daily_content['word_content']
            print(f"\n📖 今日单词 ({len(word_content['words'])} 个):")
            for i, word in enumerate(word_content['words'][:10], 1):  # 只显示前10个
                print(f"   {i:2d}. {word.word} - {word.chinese_meaning} ({word.part_of_speech})")
            if len(word_content['words']) > 10:
                print(f"   ... 还有 {len(word_content['words']) - 10} 个单词")
        
        # 显示语法内容
        if 'grammar_content' in daily_content:
            grammar_content = daily_content['grammar_content']
            print(f"\n📝 今日语法: {grammar_content['topic']}")
            print(f"   级别: {grammar_content['level']}")
        
        # 显示综合句子
        if 'integrated_sentences' in daily_content:
            print(f"\n💬 综合句子 ({len(daily_content['integrated_sentences'])} 个):")
            for i, sentence in enumerate(daily_content['integrated_sentences'][:5], 1):  # 只显示前5个
                print(f"   {i}. {sentence.get('sentence', 'N/A')}")
                if 'translation' in sentence:
                    print(f"      翻译: {sentence['translation']}")
            if len(daily_content['integrated_sentences']) > 5:
                print(f"   ... 还有 {len(daily_content['integrated_sentences']) - 5} 个句子")
        
        # 显示练习题
        if 'exercises' in daily_content:
            print(f"\n✏️ 今日练习 ({len(daily_content['exercises'])} 题):")
            for i, exercise in enumerate(daily_content['exercises'][:3], 1):  # 只显示前3题
                if hasattr(exercise, 'type') and hasattr(exercise, 'question'):
                    print(f"   {i}. {exercise.type}: {exercise.question}")
                elif isinstance(exercise, dict):
                    print(f"   {i}. {exercise.get('type', 'N/A')}: {exercise.get('question', 'N/A')}")
                else:
                    print(f"   {i}. 练习题: {str(exercise)[:50]}...")
            if len(daily_content['exercises']) > 3:
                print(f"   ... 还有 {len(daily_content['exercises']) - 3} 道练习题")
    
    def delete_plan(self, plan_id: str):
        """删除指定计划"""
        if plan_id not in self.saved_plans:
            print(f"❌ 未找到计划ID: {plan_id}")
            return
        
        plan_info = self.saved_plans[plan_id]
        
        # 删除相关文件
        files_to_delete = [
            plan_info['files']['json_file'],
            plan_info['files']['word_file'],
            plan_info['files']['txt_file'],
            plan_info.get('detail_file', '')
        ]
        
        for file_path in files_to_delete:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"⚠️ 删除文件失败 {file_path}: {e}")
        
        # 从索引中删除
        del self.saved_plans[plan_id]
        self._save_plans_index()
        
        print(f"✅ 计划已删除: {plan_info['name']}")
    
    def export_plan(self, plan_id: str, output_file: str):
        """导出计划到指定文件"""
        if plan_id not in self.saved_plans:
            print(f"❌ 未找到计划ID: {plan_id}")
            return
        
        plan_info = self.saved_plans[plan_id]
        
        # 读取详细数据
        if 'detail_file' in plan_info and os.path.exists(plan_info['detail_file']):
            with open(plan_info['detail_file'], 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
        else:
            print("❌ 计划详细数据文件不存在")
            return
        
        # 导出到指定文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 计划已导出到: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="学习计划管理器")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建计划命令
    create_parser = subparsers.add_parser('create', help='创建新计划')
    create_parser.add_argument('--name', required=True, help='计划名称')
    create_parser.add_argument('--days', '-d', type=int, required=True, help='计划时长（天数）')
    create_parser.add_argument('--minutes', '-m', type=int, required=True, help='每日学习时间（分钟）')
    create_parser.add_argument('--stage', choices=['beginner', 'intermediate', 'advanced', 'comprehensive'], 
                               default='intermediate', help='学习阶段')
    create_parser.add_argument('--words', type=int, help='自定义每日单词数')
    create_parser.add_argument('--grammar', type=int, help='自定义每日语法点数')
    create_parser.add_argument('--exercises', type=int, help='自定义每日练习题数')
    create_parser.add_argument('--start-date', '-s', help='开始日期 (YYYY-MM-DD)')
    
    # 列出计划命令
    list_parser = subparsers.add_parser('list', help='列出所有计划')
    
    # 显示计划详情命令
    show_parser = subparsers.add_parser('show', help='显示计划详情')
    show_parser.add_argument('--id', required=True, help='计划ID')
    
    # 生成日常内容命令
    daily_parser = subparsers.add_parser('daily', help='生成指定天的学习内容')
    daily_parser.add_argument('--id', required=True, help='计划ID')
    daily_parser.add_argument('--day', type=int, required=True, help='天数')
    daily_parser.add_argument('--format', choices=['console', 'word'], default='console', help='输出格式')
    
    # 生成多天内容命令
    multi_parser = subparsers.add_parser('multi', help='生成多天学习内容')
    multi_parser.add_argument('--id', required=True, help='计划ID')
    multi_parser.add_argument('--start-day', type=int, required=True, help='开始天数')
    multi_parser.add_argument('--days', type=int, required=True, help='天数')
    multi_parser.add_argument('--format', choices=['console', 'word'], default='console', help='输出格式')
    
    # 删除计划命令
    delete_parser = subparsers.add_parser('delete', help='删除计划')
    delete_parser.add_argument('--id', required=True, help='计划ID')
    
    # 导出计划命令
    export_parser = subparsers.add_parser('export', help='导出计划')
    export_parser.add_argument('--id', required=True, help='计划ID')
    export_parser.add_argument('--output', '-o', required=True, help='输出文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = PlanManager()
        
        if args.command == 'create':
            plan_id = manager.create_plan(
                plan_name=args.name,
                total_days=args.days,
                daily_minutes=args.minutes,
                stage=args.stage,
                custom_words=args.words,
                custom_grammar=args.grammar,
                custom_exercises=args.exercises,
                start_date=args.start_date
            )
            print(f"\n🎉 计划创建完成！计划ID: {plan_id}")
            
        elif args.command == 'list':
            manager.list_plans()
            
        elif args.command == 'show':
            manager.show_plan_detail(args.id)
            
        elif args.command == 'daily':
            manager.generate_daily_content(args.id, args.day, args.format)
            
        elif args.command == 'multi':
            manager.generate_multi_day_content(args.id, args.start_day, args.days, args.format)
            
        elif args.command == 'delete':
            manager.delete_plan(args.id)
            
        elif args.command == 'export':
            manager.export_plan(args.id, args.output)
    
    except Exception as e:
        print(f"❌ 操作失败: {e}")


if __name__ == "__main__":
    main()

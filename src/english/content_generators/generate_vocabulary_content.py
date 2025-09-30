#!/usr/bin/env python3
"""
每日单词学习内容生成器
根据FSRS算法生成每天应学习的单词，按天、词性输出确定的学习内容
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.services.fsrs_learning_service import FSRSLearningGenerator
from src.english.content_generators.coordinate_learning_content import LearningContentGenerator


class DailyWordsGenerator:
    """每日单词生成器"""
    
    def __init__(self):
        self.fsrs_generator = FSRSLearningGenerator()
        self.plan_reader = LearningContentGenerator()
    
    def generate_daily_words_schedule(self, plan_id: str = None, days: int = 7) -> Dict:
        """
        生成每日单词学习计划
        
        Args:
            plan_id: 学习计划ID，如果为None则使用最新计划
            days: 生成天数，默认7天
            
        Returns:
            每日单词学习计划
        """
        # 读取学习计划
        if plan_id is None:
            plans = self.plan_reader.list_plans()
            if not plans:
                print("❌ 没有找到学习计划")
                return {}
            plan_id = plans[0]['id']
        
        learning_plan = self.plan_reader.read_plan(plan_id=plan_id)
        if not learning_plan:
            print(f"❌ 无法读取学习计划: {plan_id}")
            return {}
        
        print(f"📋 使用学习计划: {plan_id}")
        print(f"📋 学习阶段: {learning_plan['metadata']['stage']}")
        print(f"📋 学习周期: {learning_plan['metadata']['days']}天")
        print()
        
        # 生成指定天数的学习内容
        start_date = datetime.now().strftime("%Y-%m-%d")
        daily_schedule = []
        
        for day in range(days):
            current_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day)).strftime("%Y-%m-%d")
            daily_content = self.fsrs_generator.generate_daily_learning_content(learning_plan, current_date)
            daily_schedule.append(daily_content)
        
        return {
            "plan_id": plan_id,
            "plan_name": learning_plan['learning_plan']['learning_plan_name'],
            "stage": learning_plan['metadata']['stage'],
            "start_date": start_date,
            "days": days,
            "daily_schedule": daily_schedule
        }
    
    def display_daily_words(self, schedule: Dict, show_details: bool = True) -> None:
        """
        显示每日单词学习内容
        
        Args:
            schedule: 学习计划
            show_details: 是否显示详细信息
        """
        if not schedule:
            print("❌ 没有学习计划数据")
            return
        
        print("📚 每日单词学习计划")
        print("=" * 80)
        print(f"计划名称: {schedule['plan_name']}")
        print(f"学习阶段: {schedule['stage']}")
        print(f"开始日期: {schedule['start_date']}")
        print(f"生成天数: {schedule['days']}天")
        print()
        
        for i, daily in enumerate(schedule['daily_schedule'], 1):
            print(f"📅 第{i}天 - {daily['date']}")
            print(f"   总单词数: {daily['total_words']}个")
            print()
            
            # 按词性显示单词
            for pos, words in daily['pos_content'].items():
                if words:
                    print(f"   📖 {pos.upper()} ({len(words)}个):")
                    
                    if show_details:
                        # 显示所有单词
                        for j, word in enumerate(words, 1):
                            print(f"      {j:2d}. {word['word']:<15} "
                                  f"(难度: {word['difficulty']:.1f}, "
                                  f"稳定性: {word['stability']:.1f})")
                    else:
                        # 只显示前5个单词
                        for j, word in enumerate(words[:5], 1):
                            print(f"      {j:2d}. {word['word']:<15} "
                                  f"(难度: {word['difficulty']:.1f})")
                        if len(words) > 5:
                            print(f"      ... 还有{len(words) - 5}个单词")
                    
                    print()
            
            print("-" * 80)
            print()
    
    def export_daily_words(self, schedule: Dict, filename: str = None) -> str:
        """
        导出每日单词学习计划到文件
        
        Args:
            schedule: 学习计划
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"daily_words_{timestamp}.json"
        
        output_dir = Path("outputs/english/daily_words")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)
        
        print(f"💾 每日单词学习计划已保存到: {filepath}")
        return str(filepath)
    
    def generate_pos_summary(self, schedule: Dict) -> Dict:
        """
        生成词性学习摘要
        
        Args:
            schedule: 学习计划
            
        Returns:
            词性学习摘要
        """
        pos_summary = {}
        
        for daily in schedule['daily_schedule']:
            for pos, words in daily['pos_content'].items():
                if pos not in pos_summary:
                    pos_summary[pos] = {
                        'total_words': 0,
                        'days_with_words': 0,
                        'avg_difficulty': 0.0,
                        'word_list': []
                    }
                
                if words:
                    pos_summary[pos]['total_words'] += len(words)
                    pos_summary[pos]['days_with_words'] += 1
                    
                    # 计算平均难度
                    total_difficulty = sum(word['difficulty'] for word in words)
                    avg_difficulty = total_difficulty / len(words)
                    pos_summary[pos]['avg_difficulty'] = avg_difficulty
                    
                    # 收集单词列表
                    pos_summary[pos]['word_list'].extend([word['word'] for word in words])
        
        # 计算总体平均难度
        for pos, data in pos_summary.items():
            if data['total_words'] > 0:
                data['avg_difficulty'] = data['avg_difficulty'] / data['days_with_words']
        
        return pos_summary
    
    def display_pos_summary(self, schedule: Dict) -> None:
        """
        显示词性学习摘要
        
        Args:
            schedule: 学习计划
        """
        pos_summary = self.generate_pos_summary(schedule)
        
        print("📊 词性学习摘要")
        print("=" * 60)
        
        for pos, data in pos_summary.items():
            if data['total_words'] > 0:
                print(f"📖 {pos.upper()}:")
                print(f"   总单词数: {data['total_words']}个")
                print(f"   学习天数: {data['days_with_words']}天")
                print(f"   平均难度: {data['avg_difficulty']:.1f}")
                print(f"   平均每天: {data['total_words'] / data['days_with_words']:.1f}个")
                print()
        
        # 显示总体统计
        total_words = sum(data['total_words'] for data in pos_summary.values())
        total_days = schedule['days']
        avg_daily = total_words / total_days if total_days > 0 else 0
        
        print("📈 总体统计:")
        print(f"   总单词数: {total_words}个")
        print(f"   学习天数: {total_days}天")
        print(f"   平均每天: {avg_daily:.1f}个单词")
        print()


def main():
    """主函数"""
    generator = DailyWordsGenerator()
    
    print("🔍 每日单词学习计划生成器")
    print("=" * 50)
    
    # 获取用户输入
    plan_id = input("请输入学习计划ID (按回车使用最新计划): ").strip()
    if not plan_id:
        plan_id = None
    
    try:
        days = int(input("请输入生成天数 (默认7天): ").strip() or "7")
    except ValueError:
        days = 7
    
    show_details = input("是否显示详细信息? (y/n, 默认y): ").strip().lower()
    show_details = show_details != 'n'
    
    print()
    
    # 生成每日单词学习计划
    schedule = generator.generate_daily_words_schedule(plan_id, days)
    
    if not schedule:
        print("❌ 生成失败")
        return
    
    # 显示学习计划
    generator.display_daily_words(schedule, show_details)
    
    # 显示词性摘要
    generator.display_pos_summary(schedule)
    
    # 询问是否导出
    export = input("是否导出到文件? (y/n, 默认n): ").strip().lower()
    if export == 'y':
        generator.export_daily_words(schedule)
    
    print("\n✅ 每日单词学习计划生成完成!")


if __name__ == "__main__":
    main()
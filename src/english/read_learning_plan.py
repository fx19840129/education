#!/usr/bin/env python3
"""
学习计划读取器
读取已生成好的学习计划文件，提供查看和分析功能
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.english.services.vocab_selector import VocabSelector

class LearningPlanReader:
    """学习计划读取器"""
    
    def __init__(self, plans_dir: str = "outputs/english"):
        self.plans_dir = Path(plans_dir)
        if not self.plans_dir.exists():
            print(f"❌ 学习计划目录不存在: {self.plans_dir}")
            self.plans_dir = None
        
        # 初始化词库选择器
        self.vocab_selector = VocabSelector()
    
    def list_plans(self) -> List[Dict]:
        """列出所有可用的学习计划"""
        if not self.plans_dir:
            return []
        
        plans = []
        for file_path in self.plans_dir.glob("english_learning_plan_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                
                # 提取基本信息
                plan_info = {
                    'file_path': str(file_path),
                    'filename': file_path.name,
                    'id': plan_data.get('id', '未知'),
                    'stage': plan_data.get('metadata', {}).get('stage', '未知阶段'),
                    'days': plan_data.get('metadata', {}).get('days', 0),
                    'minutes_per_day': plan_data.get('metadata', {}).get('minutes_per_day', 0),
                    'created_at': plan_data.get('metadata', {}).get('generated_at', '未知时间'),
                    'ai_model': plan_data.get('metadata', {}).get('ai_model', '未知模型'),
                    'file_size': file_path.stat().st_size,
                    'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime)
                }
                plans.append(plan_info)
            except Exception as e:
                print(f"⚠️ 读取文件失败 {file_path.name}: {e}")
        
        # 按修改时间排序（最新的在前）
        plans.sort(key=lambda x: x['modified_time'], reverse=True)
        return plans
    
    def read_plan(self, plan_id: str = None, filename: str = None) -> Optional[Dict]:
        """读取指定的学习计划"""
        if not self.plans_dir:
            return None
        
        if plan_id:
            # 根据ID查找文件
            for file_path in self.plans_dir.glob(f"english_learning_plan_{plan_id}.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"❌ 读取文件失败: {e}")
                    return None
        
        elif filename:
            # 根据文件名查找
            file_path = self.plans_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"❌ 读取文件失败: {e}")
                    return None
            else:
                print(f"❌ 文件不存在: {filename}")
                return None
        
        return None
    
    def display_plan_summary(self, plan: Dict) -> None:
        """显示学习计划摘要"""
        if not plan:
            print("❌ 没有可显示的学习计划")
            return
        
        metadata = plan.get('metadata', {})
        learning_plan = plan.get('learning_plan', {})
        
        print("📋 学习计划摘要")
        print("=" * 60)
        print(f"计划ID: {plan.get('id', '未知')}")
        print(f"学习阶段: {metadata.get('stage', '未知')}")
        print(f"学习周期: {metadata.get('days', 0)}天")
        print(f"每日时间: {metadata.get('minutes_per_day', 0)}分钟")
        print(f"AI模型: {metadata.get('ai_model', '未知')}")
        print(f"生成时间: {metadata.get('generated_at', '未知')}")
        print(f"响应时间: {metadata.get('ai_response_time', 0):.2f}秒")
        
        if learning_plan:
            print(f"\n学习计划名称: {learning_plan.get('learning_plan_name', '未知')}")
            print(f"学习难度: {learning_plan.get('learning_difficulty', '未知')}")
            
            # 显示资源统计
            total_resources = learning_plan.get('total_resources', {})
            print(f"\n📊 学习资源:")
            print(f"  词汇总量: {total_resources.get('total_vocab', 0)}")
            print(f"  词法总量: {total_resources.get('total_word_forms', 0)}")
            print(f"  句法总量: {total_resources.get('total_sentence_patterns', 0)}")
            
            # 显示词性学习计划
            study_plan = learning_plan.get('study_plan', {})
            if study_plan:
                print(f"\n📚 词性学习计划:")
                for pos, data in study_plan.items():
                    if isinstance(data, dict) and 'total_count' in data:
                        print(f"  {pos}: {data.get('total_count', 0)}个, "
                              f"每日{data.get('daily_learn_count', 0)}个, "
                              f"学习{data.get('total_study_cycles', 0)}次")
            
            # 显示词法和句法
            morphology = learning_plan.get('morphology', {})
            if morphology and 'total_count' in morphology:
                print(f"\n🔤 词法学习计划:")
                print(f"  词法: {morphology.get('total_count', 0)}个, "
                      f"每日{morphology.get('daily_learn_count', 0)}个, "
                      f"学习{morphology.get('total_study_cycles', 0)}次")
            
            syntax = learning_plan.get('syntax', {})
            if syntax and 'total_count' in syntax:
                print(f"\n📝 句法学习计划:")
                print(f"  句法: {syntax.get('total_count', 0)}个, "
                      f"每日{syntax.get('daily_learn_count', 0)}个, "
                      f"学习{syntax.get('total_study_cycles', 0)}次")
        
        print("=" * 60)
    
    def get_vocab_sources(self, plan: Dict) -> Dict:
        """获取学习计划的词库来源信息"""
        if not plan:
            return {}
        
        stage = plan.get('metadata', {}).get('stage', '')
        if not stage:
            return {}
        
        # 使用词库选择器获取来源信息
        vocab_files = self.vocab_selector.get_available_vocab_files(stage)
        pos_vocab_files = self.vocab_selector.get_available_pos_vocab_files(stage)
        morphology_files = self.vocab_selector.get_available_morphology_files(stage)
        syntax_files = self.vocab_selector.get_available_syntax_files(stage)
        
        # 获取详细配置
        stage_details = self.vocab_selector.get_stage_vocab_details(stage)
        
        return {
            'stage': stage,
            'stage_name': stage_details.get('stage_name', ''),
            'vocab_files': vocab_files,
            'pos_vocab_files': pos_vocab_files,
            'morphology_files': morphology_files,
            'syntax_files': syntax_files,
            'vocab_ratios': stage_details.get('vocab_ratios', {}),
            'morphology_ratios': stage_details.get('morphology_ratios', {}),
            'syntax_ratios': stage_details.get('syntax_ratios', {}),
            'vocab_details': stage_details.get('vocab_details', {}),
            'morphology_details': stage_details.get('morphology_details', {}),
            'syntax_details': stage_details.get('syntax_details', {})
        }
    
    def display_vocab_sources(self, plan: Dict) -> None:
        """显示学习计划的词库来源信息"""
        if not plan:
            print("❌ 没有可显示的学习计划")
            return
        
        sources = self.get_vocab_sources(plan)
        if not sources:
            print("❌ 无法获取词库来源信息")
            return
        
        print("📚 词库来源信息")
        print("=" * 60)
        print(f"学习阶段: {sources['stage']}")
        print(f"阶段名称: {sources['stage_name']}")
        
        # 显示文件来源
        print(f"\n📁 需要加载的文件:")
        print(f"  总词汇文件: {', '.join(sources['vocab_files'])}")
        print(f"  词法文件: {', '.join(sources['morphology_files'])}")
        print(f"  句法文件: {', '.join(sources['syntax_files'])}")
        
        # 显示按词性分词的词库文件
        print(f"\n📚 按词性分词的词库文件:")
        pos_vocab_files = sources.get('pos_vocab_files', {})
        for pos, files in pos_vocab_files.items():
            if files:  # 只显示有文件的词性
                print(f"  {pos}: {', '.join(files)}")
        
        # 显示比例配置
        print(f"\n📊 比例配置:")
        vocab_ratios = sources['vocab_ratios']
        print(f"  词汇比例: 小学{vocab_ratios.get('elementary', 0):.0%} + 初中{vocab_ratios.get('junior_high', 0):.0%} + 高中{vocab_ratios.get('high_school', 0):.0%}")
        
        morphology_ratios = sources['morphology_ratios']
        print(f"  词法比例: 小学{morphology_ratios.get('elementary', 0):.0%} + 初中{morphology_ratios.get('junior_high', 0):.0%} + 高中{morphology_ratios.get('high_school', 0):.0%}")
        
        syntax_ratios = sources['syntax_ratios']
        print(f"  句法比例: 小学{syntax_ratios.get('elementary', 0):.0%} + 初中{syntax_ratios.get('junior_high', 0):.0%} + 高中{syntax_ratios.get('high_school', 0):.0%}")
        
        # 显示详细数量
        print(f"\n📈 详细数量:")
        vocab_details = sources['vocab_details']
        print(f"  词汇: 小学{vocab_details.get('elementary', 0)}个 + 初中{vocab_details.get('junior_high', 0)}个 + 高中{vocab_details.get('high_school', 0)}个 = 总计{vocab_details.get('total', 0)}个")
        
        morphology_details = sources['morphology_details']
        print(f"  词法: 小学{morphology_details.get('elementary', 0)}个 + 初中{morphology_details.get('junior_high', 0)}个 + 高中{morphology_details.get('high_school', 0)}个 = 总计{morphology_details.get('total', 0)}个")
        
        syntax_details = sources['syntax_details']
        print(f"  句法: 小学{syntax_details.get('elementary', 0)}个 + 初中{syntax_details.get('junior_high', 0)}个 + 高中{syntax_details.get('high_school', 0)}个 = 总计{syntax_details.get('total', 0)}个")
        
        print("=" * 60)
    
    def display_plan_details(self, plan: Dict) -> None:
        """显示学习计划详细信息"""
        if not plan:
            print("❌ 没有可显示的学习计划")
            return
        
        print("📄 学习计划详细信息")
        print("=" * 80)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        print("=" * 80)
    
    def analyze_plans(self) -> None:
        """分析所有学习计划"""
        plans = self.list_plans()
        if not plans:
            print("❌ 没有找到任何学习计划")
            return
        
        print(f"📊 学习计划分析 (共{len(plans)}个计划)")
        print("=" * 80)
        
        # 按阶段统计
        stage_stats = {}
        total_days = 0
        total_minutes = 0
        
        for plan in plans:
            stage = plan['stage']
            if stage not in stage_stats:
                stage_stats[stage] = 0
            stage_stats[stage] += 1
            total_days += plan['days']
            total_minutes += plan['minutes_per_day']
        
        print("📈 按学习阶段统计:")
        for stage, count in stage_stats.items():
            print(f"  {stage}: {count}个计划")
        
        print(f"\n📊 总体统计:")
        print(f"  总计划数: {len(plans)}")
        print(f"  平均学习周期: {total_days / len(plans):.1f}天")
        print(f"  平均每日时间: {total_minutes / len(plans):.1f}分钟")
        
        # 显示最新的5个计划
        print(f"\n📋 最新计划:")
        for i, plan in enumerate(plans[:5], 1):
            print(f"  {i}. {plan['filename']} - {plan['stage']} "
                  f"({plan['days']}天, {plan['minutes_per_day']}分钟)")
        
        print("=" * 80)

def main():
    """主函数"""
    reader = LearningPlanReader()
    
    while True:
        print("\n🔍 学习计划读取器")
        print("=" * 40)
        print("1. 列出所有学习计划")
        print("2. 查看计划摘要")
        print("3. 查看计划详情")
        print("4. 查看词库来源")
        print("5. 分析所有计划")
        print("6. 退出")
        print("=" * 40)
        
        choice = input("请选择操作 (1-6): ").strip()
        
        if choice == '1':
            plans = reader.list_plans()
            if plans:
                print(f"\n📋 找到 {len(plans)} 个学习计划:")
                for i, plan in enumerate(plans, 1):
                    print(f"{i:2d}. {plan['filename']}")
                    print(f"    ID: {plan['id']}")
                    print(f"    阶段: {plan['stage']}")
                    print(f"    周期: {plan['days']}天, {plan['minutes_per_day']}分钟")
                    print(f"    创建时间: {plan['created_at']}")
                    print(f"    文件大小: {plan['file_size']} 字节")
                    print()
            else:
                print("❌ 没有找到任何学习计划")
        
        elif choice == '2':
            plan_id = input("请输入计划ID (或按回车查看最新计划): ").strip()
            if not plan_id:
                plans = reader.list_plans()
                if plans:
                    plan = reader.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = reader.read_plan(plan_id=plan_id)
            
            if plan:
                reader.display_plan_summary(plan)
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '3':
            plan_id = input("请输入计划ID (或按回车查看最新计划): ").strip()
            if not plan_id:
                plans = reader.list_plans()
                if plans:
                    plan = reader.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = reader.read_plan(plan_id=plan_id)
            
            if plan:
                reader.display_plan_details(plan)
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '4':
            plan_id = input("请输入计划ID (或按回车查看最新计划): ").strip()
            if not plan_id:
                plans = reader.list_plans()
                if plans:
                    plan = reader.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = reader.read_plan(plan_id=plan_id)
            
            if plan:
                reader.display_vocab_sources(plan)
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '5':
            reader.analyze_plans()
        
        elif choice == '6':
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()

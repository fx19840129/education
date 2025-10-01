#!/usr/bin/env python3
"""
学习内容生成器 - 主入口
根据学习计划生成各种学习内容：单词、词法、句法、练习句子、练习题等
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.services.vocabulary_selection_service import VocabSelector


class LearningContentGenerator:
    """学习内容生成器主入口"""
    
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
                    'file_size': file_path.stat().st_size
                }
                plans.append(plan_info)
                
            except Exception as e:
                print(f"⚠️ 读取计划文件失败 {file_path}: {e}")
                continue
        
        # 按创建时间排序，最新的在前
        plans.sort(key=lambda x: x['created_at'], reverse=True)
        return plans
    
    def read_plan(self, plan_id: str = None, file_path: str = None) -> Optional[Dict]:
        """读取指定的学习计划"""
        if file_path:
            plan_file = Path(file_path)
        elif plan_id:
            # 根据ID查找文件
            plans = self.list_plans()
            plan_file = None
            for plan in plans:
                if plan['id'] == plan_id:
                    plan_file = Path(plan['file_path'])
                    break
            
            if not plan_file:
                print(f"❌ 未找到ID为 {plan_id} 的学习计划")
                return None
        else:
            print("❌ 请提供计划ID或文件路径")
            return None
        
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 读取学习计划失败: {e}")
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
        print(f"计划名称: {learning_plan.get('learning_plan_name', '未知')}")
        print(f"学习阶段: {metadata.get('stage', '未知')}")
        print(f"学习周期: {learning_plan.get('learning_cycle_days', 0)}天")
        print(f"每日时间: {learning_plan.get('daily_study_time_minutes', 0)}分钟")
        print(f"学习难度: {learning_plan.get('learning_difficulty', '未知')}")
        print(f"创建时间: {metadata.get('generated_at', '未知')}")
        
        # 显示资源统计
        total_resources = learning_plan.get('total_resources', {})
        print(f"\n📊 学习资源:")
        print(f"  总词汇: {total_resources.get('total_vocab', 0)}个")
        print(f"  总词法: {total_resources.get('total_word_forms', 0)}个")
        print(f"  总句法: {total_resources.get('total_sentence_patterns', 0)}个")
        
        # 显示各词性统计
        study_plan = learning_plan.get('study_plan', {})
        print(f"\n📚 词性学习计划:")
        for pos, plan_data in study_plan.items():
            daily_count = plan_data.get('daily_learn_count', 0)
            total_count = plan_data.get('total_count', 0)
            if daily_count > 0:
                print(f"  {pos}: 每天{daily_count}个，总计{total_count}个")
        
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
    
    def run_content_generator(self, generator_type: str, plan: Dict, **kwargs) -> None:
        """运行指定的内容生成器"""
        if generator_type == "words":
            from generate_daily_words import DailyWordsGenerator
            generator = DailyWordsGenerator()
            generator.display_daily_words(generator.generate_daily_words_schedule(plan['id'], kwargs.get('days', 7)), kwargs.get('show_details', True))
        
        elif generator_type == "morphology":
            from src.english.services.word_morphology_service import MorphologyService
            service = MorphologyService()
            # 获取形态学内容并显示
            stage = plan.get('stage', '第一阶段：基础巩固 (小学中高年级)')
            morphology_points = service.get_morphology_points(stage, kwargs.get('days', 7))
            print(f"✅ 获取到 {len(morphology_points)} 个形态学知识点")
        
        elif generator_type == "syntax":
            from src.english.services.sentence_syntax_service import SyntaxService
            service = SyntaxService()
            # 获取语法内容并显示
            stage = plan.get('stage', '第一阶段：基础巩固 (小学中高年级)')
            syntax_points = service.get_syntax_points(stage, kwargs.get('days', 7))
            print(f"✅ 获取到 {len(syntax_points)} 个语法知识点")
        
        elif generator_type == "practice_sentences":
            from generate_practice_sentences import PracticeSentencesGenerator
            generator = PracticeSentencesGenerator()
            generator.generate_and_display(plan, kwargs.get('days', 7))
        
        elif generator_type == "practice_exercises":
            from generate_practice_exercises import PracticeExercisesGenerator
            generator = PracticeExercisesGenerator()
            generator.generate_and_display(plan, kwargs.get('days', 7))
        
        else:
            print(f"❌ 未知的生成器类型: {generator_type}")


def main():
    """主函数"""
    generator = LearningContentGenerator()
    
    while True:
        print("\n🎯 学习内容生成器")
        print("=" * 50)
        print("1. 列出所有学习计划")
        print("2. 查看计划摘要")
        print("3. 查看词库来源")
        print("4. 生成单词学习内容")
        print("5. 生成词法学习内容")
        print("6. 生成句法学习内容")
        print("7. 生成练习句子")
        print("8. 生成练习题")
        print("9. 退出")
        print("=" * 50)
        
        choice = input("请选择操作 (1-9): ").strip()
        
        if choice == '1':
            plans = generator.list_plans()
            if plans:
                print(f"\n📋 找到 {len(plans)} 个学习计划:")
                for i, plan_info in enumerate(plans):
                    print(f" {i+1}. {plan_info['filename']}")
                    print(f"    ID: {plan_info['id']}")
                    print(f"    阶段: {plan_info['stage']}")
                    print(f"    周期: {plan_info['days']}天, {plan_info['minutes_per_day']}分钟")
                    print(f"    创建时间: {plan_info['created_at']}")
                    print(f"    文件大小: {plan_info['file_size']} 字节")
                    print()
            else:
                print("❌ 没有找到任何学习计划")
        
        elif choice == '2':
            plan_id = input("请输入计划ID (或按回车查看最新计划): ").strip()
            if not plan_id:
                plans = generator.list_plans()
                if plans:
                    plan = generator.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = generator.read_plan(plan_id=plan_id)
            
            if plan:
                generator.display_plan_summary(plan)
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '3':
            plan_id = input("请输入计划ID (或按回车查看最新计划): ").strip()
            if not plan_id:
                plans = generator.list_plans()
                if plans:
                    plan = generator.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = generator.read_plan(plan_id=plan_id)
            
            if plan:
                generator.display_vocab_sources(plan)
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '4':
            plan_id = input("请输入计划ID (或按回车使用最新计划): ").strip()
            if not plan_id:
                plans = generator.list_plans()
                if plans:
                    plan = generator.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = generator.read_plan(plan_id=plan_id)
            
            if plan:
                try:
                    days = int(input("请输入生成天数 (默认7天): ").strip() or "7")
                    show_details = input("是否显示详细信息? (y/n, 默认y): ").strip().lower() != 'n'
                    generator.run_content_generator("words", plan, days=days, show_details=show_details)
                except ValueError:
                    print("❌ 请输入有效的天数")
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '5':
            plan_id = input("请输入计划ID (或按回车使用最新计划): ").strip()
            if not plan_id:
                plans = generator.list_plans()
                if plans:
                    plan = generator.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = generator.read_plan(plan_id=plan_id)
            
            if plan:
                try:
                    days = int(input("请输入生成天数 (默认7天): ").strip() or "7")
                    generator.run_content_generator("morphology", plan, days=days)
                except ValueError:
                    print("❌ 请输入有效的天数")
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '6':
            plan_id = input("请输入计划ID (或按回车使用最新计划): ").strip()
            if not plan_id:
                plans = generator.list_plans()
                if plans:
                    plan = generator.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = generator.read_plan(plan_id=plan_id)
            
            if plan:
                try:
                    days = int(input("请输入生成天数 (默认7天): ").strip() or "7")
                    generator.run_content_generator("syntax", plan, days=days)
                except ValueError:
                    print("❌ 请输入有效的天数")
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '7':
            plan_id = input("请输入计划ID (或按回车使用最新计划): ").strip()
            if not plan_id:
                plans = generator.list_plans()
                if plans:
                    plan = generator.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = generator.read_plan(plan_id=plan_id)
            
            if plan:
                try:
                    days = int(input("请输入生成天数 (默认7天): ").strip() or "7")
                    generator.run_content_generator("practice_sentences", plan, days=days)
                except ValueError:
                    print("❌ 请输入有效的天数")
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '8':
            plan_id = input("请输入计划ID (或按回车使用最新计划): ").strip()
            if not plan_id:
                plans = generator.list_plans()
                if plans:
                    plan = generator.read_plan(plan_id=plans[0]['id'])
                else:
                    print("❌ 没有找到任何学习计划")
                    continue
            else:
                plan = generator.read_plan(plan_id=plan_id)
            
            if plan:
                try:
                    days = int(input("请输入生成天数 (默认7天): ").strip() or "7")
                    generator.run_content_generator("practice_exercises", plan, days=days)
                except ValueError:
                    print("❌ 请输入有效的天数")
            else:
                print("❌ 未找到指定的学习计划")
        
        elif choice == '9':
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
句法学习内容生成器
根据学习计划生成句法学习内容
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.english.learning_content_generator import LearningContentGenerator


class SyntaxContentGenerator:
    """句法学习内容生成器"""
    
    def __init__(self):
        self.plan_reader = LearningContentGenerator()
        self.learning_progress = {}  # 存储学习进度
        self.progress_file = Path("learning_data/english/syntax_progress.json")
        self._load_progress()
    
    def load_syntax_data(self, stage: str) -> Dict:
        """加载句法数据"""
        # 根据阶段确定需要加载的句法文件
        sources = self.plan_reader.get_vocab_sources({'metadata': {'stage': stage}})
        syntax_files = sources.get('syntax_files', [])
        
        syntax_data = {}
        for file_path in syntax_files:
            full_path = Path("src/english/config") / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 解析句法数据结构
                        for key, value in data.items():
                            if isinstance(value, dict) and 'sentence_structures' in value:
                                syntax_data[key] = value['sentence_structures']
                except Exception as e:
                    print(f"⚠️ 加载句法文件失败 {file_path}: {e}")
        
        return syntax_data
    
    def _load_progress(self):
        """加载学习进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 转换set为list（JSON不支持set）
                    for key, progress in data.items():
                        if 'learned_items' in progress:
                            progress['learned_items'] = set(progress['learned_items'])
                    self.learning_progress = data
            except Exception as e:
                print(f"⚠️ 加载句法学习进度失败: {e}")
                self.learning_progress = {}
    
    def _save_progress(self):
        """保存学习进度"""
        try:
            # 确保目录存在
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换set为list（JSON不支持set）
            data = {}
            for key, progress in self.learning_progress.items():
                data[key] = {
                    'learned_items': list(progress['learned_items']),
                    'current_day': progress['current_day']
                }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存句法学习进度失败: {e}")
    
    def reset_progress(self, stage: str = None):
        """重置学习进度"""
        if stage:
            if stage in self.learning_progress:
                del self.learning_progress[stage]
                print(f"📚 已重置 {stage} 的句法学习进度")
        else:
            self.learning_progress.clear()
            print("📚 已重置所有句法学习进度")
        
        self._save_progress()
    
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
    
    def generate_daily_syntax(self, learning_plan: Dict, target_date: str = None) -> Dict:
        """生成指定日期的句法学习内容"""
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        stage = learning_plan.get("metadata", {}).get("stage", "")
        syntax_plan = learning_plan.get("learning_plan", {}).get("syntax", {})
        
        daily_count = syntax_plan.get("daily_learn_count", 0)
        total_count = syntax_plan.get("total_count", 0)
        total_cycles = syntax_plan.get("total_study_cycles", 0)
        
        print(f"📋 句法学习配置: 每天{daily_count}个，总计{total_count}个，学习周期{total_cycles}次")
        
        if daily_count <= 0:
            return {
                "date": target_date,
                "stage": stage,
                "total_items": 0,
                "syntax_items": [],
                "plan_info": {
                    "daily_count": daily_count,
                    "total_count": total_count,
                    "total_cycles": total_cycles
                }
            }
        
        # 加载句法数据
        syntax_data = self.load_syntax_data(stage)
        
        # 选择要学习的句法项目
        selected_items = self._select_syntax_items(syntax_data, daily_count, stage, target_date)
        
        # 为每个句法项目生成学习内容
        learning_items = []
        for item in selected_items:
            learning_item = {
                "name": item.get("name", ""),
                "type": item.get("type", ""),
                "description": item.get("description", ""),
                "structure": item.get("structure", ""),
                "examples": item.get("examples", []),
                "usage_rules": item.get("usage_rules", []),
                "difficulty": self._calculate_syntax_difficulty(item),
                "learning_phase": "new",
                "study_cycles": total_cycles,
                "elementary_ratio": syntax_plan.get("elementary_ratio", 0),
                "junior_high_ratio": syntax_plan.get("junior_high_ratio", 0),
                "high_school_ratio": syntax_plan.get("high_school_ratio", 0)
            }
            learning_items.append(learning_item)
        
        return {
            "date": target_date,
            "stage": stage,
            "total_items": len(learning_items),
            "syntax_items": learning_items,
            "plan_info": {
                "daily_count": daily_count,
                "total_count": total_count,
                "total_cycles": total_cycles
            }
        }
    
    def _select_syntax_items(self, syntax_data: Dict, daily_count: int, stage: str, target_date: str) -> List[Dict]:
        """选择要学习的句法项目，确保每天内容不同"""
        all_items = []
        
        # 收集所有句法项目
        for category, items in syntax_data.items():
            if isinstance(items, list):
                for item in items:
                    # 转换句法项目格式
                    syntax_item = {
                        'name': item.get('structure_name', ''),
                        'type': item.get('description', ''),
                        'description': item.get('description', ''),
                        'structure': ', '.join(item.get('components', [])),
                        'examples': [],
                        'usage_rules': [],
                        'category': category,
                        'item_id': f"{category}_{item.get('structure_name', '')}"  # 添加唯一ID
                    }
                    
                    # 收集例句
                    examples = item.get('examples', [])
                    for example in examples:
                        if isinstance(example, dict):
                            sentence = example.get('sentence', '')
                            analysis = example.get('analysis', '')
                            if sentence:
                                syntax_item['examples'].append(f"{sentence} ({analysis})")
                        elif isinstance(example, str):
                            syntax_item['examples'].append(example)
                    
                    # 收集使用规则
                    details = item.get('details', '')
                    if details:
                        syntax_item['usage_rules'].append(details)
                    
                    all_items.append(syntax_item)
        
        if len(all_items) <= daily_count:
            return all_items
        
        # 获取学习进度（使用阶段作为key，而不是具体日期）
        progress_key = f"{stage}"
        if progress_key not in self.learning_progress:
            self.learning_progress[progress_key] = {
                'learned_items': set(),
                'current_day': 0,
                'last_date': target_date
            }
        
        progress = self.learning_progress[progress_key]
        
        # 确保last_date字段存在
        if 'last_date' not in progress:
            progress['last_date'] = target_date
        
        # 检查是否是新的学习日期
        if progress['last_date'] != target_date:
            progress['current_day'] += 1
            progress['last_date'] = target_date
        
        # 过滤掉已经学过的项目
        available_items = [item for item in all_items if item['item_id'] not in progress['learned_items']]
        
        # 如果可用项目不足，重新开始（完成一轮学习）
        if len(available_items) < daily_count:
            print(f"📚 句法学习：已完成一轮学习，重新开始")
            progress['learned_items'].clear()
            available_items = all_items
        
        # 选择指定数量的句法项目
        import random
        selected = random.sample(available_items, min(daily_count, len(available_items)))
        
        # 更新学习进度
        for item in selected:
            progress['learned_items'].add(item['item_id'])
        
        progress['current_day'] += 1
        
        # 保存学习进度
        self._save_progress()
        
        return selected
    
    def _calculate_syntax_difficulty(self, item: Dict) -> float:
        """计算句法项目的难度"""
        # 基于项目类型和复杂度估算难度
        base_difficulty = 3.0
        
        # 根据类型调整难度
        item_type = item.get("type", "").lower()
        if "简单" in item_type or "基础" in item_type:
            base_difficulty = 2.0
        elif "复合" in item_type or "复杂" in item_type:
            base_difficulty = 4.0
        elif "高级" in item_type:
            base_difficulty = 4.5
        
        # 根据规则数量调整难度
        rules_count = len(item.get("usage_rules", []))
        if rules_count > 3:
            base_difficulty += 0.5
        elif rules_count <= 1:
            base_difficulty -= 0.5
        
        # 根据例句数量调整难度
        examples_count = len(item.get("examples", []))
        if examples_count > 5:
            base_difficulty += 0.3
        elif examples_count <= 2:
            base_difficulty -= 0.3
        
        return max(1.0, min(5.0, base_difficulty))
    
    def generate_syntax_schedule(self, learning_plan: Dict, days: int = 7) -> Dict:
        """生成句法学习计划"""
        stage = learning_plan.get("metadata", {}).get("stage", "")
        plan_name = learning_plan.get("learning_plan", {}).get("learning_plan_name", "")
        
        start_date = datetime.now().strftime("%Y-%m-%d")
        daily_schedule = []
        
        for day in range(days):
            current_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day)).strftime("%Y-%m-%d")
            daily_content = self.generate_daily_syntax(learning_plan, current_date)
            daily_schedule.append(daily_content)
        
        return {
            "plan_name": plan_name,
            "stage": stage,
            "start_date": start_date,
            "days": days,
            "daily_schedule": daily_schedule
        }
    
    def display_syntax_content(self, schedule: Dict) -> None:
        """显示句法学习内容"""
        if not schedule:
            print("❌ 没有句法学习计划数据")
            return
        
        print("📚 句法学习计划")
        print("=" * 80)
        print(f"计划名称: {schedule['plan_name']}")
        print(f"学习阶段: {schedule['stage']}")
        print(f"开始日期: {schedule['start_date']}")
        print(f"生成天数: {schedule['days']}天")
        print()
        
        for i, daily in enumerate(schedule['daily_schedule'], 1):
            print(f"📅 第{i}天 - {daily['date']}")
            print(f"   总句法项目: {daily['total_items']}个")
            
            # 显示学习计划配置信息
            plan_info = daily.get('plan_info', {})
            if plan_info:
                print(f"   学习配置: 每天{plan_info.get('daily_count', 0)}个，总计{plan_info.get('total_count', 0)}个，学习周期{plan_info.get('total_cycles', 0)}次")
                print(f"   比例配置: 小学{plan_info.get('elementary_ratio', 0)}% + 初中{plan_info.get('junior_high_ratio', 0)}% + 高中{plan_info.get('high_school_ratio', 0)}%")
                
                # 显示学习进度信息
                stage = daily.get('stage', '')
                progress_info = self.get_progress_info(stage)
                print(f"   学习进度: 已学{progress_info['learned_count']}个，第{progress_info['current_day']}天")
            print()
            
            if daily['syntax_items']:
                for j, item in enumerate(daily['syntax_items'], 1):
                    print(f"   📖 {j}. {item['name']} ({item['type']})")
                    print(f"      描述: {item['description']}")
                    print(f"      难度: {item['difficulty']:.1f}")
                    print(f"      学习周期: {item.get('study_cycles', 0)}次")
                    
                    if item['structure']:
                        print(f"      结构: {item['structure']}")
                    
                    if item['usage_rules']:
                        print(f"      使用规则:")
                        for rule in item['usage_rules'][:2]:  # 只显示前2个规则
                            print(f"        - {rule}")
                        if len(item['usage_rules']) > 2:
                            print(f"        ... 还有{len(item['usage_rules']) - 2}个规则")
                    
                    if item['examples']:
                        print(f"      例句:")
                        for example in item['examples'][:2]:  # 只显示前2个例句
                            print(f"        - {example}")
                        if len(item['examples']) > 2:
                            print(f"        ... 还有{len(item['examples']) - 2}个例句")
                    
                    print()
            else:
                print("   今天没有句法学习内容")
            
            print("-" * 80)
            print()
    
    def generate_and_display(self, learning_plan: Dict, days: int = 7) -> None:
        """生成并显示句法学习内容"""
        print(f"📋 使用学习计划: {learning_plan.get('id', '未知')}")
        print(f"📋 学习阶段: {learning_plan['metadata']['stage']}")
        print()
        
        # 生成句法学习计划
        schedule = self.generate_syntax_schedule(learning_plan, days)
        
        # 显示学习内容
        self.display_syntax_content(schedule)
        
        # 显示统计信息
        total_items = sum(daily['total_items'] for daily in schedule['daily_schedule'])
        avg_daily = total_items / days if days > 0 else 0
        
        print("📊 句法学习统计:")
        print(f"   总句法项目: {total_items}个")
        print(f"   学习天数: {days}天")
        print(f"   平均每天: {avg_daily:.1f}个句法项目")
        print()


def main():
    """主函数"""
    generator = SyntaxContentGenerator()
    plan_reader = LearningContentGenerator()
    
    print("🔍 句法学习内容生成器")
    print("=" * 50)
    
    # 获取用户输入
    plan_id = input("请输入学习计划ID (按回车使用最新计划): ").strip()
    if not plan_id:
        plans = plan_reader.list_plans()
        if plans:
            plan_id = plans[0]['id']
        else:
            print("❌ 没有找到学习计划")
            return
    
    try:
        days = int(input("请输入生成天数 (默认7天): ").strip() or "7")
    except ValueError:
        days = 7
    
    print()
    
    # 读取学习计划
    learning_plan = plan_reader.read_plan(plan_id=plan_id)
    if not learning_plan:
        print(f"❌ 无法读取学习计划: {plan_id}")
        return
    
    # 生成并显示句法学习内容
    generator.generate_and_display(learning_plan, days)
    
    print("\n✅ 句法学习内容生成完成!")


if __name__ == "__main__":
    main()

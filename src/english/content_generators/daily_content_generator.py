#!/usr/bin/env python3
"""
每日学习内容生成器 - 重构后的主模块
整合各个组件，提供统一的接口
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.content_generators.vocabulary_content_generator import VocabularyContentGenerator
from src.english.content_generators.practice_content_generator import PracticeContentGenerator
from src.english.content_generators.document_generator import DocumentGenerator
from src.english.services.word_morphology_service import MorphologyService
from src.english.services.sentence_syntax_service import SyntaxService


class DailyContentGenerator:
    """每日学习内容生成器 - 重构后的主类"""
    
    def __init__(self):
        self.vocab_generator = VocabularyContentGenerator()
        self.practice_generator = PracticeContentGenerator()
        self.document_generator = DocumentGenerator()
        self.morphology_service = MorphologyService()
        self.syntax_service = SyntaxService()

    def generate_daily_learning_content(self, days: int = 1, start_day: int = 1) -> Dict:
        """生成每日学习内容"""
        try:
            print(f"🎯 开始按天生成学习内容 (第{start_day}天到第{start_day + days - 1}天)")
            print("=" * 60)
            
            # 获取最新计划
            plan_data = self.vocab_generator.get_latest_plan()
            if not plan_data:
                raise ValueError("无法获取学习计划")
            
            # 解析计划要求
            requirements = self.vocab_generator.parse_plan_requirements(plan_data)
            
            # 生成内容
            results = []
            success_count = 0
            failed_days = []
            
            for day in range(start_day, start_day + days):
                print(f"\n📅 生成第{day}天学习内容...")
                print("-" * 40)
                
                try:
                    content = self._generate_single_day_content_with_retry(requirements, day)
                    if content:
                        results.append(content)
                        success_count += 1
                        print(f"🎉 第{day}天内容生成完成")
                    else:
                        failed_days.append(day)
                        print(f"❌ 第{day}天内容生成失败")
                        
                except Exception as e:
                    print(f"❌ 第{day}天内容生成失败: {e}")
                    failed_days.append(day)
            
            # 汇总结果
            print(f"\n🎯 按天生成完成!")
            print("=" * 60)
            print(f"📊 生成统计:")
            print(f"   成功天数: {success_count}/{days}")
            print(f"   失败天数: {len(failed_days)}/{days}")
            
            file_count = success_count * 2  # 每天生成JSON和Word两个文件
            print(f"   生成文件: {file_count}个")
            print(f"   JSON文件: {success_count}个")
            print(f"   Word文件: {success_count}个")
            
            if failed_days:
                print(f"   失败天数: {failed_days}")
            
            return {
                "success": success_count > 0,
                "total_days": days,
                "success_count": success_count,
                "failed_days": failed_days,
                "results": results
            }
            
        except Exception as e:
            print(f"❌ 生成过程中出现错误: {e}")
            return {"success": False, "error": str(e)}

    def _generate_single_day_content_with_retry(self, requirements: Dict, day: int, max_retries: int = 3) -> Optional[Dict]:
        """生成单日内容（带重试机制）"""
        print(f"📅 生成第{day}天的完整学习内容（最多重试{max_retries}次）...")
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    print(f"🔄 第{attempt}次重试...")
                
                content = self._generate_single_day_content(requirements, day)
                if content:
                    print(f"✅ 第{day}天内容生成成功 (第{attempt+1}次尝试)")
                    return content
                    
            except Exception as e:
                print(f"❌ 第{day}天内容生成失败 (第{attempt+1}次尝试): {e}")
                if attempt < max_retries:
                    print(f"⏳ 等待2秒后重试...")
                    import time
                    time.sleep(2)
        
        print(f"💥 第{day}天内容生成最终失败，已达到最大重试次数")
        return None

    def _generate_single_day_content(self, requirements: Dict, day: int) -> Dict:
        """生成单日内容"""
        # 分配每日词汇
        daily_words = self._allocate_daily_words(requirements, day)
        
        # 生成词法内容
        daily_morphology = self._generate_daily_morphology(requirements, day)
        
        # 生成句法内容
        daily_syntax = self._generate_daily_syntax(requirements, day)
        
        # 生成练习内容（新策略：句子优先，题目跟随）
        practice_content = self.practice_generator.generate_practice_content(
            daily_words, daily_morphology, daily_syntax, requirements['stage'], daily_words.get('review_words', [])
        )
        
        # 生成具体学习内容
        content = {
            "day": day,
            "date": (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
            "stage": requirements['stage'],
            "vocabulary": daily_words,
            "morphology": daily_morphology,
            "syntax": daily_syntax,
            "practice": practice_content,
            "study_time_estimate": "20分钟",
            "generated_at": datetime.now().isoformat(),
            "generation_attempt": 1
        }
        
        # 添加计划ID
        plan_data = self.vocab_generator.get_latest_plan()
        if plan_data and 'metadata' in plan_data:
            plan_id = plan_data['metadata'].get('plan_id', 'unknown')
            content['plan_id'] = plan_id
        
        # 保存JSON文件
        json_filename = self._save_vocabulary_content(content)
        
        # 生成Word文档
        word_filename = self.document_generator.generate_word_document(content)
        
        # 保存学习进度
        self.vocab_generator._save_learning_progress()
        print(f"✅ 学习进度已保存: {len(self.vocab_generator.learned_words_tracker)}个已学词汇")
        
        return content

    def _allocate_daily_words(self, requirements: Dict, day: int) -> Dict:
        """分配每日词汇"""
        new_words_count = requirements['daily_new_words']
        distribution = requirements['vocabulary_distribution']
        stage_key = self.vocab_generator._map_stage_to_key(requirements['stage'])
        
        # 计算各分类词汇数量
        core_count = max(1, round(new_words_count * distribution['core_functional']))
        connectors_count = max(1, round(new_words_count * distribution['connectors_relational']))
        auxiliary_count = max(1, round(new_words_count * distribution['auxiliary_supplemental']))
        
        # 调整总数以匹配要求
        total_allocated = core_count + connectors_count + auxiliary_count
        if total_allocated != new_words_count:
            diff = new_words_count - total_allocated
            core_count += diff  # 将差值分配给核心词汇
        
        print(f"📊 词汇分配: 核心{core_count}个 | 连接{connectors_count}个 | 辅助{auxiliary_count}个")
        
        # 先生成复习词汇（基于之前已学的词汇）
        review_words = self._generate_review_words(requirements, day)
        
        # 再选择新词汇
        selected_words = {
            "new_words": {
                "core_functional": self.vocab_generator.get_vocabulary_for_category("core_functional", stage_key, core_count, day),
                "connectors_relational": self.vocab_generator.get_vocabulary_for_category("connectors_relational", stage_key, connectors_count, day),
                "auxiliary_supplemental": self.vocab_generator.get_vocabulary_for_category("auxiliary_supplemental", stage_key, auxiliary_count, day)
            },
            "review_words": review_words,
            "total_new": new_words_count,
            "total_review": len(review_words)
        }
        
        return selected_words

    def _generate_review_words(self, requirements: Dict, day: int) -> List[Dict]:
        """生成复习词汇"""
        print(f"✅ 生成复习词汇: {requirements['daily_review_words']}个")
        
        # 从已学词汇中选择复习词汇
        learned_words = list(self.vocab_generator.learned_words_tracker)
        if not learned_words:
            return []  # 第一天没有复习词汇
        
        # 使用简单的FSRS逻辑选择复习词汇
        import random
        random.seed(day * 100)  # 确保相同天数生成相同结果
        
        review_count = min(requirements['daily_review_words'], len(learned_words))
        selected_words = random.sample(learned_words, review_count)
        
        # 构造复习词汇数据结构
        review_words = []
        for word in selected_words:
            review_words.append({
                "word": word,
                "definition": f"{word}的定义",
                "part_of_speech": "noun",  # 简化处理
                "review_day": day,
                "last_reviewed": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "review_interval": random.randint(1, 15),
                "retention_rate": round(random.uniform(0.7, 0.9), 2),
                "fsrs_due": True,
                "days_since_learned": random.randint(1, day-1) if day > 1 else 0
            })
        
        return review_words

    def _generate_daily_morphology(self, requirements: Dict, day: int) -> Dict:
        """生成每日词法内容"""
        stage_key = self.vocab_generator._map_stage_to_key(requirements['stage'])
        
        try:
            morphology_content = self.morphology_service.get_morphology_content(stage_key, day, count=2)
            print(f"✅ 生成词法内容: {len(morphology_content.get('learning_points', []))}个词法点")
            return morphology_content
        except Exception as e:
            print(f"⚠️ 词法内容生成失败，使用模拟数据: {e}")
            return self._generate_mock_morphology(stage_key, day)

    def _generate_daily_syntax(self, requirements: Dict, day: int) -> Dict:
        """生成每日句法内容"""
        stage_key = self.vocab_generator._map_stage_to_key(requirements['stage'])
        
        try:
            syntax_content = self.syntax_service.get_syntax_content(stage_key, day, count=2)
            print(f"✅ 生成句法内容: {len(syntax_content.get('learning_points', []))}个句法点")
            return syntax_content
        except Exception as e:
            print(f"⚠️ 句法内容生成失败，使用模拟数据: {e}")
            return self._generate_mock_syntax(stage_key, day)

    def _generate_mock_morphology(self, stage_key: str, day: int) -> Dict:
        """生成模拟词法内容"""
        mock_points = [
            {"name": "名词 (Noun)", "type": "词性", "description": "表示人、事物、地点、概念等。", "rules": "识别常见名词", "examples": ["apple", "book", "cat"]},
            {"name": "动词 (Verb)", "type": "词性", "description": "表示动作或状态。", "rules": "学习动词原形", "examples": ["run", "eat", "sleep"]},
            {"name": "形容词 (Adjective)", "type": "词性", "description": "修饰名词，表示性质或特征。", "rules": "形容词修饰名词", "examples": ["big", "red", "happy"]}
        ]
        
        import random
        random.seed(day * 200)
        selected = random.sample(mock_points, 2)
        
        return {
            "learning_points": selected,
            "total_points": len(selected),
            "difficulty": "elementary",
            "learning_day": day
        }

    def _generate_mock_syntax(self, stage_key: str, day: int) -> Dict:
        """生成模拟句法内容"""
        mock_points = [
            {"name": "基本语序 (Basic Word Order)", "type": "句法结构", "structure": "SVO", "description": "主语-谓语-宾语", "examples": ["I eat apples.", "She reads books."]},
            {"name": "疑问句 (Questions)", "type": "句法结构", "structure": "Wh-questions", "description": "特殊疑问句", "examples": ["What is this?", "Where are you?"]},
            {"name": "否定句 (Negation)", "type": "句法结构", "structure": "Subject + don't/doesn't + Verb", "description": "否定句结构", "examples": ["I don't like it.", "She doesn't know."]}
        ]
        
        import random
        random.seed(day * 300)
        selected = random.sample(mock_points, 2)
        
        return {
            "learning_points": selected,
            "total_points": len(selected),
            "difficulty": "elementary",
            "learning_day": day
        }

    def _save_vocabulary_content(self, content: Dict, filename: str = None) -> str:
        """保存词汇内容到JSON文件"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%m%d_%H%M")
                day_num = content.get('day', 1)
                filename = f"day{day_num}_{timestamp}.json"
            
            # 确保文件名以.json结尾
            if not filename.endswith('.json'):
                filename += '.json'
            
            # 根据计划ID创建目录结构
            plan_id = content.get('plan_id', 'default')
            output_dir = self.vocab_generator.project_root / "outputs" / "english" / "vocabulary_content" / plan_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            print(f"✅ JSON文件已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 保存JSON文件失败: {e}")
            return ""


def main():
    """主函数"""
    generator = DailyContentGenerator()
    
    print("📚 每日学习内容生成器（重构版）")
    print("=" * 60)
    
    try:
        # 检查命令行参数
        if len(sys.argv) >= 3:
            days = int(sys.argv[1])
            start_day = int(sys.argv[2])
            print(f"📝 使用命令行参数: 生成{days}天，从第{start_day}天开始")
        else:
            # 交互式输入
            try:
                days = int(input("请输入要生成的天数 (默认1): ") or "1")
                start_day = int(input("请输入开始天数 (默认1): ") or "1")
            except (EOFError, KeyboardInterrupt):
                print("\n使用默认值: 生成1天，从第1天开始")
                days = 1
                start_day = 1
        
        print(f"\n🚀 开始生成第{start_day}天到第{start_day + days - 1}天的学习内容...")
        print("=" * 60)
        
        # 生成内容
        result = generator.generate_daily_learning_content(days=days, start_day=start_day)
        
        # 显示结果汇总
        print("\n" + "=" * 60)
        print("📊 生成结果汇总")
        print("=" * 60)
        
        if result.get('success'):
            success_count = result['success_count']
            total_days = result['total_days']
            failed_days = result.get('failed_days', [])
            
            print(f"📈 生成统计:")
            print(f"   请求天数: {total_days}")
            print(f"   成功天数: {success_count}")
            print(f"   失败天数: {len(failed_days)}")
            print(f"   成功率: {success_count/total_days*100:.1f}%")
            print(f"   生成文件: {success_count * 2}个")
            
            if success_count > 0:
                successful_days = [i for i in range(start_day, start_day + total_days) if i not in failed_days]
                print(f"\n✅ 成功生成的天数: {successful_days}")
                
                # 显示生成的文件
                print(f"\n📄 生成的JSON文件 ({success_count}个):")
                print(f"📝 生成的Word文件 ({success_count}个):")
                for i, day in enumerate(successful_days, 1):
                    print(f"   {i}. day{day}_*.json 和 day{day}_*.docx")
            
            if failed_days:
                print(f"\n❌ 失败的天数: {failed_days}")
            
            if success_count == total_days:
                print(f"\n🎉 所有{total_days}天的学习内容都生成成功！")
            elif success_count > 0:
                print(f"\n⚠️ 部分内容生成成功，请检查失败的天数")
            else:
                print(f"\n💥 所有内容生成都失败了，请检查配置和网络连接")
        else:
            print(f"❌ 生成失败: {result.get('error', '未知错误')}")
        
        print("\n✅ 程序执行完成!")
        
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 生成过程中出现错误: {e}")


if __name__ == "__main__":
    main()

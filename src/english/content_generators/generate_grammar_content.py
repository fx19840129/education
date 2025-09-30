#!/usr/bin/env python3
"""
语法学习内容生成器（合并版）
整合词法（Morphology）和句法（Syntax）学习内容生成功能
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.content_generators.coordinate_learning_content import LearningContentGenerator


class GrammarContentGenerator:
    """语法学习内容生成器（词法+句法）"""
    
    def __init__(self):
        self.plan_reader = LearningContentGenerator()
        self.learning_progress = {}  # 存储学习进度
        self.morphology_progress_file = Path("learning_data/english/morphology_progress.json")
        self.syntax_progress_file = Path("learning_data/english/syntax_progress.json")
        self._load_progress()
    
    def _load_progress(self):
        """加载学习进度"""
        # 加载词法进度
        if self.morphology_progress_file.exists():
            try:
                with open(self.morphology_progress_file, 'r', encoding='utf-8') as f:
                    morphology_progress = json.load(f)
                    self.learning_progress['morphology'] = morphology_progress
            except Exception as e:
                print(f"⚠️ 加载词法进度失败: {e}")
                self.learning_progress['morphology'] = {}
        else:
            self.learning_progress['morphology'] = {}
        
        # 加载句法进度
        if self.syntax_progress_file.exists():
            try:
                with open(self.syntax_progress_file, 'r', encoding='utf-8') as f:
                    syntax_progress = json.load(f)
                    self.learning_progress['syntax'] = syntax_progress
            except Exception as e:
                print(f"⚠️ 加载句法进度失败: {e}")
                self.learning_progress['syntax'] = {}
        else:
            self.learning_progress['syntax'] = {}
    
    def _save_progress(self):
        """保存学习进度"""
        # 保存词法进度
        try:
            self.morphology_progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.morphology_progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_progress.get('morphology', {}), f, 
                         ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存词法进度失败: {e}")
        
        # 保存句法进度
        try:
            self.syntax_progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.syntax_progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_progress.get('syntax', {}), f, 
                         ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存句法进度失败: {e}")
    
    # ========== 词法相关功能 ==========
    
    def load_morphology_data(self, stage: str) -> Dict:
        """加载词法数据"""
        # 根据阶段确定需要加载的词法文件
        sources = self.plan_reader.get_vocab_sources({'metadata': {'stage': stage}})
        morphology_files = sources.get('morphology_files', [])
        
        morphology_data = {}
        for file_path in morphology_files:
            full_path = Path("src/english/config") / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 解析词法数据结构
                        for key, value in data.items():
                            if isinstance(value, dict) and 'parts_of_speech' in value:
                                morphology_data[key] = value['parts_of_speech']
                except Exception as e:
                    print(f"⚠️ 加载词法文件失败 {file_path}: {e}")
        
        return morphology_data
    
    def generate_morphology_content(self, plan_data: Dict, day: int) -> Dict:
        """生成词法学习内容"""
        stage = plan_data.get('metadata', {}).get('stage', 'beginner')
        morphology_data = self.load_morphology_data(stage)
        
        # 获取当天的词法重点
        daily_focus = self._get_daily_morphology_focus(plan_data, day)
        
        content = {
            "day": day,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "morphology",
            "stage": stage,
            "focus": daily_focus,
            "content": {}
        }
        
        # 根据重点生成具体内容
        for focus_item in daily_focus:
            if focus_item in morphology_data:
                pos_data = morphology_data[focus_item]
                content["content"][focus_item] = {
                    "definition": pos_data.get("definition", ""),
                    "examples": pos_data.get("examples", [])[:3],
                    "rules": pos_data.get("rules", [])[:2],
                    "exercises": self._generate_morphology_exercises(focus_item, pos_data)
                }
        
        return content
    
    def _get_daily_morphology_focus(self, plan_data: Dict, day: int) -> List[str]:
        """获取当天词法学习重点"""
        morphology_plan = plan_data.get('morphology_plan', {})
        daily_topics = morphology_plan.get('daily_topics', [])
        
        if day <= len(daily_topics):
            return daily_topics[day - 1].get('topics', [])
        else:
            # 如果超出计划天数，循环使用
            cycle_day = (day - 1) % len(daily_topics) if daily_topics else 0
            return daily_topics[cycle_day].get('topics', []) if daily_topics else []
    
    def _generate_morphology_exercises(self, pos_type: str, pos_data: Dict) -> List[Dict]:
        """生成词法练习题"""
        exercises = []
        
        # 识别练习
        if pos_data.get("examples"):
            exercises.append({
                "type": "identification",
                "question": f"找出下列句子中的{pos_data.get('definition', pos_type)}：",
                "sentence": pos_data["examples"][0] if pos_data["examples"] else "",
                "answer_type": "selection"
            })
        
        # 应用练习
        if pos_data.get("rules"):
            exercises.append({
                "type": "application",
                "question": f"根据{pos_type}的规则，完成下列句子：",
                "rule": pos_data["rules"][0] if pos_data["rules"] else "",
                "answer_type": "fill_blank"
            })
        
        return exercises
    
    # ========== 句法相关功能 ==========
    
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
    
    def generate_syntax_content(self, plan_data: Dict, day: int) -> Dict:
        """生成句法学习内容"""
        stage = plan_data.get('metadata', {}).get('stage', 'beginner')
        syntax_data = self.load_syntax_data(stage)
        
        # 获取当天的句法重点
        daily_focus = self._get_daily_syntax_focus(plan_data, day)
        
        content = {
            "day": day,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "syntax",
            "stage": stage,
            "focus": daily_focus,
            "content": {}
        }
        
        # 根据重点生成具体内容
        for focus_item in daily_focus:
            if focus_item in syntax_data:
                structure_data = syntax_data[focus_item]
                content["content"][focus_item] = {
                    "pattern": structure_data.get("pattern", ""),
                    "description": structure_data.get("description", ""),
                    "examples": structure_data.get("examples", [])[:3],
                    "exercises": self._generate_syntax_exercises(focus_item, structure_data)
                }
        
        return content
    
    def _get_daily_syntax_focus(self, plan_data: Dict, day: int) -> List[str]:
        """获取当天句法学习重点"""
        syntax_plan = plan_data.get('syntax_plan', {})
        daily_topics = syntax_plan.get('daily_topics', [])
        
        if day <= len(daily_topics):
            return daily_topics[day - 1].get('topics', [])
        else:
            # 如果超出计划天数，循环使用
            cycle_day = (day - 1) % len(daily_topics) if daily_topics else 0
            return daily_topics[cycle_day].get('topics', []) if daily_topics else []
    
    def _generate_syntax_exercises(self, structure_type: str, structure_data: Dict) -> List[Dict]:
        """生成句法练习题"""
        exercises = []
        
        # 结构识别练习
        if structure_data.get("examples"):
            exercises.append({
                "type": "structure_identification",
                "question": f"识别下列句子的{structure_type}结构：",
                "sentence": structure_data["examples"][0] if structure_data["examples"] else "",
                "pattern": structure_data.get("pattern", ""),
                "answer_type": "analysis"
            })
        
        # 句子构造练习
        if structure_data.get("pattern"):
            exercises.append({
                "type": "sentence_construction",
                "question": f"根据{structure_type}的模式构造句子：",
                "pattern": structure_data["pattern"],
                "answer_type": "construction"
            })
        
        return exercises
    
    # ========== 综合功能 ==========
    
    def generate_combined_grammar_content(self, plan_data: Dict, day: int) -> Dict:
        """生成综合语法内容（词法+句法）"""
        morphology_content = self.generate_morphology_content(plan_data, day)
        syntax_content = self.generate_syntax_content(plan_data, day)
        
        combined_content = {
            "day": day,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "combined_grammar",
            "stage": plan_data.get('metadata', {}).get('stage', 'beginner'),
            "morphology": morphology_content,
            "syntax": syntax_content,
            "integration_exercises": self._generate_integration_exercises(
                morphology_content, syntax_content
            )
        }
        
        return combined_content
    
    def _generate_integration_exercises(self, morphology_content: Dict, syntax_content: Dict) -> List[Dict]:
        """生成词法句法综合练习"""
        exercises = []
        
        # 综合分析练习
        exercises.append({
            "type": "comprehensive_analysis",
            "question": "分析下列句子的词法和句法特征：",
            "instruction": "请识别句子中的词性分布和句法结构",
            "answer_type": "comprehensive"
        })
        
        # 综合构造练习
        exercises.append({
            "type": "comprehensive_construction",
            "question": "运用今天学习的词法和句法知识构造句子：",
            "requirements": {
                "morphology": morphology_content.get("focus", []),
                "syntax": syntax_content.get("focus", [])
            },
            "answer_type": "construction"
        })
        
        return exercises
    
    def save_daily_progress(self, day: int, content_type: str, progress_data: Dict):
        """保存每日学习进度"""
        date_key = datetime.now().strftime("%Y-%m-%d")
        
        if content_type not in self.learning_progress:
            self.learning_progress[content_type] = {}
        
        self.learning_progress[content_type][date_key] = {
            "day": day,
            "completed": True,
            "timestamp": datetime.now().isoformat(),
            "progress": progress_data
        }
        
        self._save_progress()


def main():
    """主程序入口"""
    generator = GrammarContentGenerator()
    
    # 示例使用
    sample_plan = {
        "metadata": {"stage": "intermediate"},
        "morphology_plan": {
            "daily_topics": [
                {"topics": ["noun", "adjective"]},
                {"topics": ["verb", "adverb"]},
                {"topics": ["preposition", "conjunction"]}
            ]
        },
        "syntax_plan": {
            "daily_topics": [
                {"topics": ["simple_sentence", "compound_sentence"]},
                {"topics": ["complex_sentence", "compound_complex_sentence"]},
                {"topics": ["passive_voice", "conditional_sentences"]}
            ]
        }
    }
    
    print("🎯 语法学习内容生成器")
    print("=" * 50)
    
    day = 1
    
    # 生成词法内容
    print(f"\n📖 第{day}天词法内容：")
    morphology_content = generator.generate_morphology_content(sample_plan, day)
    print(json.dumps(morphology_content, ensure_ascii=False, indent=2))
    
    # 生成句法内容
    print(f"\n📝 第{day}天句法内容：")
    syntax_content = generator.generate_syntax_content(sample_plan, day)
    print(json.dumps(syntax_content, ensure_ascii=False, indent=2))
    
    # 生成综合内容
    print(f"\n🔄 第{day}天综合语法内容：")
    combined_content = generator.generate_combined_grammar_content(sample_plan, day)
    print(json.dumps(combined_content, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

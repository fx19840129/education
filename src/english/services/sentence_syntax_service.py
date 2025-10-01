#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
句法服务
管理句法数据和学习进度
"""

from ast import main
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class SyntaxPoint:
    """句法点数据类"""
    id: str
    name: str
    category: str
    description: str
    examples: List[str]
    difficulty: str
    stage: str

class SyntaxService:
    """句法服务"""
    
    def __init__(self, config_dir: str = "src/english/config"):
        self.config_dir = Path(config_dir)
        self.syntax_configs = self._load_syntax_configs()
    
    def _load_syntax_configs(self) -> Dict[str, List[Dict]]:
        """加载句法配置"""
        syntax_configs = {}
        
        # 加载小学句法
        elementary_file = self.config_dir / "grammar_configs" / "小学句法.json"
        if elementary_file.exists():
            try:
                with open(elementary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 从实际配置文件中提取句法点
                    syntax_points = self._extract_syntax_points(data)
                    syntax_configs["elementary"] = syntax_points
            except Exception as e:
                print(f"⚠️ 加载小学句法失败: {e}")
                syntax_configs["elementary"] = []
        
        # 加载初中句法
        junior_file = self.config_dir / "grammar_configs" / "初中句法.json"
        if junior_file.exists():
            try:
                with open(junior_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    syntax_points = self._extract_syntax_points(data)
                    syntax_configs["junior_high"] = syntax_points
            except Exception as e:
                print(f"⚠️ 加载初中句法失败: {e}")
                syntax_configs["junior_high"] = []
        
        # 加载高中句法
        senior_file = self.config_dir / "grammar_configs" / "高中句法.json"
        if senior_file.exists():
            try:
                with open(senior_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    syntax_points = self._extract_syntax_points(data)
                    syntax_configs["high_school"] = syntax_points
            except Exception as e:
                print(f"⚠️ 加载高中句法失败: {e}")
                syntax_configs["high_school"] = []
        
        return syntax_configs
    
    def _extract_syntax_points(self, data: Dict) -> List[Dict]:
        """从配置文件中提取句法点"""
        syntax_points = []
        
        # 遍历配置文件中的句法结构部分
        for key, value in data.items():
            if isinstance(value, dict):
                # 处理 sentence_structures
                if "sentence_structures" in value:
                    for structure in value["sentence_structures"]:
                        # 创建句法点
                        point = {
                            "id": f"{structure.get('structure_name', '')}_{len(syntax_points)}",
                            "name": structure.get("structure_name", ""),
                            "category": "句法结构",
                            "description": structure.get("description", ""),
                            "examples": [example.get("sentence", "") for example in structure.get("examples", [])],
                            "difficulty": "elementary",
                            "stage": "elementary"
                        }
                        syntax_points.append(point)
                        
                        # 处理子结构
                        if "sub_structures" in structure:
                            for sub_structure in structure["sub_structures"]:
                                sub_point = {
                                    "id": f"{sub_structure.get('name', '')}_{len(syntax_points)}",
                                    "name": sub_structure.get("name", ""),
                                    "category": "子结构",
                                    "description": sub_structure.get("description", ""),
                                    "examples": sub_structure.get("examples", []),
                                    "difficulty": "elementary",
                                    "stage": "elementary"
                                }
                                syntax_points.append(sub_point)
                
                # 处理 common_sentence_patterns
                if "common_sentence_patterns" in value:
                    for pattern in value["common_sentence_patterns"]:
                        # 检查是否需要拆分复合句型
                        if self._should_split_pattern(pattern):
                            # 拆分复合句型
                            split_points = self._split_complex_pattern(pattern, len(syntax_points))
                            syntax_points.extend(split_points)
                        else:
                            # 创建单个句型模式点
                            pattern_point = {
                                "id": f"{pattern.get('pattern_name', '')}_{len(syntax_points)}",
                                "name": pattern.get("pattern_name", ""),
                                "category": "句型模式",
                                "description": f"{pattern.get('type', '')} - {pattern.get('description', '')}",
                                "examples": [example.get("sentence", "") for example in pattern.get("examples", [])],
                                "difficulty": "elementary",
                                "stage": "elementary"
                            }
                            syntax_points.append(pattern_point)
        
        return syntax_points
    
    def _should_split_pattern(self, pattern: Dict) -> bool:
        """判断是否需要拆分复合句型"""
        pattern_name = pattern.get("pattern_name", "").lower()
        description = pattern.get("description", "").lower()
        
        # 需要拆分的复合句型关键词
        split_keywords = [
            "时态句型", "时态", "不同时态",
            "从句句型", "从句", "各类从句",
            "非谓语动词句型", "非谓语动词",
            "情态动词句型", "情态动词",
            "被动语态句型", "被动语态"
        ]
        
        return any(keyword in pattern_name or keyword in description for keyword in split_keywords)
    
    def _split_complex_pattern(self, pattern: Dict, start_id: int) -> List[Dict]:
        """拆分复合句型为多个独立的句法点"""
        split_points = []
        pattern_name = pattern.get("pattern_name", "")
        pattern_type = pattern.get("type", "")
        examples = pattern.get("examples", [])
        
        # 根据句型类型进行拆分
        if "时态句型" in pattern_name:
            split_points = self._split_tense_patterns(pattern, start_id)
        elif "从句句型" in pattern_name or "各类从句" in pattern_name:
            split_points = self._split_clause_patterns(pattern, start_id)
        elif "非谓语动词句型" in pattern_name:
            split_points = self._split_non_finite_patterns(pattern, start_id)
        elif "情态动词句型" in pattern_name:
            split_points = self._split_modal_patterns(pattern, start_id)
        elif "被动语态句型" in pattern_name:
            split_points = self._split_passive_patterns(pattern, start_id)
        else:
            # 默认不拆分
            return []
        
        return split_points
    
    def _split_tense_patterns(self, pattern: Dict, start_id: int) -> List[Dict]:
        """拆分时态句型"""
        split_points = []
        examples = pattern.get("examples", [])
        
        # 定义各种时态
        tenses = [
            ("一般现在时", "Present Simple", "表示经常性、习惯性的动作或状态"),
            ("一般过去时", "Past Simple", "表示过去发生的动作或状态"),
            ("一般将来时", "Future Simple", "表示将来要发生的动作或状态"),
            ("现在进行时", "Present Continuous", "表示现在正在进行的动作"),
            ("过去进行时", "Past Continuous", "表示过去某个时间正在进行的动作"),
            ("现在完成时", "Present Perfect", "表示过去发生但对现在有影响的动作"),
            ("过去完成时", "Past Perfect", "表示过去某个时间之前已经完成的动作"),
            ("将来进行时", "Future Continuous", "表示将来某个时间正在进行的动作")
        ]
        
        for i, (chinese_name, english_name, description) in enumerate(tenses):
            # 为每个时态创建独立的句法点
            point = {
                "id": f"{chinese_name}_{start_id + i}",
                "name": f"{chinese_name}句型",
                "category": "句型模式",
                "description": f"{pattern.get('type', '')} - {description}",
                "examples": [example.get("sentence", "") for example in examples if english_name.lower() in example.get("analysis", "").lower()],
                "difficulty": "elementary",
                "stage": "elementary"
            }
            split_points.append(point)
        
        return split_points
    
    def _split_clause_patterns(self, pattern: Dict, start_id: int) -> List[Dict]:
        """拆分从句句型"""
        split_points = []
        
        clause_types = [
            ("名词性从句", "Noun Clause", "在句中作主语、宾语、表语、同位语"),
            ("定语从句", "Relative Clause", "修饰名词或代词"),
            ("状语从句", "Adverbial Clause", "修饰动词、形容词、副词或整个句子"),
            ("时间状语从句", "Time Clause", "表示时间关系"),
            ("条件状语从句", "Conditional Clause", "表示条件关系"),
            ("原因状语从句", "Reason Clause", "表示原因关系"),
            ("结果状语从句", "Result Clause", "表示结果关系"),
            ("目的状语从句", "Purpose Clause", "表示目的关系")
        ]
        
        for i, (chinese_name, english_name, description) in enumerate(clause_types):
            point = {
                "id": f"{chinese_name}_{start_id + i}",
                "name": f"{chinese_name}句型",
                "category": "句型模式",
                "description": f"{pattern.get('type', '')} - {description}",
                "examples": [],
                "difficulty": "elementary",
                "stage": "elementary"
            }
            split_points.append(point)
        
        return split_points
    
    def _split_non_finite_patterns(self, pattern: Dict, start_id: int) -> List[Dict]:
        """拆分非谓语动词句型"""
        split_points = []
        
        non_finite_types = [
            ("不定式句型", "Infinitive", "to + 动词原形，作主语、宾语、定语、状语等"),
            ("动名词句型", "Gerund", "动词-ing形式，作主语、宾语、定语等"),
            ("现在分词句型", "Present Participle", "动词-ing形式，作定语、状语、补语等"),
            ("过去分词句型", "Past Participle", "动词-ed形式，作定语、状语、补语等")
        ]
        
        for i, (chinese_name, english_name, description) in enumerate(non_finite_types):
            point = {
                "id": f"{chinese_name}_{start_id + i}",
                "name": f"{chinese_name}",
                "category": "句型模式",
                "description": f"{pattern.get('type', '')} - {description}",
                "examples": [],
                "difficulty": "elementary",
                "stage": "elementary"
            }
            split_points.append(point)
        
        return split_points
    
    def _split_modal_patterns(self, pattern: Dict, start_id: int) -> List[Dict]:
        """拆分情态动词句型"""
        split_points = []
        
        modal_types = [
            ("can/could句型", "Ability", "表示能力"),
            ("may/might句型", "Possibility", "表示可能性"),
            ("must句型", "Obligation", "表示义务、必须"),
            ("should句型", "Advice", "表示建议、应该"),
            ("will/would句型", "Future/Polite", "表示将来或礼貌请求"),
            ("shall句型", "Suggestion", "表示建议、提议")
        ]
        
        for i, (chinese_name, english_name, description) in enumerate(modal_types):
            point = {
                "id": f"{chinese_name}_{start_id + i}",
                "name": f"{chinese_name}",
                "category": "句型模式",
                "description": f"{pattern.get('type', '')} - {description}",
                "examples": [],
                "difficulty": "elementary",
                "stage": "elementary"
            }
            split_points.append(point)
        
        return split_points
    
    def _split_passive_patterns(self, pattern: Dict, start_id: int) -> List[Dict]:
        """拆分被动语态句型"""
        split_points = []
        
        passive_types = [
            ("一般现在时被动", "Present Simple Passive", "am/is/are + 过去分词"),
            ("一般过去时被动", "Past Simple Passive", "was/were + 过去分词"),
            ("一般将来时被动", "Future Simple Passive", "will be + 过去分词"),
            ("现在进行时被动", "Present Continuous Passive", "am/is/are being + 过去分词"),
            ("现在完成时被动", "Present Perfect Passive", "have/has been + 过去分词"),
            ("情态动词被动", "Modal Passive", "情态动词 + be + 过去分词")
        ]
        
        for i, (chinese_name, english_name, description) in enumerate(passive_types):
            point = {
                "id": f"{chinese_name}_{start_id + i}",
                "name": f"{chinese_name}",
                "category": "句型模式",
                "description": f"{pattern.get('type', '')} - {description}",
                "examples": [],
                "difficulty": "elementary",
                "stage": "elementary"
            }
            split_points.append(point)
        
        return split_points
    
    def get_syntax_count(self, stage: str) -> int:
        """获取指定阶段的句法点数量"""
        stage_mapping = {
            "小学": "elementary",
            "初中": "junior_high",
            "高中": "high_school"
        }
        
        stage_key = stage_mapping.get(stage, "elementary")
        return len(self.syntax_configs.get(stage_key, []))
    
    def get_syntax_points(self, stage: str) -> List[SyntaxPoint]:
        """获取指定阶段的句法点列表"""
        stage_mapping = {
            "小学": "elementary",
            "初中": "junior_high",
            "高中": "high_school"
        }
        
        stage_key = stage_mapping.get(stage, "elementary")
        points_data = self.syntax_configs.get(stage_key, [])
        
        syntax_points = []
        for point_data in points_data:
            point = SyntaxPoint(
                id=point_data.get("id", ""),
                name=point_data.get("name", ""),
                category=point_data.get("category", ""),
                description=point_data.get("description", ""),
                examples=point_data.get("examples", []),
                difficulty=point_data.get("difficulty", ""),
                stage=stage
            )
            syntax_points.append(point)
        
        return syntax_points
    
    def get_syntax_by_category(self, stage: str, category: str) -> List[SyntaxPoint]:
        """根据分类获取句法点"""
        all_points = self.get_syntax_points(stage)
        return [point for point in all_points if point.category == category]
    
    def get_syntax_statistics(self) -> Dict[str, int]:
        """获取句法统计信息"""
        stats = {}
        for stage, points in self.syntax_configs.items():
            stats[stage] = len(points)
        
        stats["total"] = sum(stats.values())
        return stats
    
    def search_syntax(self, stage: str, keyword: str) -> List[SyntaxPoint]:
        """搜索句法点"""
        all_points = self.get_syntax_points(stage)
        keyword_lower = keyword.lower()
        
        results = []
        for point in all_points:
            if (keyword_lower in point.name.lower() or 
                keyword_lower in point.description.lower() or
                keyword_lower in point.category.lower()):
                results.append(point)
        
        return results
    
    def get_all_syntax_by_stage(self) -> Dict[str, List[SyntaxPoint]]:
        """获取所有学习阶段的句法点列表"""
        all_syntax = {}
        
        stages = ["小学", "初中", "高中"]
        for stage in stages:
            all_syntax[stage] = self.get_syntax_points(stage)
        
        return all_syntax
    
    def get_detailed_syntax_statistics(self) -> Dict[str, Any]:
        """获取详细的句法统计信息"""
        stats = {
            "total_points": 0,
            "by_stage": {},
            "by_category": {}
        }
        
        # 按阶段统计
        for stage in ["小学", "初中", "高中"]:
            points = self.get_syntax_points(stage)
            stats["by_stage"][stage] = {
                "count": len(points),
                "categories": {}
            }
            
            # 按类别统计
            for point in points:
                category = point.category
                if category not in stats["by_category"]:
                    stats["by_category"][category] = 0
                stats["by_category"][category] += 1
                
                if category not in stats["by_stage"][stage]["categories"]:
                    stats["by_stage"][stage]["categories"][category] = 0
                stats["by_stage"][stage]["categories"][category] += 1
            
            stats["total_points"] += len(points)
        
        return stats
    
    def get_syntax_content(self, stage_key: str, day: int, count: int = 2) -> Dict:
        """
        获取每日句法学习内容
        
        Args:
            stage_key: 学习阶段键值 (elementary, junior_high, high_school)
            day: 学习天数
            count: 需要的句法点数量
            
        Returns:
            Dict: 包含句法学习点的字典
        """
        # 映射阶段键值到中文阶段名
        stage_mapping = {
            "elementary": "小学",
            "junior_high": "初中", 
            "high_school": "高中"
        }
        
        stage = stage_mapping.get(stage_key, "小学")
        syntax_points = self.get_syntax_points(stage)
        
        if not syntax_points:
            return {"learning_points": []}
        
        # 使用天数作为种子，确保相同天数生成相同内容
        import random
        random.seed(day * 150)  # 使用不同的种子避免与词法重复
        
        # 随机选择指定数量的句法点
        selected_points = random.sample(syntax_points, min(count, len(syntax_points)))
        
        # 转换为字典格式
        learning_points = []
        for point in selected_points:
            learning_points.append({
                "name": point.name,
                "type": point.category,
                "description": point.description,
                "structure": point.description,  # 使用description作为structure
                "examples": point.examples[:3]  # 最多3个例句
            })
        
        return {
            "learning_points": learning_points,
            "stage": stage,
            "day": day,
            "total_available": len(syntax_points)
        }

if __name__ == "__main__":
    syntax_service = SyntaxService()
    print("句法统计:")
    # 获取所有阶段的句法点
    all_syntax = syntax_service.get_all_syntax_by_stage()
    for stage, points in all_syntax.items():
        print(f"\n=== {stage}句法点 ({len(points)}个) ===")
        for i, point in enumerate(points, 1):
            print(f"{i}. {point.name} ({point.category})")
            print(f"   描述: {point.description}")
            if point.examples:
                print(f"   例句: {', '.join(point.examples[:2])}")  # 显示前2个例句
            print()
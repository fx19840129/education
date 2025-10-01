#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词法服务
管理词法数据和学习进度
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class MorphologyPoint:
    """词法点数据类"""
    id: str
    name: str
    category: str
    description: str
    examples: List[str]
    difficulty: str
    stage: str

class MorphologyService:
    """词法服务"""
    
    def __init__(self, config_dir: str = "src/english/config"):
        self.config_dir = Path(config_dir)
        self.morphology_configs = self._load_morphology_configs()
    
    def _load_morphology_configs(self) -> Dict[str, List[Dict]]:
        """加载词法配置"""
        morphology_configs = {}
        
        # 加载小学词法
        elementary_file = self.config_dir / "morphology_configs" / "小学词法.json"
        if elementary_file.exists():
            try:
                with open(elementary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 从实际配置文件中提取词法点
                    morphology_points = self._extract_morphology_points(data)
                    morphology_configs["elementary"] = morphology_points
            except Exception as e:
                print(f"⚠️ 加载小学词法失败: {e}")
                morphology_configs["elementary"] = []
        
        # 加载初中词法
        junior_file = self.config_dir / "morphology_configs" / "初中词法.json"
        if junior_file.exists():
            try:
                with open(junior_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    morphology_points = self._extract_morphology_points(data)
                    morphology_configs["junior_high"] = morphology_points
            except Exception as e:
                print(f"⚠️ 加载初中词法失败: {e}")
                morphology_configs["junior_high"] = []
        
        # 加载高中词法
        senior_file = self.config_dir / "morphology_configs" / "高中词法.json"
        if senior_file.exists():
            try:
                with open(senior_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    morphology_points = self._extract_morphology_points(data)
                    morphology_configs["high_school"] = morphology_points
            except Exception as e:
                print(f"⚠️ 加载高中词法失败: {e}")
                morphology_configs["high_school"] = []
        
        return morphology_configs
    
    def _extract_morphology_points(self, data: Dict) -> List[Dict]:
        """从配置文件中提取词法点"""
        morphology_points = []
        
        # 遍历配置文件中的词性部分
        for key, value in data.items():
            if isinstance(value, dict) and "parts_of_speech" in value:
                parts_of_speech = value["parts_of_speech"]
                if isinstance(parts_of_speech, list):
                    for pos in parts_of_speech:
                        # 创建词法点
                        point = {
                            "id": f"{pos.get('pos_name', '')}_{len(morphology_points)}",
                            "name": pos.get("pos_name", ""),
                            "category": "词性",
                            "description": pos.get("pos_description", ""),
                            "examples": pos.get("learning_focus", []),
                            "difficulty": "elementary",
                            "stage": "elementary"
                        }
                        morphology_points.append(point)
                        
                        # 处理形式变化
                        if "form_changes" in pos and isinstance(pos["form_changes"], list):
                            for change in pos["form_changes"]:
                                change_point = {
                                    "id": f"{change.get('change_type', '')}_{len(morphology_points)}",
                                    "name": change.get("change_type", ""),
                                    "category": "形式变化",
                                    "description": change.get("description", ""),
                                    "examples": change.get("rules_examples", []),
                                    "difficulty": "elementary",
                                    "stage": "elementary"
                                }
                                morphology_points.append(change_point)
        
        return morphology_points
    
    def get_morphology_count(self, stage: str) -> int:
        """获取指定阶段的词法点数量"""
        stage_mapping = {
            "小学": "elementary",
            "初中": "junior_high", 
            "高中": "high_school"
        }
        
        stage_key = stage_mapping.get(stage, "elementary")
        return len(self.morphology_configs.get(stage_key, []))
    
    def get_morphology_points(self, stage: str) -> List[MorphologyPoint]:
        """获取指定阶段的词法点列表"""
        stage_mapping = {
            "小学": "elementary",
            "初中": "junior_high",
            "高中": "high_school"
        }
        
        stage_key = stage_mapping.get(stage, "elementary")
        points_data = self.morphology_configs.get(stage_key, [])
        
        morphology_points = []
        for point_data in points_data:
            point = MorphologyPoint(
                id=point_data.get("id", ""),
                name=point_data.get("name", ""),
                category=point_data.get("category", ""),
                description=point_data.get("description", ""),
                examples=point_data.get("examples", []),
                difficulty=point_data.get("difficulty", ""),
                stage=stage
            )
            morphology_points.append(point)
        
        return morphology_points
    
    def get_morphology_by_category(self, stage: str, category: str) -> List[MorphologyPoint]:
        """根据分类获取词法点"""
        all_points = self.get_morphology_points(stage)
        return [point for point in all_points if point.category == category]
    
    def get_morphology_statistics(self) -> Dict[str, int]:
        """获取词法统计信息"""
        stats = {}
        for stage, points in self.morphology_configs.items():
            stats[stage] = len(points)
        
        stats["total"] = sum(stats.values())
        return stats
    
    def search_morphology(self, stage: str, keyword: str) -> List[MorphologyPoint]:
        """搜索词法点"""
        all_points = self.get_morphology_points(stage)
        keyword_lower = keyword.lower()
        
        results = []
        for point in all_points:
            if (keyword_lower in point.name.lower() or 
                keyword_lower in point.description.lower() or
                keyword_lower in point.category.lower()):
                results.append(point)
        
        return results
    
    def get_all_morphology_by_stage(self) -> Dict[str, List[MorphologyPoint]]:
        """获取所有学习阶段的词法点列表"""
        all_morphology = {}
        
        stages = ["小学", "初中", "高中"]
        for stage in stages:
            all_morphology[stage] = self.get_morphology_points(stage)
        
        return all_morphology
    
    def get_detailed_morphology_statistics(self) -> Dict[str, Any]:
        """获取详细的词法统计信息"""
        stats = {
            "total_points": 0,
            "by_stage": {},
            "by_category": {}
        }
        
        # 按阶段统计
        for stage in ["小学", "初中", "高中"]:
            points = self.get_morphology_points(stage)
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
    
    def get_morphology_content(self, stage_key: str, day: int, count: int = 2) -> Dict:
        """
        获取每日词法学习内容
        
        Args:
            stage_key: 学习阶段键值 (elementary, junior_high, high_school)
            day: 学习天数
            count: 需要的词法点数量
            
        Returns:
            Dict: 包含词法学习点的字典
        """
        # 映射阶段键值到中文阶段名
        stage_mapping = {
            "elementary": "小学",
            "junior_high": "初中", 
            "high_school": "高中"
        }
        
        stage = stage_mapping.get(stage_key, "小学")
        morphology_points = self.get_morphology_points(stage)
        
        if not morphology_points:
            return {"learning_points": []}
        
        # 使用天数作为种子，确保相同天数生成相同内容
        import random
        random.seed(day * 100)
        
        # 随机选择指定数量的词法点
        selected_points = random.sample(morphology_points, min(count, len(morphology_points)))
        
        # 转换为字典格式
        learning_points = []
        for point in selected_points:
            learning_points.append({
                "name": point.name,
                "type": point.category,
                "description": point.description,
                "rules": point.description,  # 使用description作为rules
                "examples": point.examples[:3]  # 最多3个例句
            })
        
        return {
            "learning_points": learning_points,
            "stage": stage,
            "day": day,
            "total_available": len(morphology_points)
        }


if __name__ == "__main__":
    morphology_service = MorphologyService()
    print("词法统计:")
    # 获取所有阶段的词法点
    all_morphology = morphology_service.get_all_morphology_by_stage()
    for stage, points in all_morphology.items():
        print(f"\n=== {stage}词法点 ({len(points)}个) ===")
        for i, point in enumerate(points, 1):
            print(f"{i}. {point.name} ({point.category})")
            print(f"   描述: {point.description}")
            if point.examples:
                print(f"   例句: {', '.join(point.examples[:2])}")  # 显示前2个例句
            print()

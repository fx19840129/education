#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的单词服务
提供单词统计功能，不依赖复杂的infrastructure
"""

import json
from pathlib import Path
from typing import Dict

class SimpleWordService:
    """简化的单词服务"""
    
    def __init__(self, config_dir: str = "src/english/config"):
        self.config_dir = Path(config_dir)
    
    def get_learning_resource_statistics(self, show_stats: bool = False) -> Dict:
        """获取学习资源统计信息（词汇、词法、句法）"""
        stats = {
            "words": {
                "elementary": 0,  # 小学
                "junior_high": 0,  # 初中
                "high_school": 0,  # 高中
                "total": 0
            },
            "pos_distribution": {
                "elementary": {},  # 小学词性分布
                "junior_high": {},  # 初中词性分布
                "high_school": {},  # 高中词性分布
                "total": {}  # 总计词性分布
            },
            "morphology": {
                "elementary": 0,
                "junior_high": 0,
                "high_school": 0,
                "total": 0
            },
            "syntax": {
                "elementary": 0,
                "junior_high": 0,
                "high_school": 0,
                "total": 0
            }
        }
        
        try:
            # 加载词汇统计
            word_files = [
                ("elementary", "word_configs", "小学英语单词.json"),
                ("junior_high", "word_configs", "初中英语单词.json"),
                ("high_school", "word_configs", "高中英语单词.json")
            ]
            
            for stage, config_dir, filename in word_files:
                file_path = self.config_dir / config_dir / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        stats["words"][stage] = data.get("metadata", {}).get("word_count", 0)
                        # 获取词性分布
                        pos_dist = data.get("metadata", {}).get("pos_distribution", {})
                        stats["pos_distribution"][stage] = pos_dist
            
            # 使用词法服务获取词法统计
            from .morphology_service import MorphologyService
            morphology_service = MorphologyService(str(self.config_dir))
            stats["morphology"]["elementary"] = morphology_service.get_morphology_count("小学")
            stats["morphology"]["junior_high"] = morphology_service.get_morphology_count("初中")
            stats["morphology"]["high_school"] = morphology_service.get_morphology_count("高中")
            
            # 使用句法服务获取句法统计
            from .syntax_service import SyntaxService
            syntax_service = SyntaxService(str(self.config_dir))
            stats["syntax"]["elementary"] = syntax_service.get_syntax_count("小学")
            stats["syntax"]["junior_high"] = syntax_service.get_syntax_count("初中")
            stats["syntax"]["high_school"] = syntax_service.get_syntax_count("高中")
            
            # 计算总计
            stats["words"]["total"] = sum(stats["words"][stage] for stage in ["elementary", "junior_high", "high_school"])
            stats["morphology"]["total"] = sum(stats["morphology"][stage] for stage in ["elementary", "junior_high", "high_school"])
            stats["syntax"]["total"] = sum(stats["syntax"][stage] for stage in ["elementary", "junior_high", "high_school"])
            
            # 计算总计词性分布
            total_pos = {}
            for stage in ["elementary", "junior_high", "high_school"]:
                for pos, count in stats["pos_distribution"][stage].items():
                    total_pos[pos] = total_pos.get(pos, 0) + count
            stats["pos_distribution"]["total"] = total_pos
            
            if show_stats:
                print(f"📊 学习资源统计:")
                print(f"   词汇:")
                print(f"     - 小学: {stats['words']['elementary']}个")
                print(f"     - 初中: {stats['words']['junior_high']}个")
                print(f"     - 高中: {stats['words']['high_school']}个")
                print(f"     - 总计: {stats['words']['total']}个")
                
                # 打印词性分布
                self._print_pos_distribution(stats)
                
                print(f"   词法:")
                print(f"     - 小学: {stats['morphology']['elementary']}个")
                print(f"     - 初中: {stats['morphology']['junior_high']}个")
                print(f"     - 高中: {stats['morphology']['high_school']}个")
                print(f"     - 总计: {stats['morphology']['total']}个")
                print(f"   句法:")
                print(f"     - 小学: {stats['syntax']['elementary']}个")
                print(f"     - 初中: {stats['syntax']['junior_high']}个")
                print(f"     - 高中: {stats['syntax']['high_school']}个")
                print(f"     - 总计: {stats['syntax']['total']}个")
                print()
            
        except Exception as e:
            print(f"⚠️ 加载学习资源统计失败: {e}")
        
        return stats
    
    def _print_pos_distribution(self, stats: Dict) -> None:
        """打印词性分布信息"""
        # 定义词性映射（将复杂词性映射到简单词性）
        pos_mapping = {
            "noun": "名词",
            "verb": "动词", 
            "adjective": "形容词",
            "adverb": "副词",
            "preposition": "介词",
            "pronoun": "代词",
            "conjunction": "连词",
            "article": "冠词",
            "determiner": "限定词",
            "interjection": "感叹词",
            "numeral": "数词",
            "modal": "情态动词",
            "phrase": "短语"
        }
        
        # 统计各阶段的词性分布
        for stage_name, stage_key in [("小学", "elementary"), ("初中", "junior_high"), ("高中", "high_school")]:
            print(f"     {stage_name}词性分布:")
            pos_dist = stats["pos_distribution"][stage_key]
            
            # 按数量排序
            sorted_pos = sorted(pos_dist.items(), key=lambda x: x[1], reverse=True)
            
            # 只显示前10个主要词性
            for pos, count in sorted_pos[:10]:
                pos_name = pos_mapping.get(pos, pos)
                print(f"       - {pos_name}: {count}个")
            
            if len(sorted_pos) > 10:
                print(f"       - 其他: {sum(count for _, count in sorted_pos[10:])}个")
        
        # 打印总计词性分布
        print(f"     总计词性分布:")
        total_pos_dist = stats["pos_distribution"]["total"]
        sorted_total_pos = sorted(total_pos_dist.items(), key=lambda x: x[1], reverse=True)
        
        for pos, count in sorted_total_pos[:10]:
            pos_name = pos_mapping.get(pos, pos)
            print(f"       - {pos_name}: {count}个")
        
        if len(sorted_total_pos) > 10:
            print(f"       - 其他: {sum(count for _, count in sorted_total_pos[10:])}个")

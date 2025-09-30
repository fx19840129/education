#!/usr/bin/env python3
"""
词库选择器
根据学习阶段配置，选择合适的小学、初中、高中词库、词法和句法
"""

from typing import Dict, Tuple, List
from pathlib import Path
import json

class VocabSelector:
    """词库选择器"""
    
    def __init__(self, config_dir: Path = None):
        """
        初始化词库选择器
        
        Args:
            config_dir: 配置文件目录，默认为 src/english/config
        """
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
        
        # 加载词库统计数据
        self.word_stats = self._load_word_statistics()
        
        # 阶段配置映射
        self.stage_configs = {
            "第一阶段": {
                "name": "基础巩固 (小学中高年级)",
                "vocab_ratios": {"elementary": 1.0, "junior_high": 0.0, "high_school": 0.0},
                "morphology_ratios": {"elementary": 1.0, "junior_high": 0.0, "high_school": 0.0},
                "syntax_ratios": {"elementary": 1.0, "junior_high": 0.0, "high_school": 0.0}
            },
            "第二阶段": {
                "name": "小学初中过渡 (小学高年级 - 初一)",
                "vocab_ratios": {"elementary": 0.6, "junior_high": 0.4, "high_school": 0.0},
                "morphology_ratios": {"elementary": 0.7, "junior_high": 0.3, "high_school": 0.0},
                "syntax_ratios": {"elementary": 0.7, "junior_high": 0.3, "high_school": 0.0}
            },
            "第三阶段": {
                "name": "能力构建 (初中低年级)",
                "vocab_ratios": {"elementary": 0.3, "junior_high": 0.7, "high_school": 0.0},
                "morphology_ratios": {"elementary": 0.2, "junior_high": 0.8, "high_school": 0.0},
                "syntax_ratios": {"elementary": 0.2, "junior_high": 0.8, "high_school": 0.0}
            },
            "第四阶段": {
                "name": "综合提升 (初中中高年级)",
                "vocab_ratios": {"elementary": 0.2, "junior_high": 0.8, "high_school": 0.0},
                "morphology_ratios": {"elementary": 0.1, "junior_high": 0.9, "high_school": 0.0},
                "syntax_ratios": {"elementary": 0.1, "junior_high": 0.9, "high_school": 0.0}
            },
            "第五阶段": {
                "name": "初高中过渡 (初三 - 高一)",
                "vocab_ratios": {"elementary": 0.1, "junior_high": 0.55, "high_school": 0.35},
                "morphology_ratios": {"elementary": 0.1, "junior_high": 0.45, "high_school": 0.45},
                "syntax_ratios": {"elementary": 0.1, "junior_high": 0.45, "high_school": 0.45}
            },
            "第六阶段": {
                "name": "精细打磨 (高中低年级)",
                "vocab_ratios": {"elementary": 0.1, "junior_high": 0.25, "high_school": 0.65},
                "morphology_ratios": {"elementary": 0.1, "junior_high": 0.2, "high_school": 0.7},
                "syntax_ratios": {"elementary": 0.1, "junior_high": 0.2, "high_school": 0.7}
            },
            "第七阶段": {
                "name": "拔尖应用 (高中中高年级)",
                "vocab_ratios": {"elementary": 0.05, "junior_high": 0.15, "high_school": 0.8},
                "morphology_ratios": {"elementary": 0.05, "junior_high": 0.15, "high_school": 0.8},
                "syntax_ratios": {"elementary": 0.05, "junior_high": 0.15, "high_school": 0.8}
            }
        }
    
    def _load_word_statistics(self) -> Dict:
        """加载词库统计数据"""
        import sys
        from pathlib import Path
        
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent.parent.parent
        sys.path.append(str(project_root))
        
        from src.english.services.word_data_service import SimpleWordService
        word_service = SimpleWordService()
        return word_service.get_learning_resource_statistics(show_stats=False)
    
    def get_stage_config(self, stage: str) -> Dict:
        """
        获取指定阶段的配置
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            阶段配置字典
        """
        # 清理阶段名称
        clean_stage = stage.replace('### ', '').strip()
        
        # 查找匹配的阶段
        for stage_key, config in self.stage_configs.items():
            if stage_key in clean_stage:
                return config
        
        # 默认返回第一阶段配置
        return self.stage_configs["第一阶段"]
    
    def calculate_stage_resources(self, stage: str) -> Tuple[int, int, int, Dict]:
        """
        计算指定阶段应该使用的资源数量
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            (词汇总量, 词法总量, 句法总量, 词性分布)
        """
        config = self.get_stage_config(stage)
        
        # 获取基础数据
        elementary_words = self.word_stats.get('words', {}).get('elementary', 0)
        junior_high_words = self.word_stats.get('words', {}).get('junior_high', 0)
        high_school_words = self.word_stats.get('words', {}).get('high_school', 0)
        
        elementary_morphology = self.word_stats.get('morphology', {}).get('elementary', 0)
        junior_high_morphology = self.word_stats.get('morphology', {}).get('junior_high', 0)
        high_school_morphology = self.word_stats.get('morphology', {}).get('high_school', 0)
        
        elementary_syntax = self.word_stats.get('syntax', {}).get('elementary', 0)
        junior_high_syntax = self.word_stats.get('syntax', {}).get('junior_high', 0)
        high_school_syntax = self.word_stats.get('syntax', {}).get('high_school', 0)
        
        # 计算词汇总量
        vocab_total = int(
            elementary_words * config['vocab_ratios']['elementary'] +
            junior_high_words * config['vocab_ratios']['junior_high'] +
            high_school_words * config['vocab_ratios']['high_school']
        )
        
        # 计算词法总量
        morphology_total = int(
            elementary_morphology * config['morphology_ratios']['elementary'] +
            junior_high_morphology * config['morphology_ratios']['junior_high'] +
            high_school_morphology * config['morphology_ratios']['high_school']
        )
        
        # 计算句法总量
        syntax_total = int(
            elementary_syntax * config['syntax_ratios']['elementary'] +
            junior_high_syntax * config['syntax_ratios']['junior_high'] +
            high_school_syntax * config['syntax_ratios']['high_school']
        )
        
        # 计算词性分布
        pos_distribution = self._mix_pos_distributions(
            config['vocab_ratios']['elementary'],
            config['vocab_ratios']['junior_high'],
            config['vocab_ratios']['high_school']
        )
        
        return vocab_total, morphology_total, syntax_total, pos_distribution
    
    def _mix_pos_distributions(self, elementary_ratio: float, junior_high_ratio: float, high_school_ratio: float) -> Dict:
        """
        混合三个阶段的词性分布
        
        Args:
            elementary_ratio: 小学比例
            junior_high_ratio: 初中比例
            high_school_ratio: 高中比例
            
        Returns:
            混合后的词性分布字典
        """
        elementary_pos = self.word_stats.get('pos_distribution', {}).get('elementary', {})
        junior_high_pos = self.word_stats.get('pos_distribution', {}).get('junior_high', {})
        high_school_pos = self.word_stats.get('pos_distribution', {}).get('high_school', {})
        
        mixed = {}
        all_pos = set(elementary_pos.keys()) | set(junior_high_pos.keys()) | set(high_school_pos.keys())
        
        for pos in all_pos:
            count_elementary = elementary_pos.get(pos, 0)
            count_junior_high = junior_high_pos.get(pos, 0)
            count_high_school = high_school_pos.get(pos, 0)
            
            mixed[pos] = int(
                count_elementary * elementary_ratio +
                count_junior_high * junior_high_ratio +
                count_high_school * high_school_ratio
            )
        
        return mixed
    
    def get_stage_vocab_details(self, stage: str) -> Dict:
        """
        获取指定阶段的详细词库信息
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            包含各阶段词库详细信息的字典
        """
        config = self.get_stage_config(stage)
        
        # 获取基础数据
        elementary_words = self.word_stats.get('words', {}).get('elementary', 0)
        junior_high_words = self.word_stats.get('words', {}).get('junior_high', 0)
        high_school_words = self.word_stats.get('words', {}).get('high_school', 0)
        
        elementary_morphology = self.word_stats.get('morphology', {}).get('elementary', 0)
        junior_high_morphology = self.word_stats.get('morphology', {}).get('junior_high', 0)
        high_school_morphology = self.word_stats.get('morphology', {}).get('high_school', 0)
        
        elementary_syntax = self.word_stats.get('syntax', {}).get('elementary', 0)
        junior_high_syntax = self.word_stats.get('syntax', {}).get('junior_high', 0)
        high_school_syntax = self.word_stats.get('syntax', {}).get('high_school', 0)
        
        # 计算各阶段实际使用的数量
        vocab_details = {
            'elementary': int(elementary_words * config['vocab_ratios']['elementary']),
            'junior_high': int(junior_high_words * config['vocab_ratios']['junior_high']),
            'high_school': int(high_school_words * config['vocab_ratios']['high_school']),
            'total': 0
        }
        vocab_details['total'] = sum(vocab_details.values())
        
        morphology_details = {
            'elementary': int(elementary_morphology * config['morphology_ratios']['elementary']),
            'junior_high': int(junior_high_morphology * config['morphology_ratios']['junior_high']),
            'high_school': int(high_school_morphology * config['morphology_ratios']['high_school']),
            'total': 0
        }
        morphology_details['total'] = sum(morphology_details.values())
        
        syntax_details = {
            'elementary': int(elementary_syntax * config['syntax_ratios']['elementary']),
            'junior_high': int(junior_high_syntax * config['syntax_ratios']['junior_high']),
            'high_school': int(high_school_syntax * config['syntax_ratios']['high_school']),
            'total': 0
        }
        syntax_details['total'] = sum(syntax_details.values())
        
        return {
            'stage_name': config['name'],
            'vocab_ratios': config['vocab_ratios'],
            'morphology_ratios': config['morphology_ratios'],
            'syntax_ratios': config['syntax_ratios'],
            'vocab_details': vocab_details,
            'morphology_details': morphology_details,
            'syntax_details': syntax_details,
            'pos_distribution': self._mix_pos_distributions(
                config['vocab_ratios']['elementary'],
                config['vocab_ratios']['junior_high'],
                config['vocab_ratios']['high_school']
            )
        }
    
    def list_all_stages(self) -> List[Dict]:
        """
        列出所有可用的学习阶段
        
        Returns:
            所有阶段配置的列表
        """
        stages = []
        for stage_key, config in self.stage_configs.items():
            stages.append({
                'key': stage_key,
                'name': config['name'],
                'vocab_ratios': config['vocab_ratios'],
                'morphology_ratios': config['morphology_ratios'],
                'syntax_ratios': config['syntax_ratios']
            })
        return stages
    
    def get_available_vocab_files(self, stage: str) -> List[str]:
        """
        获取指定阶段应该使用的词库文件列表（总词库）
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            词库文件路径列表
        """
        config = self.get_stage_config(stage)
        vocab_files = []
        
        # 根据比例确定需要哪些词库文件
        if config['vocab_ratios']['elementary'] > 0:
            vocab_files.append('word_configs/小学英语单词.json')
        
        if config['vocab_ratios']['junior_high'] > 0:
            vocab_files.append('word_configs/初中英语单词.json')
        
        if config['vocab_ratios']['high_school'] > 0:
            vocab_files.append('word_configs/高中英语单词.json')
        
        return vocab_files
    
    def get_available_pos_vocab_files(self, stage: str) -> Dict[str, List[str]]:
        """
        获取指定阶段应该使用的按词性分词的词库文件列表
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            按词性分组的词库文件路径字典
        """
        config = self.get_stage_config(stage)
        pos_vocab_files = {}
        
        # 定义所有词性
        pos_list = [
            'noun', 'verb', 'adjective', 'adverb', 'preposition', 
            'pronoun', 'conjunction', 'article', 'determiner', 
            'interjection', 'numeral', 'modal', 'phrase', 'auxiliary'
        ]
        
        # 为每个词性确定需要加载的文件
        for pos in pos_list:
            pos_files = []
            
            if config['vocab_ratios']['elementary'] > 0:
                pos_files.append(f'word_configs/classified_by_pos/小学_{pos}_words.json')
            
            if config['vocab_ratios']['junior_high'] > 0:
                pos_files.append(f'word_configs/classified_by_pos/初中_{pos}_words.json')
            
            if config['vocab_ratios']['high_school'] > 0:
                pos_files.append(f'word_configs/classified_by_pos/高中_{pos}_words.json')
            
            pos_vocab_files[pos] = pos_files
        
        return pos_vocab_files
    
    def get_pos_vocab_file_paths(self, stage: str) -> Dict[str, List[str]]:
        """
        获取指定阶段按词性分词的词库文件完整路径
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            按词性分组的词库文件完整路径字典
        """
        config = self.get_stage_config(stage)
        pos_file_paths = {}
        
        # 定义所有词性
        pos_list = [
            'noun', 'verb', 'adjective', 'adverb', 'preposition', 
            'pronoun', 'conjunction', 'article', 'determiner', 
            'interjection', 'numeral', 'modal', 'phrase', 'auxiliary'
        ]
        
        # 为每个词性确定需要加载的文件完整路径
        for pos in pos_list:
            pos_files = []
            
            if config['vocab_ratios']['elementary'] > 0:
                file_path = self.config_dir / 'word_configs' / 'classified_by_pos' / f'小学_{pos}_words.json'
                if file_path.exists():
                    pos_files.append(str(file_path))
            
            if config['vocab_ratios']['junior_high'] > 0:
                file_path = self.config_dir / 'word_configs' / 'classified_by_pos' / f'初中_{pos}_words.json'
                if file_path.exists():
                    pos_files.append(str(file_path))
            
            if config['vocab_ratios']['high_school'] > 0:
                file_path = self.config_dir / 'word_configs' / 'classified_by_pos' / f'高中_{pos}_words.json'
                if file_path.exists():
                    pos_files.append(str(file_path))
            
            pos_file_paths[pos] = pos_files
        
        return pos_file_paths
    
    def load_pos_words(self, stage: str, pos: str) -> List[Dict]:
        """
        加载指定阶段和词性的单词列表
        
        Args:
            stage: 学习阶段名称
            pos: 词性名称
            
        Returns:
            单词列表
        """
        pos_file_paths = self.get_pos_vocab_file_paths(stage)
        all_words = []
        
        for file_path in pos_file_paths.get(pos, []):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    words = data.get('words', [])
                    all_words.extend(words)
            except Exception as e:
                print(f"⚠️ 加载文件失败 {file_path}: {e}")
        
        return all_words
    
    def get_pos_words_count(self, stage: str, pos: str) -> int:
        """
        获取指定阶段和词性的单词数量
        
        Args:
            stage: 学习阶段名称
            pos: 词性名称
            
        Returns:
            单词数量
        """
        words = self.load_pos_words(stage, pos)
        return len(words)
    
    def get_stage_pos_words_summary(self, stage: str) -> Dict[str, int]:
        """
        获取指定阶段所有词性的单词数量摘要
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            各词性单词数量字典
        """
        pos_list = [
            'noun', 'verb', 'adjective', 'adverb', 'preposition', 
            'pronoun', 'conjunction', 'article', 'determiner', 
            'interjection', 'numeral', 'modal', 'phrase', 'auxiliary'
        ]
        
        pos_counts = {}
        for pos in pos_list:
            pos_counts[pos] = self.get_pos_words_count(stage, pos)
        
        return pos_counts
    
    def get_available_morphology_files(self, stage: str) -> List[str]:
        """
        获取指定阶段应该使用的词法文件列表
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            词法文件路径列表
        """
        config = self.get_stage_config(stage)
        morphology_files = []
        
        # 根据比例确定需要哪些词法文件
        if config['morphology_ratios']['elementary'] > 0:
            morphology_files.append('morphology_configs/小学词法.json')
        
        if config['morphology_ratios']['junior_high'] > 0:
            morphology_files.append('morphology_configs/初中词法.json')
        
        if config['morphology_ratios']['high_school'] > 0:
            morphology_files.append('morphology_configs/高中词法.json')
        
        return morphology_files
    
    def get_available_syntax_files(self, stage: str) -> List[str]:
        """
        获取指定阶段应该使用的句法文件列表
        
        Args:
            stage: 学习阶段名称
            
        Returns:
            句法文件路径列表
        """
        config = self.get_stage_config(stage)
        syntax_files = []
        
        # 根据比例确定需要哪些句法文件
        if config['syntax_ratios']['elementary'] > 0:
            syntax_files.append('grammar_configs/小学句法.json')
        
        if config['syntax_ratios']['junior_high'] > 0:
            syntax_files.append('grammar_configs/初中句法.json')
        
        if config['syntax_ratios']['high_school'] > 0:
            syntax_files.append('grammar_configs/高中句法.json')
        
        return syntax_files

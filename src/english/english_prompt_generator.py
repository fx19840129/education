#!/usr/bin/env python3
"""
英语学习计划AI提示词生成器

这个模块负责为英语学习计划生成AI提示词，支持：
1. 根据学习阶段（小学、初中、高中）生成相应的学习计划提示词
2. 根据学习周期和每日学习时间计算学习内容分配
3. 生成练习句子和练习题的AI提示词
4. 管理词汇、词法、句法的统计信息和配置

主要功能：
- 解析学习阶段配置文件（stage.md）
- 计算各阶段词汇、词法、句法的占比和数量
- 生成结构化的AI提示词，包含详细的学习计划要求
- 支持多种题型（选择题、翻译题、填空题）的提示词生成
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class EnglishLearningPromptGenerator:
    """
    英语学习计划AI提示词生成器
    
    负责根据学习阶段、学习周期、每日学习时间等参数，
    生成用于AI模型的结构化提示词，用于生成学习计划、练习句子和练习题。
    
    Attributes:
        config_dir (Path): 配置文件目录路径
        word_service (SimpleWordService): 单词服务，用于获取词汇统计信息
        word_stats (Dict): 词汇、词法、句法统计信息
        vocab_selector (VocabSelector): 词库选择器，用于选择合适的学习资源
        stage_config (Dict): 学习阶段配置信息
    """
    
    def __init__(self, config_dir: str = "src/english/config"):
        """
        初始化英语学习计划AI提示词生成器
        
        Args:
            config_dir (str): 配置文件目录路径，默认为 "src/english/config"
        """
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))
        
        # 设置配置文件目录
        self.config_dir = Path(config_dir)
        
        # 初始化服务组件
        from services.simple_word_service import SimpleWordService
        from services.vocab_selector import VocabSelector
        
        # 单词服务：获取词汇、词法、句法统计信息
        self.word_service = SimpleWordService()
        self.word_stats = self.word_service.get_learning_resource_statistics(show_stats=False)
        
        # 词库选择器：根据学习阶段选择合适的学习资源
        self.vocab_selector = VocabSelector(self.config_dir)
        
        # 加载学习阶段配置
        self.stage_config = self._load_stage_config()
        
    def _load_stage_config(self) -> Dict:
        """
        加载学习阶段配置文件
        
        从 stage.md 文件中解析学习阶段配置，包括各阶段的词汇、词法、句法占比。
        配置文件格式：
        ```
        第一阶段：基础巩固 (小学中高年级)
        - 词汇：小学100%，初中0%，高中0%
        - 词法：小学100%，初中0%，高中0%
        - 句法：小学100%，初中0%，高中0%
        ```
        
        Returns:
            Dict: 解析后的阶段配置字典，格式为：
            {
                "阶段名": {
                    "name": "阶段描述",
                    "vocab_ratios": {"elementary": 1.0, "junior_high": 0.0, "high_school": 0.0},
                    "morphology_ratios": {"elementary": 1.0, "junior_high": 0.0, "high_school": 0.0},
                    "syntax_ratios": {"elementary": 1.0, "junior_high": 0.0, "high_school": 0.0}
                }
            }
        """
        stage_file = self.config_dir / "stage.md"
        if not stage_file.exists():
            print(f"⚠️ 阶段配置文件不存在: {stage_file}")
            return {}
        
        with open(stage_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stages = {}
        current_stage = None
        current_content = []
        
        for line in content.split('\n'):
            line = line.strip()
            # 匹配格式：第一阶段：基础巩固 (小学中高年级)
            if line.startswith('第') and '阶段：' in line and ('小学' in line or '初中' in line or '高中' in line):
                if current_stage:
                    # 替换阶段内容中的变量并解析占比信息
                    processed_content = self._replace_stage_variables('\n'.join(current_content))
                    stage_ratios = self._parse_stage_ratios('\n'.join(current_content))
                    stages[current_stage] = {
                        'content': processed_content,
                        'ratios': stage_ratios
                    }
                current_stage = line
                current_content = []
            elif current_stage and line:
                current_content.append(line)
        
        if current_stage:
            # 替换最后一个阶段的变量并解析占比信息
            processed_content = self._replace_stage_variables('\n'.join(current_content))
            stage_ratios = self._parse_stage_ratios('\n'.join(current_content))
            stages[current_stage] = {
                'content': processed_content,
                'ratios': stage_ratios
            }
        
        return stages
    
    def _replace_stage_variables(self, content: str) -> str:
        """替换阶段内容中的变量"""
        # 定义变量映射
        variables = {
            "{elementary_total_words}": str(self.word_stats.get("words", {}).get("elementary", 0)),
            "{middle_school_total_words}": str(self.word_stats.get("words", {}).get("junior_high", 0)),
            "{high_school_total_words}": str(self.word_stats.get("words", {}).get("high_school", 0)),
            "{elementary_total_grammar}": str(self.word_stats.get("syntax", {}).get("elementary", 0)),
            "{middle_school_total_grammar}": str(self.word_stats.get("syntax", {}).get("junior_high", 0)),
            "{high_school_total_grammar}": str(self.word_stats.get("syntax", {}).get("high_school", 0)),
            "{elementary_total_morphology}": str(self.word_stats.get("morphology", {}).get("elementary", 0)),
            "{middle_school_total_morphology}": str(self.word_stats.get("morphology", {}).get("junior_high", 0)),
            "{high_school_total_morphology}": str(self.word_stats.get("morphology", {}).get("high_school", 0)),
        }
        
        # 替换变量
        for var, value in variables.items():
            content = content.replace(var, value)
        
        return content
    
    def _parse_stage_ratios(self, content: str) -> Dict:
        """解析阶段内容中的占比信息"""
        ratios = {
            'vocabulary': {'elementary': 0, 'junior_high': 0, 'high_school': 0},
            'morphology': {'elementary': 0, 'junior_high': 0, 'high_school': 0},
            'syntax': {'elementary': 0, 'junior_high': 0, 'high_school': 0}
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # 识别词汇、词法、句法部分
            if '词汇' in line and '总占比' in line:
                current_section = 'vocabulary'
            elif '词法' in line and '总占比' in line:
                current_section = 'morphology'
            elif '句法' in line and '总占比' in line:
                current_section = 'syntax'
            elif line == '词汇':
                current_section = 'vocabulary'
            elif line == '词法':
                current_section = 'morphology'
            elif line == '句法':
                current_section = 'syntax'
            elif line.startswith('小学：') and current_section:
                # 解析小学占比
                try:
                    ratio = int(line.replace('小学：', '').replace('%', ''))
                    ratios[current_section]['elementary'] = ratio
                except ValueError:
                    pass
            elif line.startswith('初中：') and current_section:
                # 解析初中占比
                try:
                    ratio = int(line.replace('初中：', '').replace('%', ''))
                    ratios[current_section]['junior_high'] = ratio
                except ValueError:
                    pass
            elif line.startswith('高中：') and current_section:
                # 解析高中占比
                try:
                    ratio = int(line.replace('高中：', '').replace('%', ''))
                    ratios[current_section]['high_school'] = ratio
                except ValueError:
                    pass
            elif line.startswith('小学词库：'):
                # 处理第一阶段的特殊格式
                try:
                    ratio = int(line.replace('小学词库：', '').replace('%', ''))
                    ratios['vocabulary']['elementary'] = ratio
                except ValueError:
                    pass
            elif line.startswith('小学词法：'):
                # 处理第一阶段词法
                try:
                    ratio = int(line.replace('小学词法：', '').replace('%', ''))
                    ratios['morphology']['elementary'] = ratio
                except ValueError:
                    pass
            elif line.startswith('小学句法：'):
                # 处理第一阶段句法
                try:
                    ratio = int(line.replace('小学句法：', '').replace('%', ''))
                    ratios['syntax']['elementary'] = ratio
                except ValueError:
                    pass
        
        return ratios
    
    def get_stage_options(self) -> List[str]:
        """获取可用的学习阶段列表"""
        return list(self.stage_config.keys())
    
    def get_stage_info(self, stage: str) -> str:
        """获取指定阶段的信息"""
        stage_data = self.stage_config.get(stage, {})
        if isinstance(stage_data, dict):
            return stage_data.get('content', '')
        return stage_data
    
    def get_stage_ratios(self, stage: str) -> Dict:
        """获取指定阶段的占比信息"""
        stage_data = self.stage_config.get(stage, {})
        if isinstance(stage_data, dict):
            return stage_data.get('ratios', {
                'vocabulary': {'elementary': 0, 'junior_high': 0, 'high_school': 0},
                'morphology': {'elementary': 0, 'junior_high': 0, 'high_school': 0},
                'syntax': {'elementary': 0, 'junior_high': 0, 'high_school': 0}
            })
        return {
            'vocabulary': {'elementary': 0, 'junior_high': 0, 'high_school': 0},
            'morphology': {'elementary': 0, 'junior_high': 0, 'high_school': 0},
            'syntax': {'elementary': 0, 'junior_high': 0, 'high_school': 0}
        }
    
    def get_word_statistics(self) -> Dict:
        """获取单词统计信息"""
        return self.word_stats.copy()
    
    
    

    def generate_fsrs_template_prompt(self, total_days: int, daily_minutes: int, 
                                    pos_distribution: Dict, morphology_total: int, 
                                    syntax_total: int, stage: str = "balanced",
                                    learning_efficiency: float = 1.0,
                                    review_efficiency: float = 0.6,
                                    morphology_time: int = 4,
                                    syntax_time: int = 8) -> str:
        """
        生成FSRS算法适配的学习计划模板AI提示词（分段式版本）
        
        Args:
            total_days (int): 总学习周期天数
            daily_minutes (int): 每日学习总时间（分钟）
            pos_distribution (Dict): 词性分布，如 {"noun": 411, "verb": 156, ...}
            morphology_total (int): 词法总数
            syntax_total (int): 句法总数
            stage (str): 学习阶段，默认为"balanced"
            learning_efficiency (int): 学习效率（分钟/词）
            review_efficiency (int): 复习效率（分钟/词）
            morphology_time (int): 词法练习时间（分钟）
            syntax_time (int): 句法练习时间（分钟）
            morphology_ratio (int): 词法比例
            syntax_ratio (int): 句法比例
            
        Returns:
            str: 完整的FSRS模板适配AI提示词
        """
        # 计算总词汇量
        total_vocab = sum(pos_distribution.values())
        
        # 构建词性分布JSON字符串
        import json
        pos_data_json = json.dumps(pos_distribution, separators=(',', ':'))
        
        # 分段式提示词构建
        segments = {
            "objective_scope": f"生成一个'宏观 FSRS 学习计划模板'的 JSON 对象，仅给出全周期的平均每日学习量与比例指导；不包含任何具体词条文本或逐日安排；只输出一个完整 JSON，对象以 {{ 开始、以 }} 结束。",
            
            "input_params": f"total_study_days={total_days}; daily_learning_minutes={daily_minutes}; total_words={total_vocab}; stage={stage}; pos_distribution={pos_data_json}; total_syntax_units={syntax_total}; total_morphology_units={morphology_total}.",
            
            "category_mapping": "core_functional=[noun,verb,adjective]; connectors_relational=[adverb,preposition,conjunction,pronoun,determiner,article,numeral]; auxiliary_supplemental=[interjection,modal,auxiliary,phrase].",
            
            "json_schema": "键名全为小写下划线；数值用数字类型；百分比为 0–100 的数值（非小数比例）。顶层字段包括：metadata, word_categories, fsrs_initial_parameters, daily_planning_guidelines, example_review_item_structure_for_fsrs。字段与示例模式完全一致。",
            
            "metadata_rules": f"estimated_avg_word_rotations_per_cycle= 1 + min({total_days}/1.5,3.0) + (0.5 if {daily_minutes}≥30 else 0)，一位小数；learning_efficiency_estimate={learning_efficiency}；review_efficiency_estimate={review_efficiency}；morphology_practice_time_estimate={morphology_time}；syntax_practice_time_estimate={syntax_time}。",
            
            "fsrs_params": f"default_ease ∈[1.8,2.4]，基于{stage}偏低（1.8–2.0）；new_word_first_review_interval_days: {total_days}>20 ⇒ 0.28–0.47，{stage}减0.02；morphology_first_review_interval_days = 词汇间隔*0.9；syntax_first_review_interval_days = 词汇间隔*1.05。",
            
            "time_budget": f"{daily_minutes} = 新学({learning_efficiency}m/词) + 复习({review_efficiency}m/词) + 词法练习({morphology_time}m/次) + 句法练习({syntax_time}m/次)；若溢出：先将练习=0，再强制新学:复习=1:1（词数相等），仍溢出则按阶段优先新学微调；总和≤{daily_minutes}。",
            
            "word_allocation": f"阶段权重：new_learning=0.7、balanced=0.6、review_focus=0.5；avg_new_words_per_day = min( floor(({daily_minutes}*权重)/(1.6)), ({total_vocab}/{total_days})*1.5 )；avg_review_words_per_day = 同值（1:1）；若 {total_vocab}/{total_days} > 计算值，则允许小数表示；总新词不超过 {total_vocab}，目标可上调至原计算的1.2倍但不得超限。每日新学单词与复习单词要向上取整",
            
            "morph_syntax_allocation": f"avg_new_morphology_units_per_day ≈ {morphology_total}/{total_days}，均匀分布，review 同值；avg_new_syntax_units_per_day ≈ {syntax_total}/{total_days}，review 同值；若时间不足优先词汇；轮转：morphology=min(1.5+{total_days}/15*0.2,3.0)，syntax=min(1.2+{total_days}/15*0.15,2.5)；若时间溢出每次各减0.5直至≤{daily_minutes}。每日新学词法与句法单位要向上取整。",
            
            "pos_composition": f"按分组汇总词数/{total_vocab}×100，四舍五入两位小数；{stage}对 core_functional +10%（从其他组按比例扣除）；末项补差确保三者和=100%。",
            
            "practice_minutes_rules": f"suggested_morphology={morphology_time} if ({daily_minutes}≥15 and 总词预算<20 and 阶段≠review_focus) else 0；suggested_syntax={syntax_time} if ({daily_minutes}≥25 and 总词预算<15) else 0；若总时间>{daily_minutes}，优先减句法练习至0，再减词法练习。",
            
            "example_item": "不填实际内容；id/text 为占位；initial_interval_days 与对应首复间隔一致或近似；status 固定为 review。",
            
            "boundary_checks": f"禁止 NaN/Infinity/空字符串；百分比 0–100；时间与词数≥0；若 {daily_minutes}<4：所有练习=0，新学=复习=floor({daily_minutes}/2)；若 {total_days}=1：轮转=2.0、间隔=0.09、ease=1.8；单位按库总数/天。",
            
            "single_line_note": "单行英文提示，包含：高强度10%缩短、1:1比例、词法句法均匀分配、溢出时先减练习后调轮转。示例：For high-intensity 1:1 ratio, shorten intervals by 10%; cap reviews at new words; allocate morphology/syntax evenly with 2.0 rotations/day; trim practice first if time overflows."
        }
        
        # 构建完整提示词
        prompt = f"""你是精通 FSRS 的语言学习策略师。

## 目标与范围
{segments["objective_scope"]}

## 输入参数
{segments["input_params"]}

## 词类分组映射
{segments["category_mapping"]}

## JSON 结构与键名规范
{segments["json_schema"]}

## metadata 填充规则
{segments["metadata_rules"]}

## FSRS 初始参数计算
{segments["fsrs_params"]}

## 时间预算与优先级
{segments["time_budget"]}

## 词汇日均分配
{segments["word_allocation"]}

## 词法/句法单位与轮转
{segments["morph_syntax_allocation"]}

## 新词构成比例
{segments["pos_composition"]}

## 建议练习分钟数
{segments["practice_minutes_rules"]}

## 示例复习条目占位
{segments["example_item"]}

## 边界与校验
{segments["boundary_checks"]}

## 实现提示语格式
{segments["single_line_note"]}

基于以上所有规则，立即生成符合要求的JSON对象："""
        
        return prompt
    
    def add_ratios_to_learning_plan(self, learning_plan: Dict, stage: str) -> Dict:
        """为学习计划添加比例信息"""
        if not learning_plan or not isinstance(learning_plan, dict):
            return learning_plan
        
        # 获取阶段占比信息
        stage_ratios = self.get_stage_ratios(stage)
        vocab_ratios = stage_ratios.get('vocabulary', {'elementary': 0, 'junior_high': 0, 'high_school': 0})
        morphology_ratios = stage_ratios.get('morphology', {'elementary': 0, 'junior_high': 0, 'high_school': 0})
        syntax_ratios = stage_ratios.get('syntax', {'elementary': 0, 'junior_high': 0, 'high_school': 0})
        
        # 为每个词性添加比例信息
        study_plan = learning_plan.get('study_plan', {})
        for pos in study_plan:
            if isinstance(study_plan[pos], dict):
                study_plan[pos]['elementary_ratio'] = vocab_ratios['elementary']
                study_plan[pos]['junior_high_ratio'] = vocab_ratios['junior_high']
                study_plan[pos]['high_school_ratio'] = vocab_ratios['high_school']
        
        # 为词法添加比例信息
        morphology = learning_plan.get('morphology', {})
        if isinstance(morphology, dict):
            morphology['elementary_ratio'] = morphology_ratios['elementary']
            morphology['junior_high_ratio'] = morphology_ratios['junior_high']
            morphology['high_school_ratio'] = morphology_ratios['high_school']
        
        # 为句法添加比例信息
        syntax = learning_plan.get('syntax', {})
        if isinstance(syntax, dict):
            syntax['elementary_ratio'] = syntax_ratios['elementary']
            syntax['junior_high_ratio'] = syntax_ratios['junior_high']
            syntax['high_school_ratio'] = syntax_ratios['high_school']
        
        return learning_plan
    
    def generate_practice_sentences_prompt(self, daily_words: Dict, daily_morphology: Dict, daily_syntax: Dict, stage: str) -> str:
        """
        生成练习句子的AI提示词
        
        根据当日学习的单词、词法、句法内容，生成用于AI模型创建练习句子的提示词。
        生成的练习句子会包含当日学习的目标单词、词法规则和句法结构。
        
        Args:
            daily_words (Dict): 当日学习的单词内容，格式：
                {
                    "pos_content": {
                        "noun": [{"word": "apple", "translation": "苹果", "difficulty": 3.0}, ...],
                        "verb": [...],
                        ...
                    }
                }
            daily_morphology (Dict): 当日学习的词法内容，格式：
                {
                    "morphology_items": [
                        {"name": "名词复数", "type": "词形变化", "description": "...", "rules": [...]},
                        ...
                    ]
                }
            daily_syntax (Dict): 当日学习的句法内容，格式：
                {
                    "syntax_items": [
                        {"name": "主谓宾结构", "type": "句型", "structure": "S+V+O", "examples": [...]},
                        ...
                    ]
                }
            stage (str): 学习阶段名称
            
        Returns:
            str: 用于生成练习句子的AI提示词，包含：
            - 学习阶段信息
            - 当日学习内容详情
            - 练习句子生成要求
            - 期望的JSON输出格式
        """
        # 收集单词信息
        words_info = []
        for pos, words in daily_words.get('pos_content', {}).items():
            for word in words:
                words_info.append({
                    'word': word['word'],
                    'pos': pos,
                    'translation': word.get('translation', ''),
                    'difficulty': word.get('difficulty', 3.0)
                })
        
        # 收集词法信息
        morphology_info = []
        for item in daily_morphology.get('morphology_items', []):
            morphology_info.append({
                'name': item['name'],
                'type': item['type'],
                'description': item['description'],
                'rules': item.get('rules', [])[:3]  # 只取前3个规则
            })
        
        # 收集句法信息
        syntax_info = []
        for item in daily_syntax.get('syntax_items', []):
            syntax_info.append({
                'name': item['name'],
                'type': item['type'],
                'structure': item['structure'],
                'examples': item.get('examples', [])[:2]  # 只取前2个例句
            })
        
        # 生成提示词
        prompt = f"""你是一个英语教学专家，需要根据每日学习的单词、词法、句法生成练习句子。

学习阶段：{stage}

今日学习内容：
1. 单词列表：
"""
        
        for word in words_info:
            prompt += f"   - {word['word']} ({word['pos']})\n"
        
        if morphology_info:
            prompt += f"\n2. 词法项目：\n"
            for morph in morphology_info:
                prompt += f"   - {morph['name']}: {morph['description']}\n"
                if morph['rules']:
                    prompt += f"     规则: {'; '.join(morph['rules'][:2])}\n"
        
        if syntax_info:
            prompt += f"\n3. 句法结构：\n"
            for syntax in syntax_info:
                prompt += f"   - {syntax['name']}: {syntax['structure']}\n"
                if syntax['examples']:
                    prompt += f"     例句: {'; '.join(syntax['examples'][:1])}\n"
        
        prompt += f"""
请根据以上学习内容生成练习句子，要求：
1. 每个句子必须包含至少一个今日学习的单词
2. 句子要体现今日学习的词法规则
3. 句子要使用今日学习的句法结构
4. 句子难度要适合{stage}阶段
5. 每个句子都要有中文翻译
6. 提供练习类型（翻译、填空、选择等）

请生成8-12个练习句子，以JSON格式返回：
{{
  "practice_sentences": [
    {{
      "sentence": "英文句子",
      "translation": "中文翻译",
      "target_words": ["目标单词1", "目标单词2"],
      "morphology_points": ["词法点1", "词法点2"],
      "syntax_structure": "句法结构",
      "difficulty": 3.0,
      "exercise_type": "translation",
      "explanation": "句子解释"
    }}
  ]
}}

只返回JSON，不要其他文字说明。"""
        
        return prompt
    
    def generate_practice_exercises_prompt(self, daily_words: Dict, daily_morphology: Dict, daily_syntax: Dict, stage: str) -> str:
        """
        生成练习题的AI提示词
        
        根据当日学习的单词、词法、句法内容，生成用于AI模型创建练习题的提示词。
        生成的练习题包括选择题、翻译题、填空题三种题型，每种题型都会涉及当日学习的内容。
        
        Args:
            daily_words (Dict): 当日学习的单词内容，格式同 generate_practice_sentences_prompt
            daily_morphology (Dict): 当日学习的词法内容，格式同 generate_practice_sentences_prompt
            daily_syntax (Dict): 当日学习的句法内容，格式同 generate_practice_sentences_prompt
            stage (str): 学习阶段名称
            
        Returns:
            str: 用于生成练习题的AI提示词，包含：
            - 学习阶段信息
            - 当日学习内容详情
            - 三种题型的生成要求（选择题、翻译题、填空题）
            - 题目难度和内容关联要求
            - 期望的JSON输出格式
        """
        # 收集单词信息
        words_info = []
        for pos, words in daily_words.get('pos_content', {}).items():
            for word in words:
                words_info.append({
                    'word': word['word'],
                    'pos': pos,
                    'translation': word.get('translation', ''),
                    'difficulty': word.get('difficulty', 3.0)
                })
        
        # 收集词法信息
        morphology_info = []
        for item in daily_morphology.get('morphology_items', []):
            morphology_info.append({
                'name': item['name'],
                'type': item['type'],
                'description': item['description'],
                'rules': item.get('rules', [])[:3]  # 只取前3个规则
            })
        
        # 收集句法信息
        syntax_info = []
        for item in daily_syntax.get('syntax_items', []):
            syntax_info.append({
                'name': item['name'],
                'type': item['type'],
                'structure': item['structure'],
                'examples': item.get('examples', [])[:2]  # 只取前2个例句
            })
        
        # 生成提示词
        prompt = f"""你是一个英语教学专家，需要根据每日学习的单词、词法、句法生成练习题。

学习阶段：{stage}

今日学习内容：
1. 单词列表：
"""
        
        for word in words_info:
            prompt += f"   - {word['word']} ({word['pos']})\n"
        
        if morphology_info:
            prompt += f"\n2. 词法项目：\n"
            for morph in morphology_info:
                prompt += f"   - {morph['name']}: {morph['description']}\n"
                if morph['rules']:
                    prompt += f"     规则: {'; '.join(morph['rules'][:2])}\n"
        
        if syntax_info:
            prompt += f"\n3. 句法结构：\n"
            for syntax in syntax_info:
                prompt += f"   - {syntax['name']}: {syntax['structure']}\n"
                if syntax['examples']:
                    prompt += f"     例句: {'; '.join(syntax['examples'][:1])}\n"
        
        prompt += f"""
请根据以上学习内容生成练习题，要求：
1. 每个题目必须涉及今日学习的单词、词法或句法
2. 题目难度要适合{stage}阶段
3. 包含三种题型：选择题、翻译题、填空题
4. 每种题型至少2道题，总共8-12道题
5. 选择题要有4个选项，其中1个正确答案
6. 翻译题要有中英文对照
7. 填空题要有明确的填空位置和答案
8. 每道题都要有详细的解析

请以JSON格式返回：
{{
  "practice_exercises": [
    {{
      "id": 1,
      "type": "choice",
      "question": "题目内容",
      "options": ["选项A", "选项B", "选项C", "选项D"],
      "correct_answer": "A",
      "explanation": "题目解析",
      "target_words": ["相关单词"],
      "morphology_points": ["相关词法点"],
      "syntax_structure": "相关句法结构",
      "difficulty": 3.0
    }},
    {{
      "id": 2,
      "type": "translation",
      "question": "请将以下中文翻译成英文：",
      "chinese_text": "中文句子",
      "english_text": "English sentence",
      "explanation": "翻译要点",
      "target_words": ["相关单词"],
      "morphology_points": ["相关词法点"],
      "syntax_structure": "相关句法结构",
      "difficulty": 3.0
    }},
    {{
      "id": 3,
      "type": "fill_blank",
      "question": "请填入适当的单词：",
      "sentence": "I ___ to school every day.",
      "answer": "go",
      "explanation": "填空解析",
      "target_words": ["相关单词"],
      "morphology_points": ["相关词法点"],
      "syntax_structure": "相关句法结构",
      "difficulty": 3.0
    }}
  ]
}}

只返回JSON，不要其他文字说明。"""
        
        return prompt
    

def main():
    """主函数 - 用于测试"""
    generator = EnglishLearningPromptGenerator()
    
    # 测试FSRS模板提示词生成
    stage = "第一阶段：基础巩固 (小学中高年级)"
    days = 60
    minutes = 30
    pos_distribution = {"noun": 100, "verb": 50, "adjective": 30}
    morphology_total = 13
    syntax_total = 16
    
    prompt = generator.generate_fsrs_template_prompt(
        total_days=days,
        daily_minutes=minutes,
        pos_distribution=pos_distribution,
        morphology_total=morphology_total,
        syntax_total=syntax_total,
        stage=stage
    )
    print("生成的FSRS模板提示词:")
    print("=" * 50)
    print(prompt)


if __name__ == "__main__":
    main()

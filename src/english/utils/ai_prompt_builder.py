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

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.shared.ai_framework.unified_ai_client import UnifiedAIClient, AIModel

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
        from src.english.services.word_data_service import SimpleWordService
        from src.english.services.vocabulary_selection_service import VocabSelector
        
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
            
            "json_schema": "键名全为小写下划线；数值用数字类型；百分比为 0–100 的数值（非小数比例）。必须使用FSRS标准格式字段名：scheduler_config, cards, learning_plan_metadata, daily_targets, word_categories, card_template, review_rating_guide, implementation_notes, generated_at, format_version。字段与FSRS标准格式完全一致。",
            
            "metadata_rules": f"estimated_avg_word_rotations_per_cycle= 1 + min({total_days}/1.5,3.0) + (0.5 if {daily_minutes}≥30 else 0)，一位小数；learning_efficiency_estimate={learning_efficiency}；review_efficiency_estimate={review_efficiency}；morphology_practice_time_estimate={morphology_time}；syntax_practice_time_estimate={syntax_time}。",
            
            "fsrs_params": f"default_ease ∈[1.8,2.4]，基于{stage}偏低（1.8–2.0）；new_word_first_review_interval_days: {total_days}>20 ⇒ 0.28–0.47，{stage}减0.02；morphology_first_review_interval_days = 词汇间隔*0.9；syntax_first_review_interval_days = 词汇间隔*1.05。",
            
            "time_budget": f"{daily_minutes} = 新学({learning_efficiency}m/词) + 复习({review_efficiency}m/词) + 词法练习({morphology_time}m/次) + 句法练习({syntax_time}m/次)；若溢出：先将练习=0，再强制新学:复习=1:1（词数相等），仍溢出则按阶段优先新学微调；总和≤{daily_minutes}。",
            
            "word_allocation": f"阶段权重：new_learning=0.7、balanced=0.6、review_focus=0.5；avg_new_words_per_day = min( floor(({daily_minutes}*权重)/(1.6)), ({total_vocab}/{total_days})*1.5 )；avg_review_words_per_day = 同值（1:1）；若 {total_vocab}/{total_days} > 计算值，则允许小数表示；总新词不超过 {total_vocab}，目标可上调至原计算的1.2倍但不得超限。每日新学单词与复习单词要向上取整",
            
            "morph_syntax_allocation": f"avg_new_morphology_units_per_day ≈ {morphology_total}/{total_days}，均匀分布，review 同值；avg_new_syntax_units_per_day ≈ {syntax_total}/{total_days}，review 同值；若时间不足优先词汇；轮转：morphology=min(1.5+{total_days}/15*0.2,3.0)，syntax=min(1.2+{total_days}/15*0.15,2.5)；若时间溢出每次各减0.5直至≤{daily_minutes}。每日新学词法与句法单位要向上取整。",
            
            "pos_composition": f"按分组汇总词数/{total_vocab}×100，四舍五入两位小数；{stage}对 core_functional +10%（从其他组按比例扣除）；末项补差确保三者和=100%。",
            
            "practice_minutes_rules": f"suggested_morphology={morphology_time} if ({daily_minutes}≥15 and 总词预算<20 and 阶段≠review_focus) else 0；suggested_syntax={syntax_time} if ({daily_minutes}≥25 and 总词预算<15) else 0；若总时间>{daily_minutes}，优先减句法练习至0，再减词法练习。",
            
            "example_item": "不填实际内容；id/text 为占位；initial_interval_days 与对应首复间隔一致或近似；status 固定为 review。",
            
            "boundary_checks": f"禁止 NaN/Infinity/空字符串；百分比 0–100；时间与词数≥0；若 {daily_minutes}<4：所有练习=0，新学=复习=floor({daily_minutes}/2)；若 {total_days}=1：轮转=2.0、间隔=0.09、ease=1.8；单位按库总数/天。",
            
            "single_line_note": "单行英文提示，包含：高强度10%缩短、1:1比例、词法句法均匀分配、溢出时先减练习后调轮转。示例：For high-intensity 1:1 ratio, shorten intervals by 10%; cap reviews at new words; allocate morphology/syntax evenly with 2.0 rotations/day; trim practice first if time overflows.",
            
            "card_template_specification": """card_template字段必须严格按照以下格式（注意数据类型和默认值）：
{
  "id": "PLACEHOLDER_ID",
  "text": "PLACEHOLDER_TEXT", 
  "category": "core_functional",
  "part_of_speech": "noun",
  "due": "2024-01-01T00:00:00Z",
  "stability": 1.0,
  "difficulty": 5.0,
  "elapsed_days": 0,
  "scheduled_days": 1440,
  "reps": 0,
  "lapses": 0,
  "state": 1,
  "last_review": null,
  "review_logs": []
}
关键要求：due必须是ISO时间字符串；stability=1.0，difficulty=5.0（浮点数）；state=1（数字不是字符串）；scheduled_days使用分钟数。""",
            
            "fsrs_standard_format": """返回的JSON必须符合FSRS标准格式要求，包含以下必需字段：
1. scheduler_config: 包含21个FSRS参数的数组、desired_retention(0.9)、learning_steps([1,10])、relearning_steps([10])、maximum_interval(基于ease计算)、enable_fuzzing(true)
2. cards: 空数组[]
3. learning_plan_metadata: 包含total_study_days、daily_learning_minutes_target、各种统计数据
4. daily_targets: 重命名daily_planning_guidelines为daily_targets，包含所有每日目标数据
5. word_categories: 改为复数形式，字段名加_percentage后缀
6. card_template: 使用上述card_template_specification的精确格式
7. review_rating_guide: 1-4评分说明
8. implementation_notes: 实现说明
9. generated_at: 生成时间
10. format_version: "1.0"
注意：字段名必须与标准FSRS格式完全一致，不能使用自定义命名。"""
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

## card_template格式规范
{segments["card_template_specification"]}

## FSRS标准格式要求
{segments["fsrs_standard_format"]}

基于以上所有规则，立即生成符合FSRS标准格式要求的JSON对象："""
        
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
    
    
    def generate_practice_sentences_prompt_v2(self, daily_words: dict, daily_morphology: list, daily_syntax: list, stage: str, review_words: list = None) -> str:
        """
        生成练习句子提示词 - 100%新学单词覆盖策略
        
        Args:
            daily_words: 每日词汇数据
            daily_morphology: 每日词法内容
            daily_syntax: 每日句法内容
            stage: 学习阶段
            review_words: 复习词汇列表
            
        Returns:
            str: 生成的提示词
        """
        # 提取新学单词
        new_words_list = []
        pos_content = daily_words.get('pos_content', {})
        for pos, words in pos_content.items():
            for word_data in words:
                if isinstance(word_data, dict):
                    new_words_list.append(word_data.get('word', ''))
                else:
                    new_words_list.append(str(word_data))
        
        # 处理复习词汇
        review_words_list = []
        if review_words:
            for word in review_words:
                if isinstance(word, dict):
                    review_words_list.append(word.get('word', ''))
                else:
                    review_words_list.append(str(word))
        
        # 构建词法内容
        morphology_content = ""
        if daily_morphology:
            morphology_content += "### 今日词法重点：\n"
            morphology_info = []
            
            # 处理字典或列表类型的daily_morphology
            if isinstance(daily_morphology, dict):
                # 如果是字典，检查learning_points键
                if 'learning_points' in daily_morphology:
                    morphology_info.extend(daily_morphology['learning_points'])
                else:
                    # 如果没有learning_points，将整个字典作为一个条目
                    morphology_info.append(daily_morphology)
            elif isinstance(daily_morphology, list):
                # 如果是列表，遍历每个元素
                for morph in daily_morphology:
                    if isinstance(morph, dict):
                        # 检查是否有 morphology_items 或 learning_points
                        if 'morphology_items' in morph:
                            morphology_info.extend(morph['morphology_items'])
                        elif 'learning_points' in morph:
                            morphology_info.extend(morph['learning_points'])
                        else:
                            # 直接使用当前字典
                            morphology_info.append(morph)
                    else:
                        morphology_info.append(morph)
            
            for morph in morphology_info:
                name = morph.get('name', morph.get('type', '词法规则'))
                description = morph.get('description', morph.get('rules', ''))
                morphology_content += f"- **{name}**: {description}\n"
                if morph.get('examples'):
                    morphology_content += f"  - 规则/例句: {'; '.join(morph['examples'][:2])}\n"
                elif morph.get('rules'):
                    morphology_content += f"  - 规则/例句: {morph['rules']}\n"
        
        # 构建句法内容
        syntax_content = ""
        if daily_syntax:
            syntax_content += "### 今日句法重点：\n"
            syntax_info = []
            
            # 处理字典或列表类型的daily_syntax
            if isinstance(daily_syntax, dict):
                # 如果是字典，检查learning_points键
                if 'learning_points' in daily_syntax:
                    syntax_info.extend(daily_syntax['learning_points'])
                else:
                    # 如果没有learning_points，将整个字典作为一个条目
                    syntax_info.append(daily_syntax)
            elif isinstance(daily_syntax, list):
                # 如果是列表，遍历每个元素
                for syntax in daily_syntax:
                    if isinstance(syntax, dict):
                        # 检查是否有 syntax_items 或 learning_points
                        if 'syntax_items' in syntax:
                            syntax_info.extend(syntax['syntax_items'])
                        elif 'learning_points' in syntax:
                            syntax_info.extend(syntax['learning_points'])
                        else:
                            # 直接使用当前字典
                            syntax_info.append(syntax)
                    else:
                        syntax_info.append(syntax)
            
            for syntax in syntax_info:
                name = syntax.get('name', syntax.get('type', '句法规则'))
                description = syntax.get('description', syntax.get('structure', ''))
                syntax_content += f"- **{name}**: {description}\n"
                if syntax.get('examples'):
                    syntax_content += f"  - 例句: {'; '.join(syntax['examples'][:2])}\n"
        
        # 100%新学单词使用策略
        new_words_count = len(new_words_list)
        
        # 计算复习单词要求
        review_words_count = len(review_words_list)
        target_review_coverage = max(int(review_words_count * 0.7), 1) if review_words_count > 0 else 0
        target_sentences_with_review = max(int(10 * 0.4), 1) if review_words_count > 0 else 0
        
        prompt = f"""🎯 TASK: Create 10 practice sentences with 100% new vocabulary coverage AND 70%+ review word coverage.

📋 NEW WORDS (MUST USE ALL): {new_words_list}
📊 NEW WORDS REQUIREMENT: All {new_words_count} new words MUST appear across the 10 sentences.

📖 REVIEW WORDS (MUST USE 70%+): {review_words_list}
📊 REVIEW WORDS REQUIREMENT: At least {target_review_coverage}/{review_words_count} review words MUST be used across sentences.
📊 SENTENCE DISTRIBUTION: At least {target_sentences_with_review}/10 sentences MUST contain review words.

🔥 MANDATORY DUAL STRATEGY:
1. NEW WORDS: Ensure each new word appears at least once:
   - If 10 new words: 1 word per sentence
   - If fewer than 10: some words appear multiple times  
   - If more than 10: multiple words per sentence

2. REVIEW WORDS: Strategically distribute review words:
   - Prioritize natural integration with new vocabulary
   - Aim for {target_sentences_with_review}+ sentences containing review words
   - Use high-frequency review words first
   - Combine review words with new words in meaningful contexts

💡 INTEGRATION REQUIREMENTS:
- Level: Elementary ({stage})
- Grammar focus: 
{morphology_content}{syntax_content}
- Natural sentence flow combining new and review vocabulary
- Contextually appropriate usage of both word types

📝 JSON OUTPUT FORMAT:
{{
  "practice_sentences": [
    {{
      "sentence": "[English sentence with new word + review word when possible]",
      "translation": "[Chinese translation]",
      "morphology_rule": "[Grammar rule description]",
      "syntactic_structure": "[Sentence structure]",
      "difficulty": 2.5,
      "explanation": "[Chinese explanation of vocabulary and grammar usage]"
    }}
  ]
}}

🚨 ENHANCED VERIFICATION CHECKLIST:
□ All {new_words_count} new words used? 
□ At least {target_review_coverage}/{review_words_count} review words used?
□ At least {target_sentences_with_review}/10 sentences contain review words?
□ Each sentence contains at least one new word?
□ Review words naturally integrated with new words?
□ Exactly 10 sentences generated?
□ JSON format correct?

⚠️ CRITICAL DUAL REQUIREMENTS:
1. Every new word from the list MUST appear in at least one sentence.
2. At least 70% of review words MUST be used across all sentences.
3. At least 40% of sentences MUST contain review words.

RETURN ONLY JSON - NO OTHER TEXT"""
        
        return prompt
    
    def generate_exercises_from_sentences(self, practice_sentences: list, stage: str) -> str:
        """
        基于练习句子生成练习题的提示词
        
        Args:
            practice_sentences: 练习句子列表
            stage: 学习阶段
            
        Returns:
            str: 生成练习题的提示词
        """
        # 提取句子中的所有词汇
        sentences_text = []
        for sentence in practice_sentences:
            sentences_text.append(f"- {sentence.get('sentence', '')}")
        
        sentences_content = "\n".join(sentences_text)
        
        prompt = f"""🎯 TASK: Create 10 practice exercises based on the given practice sentences.

📋 SOURCE SENTENCES:
{sentences_content}

🔥 MANDATORY REQUIREMENTS:
- Generate exactly 10 exercises (4 choice + 4 translation + 2 fill-blank)
- Use vocabulary and structures from the source sentences
- Ensure all exercises are based on the provided sentences
- Level: Elementary ({stage})

📝 EXERCISE TYPES:
1. Multiple Choice (4 exercises): Create questions with 4 options each
2. Translation (4 exercises): Chinese to English translation
3. Fill in the Blank (2 exercises): Complete the sentence

📝 JSON OUTPUT FORMAT:
{{
  "practice_exercises": [
    {{
      "id": 1,
      "type": "choice",
      "question": "[Question based on source sentences]",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": "correct_option",
      "morphology_rule": "语法规则说明",
      "syntactic_structure": "句法结构",
      "difficulty": 2.5,
      "explanation": "中文解释"
    }},
    {{
      "id": 2,
      "type": "translation",
      "question": "请将以下中文翻译成英文",
      "chinese_text": "[Chinese sentence based on source]",
      "english_text": "[English translation from source sentences]",
      "morphology_rule": "语法规则说明",
      "syntactic_structure": "句法结构",
      "difficulty": 2.5,
      "explanation": "中文解释"
    }},
    {{
      "id": 3,
      "type": "fill_blank",
      "question": "请填入适当的单词",
      "sentence": "[Sentence with ___ from source sentences]",
      "answer": "[correct word]",
      "morphology_rule": "语法规则说明",
      "syntactic_structure": "句法结构",
      "difficulty": 2.5,
      "explanation": "中文解释"
    }}
  ]
}}

🚨 VERIFICATION CHECKLIST:
□ All exercises based on source sentences?
□ Exactly 10 exercises generated?
□ 4 choice + 4 translation + 2 fill-blank?
□ All explanations in Chinese?
□ JSON format correct?

RETURN ONLY JSON - NO OTHER TEXT"""
        
        return prompt
    
    def translate_prompt_to_english(self, chinese_prompt: str) -> str:
        """
        将中文提示词翻译成英文
        
        使用智谱GLM模型将中文提示词翻译成英文，保持原有的结构和格式。
        此方法可独立使用，也可配合其他提示词生成方法使用。
        
        使用示例：
            # 先生成中文提示词
            chinese_prompt = generator.generate_practice_sentences_prompt_v2(...)
            # 再翻译为英文
            english_prompt = generator.translate_prompt_to_english(chinese_prompt)
            
            # 或者直接翻译练习题提示词
            chinese_exercises = generator.generate_practice_exercises_prompt(...)
            english_exercises = generator.translate_prompt_to_english(chinese_exercises)
        
        Args:
            chinese_prompt (str): 中文提示词（来自任何生成方法）
            
        Returns:
            str: 翻译后的英文提示词
        """
        # 初始化AI客户端（使用智谱GLM模型）
        ai_client = UnifiedAIClient(default_model=AIModel.GLM_45)
        
        # 构建翻译提示词
        translation_prompt = f"""请将以下中文提示词翻译成英文，保持原有的结构、格式和专业术语的准确性。
要求：
1. 保持JSON格式示例不变
2. 保持专业的教学用语
3. 确保英语教学术语的准确性
4. 保持提示词的逻辑结构

需要翻译的中文提示词：
{chinese_prompt}

请只返回翻译后的英文提示词，不要其他说明。"""

        try:
            # 调用AI进行翻译
            print("🔄 正在调用智谱GLM模型翻译提示词...")
            ai_response = ai_client.generate_content(translation_prompt)
            
            # 检查响应类型并提取内容
            if hasattr(ai_response, 'content'):
                english_prompt = ai_response.content
            else:
                english_prompt = str(ai_response)
            
            # 验证翻译结果
            if english_prompt and len(english_prompt.strip()) > 0:
                print("✅ 提示词翻译完成")
                return english_prompt.strip()
            else:
                print("⚠️ 翻译结果为空，返回原始中文提示词")
                return chinese_prompt
                
        except Exception as e:
            print(f"❌ 翻译失败: {e}")
            print("⚠️ 返回原始中文提示词")
            return chinese_prompt
    
    
    def generate_practice_exercises_prompt(self, daily_words: Dict, daily_morphology: Dict, daily_syntax: Dict, stage: str, review_words: List[Dict] = None) -> str:
        """
        生成练习题的AI提示词
        
        根据当日学习的单词、词法、句法内容，生成用于AI模型创建练习题的提示词。
        仿照练习句子的分段式格式，生成包括选择题、翻译题、填空题的综合练习。
        
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
                    "learning_points": [
                        {"name": "名词复数", "category": "词形变化", "description": "...", "examples": [...]},
                        ...
                    ]
                }
            daily_syntax (Dict): 当日学习的句法内容，格式：
                {
                    "learning_points": [
                        {"name": "主谓宾结构", "category": "句型", "structure": "S+V+O", "examples": [...]},
                        ...
                    ]
                }
            stage (str): 学习阶段，例如 "第一阶段：基础巩固 (小学中高年级)"
            review_words (List[Dict]): 当日复习的单词列表
            
        Returns:
            str: 包含所有必要信息的AI提示词
        """
        if review_words is None:
            review_words = []
        
        # 收集新学单词信息
        new_words_info = []
        for pos, words in daily_words.get('pos_content', {}).items():
            for word in words:
                new_words_info.append({
                    'word': word['word'],
                    'pos': pos,
                    'translation': word.get('translation', ''),
                    'difficulty': word.get('difficulty', 3.0),
                    'type': 'new'
                })
        
        # 收集复习单词信息
        review_words_info = []
        if review_words:
            for word in review_words:
                review_words_info.append({
                    'word': word['word'],
                    'pos': word.get('part_of_speech', 'unknown'),
                    'translation': word.get('definition', ''),
                    'difficulty': word.get('difficulty', 3.0),
                    'type': 'review'
                })
        
        # 合并所有单词
        all_words_info = new_words_info + review_words_info
        
        # 收集词法信息
        morphology_info = []
        # 支持两种数据结构：morphology_items 和 learning_points
        morph_items = daily_morphology.get('morphology_items', []) or daily_morphology.get('learning_points', [])
        for item in morph_items:
            morphology_info.append({
                'name': item.get('name', '未知词法'),
                'type': item.get('type', item.get('category', 'unknown')),
                'description': item.get('description', '词法描述'),
                'rules': item.get('rules', item.get('examples', []))[:3]  # 只取前3个规则/例句
            })
        
        # 收集句法信息
        syntax_info = []
        # 支持两种数据结构：syntax_items 和 learning_points
        syntax_items = daily_syntax.get('syntax_items', []) or daily_syntax.get('learning_points', [])
        for item in syntax_items:
            syntax_info.append({
                'name': item.get('name', '未知句法'),
                'type': item.get('type', item.get('category', 'unknown')),
                'description': item.get('description', '句法描述'),
                'structure': item.get('structure', item.get('description', '')),
                'examples': item.get('examples', [])[:2]  # 只取前2个例句
            })
        
        # 构建新学单词和复习单词列表
        new_words_list = [word['word'] for word in new_words_info]
        review_words_list = [word['word'] for word in review_words_info] if review_words_info else []
        
        # 构建词法内容
        morphology_content = ""
        if morphology_info:
            morphology_content = "\n### 今日词法重点：\n"
            for morph in morphology_info:
                morphology_content += f"- **{morph['name']}**: {morph['description']}\n"
                if morph.get('rules'):
                    morphology_content += f"  - 规则/例句: {'; '.join(morph['rules'][:3])}\n"
        
        # 构建句法内容
        syntax_content = ""
        if syntax_info:
            syntax_content = "\n### 今日句法重点：\n"
            for syntax in syntax_info:
                syntax_content += f"- **{syntax['name']}**: {syntax['description']}\n"
                if syntax.get('examples'):
                    syntax_content += f"  - 例句: {'; '.join(syntax['examples'][:2])}\n"
        
        # 极端优化：逐词指定策略
        new_words_str = str(new_words_list).replace("'", '"')
        
        prompt = f"""TASK: Create exactly 10 English exercises using ALL specified vocabulary words.

TARGET VOCABULARY (MUST USE ALL): {new_words_str}

MANDATORY REQUIREMENTS:
✅ Use EVERY word from the vocabulary list
✅ Generate exactly 10 exercises
✅ 4 multiple choice + 4 translation + 2 fill-blank
✅ Each vocabulary word appears at least once

STRATEGY: Create exercises one by one, ensuring each vocabulary word is used:

Exercise 1 (choice): Use word 1 from list
Exercise 2 (choice): Use word 2 from list  
Exercise 3 (choice): Use word 3 from list
Exercise 4 (choice): Use word 4 from list
Exercise 5 (translation): Use word 5 from list
Exercise 6 (translation): Use word 6 from list
Exercise 7 (translation): Use word 7 from list
Exercise 8 (translation): Use word 8 from list
Exercise 9 (fill_blank): Use word 9 from list
Exercise 10 (fill_blank): Use word 10 from list

GRAMMAR FOCUS:
{morphology_content}{syntax_content}

JSON FORMAT (EXACT STRUCTURE):
{{
  "practice_exercises": [
    {{
      "id": 1,
      "type": "choice",
      "question": "[Question using vocabulary word 1]",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": "correct_option",
      "morphology_rule": "语法规则说明",
      "syntactic_structure": "句法结构",
      "difficulty": 2.5,
      "explanation": "中文解释"
    }},
    {{
      "id": 2,
      "type": "translation", 
      "question": "请将以下中文翻译成英文",
      "chinese_text": "[Chinese sentence with vocabulary word]",
      "english_text": "[English translation]",
      "morphology_rule": "语法规则说明",
      "syntactic_structure": "句法结构", 
      "difficulty": 2.5,
      "explanation": "中文解释"
    }},
    {{
      "id": 3,
      "type": "fill_blank",
      "question": "请填入适当的单词",
      "sentence": "[Sentence with ___ for vocabulary word]",
      "answer": "[vocabulary_word]",
      "morphology_rule": "语法规则说明",
      "syntactic_structure": "句法结构",
      "difficulty": 2.5,
      "explanation": "中文解释"
    }}
  ]
}}

VERIFICATION CHECKLIST:
□ All {len(eval(new_words_str))} vocabulary words used?
□ Exactly 10 exercises created?
□ JSON format correct?
□ All explanations in Chinese?

RETURN ONLY THE JSON - NO OTHER TEXT"""
        
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

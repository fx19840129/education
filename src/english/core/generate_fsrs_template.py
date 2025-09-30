#!/usr/bin/env python3
"""
FSRS模板生成器 - 独立工具脚本
包含FSRS学习计划模板生成、标准格式转换和注解显示功能
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent  # 回到项目根目录
sys.path.insert(0, str(project_root))

# 导入统一AI客户端
from src.shared.ai_framework.unified_ai_client import UnifiedAIClient, AIModel

# 导入提示词生成器
from src.english.utils.ai_prompt_builder import EnglishLearningPromptGenerator


class FSRSTemplateGenerator:
    """FSRS模板生成器 - 独立工具类"""
    
    def __init__(self):
        """初始化FSRS模板生成器"""
        self.prompt_generator = EnglishLearningPromptGenerator()
        self.ai_client = UnifiedAIClient(default_model=AIModel.GLM_45)
    
    def _extract_json_from_content(self, content: str) -> str:
        """从AI响应内容中提取JSON对象"""
        if not content:
            return None
            
        # 方法1: 查找最后一个完整的JSON块（markdown格式）
        json_start = content.rfind('```json')
        if json_start != -1:
            json_start = content.find('{', json_start)
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                potential_json = content[json_start:json_end]
                # 验证是否为有效JSON
                try:
                    import json
                    json.loads(potential_json)
                    print(f"✅ 从markdown代码块中提取到有效JSON")
                    return potential_json
                except:
                    pass
        
        # 方法2: 查找第一个{到最后一个}的内容
        first_brace = content.find('{')
        last_brace = content.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            potential_json = content[first_brace:last_brace + 1]
            # 验证是否为有效JSON
            try:
                import json
                json.loads(potential_json)
                print(f"✅ 从内容中提取到有效JSON (长度: {len(potential_json)} 字符)")
                return potential_json
            except Exception as e:
                print(f"⚠️ JSON验证失败: {e}")
                pass
        
        # 方法3: 使用正则表达式查找JSON结构
        import re
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, content, re.DOTALL)
        for match in reversed(matches):  # 从最后一个匹配开始尝试
            try:
                import json
                json.loads(match)
                print(f"✅ 通过正则表达式提取到有效JSON")
                return match
            except:
                continue
        
        print(f"❌ 无法从内容中提取有效的JSON对象")
        return None

    def convert_to_fsrs_standard_format(self, template: Dict) -> Dict:
        """将FSRS模板转换成FSRS标准格式的JSON
        
        Args:
            template (Dict): 生成的FSRS模板
            
        Returns:
            Dict: FSRS标准格式的数据结构
        """
        print(f"\n🔄 正在转换为FSRS标准格式...")
        
        try:
            # 从模板中提取关键信息
            fsrs_template = template.get('fsrs_template', template)
            metadata = fsrs_template.get('metadata', {})
            fsrs_params = fsrs_template.get('fsrs_initial_parameters', {})
            daily_guidelines = fsrs_template.get('daily_planning_guidelines', {})
            word_categories = fsrs_template.get('word_categories', {})
            
            # 构建FSRS标准格式
            fsrs_standard = {
                "scheduler_config": {
                    "parameters": [
                        0.2172, 1.1771, 3.2602, 16.1507, 7.0114, 0.57, 2.0966, 0.0069, 1.5261, 0.112,
                        1.0178, 1.849, 0.1133, 0.3127, 2.2934, 0.2191, 3.0004, 0.7536, 0.3332, 0.1437, 0.2
                    ],
                    "desired_retention": 0.9,
                    "learning_steps": [1, 10],  # 分钟
                    "relearning_steps": [10],   # 分钟
                    "maximum_interval": int(fsrs_params.get('default_ease', 2.0) * 365),  # 基于ease计算最大间隔
                    "enable_fuzzing": True
                },
                "cards": [],  # 空的卡片列表，将由具体词汇填充
                "learning_plan_metadata": {
                    "total_study_days": metadata.get('total_study_days', 30),
                    "daily_learning_minutes_target": metadata.get('daily_learning_minutes_target', 30),
                    "total_words_in_library": metadata.get('total_words_in_library', 0),
                    "total_morphology_units_in_library": metadata.get('total_morphology_units_in_library', 0),
                    "total_syntax_units_in_library": metadata.get('total_syntax_units_in_library', 0),
                    "estimated_avg_word_rotations_per_cycle": metadata.get('estimated_avg_word_rotations_per_cycle', 2.0),
                    "learning_efficiency_estimate": metadata.get('learning_efficiency_estimate', 1.0),
                    "review_efficiency_estimate": metadata.get('review_efficiency_estimate', 0.6),
                    "morphology_practice_time_estimate": metadata.get('morphology_practice_time_estimate', 4),
                    "syntax_practice_time_estimate": metadata.get('syntax_practice_time_estimate', 8)
                },
                "daily_targets": {
                    "avg_new_words_per_day": daily_guidelines.get('avg_new_words_per_day', 8),
                    "avg_review_words_per_day": daily_guidelines.get('avg_review_words_per_day', 8),
                    "avg_new_morphology_units_per_day": daily_guidelines.get('avg_new_morphology_units_per_day', 1),
                    "avg_review_morphology_units_per_day": daily_guidelines.get('avg_review_morphology_units_per_day', 1),
                    "avg_new_syntax_units_per_day": daily_guidelines.get('avg_new_syntax_units_per_day', 1),
                    "avg_review_syntax_units_per_day": daily_guidelines.get('avg_review_syntax_units_per_day', 1),
                    "suggested_morphology_practice_minutes_per_day": daily_guidelines.get('suggested_morphology_practice_minutes_per_day', 4),
                    "suggested_syntax_practice_minutes_per_day": daily_guidelines.get('suggested_syntax_practice_minutes_per_day', 8)
                },
                "word_categories": word_categories,
                "card_template": {
                    "id": "PLACEHOLDER_ID",
                    "text": "PLACEHOLDER_TEXT", 
                    "category": "core_functional",  # core_functional | connectors_relational | auxiliary_supplemental | morphology | syntax
                    "part_of_speech": "noun",  # 具体词性
                    "due": "2024-01-01T00:00:00Z",  # UTC时间
                    "stability": 1.0,  # FSRS稳定性参数
                    "difficulty": 5.0,  # FSRS难度参数
                    "elapsed_days": 0,  # 经过天数
                    "scheduled_days": int(fsrs_params.get('new_word_first_review_interval_days', 0.3) * 24 * 60),  # 转换为分钟
                    "reps": 0,  # 复习次数
                    "lapses": 0,  # 遗忘次数
                    "state": 1,  # 1=Learning, 2=Review, 3=Relearning
                    "last_review": None,  # 最后复习时间
                    "review_logs": []  # 复习历史
                },
                "review_rating_guide": {
                    "1": "Again - 完全忘记",
                    "2": "Hard - 困难记起",
                    "3": "Good - 犹豫后记起", 
                    "4": "Easy - 轻松记起"
                },
                "implementation_notes": daily_guidelines.get('notes_for_fsrs_implementation', 
                    "For FSRS implementation: Use scheduler_config to initialize FSRS scheduler, create cards based on card_template, and follow daily_targets for content generation."),
                "generated_at": datetime.now().isoformat(),
                "format_version": "1.0"
            }
            
            print(f"✅ 成功转换为FSRS标准格式")
            print(f"   调度器参数: {len(fsrs_standard['scheduler_config']['parameters'])}个")
            print(f"   学习步骤: {fsrs_standard['scheduler_config']['learning_steps']}")
            print(f"   复习步骤: {fsrs_standard['scheduler_config']['relearning_steps']}")
            print(f"   最大间隔: {fsrs_standard['scheduler_config']['maximum_interval']}天")
            print(f"   每日新词目标: {fsrs_standard['daily_targets']['avg_new_words_per_day']}个")
            print(f"   每日复习目标: {fsrs_standard['daily_targets']['avg_review_words_per_day']}个")
            
            return fsrs_standard
            
        except Exception as e:
            print(f"❌ 转换为FSRS标准格式失败: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"转换失败: {e}"}

    def print_fsrs_template_with_annotations(self, full_template: Dict):
        """打印带有中文注解的FSRS模板内容"""
        import json
        
        template = full_template.get("fsrs_template", {})
        
        # 显示简化的带注解版本
        print("📊 FSRS学习计划模板 - 字段说明")
        print("=" * 50)
        
        # 元数据信息
        if "metadata" in template:
            print("\n📊 元数据信息 (metadata):")
            metadata = template["metadata"]
            print(f"  • total_study_days: {metadata.get('total_study_days', 'N/A')} // 总学习周期天数")
            print(f"  • daily_learning_minutes_target: {metadata.get('daily_learning_minutes_target', 'N/A')} // 每日学习总时间（分钟）")
            print(f"  • total_words_in_library: {metadata.get('total_words_in_library', 'N/A')} // 词库总词数")
            print(f"  • total_morphology_units_in_library: {metadata.get('total_morphology_units_in_library', 'N/A')} // 词法库总单位数")
            print(f"  • total_syntax_units_in_library: {metadata.get('total_syntax_units_in_library', 'N/A')} // 句法库总单位数")
            print(f"  • estimated_avg_word_rotations_per_cycle: {metadata.get('estimated_avg_word_rotations_per_cycle', 'N/A')} // 每个单词在周期内的平均复习次数")
            print(f"  • learning_efficiency_estimate: {metadata.get('learning_efficiency_estimate', 'N/A')} // 学习新单词估算时间（分钟）")
            print(f"  • review_efficiency_estimate: {metadata.get('review_efficiency_estimate', 'N/A')} // 复习单词估算时间（分钟）")
            print(f"  • morphology_practice_time_estimate: {metadata.get('morphology_practice_time_estimate', 'N/A')} // 词法练习估算时间（分钟）")
            print(f"  • syntax_practice_time_estimate: {metadata.get('syntax_practice_time_estimate', 'N/A')} // 句法练习估算时间（分钟）")
        
        # 词性分类
        if "word_categories" in template:
            print("\n🏷️ 词性分类定义 (word_categories):")
            categories = template["word_categories"]
            print(f"  • core_functional: {categories.get('core_functional', [])} // 核心功能词（句子骨架，主要动作和对象）")
            print(f"  • connectors_relational: {categories.get('connectors_relational', [])} // 连接与关系词（连接、修饰、限定、表达关系）")
            print(f"  • auxiliary_supplemental: {categories.get('auxiliary_supplemental', [])} // 辅助与补充词（语气、情感、辅助功能）")
        
        # FSRS参数
        if "fsrs_initial_parameters" in template:
            print("\n🎯 FSRS算法初始参数 (fsrs_initial_parameters):")
            fsrs_params = template["fsrs_initial_parameters"]
            print(f"  • default_ease: {fsrs_params.get('default_ease', 'N/A')} // 默认难度系数（由模型根据目标复习次数和周期计算）")
            print(f"  • new_word_first_review_interval_days: {fsrs_params.get('new_word_first_review_interval_days', 'N/A')} // 新单词首次复习间隔天数（由模型建议）")
            print(f"  • morphology_first_review_interval_days: {fsrs_params.get('morphology_first_review_interval_days', 'N/A')} // 词法首次复习间隔天数（由模型建议）")
            print(f"  • syntax_first_review_interval_days: {fsrs_params.get('syntax_first_review_interval_days', 'N/A')} // 句法首次复习间隔天数（由模型建议）")
        
        # 每日规划指导
        if "daily_planning_guidelines" in template:
            print("\n📅 每日学习量和分布的宏观指导 (daily_planning_guidelines):")
            guidelines = template["daily_planning_guidelines"]
            print(f"  • avg_new_words_per_day: {guidelines.get('avg_new_words_per_day', 'N/A')} // 整个周期内平均每天学习的新单词总数")
            print(f"  • avg_review_words_per_day: {guidelines.get('avg_review_words_per_day', 'N/A')} // 整个周期内平均每天复习的单词总数")
            print(f"  • avg_new_morphology_units_per_day: {guidelines.get('avg_new_morphology_units_per_day', 'N/A')} // 整个周期内平均每天学习的新词法单位数")
            print(f"  • avg_review_morphology_units_per_day: {guidelines.get('avg_review_morphology_units_per_day', 'N/A')} // 整个周期内平均每天复习的词法单位数")
            print(f"  • avg_new_syntax_units_per_day: {guidelines.get('avg_new_syntax_units_per_day', 'N/A')} // 整个周期内平均每天学习的新句法单位数")
            print(f"  • avg_review_syntax_units_per_day: {guidelines.get('avg_review_syntax_units_per_day', 'N/A')} // 整个周期内平均每天复习的句法单位数")
            print(f"  • morphology_rotation_cycles_per_day: {guidelines.get('morphology_rotation_cycles_per_day', 'N/A')} // 词法单位每日轮转次数")
            print(f"  • syntax_rotation_cycles_per_day: {guidelines.get('syntax_rotation_cycles_per_day', 'N/A')} // 句法单位每日轮转次数")
            
            if "new_words_composition_guideline" in guidelines:
                print("  • new_words_composition_guideline: // 新学单词的词性分布指示（按百分比）")
                composition = guidelines["new_words_composition_guideline"]
                print(f"    - core_functional_percentage: {composition.get('core_functional_percentage', 'N/A')}% // 核心功能词（名词、动词、形容词）的总百分比")
                print(f"    - connectors_relational_percentage: {composition.get('connectors_relational_percentage', 'N/A')}% // 连接与关系词的总百分比")
                print(f"    - auxiliary_supplemental_percentage: {composition.get('auxiliary_supplemental_percentage', 'N/A')}% // 辅助与补充词的总百分比")
            
            print(f"  • suggested_morphology_practice_minutes_per_day: {guidelines.get('suggested_morphology_practice_minutes_per_day', 'N/A')} // 每日建议的词法练习分钟数")
            print(f"  • suggested_syntax_practice_minutes_per_day: {guidelines.get('suggested_syntax_practice_minutes_per_day', 'N/A')} // 每日建议的句法练习分钟数")
            print(f"  • notes_for_fsrs_implementation: // 关于如何使用此模板和FSRS工具的提示")
            print(f"    \"{guidelines.get('notes_for_fsrs_implementation', 'N/A')}\"")
        
        # 复习项示例
        if "example_review_item_structure_for_fsrs" in template:
            print("\n📝 复习项的FSRS输入格式示例 (example_review_item_structure_for_fsrs):")
            example = template["example_review_item_structure_for_fsrs"]
            print(f"  • id: \"{example.get('id', 'PLACEHOLDER_ID')}\" // 项目唯一标识")
            print(f"  • text: \"{example.get('text', 'PLACEHOLDER_TEXT')}\" // 单词文本")
            print(f"  • category: \"{example.get('category', '...')}\" // 单词类别")
            print(f"  • part_of_speech: \"{example.get('part_of_speech', '...')}\" // 词性")
            print(f"  • initial_interval_days: \"{example.get('initial_interval_days', '1')}\" // 初始复习间隔天数（建议值）")
            print(f"  • status: \"{example.get('status', 'review')}\" // 复习状态")
        
        print("\n" + "=" * 50)
        print("📄 完整JSON结构:")
        print(json.dumps(full_template, ensure_ascii=False, indent=2))

    def generate_fsrs_template(self, stage: str, days: int, minutes: int, 
                               learning_efficiency: float = 1.0, review_efficiency: float = 0.6,
                               morphology_time: int = 4, syntax_time: int = 8) -> Dict:
        """生成FSRS算法适配的学习计划模板"""
        print(f"\n🔄 正在生成FSRS学习计划模板...")
        print(f"   学习阶段: {stage}")
        print(f"   学习周期: {days} 天")
        print(f"   每日时间: {minutes} 分钟")
        print(f"   效率参数: 学习{learning_efficiency}分钟/词, 复习{review_efficiency}分钟/词, 词法{morphology_time}分钟/次, 句法{syntax_time}分钟/次")
        
        # 获取词性分布数据
        vocab_selector = self.prompt_generator.vocab_selector
        pos_distribution = vocab_selector.get_stage_pos_words_summary(stage)
        morphology_total = 13
        syntax_total = 16
        
        # 生成FSRS模板的AI提示词
        prompt = self.prompt_generator.generate_fsrs_template_prompt(
            days, minutes, pos_distribution, morphology_total, syntax_total, stage,
            learning_efficiency, review_efficiency, morphology_time, syntax_time
        )
        
        print("=" * 80)
        print("📝 完整FSRS模板提示词:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        
        # 调用AI模型生成学习计划模板
        print(f"\n🤖 正在调用AI模型生成FSRS学习计划模板...")
        start_time = time.time()
        
        try:
            print(f"🎯 开始调用AI生成FSRS学习计划模板")
            print(f"   学习阶段: {stage}")
            print(f"   学习周期: {days}天")
            print(f"   每日时间: {minutes}分钟")
            print(f"🔧 使用统一AI客户端调用")
            
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    print(f"🔄 第 {attempt + 1} 次尝试调用AI模型...")
                    
                    # 使用非流式输出生成学习计划模板
                    response = self.ai_client.generate_content(
                        prompt=prompt,
                        temperature=0.7,
                        max_tokens=5000,  # FSRS模板JSON响应约1400字符，3000 tokens提供充足缓冲
                        model=AIModel.GLM_45,
                        timeout=120.0  # 设置2分钟超时
                    )
                    
                    response_time = time.time() - start_time
                    
                    # 检查是否成功且有内容
                    if response.success and response.content and response.content.strip():
                        print(f"✅ AI生成成功! (第 {attempt + 1} 次尝试)")
                        print(f"✅ AI生成成功!")
                        print(f"   模型: {response.model}")
                        print(f"   响应时间: {response_time:.2f}秒")
                        print(f"   使用情况: {response.usage}")
                        print(f"   完成原因: {response.finish_reason}")
                        
                        print(f"\n📋 AI生成的FSRS学习计划模板:")
                        print("=" * 80)
                        print(response.content[:1000] + "..." if len(response.content) > 1000 else response.content)
                        print("=" * 80)
                
                        # 尝试解析AI返回的JSON
                        try:
                            import json
                            # 使用健壮的JSON提取方法
                            json_content = self._extract_json_from_content(response.content)
                            if json_content:
                                template = json.loads(json_content)
                            else:
                                # 如果提取失败，尝试直接解析
                                template = json.loads(response.content)
                            print(f"✅ 成功解析AI返回的FSRS学习计划模板JSON")
                            
                            # 保存学习计划模板
                            template_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                            output_file = Path("outputs/english/plans/fsrs_templates") / f"fsrs_template_{template_id}.json"
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            # 构建完整的学习计划模板数据
                            full_template = {
                                "id": template_id,
                                "type": "fsrs_learning_template",
                                "metadata": {
                                    "stage": stage,
                                    "days": days,
                                    "minutes_per_day": minutes,
                                    "ai_model": response.model,
                                    "generated_at": datetime.now().isoformat(),
                                    "ai_response_time": response_time,
                                    "ai_usage": response.usage,
                                    "retry_count": attempt + 1
                                },
                                "fsrs_template": template
                            }
                            
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(full_template, f, ensure_ascii=False, indent=2)
                            
                            print(f"💾 FSRS学习计划模板已保存到: {output_file}")
                            print(f"📋 模板ID: {template_id}")
                            
                            # 显示模板摘要
                            if "metadata" in template:
                                metadata = template["metadata"]
                                print(f"📋 总学习天数: {metadata.get('total_study_days', '未知')}天")
                                print(f"📋 每日目标时间: {metadata.get('daily_learning_minutes_target', '未知')}分钟")
                                print(f"📋 词库总数: {metadata.get('total_words_in_library', '未知')}个")
                                print(f"📋 预计轮转次数: {metadata.get('estimated_avg_word_rotations_per_cycle', '未知')}")
                            
                            if "daily_planning_guidelines" in template:
                                guidelines = template["daily_planning_guidelines"]
                                print(f"📋 平均每日新词: {guidelines.get('avg_new_words_per_day', '未知')}个")
                                print(f"📋 平均每日复习: {guidelines.get('avg_review_words_per_day', '未知')}个")
                                print(f"📋 平均每日新词法: {guidelines.get('avg_new_morphology_units_per_day', '未知')}个")
                                print(f"📋 平均每日复习词法: {guidelines.get('avg_review_morphology_units_per_day', '未知')}个")
                                print(f"📋 平均每日新句法: {guidelines.get('avg_new_syntax_units_per_day', '未知')}个")
                                print(f"📋 平均每日复习句法: {guidelines.get('avg_review_syntax_units_per_day', '未知')}个")
                            
                            print(f"\n📄 完整FSRS学习计划模板内容（带字段注解）:")
                            print("=" * 100)
                            self.print_fsrs_template_with_annotations(full_template)
                            print("=" * 100)
                            
                            # 转换为FSRS标准格式并保存
                            fsrs_standard = self.convert_to_fsrs_standard_format(full_template)
                            if "error" not in fsrs_standard:
                                # 保存FSRS标准格式文件
                                fsrs_output_file = Path("outputs/english/plans/fsrs_standard") / f"fsrs_standard_{template_id}.json"
                                with open(fsrs_output_file, 'w', encoding='utf-8') as f:
                                    json.dump(fsrs_standard, f, ensure_ascii=False, indent=2)
                                print(f"💾 FSRS标准格式已保存到: {fsrs_output_file}")
                                
                                # 在返回的数据中添加FSRS标准格式
                                full_template["fsrs_standard_format"] = fsrs_standard
                            
                            return full_template
                            
                        except json.JSONDecodeError as e:
                            print(f"❌ 解析AI返回的JSON失败: {e}")
                            print(f"🔍 原始内容: {response.content[:500]}...")
                            
                            # 保存失败的响应用于调试
                            template_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                            output_file = Path("outputs/english/plans/fsrs_templates") / f"fsrs_template_error_{template_id}.json"
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            full_template = {
                                "id": template_id,
                                "type": "fsrs_learning_template",
                                "metadata": {
                                    "stage": stage,
                                    "days": days,
                                    "minutes_per_day": minutes,
                                    "ai_model": response.model,
                                    "generated_at": datetime.now().isoformat(),
                                    "ai_response_time": response_time,
                                    "ai_usage": response.usage,
                                    "parse_error": str(e)
                                },
                                "fsrs_template": None,
                                "raw_content": response.content
                            }
                            
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(full_template, f, ensure_ascii=False, indent=2)
                            
                            print(f"💾 失败的响应已保存到: {output_file}")
                            
                            # 如果这不是最后一次尝试，继续重试
                            if attempt < max_retries - 1:
                                print(f"🔄 将进行第 {attempt + 2} 次尝试...")
                                continue
                            else:
                                return full_template
                    else:
                        print(f"❌ AI生成失败 (第 {attempt + 1} 次尝试)")
                        print(f"   成功状态: {response.success}")
                        print(f"   内容长度: {len(response.content) if response.content else 0}")
                        print(f"   错误信息: {response.error_message}")
                        
                        if attempt < max_retries - 1:
                            print(f"🔄 将进行第 {attempt + 2} 次尝试...")
                            continue
                        else:
                            # 最后一次尝试失败，返回错误信息
                            return {
                                "error": "AI生成失败",
                                "details": {
                                    "success": response.success,
                                    "error_message": response.error_message,
                                    "attempts": max_retries
                                }
                            }
                            
                except Exception as e:
                    print(f"❌ 调用AI模型时发生异常 (第 {attempt + 1} 次尝试): {e}")
                    if attempt < max_retries - 1:
                        print(f"🔄 等待 2 秒后重试...")
                        time.sleep(2)
                        continue
                    else:
                        # 异常处理的最后一次尝试失败
                        return {
                            "error": "AI调用异常",
                            "details": {
                                "exception": str(e),
                                "attempts": max_retries
                            }
                        }
            
            # 所有尝试都失败
            return {
                "error": "AI生成失败",
                "details": {
                    "attempts": max_retries
                }
            }
                
        except Exception as e:
            print(f"❌ 生成学习计划模板时发生异常: {e}")
            return {
                "error": "生成学习计划模板异常",
                "details": {
                    "exception": str(e)
                }
            }

    def run_interactive(self):
        """运行交互式FSRS模板生成"""
        try:
            print("🎓 FSRS模板生成器")
            print("=" * 50)
            
            print("\n📚 FSRS算法适配学习计划模板生成")
            print("正在启动FSRS模板生成功能...")
            
            print("\n🎯 FSRS算法适配学习计划模板生成")
            print("-" * 30)
            
            # 选择学习阶段
            print("\n📚 请选择学习阶段:")
            stage_options = self.prompt_generator.get_stage_options()
            
            for i, stage in enumerate(stage_options, 1):
                stage_name = stage.replace('### ', '').strip()
                print(f"{i}. {stage_name}")
            
            while True:
                try:
                    stage_choice = input(f"\n请输入选择 (1-{len(stage_options)}): ").strip()
                    if stage_choice.isdigit():
                        stage_index = int(stage_choice) - 1
                        if 0 <= stage_index < len(stage_options):
                            selected_stage = stage_options[stage_index]
                            break
                    print(f"❌ 请输入1到{len(stage_options)}之间的数字")
                except (ValueError, KeyboardInterrupt):
                    print("❌ 输入无效，请重新输入")
                    continue
            
            # 输入学习周期
            while True:
                try:
                    days = int(input("📅 请输入学习周期（天数）: ").strip())
                    if days > 0:
                        break
                    else:
                        print("❌ 学习周期必须大于0")
                except (ValueError, KeyboardInterrupt):
                    print("❌ 请输入有效的数字")
                    continue
            
            # 输入每日学习时间
            while True:
                try:
                    minutes = int(input("⏰ 请输入每日学习时间（分钟）: ").strip())
                    if minutes > 0:
                        break
                    else:
                        print("❌ 学习时间必须大于0")
                except (ValueError, KeyboardInterrupt):
                    print("❌ 请输入有效的数字")
                    continue
                    
                # 询问是否自定义效率参数
            print("\n🔧 效率参数设置:")
            print("是否使用默认效率参数？")
            print("📊 默认值: 学习效率1.0分钟/词, 复习效率0.6分钟/词, 词法练习4分钟/次, 句法练习8分钟/次")
            
            use_default = input("使用默认值？(y/n，默认y): ").strip().lower()
            
            if use_default in ['n', 'no', '否']:
                # 自定义效率参数
                try:
                    learning_efficiency = input("\n📚 请输入学习新词效率（分钟/词，默认1.0）: ").strip()
                    learning_efficiency = 1.0 if learning_efficiency == "" else float(learning_efficiency)
                    
                    review_efficiency = input("🔄 请输入复习词汇效率（分钟/词，默认0.6）: ").strip()
                    review_efficiency = 0.6 if review_efficiency == "" else float(review_efficiency)
                    
                    morphology_time = input("📝 请输入词法练习时间（分钟/次，默认4）: ").strip()
                    morphology_time = 4 if morphology_time == "" else int(morphology_time)
                    
                    syntax_time = input("📖 请输入句法练习时间（分钟/次，默认8）: ").strip()
                    syntax_time = 8 if syntax_time == "" else int(syntax_time)
                    
                except (ValueError, KeyboardInterrupt, Exception) as e:
                    print(f"❌ 输入错误，使用默认值: {e}")
                    learning_efficiency, review_efficiency, morphology_time, syntax_time = 1.0, 0.6, 4, 8
            else:
                # 使用默认值
                learning_efficiency, review_efficiency, morphology_time, syntax_time = 1.0, 0.6, 4, 8
                
            # 生成FSRS学习计划模板
            fsrs_template = self.generate_fsrs_template(
                selected_stage, days, minutes, 
                learning_efficiency, review_efficiency, morphology_time, syntax_time
            )
            
            if "error" not in fsrs_template:
                print("\n🎉 FSRS学习计划模板生成完成!")
            else:
                print(f"\n❌ FSRS学习计划模板生成失败: {fsrs_template['error']}")
                
        except KeyboardInterrupt:
            print("\n\n❌ 用户中断操作")
        except Exception as e:
            print(f"\n❌ 程序运行错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    generator = FSRSTemplateGenerator()
    generator.run_interactive()


if __name__ == "__main__":
    main()

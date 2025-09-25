#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI练习题生成器
根据词汇特性和学习进度，智能生成填空、翻译、选择题等练习
"""

import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from zhipu_ai_client import ai_client
from content_generation_config import config_manager, GenerationMode

class ExerciseType(Enum):
    """练习题类型"""
    FILL_BLANK = "fill_blank"
    TRANSLATION = "translation"
    MULTIPLE_CHOICE = "multiple_choice"
    SENTENCE_COMPLETION = "sentence_completion"
    GRAMMAR_CORRECTION = "grammar_correction"

@dataclass
class WordInfo:
    """单词信息"""
    word: str
    chinese_meaning: str
    part_of_speech: str
    difficulty: str
    grade_level: str
    category: str

@dataclass
class Exercise:
    """练习题结构"""
    question: str
    options: List[str] = None  # 选择题选项
    answer: str = ""
    explanation: str = ""
    hint: str = ""
    exercise_type: ExerciseType = ExerciseType.FILL_BLANK
    difficulty: str = "medium"
    grammar_focus: str = ""
    is_ai_generated: bool = False
    quality_score: float = 0.0

class SmartExerciseGenerator:
    """智能练习题生成器"""
    
    def __init__(self):
        self.ai_client = ai_client
        self.config_manager = config_manager
        
        # 基础模板（保守模式使用）
        self.exercise_templates = {
            ExerciseType.FILL_BLANK: {
                "noun": [
                    {
                        "question": "I have a _____ in my bag.",
                        "answer": "{word}",
                        "hint": "名词填空",
                        "chinese": "我的包里有一个_____。"
                    },
                    {
                        "question": "This is a beautiful _____.",
                        "answer": "{word}",
                        "hint": "名词填空",
                        "chinese": "这是一个漂亮的_____。"
                    }
                ],
                "verb": [
                    {
                        "question": "I _____ to school every day.",
                        "answer": "{word}",
                        "hint": "动词填空",
                        "chinese": "我每天_____去学校。"
                    },
                    {
                        "question": "She _____ her homework carefully.",
                        "answer": "{word}s",
                        "hint": "动词第三人称单数",
                        "chinese": "她认真地_____作业。"
                    }
                ],
                "adjective": [
                    {
                        "question": "The weather is very _____ today.",
                        "answer": "{word}",
                        "hint": "形容词填空",
                        "chinese": "今天天气很_____。"
                    },
                    {
                        "question": "I feel _____ about this news.",
                        "answer": "{word}",
                        "hint": "形容词填空",
                        "chinese": "对于这个消息我感到_____。"
                    }
                ]
            },
            ExerciseType.TRANSLATION: {
                "general": [
                    {
                        "question": "翻译下列句子：I like {word} very much.",
                        "answer": "我非常喜欢{chinese}。",
                        "hint": "注意{word}的含义",
                        "chinese": ""
                    }
                ]
            },
            ExerciseType.MULTIPLE_CHOICE: {
                "general": [
                    {
                        "question": "Choose the correct word: I want to _____ an apple.",
                        "options": ["{word}", "wrong1", "wrong2", "wrong3"],
                        "answer": "{word}",
                        "hint": "选择正确的词汇",
                        "chinese": "我想要_____一个苹果。"
                    }
                ]
            }
        }
        
        # 语法主题对应的练习重点
        self.grammar_exercise_focus = {
            "一般现在时": ["verb_conjugation", "third_person_singular", "question_formation"],
            "现在进行时": ["be_verb", "ing_form", "time_expressions"],
            "过去时": ["past_tense", "irregular_verbs", "time_markers"],
            "名词单复数": ["plural_rules", "countable_uncountable", "articles"],
            "形容词比较级": ["comparative_form", "superlative_form", "comparison_structure"],
            "被动语态": ["passive_structure", "by_agent", "tense_transformation"]
        }
    
    def generate_exercise(self, word_info: WordInfo, grammar_topic: str,
                         exercise_type: ExerciseType = ExerciseType.FILL_BLANK,
                         mode: str = None) -> Exercise:
        """
        生成智能练习题
        
        Args:
            word_info: 单词信息
            grammar_topic: 语法主题
            exercise_type: 练习类型
            mode: 生成模式
        """
        # 获取配置
        if mode:
            self.config_manager.set_mode(mode)
        
        config = self.config_manager.get_config("exercises")
        
        # 根据模式选择生成策略
        if config.mode == GenerationMode.CONSERVATIVE:
            return self._generate_template_exercise(word_info, grammar_topic, exercise_type)
        elif config.mode == GenerationMode.BALANCED:
            return self._generate_balanced_exercise(word_info, grammar_topic, exercise_type, config)
        else:  # INNOVATIVE
            return self._generate_ai_exercise(word_info, grammar_topic, exercise_type, config)
    
    def _generate_template_exercise(self, word_info: WordInfo, grammar_topic: str,
                                  exercise_type: ExerciseType) -> Exercise:
        """生成模板练习题"""
        templates = self.exercise_templates.get(exercise_type, {})
        pos_templates = templates.get(word_info.part_of_speech, templates.get("general", []))
        
        if not pos_templates:
            # 创建默认练习
            if exercise_type == ExerciseType.FILL_BLANK:
                question = f"Fill in the blank with the correct word: I _____ every day."
                answer = word_info.word
                hint = f"Use the word '{word_info.word}'"
            elif exercise_type == ExerciseType.TRANSLATION:
                question = f"Translate: I like {word_info.word}."
                answer = f"我喜欢{word_info.chinese_meaning}。"
                hint = "Direct translation"
            else:
                question = f"Complete the sentence with '{word_info.word}'"
                answer = word_info.word
                hint = "Use the given word"
            
            explanation = f"This exercise practices using '{word_info.word}' ({word_info.chinese_meaning})"
        else:
            template = random.choice(pos_templates)
            question = template["question"].replace("{word}", word_info.word)
            answer = template["answer"].format(word=word_info.word, chinese=word_info.chinese_meaning)
            hint = template["hint"]
            explanation = f"Practice using '{word_info.word}' in context"
            
            # 处理选择题选项
            options = None
            if exercise_type == ExerciseType.MULTIPLE_CHOICE and "options" in template:
                options = [opt.format(word=word_info.word) if opt == "{word}" else opt 
                          for opt in template["options"]]
        
        return Exercise(
            question=question,
            options=options,
            answer=answer,
            explanation=explanation,
            hint=hint,
            exercise_type=exercise_type,
            difficulty=word_info.difficulty,
            grammar_focus=grammar_topic,
            is_ai_generated=False,
            quality_score=0.7
        )
    
    def _generate_balanced_exercise(self, word_info: WordInfo, grammar_topic: str,
                                  exercise_type: ExerciseType, config) -> Exercise:
        """生成平衡模式练习题（模板+AI优化）"""
        # 决定是否使用AI生成
        should_use_ai = random.random() < config.ai_enhancement_ratio
        
        if should_use_ai:
            try:
                ai_exercise = self._generate_ai_exercise(word_info, grammar_topic, exercise_type, config)
                # 如果AI生成质量高，使用AI结果
                if ai_exercise.quality_score > config.quality_threshold:
                    return ai_exercise
            except Exception as e:
                print(f"AI生成失败，使用模板: {e}")
        
        # 使用模板或AI质量不够时的后备
        return self._generate_template_exercise(word_info, grammar_topic, exercise_type)
    
    def _generate_ai_exercise(self, word_info: WordInfo, grammar_topic: str,
                            exercise_type: ExerciseType, config) -> Exercise:
        """生成AI练习题"""
        
        # 获取语法重点
        grammar_focuses = self.grammar_exercise_focus.get(grammar_topic, ["general_usage"])
        focus = random.choice(grammar_focuses)
        
        # 构建AI提示
        system_prompt = """你是一个专业的英语教育专家，擅长设计高质量的练习题。
你的任务是根据给定的条件创建符合以下要求的练习题：
1. 题目要突出指定的语法主题
2. 包含目标单词并体现其用法
3. 适合指定的年级水平
4. 答案准确，解释清晰
5. 具有一定的挑战性但不超出学生能力"""
        
        exercise_type_cn = {
            ExerciseType.FILL_BLANK: "填空题",
            ExerciseType.TRANSLATION: "翻译题", 
            ExerciseType.MULTIPLE_CHOICE: "选择题",
            ExerciseType.SENTENCE_COMPLETION: "句子完成题",
            ExerciseType.GRAMMAR_CORRECTION: "语法改错题"
        }
        
        prompt = f"""请为以下条件设计一道高质量的英语练习题：

目标单词：{word_info.word} ({word_info.chinese_meaning})
词性：{word_info.part_of_speech}
语法主题：{grammar_topic}
语法重点：{focus}
练习类型：{exercise_type_cn[exercise_type]}
难度级别：{word_info.difficulty}
年级水平：{word_info.grade_level}

设计要求：
1. 题目必须突出{grammar_topic}的语法特点
2. 单词{word_info.word}必须在题目中自然出现
3. 符合{word_info.grade_level}学生的水平
4. 避免过于简单或过于复杂的表达
5. 提供准确的答案和清晰的解释

请按以下格式返回：
题目：[练习题题目]
"""
        
        # 根据练习类型添加特定要求
        if exercise_type == ExerciseType.MULTIPLE_CHOICE:
            prompt += """选项A：[选项A]
选项B：[选项B]  
选项C：[选项C]
选项D：[选项D]
"""
        
        prompt += """答案：[正确答案]
解释：[答案解释，说明为什么这是正确答案]
提示：[给学生的提示，不要直接给出答案]"""
        
        try:
            response = self.ai_client.generate_content(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            if response.success:
                # 解析AI响应
                exercise_data = self._parse_ai_exercise_response(response.content, exercise_type)
                
                # 评估质量
                quality_score = self._evaluate_exercise_quality(exercise_data, word_info, grammar_topic)
                
                return Exercise(
                    question=exercise_data["question"],
                    options=exercise_data.get("options"),
                    answer=exercise_data["answer"],
                    explanation=exercise_data["explanation"],
                    hint=exercise_data["hint"],
                    exercise_type=exercise_type,
                    difficulty=word_info.difficulty,
                    grammar_focus=grammar_topic,
                    is_ai_generated=True,
                    quality_score=quality_score
                )
            else:
                raise Exception(f"AI生成失败: {response.error_message}")
                
        except Exception as e:
            print(f"AI练习题生成异常: {e}")
            if config.fallback_to_template:
                return self._generate_template_exercise(word_info, grammar_topic, exercise_type)
            else:
                raise e
    
    def _parse_ai_exercise_response(self, content: str, exercise_type: ExerciseType) -> Dict[str, Any]:
        """解析AI练习题响应"""
        lines = content.strip().split('\n')
        result = {
            "question": "",
            "answer": "",
            "explanation": "",
            "hint": "",
            "options": None
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('题目：'):
                result["question"] = line.split('：', 1)[1].strip()
                current_section = "question"
            elif line.startswith('答案：'):
                result["answer"] = line.split('：', 1)[1].strip()
                current_section = "answer"
            elif line.startswith('解释：'):
                result["explanation"] = line.split('：', 1)[1].strip()
                current_section = "explanation"
            elif line.startswith('提示：'):
                result["hint"] = line.split('：', 1)[1].strip()
                current_section = "hint"
            elif exercise_type == ExerciseType.MULTIPLE_CHOICE:
                if line.startswith('选项A：') or line.startswith('A：'):
                    if result["options"] is None:
                        result["options"] = []
                    result["options"].append(line.split('：', 1)[1].strip())
                elif line.startswith('选项B：') or line.startswith('B：'):
                    result["options"].append(line.split('：', 1)[1].strip())
                elif line.startswith('选项C：') or line.startswith('C：'):
                    result["options"].append(line.split('：', 1)[1].strip())
                elif line.startswith('选项D：') or line.startswith('D：'):
                    result["options"].append(line.split('：', 1)[1].strip())
            elif current_section and not any(line.startswith(prefix) for prefix in ['题目：', '答案：', '解释：', '提示：', '选项']):
                # 继续当前部分的内容
                if current_section == "question" and result["question"]:
                    result["question"] += " " + line
                elif current_section == "explanation" and result["explanation"]:
                    result["explanation"] += " " + line
        
        # 设置默认值
        if not result["question"]:
            result["question"] = "请完成练习。"
        if not result["answer"]:
            result["answer"] = "答案"
        if not result["explanation"]:
            result["explanation"] = "这道题练习指定的语法点。"
        if not result["hint"]:
            result["hint"] = "仔细思考语法规则。"
        
        return result
    
    def _evaluate_exercise_quality(self, exercise_data: Dict[str, Any], 
                                 word_info: WordInfo, grammar_topic: str) -> float:
        """评估练习题质量"""
        score = 0.0
        
        question = exercise_data.get("question", "")
        answer = exercise_data.get("answer", "")
        
        # 基础检查
        if not question or len(question) < 10:
            return 0.0
        
        # 检查是否包含目标单词
        if word_info.word.lower() in question.lower():
            score += 0.3
        
        # 检查答案非空
        if answer and len(answer) > 0:
            score += 0.2
        
        # 检查题目合理长度
        if 10 <= len(question) <= 200:
            score += 0.2
        
        # 检查是否有解释
        if exercise_data.get("explanation") and len(exercise_data["explanation"]) > 10:
            score += 0.1
        
        # 检查是否有提示
        if exercise_data.get("hint") and len(exercise_data["hint"]) > 5:
            score += 0.1
        
        # 检查语法相关性（简单关键词匹配）
        if any(keyword in question.lower() for keyword in grammar_topic.lower().split()):
            score += 0.1
        
        return min(score, 1.0)
    
    def generate_exercise_set(self, word_info: WordInfo, grammar_topic: str,
                            exercise_types: List[ExerciseType] = None,
                            count_per_type: int = 2) -> List[Exercise]:
        """生成练习题集合"""
        if exercise_types is None:
            exercise_types = [ExerciseType.FILL_BLANK, ExerciseType.TRANSLATION, 
                            ExerciseType.MULTIPLE_CHOICE]
        
        exercises = []
        
        for exercise_type in exercise_types:
            for i in range(count_per_type):
                try:
                    exercise = self.generate_exercise(word_info, grammar_topic, exercise_type)
                    exercises.append(exercise)
                except Exception as e:
                    print(f"生成练习题失败 {exercise_type}: {e}")
                    # 使用模板作为备选
                    template_exercise = self._generate_template_exercise(
                        word_info, grammar_topic, exercise_type
                    )
                    exercises.append(template_exercise)
        
        return exercises
    
    def generate_adaptive_exercise(self, word_info: WordInfo, grammar_topic: str,
                                 user_performance: Dict[str, float] = None) -> Exercise:
        """生成自适应练习题（根据用户表现调整难度）"""
        # 根据用户表现选择合适的练习类型
        if user_performance:
            accuracy = user_performance.get("accuracy", 0.5)
            
            if accuracy < 0.3:
                # 表现较差，使用简单的填空题
                exercise_type = ExerciseType.FILL_BLANK
                self.config_manager.set_mode("conservative")
            elif accuracy < 0.7:
                # 表现中等，使用平衡模式
                exercise_type = random.choice([ExerciseType.FILL_BLANK, ExerciseType.TRANSLATION])
                self.config_manager.set_mode("balanced")
            else:
                # 表现良好，使用更有挑战性的题型
                exercise_type = random.choice([
                    ExerciseType.MULTIPLE_CHOICE, 
                    ExerciseType.SENTENCE_COMPLETION,
                    ExerciseType.GRAMMAR_CORRECTION
                ])
                self.config_manager.set_mode("innovative")
        else:
            # 默认使用平衡模式
            exercise_type = ExerciseType.FILL_BLANK
            self.config_manager.set_mode("balanced")
        
        return self.generate_exercise(word_info, grammar_topic, exercise_type)
    
    def get_exercise_statistics(self) -> Dict[str, Any]:
        """获取练习题生成统计"""
        current_mode = self.config_manager.get_current_mode()
        config = self.config_manager.get_config("exercises")
        
        return {
            "current_mode": current_mode,
            "supported_types": [t.value for t in ExerciseType],
            "template_coverage": len(self.exercise_templates),
            "grammar_topics": list(self.grammar_exercise_focus.keys()),
            "config": {
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "ai_enhancement_ratio": config.ai_enhancement_ratio,
                "quality_threshold": config.quality_threshold
            }
        }

# 全局实例
exercise_generator = SmartExerciseGenerator()

if __name__ == "__main__":
    # 测试AI练习题生成器
    print("=== AI练习题生成器测试 ===")
    
    # 测试单词
    test_word = WordInfo(
        word="study",
        chinese_meaning="学习",
        part_of_speech="verb",
        difficulty="medium",
        grade_level="elementary_5_6",
        category="education"
    )
    
    # 测试不同类型的练习题
    exercise_types = [ExerciseType.FILL_BLANK, ExerciseType.TRANSLATION, ExerciseType.MULTIPLE_CHOICE]
    
    for ex_type in exercise_types:
        print(f"\n--- {ex_type.value.upper()} 测试 ---")
        
        exercise = exercise_generator.generate_exercise(
            test_word,
            "一般现在时",
            ex_type,
            mode="balanced"
        )
        
        print(f"题目: {exercise.question}")
        if exercise.options:
            for i, option in enumerate(exercise.options, 1):
                print(f"  {chr(64+i)}. {option}")
        print(f"答案: {exercise.answer}")
        print(f"解释: {exercise.explanation}")
        print(f"提示: {exercise.hint}")
        print(f"AI生成: {exercise.is_ai_generated}")
        print(f"质量评分: {exercise.quality_score}")
    
    # 生成练习题集合
    print(f"\n--- 练习题集合测试 ---")
    exercise_set = exercise_generator.generate_exercise_set(
        test_word, 
        "一般现在时",
        count_per_type=1
    )
    
    print(f"共生成 {len(exercise_set)} 道练习题")
    
    # 统计信息
    print(f"\n--- 生成器统计 ---")
    stats = exercise_generator.get_exercise_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

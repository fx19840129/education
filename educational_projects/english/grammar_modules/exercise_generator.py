#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的练习题生成器
支持多样化的练习题生成，增加随机性和实用性
"""

import random
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ExerciseTemplate:
    """练习题模板"""
    question: str
    correct_answer: str
    wrong_options: List[str]
    explanation: str
    difficulty: str = "medium"


class ImprovedExerciseGenerator:
    """改进的练习题生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.exercise_types = [
            "multiple_choice", "fill_in_blank", "error_correction", 
            "sentence_creation", "transformation", "classification",
            "matching", "true_false", "completion", "translation"
        ]
        
    def generate_exercises(self, grammar_config: Dict[str, Any], 
                          num_exercises: int = 30, 
                          difficulty_level: str = "medium") -> List[Dict[str, Any]]:
        """
        生成练习题
        
        Args:
            grammar_config: 语法配置
            num_exercises: 练习题数量
            difficulty_level: 难度级别
            
        Returns:
            练习题列表
        """
        exercises = []
        grammar_name = grammar_config.get("grammar_name", "")
        exercise_templates = grammar_config.get("exercise_templates", {})
        
        # 使用时间戳和语法名称的组合作为随机种子，增加随机性
        random.seed(int(time.time()) + hash(grammar_name))
        
        # 根据难度级别调整练习题类型分布
        type_distribution = self._get_type_distribution(difficulty_level)
        
        for i in range(num_exercises):
            # 根据分布选择练习题型
            exercise_type = self._select_exercise_type(type_distribution)
            
            # 生成对应类型的练习题
            exercise = self._generate_single_exercise(
                grammar_config, exercise_type, i + 1, difficulty_level
            )
            
            if exercise:
                exercises.append(exercise)
        
        return exercises
    
    def _get_type_distribution(self, difficulty_level: str) -> Dict[str, float]:
        """根据难度级别获取题型分布"""
        distributions = {
            "easy": {
                "multiple_choice": 0.4,
                "fill_in_blank": 0.3,
                "true_false": 0.2,
                "matching": 0.1
            },
            "medium": {
                "multiple_choice": 0.3,
                "fill_in_blank": 0.25,
                "error_correction": 0.2,
                "transformation": 0.15,
                "sentence_creation": 0.1
            },
            "hard": {
                "error_correction": 0.3,
                "transformation": 0.25,
                "sentence_creation": 0.2,
                "completion": 0.15,
                "translation": 0.1
            }
        }
        
        return distributions.get(difficulty_level, distributions["medium"])
    
    def _select_exercise_type(self, distribution: Dict[str, float]) -> str:
        """根据分布选择练习题型"""
        rand = random.random()
        cumulative = 0
        
        for exercise_type, probability in distribution.items():
            cumulative += probability
            if rand <= cumulative:
                return exercise_type
        
        return "multiple_choice"  # 默认返回选择题
    
    def _generate_single_exercise(self, grammar_config: Dict[str, Any], 
                                 exercise_type: str, question_num: int, 
                                 difficulty_level: str) -> Optional[Dict[str, Any]]:
        """生成单个练习题"""
        
        if exercise_type == "multiple_choice":
            return self._generate_multiple_choice(grammar_config, question_num)
        elif exercise_type == "fill_in_blank":
            return self._generate_fill_in_blank(grammar_config, question_num)
        elif exercise_type == "error_correction":
            return self._generate_error_correction(grammar_config, question_num)
        elif exercise_type == "sentence_creation":
            return self._generate_sentence_creation(grammar_config, question_num)
        elif exercise_type == "transformation":
            return self._generate_transformation(grammar_config, question_num)
        elif exercise_type == "classification":
            return self._generate_classification(grammar_config, question_num)
        elif exercise_type == "matching":
            return self._generate_matching(grammar_config, question_num)
        elif exercise_type == "true_false":
            return self._generate_true_false(grammar_config, question_num)
        elif exercise_type == "completion":
            return self._generate_completion(grammar_config, question_num)
        elif exercise_type == "translation":
            return self._generate_translation(grammar_config, question_num)
        else:
            return self._generate_general_exercise(grammar_config, question_num)
    
    def _generate_multiple_choice(self, grammar_config: Dict[str, Any], 
                                 question_num: int) -> Dict[str, Any]:
        """生成选择题"""
        templates = grammar_config.get("exercise_templates", {}).get("multiple_choice", {}).get("templates", [])
        
        if not templates:
            return self._create_default_multiple_choice(grammar_config, question_num)
        
        # 随机选择一个模板
        template = random.choice(templates)
        
        # 随机打乱选项
        all_options = [template["correct"]] + template["wrong_options"]
        random.shuffle(all_options)
        
        return {
            "type": "选择题",
            "question": template["question"],
            "options": [f"{chr(65+i)}. {opt}" for i, opt in enumerate(all_options)],
            "answer": f"{chr(65+all_options.index(template['correct']))}",
            "explanation": template["explanation"],
            "difficulty": "easy"
        }
    
    def _generate_fill_in_blank(self, grammar_config: Dict[str, Any], 
                               question_num: int) -> Dict[str, Any]:
        """生成填空题"""
        templates = grammar_config.get("exercise_templates", {}).get("fill_in_blank", {}).get("templates", [])
        
        if not templates:
            return self._create_default_fill_in_blank(grammar_config, question_num)
        
        template = random.choice(templates)
        
        return {
            "type": "填空题",
            "question": template["question"],
            "options": [],
            "answer": template["answer"],
            "explanation": template["explanation"],
            "difficulty": "easy"
        }
    
    def _generate_error_correction(self, grammar_config: Dict[str, Any], 
                                  question_num: int) -> Dict[str, Any]:
        """生成改错题"""
        templates = grammar_config.get("exercise_templates", {}).get("error_correction", {}).get("templates", [])
        
        if not templates:
            return self._create_default_error_correction(grammar_config, question_num)
        
        template = random.choice(templates)
        
        return {
            "type": "改错题",
            "question": f"找出并改正下列句子中的错误：{template['sentence']}",
            "options": [],
            "answer": f"错误：{template['error']} → 正确：{template['correction']}",
            "explanation": template["explanation"],
            "difficulty": "medium"
        }
    
    def _generate_sentence_creation(self, grammar_config: Dict[str, Any], 
                                   question_num: int) -> Dict[str, Any]:
        """生成造句题"""
        templates = grammar_config.get("exercise_templates", {}).get("sentence_creation", {}).get("templates", [])
        
        if not templates:
            return self._create_default_sentence_creation(grammar_config, question_num)
        
        template = random.choice(templates)
        
        return {
            "type": "造句题",
            "question": template["requirement"],
            "options": [],
            "answer": template["example"],
            "explanation": template["explanation"],
            "difficulty": "medium"
        }
    
    def _generate_transformation(self, grammar_config: Dict[str, Any], 
                               question_num: int) -> Dict[str, Any]:
        """生成转换题"""
        templates = grammar_config.get("exercise_templates", {}).get("tense_transformation", {}).get("templates", [])
        
        if not templates:
            return self._create_default_transformation(grammar_config, question_num)
        
        template = random.choice(templates)
        
        return {
            "type": "转换题",
            "question": f"按要求转换句子：{template['original']}",
            "options": [],
            "answer": template["transformed"],
            "explanation": template["explanation"],
            "difficulty": "hard"
        }
    
    def _generate_classification(self, grammar_config: Dict[str, Any], 
                               question_num: int) -> Dict[str, Any]:
        """生成分类题"""
        templates = grammar_config.get("exercise_templates", {}).get("classification", {}).get("templates", [])
        
        if not templates:
            return self._create_default_classification(grammar_config, question_num)
        
        template = random.choice(templates)
        
        return {
            "type": "分类题",
            "question": template["question"],
            "options": [],
            "answer": template["answer"],
            "explanation": template["explanation"],
            "difficulty": "medium"
        }
    
    def _generate_matching(self, grammar_config: Dict[str, Any], 
                          question_num: int) -> Dict[str, Any]:
        """生成匹配题"""
        examples = grammar_config.get("examples", {})
        
        # 创建匹配题：将例句与语法点匹配
        if "basic" in examples and len(examples["basic"]) >= 4:
            items = random.sample(examples["basic"], 4)
            question = "将下列句子与正确的语法点匹配："
            
            return {
                "type": "匹配题",
                "question": question,
                "options": [f"{i+1}. {item}" for i, item in enumerate(items)],
                "answer": f"1-{grammar_config.get('grammar_name', '语法点')}",
                "explanation": "所有句子都体现了该语法点的用法",
                "difficulty": "easy"
            }
        
        return self._create_default_matching(grammar_config, question_num)
    
    def _generate_true_false(self, grammar_config: Dict[str, Any], 
                            question_num: int) -> Dict[str, Any]:
        """生成判断题"""
        grammar_name = grammar_config.get("grammar_name", "")
        explanation = grammar_config.get("explanation", {})
        
        # 创建判断题
        if "basic_rules" in explanation:
            rule = random.choice(explanation["basic_rules"])
            is_true = random.choice([True, False])
            
            if is_true:
                statement = f"在{grammar_name}中，{rule}"
                answer = "正确"
            else:
                statement = f"在{grammar_name}中，{rule}（错误表述）"
                answer = "错误"
            
            return {
                "type": "判断题",
                "question": f"判断下列说法是否正确：{statement}",
                "options": ["正确", "错误"],
                "answer": answer,
                "explanation": f"这是{grammar_name}的基本规则" if is_true else "这个表述是错误的",
                "difficulty": "easy"
            }
        
        return self._create_default_true_false(grammar_config, question_num)
    
    def _generate_completion(self, grammar_config: Dict[str, Any], 
                            question_num: int) -> Dict[str, Any]:
        """生成补全题"""
        examples = grammar_config.get("examples", {})
        
        if "basic" in examples and len(examples["basic"]) >= 3:
            sentence = random.choice(examples["basic"])
            # 随机选择一个词进行挖空
            words = sentence.split()
            if len(words) > 2:
                blank_word = random.choice(words[1:-1])  # 不选择第一个和最后一个词
                question = sentence.replace(blank_word, "_____")
                
                return {
                    "type": "补全题",
                    "question": f"补全句子：{question}",
                    "options": [],
                    "answer": blank_word,
                    "explanation": f"这是{grammar_config.get('grammar_name', '语法点')}的典型用法",
                    "difficulty": "medium"
                }
        
        return self._create_default_completion(grammar_config, question_num)
    
    def _generate_translation(self, grammar_config: Dict[str, Any], 
                             question_num: int) -> Dict[str, Any]:
        """生成翻译题"""
        examples = grammar_config.get("examples", {})
        
        if "basic" in examples and len(examples["basic"]) >= 3:
            sentence = random.choice(examples["basic"])
            
            return {
                "type": "翻译题",
                "question": f"将下列英语句子翻译成中文：{sentence}",
                "options": [],
                "answer": f"请参考例句翻译",
                "explanation": f"注意{grammar_config.get('grammar_name', '语法点')}的用法",
                "difficulty": "hard"
            }
        
        return self._create_default_translation(grammar_config, question_num)
    
    def _create_default_multiple_choice(self, grammar_config: Dict[str, Any], 
                                       question_num: int) -> Dict[str, Any]:
        """创建默认选择题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "选择题",
            "question": f"关于{grammar_name}的选择题 {question_num}",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "answer": "A",
            "explanation": f"这是{grammar_name}的基本用法",
            "difficulty": "easy"
        }
    
    def _create_default_fill_in_blank(self, grammar_config: Dict[str, Any], 
                                     question_num: int) -> Dict[str, Any]:
        """创建默认填空题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "填空题",
            "question": f"关于{grammar_name}的填空题 {question_num}：_____",
            "options": [],
            "answer": "答案",
            "explanation": f"这是{grammar_name}的基本用法",
            "difficulty": "easy"
        }
    
    def _create_default_error_correction(self, grammar_config: Dict[str, Any], 
                                        question_num: int) -> Dict[str, Any]:
        """创建默认改错题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "改错题",
            "question": f"找出并改正下列句子中的错误：关于{grammar_name}的错误句子 {question_num}",
            "options": [],
            "answer": "错误：错误部分 → 正确：正确部分",
            "explanation": f"这是{grammar_name}的正确用法",
            "difficulty": "medium"
        }
    
    def _create_default_sentence_creation(self, grammar_config: Dict[str, Any], 
                                         question_num: int) -> Dict[str, Any]:
        """创建默认造句题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "造句题",
            "question": f"用{grammar_name}造句",
            "options": [],
            "answer": f"这是使用{grammar_name}的例句",
            "explanation": f"正确使用{grammar_name}",
            "difficulty": "medium"
        }
    
    def _create_default_transformation(self, grammar_config: Dict[str, Any], 
                                      question_num: int) -> Dict[str, Any]:
        """创建默认转换题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "转换题",
            "question": f"按要求转换句子：关于{grammar_name}的原句 {question_num}",
            "options": [],
            "answer": "转换后的句子",
            "explanation": f"这是{grammar_name}的转换规则",
            "difficulty": "hard"
        }
    
    def _create_default_classification(self, grammar_config: Dict[str, Any], 
                                      question_num: int) -> Dict[str, Any]:
        """创建默认分类题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "分类题",
            "question": f"将下列{grammar_name}分类：word1, word2, word3, word4",
            "options": [],
            "answer": "第一组：word1, word2；第二组：word3, word4",
            "explanation": f"根据{grammar_name}规则进行分类",
            "difficulty": "medium"
        }
    
    def _create_default_matching(self, grammar_config: Dict[str, Any], 
                                question_num: int) -> Dict[str, Any]:
        """创建默认匹配题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "匹配题",
            "question": f"将下列内容与{grammar_name}匹配：",
            "options": ["1. 内容1", "2. 内容2", "3. 内容3", "4. 内容4"],
            "answer": f"1-{grammar_name}",
            "explanation": f"所有内容都与{grammar_name}相关",
            "difficulty": "easy"
        }
    
    def _create_default_true_false(self, grammar_config: Dict[str, Any], 
                                  question_num: int) -> Dict[str, Any]:
        """创建默认判断题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "判断题",
            "question": f"判断下列说法是否正确：{grammar_name}的用法规则",
            "options": ["正确", "错误"],
            "answer": "正确",
            "explanation": f"这是{grammar_name}的基本规则",
            "difficulty": "easy"
        }
    
    def _create_default_completion(self, grammar_config: Dict[str, Any], 
                                  question_num: int) -> Dict[str, Any]:
        """创建默认补全题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "补全题",
            "question": f"补全句子：关于{grammar_name}的句子 _____",
            "options": [],
            "answer": "答案",
            "explanation": f"这是{grammar_name}的典型用法",
            "difficulty": "medium"
        }
    
    def _create_default_translation(self, grammar_config: Dict[str, Any], 
                                   question_num: int) -> Dict[str, Any]:
        """创建默认翻译题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "翻译题",
            "question": f"将下列英语句子翻译成中文：{grammar_name} example sentence",
            "options": [],
            "answer": f"请参考{grammar_name}的例句翻译",
            "explanation": f"注意{grammar_name}的用法",
            "difficulty": "hard"
        }
    
    def _generate_general_exercise(self, grammar_config: Dict[str, Any], 
                                  question_num: int) -> Dict[str, Any]:
        """生成通用练习题"""
        grammar_name = grammar_config.get("grammar_name", "")
        
        return {
            "type": "综合题",
            "question": f"关于{grammar_name}的综合练习题 {question_num}",
            "options": [],
            "answer": "答案",
            "explanation": f"这是{grammar_name}的综合应用",
            "difficulty": "medium"
        }


if __name__ == "__main__":
    # 测试练习题生成器
    generator = ImprovedExerciseGenerator()
    
    # 测试配置
    test_config = {
        "grammar_name": "be动词用法",
        "exercise_templates": {
            "multiple_choice": {
                "templates": [
                    {
                        "question": "_____ a student.",
                        "correct": "I am",
                        "wrong_options": ["I is", "I are", "I be"],
                        "explanation": "第一人称单数用am"
                    }
                ]
            }
        }
    }
    
    # 生成练习题
    exercises = generator.generate_exercises(test_config, 5, "medium")
    
    for i, exercise in enumerate(exercises, 1):
        print(f"第{i}题 [{exercise['type']}]")
        print(f"题目：{exercise['question']}")
        if exercise.get('options'):
            print(f"选项：{exercise['options']}")
        print(f"答案：{exercise['answer']}")
        print(f"解析：{exercise['explanation']}")
        print("-" * 50)

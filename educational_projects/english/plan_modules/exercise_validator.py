#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
练习题校验器模块
确保练习题的语法正确性、单词针对性和提示准确性
"""

import re
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

@dataclass
class ExerciseValidationResult:
    """练习题校验结果"""
    is_valid: bool
    issues: List[str]
    suggestions: List[str]
    improved_question: Optional[str] = None
    improved_answer: Optional[str] = None
    improved_hint: Optional[str] = None
    improved_explanation: Optional[str] = None

class ExerciseValidator:
    """练习题校验器"""
    
    def __init__(self):
        # 常见语法错误模式
        self.grammar_error_patterns = [
            (r'\ba\s+(water|milk|air|music|information)\b', '不可数名词不能使用不定冠词a'),
            (r'\bI\s+am\s+(nice|good|bad)\s*[^a-zA-Z]', 'I am + 形容词的表达不够自然'),
            (r'\bI\s+like\s+(nice|good|bad|happy|sad)\s*[^a-zA-Z]', '不能直接说I like + 形容词'),
            (r'\bThis\s+is\s+a\s+(they|we|you|I)\b', '代词前不能使用冠词'),
            (r'\b(cat|dog|book|table)s\s+is\b', '复数名词应该用are而不是is'),
            (r'\bHe\s+(work|study|go|play)\s', '第三人称单数后动词应该加-s或变形'),
            # 新增：针对"There are many"类型错误的校验
            (r'\bThere\s+are\s+many\s+(work|study|go|play|run|jump|dance|sing|read|write|eat|drink|sleep|think)\s+here\b', 
             '动词不能直接用在"There are many _____ here"句型中'),
            (r'\bThere\s+are\s+many\s+(nice|good|bad|happy|sad|big|small|tall|short)\s+here\b', 
             '形容词不能直接用在"There are many _____ here"句型中，需要搭配名词'),
        ]
        
        # 提示信息模板
        self.hint_templates = {
            "一般现在时": {
                "third_person": "提示：一般现在时第三人称单数，动词要加-s或变形",
                "negative": "提示：一般现在时否定句，用don't/doesn't + 动词原形",
                "question": "提示：一般现在时疑问句，用Do/Does + 主语 + 动词原形"
            },
            "名词单复数": {
                "plural": "提示：复数名词变化规则",
                "countable": "提示：可数名词前可以用a/an，不可数名词不能用",
                "irregular": "提示：不规则复数变化"
            },
            "一般过去时": {
                "regular": "提示：规则动词过去式加-ed",
                "irregular": "提示：不规则动词过去式变化",
                "past_time": "提示：一般过去时常用yesterday, last等时间状语"
            },
            "现在进行时": {
                "structure": "提示：现在进行时 = be + 动词-ing",
                "ing_rules": "提示：动词-ing变化规则",
                "time": "提示：现在进行时常用now, at the moment等时间状语"
            },
            "现在完成时": {
                "structure": "提示：现在完成时 = have/has + 过去分词",
                "past_participle": "提示：过去分词变化规则",
                "time": "提示：现在完成时常用already, just, ever等副词"
            },
            "被动语态": {
                "structure": "提示：被动语态 = be + 过去分词",
                "agent": "提示：被动语态可以用by引出动作执行者"
            },
            "情态动词": {
                "structure": "提示：情态动词 + 动词原形",
                "meaning": "提示：不同情态动词表达不同语气和态度"
            }
        }
        
        # 不可数名词列表
        self.uncountable_nouns = {
            'water', 'milk', 'juice', 'coffee', 'tea', 'oil', 'air', 
            'music', 'information', 'news', 'advice', 'money', 'time',
            'weather', 'homework', 'work', 'furniture', 'equipment'
        }
        
        # 常用动词变形
        self.irregular_verbs = {
            'go': {'past': 'went', 'past_participle': 'gone', 'third_person': 'goes'},
            'have': {'past': 'had', 'past_participle': 'had', 'third_person': 'has'},
            'do': {'past': 'did', 'past_participle': 'done', 'third_person': 'does'},
            'make': {'past': 'made', 'past_participle': 'made', 'third_person': 'makes'},
            'take': {'past': 'took', 'past_participle': 'taken', 'third_person': 'takes'},
            'see': {'past': 'saw', 'past_participle': 'seen', 'third_person': 'sees'},
            'come': {'past': 'came', 'past_participle': 'come', 'third_person': 'comes'},
            'give': {'past': 'gave', 'past_participle': 'given', 'third_person': 'gives'},
            'write': {'past': 'wrote', 'past_participle': 'written', 'third_person': 'writes'},
            'read': {'past': 'read', 'past_participle': 'read', 'third_person': 'reads'},
        }
    
    def validate_exercise(self, question: str, answer: str, word_info, grammar_topic: str, 
                         hint: str = "", explanation: str = "") -> ExerciseValidationResult:
        """校验练习题的完整性"""
        issues = []
        suggestions = []
        
        # 1. 语法校验
        grammar_issues = self._check_grammar(question, answer)
        issues.extend(grammar_issues)
        
        # 2. 单词针对性校验
        word_targeting_issues = self._check_word_targeting(question, answer, word_info)
        issues.extend(word_targeting_issues)
        
        # 3. 提示信息校验
        hint_issues = self._check_hint_quality(hint, grammar_topic, word_info)
        issues.extend(hint_issues)
        
        # 4. 答案正确性校验
        answer_issues = self._check_answer_correctness(question, answer, word_info, grammar_topic)
        issues.extend(answer_issues)
        
        # 5. 解释质量校验
        explanation_issues = self._check_explanation_quality(explanation, word_info, grammar_topic)
        issues.extend(explanation_issues)
        
        # 生成改进建议
        improved_question, improved_answer, improved_hint, improved_explanation = \
            self._generate_improvements(question, answer, hint, explanation, word_info, grammar_topic, issues)
        
        is_valid = len(issues) == 0
        
        return ExerciseValidationResult(
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions,
            improved_question=improved_question,
            improved_answer=improved_answer,
            improved_hint=improved_hint,
            improved_explanation=improved_explanation
        )
    
    def _check_grammar(self, question: str, answer: str) -> List[str]:
        """检查语法错误"""
        issues = []
        
        # 检查问题中的语法错误
        for pattern, error_msg in self.grammar_error_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                issues.append(f"问题语法错误：{error_msg}")
        
        # 检查答案中的语法错误
        for pattern, error_msg in self.grammar_error_patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                issues.append(f"答案语法错误：{error_msg}")
        
        # 检查特定语法错误
        issues.extend(self._check_specific_grammar_issues(question, answer))
        
        return issues
    
    def _check_specific_grammar_issues(self, question: str, answer: str) -> List[str]:
        """检查特定的语法问题"""
        issues = []
        
        # 检查冠词使用
        if re.search(r'\ba\s+(water|air|music|information)\b', question + " " + answer, re.IGNORECASE):
            issues.append("不可数名词前不应使用不定冠词'a'")
        
        # 检查主谓一致
        if re.search(r'\b(books|cats|dogs|students)\s+is\b', question + " " + answer, re.IGNORECASE):
            issues.append("复数主语应该使用'are'而不是'is'")
        
        # 检查第三人称单数
        third_person_subjects = r'\b(he|she|it|Tom|Mary|the boy|the girl)\s+'
        common_verbs = r'(work|study|play|go|come|like)\s'
        if re.search(third_person_subjects + common_verbs, question + " " + answer, re.IGNORECASE):
            if not re.search(third_person_subjects + r'(works|studies|plays|goes|comes|likes)\s', 
                           question + " " + answer, re.IGNORECASE):
                issues.append("第三人称单数主语后动词应该加-s或相应变形")
        
        return issues
    
    def _check_word_targeting(self, question: str, answer: str, word_info) -> List[str]:
        """检查是否针对当日学习单词"""
        issues = []
        
        target_word = word_info.word.lower()
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # 检查目标单词是否出现
        if target_word not in question_lower and target_word not in answer_lower:
            # 检查常见变形
            word_variations = self._get_word_variations(word_info)
            found_variation = False
            
            for variation in word_variations:
                if variation.lower() in question_lower or variation.lower() in answer_lower:
                    found_variation = True
                    break
            
            if not found_variation:
                issues.append(f"练习题中未包含目标单词'{target_word}'或其变形")
        
        # 检查中文意思是否出现
        if word_info.chinese_meaning not in question and word_info.chinese_meaning not in answer:
            issues.append(f"练习题中未包含单词的中文意思'{word_info.chinese_meaning}'")
        
        return issues
    
    def _check_hint_quality(self, hint: str, grammar_topic: str, word_info) -> List[str]:
        """检查提示信息质量"""
        issues = []
        
        if not hint or len(hint.strip()) < 5:
            issues.append("提示信息过短或缺失")
            return issues
        
        # 检查提示是否与语法主题相关
        topic_keywords = self._get_topic_keywords(grammar_topic)
        hint_contains_topic = any(keyword in hint for keyword in topic_keywords)
        
        if not hint_contains_topic:
            issues.append(f"提示信息与语法主题'{grammar_topic}'关联度不足")
        
        # 检查提示是否包含具体的语法规则
        if "提示：" not in hint:
            issues.append("提示信息应该以'提示：'开头")
        
        return issues
    
    def _check_answer_correctness(self, question: str, answer: str, word_info, grammar_topic: str) -> List[str]:
        """检查答案正确性"""
        issues = []
        
        if not answer or len(answer.strip()) < 2:
            issues.append("答案过短或缺失")
            return issues
        
        # 根据语法主题检查特定答案格式
        if "第三人称单数" in grammar_topic and word_info.part_of_speech == "verb":
            expected_form = self._get_third_person_form(word_info.word)
            if expected_form not in answer and word_info.word + "s" not in answer:
                issues.append(f"第三人称单数题目中应该包含正确的动词变形")
        
        if "名词单复数" in grammar_topic and word_info.part_of_speech == "noun":
            expected_plural = self._get_plural_form(word_info.word)
            if "two" in question.lower() or "many" in question.lower():
                if expected_plural not in answer:
                    issues.append("复数题目中应该包含正确的名词复数形式")
        
        return issues
    
    def _check_explanation_quality(self, explanation: str, word_info, grammar_topic: str) -> List[str]:
        """检查解释质量"""
        issues = []
        
        if not explanation or len(explanation.strip()) < 10:
            issues.append("解释过短或缺失")
            return issues
        
        # 检查解释是否包含语法规则说明
        if "规则：" not in explanation and "语法" not in explanation:
            issues.append("解释中应该包含语法规则说明")
        
        # 检查解释是否包含单词信息
        if word_info.word not in explanation and word_info.chinese_meaning not in explanation:
            issues.append("解释中应该包含目标单词及其含义")
        
        return issues
    
    def _generate_improvements(self, question: str, answer: str, hint: str, explanation: str,
                             word_info, grammar_topic: str, issues: List[str]) -> Tuple[str, str, str, str]:
        """生成改进的练习题"""
        improved_question = question
        improved_answer = answer
        improved_hint = hint
        improved_explanation = explanation
        
        # 改进提示信息
        if not hint or any("提示" in issue for issue in issues):
            improved_hint = self._generate_better_hint(word_info, grammar_topic)
        
        # 改进解释
        if not explanation or any("解释" in issue for issue in issues):
            improved_explanation = self._generate_better_explanation(word_info, grammar_topic, answer)
        
        # 改进语法错误
        if any("语法错误" in issue for issue in issues):
            improved_question, improved_answer = self._fix_grammar_issues(question, answer, word_info, grammar_topic)
        
        return improved_question, improved_answer, improved_hint, improved_explanation
    
    def _generate_better_hint(self, word_info, grammar_topic: str) -> str:
        """生成更好的提示信息"""
        # 根据语法主题生成相应提示
        if "一般现在时" in grammar_topic:
            if "第三人称单数" in grammar_topic:
                if word_info.part_of_speech == "verb":
                    third_form = self._get_third_person_form(word_info.word)
                    return f"提示：一般现在时第三人称单数，{word_info.word} → {third_form}"
                else:
                    return "提示：一般现在时第三人称单数，He/She + 动词第三人称单数形式"
        
        elif "名词单复数" in grammar_topic:
            if word_info.part_of_speech == "noun":
                plural_form = self._get_plural_form(word_info.word)
                rule = self._get_plural_rule(word_info.word)
                return f"提示：{rule}，{word_info.word} → {plural_form}"
            else:
                return "提示：名词复数变化，注意可数名词和不可数名词的区别"
        
        elif "一般过去时" in grammar_topic:
            if word_info.part_of_speech == "verb":
                past_form = self._get_past_form(word_info.word)
                rule = self._get_past_rule(word_info.word)
                return f"提示：{rule}，{word_info.word} → {past_form}"
            else:
                return "提示：一般过去时表示过去发生的动作，常用yesterday, last等时间状语"
        
        elif "现在进行时" in grammar_topic:
            if word_info.part_of_speech == "verb":
                ing_form = self._get_ing_form(word_info.word)
                rule = self._get_ing_rule(word_info.word)
                return f"提示：现在进行时 = be + 动词-ing，{rule}，{word_info.word} → {ing_form}"
            else:
                return "提示：现在进行时 = be + 动词-ing，表示正在进行的动作"
        
        else:
            return f"提示：注意{word_info.word}（{word_info.chinese_meaning}）在句子中的正确使用"
    
    def _generate_better_explanation(self, word_info, grammar_topic: str, answer: str) -> str:
        """生成更好的解释"""
        if "一般现在时" in grammar_topic and "第三人称单数" in grammar_topic:
            if word_info.part_of_speech == "verb":
                third_form = self._get_third_person_form(word_info.word)
                rule = self._get_third_person_rule(word_info.word)
                return f"第三人称单数语法：{rule}。{word_info.word}（{word_info.chinese_meaning}）的第三人称单数形式是{third_form}。"
        
        elif "名词单复数" in grammar_topic and word_info.part_of_speech == "noun":
            plural_form = self._get_plural_form(word_info.word)
            rule = self._get_plural_rule(word_info.word)
            return f"名词复数语法：{rule}。{word_info.word}（{word_info.chinese_meaning}）的复数形式是{plural_form}。"
        
        elif "一般过去时" in grammar_topic and word_info.part_of_speech == "verb":
            past_form = self._get_past_form(word_info.word)
            rule = self._get_past_rule(word_info.word)
            return f"一般过去时语法：{rule}。{word_info.word}（{word_info.chinese_meaning}）的过去式是{past_form}。"
        
        else:
            return f"语法解释：{word_info.word}（{word_info.chinese_meaning}）是{self._get_part_of_speech_chinese(word_info.part_of_speech)}，在句子中的使用要符合相应的语法规则。"
    
    def _fix_grammar_issues(self, question: str, answer: str, word_info, grammar_topic: str) -> Tuple[str, str]:
        """修复语法问题"""
        fixed_question = question
        fixed_answer = answer
        
        # 修复不可数名词前的冠词问题
        if word_info.word.lower() in self.uncountable_nouns:
            fixed_question = re.sub(r'\ba\s+' + re.escape(word_info.word), word_info.word, fixed_question, flags=re.IGNORECASE)
            fixed_answer = re.sub(r'\ba\s+' + re.escape(word_info.word), word_info.word, fixed_answer, flags=re.IGNORECASE)
        
        # 修复第三人称单数问题
        if "第三人称单数" in grammar_topic and word_info.part_of_speech == "verb":
            # 确保使用正确的第三人称单数形式
            third_form = self._get_third_person_form(word_info.word)
            # 替换He/She + 动词原形 为 He/She + 动词第三人称单数
            fixed_answer = re.sub(r'\b(He|She|It)\s+' + re.escape(word_info.word) + r'\b', 
                                r'\1 ' + third_form, fixed_answer, flags=re.IGNORECASE)
        
        # 修复"There are many"类型的问题
        if "There are many" in fixed_question and "here" in fixed_question:
            if word_info.part_of_speech == "verb":
                # 动词不能直接用在这个句型中，改为合适的句型
                fixed_question = f"I _____ every day.\n我每天{word_info.chinese_meaning}。"
                fixed_answer = word_info.word
            elif word_info.part_of_speech == "adjective":
                # 形容词需要搭配名词，改为合适的句型
                chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
                fixed_question = f"I am _____.\n我很{chinese_adj}。"
                fixed_answer = word_info.word
            elif word_info.part_of_speech not in ["noun"]:
                # 其他非名词词性，使用通用句型
                fixed_question = f"I like _____ things.\n我喜欢{word_info.chinese_meaning}的事物。"
                fixed_answer = word_info.word
        
        # 修复"I like + 形容词"类型的问题
        if "I like" in fixed_question and word_info.part_of_speech == "adjective":
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            fixed_question = f"I am _____.\n我很{chinese_adj}。"
            fixed_answer = word_info.word
        
        return fixed_question, fixed_answer
    
    # 辅助方法（复用现有的语法变化方法）
    def _get_word_variations(self, word_info):
        """获取单词的各种变形"""
        variations = [word_info.word]
        
        if word_info.part_of_speech == "verb":
            variations.extend([
                self._get_third_person_form(word_info.word),
                self._get_past_form(word_info.word),
                self._get_ing_form(word_info.word),
                self._get_past_participle_form(word_info.word)
            ])
        elif word_info.part_of_speech == "noun":
            variations.append(self._get_plural_form(word_info.word))
        
        return variations
    
    def _get_topic_keywords(self, grammar_topic: str) -> List[str]:
        """获取语法主题关键词"""
        if "一般现在时" in grammar_topic:
            return ["一般现在时", "现在时", "第三人称单数", "动词", "every day"]
        elif "名词单复数" in grammar_topic:
            return ["名词", "复数", "单数", "many", "two", "-s", "-es"]
        elif "一般过去时" in grammar_topic:
            return ["过去时", "yesterday", "last", "-ed", "过去式"]
        elif "现在进行时" in grammar_topic:
            return ["进行时", "be", "-ing", "now", "正在"]
        else:
            return [grammar_topic]
    
    def _get_part_of_speech_chinese(self, part_of_speech: str) -> str:
        """获取词性的中文名称"""
        mapping = {
            "noun": "名词",
            "verb": "动词", 
            "adjective": "形容词",
            "adverb": "副词"
        }
        return mapping.get(part_of_speech, part_of_speech)
    
    # 复用exercise_generator中的方法
    def _get_third_person_form(self, word: str) -> str:
        if word in self.irregular_verbs:
            return self.irregular_verbs[word]['third_person']
        elif word.endswith(('s', 'x', 'ch', 'sh', 'o')):
            return f"{word}es"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"{word[:-1]}ies"
        else:
            return f"{word}s"
    
    def _get_third_person_rule(self, word: str) -> str:
        if word in self.irregular_verbs:
            return f"不规则变化：{word} → {self.irregular_verbs[word]['third_person']}"
        elif word.endswith(('s', 'x', 'ch', 'sh', 'o')):
            return f"以s, x, ch, sh, o结尾加-es"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"以辅音+y结尾，变y为i加-es"
        else:
            return f"一般情况加-s"
    
    def _get_plural_form(self, word: str) -> str:
        if word.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return f"{word}es"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"{word[:-1]}ies"
        elif word.endswith('f'):
            return f"{word[:-1]}ves"
        elif word.endswith('fe'):
            return f"{word[:-2]}ves"
        else:
            return f"{word}s"
    
    def _get_plural_rule(self, word: str) -> str:
        if word.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return f"以s, sh, ch, x, z结尾的名词，复数加-es"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"以辅音字母+y结尾的名词，变y为i再加-es"
        elif word.endswith('f'):
            return f"以f结尾的名词，变f为v再加-es"
        elif word.endswith('fe'):
            return f"以fe结尾的名词，变fe为v再加-es"
        else:
            return f"一般名词复数直接加-s"
    
    def _get_past_form(self, word: str) -> str:
        if word in self.irregular_verbs:
            return self.irregular_verbs[word]['past']
        elif word.endswith('e'):
            return f"{word}d"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"{word[:-1]}ied"
        else:
            return f"{word}ed"
    
    def _get_past_rule(self, word: str) -> str:
        if word in self.irregular_verbs:
            return f"不规则变化：{word} → {self.irregular_verbs[word]['past']}"
        elif word.endswith('e'):
            return f"以e结尾的动词，过去式加-d"
        elif word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return f"以辅音+y结尾的动词，变y为i加-ed"
        else:
            return f"一般动词，过去式加-ed"
    
    def _get_ing_form(self, word: str) -> str:
        if word.endswith('e') and len(word) > 2:
            return f"{word[:-1]}ing"
        else:
            return f"{word}ing"
    
    def _get_ing_rule(self, word: str) -> str:
        if word.endswith('e') and len(word) > 2:
            return f"以e结尾的动词，去e加-ing"
        else:
            return f"一般动词，直接加-ing"
    
    def _get_past_participle_form(self, word: str) -> str:
        if word in self.irregular_verbs:
            return self.irregular_verbs[word]['past_participle']
        else:
            return self._get_past_form(word)

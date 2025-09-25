#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
形容词语法生成器
处理形容词相关语法的练习题生成
"""

import random
from typing import List
from .base_generator import BaseGrammarGenerator, Exercise
from .grammar_rules import GrammarRules
from .exercise_templates import ExerciseTemplates


class AdjectiveGenerators(BaseGrammarGenerator):
    """形容词语法生成器"""
    
    def __init__(self):
        super().__init__()
        self.grammar_rules = GrammarRules()
        self.templates = ExerciseTemplates()
        self.supported_grammar_topics = [
            "形容词比较级-基础用法",
            "形容词最高级-基础用法",
            "形容词修饰名词",
            "be动词用法",
        ]
    
    def supports_grammar_topic(self, grammar_topic: str) -> bool:
        """检查是否支持指定的语法主题"""
        return any(topic in grammar_topic for topic in self.supported_grammar_topics)
    
    def generate_fill_blank_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成填空题"""
        if "比较级" in grammar_topic:
            return self._generate_comparative_fill_blank(word_info, grammar_topic)
        elif "最高级" in grammar_topic:
            return self._generate_superlative_fill_blank(word_info, grammar_topic)
        elif "be动词" in grammar_topic:
            return self._generate_be_verb_fill_blank(word_info, grammar_topic)
        else:
            return self._generate_basic_adjective_fill_blank(word_info, grammar_topic)
    
    def generate_translation_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成翻译题"""
        if "比较级" in grammar_topic:
            return self._generate_comparative_translation(word_info, grammar_topic)
        elif "最高级" in grammar_topic:
            return self._generate_superlative_translation(word_info, grammar_topic)
        elif "be动词" in grammar_topic:
            return self._generate_be_verb_translation(word_info, grammar_topic)
        else:
            return self._generate_basic_adjective_translation(word_info, grammar_topic)
    
    def generate_choice_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成选择题"""
        if "比较级" in grammar_topic:
            return self._generate_comparative_choice(word_info, grammar_topic)
        elif "最高级" in grammar_topic:
            return self._generate_superlative_choice(word_info, grammar_topic)
        elif "be动词" in grammar_topic:
            return self._generate_be_verb_choice(word_info, grammar_topic)
        else:
            return self._generate_basic_adjective_choice(word_info, grammar_topic)
    
    def generate_completion_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成句子完成题"""
        if "比较级" in grammar_topic:
            return self._generate_comparative_completion(word_info, grammar_topic)
        elif "最高级" in grammar_topic:
            return self._generate_superlative_completion(word_info, grammar_topic)
        elif "be动词" in grammar_topic:
            return self._generate_be_verb_completion(word_info, grammar_topic)
        else:
            return self._generate_basic_adjective_completion(word_info, grammar_topic)
    
    # 形容词比较级练习题生成
    def _generate_comparative_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成形容词比较级填空题"""
        if word_info.part_of_speech == "adjective":
            comparative_form = self.grammar_rules.get_comparative_form(word_info.word)
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            question = f"This book is _____ than that one.\n这本书比那本更{chinese_adj}。"
            hint = f"提示：{self.grammar_rules.get_comparative_rule(word_info.word)}"
            explanation = f"形容词比较级变化：{word_info.word} → {comparative_form}。规则：{self.grammar_rules.get_comparative_rule(word_info.word)}"
            return Exercise(question, comparative_form, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            # 非形容词的比较级练习
            question = f"This _____ is bigger than that one.\n这个{word_info.chinese_meaning}比那个大。"
            hint = f"提示：比较级句型：A + be + 比较级 + than + B"
            explanation = f"形容词比较级语法：{grammar_topic}。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_superlative_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成形容词最高级填空题"""
        if word_info.part_of_speech == "adjective":
            superlative_form = self.grammar_rules.get_superlative_form(word_info.word)
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            question = f"This is the _____ book.\n这是最{chinese_adj}的书。"
            hint = f"提示：最高级前要加the"
            explanation = f"形容词最高级：{word_info.word} → {superlative_form}。最高级前要加定冠词the。"
            return Exercise(question, superlative_form, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"This _____ is the biggest.\n这个{word_info.chinese_meaning}是最大的。"
            hint = f"提示：最高级句型：the + 最高级"
            explanation = f"形容词最高级语法：{grammar_topic}。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_be_verb_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成be动词用法填空题"""
        if word_info.part_of_speech == "adjective":
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            question = f"I am _____.\n我很{chinese_adj}。"
            hint = "提示：be动词 + 形容词，表示状态"
            explanation = f"be动词后接形容词表示状态。{word_info.word}（{word_info.chinese_meaning}）是形容词。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        elif word_info.part_of_speech == "noun":
            question = f"This is a _____.\n这是一个{word_info.chinese_meaning}。"
            hint = "提示：This is + a/an + 名词"
            explanation = f"be动词句型：This is + 名词。{word_info.word}（{word_info.chinese_meaning}）是名词。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"I am a _____.\n我是一个{word_info.chinese_meaning}。"
            hint = f"提示：be动词的基本用法"
            explanation = f"be动词用法：I am a + 名词/身份。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    # 翻译题生成方法
    def _generate_comparative_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成比较级翻译题"""
        if word_info.part_of_speech == "adjective":
            comparative_form = self.grammar_rules.get_comparative_form(word_info.word)
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            english_sentence = f"This book is {comparative_form} than that one."
            chinese_sentence = f"这本书比那本更{chinese_adj}。"
            question = f"中译英：{chinese_sentence}"
            hint = f"提示：比较级句型 A + be + 比较级 + than + B"
            explanation = f"翻译：{chinese_sentence} = {english_sentence}。比较级：{word_info.word} → {comparative_form}"
            return Exercise(question, english_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_translation(word_info, grammar_topic)
    
    def _generate_superlative_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成最高级翻译题"""
        if word_info.part_of_speech == "adjective":
            superlative_form = self.grammar_rules.get_superlative_form(word_info.word)
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            english_sentence = f"This is the {superlative_form} book."
            chinese_sentence = f"这是最{chinese_adj}的书。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：最高级前要加the"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}。最高级：{word_info.word} → the {superlative_form}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_translation(word_info, grammar_topic)
    
    def _generate_be_verb_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成be动词翻译题"""
        if word_info.part_of_speech == "adjective":
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            english_sentence = f"I am {word_info.word}."
            chinese_sentence = f"我很{chinese_adj}。"
            question = f"中译英：{chinese_sentence}"
            hint = f"提示：be动词 + 形容词"
            explanation = f"翻译：{chinese_sentence} = {english_sentence}。be动词用法：am + 形容词"
            return Exercise(question, english_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        elif word_info.part_of_speech == "noun":
            english_sentence = f"This is a {word_info.word}."
            chinese_sentence = f"这是一个{word_info.chinese_meaning}。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：This is + a + 名词"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}。be动词用法：is + 名词"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_translation(word_info, grammar_topic)
    
    # 选择题生成方法
    def _generate_comparative_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成比较级选择题"""
        if word_info.part_of_speech == "adjective":
            correct_answer = self.grammar_rules.get_comparative_form(word_info.word)
            options = self.templates.generate_choice_options(correct_answer, "adjective", grammar_topic)
            question_text = f"What is the comparative form of '{word_info.word}'?"
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：{self.grammar_rules.get_comparative_rule(word_info.word)}"
            explanation = f"形容词比较级：{word_info.word} → {correct_answer}。规则：{self.grammar_rules.get_comparative_rule(word_info.word)}"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_choice(word_info, grammar_topic)
    
    def _generate_superlative_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成最高级选择题"""
        if word_info.part_of_speech == "adjective":
            correct_answer = self.grammar_rules.get_superlative_form(word_info.word)
            base_adj = word_info.word
            comparative = self.grammar_rules.get_comparative_form(word_info.word)
            options = [correct_answer, base_adj, comparative, f"very {base_adj}"]
            random.shuffle(options)
            question_text = f"What is the superlative form of '{word_info.word}'?"
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：最高级表示三者或以上的比较"
            explanation = f"形容词最高级：{word_info.word} → {correct_answer}。最高级用于三者或以上的比较。"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_choice(word_info, grammar_topic)
    
    def _generate_be_verb_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成be动词选择题"""
        if word_info.part_of_speech == "adjective":
            options = ["am", "is", "are", "be"]
            correct_answer = "am"  # 假设主语是I
            question_text = f"I _____ {word_info.word}."
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：主语I后面用am"
            explanation = f"be动词用法：I + am + 形容词。{word_info.word}是形容词。"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_choice(word_info, grammar_topic)
    
    # 句子完成题生成方法
    def _generate_comparative_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成比较级句子完成题"""
        if word_info.part_of_speech == "adjective":
            comparative_form = self.grammar_rules.get_comparative_form(word_info.word)
            question = f"完成句子：\nThis book is _____ than that one (提示：{word_info.chinese_meaning})"
            answer = f"This book is {comparative_form} than that one"
            hint = f"提示：比较级句型 A + be + 比较级 + than + B"
            explanation = f"句子完成：This book is {comparative_form} than that one。比较级：{word_info.word} → {comparative_form}"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_completion(word_info, grammar_topic)
    
    def _generate_superlative_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成最高级句子完成题"""
        if word_info.part_of_speech == "adjective":
            superlative_form = self.grammar_rules.get_superlative_form(word_info.word)
            question = f"完成句子：\nThis is the _____ book (提示：{word_info.chinese_meaning})"
            answer = f"This is the {superlative_form} book"
            hint = f"提示：最高级前要加the"
            explanation = f"句子完成：This is the {superlative_form} book。最高级：{word_info.word} → the {superlative_form}"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_completion(word_info, grammar_topic)
    
    def _generate_be_verb_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成be动词句子完成题"""
        if word_info.part_of_speech == "adjective":
            question = f"完成句子：\nI am _____ (提示：{word_info.chinese_meaning})"
            answer = f"I am {word_info.word}"
            hint = f"提示：be动词 + 形容词"
            explanation = f"句子完成：I am {word_info.word}。be动词用法：am + 形容词表示状态。"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        elif word_info.part_of_speech == "noun":
            question = f"完成句子：\nThis is a _____ (提示：{word_info.chinese_meaning})"
            answer = f"This is a {word_info.word}"
            hint = f"提示：This is + a + 名词"
            explanation = f"句子完成：This is a {word_info.word}。be动词用法：is + 名词。"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_adjective_completion(word_info, grammar_topic)
    
    # 基础练习题生成方法
    def _generate_basic_adjective_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础形容词填空题"""
        if word_info.part_of_speech == "adjective":
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            question = f"The book is _____.\n这本书很{chinese_adj}。"
            hint = f"提示：{word_info.word}（{word_info.chinese_meaning}）是形容词"
            explanation = f"形容词用法：主语 + be动词 + 形容词。{word_info.word}（{word_info.chinese_meaning}）是形容词。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"I like _____.\n我喜欢{word_info.chinese_meaning}。"
            hint = f"提示：{word_info.word}（{word_info.chinese_meaning}）"
            explanation = f"基础句型：I like + 词语。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_adjective_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础形容词翻译题"""
        if word_info.part_of_speech == "adjective":
            chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
            english_sentence = f"The book is {word_info.word}."
            chinese_sentence = f"这本书很{chinese_adj}。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：{word_info.word} = {word_info.chinese_meaning}"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            english_sentence = f"I like {word_info.word}."
            chinese_sentence = f"我喜欢{word_info.chinese_meaning}。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：{word_info.word} = {word_info.chinese_meaning}"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_adjective_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础形容词选择题"""
        options = [word_info.word, "option1", "option2", "option3"]
        random.shuffle(options)
        question_text = f"What is the English word for '{word_info.chinese_meaning}'?"
        question = self.templates.format_choice_question(question_text, options)
        hint = f"提示：{word_info.chinese_meaning}的英文单词"
        explanation = f"答案：{word_info.chinese_meaning} = {word_info.word}"
        return Exercise(question, chr(65 + options.index(word_info.word)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_adjective_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础形容词句子完成题"""
        if word_info.part_of_speech == "adjective":
            question = f"完成句子：\nThe book is _____ (提示：{word_info.chinese_meaning})"
            answer = f"The book is {word_info.word}"
            hint = f"提示：{word_info.chinese_meaning} = {word_info.word}"
            explanation = f"句子完成：The book is {word_info.word}。{word_info.word}（{word_info.chinese_meaning}）是形容词。"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"完成句子：\nI like _____ (提示：{word_info.chinese_meaning})"
            answer = f"I like {word_info.word}"
            hint = f"提示：{word_info.chinese_meaning} = {word_info.word}"
            explanation = f"句子完成：I like {word_info.word}。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)

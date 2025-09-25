#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
名词语法生成器
处理名词相关语法的练习题生成
"""

import random
from typing import List
from .base_generator import BaseGrammarGenerator, Exercise
from .grammar_rules import GrammarRules
from .exercise_templates import ExerciseTemplates


class NounGenerators(BaseGrammarGenerator):
    """名词语法生成器"""
    
    def __init__(self):
        super().__init__()
        self.grammar_rules = GrammarRules()
        self.templates = ExerciseTemplates()
        self.supported_grammar_topics = [
            "名词单复数-基础规则",
            "冠词用法",
            "不可数名词",
            "可数名词",
        ]
    
    def supports_grammar_topic(self, grammar_topic: str) -> bool:
        """检查是否支持指定的语法主题"""
        return any(topic in grammar_topic for topic in self.supported_grammar_topics)
    
    def generate_fill_blank_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成填空题"""
        if "名词单复数" in grammar_topic:
            return self._generate_plural_fill_blank(word_info, grammar_topic)
        elif "冠词" in grammar_topic:
            return self._generate_article_fill_blank(word_info, grammar_topic)
        else:
            return self._generate_basic_noun_fill_blank(word_info, grammar_topic)
    
    def generate_translation_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成翻译题"""
        if "名词单复数" in grammar_topic:
            return self._generate_plural_translation(word_info, grammar_topic)
        elif "冠词" in grammar_topic:
            return self._generate_article_translation(word_info, grammar_topic)
        else:
            return self._generate_basic_noun_translation(word_info, grammar_topic)
    
    def generate_choice_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成选择题"""
        if "名词单复数" in grammar_topic:
            return self._generate_plural_choice(word_info, grammar_topic)
        elif "冠词" in grammar_topic:
            return self._generate_article_choice(word_info, grammar_topic)
        else:
            return self._generate_basic_noun_choice(word_info, grammar_topic)
    
    def generate_completion_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成句子完成题"""
        if "名词单复数" in grammar_topic:
            return self._generate_plural_completion(word_info, grammar_topic)
        elif "冠词" in grammar_topic:
            return self._generate_article_completion(word_info, grammar_topic)
        else:
            return self._generate_basic_noun_completion(word_info, grammar_topic)
    
    # 名词单复数练习题生成
    def _generate_plural_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成名词单复数填空题"""
        if word_info.part_of_speech == "noun":
            plural_form = self.grammar_rules.get_plural_form(word_info.word)
            question = f"I have two _____.\n我有两个{word_info.chinese_meaning}。"
            hint = f"提示：{self.grammar_rules.get_plural_rule(word_info.word)}"
            explanation = f"名词复数语法：{self.grammar_rules.get_plural_rule(word_info.word)}。{word_info.word}的复数形式是{plural_form}。"
            return Exercise(question, plural_form, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            # 非名词的单复数练习
            if word_info.part_of_speech == "adjective":
                chinese_adj = word_info.chinese_meaning.rstrip('的') if word_info.chinese_meaning.endswith('的') else word_info.chinese_meaning
                question = f"I have many _____ books.\n我有很多{chinese_adj}的书。"
                hint = f"提示：形容词修饰复数名词"
                explanation = f"形容词修饰名词：形容词 + 复数名词。{word_info.word}（{word_info.chinese_meaning}）是形容词。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
            else:
                # 对于非名词的处理，需要更谨慎
                if word_info.part_of_speech == "verb":
                    # 动词不能直接放在 "There are many _____ here" 中，使用更合适的句型
                    question = f"I _____ every day.\n我每天{word_info.chinese_meaning}。"
                    hint = f"提示：动词在一般现在时的用法"
                    explanation = f"动词用法：{word_info.word}（{word_info.chinese_meaning}）是动词。"
                    return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
                else:
                    # 其他词性也需要合适的句型
                    question = f"I like _____ things.\n我喜欢{word_info.chinese_meaning}的东西。"
                    hint = f"提示：{word_info.word}（{word_info.chinese_meaning}）"
                    explanation = f"词汇用法：{word_info.word}（{word_info.chinese_meaning}）。"
                    return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_article_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成冠词用法填空题"""
        if word_info.part_of_speech == "noun":
            if self.grammar_rules.is_uncountable_noun(word_info.word):
                question = f"I like _____.\n我喜欢{word_info.chinese_meaning}。"
                answer = word_info.word
                hint = f"提示：不可数名词前不用冠词"
                explanation = f"冠词用法：{word_info.word}是不可数名词，前面不需要冠词。"
            else:
                article = "an" if word_info.word[0].lower() in 'aeiou' else "a"
                question = f"This is _____ {word_info.word}.\n这是一个{word_info.chinese_meaning}。"
                answer = article
                hint = f"提示：可数名词单数前用a/an"
                explanation = f"冠词用法：{word_info.word}是可数名词，前面用{article}。"
            return Exercise(question, answer, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_noun_fill_blank(word_info, grammar_topic)
    
    # 翻译题生成方法
    def _generate_plural_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成名词复数翻译题"""
        if word_info.part_of_speech == "noun":
            plural_form = self.grammar_rules.get_plural_form(word_info.word)
            english_sentence = f"I have many {plural_form}."
            chinese_sentence = f"我有很多{word_info.chinese_meaning}。"
            question = f"中译英：{chinese_sentence}"
            hint = f"提示：many后接名词复数"
            explanation = f"翻译：{chinese_sentence} = {english_sentence}。名词复数：{word_info.word} → {plural_form}"
            return Exercise(question, english_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_noun_translation(word_info, grammar_topic)
    
    def _generate_article_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成冠词翻译题"""
        if word_info.part_of_speech == "noun":
            if self.grammar_rules.is_uncountable_noun(word_info.word):
                english_sentence = f"I like {word_info.word}."
                chinese_sentence = f"我喜欢{word_info.chinese_meaning}。"
                question = f"中译英：{chinese_sentence}"
                hint = f"提示：不可数名词前不用冠词"
                explanation = f"翻译：{chinese_sentence} = {english_sentence}。{word_info.word}是不可数名词。"
            else:
                article = "an" if word_info.word[0].lower() in 'aeiou' else "a"
                english_sentence = f"This is {article} {word_info.word}."
                chinese_sentence = f"这是一个{word_info.chinese_meaning}。"
                question = f"中译英：{chinese_sentence}"
                hint = f"提示：可数名词单数前用a/an"
                explanation = f"翻译：{chinese_sentence} = {english_sentence}。冠词：{article} {word_info.word}"
            return Exercise(question, english_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_noun_translation(word_info, grammar_topic)
    
    # 选择题生成方法
    def _generate_plural_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成名词复数选择题"""
        if word_info.part_of_speech == "noun":
            correct_answer = self.grammar_rules.get_plural_form(word_info.word)
            options = self.templates.generate_choice_options(correct_answer, "noun", grammar_topic)
            question_text = f"What is the plural form of '{word_info.word}'?"
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：{self.grammar_rules.get_plural_rule(word_info.word)}"
            explanation = f"名词复数：{word_info.word} → {correct_answer}。规则：{self.grammar_rules.get_plural_rule(word_info.word)}"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_noun_choice(word_info, grammar_topic)
    
    def _generate_article_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成冠词选择题"""
        if word_info.part_of_speech == "noun":
            if self.grammar_rules.is_uncountable_noun(word_info.word):
                correct_answer = "no article"
                options = ["a", "an", "the", "no article"]
                question_text = f"Choose the correct article for '{word_info.word}': I like _____ {word_info.word}."
            else:
                correct_answer = "an" if word_info.word[0].lower() in 'aeiou' else "a"
                options = ["a", "an", "the", "no article"]
                question_text = f"Choose the correct article for '{word_info.word}': This is _____ {word_info.word}."
            
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：根据名词类型选择合适的冠词"
            explanation = f"冠词用法：{word_info.word}是{'不可数名词' if self.grammar_rules.is_uncountable_noun(word_info.word) else '可数名词'}，应该用{correct_answer}。"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_noun_choice(word_info, grammar_topic)
    
    # 句子完成题生成方法
    def _generate_plural_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成名词复数句子完成题"""
        if word_info.part_of_speech == "noun":
            plural_form = self.grammar_rules.get_plural_form(word_info.word)
            question = f"完成句子：\nI have two _____ (提示：{word_info.chinese_meaning})"
            answer = f"I have two {plural_form}"
            hint = f"提示：two后接名词复数"
            explanation = f"句子完成：I have two {plural_form}。名词复数：{word_info.word} → {plural_form}"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_noun_completion(word_info, grammar_topic)
    
    def _generate_article_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成冠词句子完成题"""
        if word_info.part_of_speech == "noun":
            if self.grammar_rules.is_uncountable_noun(word_info.word):
                question = f"完成句子：\nI like _____ (提示：{word_info.chinese_meaning})"
                answer = f"I like {word_info.word}"
                hint = f"提示：不可数名词前不用冠词"
                explanation = f"句子完成：I like {word_info.word}。{word_info.word}是不可数名词。"
            else:
                article = "an" if word_info.word[0].lower() in 'aeiou' else "a"
                question = f"完成句子：\nThis is _____ (提示：{word_info.chinese_meaning})"
                answer = f"This is {article} {word_info.word}"
                hint = f"提示：可数名词单数前用a/an"
                explanation = f"句子完成：This is {article} {word_info.word}。冠词用法。"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_noun_completion(word_info, grammar_topic)
    
    # 基础练习题生成方法
    def _generate_basic_noun_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础名词填空题"""
        if word_info.part_of_speech == "noun":
            question = f"This is a _____.\n这是一个{word_info.chinese_meaning}。"
            hint = f"提示：{word_info.word}（{word_info.chinese_meaning}）是名词"
            explanation = f"名词用法：This is a + 名词。{word_info.word}（{word_info.chinese_meaning}）是名词。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"I like _____.\n我喜欢{word_info.chinese_meaning}。"
            hint = f"提示：{word_info.word}（{word_info.chinese_meaning}）"
            explanation = f"基础句型：I like + 词语。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_noun_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础名词翻译题"""
        if word_info.part_of_speech == "noun":
            english_sentence = f"This is a {word_info.word}."
            chinese_sentence = f"这是一个{word_info.chinese_meaning}。"
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
    
    def _generate_basic_noun_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础名词选择题"""
        options = [word_info.word, "option1", "option2", "option3"]
        random.shuffle(options)
        question_text = f"What is the English word for '{word_info.chinese_meaning}'?"
        question = self.templates.format_choice_question(question_text, options)
        hint = f"提示：{word_info.chinese_meaning}的英文单词"
        explanation = f"答案：{word_info.chinese_meaning} = {word_info.word}"
        return Exercise(question, chr(65 + options.index(word_info.word)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_noun_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础名词句子完成题"""
        if word_info.part_of_speech == "noun":
            question = f"完成句子：\nThis is a _____ (提示：{word_info.chinese_meaning})"
            answer = f"This is a {word_info.word}"
            hint = f"提示：{word_info.chinese_meaning} = {word_info.word}"
            explanation = f"句子完成：This is a {word_info.word}。{word_info.word}（{word_info.chinese_meaning}）是名词。"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"完成句子：\nI like _____ (提示：{word_info.chinese_meaning})"
            answer = f"I like {word_info.word}"
            hint = f"提示：{word_info.chinese_meaning} = {word_info.word}"
            explanation = f"句子完成：I like {word_info.word}。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)

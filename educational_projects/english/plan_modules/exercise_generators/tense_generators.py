#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时态语法生成器
处理各种英语时态的练习题生成
"""

import random
from typing import List
from .base_generator import BaseGrammarGenerator, Exercise
from .grammar_rules import GrammarRules
from .exercise_templates import ExerciseTemplates


class TenseGenerators(BaseGrammarGenerator):
    """时态语法生成器"""
    
    def __init__(self):
        super().__init__()
        self.grammar_rules = GrammarRules()
        self.templates = ExerciseTemplates()
        self.supported_grammar_topics = [
            "一般现在时-基础用法",
            "一般现在时-第三人称单数", 
            "一般现在时-否定形式",
            "一般现在时-疑问形式",
            "一般过去时-基础用法",
            "现在进行时-基础用法",
            "现在完成时-基础用法",
            "现在完成时-持续用法",
            "过去进行时-基础用法",
        ]
    
    def supports_grammar_topic(self, grammar_topic: str) -> bool:
        """检查是否支持指定的语法主题"""
        return any(topic in grammar_topic for topic in self.supported_grammar_topics)
    
    def generate_fill_blank_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成填空题"""
        if "一般现在时" in grammar_topic:
            return self._generate_present_simple_fill_blank(word_info, grammar_topic)
        elif "一般过去时" in grammar_topic:
            return self._generate_past_simple_fill_blank(word_info, grammar_topic)
        elif "现在进行时" in grammar_topic:
            return self._generate_present_continuous_fill_blank(word_info, grammar_topic)
        elif "现在完成时" in grammar_topic:
            return self._generate_present_perfect_fill_blank(word_info, grammar_topic)
        elif "过去进行时" in grammar_topic:
            return self._generate_past_continuous_fill_blank(word_info, grammar_topic)
        else:
            return self._generate_basic_fill_blank(word_info, grammar_topic)
    
    def generate_translation_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成翻译题"""
        if "一般现在时" in grammar_topic:
            return self._generate_present_simple_translation(word_info, grammar_topic)
        elif "一般过去时" in grammar_topic:
            return self._generate_past_simple_translation(word_info, grammar_topic)
        elif "现在进行时" in grammar_topic:
            return self._generate_present_continuous_translation(word_info, grammar_topic)
        elif "现在完成时" in grammar_topic:
            return self._generate_present_perfect_translation(word_info, grammar_topic)
        else:
            return self._generate_basic_translation(word_info, grammar_topic)
    
    def generate_choice_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成选择题"""
        if "一般现在时" in grammar_topic:
            return self._generate_present_simple_choice(word_info, grammar_topic)
        elif "一般过去时" in grammar_topic:
            return self._generate_past_simple_choice(word_info, grammar_topic)
        elif "现在进行时" in grammar_topic:
            return self._generate_present_continuous_choice(word_info, grammar_topic)
        elif "现在完成时" in grammar_topic:
            return self._generate_present_perfect_choice(word_info, grammar_topic)
        else:
            return self._generate_basic_choice(word_info, grammar_topic)
    
    def generate_completion_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成句子完成题"""
        if "一般现在时" in grammar_topic:
            return self._generate_present_simple_completion(word_info, grammar_topic)
        elif "一般过去时" in grammar_topic:
            return self._generate_past_simple_completion(word_info, grammar_topic)
        elif "现在进行时" in grammar_topic:
            return self._generate_present_continuous_completion(word_info, grammar_topic)
        elif "现在完成时" in grammar_topic:
            return self._generate_present_perfect_completion(word_info, grammar_topic)
        else:
            return self._generate_basic_completion(word_info, grammar_topic)
    
    # 一般现在时练习题生成
    def _generate_present_simple_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成一般现在时填空题"""
        if word_info.part_of_speech == "verb":
            if "第三人称单数" in grammar_topic:
                verb_form = self.grammar_rules.get_third_person_form(word_info.word)
                question = f"She _____ every day.\n她每天{word_info.chinese_meaning}。"
                hint = f"提示：{self.grammar_rules.get_third_person_rule(word_info.word)}"
                explanation = f"第三人称单数语法：{self.grammar_rules.get_third_person_rule(word_info.word)}。{word_info.word}的第三人称单数形式是{verb_form}。"
                return Exercise(question, verb_form, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
            elif "否定形式" in grammar_topic:
                question = f"I don't _____ every day.\n我不是每天都{word_info.chinese_meaning}。"
                hint = f"提示：否定句中动词用原形"
                explanation = f"一般现在时否定句：主语 + don't/doesn't + 动词原形。{word_info.word}（{word_info.chinese_meaning}）用原形。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
            elif "疑问形式" in grammar_topic:
                question = f"Do you _____ every day?\n你每天{word_info.chinese_meaning}吗？"
                hint = f"提示：疑问句中动词用原形"
                explanation = f"一般现在时疑问句：Do/Does + 主语 + 动词原形？{word_info.word}（{word_info.chinese_meaning}）用原形。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
            else:
                question = f"I _____ every day.\n我每天{word_info.chinese_meaning}。"
                hint = f"提示：一般现在时动词原形"
                explanation = f"一般现在时：主语 + 动词原形。{word_info.word}（{word_info.chinese_meaning}）是动词原形。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            # 非动词的一般现在时练习
            if word_info.part_of_speech == "noun":
                question = f"This is a _____.\n这是一个{word_info.chinese_meaning}。"
                hint = f"提示：一般现在时 + 名词"
                explanation = f"一般现在时句型：This is a + 名词。{word_info.word}（{word_info.chinese_meaning}）是名词。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
            elif word_info.part_of_speech == "adjective":
                question = f"I am _____ today.\n我今天很{word_info.chinese_meaning}。"
                hint = f"提示：be动词 + 形容词"
                explanation = f"一般现在时：主语 + be动词 + 形容词。{word_info.word}（{word_info.chinese_meaning}）是形容词。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
            else:
                question = f"I can _____ well.\n我能很好地{word_info.chinese_meaning}。"
                hint = f"提示：情态动词 + 动词原形"
                explanation = f"一般现在时：情态动词 + 动词原形。{word_info.word}（{word_info.chinese_meaning}）。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_past_simple_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成一般过去时填空题"""
        if word_info.part_of_speech == "verb":
            past_form = self.grammar_rules.get_past_form(word_info.word)
            question = f"I _____ yesterday.\n我昨天{word_info.chinese_meaning}了。"
            hint = f"提示：{self.grammar_rules.get_past_rule(word_info.word)}"
            explanation = f"一般过去时语法：{self.grammar_rules.get_past_rule(word_info.word)}。{word_info.word}的过去式是{past_form}。"
            return Exercise(question, past_form, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"I saw a _____ yesterday.\n我昨天看见一个{word_info.chinese_meaning}。"
            hint = f"提示：一般过去时表示过去发生的动作"
            explanation = f"一般过去时语法：表示过去发生的动作。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_present_continuous_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成现在进行时填空题"""
        if word_info.part_of_speech == "verb":
            ing_form = self.grammar_rules.get_ing_form(word_info.word)
            question = f"I am _____ now.\n我现在正在{word_info.chinese_meaning}。"
            hint = f"提示：{self.grammar_rules.get_ing_rule(word_info.word)}"
            explanation = f"现在进行时语法：be + 动词-ing形式。{self.grammar_rules.get_ing_rule(word_info.word)}。{word_info.word}的-ing形式是{ing_form}。"
            return Exercise(question, ing_form, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"I am looking at a _____.\n我正在看一个{word_info.chinese_meaning}。"
            hint = f"提示：现在进行时表示正在进行的动作"
            explanation = f"现在进行时语法：be + 动词-ing形式。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_present_perfect_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成现在完成时填空题"""
        if word_info.part_of_speech == "verb":
            if "持续用法" in grammar_topic:
                ing_form = self.grammar_rules.get_ing_form(word_info.word)
                question = f"I have been _____ for 2 hours.\n我已经{word_info.chinese_meaning}了2个小时。"
                hint = f"提示：现在完成进行时：have been + 动词-ing"
                explanation = f"现在完成进行时语法：have/has been + 动词-ing形式，表示从过去开始持续到现在的动作。{word_info.word}的-ing形式是{ing_form}。"
                return Exercise(question, ing_form, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
            else:
                past_participle = self.grammar_rules.get_past_participle(word_info.word)
                question = f"I have _____ before.\n我以前{word_info.chinese_meaning}过。"
                hint = f"提示：{self.grammar_rules.get_past_participle_rule(word_info.word)}"
                explanation = f"现在完成时语法：have/has + 过去分词。{self.grammar_rules.get_past_participle_rule(word_info.word)}。{word_info.word}的过去分词是{past_participle}。"
                return Exercise(question, past_participle, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"I have seen a _____ before.\n我以前见过一个{word_info.chinese_meaning}。"
            hint = f"提示：现在完成时表示过去的经历"
            explanation = f"现在完成时语法：have/has + 过去分词。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_past_continuous_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成过去进行时填空题"""
        if word_info.part_of_speech == "verb":
            ing_form = self.grammar_rules.get_ing_form(word_info.word)
            question = f"I was _____ yesterday evening.\n我昨天晚上正在{word_info.chinese_meaning}。"
            hint = f"提示：过去进行时：was/were + 动词-ing"
            explanation = f"过去进行时语法：was/were + 动词-ing形式，表示过去某时正在进行的动作。{word_info.word}的-ing形式是{ing_form}。"
            return Exercise(question, ing_form, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"I was looking at a _____ yesterday.\n我昨天正在看一个{word_info.chinese_meaning}。"
            hint = f"提示：过去进行时表示过去正在进行的动作"
            explanation = f"过去进行时语法：was/were + 动词-ing形式。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    # 翻译题生成方法
    def _generate_present_simple_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成一般现在时翻译题"""
        if "第三人称单数" in grammar_topic and word_info.part_of_speech == "verb":
            verb_form = self.grammar_rules.get_third_person_form(word_info.word)
            english_sentence = f"She {verb_form} every day."
            chinese_sentence = f"她每天{word_info.chinese_meaning}。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：注意第三人称单数动词变形"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}。第三人称单数：{word_info.word} → {verb_form}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            english_sentence = f"I {word_info.word} every day."
            chinese_sentence = f"我每天{word_info.chinese_meaning}。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：一般现在时表示经常性动作"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_past_simple_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成一般过去时翻译题"""
        if word_info.part_of_speech == "verb":
            past_form = self.grammar_rules.get_past_form(word_info.word)
            english_sentence = f"I {past_form} yesterday."
            chinese_sentence = f"我昨天{word_info.chinese_meaning}了。"
            question = f"中译英：{chinese_sentence}"
            hint = f"提示：一般过去时动词变过去式"
            explanation = f"翻译：{chinese_sentence} = {english_sentence}。过去式：{word_info.word} → {past_form}"
            return Exercise(question, english_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_translation(word_info, grammar_topic)
    
    def _generate_present_continuous_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成现在进行时翻译题"""
        if word_info.part_of_speech == "verb":
            ing_form = self.grammar_rules.get_ing_form(word_info.word)
            english_sentence = f"I am {ing_form} now."
            chinese_sentence = f"我现在正在{word_info.chinese_meaning}。"
            question = f"中译英：{chinese_sentence}"
            hint = f"提示：现在进行时：be + 动词-ing"
            explanation = f"翻译：{chinese_sentence} = {english_sentence}。现在进行时：{word_info.word} → {ing_form}"
            return Exercise(question, english_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_translation(word_info, grammar_topic)
    
    def _generate_present_perfect_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成现在完成时翻译题"""
        if word_info.part_of_speech == "verb":
            past_participle = self.grammar_rules.get_past_participle(word_info.word)
            english_sentence = f"I have {past_participle} before."
            chinese_sentence = f"我以前{word_info.chinese_meaning}过。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：现在完成时：have + 过去分词"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}。现在完成时：{word_info.word} → {past_participle}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_translation(word_info, grammar_topic)
    
    # 选择题生成方法
    def _generate_present_simple_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成一般现在时选择题"""
        if word_info.part_of_speech == "verb" and "第三人称单数" in grammar_topic:
            correct_answer = self.grammar_rules.get_third_person_form(word_info.word)
            options = self.templates.generate_choice_options(correct_answer, "verb", grammar_topic)
            question_text = f"She _____ every day."
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：第三人称单数动词需要变形"
            explanation = f"第三人称单数：{word_info.word} → {correct_answer}。规则：{self.grammar_rules.get_third_person_rule(word_info.word)}"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_choice(word_info, grammar_topic)
    
    def _generate_past_simple_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成一般过去时选择题"""
        if word_info.part_of_speech == "verb":
            correct_answer = self.grammar_rules.get_past_form(word_info.word)
            options = self.templates.generate_choice_options(correct_answer, "verb", grammar_topic)
            question_text = f"I _____ yesterday."
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：一般过去时动词变过去式"
            explanation = f"一般过去时：{word_info.word} → {correct_answer}。规则：{self.grammar_rules.get_past_rule(word_info.word)}"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_choice(word_info, grammar_topic)
    
    def _generate_present_continuous_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成现在进行时选择题"""
        if word_info.part_of_speech == "verb":
            correct_answer = self.grammar_rules.get_ing_form(word_info.word)
            options = self.templates.generate_choice_options(correct_answer, "verb", grammar_topic)
            question_text = f"I am _____ now."
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：现在进行时：be + 动词-ing"
            explanation = f"现在进行时：{word_info.word} → {correct_answer}。规则：{self.grammar_rules.get_ing_rule(word_info.word)}"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_choice(word_info, grammar_topic)
    
    def _generate_present_perfect_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成现在完成时选择题"""
        if word_info.part_of_speech == "verb":
            correct_answer = self.grammar_rules.get_past_participle(word_info.word)
            options = self.templates.generate_choice_options(correct_answer, "verb", grammar_topic)
            question_text = f"I have _____ before."
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：现在完成时：have + 过去分词"
            explanation = f"现在完成时：{word_info.word} → {correct_answer}。规则：{self.grammar_rules.get_past_participle_rule(word_info.word)}"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_choice(word_info, grammar_topic)
    
    # 句子完成题生成方法
    def _generate_present_simple_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成一般现在时句子完成题"""
        if word_info.part_of_speech == "verb" and "第三人称单数" in grammar_topic:
            verb_form = self.grammar_rules.get_third_person_form(word_info.word)
            question = f"完成句子：\nShe _____ (提示：{word_info.chinese_meaning})"
            answer = f"She {verb_form}"
            hint = f"提示：第三人称单数动词变形"
            explanation = f"句子完成：She {verb_form}。第三人称单数：{word_info.word} → {verb_form}"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_completion(word_info, grammar_topic)
    
    def _generate_past_simple_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成一般过去时句子完成题"""
        if word_info.part_of_speech == "verb":
            past_form = self.grammar_rules.get_past_form(word_info.word)
            question = f"完成句子：\nI _____ yesterday (提示：{word_info.chinese_meaning})"
            answer = f"I {past_form} yesterday"
            hint = f"提示：一般过去时动词变过去式"
            explanation = f"句子完成：I {past_form} yesterday。过去式：{word_info.word} → {past_form}"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_completion(word_info, grammar_topic)
    
    def _generate_present_continuous_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成现在进行时句子完成题"""
        if word_info.part_of_speech == "verb":
            ing_form = self.grammar_rules.get_ing_form(word_info.word)
            question = f"完成句子：\nI am _____ now (提示：{word_info.chinese_meaning})"
            answer = f"I am {ing_form} now"
            hint = f"提示：现在进行时：be + 动词-ing"
            explanation = f"句子完成：I am {ing_form} now。现在进行时：{word_info.word} → {ing_form}"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_completion(word_info, grammar_topic)
    
    def _generate_present_perfect_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成现在完成时句子完成题"""
        if word_info.part_of_speech == "verb":
            past_participle = self.grammar_rules.get_past_participle(word_info.word)
            question = f"完成句子：\nI have _____ before (提示：{word_info.chinese_meaning})"
            answer = f"I have {past_participle} before"
            hint = f"提示：现在完成时：have + 过去分词"
            explanation = f"句子完成：I have {past_participle} before。现在完成时：{word_info.word} → {past_participle}"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_completion(word_info, grammar_topic)
    
    # 基础练习题生成方法（作为后备）
    def _generate_basic_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础填空题"""
        question = f"I like _____.\n我喜欢{word_info.chinese_meaning}。"
        hint = f"提示：{word_info.word}（{word_info.chinese_meaning}）"
        explanation = f"基础句型：I like + 名词/动词。{word_info.word}（{word_info.chinese_meaning}）。"
        return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础翻译题"""
        question = f"英译中：I like {word_info.word}."
        answer = f"我喜欢{word_info.chinese_meaning}。"
        hint = f"提示：{word_info.word} = {word_info.chinese_meaning}"
        explanation = f"翻译：I like {word_info.word}. = 我喜欢{word_info.chinese_meaning}。"
        return Exercise(question, answer, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础选择题"""
        options = [word_info.word, "option1", "option2", "option3"]
        random.shuffle(options)
        question_text = f"What is the English word for '{word_info.chinese_meaning}'?"
        question = self.templates.format_choice_question(question_text, options)
        hint = f"提示：{word_info.chinese_meaning}的英文单词"
        explanation = f"答案：{word_info.chinese_meaning} = {word_info.word}"
        return Exercise(question, chr(65 + options.index(word_info.word)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础句子完成题"""
        question = f"完成句子：\nI like _____ (提示：{word_info.chinese_meaning})"
        answer = f"I like {word_info.word}"
        hint = f"提示：{word_info.chinese_meaning} = {word_info.word}"
        explanation = f"句子完成：I like {word_info.word}。{word_info.word}（{word_info.chinese_meaning}）。"
        return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)

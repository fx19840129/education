#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级语法生成器
处理从句、被动语态、情态动词等高级语法的练习题生成
"""

import random
from typing import List
from .base_generator import BaseGrammarGenerator, Exercise
from .grammar_rules import GrammarRules
from .exercise_templates import ExerciseTemplates


class AdvancedGenerators(BaseGrammarGenerator):
    """高级语法生成器"""
    
    def __init__(self):
        super().__init__()
        self.grammar_rules = GrammarRules()
        self.templates = ExerciseTemplates()
        self.supported_grammar_topics = [
            "被动语态-基础用法",
            "被动语态-时态变化",
            "情态动词-基础用法",
            "条件句-基础用法",
            "定语从句-基础用法",
            "定语从句-关系代词",
            "间接引语-基础用法",
            "人称代词",
        ]
    
    def supports_grammar_topic(self, grammar_topic: str) -> bool:
        """检查是否支持指定的语法主题"""
        return any(topic in grammar_topic for topic in self.supported_grammar_topics)
    
    def generate_fill_blank_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成填空题"""
        if "被动语态" in grammar_topic:
            return self._generate_passive_fill_blank(word_info, grammar_topic)
        elif "情态动词" in grammar_topic:
            return self._generate_modal_fill_blank(word_info, grammar_topic)
        elif "条件句" in grammar_topic:
            return self._generate_conditional_fill_blank(word_info, grammar_topic)
        elif "定语从句" in grammar_topic:
            return self._generate_relative_clause_fill_blank(word_info, grammar_topic)
        elif "间接引语" in grammar_topic:
            return self._generate_reported_speech_fill_blank(word_info, grammar_topic)
        elif "人称代词" in grammar_topic:
            return self._generate_pronoun_fill_blank(word_info, grammar_topic)
        else:
            return self._generate_basic_advanced_fill_blank(word_info, grammar_topic)
    
    def generate_translation_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成翻译题"""
        if "被动语态" in grammar_topic:
            return self._generate_passive_translation(word_info, grammar_topic)
        elif "情态动词" in grammar_topic:
            return self._generate_modal_translation(word_info, grammar_topic)
        elif "条件句" in grammar_topic:
            return self._generate_conditional_translation(word_info, grammar_topic)
        elif "定语从句" in grammar_topic:
            return self._generate_relative_clause_translation(word_info, grammar_topic)
        elif "间接引语" in grammar_topic:
            return self._generate_reported_speech_translation(word_info, grammar_topic)
        elif "人称代词" in grammar_topic:
            return self._generate_pronoun_translation(word_info, grammar_topic)
        else:
            return self._generate_basic_advanced_translation(word_info, grammar_topic)
    
    def generate_choice_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成选择题"""
        if "被动语态" in grammar_topic:
            return self._generate_passive_choice(word_info, grammar_topic)
        elif "情态动词" in grammar_topic:
            return self._generate_modal_choice(word_info, grammar_topic)
        elif "条件句" in grammar_topic:
            return self._generate_conditional_choice(word_info, grammar_topic)
        elif "定语从句" in grammar_topic:
            return self._generate_relative_clause_choice(word_info, grammar_topic)
        elif "间接引语" in grammar_topic:
            return self._generate_reported_speech_choice(word_info, grammar_topic)
        elif "人称代词" in grammar_topic:
            return self._generate_pronoun_choice(word_info, grammar_topic)
        else:
            return self._generate_basic_advanced_choice(word_info, grammar_topic)
    
    def generate_completion_exercise(self, word_info, grammar_topic: str) -> Exercise:
        """生成句子完成题"""
        if "被动语态" in grammar_topic:
            return self._generate_passive_completion(word_info, grammar_topic)
        elif "情态动词" in grammar_topic:
            return self._generate_modal_completion(word_info, grammar_topic)
        elif "条件句" in grammar_topic:
            return self._generate_conditional_completion(word_info, grammar_topic)
        elif "定语从句" in grammar_topic:
            return self._generate_relative_clause_completion(word_info, grammar_topic)
        elif "间接引语" in grammar_topic:
            return self._generate_reported_speech_completion(word_info, grammar_topic)
        elif "人称代词" in grammar_topic:
            return self._generate_pronoun_completion(word_info, grammar_topic)
        else:
            return self._generate_basic_advanced_completion(word_info, grammar_topic)
    
    # 被动语态练习题生成
    def _generate_passive_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成被动语态填空题"""
        if word_info.part_of_speech == "verb":
            past_participle = self.grammar_rules.get_past_participle(word_info.word)
            if "时态变化" in grammar_topic:
                # 不同时态的被动语态
                tenses = [
                    ("is", "现在时被动语态"),
                    ("was", "过去时被动语态"),
                    ("will be", "将来时被动语态"),
                    ("has been", "现在完成时被动语态")
                ]
                be_form, tense_name = random.choice(tenses)
                question = f"The book {be_form} _____ by many people.\n这本书被很多人{word_info.chinese_meaning}。"
                hint = f"提示：{tense_name}：be + 过去分词"
                explanation = f"{tense_name}：{be_form} + {past_participle}。{word_info.word}的过去分词是{past_participle}。"
            else:
                question = f"The book is _____ by many people.\n这本书被很多人{word_info.chinese_meaning}。"
                hint = f"提示：被动语态：be + 过去分词"
                explanation = f"被动语态：is + {past_participle}。{word_info.word}的过去分词是{past_participle}。"
            return Exercise(question, past_participle, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"The _____ is used by everyone.\n这个{word_info.chinese_meaning}被每个人使用。"
            hint = f"提示：被动语态的主语"
            explanation = f"被动语态语法：{grammar_topic}。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_modal_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成情态动词填空题"""
        if word_info.part_of_speech == "verb":
            modal_verb = self.grammar_rules.get_random_modal_verb()
            modal_meaning = self.grammar_rules.get_modal_meaning_chinese(modal_verb)
            question = f"You _____ {word_info.word} hard.\n你{modal_meaning}{word_info.chinese_meaning}努力。"
            hint = f"提示：情态动词表示{modal_meaning}，后接动词原形"
            explanation = f"情态动词{modal_verb}表示{modal_meaning}，后接动词原形{word_info.word}。"
            return Exercise(question, modal_verb, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"You can see a _____.\n你能看见一个{word_info.chinese_meaning}。"
            hint = f"提示：情态动词can表示能力"
            explanation = f"情态动词用法：can + 动词原形。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_conditional_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成条件句填空题"""
        if word_info.part_of_speech == "verb":
            question = f"If you _____, you will succeed.\n如果你{word_info.chinese_meaning}，你就会成功。"
            hint = "提示：条件句 If + 主语 + 动词原形, 主句用will + 动词原形"
            explanation = f"条件句中if从句用一般现在时。{word_info.word}（{word_info.chinese_meaning}）是动词原形。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        elif word_info.part_of_speech == "noun":
            question = f"If you have a _____, you will be happy.\n如果你有一个{word_info.chinese_meaning}，你会很高兴。"
            hint = "提示：条件句 If + 主语 + have + 名词"
            explanation = f"条件句中的名词。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f"If you are _____, you will succeed.\n如果你{word_info.chinese_meaning}，你会成功。"
            hint = "提示：条件句 If + 主语 + be + 形容词"
            explanation = f"条件句中的形容词。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_relative_clause_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成定语从句填空题"""
        if "关系代词" in grammar_topic:
            if word_info.part_of_speech == "noun":
                if word_info.word.lower() in ['man', 'woman', 'boy', 'girl', 'person', 'people']:
                    pronoun = "who"
                    question = f"The _____ _____ I like is very nice.\n我喜欢的那个{word_info.chinese_meaning}很好。"
                    answer = f"{word_info.word} who"
                    hint = "提示：指人用关系代词who"
                    explanation = f"定语从句：指人的名词后用who。{word_info.word}指人，所以用who。"
                else:
                    pronoun = "that"
                    question = f"The _____ _____ I like is very good.\n我喜欢的那个{word_info.chinese_meaning}很好。"
                    answer = f"{word_info.word} that"
                    hint = "提示：指物用关系代词that"
                    explanation = f"定语从句：指物的名词后用that。{word_info.word}指物，所以用that。"
                return Exercise(question, answer, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            if word_info.part_of_speech == "noun":
                question = f"The _____ that I like is very good.\n我喜欢的{word_info.chinese_meaning}很好。"
                hint = "提示：定语从句 名词 + that + 从句"
                explanation = f"定语从句修饰名词。{word_info.word}（{word_info.chinese_meaning}）是被修饰的名词。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
            elif word_info.part_of_speech == "verb":
                question = f"The book that I _____ is interesting.\n我{word_info.chinese_meaning}的书很有趣。"
                hint = "提示：定语从句中的动词"
                explanation = f"定语从句中的动词。{word_info.word}（{word_info.chinese_meaning}）。"
                return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        
        # 默认情况
        return self._generate_basic_advanced_fill_blank(word_info, grammar_topic)
    
    def _generate_reported_speech_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成间接引语填空题"""
        if word_info.part_of_speech == "verb":
            question = f'He said that he _____ every day.\n他说他每天{word_info.chinese_meaning}。'
            hint = "提示：间接引语中动词时态要变化"
            explanation = f"间接引语：He said that + 从句。从句中用{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        elif word_info.part_of_speech == "noun":
            question = f'She said she had a _____.\n她说她有一个{word_info.chinese_meaning}。'
            hint = "提示：间接引语 said + that + 从句"
            explanation = f"间接引语：She said + that从句。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            question = f'He said he was _____.\n他说他很{word_info.chinese_meaning}。'
            hint = "提示：间接引语中形容词"
            explanation = f"间接引语中的形容词。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_pronoun_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成人称代词填空题"""
        # 人称代词映射
        pronouns = {
            "I": {"chinese": "我", "example": "_____ like books.", "chinese_example": "我喜欢书。"},
            "you": {"chinese": "你", "example": "_____ are nice.", "chinese_example": "你很好。"},
            "he": {"chinese": "他", "example": "_____ is a student.", "chinese_example": "他是学生。"},
            "she": {"chinese": "她", "example": "_____ is beautiful.", "chinese_example": "她很漂亮。"},
            "it": {"chinese": "它", "example": "_____ is big.", "chinese_example": "它很大。"},
            "we": {"chinese": "我们", "example": "_____ are friends.", "chinese_example": "我们是朋友。"},
            "they": {"chinese": "他们", "example": "_____ are students.", "chinese_example": "他们是学生。"}
        }
        
        # 如果单词本身是人称代词
        if word_info.word.lower() in pronouns:
            pronoun_info = pronouns[word_info.word.lower()]
            question = f"{pronoun_info['example']}\n{pronoun_info['chinese_example']}"
            hint = f"提示：人称代词作主语，{pronoun_info['chinese']}用英语说是{word_info.word.lower()}"
            explanation = f"人称代词：{pronoun_info['chinese']} = {word_info.word.lower()}。人称代词在句子中作主语。"
            return Exercise(question, word_info.word.lower(), explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            # 随机选择一个人称代词
            pronoun = random.choice(list(pronouns.keys()))
            pronoun_info = pronouns[pronoun]
            question = f"_____ like {word_info.word}.\n{pronoun_info['chinese']}喜欢{word_info.chinese_meaning}。"
            hint = f"提示：人称代词作主语"
            explanation = f"人称代词：{pronoun_info['chinese']} = {pronoun}。{word_info.word}（{word_info.chinese_meaning}）。"
            return Exercise(question, pronoun, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    # 翻译题生成方法
    def _generate_passive_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成被动语态翻译题"""
        if word_info.part_of_speech == "verb":
            past_participle = self.grammar_rules.get_past_participle(word_info.word)
            english_sentence = f"The book is {past_participle} by many people."
            chinese_sentence = f"这本书被很多人{word_info.chinese_meaning}。"
            question = f"中译英：{chinese_sentence}"
            hint = f"提示：被动语态：be + 过去分词"
            explanation = f"翻译：{chinese_sentence} = {english_sentence}。被动语态：{word_info.word} → {past_participle}"
            return Exercise(question, english_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_translation(word_info, grammar_topic)
    
    def _generate_modal_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成情态动词翻译题"""
        if word_info.part_of_speech == "verb":
            modal_verb = "should"  # 使用固定的情态动词便于翻译
            english_sentence = f"You {modal_verb} {word_info.word} hard."
            chinese_sentence = f"你应该努力{word_info.chinese_meaning}。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：should表示建议，后接动词原形"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}。情态动词should + {word_info.word}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_translation(word_info, grammar_topic)
    
    def _generate_conditional_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成条件句翻译题"""
        if word_info.part_of_speech == "verb":
            english_sentence = f"If you {word_info.word}, you will succeed."
            chinese_sentence = f"如果你{word_info.chinese_meaning}，你就会成功。"
            question = f"中译英：{chinese_sentence}"
            hint = f"提示：条件句 If + 现在时, 主句用将来时"
            explanation = f"翻译：{chinese_sentence} = {english_sentence}。条件句结构"
            return Exercise(question, english_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_translation(word_info, grammar_topic)
    
    def _generate_relative_clause_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成定语从句翻译题"""
        if word_info.part_of_speech == "noun":
            english_sentence = f"The {word_info.word} that I like is very good."
            chinese_sentence = f"我喜欢的{word_info.chinese_meaning}很好。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：定语从句修饰名词"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}。定语从句：that I like修饰{word_info.word}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_translation(word_info, grammar_topic)
    
    def _generate_reported_speech_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成间接引语翻译题"""
        if word_info.part_of_speech == "verb":
            english_sentence = f"He said that he {word_info.word} every day."
            chinese_sentence = f"他说他每天{word_info.chinese_meaning}。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：间接引语 said that + 从句"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}。间接引语结构"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_translation(word_info, grammar_topic)
    
    def _generate_pronoun_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成人称代词翻译题"""
        pronouns = {"I": "我", "you": "你", "he": "他", "she": "她", "it": "它", "we": "我们", "they": "他们"}
        
        if word_info.word.lower() in pronouns:
            chinese_meaning = pronouns[word_info.word.lower()]
            english_sentence = f"{word_info.word} like books."
            chinese_sentence = f"{chinese_meaning}喜欢书。"
            question = f"英译中：{english_sentence}"
            hint = f"提示：{word_info.word} = {chinese_meaning}"
            explanation = f"翻译：{english_sentence} = {chinese_sentence}。人称代词：{word_info.word} = {chinese_meaning}"
            return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_translation(word_info, grammar_topic)
    
    # 选择题和完成题生成方法（简化版本，可以进一步扩展）
    def _generate_passive_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成被动语态选择题"""
        if word_info.part_of_speech == "verb":
            correct_answer = self.grammar_rules.get_past_participle(word_info.word)
            options = [correct_answer, word_info.word, f"{word_info.word}ing", f"{word_info.word}s"]
            random.shuffle(options)
            question_text = f"The book is _____ by many people."
            question = self.templates.format_choice_question(question_text, options)
            hint = f"提示：被动语态用过去分词"
            explanation = f"被动语态：is + 过去分词。{word_info.word} → {correct_answer}"
            return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_choice(word_info, grammar_topic)
    
    def _generate_modal_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成情态动词选择题"""
        options = ["can", "should", "must", "will"]
        correct_answer = "should"
        question_text = f"You _____ study hard."
        question = self.templates.format_choice_question(question_text, options)
        hint = f"提示：should表示建议"
        explanation = f"情态动词should表示建议：You should study hard."
        return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_conditional_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成条件句选择题"""
        options = ["will succeed", "succeed", "succeeded", "succeeding"]
        correct_answer = "will succeed"
        question_text = f"If you work hard, you _____."
        question = self.templates.format_choice_question(question_text, options)
        hint = f"提示：条件句主句用将来时"
        explanation = f"条件句：If从句用现在时，主句用将来时。will succeed是正确答案。"
        return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_relative_clause_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成定语从句选择题"""
        if "关系代词" in grammar_topic:
            if word_info.part_of_speech == "noun" and word_info.word.lower() in ['man', 'woman', 'boy', 'girl', 'person']:
                options = ["who", "which", "that", "where"]
                correct_answer = "who"
                question_text = f"The {word_info.word} _____ I like is very nice."
                hint = f"提示：指人用who"
            else:
                options = ["that", "who", "where", "when"]
                correct_answer = "that"
                question_text = f"The {word_info.word} _____ I like is very good."
                hint = f"提示：指物用that"
        else:
            options = ["that", "who", "where", "when"]
            correct_answer = "that"
            question_text = f"The book _____ I read is interesting."
            hint = f"提示：定语从句用that连接"
        
        question = self.templates.format_choice_question(question_text, options)
        explanation = f"定语从句关系代词：{correct_answer}用于连接主句和从句。"
        return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_reported_speech_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成间接引语选择题"""
        options = ["said that", "said", "told that", "spoke"]
        correct_answer = "said that"
        question_text = f'He _____ he was happy.'
        question = self.templates.format_choice_question(question_text, options)
        hint = f"提示：间接引语用said that"
        explanation = f"间接引语：He said that + 从句。said that是正确的连接方式。"
        return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_pronoun_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成人称代词选择题"""
        options = ["I", "you", "he", "she"]
        correct_answer = "I"
        question_text = f"_____ like books."
        question = self.templates.format_choice_question(question_text, options)
        hint = f"提示：根据语境选择合适的人称代词"
        explanation = f"人称代词作主语：I like books. 我喜欢书。"
        return Exercise(question, chr(65 + options.index(correct_answer)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    # 句子完成题生成方法（简化版本）
    def _generate_passive_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成被动语态句子完成题"""
        if word_info.part_of_speech == "verb":
            past_participle = self.grammar_rules.get_past_participle(word_info.word)
            question = f"完成句子：\nThe book is _____ by many people (提示：{word_info.chinese_meaning})"
            answer = f"The book is {past_participle} by many people"
            hint = f"提示：被动语态用过去分词"
            explanation = f"句子完成：The book is {past_participle} by many people。被动语态：{word_info.word} → {past_participle}"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_completion(word_info, grammar_topic)
    
    def _generate_modal_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成情态动词句子完成题"""
        if word_info.part_of_speech == "verb":
            question = f"完成句子：\nYou should _____ hard (提示：{word_info.chinese_meaning})"
            answer = f"You should {word_info.word} hard"
            hint = f"提示：情态动词后接动词原形"
            explanation = f"句子完成：You should {word_info.word} hard。情态动词should + 动词原形"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_completion(word_info, grammar_topic)
    
    def _generate_conditional_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成条件句句子完成题"""
        if word_info.part_of_speech == "verb":
            question = f"完成句子：\nIf you _____, you will succeed (提示：{word_info.chinese_meaning})"
            answer = f"If you {word_info.word}, you will succeed"
            hint = f"提示：条件句If从句用现在时"
            explanation = f"句子完成：If you {word_info.word}, you will succeed。条件句结构"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_completion(word_info, grammar_topic)
    
    def _generate_relative_clause_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成定语从句句子完成题"""
        if word_info.part_of_speech == "noun":
            question = f"完成句子：\nThe _____ that I like is very good (提示：{word_info.chinese_meaning})"
            answer = f"The {word_info.word} that I like is very good"
            hint = f"提示：定语从句修饰名词"
            explanation = f"句子完成：The {word_info.word} that I like is very good。定语从句结构"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_completion(word_info, grammar_topic)
    
    def _generate_reported_speech_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成间接引语句子完成题"""
        if word_info.part_of_speech == "verb":
            question = f"完成句子：\nHe said that he _____ every day (提示：{word_info.chinese_meaning})"
            answer = f"He said that he {word_info.word} every day"
            hint = f"提示：间接引语 said that + 从句"
            explanation = f"句子完成：He said that he {word_info.word} every day。间接引语结构"
            return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
        else:
            return self._generate_basic_advanced_completion(word_info, grammar_topic)
    
    def _generate_pronoun_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成人称代词句子完成题"""
        question = f"完成句子：\n_____ like books (提示：我)"
        answer = f"I like books"
        hint = f"提示：我 = I"
        explanation = f"句子完成：I like books。人称代词：我 = I"
        return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    # 基础练习题生成方法
    def _generate_basic_advanced_fill_blank(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础高级语法填空题"""
        question = f"I like _____.\n我喜欢{word_info.chinese_meaning}。"
        hint = f"提示：{word_info.word}（{word_info.chinese_meaning}）"
        explanation = f"基础句型：I like + 词语。{word_info.word}（{word_info.chinese_meaning}）。"
        return Exercise(question, word_info.word, explanation, hint, "fill_blank", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_advanced_translation(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础高级语法翻译题"""
        english_sentence = f"I like {word_info.word}."
        chinese_sentence = f"我喜欢{word_info.chinese_meaning}。"
        question = f"英译中：{english_sentence}"
        hint = f"提示：{word_info.word} = {word_info.chinese_meaning}"
        explanation = f"翻译：{english_sentence} = {chinese_sentence}"
        return Exercise(question, chinese_sentence, explanation, hint, "translation", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_advanced_choice(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础高级语法选择题"""
        options = [word_info.word, "option1", "option2", "option3"]
        random.shuffle(options)
        question_text = f"What is the English word for '{word_info.chinese_meaning}'?"
        question = self.templates.format_choice_question(question_text, options)
        hint = f"提示：{word_info.chinese_meaning}的英文单词"
        explanation = f"答案：{word_info.chinese_meaning} = {word_info.word}"
        return Exercise(question, chr(65 + options.index(word_info.word)), explanation, hint, "choice", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)
    
    def _generate_basic_advanced_completion(self, word_info, grammar_topic: str) -> Exercise:
        """生成基础高级语法句子完成题"""
        question = f"完成句子：\nI like _____ (提示：{word_info.chinese_meaning})"
        answer = f"I like {word_info.word}"
        hint = f"提示：{word_info.chinese_meaning} = {word_info.word}"
        explanation = f"句子完成：I like {word_info.word}。{word_info.word}（{word_info.chinese_meaning}）。"
        return Exercise(question, answer, explanation, hint, "completion", self.get_difficulty_level(grammar_topic), grammar_topic, word_info.word)

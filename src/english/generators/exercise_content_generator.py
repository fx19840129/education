#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语练习题生成器
基于通用框架的英语学科特定实现
"""

import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# 添加共享框架路径
import sys
import os

from src.shared.learning_framework.generation.base_exercise_generator import (
    BaseExerciseGenerator, Exercise, GenerationRequest, GenerationResult,
    ExerciseType, DifficultyLevel
)


class EnglishExerciseGenerator(BaseExerciseGenerator):
    """英语练习题生成器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("english", config)
        
        # 英语特定的词汇数据
        self.vocabulary = {
            "beginner": {
                "nouns": ["book", "cat", "dog", "house", "car", "tree", "water", "food", "friend", "family"],
                "verbs": ["go", "come", "see", "eat", "drink", "play", "work", "study", "read", "write"],
                "adjectives": ["big", "small", "good", "bad", "happy", "sad", "hot", "cold", "new", "old"],
                "adverbs": ["very", "always", "never", "often", "sometimes", "here", "there", "now", "then", "today"]
            },
            "intermediate": {
                "nouns": ["information", "education", "development", "government", "environment", "technology", "communication", "relationship", "opportunity", "responsibility"],
                "verbs": ["achieve", "develop", "establish", "maintain", "improve", "analyze", "evaluate", "demonstrate", "participate", "contribute"],
                "adjectives": ["significant", "important", "effective", "efficient", "appropriate", "necessary", "sufficient", "available", "reliable", "flexible"],
                "adverbs": ["significantly", "effectively", "efficiently", "appropriately", "necessarily", "sufficiently", "reliably", "flexibly", "consequently", "therefore"]
            },
            "advanced": {
                "nouns": ["philosophy", "psychology", "sociology", "anthropology", "archaeology", "meteorology", "astronomy", "biotechnology", "nanotechnology", "cryptocurrency"],
                "verbs": ["synthesize", "hypothesize", "theorize", "conceptualize", "institutionalize", "revolutionize", "modernize", "optimize", "maximize", "minimize"],
                "adjectives": ["sophisticated", "comprehensive", "multifaceted", "interdisciplinary", "paradigmatic", "epistemological", "methodological", "theoretical", "empirical", "analytical"],
                "adverbs": ["sophisticatedly", "comprehensively", "multifacetedly", "interdisciplinarily", "paradigmatically", "epistemologically", "methodologically", "theoretically", "empirically", "analytically"]
            }
        }
        
        # 英语语法规则
        self.grammar_rules = {
            "一般现在时": {
                "structure": "主语 + 动词原形/第三人称单数",
                "examples": ["I work", "He works", "They work"],
                "time_markers": ["every day", "usually", "often", "sometimes", "always", "never"]
            },
            "一般过去时": {
                "structure": "主语 + 动词过去式",
                "examples": ["I worked", "He worked", "They worked"],
                "time_markers": ["yesterday", "last week", "ago", "before", "then"]
            },
            "现在进行时": {
                "structure": "主语 + be + 动词-ing",
                "examples": ["I am working", "He is working", "They are working"],
                "time_markers": ["now", "at the moment", "currently", "right now"]
            },
            "现在完成时": {
                "structure": "主语 + have/has + 过去分词",
                "examples": ["I have worked", "He has worked", "They have worked"],
                "time_markers": ["already", "just", "ever", "never", "yet", "since", "for"]
            },
            "被动语态": {
                "structure": "主语 + be + 过去分词 + (by + 动作执行者)",
                "examples": ["The book is written", "The house was built", "The work has been done"],
                "time_markers": []
            },
            "情态动词": {
                "structure": "主语 + 情态动词 + 动词原形",
                "examples": ["I can work", "He must work", "They should work"],
                "time_markers": []
            }
        }
    
    def _init_templates(self):
        """初始化学科特定的模板"""
        self.exercise_templates = {
            "multiple_choice_grammar": {
                "pattern": "Choose the correct form: {sentence_with_blank}",
                "options_count": 4,
                "difficulty_levels": ["beginner", "intermediate", "advanced"]
            },
            "fill_blank_tense": {
                "pattern": "Complete the sentence with the correct tense: {sentence_with_blank}",
                "options_count": 1,
                "difficulty_levels": ["beginner", "intermediate", "advanced"]
            },
            "translation_sentence": {
                "pattern": "Translate the following sentence: {chinese_sentence}",
                "options_count": 1,
                "difficulty_levels": ["beginner", "intermediate", "advanced"]
            },
            "sentence_completion": {
                "pattern": "Complete the sentence: {incomplete_sentence}",
                "options_count": 1,
                "difficulty_levels": ["intermediate", "advanced"]
            },
            "matching_words": {
                "pattern": "Match the words with their meanings:",
                "options_count": 5,
                "difficulty_levels": ["beginner", "intermediate"]
            },
            "true_false_grammar": {
                "pattern": "True or False: {statement}",
                "options_count": 2,
                "difficulty_levels": ["beginner", "intermediate"]
            },
            "essay_topic": {
                "pattern": "Write an essay about: {topic}",
                "options_count": 0,
                "difficulty_levels": ["advanced", "expert"]
            }
        }
    
    def _init_difficulty_settings(self):
        """初始化学科特定的难度设置"""
        self.difficulty_settings = {
            DifficultyLevel.BEGINNER: {
                "vocabulary_level": "beginner",
                "grammar_complexity": "basic",
                "sentence_length": (5, 15),
                "concepts": ["basic_tense", "simple_sentences", "common_words"]
            },
            DifficultyLevel.INTERMEDIATE: {
                "vocabulary_level": "intermediate",
                "grammar_complexity": "moderate",
                "sentence_length": (10, 25),
                "concepts": ["complex_tense", "compound_sentences", "academic_words"]
            },
            DifficultyLevel.ADVANCED: {
                "vocabulary_level": "advanced",
                "grammar_complexity": "complex",
                "sentence_length": (15, 35),
                "concepts": ["advanced_tense", "complex_sentences", "specialized_words"]
            },
            DifficultyLevel.EXPERT: {
                "vocabulary_level": "advanced",
                "grammar_complexity": "expert",
                "sentence_length": (20, 50),
                "concepts": ["expert_tense", "sophisticated_sentences", "professional_words"]
            }
        }
    
    def _generate_single_exercise(self, topic: str, exercise_type: ExerciseType, 
                                 difficulty: DifficultyLevel, content: Optional[Dict[str, Any]] = None,
                                 constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成单个英语练习题"""
        
        # 根据题型生成不同的练习题
        if exercise_type == ExerciseType.MULTIPLE_CHOICE:
            return self._generate_multiple_choice(topic, difficulty, content, constraints)
        elif exercise_type == ExerciseType.FILL_BLANK:
            return self._generate_fill_blank(topic, difficulty, content, constraints)
        elif exercise_type == ExerciseType.TRANSLATION:
            return self._generate_translation(topic, difficulty, content, constraints)
        elif exercise_type == ExerciseType.SENTENCE_COMPLETION:
            return self._generate_sentence_completion(topic, difficulty, content, constraints)
        elif exercise_type == ExerciseType.MATCHING:
            return self._generate_matching(topic, difficulty, content, constraints)
        elif exercise_type == ExerciseType.TRUE_FALSE:
            return self._generate_true_false(topic, difficulty, content, constraints)
        elif exercise_type == ExerciseType.ESSAY:
            return self._generate_essay(topic, difficulty, content, constraints)
        else:
            return None
    
    def _generate_multiple_choice(self, topic: str, difficulty: DifficultyLevel, 
                                 content: Optional[Dict[str, Any]] = None,
                                 constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成选择题"""
        settings = self._get_difficulty_settings(difficulty)
        vocab_level = settings["vocabulary_level"]
        
        # 根据主题选择词汇和语法
        if "语法" in topic or "grammar" in topic.lower():
            return self._generate_grammar_multiple_choice(topic, difficulty, vocab_level)
        elif "词汇" in topic or "vocabulary" in topic.lower():
            return self._generate_vocabulary_multiple_choice(topic, difficulty, vocab_level)
        else:
            return self._generate_general_multiple_choice(topic, difficulty, vocab_level)
    
    def _generate_grammar_multiple_choice(self, topic: str, difficulty: DifficultyLevel, vocab_level: str) -> Exercise:
        """生成语法选择题"""
        # 选择语法规则
        grammar_rule = random.choice(list(self.grammar_rules.keys()))
        rule_info = self.grammar_rules[grammar_rule]
        
        # 生成句子
        sentence = self._generate_grammar_sentence(grammar_rule, vocab_level)
        
        # 生成选项
        correct_answer = self._get_correct_grammar_form(sentence, grammar_rule)
        wrong_answers = self._generate_wrong_grammar_forms(sentence, grammar_rule, 3)
        
        options = [correct_answer] + wrong_answers
        random.shuffle(options)
        
        question = f"Choose the correct form: {sentence.replace('_____', '_____')}"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.MULTIPLE_CHOICE),
            question_type=ExerciseType.MULTIPLE_CHOICE,
            question=question,
            correct_answer=correct_answer,
            options=options,
            difficulty=difficulty,
            topic=topic,
            explanation=f"This question tests {grammar_rule}. The correct answer follows the rule: {rule_info['structure']}"
        )
    
    def _generate_vocabulary_multiple_choice(self, topic: str, difficulty: DifficultyLevel, vocab_level: str) -> Exercise:
        """生成词汇选择题"""
        vocab = self.vocabulary[vocab_level]
        word_type = random.choice(["nouns", "verbs", "adjectives", "adverbs"])
        words = vocab[word_type]
        
        target_word = random.choice(words)
        correct_meaning = self._get_word_meaning(target_word, word_type)
        
        # 生成错误选项
        wrong_meanings = []
        for _ in range(3):
            wrong_word = random.choice([w for w in words if w != target_word])
            wrong_meanings.append(self._get_word_meaning(wrong_word, word_type))
        
        options = [correct_meaning] + wrong_meanings
        random.shuffle(options)
        
        question = f"What does '{target_word}' mean?"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.MULTIPLE_CHOICE),
            question_type=ExerciseType.MULTIPLE_CHOICE,
            question=question,
            correct_answer=correct_meaning,
            options=options,
            difficulty=difficulty,
            topic=topic,
            explanation=f"'{target_word}' is a {word_type[:-1]} that means '{correct_meaning}'"
        )
    
    def _generate_general_multiple_choice(self, topic: str, difficulty: DifficultyLevel, vocab_level: str) -> Exercise:
        """生成通用选择题"""
        vocab = self.vocabulary[vocab_level]
        
        # 生成句子
        sentence = self._generate_random_sentence(vocab_level)
        
        # 生成选项
        correct_answer = "Option A"  # 简化示例
        options = ["Option A", "Option B", "Option C", "Option D"]
        
        question = f"Complete the sentence: {sentence}"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.MULTIPLE_CHOICE),
            question_type=ExerciseType.MULTIPLE_CHOICE,
            question=question,
            correct_answer=correct_answer,
            options=options,
            difficulty=difficulty,
            topic=topic
        )
    
    def _generate_fill_blank(self, topic: str, difficulty: DifficultyLevel, 
                            content: Optional[Dict[str, Any]] = None,
                            constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成填空题"""
        settings = self._get_difficulty_settings(difficulty)
        vocab_level = settings["vocabulary_level"]
        
        # 生成句子和空白
        sentence = self._generate_sentence_with_blank(vocab_level)
        correct_answer = self._get_blank_answer(sentence)
        
        question = f"Fill in the blank: {sentence}"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.FILL_BLANK),
            question_type=ExerciseType.FILL_BLANK,
            question=question,
            correct_answer=correct_answer,
            difficulty=difficulty,
            topic=topic,
            explanation=f"The correct answer is '{correct_answer}'"
        )
    
    def _generate_translation(self, topic: str, difficulty: DifficultyLevel, 
                             content: Optional[Dict[str, Any]] = None,
                             constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成翻译题"""
        settings = self._get_difficulty_settings(difficulty)
        vocab_level = settings["vocabulary_level"]
        
        # 生成中文句子
        chinese_sentence = self._generate_chinese_sentence(vocab_level)
        english_translation = self._get_english_translation(chinese_sentence)
        
        question = f"Translate the following sentence: {chinese_sentence}"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.TRANSLATION),
            question_type=ExerciseType.TRANSLATION,
            question=question,
            correct_answer=english_translation,
            difficulty=difficulty,
            topic=topic,
            explanation=f"The English translation is: '{english_translation}'"
        )
    
    def _generate_sentence_completion(self, topic: str, difficulty: DifficultyLevel, 
                                     content: Optional[Dict[str, Any]] = None,
                                     constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成句子完成题"""
        settings = self._get_difficulty_settings(difficulty)
        vocab_level = settings["vocabulary_level"]
        
        # 生成不完整句子
        incomplete_sentence = self._generate_incomplete_sentence(vocab_level)
        completion = self._get_sentence_completion(incomplete_sentence)
        
        question = f"Complete the sentence: {incomplete_sentence}"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.SENTENCE_COMPLETION),
            question_type=ExerciseType.SENTENCE_COMPLETION,
            question=question,
            correct_answer=completion,
            difficulty=difficulty,
            topic=topic,
            explanation=f"The completion is: '{completion}'"
        )
    
    def _generate_matching(self, topic: str, difficulty: DifficultyLevel, 
                          content: Optional[Dict[str, Any]] = None,
                          constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成匹配题"""
        settings = self._get_difficulty_settings(difficulty)
        vocab_level = settings["vocabulary_level"]
        
        # 生成词汇对
        word_pairs = self._generate_word_pairs(vocab_level, 5)
        
        question = "Match the words with their meanings:"
        correct_answer = self._format_matching_answer(word_pairs)
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.MATCHING),
            question_type=ExerciseType.MATCHING,
            question=question,
            correct_answer=correct_answer,
            difficulty=difficulty,
            topic=topic,
            explanation="Match each word with its correct meaning"
        )
    
    def _generate_true_false(self, topic: str, difficulty: DifficultyLevel, 
                            content: Optional[Dict[str, Any]] = None,
                            constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成判断题"""
        settings = self._get_difficulty_settings(difficulty)
        vocab_level = settings["vocabulary_level"]
        
        # 生成陈述句
        statement = self._generate_statement(vocab_level)
        is_true = random.choice([True, False])
        
        if not is_true:
            statement = self._make_statement_false(statement)
        
        question = f"True or False: {statement}"
        correct_answer = "True" if is_true else "False"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.TRUE_FALSE),
            question_type=ExerciseType.TRUE_FALSE,
            question=question,
            correct_answer=correct_answer,
            options=["True", "False"],
            difficulty=difficulty,
            topic=topic,
            explanation=f"This statement is {'true' if is_true else 'false'}"
        )
    
    def _generate_essay(self, topic: str, difficulty: DifficultyLevel, 
                       content: Optional[Dict[str, Any]] = None,
                       constraints: Optional[Dict[str, Any]] = None) -> Optional[Exercise]:
        """生成论述题"""
        essay_topic = self._generate_essay_topic(topic, difficulty)
        
        question = f"Write an essay about: {essay_topic}"
        correct_answer = f"Write a {difficulty.value}-level essay about {essay_topic}"
        
        return Exercise(
            exercise_id=self._generate_exercise_id(topic, ExerciseType.ESSAY),
            question_type=ExerciseType.ESSAY,
            question=question,
            correct_answer=correct_answer,
            difficulty=difficulty,
            topic=topic,
            explanation=f"Write a comprehensive essay about {essay_topic}"
        )
    
    # 辅助方法
    def _generate_grammar_sentence(self, grammar_rule: str, vocab_level: str) -> str:
        """生成语法句子"""
        vocab = self.vocabulary[vocab_level]
        
        if grammar_rule == "一般现在时":
            subject = random.choice(["I", "You", "He", "She", "We", "They"])
            verb = random.choice(vocab["verbs"])
            if subject in ["He", "She"]:
                verb = self._get_third_person_singular(verb)
            return f"{subject} {verb} every day."
        elif grammar_rule == "一般过去时":
            subject = random.choice(["I", "You", "He", "She", "We", "They"])
            verb = random.choice(vocab["verbs"])
            past_verb = self._get_past_tense(verb)
            return f"{subject} {past_verb} yesterday."
        elif grammar_rule == "现在进行时":
            subject = random.choice(["I", "You", "He", "She", "We", "They"])
            verb = random.choice(vocab["verbs"])
            be_verb = self._get_be_verb(subject)
            ing_verb = self._get_ing_form(verb)
            return f"{subject} {be_verb} {ing_verb} now."
        else:
            return f"This is a {grammar_rule} sentence."
    
    def _get_correct_grammar_form(self, sentence: str, grammar_rule: str) -> str:
        """获取正确的语法形式"""
        # 简化实现
        return "Correct form"
    
    def _generate_wrong_grammar_forms(self, sentence: str, grammar_rule: str, count: int) -> List[str]:
        """生成错误的语法形式"""
        return [f"Wrong form {i+1}" for i in range(count)]
    
    def _get_word_meaning(self, word: str, word_type: str) -> str:
        """获取单词含义"""
        meanings = {
            "book": "a written work",
            "cat": "a small furry animal",
            "dog": "a domestic animal",
            "house": "a building for living",
            "car": "a vehicle for transportation"
        }
        return meanings.get(word, f"meaning of {word}")
    
    def _generate_random_sentence(self, vocab_level: str) -> str:
        """生成随机句子"""
        vocab = self.vocabulary[vocab_level]
        subject = random.choice(["I", "You", "He", "She", "We", "They"])
        verb = random.choice(vocab["verbs"])
        noun = random.choice(vocab["nouns"])
        return f"{subject} {verb} a {noun}."
    
    def _generate_sentence_with_blank(self, vocab_level: str) -> str:
        """生成带空白的句子"""
        sentence = self._generate_random_sentence(vocab_level)
        words = sentence.split()
        blank_index = random.randint(0, len(words) - 1)
        words[blank_index] = "_____"
        return " ".join(words)
    
    def _get_blank_answer(self, sentence: str) -> str:
        """获取空白答案"""
        return "answer"
    
    def _generate_chinese_sentence(self, vocab_level: str) -> str:
        """生成中文句子"""
        chinese_sentences = {
            "beginner": ["我每天工作。", "他喜欢读书。", "我们在学校学习。"],
            "intermediate": ["教育是社会发展的重要基础。", "技术改变了我们的生活方式。"],
            "advanced": ["哲学思考帮助我们理解世界的本质。", "跨学科研究促进了知识的创新。"]
        }
        return random.choice(chinese_sentences.get(vocab_level, chinese_sentences["beginner"]))
    
    def _get_english_translation(self, chinese_sentence: str) -> str:
        """获取英文翻译"""
        translations = {
            "我每天工作。": "I work every day.",
            "他喜欢读书。": "He likes reading books.",
            "我们在学校学习。": "We study at school.",
            "教育是社会发展的重要基础。": "Education is an important foundation for social development.",
            "技术改变了我们的生活方式。": "Technology has changed our way of life.",
            "哲学思考帮助我们理解世界的本质。": "Philosophical thinking helps us understand the nature of the world.",
            "跨学科研究促进了知识的创新。": "Interdisciplinary research promotes knowledge innovation."
        }
        return translations.get(chinese_sentence, "Translation not available")
    
    def _generate_incomplete_sentence(self, vocab_level: str) -> str:
        """生成不完整句子"""
        incomplete_sentences = {
            "beginner": ["I like to _____", "He goes to _____", "We have a _____"],
            "intermediate": ["Education is important for _____", "Technology helps us _____"],
            "advanced": ["Philosophy explores the nature of _____", "Research contributes to _____"]
        }
        return random.choice(incomplete_sentences.get(vocab_level, incomplete_sentences["beginner"]))
    
    def _get_sentence_completion(self, incomplete_sentence: str) -> str:
        """获取句子完成"""
        completions = {
            "I like to _____": "read books",
            "He goes to _____": "school",
            "We have a _____": "meeting",
            "Education is important for _____": "personal development",
            "Technology helps us _____": "solve problems",
            "Philosophy explores the nature of _____": "existence",
            "Research contributes to _____": "knowledge advancement"
        }
        return completions.get(incomplete_sentence, "completion")
    
    def _generate_word_pairs(self, vocab_level: str, count: int) -> List[tuple]:
        """生成词汇对"""
        vocab = self.vocabulary[vocab_level]
        pairs = []
        
        for word_type in ["nouns", "verbs", "adjectives"]:
            words = vocab[word_type][:count]
            for word in words:
                meaning = self._get_word_meaning(word, word_type)
                pairs.append((word, meaning))
        
        return pairs[:count]
    
    def _format_matching_answer(self, word_pairs: List[tuple]) -> str:
        """格式化匹配答案"""
        return " | ".join([f"{word}: {meaning}" for word, meaning in word_pairs])
    
    def _generate_statement(self, vocab_level: str) -> str:
        """生成陈述句"""
        statements = {
            "beginner": ["Cats are animals.", "Books contain information.", "Water is essential for life."],
            "intermediate": ["Education improves society.", "Technology advances rapidly.", "Research requires methodology."],
            "advanced": ["Philosophy examines fundamental questions.", "Interdisciplinary approaches enhance understanding."]
        }
        return random.choice(statements.get(vocab_level, statements["beginner"]))
    
    def _make_statement_false(self, statement: str) -> str:
        """使陈述句变为错误"""
        false_statements = {
            "Cats are animals.": "Cats are plants.",
            "Books contain information.": "Books contain nothing.",
            "Water is essential for life.": "Water is harmful to life.",
            "Education improves society.": "Education harms society.",
            "Technology advances rapidly.": "Technology never changes.",
            "Research requires methodology.": "Research needs no method.",
            "Philosophy examines fundamental questions.": "Philosophy ignores all questions.",
            "Interdisciplinary approaches enhance understanding.": "Interdisciplinary approaches confuse understanding."
        }
        return false_statements.get(statement, f"Not {statement}")
    
    def _generate_essay_topic(self, topic: str, difficulty: DifficultyLevel) -> str:
        """生成论述题主题"""
        essay_topics = {
            DifficultyLevel.BEGINNER: ["My favorite hobby", "My family", "My school"],
            DifficultyLevel.INTERMEDIATE: ["The importance of education", "Technology in daily life", "Environmental protection"],
            DifficultyLevel.ADVANCED: ["The role of philosophy in modern society", "Interdisciplinary research methods", "The future of artificial intelligence"],
            DifficultyLevel.EXPERT: ["Epistemological foundations of scientific knowledge", "The intersection of technology and ethics", "Global challenges and solutions"]
        }
        return random.choice(essay_topics.get(difficulty, essay_topics[DifficultyLevel.INTERMEDIATE]))
    
    def _get_third_person_singular(self, verb: str) -> str:
        """获取第三人称单数形式"""
        if verb.endswith('y'):
            return verb[:-1] + 'ies'
        elif verb.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return verb + 'es'
        else:
            return verb + 's'
    
    def _get_past_tense(self, verb: str) -> str:
        """获取过去时形式"""
        irregular_past = {
            'go': 'went', 'see': 'saw', 'do': 'did', 'have': 'had',
            'make': 'made', 'take': 'took', 'come': 'came', 'give': 'gave'
        }
        return irregular_past.get(verb, verb + 'ed')
    
    def _get_be_verb(self, subject: str) -> str:
        """获取be动词"""
        be_verbs = {
            'I': 'am', 'You': 'are', 'He': 'is', 'She': 'is',
            'We': 'are', 'They': 'are'
        }
        return be_verbs.get(subject, 'is')
    
    def _get_ing_form(self, verb: str) -> str:
        """获取ing形式"""
        if verb.endswith('e'):
            return verb[:-1] + 'ing'
        elif verb.endswith(('ie')):
            return verb[:-2] + 'ying'
        elif len(verb) > 2 and verb[-1] in 'bcdfghjklmnpqrstvwxyz' and verb[-2] in 'aeiou':
            return verb + verb[-1] + 'ing'
        else:
            return verb + 'ing'
    
    def generate_daily_exercises(self, words: List[Any], grammar_topic: str, count: int) -> List[Dict[str, Any]]:
        """生成每日练习题"""
        exercises = []
        
        # 根据语法主题和单词生成练习题
        for i in range(count):
            # 随机选择练习类型
            exercise_type = random.choice(list(ExerciseType))
            
            # 根据难度级别生成练习
            difficulty = random.choice([DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED])
            
            try:
                exercise = self._generate_single_exercise(
                    topic=grammar_topic,
                    exercise_type=exercise_type,
                    difficulty=difficulty
                )
                
                if exercise:
                    exercises.append({
                        "type": exercise.question_type.value,
                        "question": exercise.question,
                        "options": exercise.options,
                        "correct_answer": exercise.correct_answer,
                        "explanation": exercise.explanation,
                        "difficulty": exercise.difficulty.value
                    })
            except Exception as e:
                print(f"⚠️ 生成练习题失败: {e}")
                continue
        
        return exercises

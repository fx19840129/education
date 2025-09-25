#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单词学习练习生成器
生成多种类型的单词学习练习题
"""

import random
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from word_database import WordInfo


@dataclass
class Exercise:
    """练习题数据类"""
    question: str
    options: List[str] = None
    correct_answer: str = ""
    explanation: str = ""
    exercise_type: str = ""
    difficulty: str = "easy"
    word: str = ""


class WordExerciseGenerator:
    """单词练习生成器"""
    
    def __init__(self, word_database):
        self.word_database = word_database
        self.exercise_types = [
            "multiple_choice_meaning",
            "multiple_choice_word",
            "fill_in_blank",
            "matching",
            "spelling",
            "pronunciation",
            "sentence_completion",
            "synonym_antonym",
            "word_formation",
            "translation"
        ]
    
    def generate_exercises(self, words: List[WordInfo], count: int = 30, 
                         difficulty: str = "easy", exercise_types: List[str] = None) -> List[Exercise]:
        """生成练习题"""
        if exercise_types is None:
            exercise_types = self.exercise_types
        
        exercises = []
        random.seed()
        
        for i in range(count):
            word = random.choice(words)
            exercise_type = random.choice(exercise_types)
            
            try:
                if exercise_type == "multiple_choice_meaning":
                    exercise = self._generate_multiple_choice_meaning(word, words)
                elif exercise_type == "multiple_choice_word":
                    exercise = self._generate_multiple_choice_word(word, words)
                elif exercise_type == "fill_in_blank":
                    exercise = self._generate_fill_in_blank(word)
                elif exercise_type == "matching":
                    exercise = self._generate_matching(word, words)
                elif exercise_type == "spelling":
                    exercise = self._generate_spelling(word)
                elif exercise_type == "pronunciation":
                    exercise = self._generate_pronunciation(word)
                elif exercise_type == "sentence_completion":
                    exercise = self._generate_sentence_completion(word)
                elif exercise_type == "synonym_antonym":
                    exercise = self._generate_synonym_antonym(word)
                elif exercise_type == "word_formation":
                    exercise = self._generate_word_formation(word)
                elif exercise_type == "translation":
                    exercise = self._generate_translation(word)
                else:
                    continue
                
                if exercise:
                    exercises.append(exercise)
            except Exception as e:
                print(f"生成练习题失败: {e}")
                continue
        
        return exercises
    
    def _generate_multiple_choice_meaning(self, word: WordInfo, all_words: List[WordInfo]) -> Exercise:
        """生成选择题（选择词义）"""
        # 生成错误选项
        wrong_words = [w for w in all_words if w.word != word.word]
        wrong_options = random.sample(wrong_words, min(3, len(wrong_words)))
        
        options = [word.chinese_meaning] + [w.chinese_meaning for w in wrong_options]
        random.shuffle(options)
        
        return Exercise(
            question=f"单词 '{word.word}' 的中文意思是：",
            options=options,
            correct_answer=word.chinese_meaning,
            explanation=f"'{word.word}' 的中文意思是 '{word.chinese_meaning}'。",
            exercise_type="multiple_choice_meaning",
            difficulty=word.difficulty,
            word=word.word
        )
    
    def _generate_multiple_choice_word(self, word: WordInfo, all_words: List[WordInfo]) -> Exercise:
        """生成选择题（选择单词）"""
        # 生成错误选项
        wrong_words = [w for w in all_words if w.word != word.word]
        wrong_options = random.sample(wrong_words, min(3, len(wrong_words)))
        
        options = [word.word] + [w.word for w in wrong_options]
        random.shuffle(options)
        
        return Exercise(
            question=f"下列哪个单词的中文意思是 '{word.chinese_meaning}'：",
            options=options,
            correct_answer=word.word,
            explanation=f"中文意思是 '{word.chinese_meaning}' 的单词是 '{word.word}'。",
            exercise_type="multiple_choice_word",
            difficulty=word.difficulty,
            word=word.word
        )
    
    def _generate_fill_in_blank(self, word: WordInfo) -> Exercise:
        """生成填空题"""
        sentence = word.example_sentence
        # 将单词替换为空白
        blank_sentence = sentence.replace(word.word, "_____")
        
        return Exercise(
            question=f"根据中文意思填空：{word.chinese_meaning}\n{blank_sentence}",
            correct_answer=word.word,
            explanation=f"根据中文意思 '{word.chinese_meaning}'，应该填入 '{word.word}'。",
            exercise_type="fill_in_blank",
            difficulty=word.difficulty,
            word=word.word
        )
    
    def _generate_matching(self, word: WordInfo, all_words: List[WordInfo]) -> Exercise:
        """生成匹配题"""
        # 选择3-4个相关单词
        related_words = random.sample(all_words, min(4, len(all_words)))
        if word not in related_words:
            related_words[0] = word
        
        words_list = [w.word for w in related_words]
        meanings_list = [w.chinese_meaning for w in related_words]
        
        # 打乱顺序
        random.shuffle(meanings_list)
        
        question = "请将下列单词与对应的中文意思匹配：\n"
        question += f"单词：{', '.join(words_list)}\n"
        question += f"中文：{', '.join(meanings_list)}"
        
        # 正确答案
        correct_pairs = []
        for w in related_words:
            correct_pairs.append(f"{w.word} - {w.chinese_meaning}")
        
        return Exercise(
            question=question,
            correct_answer="\n".join(correct_pairs),
            explanation="匹配题需要将单词与对应的中文意思正确配对。",
            exercise_type="matching",
            difficulty=word.difficulty,
            word=word.word
        )
    
    def _generate_spelling(self, word: WordInfo) -> Exercise:
        """生成拼写题"""
        # 将单词的字母打乱
        letters = list(word.word)
        random.shuffle(letters)
        scrambled = "".join(letters)
        
        return Exercise(
            question=f"请正确拼写这个单词（字母已打乱）：{scrambled}",
            correct_answer=word.word,
            explanation=f"正确拼写是 '{word.word}'。",
            exercise_type="spelling",
            difficulty=word.difficulty,
            word=word.word
        )
    
    def _generate_pronunciation(self, word: WordInfo) -> Exercise:
        """生成发音题"""
        if not word.pronunciation:
            return None
        
        return Exercise(
            question=f"单词 '{word.word}' 的正确发音是：",
            correct_answer=word.pronunciation,
            explanation=f"'{word.word}' 的发音是 {word.pronunciation}。",
            exercise_type="pronunciation",
            difficulty=word.difficulty,
            word=word.word
        )
    
    def _generate_sentence_completion(self, word: WordInfo) -> Exercise:
        """生成句子完成题"""
        sentence = word.example_sentence
        # 将单词替换为空白
        blank_sentence = sentence.replace(word.word, "_____")
        
        return Exercise(
            question=f"完成句子：{blank_sentence}",
            correct_answer=word.word,
            explanation=f"根据句子意思，应该填入 '{word.word}'。",
            exercise_type="sentence_completion",
            difficulty=word.difficulty,
            word=word.word
        )
    
    def _generate_synonym_antonym(self, word: WordInfo) -> Exercise:
        """生成同义词/反义词题"""
        if not word.synonyms and not word.antonyms:
            return None
        
        if word.synonyms:
            synonym = random.choice(word.synonyms)
            return Exercise(
                question=f"单词 '{word.word}' 的同义词是：",
                correct_answer=synonym,
                explanation=f"'{word.word}' 的同义词是 '{synonym}'。",
                exercise_type="synonym_antonym",
                difficulty=word.difficulty,
                word=word.word
            )
        elif word.antonyms:
            antonym = random.choice(word.antonyms)
            return Exercise(
                question=f"单词 '{word.word}' 的反义词是：",
                correct_answer=antonym,
                explanation=f"'{word.word}' 的反义词是 '{antonym}'。",
                exercise_type="synonym_antonym",
                difficulty=word.difficulty,
                word=word.word
            )
    
    def _generate_word_formation(self, word: WordInfo) -> Exercise:
        """生成词形变化题"""
        if word.part_of_speech == "noun":
            return Exercise(
                question=f"将 '{word.word}' 变为复数形式：",
                correct_answer=f"{word.word}s",
                explanation=f"名词 '{word.word}' 的复数形式是 '{word.word}s'。",
                exercise_type="word_formation",
                difficulty=word.difficulty,
                word=word.word
            )
        elif word.part_of_speech == "verb":
            return Exercise(
                question=f"将 '{word.word}' 变为过去式：",
                correct_answer=f"{word.word}ed",
                explanation=f"动词 '{word.word}' 的过去式是 '{word.word}ed'。",
                exercise_type="word_formation",
                difficulty=word.difficulty,
                word=word.word
            )
        elif word.part_of_speech == "adjective":
            return Exercise(
                question=f"将 '{word.word}' 变为比较级：",
                correct_answer=f"more {word.word}",
                explanation=f"形容词 '{word.word}' 的比较级是 'more {word.word}'。",
                exercise_type="word_formation",
                difficulty=word.difficulty,
                word=word.word
            )
        else:
            return None
    
    def _generate_translation(self, word: WordInfo) -> Exercise:
        """生成翻译题"""
        return Exercise(
            question=f"请将 '{word.word}' 翻译成中文：",
            correct_answer=word.chinese_meaning,
            explanation=f"'{word.word}' 的中文翻译是 '{word.chinese_meaning}'。",
            exercise_type="translation",
            difficulty=word.difficulty,
            word=word.word
        )
    
    def get_exercise_type_name(self, exercise_type: str) -> str:
        """获取题型中文名称"""
        type_names = {
            "multiple_choice_meaning": "选择题（词义）",
            "multiple_choice_word": "选择题（单词）",
            "fill_in_blank": "填空题",
            "matching": "匹配题",
            "spelling": "拼写题",
            "pronunciation": "发音题",
            "sentence_completion": "句子完成题",
            "synonym_antonym": "同义词/反义词题",
            "word_formation": "词形变化题",
            "translation": "翻译题"
        }
        return type_names.get(exercise_type, exercise_type)
    
    def get_difficulty_name(self, difficulty: str) -> str:
        """获取难度中文名称"""
        difficulty_names = {
            "easy": "简单",
            "medium": "中等",
            "hard": "困难"
        }
        return difficulty_names.get(difficulty, difficulty)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词库标准化处理器
将下载的词库转换为系统统一格式，补充缺失字段
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from zhipu_ai_client import ai_client, AIResponse

@dataclass
class StandardWordEntry:
    """标准化单词条目"""
    word: str
    pronunciation: str
    part_of_speech: str
    chinese_meaning: str
    english_meaning: str
    example_sentence: str
    difficulty: str
    grade_level: str
    category: str
    frequency_rank: int = 0
    synonyms: List[str] = None
    antonyms: List[str] = None
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []
        if self.antonyms is None:
            self.antonyms = []

class VocabularyProcessor:
    """词库处理器"""
    
    def __init__(self, data_dir: str = "vocabulary_data"):
        self.data_dir = data_dir
        self.ai_client = ai_client
        
        # 词性标准化映射
        self.pos_mapping = {
            "n": "noun", "noun": "noun",
            "v": "verb", "verb": "verb", 
            "adj": "adjective", "adjective": "adjective",
            "adv": "adverb", "adverb": "adverb",
            "prep": "preposition", "preposition": "preposition",
            "pron": "pronoun", "pronoun": "pronoun",
            "conj": "conjunction", "conjunction": "conjunction",
            "interj": "interjection", "interjection": "interjection",
            "art": "article", "article": "article",
            "num": "numeral", "numeral": "numeral",
            "det": "determiner", "determiner": "determiner"
        }
        
        # 难度级别映射
        self.difficulty_mapping = {
            "elementary_1_2": "easy",
            "elementary_3_4": "easy", 
            "elementary_5_6": "medium",
            "middle_school_7": "medium",
            "middle_school_8": "medium",
            "middle_school_9": "hard"
        }
    
    def load_raw_vocabulary(self, filename: str) -> List[Dict[str, Any]]:
        """加载原始词库数据"""
        file_path = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"加载了 {len(data)} 个词汇条目")
                return data
        except Exception as e:
            print(f"加载词库失败: {e}")
            return []
    
    def standardize_part_of_speech(self, pos: str) -> str:
        """标准化词性"""
        pos = pos.lower().strip()
        return self.pos_mapping.get(pos, pos)
    
    def enhance_word_with_ai(self, word_data: Dict[str, Any]) -> StandardWordEntry:
        """使用AI增强单词信息"""
        word = word_data.get("word", "")
        
        # 检查是否需要AI增强
        missing_fields = []
        if not word_data.get("pronunciation"):
            missing_fields.append("pronunciation")
        if not word_data.get("english_meaning"):
            missing_fields.append("english_meaning")
        if not word_data.get("example_sentence") or word_data.get("example_sentence") == f"This is a {word}.":
            missing_fields.append("example_sentence")
        
        enhanced_data = word_data.copy()
        
        if missing_fields:
            print(f"正在AI增强单词: {word} (缺失: {', '.join(missing_fields)})")
            
            # 构建AI提示
            prompt = f"""请为英语单词 "{word}" 补充以下信息：
单词：{word}
中文含义：{word_data.get('chinese_meaning', '')}
词性：{word_data.get('part_of_speech', '')}

请按以下格式提供信息：
音标：[国际音标]
英文释义：[简洁的英文解释]
例句：[包含该单词的英语例句]
中文翻译：[例句的中文翻译]"""
            
            try:
                response = self.ai_client.generate_content(
                    prompt=prompt,
                    system_prompt="你是一个专业的英语词典编辑，请提供准确、简洁的词汇信息。",
                    temperature=0.3
                )
                
                if response.success:
                    content = response.content
                    
                    # 解析AI响应
                    if "pronunciation" in missing_fields:
                        pronunciation_match = re.search(r'音标[：:]\s*(.+)', content)
                        if pronunciation_match:
                            enhanced_data["pronunciation"] = pronunciation_match.group(1).strip()
                    
                    if "english_meaning" in missing_fields:
                        meaning_match = re.search(r'英文释义[：:]\s*(.+)', content)
                        if meaning_match:
                            enhanced_data["english_meaning"] = meaning_match.group(1).strip()
                    
                    if "example_sentence" in missing_fields:
                        sentence_match = re.search(r'例句[：:]\s*(.+)', content)
                        if sentence_match:
                            enhanced_data["example_sentence"] = sentence_match.group(1).strip()
                
            except Exception as e:
                print(f"AI增强失败 {word}: {e}")
        
        # 设置默认值
        if not enhanced_data.get("pronunciation"):
            enhanced_data["pronunciation"] = f"/{word}/"
        
        if not enhanced_data.get("english_meaning"):
            enhanced_data["english_meaning"] = f"The English word '{word}'"
        
        if not enhanced_data.get("example_sentence") or enhanced_data.get("example_sentence") == f"This is a {word}.":
            # 根据词性生成合适的例句
            pos = enhanced_data.get("part_of_speech", "")
            if pos == "noun":
                enhanced_data["example_sentence"] = f"I can see a {word}."
            elif pos == "verb":
                enhanced_data["example_sentence"] = f"I {word} every day."
            elif pos == "adjective":
                enhanced_data["example_sentence"] = f"This is {word}."
            else:
                enhanced_data["example_sentence"] = f"The word '{word}' is important."
        
        # 创建标准化条目
        entry = StandardWordEntry(
            word=enhanced_data.get("word", ""),
            pronunciation=enhanced_data.get("pronunciation", ""),
            part_of_speech=self.standardize_part_of_speech(enhanced_data.get("part_of_speech", "")),
            chinese_meaning=enhanced_data.get("chinese_meaning", ""),
            english_meaning=enhanced_data.get("english_meaning", ""),
            example_sentence=enhanced_data.get("example_sentence", ""),
            difficulty=self.difficulty_mapping.get(
                enhanced_data.get("grade_level", ""), 
                enhanced_data.get("difficulty", "medium")
            ),
            grade_level=enhanced_data.get("grade_level", ""),
            category=enhanced_data.get("category", "general")
        )
        
        return entry
    
    def process_vocabulary_batch(self, vocabulary_data: List[Dict[str, Any]], 
                               batch_size: int = 5) -> List[StandardWordEntry]:
        """批量处理词汇数据"""
        processed_entries = []
        total = len(vocabulary_data)
        
        print(f"开始处理 {total} 个词汇条目...")
        
        for i in range(0, total, batch_size):
            batch = vocabulary_data[i:i+batch_size]
            print(f"处理批次 {i//batch_size + 1}/{(total-1)//batch_size + 1}")
            
            for word_data in batch:
                try:
                    entry = self.enhance_word_with_ai(word_data)
                    processed_entries.append(entry)
                except Exception as e:
                    print(f"处理失败 {word_data.get('word', 'unknown')}: {e}")
                    # 创建基础条目
                    entry = StandardWordEntry(
                        word=word_data.get("word", ""),
                        pronunciation=word_data.get("pronunciation", f"/{word_data.get('word', '')}/"),
                        part_of_speech=self.standardize_part_of_speech(word_data.get("part_of_speech", "")),
                        chinese_meaning=word_data.get("chinese_meaning", ""),
                        english_meaning=word_data.get("english_meaning", f"The word '{word_data.get('word', '')}'"),
                        example_sentence=word_data.get("example_sentence", f"This is {word_data.get('word', '')}."),
                        difficulty=word_data.get("difficulty", "medium"),
                        grade_level=word_data.get("grade_level", ""),
                        category=word_data.get("category", "general")
                    )
                    processed_entries.append(entry)
            
            # 短暂休息避免API限流
            import time
            time.sleep(1)
        
        print(f"处理完成，共 {len(processed_entries)} 个条目")
        return processed_entries
    
    def save_processed_vocabulary(self, entries: List[StandardWordEntry], 
                                filename: str):
        """保存处理后的词汇"""
        data = [asdict(entry) for entry in entries]
        
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'word_configs')
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"处理后的词汇保存到: {file_path}")
    
    def validate_vocabulary(self, entries: List[StandardWordEntry]) -> Dict[str, Any]:
        """验证词汇质量"""
        stats = {
            "total_words": len(entries),
            "has_pronunciation": 0,
            "has_english_meaning": 0,
            "has_example_sentence": 0,
            "pos_distribution": {},
            "difficulty_distribution": {},
            "grade_distribution": {}
        }
        
        for entry in entries:
            # 统计完整性
            if entry.pronunciation and entry.pronunciation != f"/{entry.word}/":
                stats["has_pronunciation"] += 1
            
            if entry.english_meaning and entry.english_meaning != f"The English word '{entry.word}'":
                stats["has_english_meaning"] += 1
            
            if entry.example_sentence and not entry.example_sentence.startswith("This is"):
                stats["has_example_sentence"] += 1
            
            # 统计分布
            pos = entry.part_of_speech
            stats["pos_distribution"][pos] = stats["pos_distribution"].get(pos, 0) + 1
            
            difficulty = entry.difficulty
            stats["difficulty_distribution"][difficulty] = stats["difficulty_distribution"].get(difficulty, 0) + 1
            
            grade = entry.grade_level
            stats["grade_distribution"][grade] = stats["grade_distribution"].get(grade, 0) + 1
        
        return stats
    
    def process_all_vocabularies(self):
        """处理所有词汇库"""
        print("开始标准化处理词库...")
        
        # 处理小学词汇
        print("\n=== 处理小学词汇 ===")
        elementary_data = self.load_raw_vocabulary("elementary_words_enhanced.json")
        if elementary_data:
            elementary_entries = self.process_vocabulary_batch(elementary_data, batch_size=3)
            self.save_processed_vocabulary(elementary_entries, "elementary_words_processed.json")
            
            # 验证质量
            stats = self.validate_vocabulary(elementary_entries)
            print("小学词汇质量统计:")
            print(f"  总词汇: {stats['total_words']}")
            print(f"  有音标: {stats['has_pronunciation']}")
            print(f"  有英文释义: {stats['has_english_meaning']}")
            print(f"  有例句: {stats['has_example_sentence']}")
            print(f"  词性分布: {stats['pos_distribution']}")
        
        # 处理初中词汇
        print("\n=== 处理初中词汇 ===")
        middle_data = self.load_raw_vocabulary("middle_school_words_enhanced.json")
        if middle_data:
            middle_entries = self.process_vocabulary_batch(middle_data, batch_size=3)
            self.save_processed_vocabulary(middle_entries, "middle_school_words_processed.json")
            
            # 验证质量
            stats = self.validate_vocabulary(middle_entries)
            print("初中词汇质量统计:")
            print(f"  总词汇: {stats['total_words']}")
            print(f"  有音标: {stats['has_pronunciation']}")
            print(f"  有英文释义: {stats['has_english_meaning']}")
            print(f"  有例句: {stats['has_example_sentence']}")
            print(f"  词性分布: {stats['pos_distribution']}")
        
        print("\n词库标准化处理完成！")

if __name__ == "__main__":
    processor = VocabularyProcessor()
    processor.process_all_vocabularies()

#!/usr/bin/env python3
"""
英语学习内容生成器 - 主入口
调用位于 src/english/ 目录下的各种内容生成脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入学习内容生成器
from src.english.learning_content_generator import LearningContentGenerator

def main():
    """主函数"""
    print("🎓 英语学习内容生成器")
    print("=" * 50)
    
    # 创建生成器实例
    generator = LearningContentGenerator()
    
    # 显示主菜单
    while True:
        print("\n📚 请选择要生成的内容类型：")
        print("1. 生成学习计划")
        print("2. 生成每日单词")
        print("3. 生成词法内容")
        print("4. 生成句法内容")
        print("5. 生成练习句子")
        print("6. 生成练习题")
        print("7. 生成完整学习文档 (包含所有内容)")
        print("8. 查看学习计划")
        print("9. 退出")
        
        choice = input("\n请输入选择 (1-9): ").strip()
        
        if choice == "1":
            # 调用学习计划生成脚本
            import subprocess
            subprocess.run([sys.executable, "english_learning_plan_standalone.py"])
            
        elif choice == "2":
            # 调用每日单词生成脚本
            from src.english.generate_daily_words import DailyWordsGenerator
            word_generator = DailyWordsGenerator()
            word_generator.generate_and_display()
            
        elif choice == "3":
            # 调用词法内容生成脚本
            from src.english.generate_morphology_content import MorphologyContentGenerator
            morph_generator = MorphologyContentGenerator()
            morph_generator.generate_and_display()
            
        elif choice == "4":
            # 调用句法内容生成脚本
            from src.english.generate_syntax_content import SyntaxContentGenerator
            syntax_generator = SyntaxContentGenerator()
            syntax_generator.generate_and_display()
            
        elif choice == "5":
            # 调用练习句子生成脚本
            from src.english.generate_practice_sentences import PracticeSentencesGenerator
            sentence_generator = PracticeSentencesGenerator()
            sentence_generator.generate_and_display()
            
        elif choice == "6":
            # 调用练习题生成脚本
            from src.english.generate_practice_exercises import PracticeExercisesGenerator
            exercise_generator = PracticeExercisesGenerator()
            exercise_generator.generate_and_display()
            
        elif choice == "7":
            # 调用完整学习文档生成脚本
            from src.english.generate_daily_learning_document import DailyLearningDocumentGenerator
            doc_generator = DailyLearningDocumentGenerator()
            doc_generator.generate_and_display()
            
        elif choice == "8":
            # 调用学习计划查看脚本
            from src.english.read_learning_plan import LearningPlanReader
            reader = LearningPlanReader()
            reader.interactive_mode()
            
        elif choice == "9":
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()

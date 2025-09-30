#!/usr/bin/env python3
"""
英语学科实现
包含英语学习的所有功能配置和特定实现
"""

import subprocess
import sys
from pathlib import Path
from typing import List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.subject_base import SubjectBase, SubjectFunction

class EnglishSubject(SubjectBase):
    """英语学科实现"""
    
    def get_name(self) -> str:
        return "english"
    
    def get_display_name(self) -> str:
        return "🇺🇸 英语学习"
    
    def get_description(self) -> str:
        return "英语词汇、语法、练习等学习内容"
    
    def initialize_functions(self) -> List[SubjectFunction]:
        """初始化英语学科功能"""
        return [
            SubjectFunction(
                name="create_plan",
                display_name="📋 创建学习计划",
                description="生成个性化的学习计划和FSRS模板",
                script_path="src/english/core/create_learning_plan.py",
                function_type="script"
            ),
            SubjectFunction(
                name="manage_plan",
                display_name="🗂️  管理学习计划",
                description="查看、搜索、删除、导出已有计划",
                script_path="src/english/core/manage_learning_plan.py",
                function_type="script"
            ),
            SubjectFunction(
                name="generate_content",
                display_name="📚 生成学习内容",
                description="基于计划生成词汇、语法、练习等内容",
                function_type="menu"
            ),
            SubjectFunction(
                name="fsrs_generator",
                display_name="🛠️  FSRS模板生成器",
                description="独立的FSRS学习模板生成工具",
                script_path="src/english/core/generate_fsrs_template.py",
                function_type="script"
            ),
            SubjectFunction(
                name="view_progress",
                display_name="📊 查看学习进度",
                description="查看学习数据和进度统计",
                function_type="builtin"
            ),
            SubjectFunction(
                name="settings",
                display_name="⚙️  系统设置",
                description="AI模型配置、参数调整等",
                function_type="builtin"
            )
        ]
    
    def _show_menu(self, function_name: str, **kwargs) -> str:
        """显示英语学科的自定义菜单"""
        if function_name == "generate_content":
            return self._show_content_generators_menu()
        
        return super()._show_menu(function_name, **kwargs)
    
    def _show_content_generators_menu(self) -> str:
        """显示内容生成器菜单"""
        content_generators = [
            ("daily_words", "📅 生成每日词汇", "src/english/content_generators/generate_vocabulary_content.py"),
            ("grammar", "🔤 生成语法内容", "src/english/content_generators/generate_grammar_content.py"),
            ("exercises", "💪 生成练习题", "src/english/content_generators/generate_practice_exercises.py"),
            ("sentences", "✍️ 生成练习句子", "src/english/content_generators/generate_practice_sentences.py"),
            ("daily_content", "📚 生成日常学习内容", "src/english/content_generators/generate_daily_learning_doc.py"),
            ("batch_all", "🎯 批量生成所有内容", None)
        ]
        
        while True:
            print(f"\n📚 {self.display_name} - 学习内容生成")
            print("=" * 60)
            
            for i, (_, display_name, _) in enumerate(content_generators, 1):
                print(f"{i}. {display_name}")
            
            print(f"{len(content_generators) + 1}. 🔙 返回功能选择")
            print("=" * 60)
            
            try:
                choice = input(f"请选择 (1-{len(content_generators) + 1}): ").strip()
                choice_index = int(choice) - 1
                
                if choice_index == len(content_generators):
                    return "continue"
                
                if 0 <= choice_index < len(content_generators):
                    generator_name, display_name, script_path = content_generators[choice_index]
                    
                    if generator_name == "batch_all":
                        self._run_batch_content_generation(content_generators[:-1])
                    else:
                        self._run_script(script_path)
                else:
                    print("❌ 无效选择，请重试")
                    input("\n按Enter键继续...")
            
            except ValueError:
                print("❌ 请输入有效数字")
                input("\n按Enter键继续...")
            except KeyboardInterrupt:
                print("\n\n⚠️  返回功能选择...")
                return "continue"
    
    def _run_batch_content_generation(self, generators: List[tuple]):
        """批量生成所有内容"""
        print(f"\n🎯 批量生成 {self.display_name} 学习内容...")
        print("-" * 50)
        
        success_count = 0
        total_count = len(generators)
        
        for i, (_, display_name, script_path) in enumerate(generators, 1):
            generator_name = Path(script_path).stem if script_path else "unknown"
            print(f"\n[{i}/{total_count}] 运行 {display_name}...")
            
            script_full_path = self.project_root / script_path
            if not script_full_path.exists():
                print(f"❌ 脚本文件不存在: {script_full_path}")
                continue
            
            try:
                result = subprocess.run(
                    [sys.executable, str(script_full_path)],
                    cwd=str(self.project_root),
                    check=False,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"✅ {display_name} 生成完成")
                    success_count += 1
                else:
                    print(f"❌ {display_name} 生成失败 (返回码: {result.returncode})")
                    if result.stderr:
                        print(f"   错误信息: {result.stderr[:200]}...")
            
            except KeyboardInterrupt:
                print(f"\n\n⚠️  用户中断批量生成")
                break
            except Exception as e:
                print(f"❌ 运行 {display_name} 时出错: {e}")
        
        print(f"\n📊 批量生成完成: {success_count}/{total_count} 个生成器成功")
        input("\n按Enter键继续...")
    
    def _run_builtin(self, function_name: str, **kwargs) -> str:
        """运行英语学科的内置功能"""
        if function_name == "view_progress":
            return self._show_progress_viewer()
        elif function_name == "settings":
            return self._show_system_settings()
        elif function_name == "back":
            return "back"
        elif function_name == "exit":
            return "exit"
        
        return super()._run_builtin(function_name, **kwargs)
    
    def _show_progress_viewer(self) -> str:
        """显示学习进度查看器"""
        print(f"\n📊 {self.display_name} - 学习进度查看")
        print("=" * 60)
        print("🚧 学习进度查看功能正在开发中...")
        print("📈 将来会显示:")
        print("   • 学习天数和完成情况")
        print("   • 词汇掌握进度")
        print("   • 练习完成统计")
        print("   • FSRS复习数据")
        print("   • 学习效率分析")
        print("=" * 60)
        input("\n按Enter键继续...")
        return "continue"
    
    def _show_system_settings(self) -> str:
        """显示系统设置"""
        print(f"\n⚙️  系统设置")
        print("=" * 60)
        print("🚧 系统设置功能正在开发中...")
        print("🔧 将来会包括:")
        print("   • AI模型配置 (OpenAI, 智谱, DeepSeek等)")
        print("   • 学习参数调整")
        print("   • 输出路径设置")
        print("   • 缓存管理")
        print("   • 数据备份与恢复")
        print("=" * 60)
        input("\n按Enter键继续...")
        return "continue"

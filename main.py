#!/usr/bin/env python3
"""
多学科学习系统 - 主入口脚本

这是整个多学科学习系统的主入口点。
基于模块化架构，支持多个学科的统一管理。

当前支持的学科：
- 🇺🇸 英语学习 (完整功能)
- 🇨🇳 中文学习 (开发中)
- 🔢 数学学习 (开发中)

使用方法：
    python main.py
    
或者直接运行：
    ./main.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.core.subject_manager import SubjectManager
except ImportError as e:
    print(f"❌ 导入学科管理器失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)

def print_main_banner():
    """打印主横幅"""
    print("=" * 80)
    print("🎓 多学科智能学习系统")
    print("📚 Multi-Subject Intelligent Learning System")
    print("=" * 80)
    print("🚀 基于AI的个性化多学科学习内容生成平台")
    print()
    print("✨ 核心特性:")
    print("   🧠 FSRS算法驱动的间隔重复学习")
    print("   🎯 AI生成的个性化学习内容")
    print("   📋 多样化练习题和学习材料")
    print("   📄 专业格式的文档输出")
    print("   ⚡ 高效经济的GPT-4o-mini模型")
    print("   🏗️ 模块化的多学科架构")
    print("=" * 80)

def run_subject_system():
    """运行学科系统"""
    print("\n🚀 启动学科管理系统...")
    
    try:
        # 初始化学科管理器
        subject_manager = SubjectManager(project_root)
        
        while True:
            # 显示学科选择菜单
            subject_names = subject_manager.display_subjects_menu()
            
            if not subject_names:
                print("❌ 没有可用的学科")
                break
            
            # 获取用户选择
            try:
                choice = input(f"\n请选择学科 (1-{len(subject_names) + 1}): ").strip()
                choice_num = int(choice)
                
                # 退出选项
                if choice_num == len(subject_names) + 1:
                    print("\n👋 感谢使用多学科学习系统！")
                    break
                
                # 学科选择
                if 1 <= choice_num <= len(subject_names):
                    subject_name = subject_names[choice_num - 1]
                    subject = subject_manager.get_subject(subject_name)
                    
                    if subject:
                        run_subject_functions(subject)
                    else:
                        print(f"❌ 学科 {subject_name} 不可用")
                else:
                    print(f"❌ 请输入1到{len(subject_names) + 1}之间的数字")
                    
            except ValueError:
                print("❌ 请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出系统")
                break
                
    except Exception as e:
        print(f"❌ 学科系统运行错误: {e}")

def run_subject_functions(subject):
    """运行学科功能"""
    while True:
        try:
            # 显示功能菜单
            function_map = subject.display_functions_menu()
            
            # 获取用户选择
            choice = input(f"\n请选择功能 (1-{len(function_map)}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(function_map):
                function_name, function_type = function_map[choice_num - 1]
                
                # 执行功能
                result = subject.execute_function(function_name)
                
                # 处理执行结果
                if result == "back":
                    break  # 返回学科选择
                elif result == "exit":
                    return "exit"  # 退出整个系统
                # "continue" 或其他结果继续循环
                
            else:
                print(f"❌ 请输入1到{len(function_map)}之间的数字")
                
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n⚠️ 用户中断操作")
            break
        except Exception as e:
            print(f"❌ 执行功能时出错: {e}")
            input("\n按Enter键继续...")

def show_system_info():
    """显示系统信息"""
    print("\n💻 系统信息")
    print("=" * 50)
    
    # 项目基本信息
    print("📁 项目信息:")
    print(f"   🏠 根目录: {project_root}")
    print(f"   📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 学科状态
    try:
        subject_manager = SubjectManager(project_root)
        available_subjects = subject_manager.get_available_subjects()
        all_subjects = subject_manager.get_all_subjects()
        
        print(f"\n📚 学科状态:")
        print(f"   ✅ 可用学科: {len(available_subjects)}个")
        print(f"   🚧 开发中学科: {len(all_subjects) - len(available_subjects)}个")
        print(f"   📊 总学科数: {len(all_subjects)}个")
        
        print(f"\n📖 学科详情:")
        for subject in all_subjects:
            status = "✅ 可用" if subject.is_available() else "🚧 开发中"
            enabled_funcs = len(subject.get_enabled_functions())
            total_funcs = len(subject.functions)
            print(f"   {subject.display_name}: {status} ({enabled_funcs}/{total_funcs}个功能)")
            
    except Exception as e:
        print(f"   ❌ 获取学科信息失败: {e}")
    
    # 检查关键目录
    print(f"\n📂 目录结构:")
    key_dirs = [
        ("src/", "源代码目录"),
        ("src/subjects/", "学科模块目录"),
        ("src/core/", "核心框架目录"),
        ("outputs/", "输出文件目录"),
        ("learning_data/", "学习数据目录")
    ]
    
    for dir_path, description in key_dirs:
        full_path = project_root / dir_path
        status = "✅ 存在" if full_path.exists() else "❌ 缺失"
        print(f"   {dir_path:<20} {description:<15} {status}")
    
    # 技术栈信息
    print(f"\n🔧 技术栈:")
    print(f"   🐍 Python: {sys.version.split()[0]}")
    print(f"   🤖 AI模型: GPT-4o-mini (OpenAI)")
    print(f"   🧠 学习算法: FSRS (Free Spaced Repetition Scheduler)")
    print(f"   🏗️ 架构模式: 模块化多学科系统")
    print(f"   📄 文档格式: Microsoft Word (.docx)")
    print(f"   💾 数据格式: JSON")

def show_usage_guide():
    """显示使用指南"""
    print(f"\n📖 使用指南:")
    print(f"   1️⃣ 学科选择:")
    print(f"      → 系统会显示所有可用的学科")
    print(f"      → 选择您要学习的学科")
    print(f"   ")
    print(f"   2️⃣ 功能使用:")
    print(f"      → 每个学科都有独立的功能菜单")
    print(f"      → 根据需要选择相应的功能")
    print(f"   ")
    print(f"   3️⃣ 英语学科 (完整功能):")
    print(f"      → 创建学习计划: 生成FSRS学习模板")
    print(f"      → 管理学习计划: 查看、导出、删除计划")
    print(f"   ")
    print(f"   4️⃣ 其他学科 (开发中):")
    print(f"      → 中文学科: 古诗词、阅读、写作")
    print(f"      → 数学学科: 公式、几何、习题")

def get_main_menu_choice():
    """获取主菜单选择"""
    print("\n🎯 请选择系统模式:")
    print("   1. 🏗️  多学科系统 (推荐)")
    print("      - 使用模块化架构")
    print("      - 支持多个学科")
    print("      - 统一的用户界面")
    print()
    print("   2. ℹ️  系统信息")
    print("      - 查看系统状态")
    print("      - 学科模块信息")
    print("      - 使用指南")
    print()
    print("   3. 🚪 退出系统")
    
    while True:
        choice = input("\n请输入选择 (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("❌ 无效选择，请输入 1-3")

def main():
    """主函数"""
    print_main_banner()
    
    while True:
        choice = get_main_menu_choice()
        
        if choice == '1':
            result = run_subject_system()
            if result == "exit":
                break
        elif choice == '2':
            show_system_info()
            show_usage_guide()
        elif choice == '3':
            print("\n👋 感谢使用多学科智能学习系统！")
            print("🎓 祝您学习愉快，进步飞速！")
            break
        
        # 询问是否继续
        if choice in ['1', '2']:
            print(f"\n" + "=" * 60)
            continue_choice = input("是否返回主菜单？(y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', '是', '继续']:
                print("\n👋 感谢使用多学科智能学习系统！")
                print("🎓 祝您学习愉快，进步飞速！")
                break

if __name__ == "__main__":
    main()

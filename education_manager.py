#!/usr/bin/env python3
"""
教育管理系统主入口（重构版）
提供学科选择和功能选择的统一界面
支持多学科的学习计划创建、管理和内容生成
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.subject_manager import SubjectManager

class EducationManager:
    """教育管理系统主类（重构版）"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        print("🔄 正在加载学科模块...")
        self.subject_manager = SubjectManager(self.project_root)
        print(f"✅ 学科模块加载完成")
    
    def display_welcome(self):
        """显示欢迎界面"""
        print("\n" + "=" * 70)
        print("🎓 教育管理系统")
        print("=" * 70)
        print("📚 多学科学习计划创建、管理和内容生成平台")
        print("🚀 支持个性化学习路径规划和智能内容生成")
        print("=" * 70)
    
    def run(self):
        """运行主程序"""
        try:
            while True:
                # 显示欢迎界面和学科选择
                self.display_welcome()
                available_subject_names = self.subject_manager.display_subjects_menu()
                
                # 获取用户选择
                try:
                    choice = input(f"\n请选择 (1-{len(available_subject_names) + 1}): ").strip()
                    choice_index = int(choice) - 1
                    
                    # 退出系统
                    if choice_index == len(available_subject_names):
                        print("\n👋 感谢使用教育管理系统！")
                        break
                    
                    # 检查选择是否有效
                    if choice_index < 0 or choice_index >= len(available_subject_names):
                        print("❌ 无效选择，请重试")
                        input("\n按Enter键继续...")
                        continue
                    
                    # 获取选择的学科
                    selected_subject_name = available_subject_names[choice_index]
                    selected_subject = self.subject_manager.get_subject(selected_subject_name)
                    
                    if not selected_subject:
                        print(f"❌ 学科不存在: {selected_subject_name}")
                        input("\n按Enter键继续...")
                        continue
                    
                    # 学科功能循环
                    while True:
                        # 显示学科功能菜单
                        function_map = selected_subject.display_functions_menu()
                        
                        # 获取功能选择
                        try:
                            func_choice = input(f"\n请选择功能 (1-{len(function_map)}): ").strip()
                            func_index = int(func_choice) - 1
                            
                            if func_index < 0 or func_index >= len(function_map):
                                print("❌ 无效选择，请重试")
                                input("\n按Enter键继续...")
                                continue
                            
                            # 执行选择的功能
                            function_name, function_type = function_map[func_index]
                            result = selected_subject.execute_function(function_name)
                            
                            if result == "back":
                                break  # 返回学科选择
                            elif result == "exit":
                                print("\n👋 感谢使用教育管理系统！")
                                return
                        
                        except ValueError:
                            print("❌ 请输入有效数字")
                            input("\n按Enter键继续...")
                        except KeyboardInterrupt:
                            print("\n\n⚠️  用户中断，返回学科选择...")
                            break
                
                except ValueError:
                    print("❌ 请输入有效数字")
                    input("\n按Enter键继续...")
                except KeyboardInterrupt:
                    print("\n\n👋 感谢使用教育管理系统！")
                    break
        
        except Exception as e:
            print(f"\n❌ 系统运行时出错: {e}")
            print("请联系开发者解决问题")
        
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用教育管理系统！")

def main():
    """主程序入口"""
    manager = EducationManager()
    manager.run()

if __name__ == "__main__":
    main()

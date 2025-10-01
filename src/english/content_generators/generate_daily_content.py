#!/usr/bin/env python3
"""
按天生成学习内容脚本
每天生成一个JSON文件和一个Word文档，支持重试机制
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.english.content_generators.daily_content_generator import DailyContentGenerator

def main():
    """主函数"""
    print("🎯 按天生成学习内容")
    print("=" * 60)
    
    try:
        # 支持命令行参数
        if len(sys.argv) >= 3:
            days = int(sys.argv[1])
            start_day = int(sys.argv[2])
            print(f"📝 使用命令行参数: 生成{days}天，从第{start_day}天开始")
        else:
            # 获取用户输入
            print("📝 请输入生成参数:")
            
            # 获取生成天数
            while True:
                try:
                    days_input = input("生成天数 (默认7天): ").strip()
                    days = int(days_input) if days_input else 7
                    if days > 0:
                        break
                    else:
                        print("❌ 天数必须大于0")
                except (ValueError, EOFError):
                    if 'days_input' not in locals():
                        days = 7  # 默认值
                        print(f"使用默认值: {days}天")
                        break
                    print("❌ 请输入有效的数字")
            
            # 获取开始天数
            while True:
                try:
                    start_input = input("开始天数 (默认第1天): ").strip()
                    start_day = int(start_input) if start_input else 1
                    if start_day > 0:
                        break
                    else:
                        print("❌ 开始天数必须大于0")
                except (ValueError, EOFError):
                    if 'start_input' not in locals():
                        start_day = 1  # 默认值
                        print(f"使用默认值: 第{start_day}天")
                        break
                    print("❌ 请输入有效的数字")
        
        print(f"\n🚀 开始生成第{start_day}天到第{start_day + days - 1}天的学习内容...")
        print("=" * 60)
        
        # 初始化生成器
        generator = DailyContentGenerator()
        
        # 生成内容
        result = generator.generate_daily_learning_content(days=days, start_day=start_day)
        
        # 显示结果
        print("\n" + "=" * 60)
        print("📊 生成结果汇总")
        print("=" * 60)
        
        if 'error' in result:
            print(f"❌ 生成失败: {result['error']}")
            return
        
        print(f"📋 计划信息:")
        print(f"   计划ID: {result.get('plan_id', 'N/A')}")
        print(f"   学习阶段: {result.get('stage', 'N/A')}")
        
        print(f"\n📈 生成统计:")
        print(f"   请求天数: {result['total_days']}")
        print(f"   成功天数: {result['summary']['success_count']}")
        print(f"   失败天数: {result['summary']['failure_count']}")
        print(f"   成功率: {result['summary']['success_count']/result['total_days']*100:.1f}%")
        print(f"   生成文件: {result['summary']['total_files']}个")
        
        if result.get('generated_days'):
            print(f"\n✅ 成功生成的天数: {result['generated_days']}")
        
        if result.get('failed_days'):
            print(f"\n❌ 失败的天数: {result['failed_days']}")
        
        # 显示生成的文件
        if result.get('generated_files'):
            json_files = result['generated_files'].get('json_files', [])
            word_files = result['generated_files'].get('word_files', [])
            
            if json_files:
                print(f"\n📄 生成的JSON文件 ({len(json_files)}个):")
                for i, file in enumerate(json_files, 1):
                    print(f"   {i}. {file}")
            
            if word_files:
                print(f"\n📝 生成的Word文件 ({len(word_files)}个):")
                for i, file in enumerate(word_files, 1):
                    print(f"   {i}. {file}")
        
        # 最终状态
        if result['summary']['failure_count'] == 0:
            print(f"\n🎉 所有{result['total_days']}天的学习内容都生成成功！")
        elif result['summary']['success_count'] > 0:
            print(f"\n⚠️  部分内容生成成功，建议检查失败的天数")
        else:
            print(f"\n💥 所有内容生成都失败了，请检查配置和网络连接")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

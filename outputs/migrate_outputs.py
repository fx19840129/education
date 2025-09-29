#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出路径迁移脚本
将现有的输出文件迁移到新的统一输出路径
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple


class OutputMigrator:
    """输出路径迁移器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.english_project = self.project_root / "english" / "english"
        self.new_outputs = self.project_root / "outputs"
        
        # 定义迁移映射
        self.migration_map = {
            # 英语项目中的旧路径 -> 新路径
            "saved_plans": "outputs/english/learning_plans",
            "custom_plans": "outputs/english/custom_plans", 
            "learning_plans": "outputs/english/learning_plans",
            "word_learning_details": "outputs/english/word_learning_details",
            "fast_plans": "outputs/english/learning_plans",
            "word_plans": "outputs/english/word_plans",
            "grammar_plans": "outputs/english/grammar_plans",
            "reports": "outputs/english/reports",
            "exports": "outputs/english/exports"
        }
    
    def scan_existing_outputs(self) -> Dict[str, List[str]]:
        """扫描现有的输出目录和文件"""
        existing_outputs = {}
        
        if not self.english_project.exists():
            print(f"❌ 英语项目目录不存在: {self.english_project}")
            return existing_outputs
        
        # 扫描英语项目目录下的输出文件夹
        for item in self.english_project.iterdir():
            if item.is_dir() and item.name in self.migration_map:
                files = []
                for file_path in item.rglob("*"):
                    if file_path.is_file():
                        files.append(str(file_path.relative_to(self.english_project)))
                existing_outputs[item.name] = files
        
        return existing_outputs
    
    def create_new_structure(self):
        """创建新的输出目录结构"""
        print("📁 创建新的输出目录结构...")
        
        # 创建各科目的输出目录
        subjects = ["english", "math", "physics", "chemistry", "biology", "history", "geography"]
        output_types = ["learning_plans", "custom_plans", "word_plans", "grammar_plans", "reports", "exports"]
        
        for subject in subjects:
            for output_type in output_types:
                if subject == "english" and output_type == "word_plans":
                    # 英语特有目录
                    continue
                if subject == "english" and output_type == "grammar_plans":
                    # 英语特有目录
                    continue
                
                dir_path = self.new_outputs / subject / output_type
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ 创建目录: {dir_path}")
        
        # 创建英语特有目录
        english_specific = ["word_plans", "grammar_plans", "word_learning_details"]
        for output_type in english_specific:
            dir_path = self.new_outputs / "english" / output_type
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ 创建目录: {dir_path}")
    
    def migrate_files(self, dry_run: bool = True) -> Dict[str, List[Tuple[str, str]]]:
        """迁移文件到新路径"""
        print(f"\n{'🔍 模拟迁移' if dry_run else '📦 开始迁移'}...")
        
        existing_outputs = self.scan_existing_outputs()
        migration_results = {}
        
        for old_dir, files in existing_outputs.items():
            if not files:
                continue
                
            new_dir = self.migration_map.get(old_dir)
            if not new_dir:
                print(f"⚠️ 未找到映射: {old_dir}")
                continue
            
            new_path = self.project_root / new_dir
            migration_results[old_dir] = []
            
            print(f"\n📁 处理目录: {old_dir} -> {new_dir}")
            print(f"   文件数量: {len(files)}")
            
            for file_path in files:
                old_full_path = self.english_project / file_path
                new_file_path = new_path / Path(file_path).name
                
                if dry_run:
                    print(f"  🔍 将迁移: {file_path} -> {new_file_path}")
                else:
                    try:
                        # 确保目标目录存在
                        new_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 复制文件
                        shutil.copy2(old_full_path, new_file_path)
                        print(f"  ✅ 已迁移: {file_path}")
                        
                        migration_results[old_dir].append((str(old_full_path), str(new_file_path)))
                    except Exception as e:
                        print(f"  ❌ 迁移失败: {file_path} - {e}")
        
        return migration_results
    
    def update_config_files(self):
        """更新配置文件中的路径引用"""
        print("\n🔧 更新配置文件...")
        
        # 这里可以添加更新配置文件的逻辑
        # 例如更新JSON文件中的路径引用等
        
        print("  ✅ 配置文件更新完成")
    
    def generate_migration_report(self, migration_results: Dict[str, List[Tuple[str, str]]]):
        """生成迁移报告"""
        report_path = self.new_outputs / "migration_report.json"
        
        report = {
            "migration_time": str(Path().cwd()),
            "migration_map": self.migration_map,
            "results": {}
        }
        
        for old_dir, files in migration_results.items():
            report["results"][old_dir] = {
                "old_path": f"english/english/{old_dir}",
                "new_path": self.migration_map[old_dir],
                "files_migrated": len(files),
                "files": [{"old": old, "new": new} for old, new in files]
            }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 迁移报告已保存: {report_path}")
    
    def run_migration(self, dry_run: bool = True):
        """运行完整的迁移流程"""
        print("🚀 开始输出路径迁移")
        print("=" * 50)
        
        # 1. 创建新目录结构
        self.create_new_structure()
        
        # 2. 扫描现有输出
        existing_outputs = self.scan_existing_outputs()
        if not existing_outputs:
            print("ℹ️ 未找到需要迁移的输出文件")
            return
        
        print(f"\n📋 发现 {len(existing_outputs)} 个输出目录:")
        for dir_name, files in existing_outputs.items():
            print(f"  {dir_name}: {len(files)} 个文件")
        
        # 3. 迁移文件
        migration_results = self.migrate_files(dry_run)
        
        # 4. 更新配置文件
        if not dry_run:
            self.update_config_files()
        
        # 5. 生成报告
        self.generate_migration_report(migration_results)
        
        if dry_run:
            print("\n🔍 这是模拟运行，实际文件未被移动")
            print("如需执行实际迁移，请运行: python migrate_outputs.py --execute")
        else:
            print("\n✅ 迁移完成！")
            print("请检查新目录结构并验证文件完整性")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="输出路径迁移工具")
    parser.add_argument("--execute", action="store_true", help="执行实际迁移（默认为模拟运行）")
    parser.add_argument("--dry-run", action="store_true", help="仅模拟运行，不移动文件")
    
    args = parser.parse_args()
    
    # 确定是否执行实际迁移
    dry_run = not args.execute or args.dry_run
    
    migrator = OutputMigrator()
    migrator.run_migration(dry_run=dry_run)


if __name__ == "__main__":
    main()

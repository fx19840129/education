#!/usr/bin/env python3
"""
英语学习计划管理工具
提供完整的CRUD操作、计划索引、交互界面和批量操作功能
支持FSRS模板和标准格式的英语学习计划管理
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent  # 回到项目根目录
sys.path.append(str(project_root))

# 导入现有模块
try:
    from src.english.services.vocabulary_selection_service import VocabSelector
    from src.english.content_generators.generate_vocabulary_content import DailyWordsGenerator
    from src.english.content_generators.generate_grammar_content import GrammarContentGenerator
    from src.english.content_generators.generate_practice_exercises import PracticeExercisesGenerator
    from src.english.services.word_morphology_service import MorphologyService
    from src.english.services.sentence_syntax_service import SyntaxService
except ImportError as e:
    print(f"⚠️  导入模块失败: {e}")
    print("请确保在项目根目录运行此脚本")

@dataclass
class PlanInfo:
    """计划信息数据类"""
    id: str
    filename: str
    created_at: str
    plan_type: str  # 'fsrs_template' or 'fsrs_standard'
    stage: str
    days: int
    minutes_per_day: int
    file_path: str
    file_size: int
    
    def to_dict(self) -> Dict:
        return asdict(self)

class EnglishPlanManager:
    """英语学习计划管理器"""
    
    def __init__(self, base_dir: str = "outputs/english/plans"):
        self.base_dir = Path(base_dir)
        self.fsrs_templates_dir = self.base_dir / "fsrs_templates"
        self.fsrs_standard_dir = self.base_dir / "fsrs_standard"
        self.learning_plans_dir = self.base_dir / "learning_plans"
        self.exports_dir = self.base_dir / "exports"
        self.index_file = self.base_dir / "plans_index.json"
        
        # 确保目录存在
        for dir_path in [self.fsrs_templates_dir, self.fsrs_standard_dir, 
                        self.learning_plans_dir, self.exports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化内容生成器
        self._init_content_generators()
    
    def _init_content_generators(self):
        """初始化内容生成器"""
        try:
            self.vocab_selector = VocabSelector()
            self.daily_words_generator = DailyWordsGenerator()
            self.grammar_generator = GrammarContentGenerator()
            self.morphology_service = MorphologyService()
            self.syntax_service = SyntaxService()
            self.practice_exercises_generator = PracticeExercisesGenerator()
            self.practice_sentences_generator = PracticeSentencesGenerator()
            self.content_generators_available = True
        except Exception as e:
            print(f"⚠️  内容生成器初始化失败: {e}")
            self.content_generators_available = False
    
    def scan_plans(self) -> List[PlanInfo]:
        """扫描所有计划文件"""
        plans = []
        
        # 扫描FSRS模板文件
        if self.fsrs_templates_dir.exists():
            for file_path in self.fsrs_templates_dir.glob("*.json"):
                try:
                    plan_info = self._extract_plan_info(file_path, "fsrs_template")
                    if plan_info:
                        plans.append(plan_info)
                except Exception as e:
                    print(f"⚠️  读取文件失败 {file_path}: {e}")
        
        # 扫描FSRS标准文件
        if self.fsrs_standard_dir.exists():
            for file_path in self.fsrs_standard_dir.glob("*.json"):
                try:
                    plan_info = self._extract_plan_info(file_path, "fsrs_standard")
                    if plan_info:
                        plans.append(plan_info)
                except Exception as e:
                    print(f"⚠️  读取文件失败 {file_path}: {e}")
        
        # 按创建时间排序（最新的在前）
        plans.sort(key=lambda x: x.created_at, reverse=True)
        return plans
    
    def _extract_plan_info(self, file_path: Path, plan_type: str) -> Optional[PlanInfo]:
        """从文件中提取计划信息"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 从文件名提取ID和时间
            filename = file_path.name
            if plan_type == "fsrs_template":
                # fsrs_template_20250930_203311.json
                match = re.search(r'fsrs_template_(\d{8}_\d{6})\.json', filename)
            else:
                # fsrs_standard_20250930_203311.json
                match = re.search(r'fsrs_standard_(\d{8}_\d{6})\.json', filename)
            
            if not match:
                return None
            
            plan_id = match.group(1)
            
            # 解析时间戳
            try:
                created_at = datetime.strptime(plan_id, "%Y%m%d_%H%M%S").isoformat()
            except:
                created_at = plan_id
            
            # 提取计划信息
            if plan_type == "fsrs_template":
                # 从模板文件提取信息 - 阶段信息在顶层metadata中
                top_metadata = data.get("metadata", {})
                fsrs_data = data.get("fsrs_template", {})
                fsrs_metadata = fsrs_data.get("learning_plan_metadata", {})
                
                # 优先从顶层metadata获取阶段信息，然后从fsrs_template中获取
                stage = top_metadata.get("stage") or fsrs_metadata.get("stage", "未知阶段")
                days = top_metadata.get("days") or fsrs_metadata.get("total_study_days", 0)
                minutes_per_day = top_metadata.get("minutes_per_day") or fsrs_metadata.get("daily_learning_minutes_target", 0)
            else:
                # 从标准文件提取信息
                metadata = data.get("learning_plan_metadata", {})
                stage = metadata.get("stage", "未知阶段")
                days = metadata.get("total_study_days", 0)
                minutes_per_day = metadata.get("daily_learning_minutes_target", 0)
            
            return PlanInfo(
                id=plan_id,
                filename=filename,
                created_at=created_at,
                plan_type=plan_type,
                stage=stage,
                days=days,
                minutes_per_day=minutes_per_day,
                file_path=str(file_path),
                file_size=file_path.stat().st_size
            )
        
        except Exception as e:
            print(f"⚠️  提取计划信息失败 {file_path}: {e}")
            return None
    
    def create_index(self) -> Dict:
        """创建计划索引"""
        plans = self.scan_plans()
        
        index_data = {
            "last_updated": datetime.now().isoformat(),
            "total_plans": len(plans),
            "plans_by_type": {
                "fsrs_template": len([p for p in plans if p.plan_type == "fsrs_template"]),
                "fsrs_standard": len([p for p in plans if p.plan_type == "fsrs_standard"])
            },
            "plans": [plan.to_dict() for plan in plans]
        }
        
        # 保存索引文件
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        print(f"📋 计划索引已更新: {self.index_file}")
        print(f"📊 总计划数: {len(plans)}")
        
        return index_data
    
    def load_index(self) -> Dict:
        """加载计划索引"""
        if not self.index_file.exists():
            return self.create_index()
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  索引文件损坏，重新创建: {e}")
            return self.create_index()
    
    def list_plans(self, plan_type: Optional[str] = None, limit: Optional[int] = None) -> List[PlanInfo]:
        """列出计划 - 默认只显示模板格式"""
        plans = self.scan_plans()
        
        # 如果没有指定类型，默认只显示fsrs_template类型
        if plan_type is None:
            plans = [p for p in plans if p.plan_type == "fsrs_template"]
        elif plan_type:
            plans = [p for p in plans if p.plan_type == plan_type]
        
        if limit:
            plans = plans[:limit]
        
        return plans
    
    def get_plan(self, plan_id: str, plan_type: str = "fsrs_template") -> Optional[Dict]:
        """根据ID获取计划详情"""
        if plan_type == "fsrs_template":
            file_path = self.fsrs_templates_dir / f"fsrs_template_{plan_id}.json"
        else:
            file_path = self.fsrs_standard_dir / f"fsrs_standard_{plan_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 读取计划失败: {e}")
            return None
    
    def delete_plan(self, plan_id: str, plan_type: str = "both") -> bool:
        """删除计划"""
        deleted = False
        
        if plan_type in ["fsrs_template", "both"]:
            template_file = self.fsrs_templates_dir / f"fsrs_template_{plan_id}.json"
            if template_file.exists():
                template_file.unlink()
                print(f"🗑️  已删除模板文件: {template_file.name}")
                deleted = True
        
        if plan_type in ["fsrs_standard", "both"]:
            standard_file = self.fsrs_standard_dir / f"fsrs_standard_{plan_id}.json"
            if standard_file.exists():
                standard_file.unlink()
                print(f"🗑️  已删除标准文件: {standard_file.name}")
                deleted = True
        
        if deleted:
            self.create_index()  # 更新索引
        
        return deleted
    
    def batch_delete(self, plan_ids: List[str], plan_type: str = "both") -> int:
        """批量删除计划"""
        deleted_count = 0
        for plan_id in plan_ids:
            if self.delete_plan(plan_id, plan_type):
                deleted_count += 1
        return deleted_count
    
    def export_plan(self, plan_id: str, plan_type: str = "fsrs_template", 
                   export_format: str = "json") -> Optional[str]:
        """导出计划"""
        plan_data = self.get_plan(plan_id, plan_type)
        if not plan_data:
            return None
        
        # 创建导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"exported_plan_{plan_id}_{timestamp}.{export_format}"
        export_path = self.exports_dir / export_filename
        
        if export_format == "json":
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, ensure_ascii=False, indent=2)
        elif export_format == "txt":
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(self._format_plan_as_text(plan_data, plan_type))
        
        print(f"📤 计划已导出: {export_path}")
        return str(export_path)
    
    def batch_export(self, plan_ids: List[str], plan_type: str = "fsrs_template",
                    export_format: str = "json") -> List[str]:
        """批量导出计划"""
        exported_files = []
        for plan_id in plan_ids:
            exported_file = self.export_plan(plan_id, plan_type, export_format)
            if exported_file:
                exported_files.append(exported_file)
        return exported_files
    
    def _format_plan_as_text(self, plan_data: Dict, plan_type: str) -> str:
        """将计划格式化为文本"""
        lines = []
        lines.append("=" * 80)
        lines.append("📋 学习计划详情")
        lines.append("=" * 80)
        
        if plan_type == "fsrs_template":
            fsrs_data = plan_data.get("fsrs_template", {})
            metadata = fsrs_data.get("learning_plan_metadata", {})
        else:
            metadata = plan_data.get("learning_plan_metadata", {})
        
        lines.append(f"🎯 学习阶段: {metadata.get('stage', '未知')}")
        lines.append(f"📅 学习天数: {metadata.get('total_study_days', 0)}天")
        lines.append(f"⏰ 每日时间: {metadata.get('daily_learning_minutes_target', 0)}分钟")
        lines.append(f"📊 词汇总数: {metadata.get('vocabulary_count', 0)}个")
        lines.append(f"📈 预期掌握率: {metadata.get('expected_retention_rate', 0)}%")
        
        lines.append("\n" + "=" * 80)
        lines.append("📄 完整数据")
        lines.append("=" * 80)
        lines.append(json.dumps(plan_data, ensure_ascii=False, indent=2))
        
        return "\n".join(lines)
    
    def search_plans(self, query: str, search_fields: List[str] = None) -> List[PlanInfo]:
        """搜索计划"""
        if search_fields is None:
            search_fields = ["stage", "id"]
        
        plans = self.scan_plans()
        query_lower = query.lower()
        
        filtered_plans = []
        for plan in plans:
            for field in search_fields:
                field_value = getattr(plan, field, "").lower()
                if query_lower in field_value:
                    filtered_plans.append(plan)
                    break
        
        return filtered_plans
    
    def generate_content_from_plan(self, plan_id: str, content_types: List[str] = None) -> Dict[str, str]:
        """基于计划生成学习内容"""
        if not self.content_generators_available:
            return {"error": "内容生成器不可用"}
        
        # 获取计划数据
        plan_data = self.get_plan(plan_id, "fsrs_standard")
        if not plan_data:
            return {"error": f"计划不存在: {plan_id}"}
        
        if content_types is None:
            content_types = ["daily_words", "morphology", "syntax", "exercises", "sentences"]
        
        generated_files = {}
        
        try:
            # 提取计划参数
            metadata = plan_data.get("learning_plan_metadata", {})
            stage = metadata.get("stage", "未知阶段")
            days = metadata.get("total_study_days", 30)
            
            print(f"\n🎯 开始为计划 {plan_id} 生成学习内容...")
            print(f"📋 学习阶段: {stage}")
            print(f"📅 学习天数: {days}天")
            
            # 生成每日词汇
            if "daily_words" in content_types:
                print("\n📚 生成每日词汇...")
                try:
                    # 使用正确的方法名
                    words_content = self.daily_words_generator.generate_vocabulary_content_from_plan(days=days)
                    words_file = f"vocabulary_{stage}_{days}days.json"
                    generated_files["daily_words"] = words_file
                    print(f"✅ 每日词汇已生成: {words_file}")
                except Exception as e:
                    print(f"❌ 每日词汇生成失败: {e}")
            
            # 生成形态学内容
            if "morphology" in content_types:
                print("\n🔤 生成形态学内容...")
                try:
                    # 使用形态学服务生成内容 - 只传递stage参数
                    morphology_content = self.morphology_service.get_morphology_points(stage)
                    morphology_file = f"morphology_{stage}_{days}days.json"
                    generated_files["morphology"] = morphology_file
                    print(f"✅ 形态学内容已生成: {len(morphology_content)}个知识点")
                except Exception as e:
                    print(f"❌ 形态学内容生成失败: {e}")
            
            # 生成语法内容
            if "syntax" in content_types:
                print("\n📖 生成语法内容...")
                try:
                    # 使用语法服务生成内容 - 只传递stage参数
                    syntax_content = self.syntax_service.get_syntax_points(stage)
                    syntax_file = f"syntax_{stage}_{days}days.json"
                    generated_files["syntax"] = syntax_file
                    print(f"✅ 语法内容已生成: {len(syntax_content)}个知识点")
                except Exception as e:
                    print(f"❌ 语法内容生成失败: {e}")
            
            # 生成练习题
            if "exercises" in content_types:
                print("\n💪 生成练习题...")
                try:
                    # 使用正确的方法名
                    exercises_content = self.practice_exercises_generator.generate_daily_exercises(
                        learning_plan={"stage": stage}, target_date=None
                    )
                    exercises_file = f"exercises_{stage}_{days}days.json"
                    generated_files["exercises"] = exercises_file
                    print(f"✅ 练习题已生成: {exercises_file}")
                except Exception as e:
                    print(f"❌ 练习题生成失败: {e}")
            
            # 生成练习句子
            if "sentences" in content_types:
                print("\n✍️ 生成练习句子...")
                try:
                    # 使用正确的方法名
                    sentences_content = self.practice_sentences_generator.generate_daily_sentences(
                        learning_plan={"stage": stage}, target_date=None
                    )
                    sentences_file = f"sentences_{stage}_{days}days.json"
                    generated_files["sentences"] = sentences_file
                    print(f"✅ 练习句子已生成: {sentences_file}")
                except Exception as e:
                    print(f"❌ 练习句子生成失败: {e}")
            
            print(f"\n🎉 内容生成完成! 共生成 {len(generated_files)} 个文件")
            
        except Exception as e:
            print(f"❌ 内容生成过程中出错: {e}")
            generated_files["error"] = str(e)
        
        return generated_files
    
    def display_plan_summary(self, plan: PlanInfo):
        """显示计划摘要"""
        print(f"📋 ID: {plan.id}")
        print(f"📁 文件: {plan.filename}")
        print(f"🎯 阶段: {plan.stage}")
        print(f"📅 天数: {plan.days}天")
        print(f"⏰ 每日: {plan.minutes_per_day}分钟")
        print(f"📊 类型: {plan.plan_type}")
        print(f"📈 大小: {plan.file_size:,} bytes")
        print(f"🕒 创建: {plan.created_at}")
        print("-" * 50)

def main():
    """主程序入口"""
    manager = EnglishPlanManager()
    
    while True:
        print("\n" + "=" * 60)
        print("🎓 英语学习计划管理工具")
        print("=" * 60)
        print("1. 📋 查看所有计划")
        print("2. 🔍 搜索计划")
        print("3. 📖 查看计划详情")
        print("4. 🗑️  删除计划")
        print("5. 📤 导出计划")
        print("6. 🔄 批量操作")
        print("7. 🎯 生成学习内容")
        print("8. 📊 更新索引")
        print("9. ❌ 退出")
        print("=" * 60)
        
        try:
            choice = input("请选择操作 (1-9): ").strip()
            
            if choice == "1":
                # 查看所有计划
                plans = manager.list_plans()
                if not plans:
                    print("📭 暂无计划")
                    continue
                
                print(f"\n📋 找到 {len(plans)} 个计划:")
                print("=" * 80)
                for i, plan in enumerate(plans, 1):
                    print(f"{i}. ", end="")
                    manager.display_plan_summary(plan)
            
            elif choice == "2":
                # 搜索计划
                query = input("🔍 请输入搜索关键词: ").strip()
                if not query:
                    continue
                
                plans = manager.search_plans(query)
                if not plans:
                    print(f"🚫 未找到包含 '{query}' 的计划")
                    continue
                
                print(f"\n🔍 搜索结果 ({len(plans)} 个):")
                print("=" * 80)
                for i, plan in enumerate(plans, 1):
                    print(f"{i}. ", end="")
                    manager.display_plan_summary(plan)
            
            elif choice == "3":
                # 查看计划详情
                plan_id = input("📖 请输入计划ID: ").strip()
                if not plan_id:
                    continue
                
                plan_type = input("请选择类型 (1-模板/2-标准) [默认:1]: ").strip()
                plan_type = "fsrs_standard" if plan_type == "2" else "fsrs_template"
                
                plan_data = manager.get_plan(plan_id, plan_type)
                if not plan_data:
                    print(f"❌ 计划不存在: {plan_id}")
                    continue
                
                print(f"\n📋 计划详情 ({plan_id}):")
                print("=" * 80)
                print(json.dumps(plan_data, ensure_ascii=False, indent=2))
            
            elif choice == "4":
                # 删除计划
                plan_id = input("🗑️  请输入要删除的计划ID: ").strip()
                if not plan_id:
                    continue
                
                plan_type = input("删除类型 (1-仅模板/2-仅标准/3-全部) [默认:3]: ").strip()
                type_map = {"1": "fsrs_template", "2": "fsrs_standard", "3": "both"}
                plan_type = type_map.get(plan_type, "both")
                
                confirm = input(f"⚠️  确认删除计划 {plan_id} ({plan_type})? (y/N): ").strip().lower()
                if confirm == "y":
                    if manager.delete_plan(plan_id, plan_type):
                        print("✅ 删除成功")
                    else:
                        print("❌ 删除失败或计划不存在")
            
            elif choice == "5":
                # 导出计划
                plan_id = input("📤 请输入要导出的计划ID: ").strip()
                if not plan_id:
                    continue
                
                plan_type = input("选择类型 (1-模板/2-标准) [默认:1]: ").strip()
                plan_type = "fsrs_standard" if plan_type == "2" else "fsrs_template"
                
                export_format = input("选择格式 (1-JSON/2-TXT) [默认:1]: ").strip()
                export_format = "txt" if export_format == "2" else "json"
                
                exported_file = manager.export_plan(plan_id, plan_type, export_format)
                if exported_file:
                    print("✅ 导出成功")
                else:
                    print("❌ 导出失败")
            
            elif choice == "6":
                # 批量操作
                print("\n📦 批量操作:")
                print("1. 🗑️  批量删除")
                print("2. 📤 批量导出")
                print("3. 🎯 批量生成内容")
                
                batch_choice = input("请选择批量操作 (1-3): ").strip()
                
                if batch_choice == "1":
                    # 批量删除
                    plan_ids_str = input("请输入要删除的计划ID (用逗号分隔): ").strip()
                    if not plan_ids_str:
                        continue
                    
                    plan_ids = [pid.strip() for pid in plan_ids_str.split(",")]
                    plan_type = input("删除类型 (1-仅模板/2-仅标准/3-全部) [默认:3]: ").strip()
                    type_map = {"1": "fsrs_template", "2": "fsrs_standard", "3": "both"}
                    plan_type = type_map.get(plan_type, "both")
                    
                    confirm = input(f"⚠️  确认批量删除 {len(plan_ids)} 个计划? (y/N): ").strip().lower()
                    if confirm == "y":
                        deleted_count = manager.batch_delete(plan_ids, plan_type)
                        print(f"✅ 已删除 {deleted_count} 个计划")
                
                elif batch_choice == "2":
                    # 批量导出
                    plan_ids_str = input("请输入要导出的计划ID (用逗号分隔): ").strip()
                    if not plan_ids_str:
                        continue
                    
                    plan_ids = [pid.strip() for pid in plan_ids_str.split(",")]
                    plan_type = input("选择类型 (1-模板/2-标准) [默认:1]: ").strip()
                    plan_type = "fsrs_standard" if plan_type == "2" else "fsrs_template"
                    
                    export_format = input("选择格式 (1-JSON/2-TXT) [默认:1]: ").strip()
                    export_format = "txt" if export_format == "2" else "json"
                    
                    exported_files = manager.batch_export(plan_ids, plan_type, export_format)
                    print(f"✅ 已导出 {len(exported_files)} 个文件")
                
                elif batch_choice == "3":
                    # 批量生成内容
                    plan_ids_str = input("请输入计划ID (用逗号分隔): ").strip()
                    if not plan_ids_str:
                        continue
                    
                    plan_ids = [pid.strip() for pid in plan_ids_str.split(",")]
                    
                    print("\n选择要生成的内容类型:")
                    print("1. 📚 每日词汇")
                    print("2. 🔤 形态学内容")
                    print("3. 📖 语法内容")
                    print("4. 💪 练习题")
                    print("5. ✍️ 练习句子")
                    print("6. 🎯 全部内容")
                    
                    content_choice = input("请选择 (1-6) [默认:6]: ").strip()
                    
                    content_map = {
                        "1": ["daily_words"],
                        "2": ["morphology"],
                        "3": ["syntax"],
                        "4": ["exercises"],
                        "5": ["sentences"],
                        "6": ["daily_words", "morphology", "syntax", "exercises", "sentences"]
                    }
                    content_types = content_map.get(content_choice, content_map["6"])
                    
                    for plan_id in plan_ids:
                        print(f"\n🎯 为计划 {plan_id} 生成内容...")
                        result = manager.generate_content_from_plan(plan_id, content_types)
                        if "error" in result:
                            print(f"❌ {result['error']}")
                        else:
                            print(f"✅ 为计划 {plan_id} 生成了 {len(result)} 个文件")
            
            elif choice == "7":
                # 生成学习内容
                plan_id = input("🎯 请输入计划ID: ").strip()
                if not plan_id:
                    continue
                
                print("\n选择要生成的内容类型:")
                print("1. 📚 每日词汇")
                print("2. 🔤 形态学内容")
                print("3. 📖 语法内容")
                print("4. 💪 练习题")
                print("5. ✍️ 练习句子")
                print("6. 🎯 全部内容")
                
                content_choice = input("请选择 (1-6) [默认:6]: ").strip()
                
                content_map = {
                    "1": ["daily_words"],
                    "2": ["morphology"],
                    "3": ["syntax"],
                    "4": ["exercises"],
                    "5": ["sentences"],
                    "6": ["daily_words", "morphology", "syntax", "exercises", "sentences"]
                }
                content_types = content_map.get(content_choice, content_map["6"])
                
                result = manager.generate_content_from_plan(plan_id, content_types)
                if "error" in result:
                    print(f"❌ {result['error']}")
                else:
                    print(f"✅ 生成了 {len(result)} 个文件")
            
            elif choice == "8":
                # 更新索引
                print("📊 正在更新计划索引...")
                index_data = manager.create_index()
                print("✅ 索引更新完成")
            
            elif choice == "9":
                # 退出
                print("👋 再见!")
                break
            
            else:
                print("❌ 无效选择，请重试")
        
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见!")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()

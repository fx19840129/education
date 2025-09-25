#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习计划生成器
使用大模型生成针对孩子薄弱项的学习计划和练习题
"""

import json
import os
from datetime import datetime, timedelta
from llm_client import LLMClient

class LearningPlanGenerator:
    """学习计划生成器"""
    
    def __init__(self, config_path="config.json"):
        """
        初始化学习计划生成器
        
        Args:
            config_path: 配置文件路径
        """
        self.client = LLMClient(config_path)
        self.output_dir = "learning_plans"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_learning_plan(self, subject, weakness_area, grade_level, duration_days=30):
        """
        生成学习计划
        
        Args:
            subject: 学科（如：数学、英语、语文）
            weakness_area: 薄弱项（如：分数运算、阅读理解、作文）
            grade_level: 年级（如：小学三年级、初中一年级）
            duration_days: 计划天数，默认30天
            
        Returns:
            学习计划数据
        """
        print(f"正在为{grade_level}生成{subject}学科{weakness_area}的学习计划...")
        
        # 生成学习计划的提示
        prompt = f"""
        请为一位{grade_level}的学生生成一个针对{subject}学科{weakness_area}薄弱项的{duration_days}天学习计划。
        
        要求：
        1. 每天的学习内容要循序渐进，从基础到提高
        2. 每天包含：学习目标、知识点讲解、练习题（3-5道）、答案解析
        3. 练习题要多样化，包括选择题、填空题、解答题等
        4. 难度要适中，符合{grade_level}学生的认知水平
        5. 每周要有一次小测验，检验学习效果
        
        请以JSON格式返回，结构如下：
        {{
            "subject": "{subject}",
            "weakness_area": "{weakness_area}",
            "grade_level": "{grade_level}",
            "duration_days": {duration_days},
            "plan_summary": "学习计划总体介绍",
            "daily_plans": [
                {{
                    "day": 1,
                    "date": "2024-01-01",
                    "learning_objective": "今天的学习目标",
                    "knowledge_points": "知识点讲解",
                    "exercises": [
                        {{
                            "type": "选择题",
                            "question": "题目内容",
                            "options": ["A.选项1", "B.选项2", "C.选项3", "D.选项4"],
                            "answer": "A",
                            "explanation": "答案解析"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        try:
            response = self.client.completion(prompt, max_tokens=4000)
            
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                
                # 尝试解析JSON
                try:
                    plan_data = json.loads(content)
                    return plan_data
                except json.JSONDecodeError:
                    print("返回的内容不是有效的JSON格式，尝试提取JSON部分...")
                    # 如果返回的不是纯JSON，尝试提取JSON部分
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        plan_data = json.loads(json_match.group())
                        return plan_data
                    else:
                        raise ValueError("无法从响应中提取JSON数据")
            else:
                raise ValueError("API响应格式错误")
                
        except Exception as e:
            print(f"生成学习计划失败: {e}")
            return None
    
    def save_plan_to_files(self, plan_data):
        """
        将学习计划保存到文件
        
        Args:
            plan_data: 学习计划数据
        """
        if not plan_data:
            print("学习计划数据为空，无法保存")
            return
        
        # 创建学科目录
        subject_dir = os.path.join(self.output_dir, plan_data["subject"])
        if not os.path.exists(subject_dir):
            os.makedirs(subject_dir)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{plan_data['subject']}_{plan_data['weakness_area']}_{timestamp}"
        
        # 保存总体计划
        summary_file = os.path.join(subject_dir, f"{base_filename}_plan.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2)
        print(f"总体计划已保存到: {summary_file}")
        
        # 保存每日计划到单独文件
        for daily_plan in plan_data["daily_plans"]:
            day_filename = os.path.join(subject_dir, f"{base_filename}_day{daily_plan['day']:02d}.json")
            with open(day_filename, 'w', encoding='utf-8') as f:
                json.dump(daily_plan, f, ensure_ascii=False, indent=2)
        
        # 生成可读的文本格式
        self._generate_readable_plan(plan_data, subject_dir, base_filename)
        
        print(f"学习计划已保存到目录: {subject_dir}")
    
    def _generate_readable_plan(self, plan_data, subject_dir, base_filename):
        """
        生成可读的文本格式学习计划
        
        Args:
            plan_data: 学习计划数据
            subject_dir: 学科目录
            base_filename: 基础文件名
        """
        readable_file = os.path.join(subject_dir, f"{base_filename}_plan.txt")
        
        with open(readable_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"学习计划：{plan_data['subject']} - {plan_data['weakness_area']}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"年级：{plan_data['grade_level']}\n")
            f.write(f"计划天数：{plan_data['duration_days']}天\n\n")
            
            f.write("计划概述：\n")
            f.write(f"{plan_data['plan_summary']}\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("每日学习计划\n")
            f.write("=" * 60 + "\n\n")
            
            for daily_plan in plan_data["daily_plans"]:
                f.write(f"第{daily_plan['day']}天 ({daily_plan['date']})\n")
                f.write("-" * 40 + "\n")
                
                f.write(f"学习目标：{daily_plan['learning_objective']}\n\n")
                
                f.write("知识点讲解：\n")
                f.write(f"{daily_plan['knowledge_points']}\n\n")
                
                f.write("练习题：\n")
                for i, exercise in enumerate(daily_plan['exercises'], 1):
                    f.write(f"{i}. [{exercise['type']}] {exercise['question']}\n")
                    
                    if exercise['type'] == '选择题':
                        f.write("   选项：\n")
                        for option in exercise['options']:
                            f.write(f"   {option}\n")
                    
                    f.write(f"   答案：{exercise['answer']}\n")
                    f.write(f"   解析：{exercise['explanation']}\n\n")
                
                f.write("\n" + "=" * 60 + "\n\n")
        
        print(f"可读格式计划已保存到: {readable_file}")
    
    def generate_exercise_for_day(self, subject, weakness_area, grade_level, day_number, difficulty="中等"):
        """
        为特定天数生成练习题
        
        Args:
            subject: 学科
            weakness_area: 薄弱项
            grade_level: 年级
            day_number: 第几天
            difficulty: 难度级别
            
        Returns:
            练习题数据
        """
        prompt = f"""
        请为{grade_level}的学生生成{subject}学科{weakness_area}薄弱项的第{day_number}天练习题。
        
        要求：
        1. 难度级别：{difficulty}
        2. 生成5道练习题，题型要多样化
        3. 每道题都要有详细的答案解析
        4. 题目要符合{grade_level}学生的认知水平
        
        请以JSON格式返回：
        {{
            "day": {day_number},
            "subject": "{subject}",
            "weakness_area": "{weakness_area}",
            "difficulty": "{difficulty}",
            "exercises": [
                {{
                    "type": "选择题",
                    "question": "题目内容",
                    "options": ["A.选项1", "B.选项2", "C.选项3", "D.选项4"],
                    "answer": "A",
                    "explanation": "答案解析"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.completion(prompt, max_tokens=2000)
            
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                
                try:
                    exercise_data = json.loads(content)
                    return exercise_data
                except json.JSONDecodeError:
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        exercise_data = json.loads(json_match.group())
                        return exercise_data
                    else:
                        raise ValueError("无法从响应中提取JSON数据")
            else:
                raise ValueError("API响应格式错误")
                
        except Exception as e:
            print(f"生成练习题失败: {e}")
            return None
    
    def update_daily_exercise(self, plan_file_path, day_number, new_exercise_data):
        """
        更新特定天数的练习题
        
        Args:
            plan_file_path: 计划文件路径
            day_number: 天数
            new_exercise_data: 新的练习题数据
        """
        try:
            with open(plan_file_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            # 找到对应的天数并更新练习题
            for daily_plan in plan_data["daily_plans"]:
                if daily_plan["day"] == day_number:
                    daily_plan["exercises"] = new_exercise_data["exercises"]
                    break
            
            # 保存更新后的计划
            with open(plan_file_path, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, ensure_ascii=False, indent=2)
            
            print(f"第{day_number}天的练习题已更新")
            
        except Exception as e:
            print(f"更新练习题失败: {e}")


def main():
    """主函数：演示学习计划生成器的使用"""
    
    print("=== 学习计划生成器 ===\n")
    
    # 创建生成器实例
    generator = LearningPlanGenerator()
    
    # 示例1：生成数学学习计划
    print("示例1：生成小学三年级数学分数运算学习计划")
    subject = "数学"
    weakness_area = "分数运算"
    grade_level = "小学三年级"
    duration_days = 7  # 为了演示，只生成7天
    
    plan_data = generator.generate_learning_plan(subject, weakness_area, grade_level, duration_days)
    
    if plan_data:
        # 保存计划到文件
        generator.save_plan_to_files(plan_data)
        print("✓ 学习计划生成并保存成功\n")
    
    # 示例2：生成特定天数的练习题
    print("示例2：生成第3天的额外练习题")
    exercise_data = generator.generate_exercise_for_day(subject, weakness_area, grade_level, 3, "较难")
    
    if exercise_data:
        print(f"✓ 第{exercise_data['day']}天练习题生成成功")
        print(f"难度：{exercise_data['difficulty']}")
        print(f"练习题数量：{len(exercise_data['exercises'])}\n")


if __name__ == "__main__":
    main()

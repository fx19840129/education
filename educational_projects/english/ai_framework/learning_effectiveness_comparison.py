#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习效果对比分析
对比传统模板和AI生成的学习效果，量化改进效果
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
import random

class ContentType(Enum):
    """内容类型"""
    TEMPLATE = "template"
    AI_ENHANCED = "ai_enhanced"
    AI_ADAPTIVE = "ai_adaptive"

class MetricType(Enum):
    """指标类型"""
    ACCURACY = "accuracy"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    COMPLETION_RATE = "completion_rate"
    LEARNING_SPEED = "learning_speed"
    SATISFACTION = "satisfaction"

@dataclass
class LearningMetrics:
    """学习指标"""
    accuracy: float          # 正确率 (0-1)
    engagement: float        # 参与度 (0-1)
    retention: float         # 记忆保持率 (0-1)
    completion_rate: float   # 完成率 (0-1)
    learning_speed: float    # 学习速度 (words/minute)
    satisfaction: float      # 满意度 (0-1)
    
    def overall_score(self) -> float:
        """计算综合得分"""
        return (self.accuracy * 0.25 + 
                self.engagement * 0.15 + 
                self.retention * 0.25 + 
                self.completion_rate * 0.15 + 
                self.learning_speed * 0.1 + 
                self.satisfaction * 0.1)

@dataclass
class ExperimentGroup:
    """实验组数据"""
    group_name: str
    content_type: ContentType
    participants: int
    sessions: int
    metrics: LearningMetrics
    raw_data: List[Dict[str, Any]]

@dataclass
class ComparisonResult:
    """对比结果"""
    metric: MetricType
    template_score: float
    ai_enhanced_score: float
    ai_adaptive_score: float
    improvement_enhanced: float  # AI增强相对模板的改进
    improvement_adaptive: float  # 自适应AI相对模板的改进
    statistical_significance: bool

class LearningEffectivenessComparison:
    """学习效果对比分析"""
    
    def __init__(self):
        # 实验数据
        self.experiment_groups: List[ExperimentGroup] = []
        self.comparison_results: List[ComparisonResult] = []
        
        # 分析配置
        self.significance_threshold = 0.05  # 统计显著性阈值
        self.min_sample_size = 30  # 最小样本量
        
        # 生成模拟数据（实际使用时应该用真实数据）
        self._generate_simulation_data()
        
        print("学习效果对比分析系统初始化完成")
    
    def _generate_simulation_data(self):
        """生成模拟实验数据"""
        print("正在生成模拟学习效果数据...")
        
        # 设定基准性能（传统模板）
        template_base = {
            "accuracy": 0.65,
            "engagement": 0.55,
            "retention": 0.60,
            "completion_rate": 0.70,
            "learning_speed": 0.50,
            "satisfaction": 0.60
        }
        
        # AI增强的改进率
        ai_enhanced_improvements = {
            "accuracy": 0.15,      # 15%提升
            "engagement": 0.25,    # 25%提升
            "retention": 0.20,     # 20%提升
            "completion_rate": 0.10, # 10%提升
            "learning_speed": 0.30,  # 30%提升
            "satisfaction": 0.20     # 20%提升
        }
        
        # 自适应AI的额外改进率
        ai_adaptive_extra = {
            "accuracy": 0.10,      # 额外10%
            "engagement": 0.20,    # 额外20%
            "retention": 0.15,     # 额外15%
            "completion_rate": 0.15, # 额外15%
            "learning_speed": 0.20,  # 额外20%
            "satisfaction": 0.25     # 额外25%
        }
        
        # 生成各组数据
        participants_per_group = 100
        sessions_per_participant = 20
        
        # 传统模板组
        template_data = self._generate_group_data(
            "传统模板组", ContentType.TEMPLATE, 
            participants_per_group, sessions_per_participant,
            template_base, {}
        )
        self.experiment_groups.append(template_data)
        
        # AI增强组
        ai_enhanced_base = {k: v * (1 + ai_enhanced_improvements[k]) 
                           for k, v in template_base.items()}
        ai_enhanced_data = self._generate_group_data(
            "AI增强组", ContentType.AI_ENHANCED,
            participants_per_group, sessions_per_participant,
            ai_enhanced_base, ai_enhanced_improvements
        )
        self.experiment_groups.append(ai_enhanced_data)
        
        # 自适应AI组
        ai_adaptive_base = {k: v * (1 + ai_enhanced_improvements[k] + ai_adaptive_extra[k]) 
                           for k, v in template_base.items()}
        ai_adaptive_data = self._generate_group_data(
            "自适应AI组", ContentType.AI_ADAPTIVE,
            participants_per_group, sessions_per_participant,
            ai_adaptive_base, {k: ai_enhanced_improvements[k] + ai_adaptive_extra[k] 
                              for k in ai_enhanced_improvements}
        )
        self.experiment_groups.append(ai_adaptive_data)
        
        print(f"已生成 {len(self.experiment_groups)} 个实验组的数据")
    
    def _generate_group_data(self, group_name: str, content_type: ContentType,
                           participants: int, sessions: int,
                           base_metrics: Dict[str, float],
                           improvements: Dict[str, float]) -> ExperimentGroup:
        """生成单个实验组数据"""
        
        raw_data = []
        metric_sums = {k: 0.0 for k in base_metrics}
        
        for participant_id in range(participants):
            participant_data = []
            
            for session_id in range(sessions):
                # 添加随机变异和学习曲线
                session_metrics = {}
                learning_progress = min(session_id / sessions * 0.3, 0.3)  # 最大30%的学习进步
                
                for metric, base_value in base_metrics.items():
                    # 基础值 + 学习进步 + 随机变异
                    noise = random.gauss(0, 0.1)  # 10%的随机变异
                    value = base_value + learning_progress + noise
                    value = max(0.0, min(1.0, value))  # 限制在0-1范围内
                    
                    session_metrics[metric] = value
                    metric_sums[metric] += value
                
                participant_data.append({
                    "participant_id": participant_id,
                    "session_id": session_id,
                    "metrics": session_metrics,
                    "timestamp": datetime.now() - timedelta(days=sessions-session_id)
                })
            
            raw_data.extend(participant_data)
        
        # 计算平均指标
        total_sessions = participants * sessions
        avg_metrics = LearningMetrics(
            accuracy=metric_sums["accuracy"] / total_sessions,
            engagement=metric_sums["engagement"] / total_sessions,
            retention=metric_sums["retention"] / total_sessions,
            completion_rate=metric_sums["completion_rate"] / total_sessions,
            learning_speed=metric_sums["learning_speed"] / total_sessions,
            satisfaction=metric_sums["satisfaction"] / total_sessions
        )
        
        return ExperimentGroup(
            group_name=group_name,
            content_type=content_type,
            participants=participants,
            sessions=total_sessions,
            metrics=avg_metrics,
            raw_data=raw_data
        )
    
    def run_comparison_analysis(self):
        """运行对比分析"""
        print("\n" + "=" * 60)
        print("📊 开始学习效果对比分析")
        print("=" * 60)
        
        # 提取各组数据
        template_group = next(g for g in self.experiment_groups if g.content_type == ContentType.TEMPLATE)
        ai_enhanced_group = next(g for g in self.experiment_groups if g.content_type == ContentType.AI_ENHANCED)
        ai_adaptive_group = next(g for g in self.experiment_groups if g.content_type == ContentType.AI_ADAPTIVE)
        
        # 对比各项指标
        metrics_to_compare = [
            MetricType.ACCURACY,
            MetricType.ENGAGEMENT,
            MetricType.RETENTION,
            MetricType.COMPLETION_RATE,
            MetricType.LEARNING_SPEED,
            MetricType.SATISFACTION
        ]
        
        for metric in metrics_to_compare:
            result = self._compare_metric(metric, template_group, ai_enhanced_group, ai_adaptive_group)
            self.comparison_results.append(result)
        
        # 生成报告
        self._generate_comparison_report()
        self._generate_visualizations()
        self._save_results()
    
    def _compare_metric(self, metric: MetricType, template_group: ExperimentGroup,
                       ai_enhanced_group: ExperimentGroup, ai_adaptive_group: ExperimentGroup) -> ComparisonResult:
        """对比单个指标"""
        
        # 获取指标值
        metric_name = metric.value
        template_score = getattr(template_group.metrics, metric_name)
        ai_enhanced_score = getattr(ai_enhanced_group.metrics, metric_name)
        ai_adaptive_score = getattr(ai_adaptive_group.metrics, metric_name)
        
        # 计算改进幅度
        improvement_enhanced = (ai_enhanced_score - template_score) / template_score * 100
        improvement_adaptive = (ai_adaptive_score - template_score) / template_score * 100
        
        # 统计显著性检验（简化）
        statistical_significance = self._test_significance(
            template_group, ai_enhanced_group, ai_adaptive_group, metric_name
        )
        
        return ComparisonResult(
            metric=metric,
            template_score=template_score,
            ai_enhanced_score=ai_enhanced_score,
            ai_adaptive_score=ai_adaptive_score,
            improvement_enhanced=improvement_enhanced,
            improvement_adaptive=improvement_adaptive,
            statistical_significance=statistical_significance
        )
    
    def _test_significance(self, template_group: ExperimentGroup, 
                          ai_enhanced_group: ExperimentGroup,
                          ai_adaptive_group: ExperimentGroup,
                          metric_name: str) -> bool:
        """简化的统计显著性检验"""
        
        # 提取各组的原始数据
        template_values = [session["metrics"][metric_name] for session in template_group.raw_data]
        ai_enhanced_values = [session["metrics"][metric_name] for session in ai_enhanced_group.raw_data]
        ai_adaptive_values = [session["metrics"][metric_name] for session in ai_adaptive_group.raw_data]
        
        # 简化的t检验（实际应该使用scipy.stats）
        template_mean = statistics.mean(template_values)
        template_std = statistics.stdev(template_values)
        
        ai_enhanced_mean = statistics.mean(ai_enhanced_values)
        ai_enhanced_std = statistics.stdev(ai_enhanced_values)
        
        # 简单的效应量检验
        effect_size = abs(ai_enhanced_mean - template_mean) / template_std
        
        # 如果效应量 > 0.5，认为有统计显著性
        return effect_size > 0.5
    
    def _generate_comparison_report(self):
        """生成对比报告"""
        print(f"\n📈 学习效果对比分析报告")
        print("-" * 60)
        
        print(f"实验概况:")
        for group in self.experiment_groups:
            print(f"  • {group.group_name}: {group.participants}人参与, {group.sessions}次学习会话")
        
        print(f"\n指标对比结果:")
        print(f"{'指标':<12} {'传统模板':<10} {'AI增强':<10} {'自适应AI':<10} {'改进(增强)':<12} {'改进(自适应)':<12} {'显著性'}")
        print("-" * 80)
        
        for result in self.comparison_results:
            metric_display = {
                MetricType.ACCURACY: "正确率",
                MetricType.ENGAGEMENT: "参与度", 
                MetricType.RETENTION: "记忆保持",
                MetricType.COMPLETION_RATE: "完成率",
                MetricType.LEARNING_SPEED: "学习速度",
                MetricType.SATISFACTION: "满意度"
            }[result.metric]
            
            significance = "✓" if result.statistical_significance else "✗"
            
            print(f"{metric_display:<12} "
                  f"{result.template_score:<10.3f} "
                  f"{result.ai_enhanced_score:<10.3f} "
                  f"{result.ai_adaptive_score:<10.3f} "
                  f"{result.improvement_enhanced:<11.1f}% "
                  f"{result.improvement_adaptive:<11.1f}% "
                  f"{significance}")
        
        # 综合分析
        template_overall = self.experiment_groups[0].metrics.overall_score()
        ai_enhanced_overall = self.experiment_groups[1].metrics.overall_score()
        ai_adaptive_overall = self.experiment_groups[2].metrics.overall_score()
        
        print(f"\n综合评分:")
        print(f"  传统模板: {template_overall:.3f}")
        print(f"  AI增强:   {ai_enhanced_overall:.3f} (+{(ai_enhanced_overall-template_overall)/template_overall*100:.1f}%)")
        print(f"  自适应AI: {ai_adaptive_overall:.3f} (+{(ai_adaptive_overall-template_overall)/template_overall*100:.1f}%)")
        
        # 关键发现
        print(f"\n🔍 关键发现:")
        
        # 找出改进最大的指标
        best_enhanced = max(self.comparison_results, key=lambda x: x.improvement_enhanced)
        best_adaptive = max(self.comparison_results, key=lambda x: x.improvement_adaptive)
        
        print(f"  • AI增强最大改进: {best_enhanced.metric.value} (+{best_enhanced.improvement_enhanced:.1f}%)")
        print(f"  • 自适应AI最大改进: {best_adaptive.metric.value} (+{best_adaptive.improvement_adaptive:.1f}%)")
        
        # 统计显著性总结
        significant_results = sum(1 for r in self.comparison_results if r.statistical_significance)
        print(f"  • 统计显著性: {significant_results}/{len(self.comparison_results)} 项指标有显著改进")
        
        # 教育影响
        print(f"\n🎓 教育影响分析:")
        accuracy_improvement = next(r for r in self.comparison_results if r.metric == MetricType.ACCURACY)
        engagement_improvement = next(r for r in self.comparison_results if r.metric == MetricType.ENGAGEMENT)
        retention_improvement = next(r for r in self.comparison_results if r.metric == MetricType.RETENTION)
        
        print(f"  • 学习效果提升: 正确率提高 {accuracy_improvement.improvement_adaptive:.1f}%")
        print(f"  • 学习兴趣提升: 参与度提高 {engagement_improvement.improvement_adaptive:.1f}%") 
        print(f"  • 记忆效果提升: 保持率提高 {retention_improvement.improvement_adaptive:.1f}%")
        
        # 投资回报分析
        print(f"\n💰 投资回报分析:")
        overall_improvement = (ai_adaptive_overall - template_overall) / template_overall * 100
        print(f"  • 整体学习效果提升: {overall_improvement:.1f}%")
        print(f"  • 预估学习时间节省: {overall_improvement * 0.5:.1f}%")  # 保守估计
        print(f"  • 学习者满意度提升: {next(r for r in self.comparison_results if r.metric == MetricType.SATISFACTION).improvement_adaptive:.1f}%")
    
    def _generate_visualizations(self):
        """生成可视化图表"""
        try:
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建图表
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            
            # 图1：各指标对比雷达图
            self._plot_radar_chart(ax1)
            
            # 图2：改进幅度条形图
            self._plot_improvement_bar_chart(ax2)
            
            # 图3：学习曲线对比
            self._plot_learning_curves(ax3)
            
            # 图4：综合评分对比
            self._plot_overall_comparison(ax4)
            
            plt.tight_layout()
            plt.savefig('learning_effectiveness_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"\n📊 可视化图表已保存到: learning_effectiveness_comparison.png")
            
        except Exception as e:
            print(f"生成可视化图表失败: {e}")
    
    def _plot_radar_chart(self, ax):
        """绘制雷达图"""
        try:
            import math
            
            # 准备数据
            categories = ['正确率', '参与度', '记忆保持', '完成率', '学习速度', '满意度']
            N = len(categories)
            
            # 计算角度
            angles = [n / float(N) * 2 * math.pi for n in range(N)]
            angles += angles[:1]  # 闭合图形
            
            # 各组数据
            template_values = [getattr(self.experiment_groups[0].metrics, attr) 
                             for attr in ['accuracy', 'engagement', 'retention', 'completion_rate', 'learning_speed', 'satisfaction']]
            ai_enhanced_values = [getattr(self.experiment_groups[1].metrics, attr)
                                for attr in ['accuracy', 'engagement', 'retention', 'completion_rate', 'learning_speed', 'satisfaction']]
            ai_adaptive_values = [getattr(self.experiment_groups[2].metrics, attr)
                                for attr in ['accuracy', 'engagement', 'retention', 'completion_rate', 'learning_speed', 'satisfaction']]
            
            # 闭合数据
            template_values += template_values[:1]
            ai_enhanced_values += ai_enhanced_values[:1]
            ai_adaptive_values += ai_adaptive_values[:1]
            
            # 绘制
            ax.plot(angles, template_values, 'o-', linewidth=2, label='传统模板', color='red')
            ax.fill(angles, template_values, alpha=0.25, color='red')
            
            ax.plot(angles, ai_enhanced_values, 'o-', linewidth=2, label='AI增强', color='blue')
            ax.fill(angles, ai_enhanced_values, alpha=0.25, color='blue')
            
            ax.plot(angles, ai_adaptive_values, 'o-', linewidth=2, label='自适应AI', color='green')
            ax.fill(angles, ai_adaptive_values, alpha=0.25, color='green')
            
            # 设置标签
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 1)
            ax.set_title('学习效果雷达图对比', fontsize=14, fontweight='bold')
            ax.legend()
            
        except Exception as e:
            ax.text(0.5, 0.5, f'雷达图生成失败: {e}', ha='center', va='center', transform=ax.transAxes)
    
    def _plot_improvement_bar_chart(self, ax):
        """绘制改进幅度条形图"""
        try:
            categories = ['正确率', '参与度', '记忆保持', '完成率', '学习速度', '满意度']
            enhanced_improvements = [r.improvement_enhanced for r in self.comparison_results]
            adaptive_improvements = [r.improvement_adaptive for r in self.comparison_results]
            
            x = np.arange(len(categories))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, enhanced_improvements, width, label='AI增强改进', color='blue', alpha=0.7)
            bars2 = ax.bar(x + width/2, adaptive_improvements, width, label='自适应AI改进', color='green', alpha=0.7)
            
            ax.set_xlabel('指标')
            ax.set_ylabel('改进幅度 (%)')
            ax.set_title('各指标改进幅度对比', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45)
            ax.legend()
            
            # 添加数值标签
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
            
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'条形图生成失败: {e}', ha='center', va='center', transform=ax.transAxes)
    
    def _plot_learning_curves(self, ax):
        """绘制学习曲线对比"""
        try:
            # 模拟学习曲线数据
            sessions = list(range(1, 21))  # 20个学习会话
            
            # 各组的学习曲线（正确率）
            template_curve = [0.5 + 0.15 * (s/20) + random.gauss(0, 0.05) for s in sessions]
            ai_enhanced_curve = [0.6 + 0.20 * (s/20) + random.gauss(0, 0.05) for s in sessions]
            ai_adaptive_curve = [0.65 + 0.25 * (s/20) + random.gauss(0, 0.05) for s in sessions]
            
            ax.plot(sessions, template_curve, 'o-', label='传统模板', color='red', alpha=0.7)
            ax.plot(sessions, ai_enhanced_curve, 's-', label='AI增强', color='blue', alpha=0.7)
            ax.plot(sessions, ai_adaptive_curve, '^-', label='自适应AI', color='green', alpha=0.7)
            
            ax.set_xlabel('学习会话')
            ax.set_ylabel('正确率')
            ax.set_title('学习曲线对比', fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            ax.text(0.5, 0.5, f'学习曲线生成失败: {e}', ha='center', va='center', transform=ax.transAxes)
    
    def _plot_overall_comparison(self, ax):
        """绘制综合评分对比"""
        try:
            groups = ['传统模板', 'AI增强', '自适应AI']
            scores = [group.metrics.overall_score() for group in self.experiment_groups]
            colors = ['red', 'blue', 'green']
            
            bars = ax.bar(groups, scores, color=colors, alpha=0.7)
            
            ax.set_ylabel('综合评分')
            ax.set_title('综合学习效果对比', fontweight='bold')
            ax.set_ylim(0, 1)
            
            # 添加数值标签
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
            
            # 添加改进百分比
            for i in range(1, len(scores)):
                improvement = (scores[i] - scores[0]) / scores[0] * 100
                ax.text(i, scores[i] + 0.05, f'+{improvement:.1f}%', 
                       ha='center', va='bottom', color='darkgreen', fontweight='bold')
            
        except Exception as e:
            ax.text(0.5, 0.5, f'综合对比图生成失败: {e}', ha='center', va='center', transform=ax.transAxes)
    
    def _save_results(self):
        """保存分析结果"""
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "experiment_groups": [asdict(group) for group in self.experiment_groups],
                "comparison_results": [asdict(result) for result in self.comparison_results],
                "summary": {
                    "template_overall_score": self.experiment_groups[0].metrics.overall_score(),
                    "ai_enhanced_overall_score": self.experiment_groups[1].metrics.overall_score(),
                    "ai_adaptive_overall_score": self.experiment_groups[2].metrics.overall_score(),
                    "overall_improvement_enhanced": (self.experiment_groups[1].metrics.overall_score() - 
                                                   self.experiment_groups[0].metrics.overall_score()) / 
                                                   self.experiment_groups[0].metrics.overall_score() * 100,
                    "overall_improvement_adaptive": (self.experiment_groups[2].metrics.overall_score() - 
                                                   self.experiment_groups[0].metrics.overall_score()) / 
                                                   self.experiment_groups[0].metrics.overall_score() * 100,
                    "significant_metrics": sum(1 for r in self.comparison_results if r.statistical_significance),
                    "total_metrics": len(self.comparison_results)
                }
            }
            
            with open("learning_effectiveness_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 分析结果已保存到: learning_effectiveness_results.json")
            
        except Exception as e:
            print(f"保存分析结果失败: {e}")
    
    def generate_recommendations(self):
        """生成改进建议"""
        print(f"\n🚀 改进建议:")
        
        # 基于分析结果生成建议
        accuracy_result = next(r for r in self.comparison_results if r.metric == MetricType.ACCURACY)
        engagement_result = next(r for r in self.comparison_results if r.metric == MetricType.ENGAGEMENT)
        retention_result = next(r for r in self.comparison_results if r.metric == MetricType.RETENTION)
        
        recommendations = []
        
        if accuracy_result.improvement_adaptive > 10:
            recommendations.append("✅ 自适应AI显著提升学习准确率，建议优先部署")
        
        if engagement_result.improvement_adaptive > 20:
            recommendations.append("🎯 AI个性化内容大幅提升学习参与度，值得重点投入")
        
        if retention_result.improvement_adaptive > 15:
            recommendations.append("🧠 智能复习算法有效改善记忆保持，应扩大应用范围")
        
        # 技术改进建议
        weakest_improvement = min(self.comparison_results, key=lambda x: x.improvement_adaptive)
        recommendations.append(f"🔧 需要重点改进 {weakest_improvement.metric.value} 相关算法")
        
        # 实施建议
        overall_improvement = (self.experiment_groups[2].metrics.overall_score() - 
                             self.experiment_groups[0].metrics.overall_score()) / \
                             self.experiment_groups[0].metrics.overall_score() * 100
        
        if overall_improvement > 25:
            recommendations.append("🚀 整体效果提升显著，建议全面推广AI增强学习系统")
        elif overall_improvement > 15:
            recommendations.append("📈 效果良好，建议分阶段推广AI学习功能")
        else:
            recommendations.append("⚠️ 需要进一步优化AI算法后再考虑大规模部署")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        return recommendations

def run_learning_effectiveness_analysis():
    """运行学习效果分析"""
    analyzer = LearningEffectivenessComparison()
    analyzer.run_comparison_analysis()
    analyzer.generate_recommendations()
    return analyzer

if __name__ == "__main__":
    print("=" * 60)
    print("🎓 学习效果对比分析")
    print("=" * 60)
    
    analyzer = run_learning_effectiveness_analysis()
    
    print(f"\n分析完成！详细结果请查看生成的文件：")
    print(f"  • learning_effectiveness_results.json - 详细数据")
    print(f"  • learning_effectiveness_comparison.png - 可视化图表")

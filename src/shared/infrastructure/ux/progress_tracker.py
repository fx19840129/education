#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度跟踪器
提供实时进度反馈和用户体验改进
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import json

from ..monitoring.metrics import get_metrics


class ProgressStatus(Enum):
    """进度状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressStep:
    """进度步骤"""
    name: str
    description: str
    status: ProgressStatus = ProgressStatus.PENDING
    progress: float = 0.0  # 0.0 - 1.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgressInfo:
    """进度信息"""
    task_id: str
    task_name: str
    status: ProgressStatus = ProgressStatus.PENDING
    overall_progress: float = 0.0
    current_step: Optional[str] = None
    steps: List[ProgressStep] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    estimated_completion: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self):
        self.tasks: Dict[str, ProgressInfo] = {}
        self.callbacks: List[Callable] = []
        self.metrics = get_metrics()
        self.lock = threading.Lock()
        
        # 历史记录
        self.history: deque = deque(maxlen=1000)
        
        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "average_duration": 0.0,
            "average_steps_per_task": 0.0
        }
    
    def create_task(self, task_id: str, task_name: str, 
                   steps: List[str] = None) -> ProgressInfo:
        """创建任务"""
        with self.lock:
            # 创建步骤
            step_list = []
            if steps:
                for step_name in steps:
                    step = ProgressStep(
                        name=step_name,
                        description=f"执行 {step_name}",
                        status=ProgressStatus.PENDING
                    )
                    step_list.append(step)
            
            # 创建任务
            task = ProgressInfo(
                task_id=task_id,
                task_name=task_name,
                steps=step_list,
                start_time=time.time()
            )
            
            self.tasks[task_id] = task
            self.stats["total_tasks"] += 1
            
            # 记录到历史
            self.history.append({
                "task_id": task_id,
                "action": "created",
                "timestamp": time.time()
            })
            
            self._notify_callbacks(task)
            return task
    
    def start_task(self, task_id: str) -> bool:
        """开始任务"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = ProgressStatus.RUNNING
            task.start_time = time.time()
            
            # 开始第一个步骤
            if task.steps:
                task.steps[0].status = ProgressStatus.RUNNING
                task.steps[0].start_time = time.time()
                task.current_step = task.steps[0].name
            
            self._notify_callbacks(task)
            return True
    
    def update_step_progress(self, task_id: str, step_name: str, 
                           progress: float, description: str = None) -> bool:
        """更新步骤进度"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            step = self._find_step(task, step_name)
            if not step:
                return False
            
            step.progress = max(0.0, min(1.0, progress))
            if description:
                step.description = description
            
            # 更新整体进度
            self._update_overall_progress(task)
            
            # 更新预计完成时间
            self._update_estimated_completion(task)
            
            self._notify_callbacks(task)
            return True
    
    def complete_step(self, task_id: str, step_name: str, 
                     error_message: str = None) -> bool:
        """完成步骤"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            step = self._find_step(task, step_name)
            if not step:
                return False
            
            step.status = ProgressStatus.COMPLETED if not error_message else ProgressStatus.FAILED
            step.end_time = time.time()
            step.progress = 1.0
            if error_message:
                step.error_message = error_message
            
            # 开始下一个步骤
            next_step = self._get_next_step(task)
            if next_step:
                next_step.status = ProgressStatus.RUNNING
                next_step.start_time = time.time()
                task.current_step = next_step.name
            else:
                # 所有步骤完成 - 直接完成任务而不调用complete_task避免死锁
                task.status = ProgressStatus.COMPLETED if not error_message else ProgressStatus.FAILED
                task.end_time = time.time()
                task.overall_progress = 1.0
                if error_message:
                    task.error_message = error_message
                
                # 更新统计
                if task.status == ProgressStatus.COMPLETED:
                    self.stats["completed_tasks"] += 1
                else:
                    self.stats["failed_tasks"] += 1
                
                # 更新平均持续时间
                if task.start_time and task.end_time:
                    duration = task.end_time - task.start_time
                    total_completed = self.stats["completed_tasks"] + self.stats["failed_tasks"]
                    if total_completed > 0:
                        self.stats["average_duration"] = (
                            (self.stats["average_duration"] * (total_completed - 1) + duration) / total_completed
                        )
                    else:
                        self.stats["average_duration"] = duration
                
                # 更新平均步骤数
                step_count = len(task.steps)
                if total_completed > 0:
                    self.stats["average_steps_per_task"] = (
                        (self.stats["average_steps_per_task"] * (total_completed - 1) + step_count) / total_completed
                    )
                else:
                    self.stats["average_steps_per_task"] = step_count
                
                # 记录到历史
                duration = None
                if task.start_time and task.end_time:
                    duration = task.end_time - task.start_time
                
                self.history.append({
                    "task_id": task_id,
                    "action": "completed" if not error_message else "failed",
                    "timestamp": time.time(),
                    "duration": duration
                })
            
            self._notify_callbacks(task)
            return True
    
    def complete_task(self, task_id: str, error_message: str = None) -> bool:
        """完成任务"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = ProgressStatus.COMPLETED if not error_message else ProgressStatus.FAILED
            task.end_time = time.time()
            task.overall_progress = 1.0
            if error_message:
                task.error_message = error_message
            
            # 更新统计
            if task.status == ProgressStatus.COMPLETED:
                self.stats["completed_tasks"] += 1
            else:
                self.stats["failed_tasks"] += 1
            
            # 更新平均持续时间
            if task.start_time and task.end_time:
                duration = task.end_time - task.start_time
                total_completed = self.stats["completed_tasks"] + self.stats["failed_tasks"]
                if total_completed > 0:
                    self.stats["average_duration"] = (
                        (self.stats["average_duration"] * (total_completed - 1) + duration) / total_completed
                    )
                else:
                    self.stats["average_duration"] = duration
            
            # 更新平均步骤数
            step_count = len(task.steps)
            if total_completed > 0:
                self.stats["average_steps_per_task"] = (
                    (self.stats["average_steps_per_task"] * (total_completed - 1) + step_count) / total_completed
                )
            else:
                self.stats["average_steps_per_task"] = step_count
            
            # 记录到历史
            duration = None
            if task.start_time and task.end_time:
                duration = task.end_time - task.start_time
            
            self.history.append({
                "task_id": task_id,
                "action": "completed" if not error_message else "failed",
                "timestamp": time.time(),
                "duration": duration
            })
            
            self._notify_callbacks(task)
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = ProgressStatus.CANCELLED
            task.end_time = time.time()
            
            # 取消当前步骤
            if task.current_step:
                current_step = self._find_step(task, task.current_step)
                if current_step:
                    current_step.status = ProgressStatus.CANCELLED
                    current_step.end_time = time.time()
            
            self.stats["cancelled_tasks"] += 1
            
            # 记录到历史
            self.history.append({
                "task_id": task_id,
                "action": "cancelled",
                "timestamp": time.time()
            })
            
            self._notify_callbacks(task)
            return True
    
    def get_task(self, task_id: str) -> Optional[ProgressInfo]:
        """获取任务信息"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[ProgressInfo]:
        """获取所有任务"""
        with self.lock:
            return list(self.tasks.values())
    
    def get_active_tasks(self) -> List[ProgressInfo]:
        """获取活跃任务"""
        with self.lock:
            return [
                task for task in self.tasks.values()
                if task.status in [ProgressStatus.PENDING, ProgressStatus.RUNNING]
            ]
    
    def _find_step(self, task: ProgressInfo, step_name: str) -> Optional[ProgressStep]:
        """查找步骤"""
        for step in task.steps:
            if step.name == step_name:
                return step
        return None
    
    def _get_next_step(self, task: ProgressInfo) -> Optional[ProgressStep]:
        """获取下一个步骤"""
        for step in task.steps:
            if step.status == ProgressStatus.PENDING:
                return step
        return None
    
    def _update_overall_progress(self, task: ProgressInfo):
        """更新整体进度"""
        if not task.steps:
            return
        
        total_progress = 0.0
        for step in task.steps:
            if step.status == ProgressStatus.COMPLETED:
                total_progress += 1.0
            elif step.status == ProgressStatus.RUNNING:
                total_progress += step.progress
            # PENDING 步骤贡献 0
        
        task.overall_progress = total_progress / len(task.steps)
    
    def _update_estimated_completion(self, task: ProgressInfo):
        """更新预计完成时间"""
        if not task.start_time or not task.steps:
            return
        
        # 计算已完成步骤的平均时间
        completed_steps = [s for s in task.steps if s.status == ProgressStatus.COMPLETED and s.start_time and s.end_time]
        if not completed_steps:
            return
        
        avg_step_time = sum(s.end_time - s.start_time for s in completed_steps) / len(completed_steps)
        
        # 计算剩余步骤数
        remaining_steps = len([s for s in task.steps if s.status == ProgressStatus.PENDING])
        
        # 估算完成时间
        estimated_remaining_time = remaining_steps * avg_step_time
        task.estimated_completion = time.time() + estimated_remaining_time
    
    def add_callback(self, callback: Callable[[ProgressInfo], None]):
        """添加回调函数"""
        with self.lock:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[ProgressInfo], None]):
        """移除回调函数"""
        with self.lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)
    
    def _notify_callbacks(self, task: ProgressInfo):
        """通知回调函数"""
        for callback in self.callbacks:
            try:
                callback(task)
            except Exception as e:
                print(f"进度回调函数执行失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            # 直接计算活跃任务数，避免调用get_active_tasks造成死锁
            active_tasks = len([
                task for task in self.tasks.values()
                if task.status in [ProgressStatus.PENDING, ProgressStatus.RUNNING]
            ])
            return {
                **self.stats,
                "active_tasks": active_tasks,
                "total_tasks_in_history": len(self.history)
            }
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取历史记录"""
        with self.lock:
            return list(self.history)[-limit:]
    
    def cleanup_completed_tasks(self, max_age: float = 3600.0):
        """清理已完成的任务"""
        current_time = time.time()
        with self.lock:
            to_remove = []
            for task_id, task in self.tasks.items():
                if (task.status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED, ProgressStatus.CANCELLED] 
                    and task.end_time and (current_time - task.end_time) > max_age):
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]


# 全局进度跟踪器实例
_progress_tracker = None

def get_progress_tracker() -> ProgressTracker:
    """获取进度跟踪器实例"""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker()
    return _progress_tracker

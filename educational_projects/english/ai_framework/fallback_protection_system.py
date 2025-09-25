#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
降级保护系统
API不可用时自动回退到模板模式，确保系统稳定性
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from threading import Lock

class FallbackLevel(Enum):
    """降级级别"""
    NONE = "none"
    CACHE_ONLY = "cache_only"
    TEMPLATE_ONLY = "template_only"
    MINIMAL = "minimal"
    EMERGENCY = "emergency"

class ComponentStatus(Enum):
    """组件状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

@dataclass
class ServiceHealth:
    """服务健康状态"""
    component_name: str
    status: ComponentStatus
    last_check: datetime
    error_count: int = 0
    consecutive_failures: int = 0
    response_time_ms: float = 0.0
    error_message: str = ""

@dataclass
class FallbackAction:
    """降级动作记录"""
    timestamp: datetime
    component: str
    from_level: FallbackLevel
    to_level: FallbackLevel
    reason: str
    automatic: bool = True

class FallbackProtectionSystem:
    """降级保护系统"""
    
    def __init__(self):
        self.current_fallback_level = FallbackLevel.NONE
        self.component_health = {}
        self.fallback_history = []
        self.lock = Lock()
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件健康状态
        self._initialize_component_health()
        
        # 降级策略配置
        self.fallback_strategies = {
            FallbackLevel.CACHE_ONLY: {
                'ai_generation': False,
                'use_cache': True,
                'use_templates': True,
                'quality_validation': True
            },
            FallbackLevel.TEMPLATE_ONLY: {
                'ai_generation': False,
                'use_cache': False,
                'use_templates': True,
                'quality_validation': True
            },
            FallbackLevel.MINIMAL: {
                'ai_generation': False,
                'use_cache': False,
                'use_templates': True,
                'quality_validation': False
            },
            FallbackLevel.EMERGENCY: {
                'ai_generation': False,
                'use_cache': False,
                'use_templates': True,
                'quality_validation': False,
                'simplified_output': True
            }
        }
    
    def _initialize_component_health(self):
        """初始化组件健康状态"""
        components = [
            'ai_client',
            'content_cache',
            'sentence_generator',
            'exercise_generator',
            'quality_validator',
        ]
        
        for component in components:
            self.component_health[component] = ServiceHealth(
                component_name=component,
                status=ComponentStatus.UNKNOWN,
                last_check=datetime.now()
            )
    
    def check_component_health(self, component_name: str, 
                             health_check_func: Callable = None) -> ServiceHealth:
        """检查组件健康状态"""
        if component_name not in self.component_health:
            self.component_health[component_name] = ServiceHealth(
                component_name=component_name,
                status=ComponentStatus.UNKNOWN,
                last_check=datetime.now()
            )
        
        health = self.component_health[component_name]
        
        try:
            start_time = time.time()
            
            # 执行健康检查
            if health_check_func:
                is_healthy = health_check_func()
            else:
                is_healthy = self._default_health_check(component_name)
            
            response_time = (time.time() - start_time) * 1000
            
            with self.lock:
                health.last_check = datetime.now()
                health.response_time_ms = response_time
                
                if is_healthy:
                    health.status = ComponentStatus.HEALTHY
                    health.consecutive_failures = 0
                else:
                    health.error_count += 1
                    health.consecutive_failures += 1
                    health.status = ComponentStatus.DEGRADED
                
                # 检查是否需要降级
                self._evaluate_fallback_triggers()
                
        except Exception as e:
            with self.lock:
                health.last_check = datetime.now()
                health.error_count += 1
                health.consecutive_failures += 1
                health.status = ComponentStatus.OFFLINE
                health.error_message = str(e)
                
                # 立即评估降级
                self._evaluate_fallback_triggers()
        
        return health
    
    def _default_health_check(self, component_name: str) -> bool:
        """默认健康检查"""
        # 简化的健康检查逻辑
        return True
    
    def _evaluate_fallback_triggers(self):
        """评估降级触发器"""
        # 简化的降级逻辑
        max_failures = 0
        for health in self.component_health.values():
            max_failures = max(max_failures, health.consecutive_failures)
        
        if max_failures >= 5:
            self._execute_fallback(FallbackLevel.EMERGENCY, "多个组件连续失败")
        elif max_failures >= 3:
            self._execute_fallback(FallbackLevel.TEMPLATE_ONLY, "组件不稳定")
        elif max_failures >= 1:
            self._execute_fallback(FallbackLevel.CACHE_ONLY, "轻微故障")
    
    def _execute_fallback(self, target_level: FallbackLevel, reason: str):
        """执行降级"""
        old_level = self.current_fallback_level
        
        if target_level == old_level:
            return
        
        with self.lock:
            self.current_fallback_level = target_level
            
            action = FallbackAction(
                timestamp=datetime.now(),
                component="system",
                from_level=old_level,
                to_level=target_level,
                reason=reason,
                automatic=True
            )
            
            self.fallback_history.append(action)
            
            self.logger.warning(f"系统降级: {old_level.value} -> {target_level.value}, 原因: {reason}")
            
            # 应用降级策略
            self._apply_fallback_strategy(target_level)
    
    def _apply_fallback_strategy(self, fallback_level: FallbackLevel):
        """应用降级策略"""
        strategy = self.fallback_strategies.get(fallback_level, {})
        self.logger.info(f"应用降级策略: {strategy}")
    
    def manual_fallback(self, target_level: FallbackLevel, reason: str = "手动降级"):
        """手动触发降级"""
        self.logger.info(f"手动降级到: {target_level.value}, 原因: {reason}")
        
        action = FallbackAction(
            timestamp=datetime.now(),
            component="manual",
            from_level=self.current_fallback_level,
            to_level=target_level,
            reason=reason,
            automatic=False
        )
        
        with self.lock:
            self.current_fallback_level = target_level
            self.fallback_history.append(action)
            self._apply_fallback_strategy(target_level)
    
    def get_current_strategy(self) -> Dict[str, Any]:
        """获取当前降级策略"""
        strategy = self.fallback_strategies.get(self.current_fallback_level, {})
        return {
            'fallback_level': self.current_fallback_level.value,
            'strategy': strategy,
            'applied_at': self.fallback_history[-1].timestamp.isoformat() if self.fallback_history else None
        }
    
    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否在当前降级级别下可用"""
        strategy = self.fallback_strategies.get(self.current_fallback_level, {})
        return strategy.get(feature, True)
    
    def get_fallback_safe_content(self, content_type: str = "sentence", 
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取降级安全的内容"""
        context = context or {}
        word = context.get('target_word', 'example')
        chinese = context.get('chinese_meaning', '示例')
        
        if content_type == "sentence":
            return {
                'content': f"This is a {word}.",
                'chinese_translation': f"这是一个{chinese}。",
                'is_fallback': True,
                'fallback_level': self.current_fallback_level.value,
                'quality_score': 0.7
            }
        elif content_type == "exercise":
            return {
                'question': f"Fill in the blank: This is a _____.",
                'answer': word,
                'hint': f"Use the word '{word}'",
                'is_fallback': True,
                'fallback_level': self.current_fallback_level.value,
                'quality_score': 0.7
            }
        else:
            return {
                'content': f"Safe fallback content for {word}.",
                'is_fallback': True,
                'fallback_level': self.current_fallback_level.value,
                'quality_score': 0.6
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        component_statuses = {}
        
        for name, health in self.component_health.items():
            component_statuses[name] = {
                'status': health.status.value,
                'last_check': health.last_check.isoformat(),
                'error_count': health.error_count,
                'consecutive_failures': health.consecutive_failures,
            }
        
        return {
            'current_fallback_level': self.current_fallback_level.value,
            'components': component_statuses,
            'recent_actions': [
                {
                    'timestamp': action.timestamp.isoformat(),
                    'from_level': action.from_level.value,
                    'to_level': action.to_level.value,
                    'reason': action.reason,
                }
                for action in self.fallback_history[-5:]
            ]
        }
    
    def simulate_component_failure(self, component_name: str, failure_type: str = "offline"):
        """模拟组件故障（用于测试）"""
        if component_name in self.component_health:
            health = self.component_health[component_name]
            
            if failure_type == "offline":
                health.status = ComponentStatus.OFFLINE
                health.consecutive_failures = 5
            elif failure_type == "error":
                health.consecutive_failures = 3
                health.status = ComponentStatus.DEGRADED
            
            self.logger.warning(f"模拟组件故障: {component_name} - {failure_type}")
            self._evaluate_fallback_triggers()

# 全局降级保护系统实例
fallback_system = FallbackProtectionSystem()

if __name__ == "__main__":
    # 测试降级保护系统
    print("=== 降级保护系统测试 ===")
    
    # 设置日志输出
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 获取初始系统状态
    print("\n--- 初始系统状态 ---")
    status = fallback_system.get_system_status()
    print(f"当前降级级别: {status['current_fallback_level']}")
    print(f"组件数量: {len(status['components'])}")
    
    # 检查组件健康状态
    print("\n--- 组件健康检查 ---")
    for component in ["ai_client", "content_cache"]:
        health = fallback_system.check_component_health(component)
        print(f"{component}: {health.status.value}")
    
    # 模拟组件故障
    print("\n--- 模拟组件故障 ---")
    fallback_system.simulate_component_failure("ai_client", "error")
    
    current_strategy = fallback_system.get_current_strategy()
    print(f"当前策略: {current_strategy['fallback_level']}")
    print(f"AI生成启用: {fallback_system.is_feature_enabled('ai_generation')}")
    
    # 获取降级安全内容
    print("\n--- 降级安全内容生成 ---")
    safe_sentence = fallback_system.get_fallback_safe_content(
        "sentence",
        {'target_word': 'apple', 'chinese_meaning': '苹果'}
    )
    print(f"安全例句: {safe_sentence['content']}")
    print(f"是否为降级内容: {safe_sentence['is_fallback']}")
    
    print("\n降级保护系统测试完成！")
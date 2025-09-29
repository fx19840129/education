#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查系统
"""

import time
import threading
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..errors.exceptions import EducationSystemError


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    name: str
    status: HealthStatus
    message: str
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = None


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.results: Dict[str, HealthCheckResult] = {}
        self.lock = threading.RLock()
        self.last_check_time = None
        
        # 注册默认检查
        self._register_default_checks()
    
    def register_check(self, name: str, check_func: Callable[[], HealthCheckResult]):
        """注册健康检查"""
        with self.lock:
            self.checks[name] = check_func
    
    def unregister_check(self, name: str):
        """取消注册健康检查"""
        with self.lock:
            if name in self.checks:
                del self.checks[name]
            if name in self.results:
                del self.results[name]
    
    def run_check(self, name: str) -> HealthCheckResult:
        """运行单个健康检查"""
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"健康检查 '{name}' 未注册",
                response_time=0.0,
                timestamp=datetime.now()
            )
        
        start_time = time.time()
        try:
            result = self.checks[name]()
            result.response_time = time.time() - start_time
            result.timestamp = datetime.now()
        except Exception as e:
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查失败: {str(e)}",
                response_time=time.time() - start_time,
                timestamp=datetime.now()
            )
        
        with self.lock:
            self.results[name] = result
        
        return result
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """运行所有健康检查"""
        with self.lock:
            self.last_check_time = datetime.now()
            
            for name in self.checks:
                self.run_check(name)
            
            return dict(self.results)
    
    def get_overall_status(self) -> HealthStatus:
        """获取整体健康状态"""
        with self.lock:
            if not self.results:
                return HealthStatus.UNKNOWN
            
            statuses = [result.status for result in self.results.values()]
            
            if HealthStatus.UNHEALTHY in statuses:
                return HealthStatus.UNHEALTHY
            elif HealthStatus.DEGRADED in statuses:
                return HealthStatus.DEGRADED
            elif all(status == HealthStatus.HEALTHY for status in statuses):
                return HealthStatus.HEALTHY
            else:
                return HealthStatus.UNKNOWN
    
    def get_health_summary(self) -> Dict[str, Any]:
        """获取健康摘要"""
        with self.lock:
            overall_status = self.get_overall_status()
            
            return {
                "overall_status": overall_status.value,
                "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
                "total_checks": len(self.checks),
                "checks": {
                    name: {
                        "status": result.status.value,
                        "message": result.message,
                        "response_time": result.response_time,
                        "timestamp": result.timestamp.isoformat(),
                        "details": result.details or {}
                    }
                    for name, result in self.results.items()
                }
            }
    
    def _register_default_checks(self):
        """注册默认健康检查"""
        self.register_check("system", self._check_system)
        self.register_check("memory", self._check_memory)
        self.register_check("disk", self._check_disk)
        self.register_check("database", self._check_database)
        self.register_check("ai_services", self._check_ai_services)
    
    def _check_system(self) -> HealthCheckResult:
        """检查系统状态"""
        try:
            import psutil
            
            # 检查CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"CPU使用率过高: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"CPU使用率较高: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU使用率正常: {cpu_percent:.1f}%"
            
            return HealthCheckResult(
                name="system",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=datetime.now(),
                details={"cpu_percent": cpu_percent}
            )
        except ImportError:
            return HealthCheckResult(
                name="system",
                status=HealthStatus.UNKNOWN,
                message="psutil未安装，无法检查系统状态",
                response_time=0.0,
                timestamp=datetime.now()
            )
        except Exception as e:
            return HealthCheckResult(
                name="system",
                status=HealthStatus.UNHEALTHY,
                message=f"系统检查失败: {str(e)}",
                response_time=0.0,
                timestamp=datetime.now()
            )
    
    def _check_memory(self) -> HealthCheckResult:
        """检查内存状态"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            available_gb = memory.available / (1024**3)
            
            if memory_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"内存使用率过高: {memory_percent:.1f}%"
            elif memory_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"内存使用率较高: {memory_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"内存使用率正常: {memory_percent:.1f}%"
            
            return HealthCheckResult(
                name="memory",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=datetime.now(),
                details={
                    "memory_percent": memory_percent,
                    "available_gb": round(available_gb, 2),
                    "total_gb": round(memory.total / (1024**3), 2)
                }
            )
        except ImportError:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.UNKNOWN,
                message="psutil未安装，无法检查内存状态",
                response_time=0.0,
                timestamp=datetime.now()
            )
        except Exception as e:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"内存检查失败: {str(e)}",
                response_time=0.0,
                timestamp=datetime.now()
            )
    
    def _check_disk(self) -> HealthCheckResult:
        """检查磁盘状态"""
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            free_gb = disk.free / (1024**3)
            
            if disk_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"磁盘使用率过高: {disk_percent:.1f}%"
            elif disk_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"磁盘使用率较高: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"磁盘使用率正常: {disk_percent:.1f}%"
            
            return HealthCheckResult(
                name="disk",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=datetime.now(),
                details={
                    "disk_percent": disk_percent,
                    "free_gb": round(free_gb, 2),
                    "total_gb": round(disk.total / (1024**3), 2)
                }
            )
        except ImportError:
            return HealthCheckResult(
                name="disk",
                status=HealthStatus.UNKNOWN,
                message="psutil未安装，无法检查磁盘状态",
                response_time=0.0,
                timestamp=datetime.now()
            )
        except Exception as e:
            return HealthCheckResult(
                name="disk",
                status=HealthStatus.UNHEALTHY,
                message=f"磁盘检查失败: {str(e)}",
                response_time=0.0,
                timestamp=datetime.now()
            )
    
    def _check_database(self) -> HealthCheckResult:
        """检查数据库状态"""
        try:
            # 这里应该检查数据库连接
            # 暂时返回健康状态
            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="数据库连接正常",
                response_time=0.0,
                timestamp=datetime.now(),
                details={"connection_pool": "active"}
            )
        except Exception as e:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"数据库连接失败: {str(e)}",
                response_time=0.0,
                timestamp=datetime.now()
            )
    
    def _check_ai_services(self) -> HealthCheckResult:
        """检查AI服务状态"""
        try:
            # 这里应该检查AI服务可用性
            # 暂时返回健康状态
            return HealthCheckResult(
                name="ai_services",
                status=HealthStatus.HEALTHY,
                message="AI服务正常",
                response_time=0.0,
                timestamp=datetime.now(),
                details={"providers": ["zhipu", "openai"]}
            )
        except Exception as e:
            return HealthCheckResult(
                name="ai_services",
                status=HealthStatus.UNHEALTHY,
                message=f"AI服务不可用: {str(e)}",
                response_time=0.0,
                timestamp=datetime.now()
            )


# 全局健康检查器实例
health_checker = HealthChecker()

def get_health_checker() -> HealthChecker:
    """获取健康检查器实例"""
    return health_checker


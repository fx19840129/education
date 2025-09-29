#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理优化器
优化数据加载、处理、缓存和存储性能
"""

import json
import pickle
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

from ..cache.cache_manager import get_cache
from ..monitoring.metrics import get_metrics
from ..errors.exceptions import FileOperationError


@dataclass
class DataConfig:
    """数据配置"""
    cache_enabled: bool = True
    cache_ttl: int = 3600
    max_cache_size: int = 1000
    enable_compression: bool = True
    batch_size: int = 100
    max_workers: int = 4
    enable_indexing: bool = True
    auto_save: bool = True
    save_interval: float = 300.0  # 5分钟


class DataCache:
    """数据缓存"""
    
    def __init__(self, config: DataConfig):
        self.config = config
        self.cache = get_cache()
        self.metrics = get_metrics()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if not self.config.cache_enabled:
            return None
        
        try:
            data = self.cache.get(key)
            if data is not None:
                with self.lock:
                    self.cache_stats["hits"] += 1
                self.metrics.increment_counter("data_cache.hits")
                return data
            else:
                with self.lock:
                    self.cache_stats["misses"] += 1
                self.metrics.increment_counter("data_cache.misses")
                return None
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存数据"""
        if not self.config.cache_enabled:
            return False
        
        try:
            ttl = ttl or self.config.cache_ttl
            success = self.cache.set(key, data, ttl)
            
            if success:
                with self.lock:
                    self.cache_stats["size"] += 1
                self.metrics.increment_counter("data_cache.sets")
            
            return success
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            success = self.cache.delete(key)
            if success:
                with self.lock:
                    self.cache_stats["size"] = max(0, self.cache_stats["size"] - 1)
            return success
        except Exception as e:
            print(f"缓存删除失败: {e}")
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            success = self.cache.clear()
            if success:
                with self.lock:
                    self.cache_stats["size"] = 0
            return success
        except Exception as e:
            print(f"缓存清空失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self.lock:
            total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
            hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.cache_stats,
                "hit_rate": hit_rate,
                "enabled": self.config.cache_enabled
            }


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config: DataConfig):
        self.config = config
        self.cache = DataCache(config)
        self.metrics = get_metrics()
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.processing_stats = {
            "total_processed": 0,
            "successful_processed": 0,
            "failed_processed": 0,
            "average_processing_time": 0.0
        }
        self.lock = threading.Lock()
    
    def process_batch(self, data_list: List[Any], processor_func: Callable) -> List[Any]:
        """批量处理数据"""
        if not data_list:
            return []
        
        start_time = time.time()
        results = []
        
        try:
            # 分批处理
            for i in range(0, len(data_list), self.config.batch_size):
                batch = data_list[i:i + self.config.batch_size]
                batch_results = self._process_batch_chunk(batch, processor_func)
                results.extend(batch_results)
            
            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(len(data_list), processing_time, True)
            
            return results
            
        except Exception as e:
            self._update_stats(len(data_list), time.time() - start_time, False)
            raise e
    
    def _process_batch_chunk(self, batch: List[Any], processor_func: Callable) -> List[Any]:
        """处理批次数据块"""
        if len(batch) == 1:
            # 单个数据直接处理
            return [processor_func(batch[0])]
        
        # 多个数据并行处理
        futures = []
        for data in batch:
            future = self.executor.submit(processor_func, data)
            futures.append(future)
        
        results = []
        # 按顺序获取结果，保持输入顺序
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"数据处理失败: {e}")
                results.append(None)
        
        return results
    
    def _update_stats(self, count: int, processing_time: float, success: bool):
        """更新统计信息"""
        with self.lock:
            self.processing_stats["total_processed"] += count
            if success:
                self.processing_stats["successful_processed"] += count
            else:
                self.processing_stats["failed_processed"] += count
            
            # 更新平均处理时间
            total = self.processing_stats["total_processed"]
            current_avg = self.processing_stats["average_processing_time"]
            self.processing_stats["average_processing_time"] = (
                (current_avg * (total - count) + processing_time) / total
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取处理统计"""
        with self.lock:
            return {
                **self.processing_stats,
                "success_rate": (
                    self.processing_stats["successful_processed"] / 
                    max(1, self.processing_stats["total_processed"]) * 100
                )
            }


class DataStorage:
    """数据存储"""
    
    def __init__(self, config: DataConfig, db_path: str = "data.db"):
        self.config = config
        self.db_path = db_path
        self.metrics = get_metrics()
        self.connection_pool = []
        self.pool_lock = threading.Lock()
        self.auto_save_timer = None
        
        # 初始化数据库
        self._init_database()
        
        # 启动自动保存
        if config.auto_save:
            self._start_auto_save()
    
    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            # 创建数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at REAL,
                    expires_at REAL,
                    data_type TEXT
                )
            ''')
            
            # 创建索引
            if self.config.enable_indexing:
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_expires_at 
                    ON data_cache(expires_at)
                ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            raise FileOperationError(f"数据库初始化失败: {e}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        with self.pool_lock:
            if self.connection_pool:
                return self.connection_pool.pop()
            else:
                return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def _return_connection(self, conn: sqlite3.Connection):
        """归还数据库连接"""
        with self.pool_lock:
            if len(self.connection_pool) < 10:  # 限制连接池大小
                self.connection_pool.append(conn)
            else:
                conn.close()
    
    def save(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """保存数据"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 序列化数据
            if isinstance(data, (dict, list)):
                value = json.dumps(data).encode('utf-8')
                data_type = 'json'
            else:
                value = pickle.dumps(data)
                data_type = 'pickle'
            
            # 计算过期时间
            expires_at = time.time() + (ttl or self.config.cache_ttl)
            
            # 插入或更新数据
            cursor.execute('''
                INSERT OR REPLACE INTO data_cache 
                (key, value, created_at, expires_at, data_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (key, value, time.time(), expires_at, data_type))
            
            conn.commit()
            self._return_connection(conn)
            
            self.metrics.increment_counter("data_storage.saves")
            return True
            
        except Exception as e:
            print(f"数据保存失败: {e}")
            return False
    
    def load(self, key: str) -> Optional[Any]:
        """加载数据"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value, data_type, expires_at 
                FROM data_cache 
                WHERE key = ? AND expires_at > ?
            ''', (key, time.time()))
            
            row = cursor.fetchone()
            self._return_connection(conn)
            
            if row:
                value, data_type, expires_at = row
                
                # 反序列化数据
                if data_type == 'json':
                    data = json.loads(value.decode('utf-8'))
                else:
                    data = pickle.loads(value)
                
                self.metrics.increment_counter("data_storage.loads")
                return data
            
            return None
            
        except Exception as e:
            print(f"数据加载失败: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除数据"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM data_cache WHERE key = ?', (key,))
            conn.commit()
            self._return_connection(conn)
            
            self.metrics.increment_counter("data_storage.deletes")
            return True
            
        except Exception as e:
            print(f"数据删除失败: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """清理过期数据"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM data_cache WHERE expires_at <= ?', (time.time(),))
            deleted_count = cursor.rowcount
            conn.commit()
            self._return_connection(conn)
            
            self.metrics.increment_counter("data_storage.cleanups", deleted_count)
            return deleted_count
            
        except Exception as e:
            print(f"清理过期数据失败: {e}")
            return 0
    
    def _start_auto_save(self):
        """启动自动保存"""
        def auto_save_worker():
            while True:
                time.sleep(self.config.save_interval)
                self.cleanup_expired()
        
        self.auto_save_timer = threading.Thread(target=auto_save_worker, daemon=True)
        self.auto_save_timer.start()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取存储统计"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM data_cache')
            total_records = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM data_cache WHERE expires_at > ?', (time.time(),))
            active_records = cursor.fetchone()[0]
            
            self._return_connection(conn)
            
            return {
                "total_records": total_records,
                "active_records": active_records,
                "expired_records": total_records - active_records
            }
            
        except Exception as e:
            print(f"获取存储统计失败: {e}")
            return {}


class DataOptimizer:
    """数据优化器"""
    
    def __init__(self, config: DataConfig = None):
        self.config = config or DataConfig()
        self.cache = DataCache(self.config)
        self.processor = DataProcessor(self.config)
        self.storage = DataStorage(self.config)
        self.metrics = get_metrics()
    
    def get_or_process(self, key: str, processor_func: Callable, 
                      data: Any = None, ttl: Optional[int] = None) -> Any:
        """获取或处理数据"""
        # 尝试从缓存获取
        cached_data = self.cache.get(key)
        if cached_data is not None:
            return cached_data
        
        # 尝试从存储获取
        stored_data = self.storage.load(key)
        if stored_data is not None:
            # 存入缓存
            self.cache.set(key, stored_data, ttl)
            return stored_data
        
        # 处理数据
        if data is not None:
            processed_data = processor_func(data)
        else:
            processed_data = processor_func()
        
        # 保存到缓存和存储
        self.cache.set(key, processed_data, ttl)
        self.storage.save(key, processed_data, ttl)
        
        return processed_data
    
    def batch_process(self, data_list: List[Any], processor_func: Callable) -> List[Any]:
        """批量处理数据"""
        return self.processor.process_batch(data_list, processor_func)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取优化器统计"""
        return {
            "cache_stats": self.cache.get_stats(),
            "processing_stats": self.processor.get_stats(),
            "storage_stats": self.storage.get_stats()
        }
    
    def cleanup(self):
        """清理资源"""
        if self.processor.executor:
            self.processor.executor.shutdown(wait=True)


# 全局数据优化器实例
_data_optimizer = None

def get_data_optimizer() -> DataOptimizer:
    """获取数据优化器实例"""
    global _data_optimizer
    if _data_optimizer is None:
        _data_optimizer = DataOptimizer()
    return _data_optimizer

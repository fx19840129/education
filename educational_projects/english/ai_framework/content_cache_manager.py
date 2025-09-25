#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容缓存管理器
实现本地缓存避免重复API调用，提高响应速度和降低成本
"""

import json
import os
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from zhipu_ai_client import AIResponse

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: int
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl_seconds <= 0:
            return False  # 永不过期
        
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds
    
    def is_stale(self, max_age_seconds: int = 3600) -> bool:
        """检查是否陈旧（用于主动刷新）"""
        return (datetime.now() - self.created_at).total_seconds() > max_age_seconds

@dataclass
class CacheStats:
    """缓存统计"""
    total_entries: int
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float
    total_size_bytes: int
    avg_response_time_ms: float
    cost_saved_estimate: float

class ContentCacheManager:
    """内容缓存管理器"""
    
    def __init__(self, cache_dir: str = "cache", max_cache_size_mb: int = 100):
        self.cache_dir = cache_dir
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        
        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)
        
        # 缓存索引文件
        self.index_file = os.path.join(cache_dir, "cache_index.json")
        
        # 内存缓存索引
        self.cache_index: Dict[str, CacheEntry] = {}
        
        # 统计信息
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
            "total_response_time": 0,
            "cost_saved": 0.0
        }
        
        # 加载现有缓存
        self._load_cache_index()
        
        # 缓存策略配置
        self.cache_strategies = {
            "sentences": {
                "ttl_seconds": 3600,  # 1小时
                "priority": "high",
                "compress": False
            },
            "exercises": {
                "ttl_seconds": 7200,  # 2小时
                "priority": "high", 
                "compress": False
            },
            "explanations": {
                "ttl_seconds": 86400,  # 24小时
                "priority": "medium",
                "compress": True
            },
            "validations": {
                "ttl_seconds": 1800,   # 30分钟
                "priority": "low",
                "compress": True
            }
        }
    
    def _generate_cache_key(self, prompt: str, system_prompt: str = "", 
                           temperature: float = 0.7, model: str = "glm-4.5") -> str:
        """生成缓存键"""
        # 组合所有影响结果的参数
        key_content = f"{prompt}|{system_prompt}|{temperature}|{model}"
        
        # 生成MD5哈希
        key_hash = hashlib.md5(key_content.encode('utf-8')).hexdigest()
        
        return key_hash
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        # 使用前两位字符作为子目录，避免单个目录文件过多
        subdir = cache_key[:2]
        cache_subdir = os.path.join(self.cache_dir, subdir)
        os.makedirs(cache_subdir, exist_ok=True)
        
        return os.path.join(cache_subdir, f"{cache_key}.json")
    
    def _load_cache_index(self):
        """加载缓存索引"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                for key, entry_data in index_data.items():
                    # 转换日期字符串
                    entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
                    entry_data["last_accessed"] = datetime.fromisoformat(entry_data["last_accessed"])
                    
                    self.cache_index[key] = CacheEntry(**entry_data)
                
                print(f"加载了 {len(self.cache_index)} 个缓存条目")
                
            except Exception as e:
                print(f"加载缓存索引失败: {e}")
                self.cache_index = {}
    
    def _save_cache_index(self):
        """保存缓存索引"""
        try:
            index_data = {}
            for key, entry in self.cache_index.items():
                entry_dict = asdict(entry)
                # 转换日期为字符串
                entry_dict["created_at"] = entry.created_at.isoformat()
                entry_dict["last_accessed"] = entry.last_accessed.isoformat()
                index_data[key] = entry_dict
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存缓存索引失败: {e}")
    
    def get_cached_content(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取缓存内容"""
        self.stats["total_requests"] += 1
        start_time = time.time()
        
        try:
            if cache_key not in self.cache_index:
                self.stats["cache_misses"] += 1
                return None
            
            entry = self.cache_index[cache_key]
            
            # 检查是否过期
            if entry.is_expired():
                print(f"缓存已过期: {cache_key}")
                self._remove_cache_entry(cache_key)
                self.stats["cache_misses"] += 1
                return None
            
            # 从文件加载内容
            cache_file = self._get_cache_file_path(cache_key)
            if not os.path.exists(cache_file):
                print(f"缓存文件不存在: {cache_file}")
                self._remove_cache_entry(cache_key)
                self.stats["cache_misses"] += 1
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # 更新访问统计
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            # 记录命中统计
            self.stats["cache_hits"] += 1
            response_time = (time.time() - start_time) * 1000
            self.stats["total_response_time"] += response_time
            
            # 估算节省的成本
            self.stats["cost_saved"] += self._estimate_api_cost(cached_data.get("tokens_used", 100))
            
            print(f"缓存命中: {cache_key[:8]}... (响应时间: {response_time:.1f}ms)")
            
            return cached_data
            
        except Exception as e:
            print(f"读取缓存失败: {e}")
            self.stats["cache_misses"] += 1
            return None
    
    def store_content(self, cache_key: str, content: str, 
                     content_type: str = "general",
                     metadata: Dict[str, Any] = None,
                     api_response: AIResponse = None) -> bool:
        """存储内容到缓存"""
        try:
            if metadata is None:
                metadata = {}
            
            # 获取缓存策略
            strategy = self.cache_strategies.get(content_type, self.cache_strategies["sentences"])
            
            # 准备缓存数据
            cache_data = {
                "content": content,
                "content_type": content_type,
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "tokens_used": api_response.usage.get("total_tokens", 0) if api_response else 0,
                "model": api_response.model if api_response else "unknown"
            }
            
            # 存储到文件
            cache_file = self._get_cache_file_path(cache_key)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            # 创建缓存条目
            cache_entry = CacheEntry(
                key=cache_key,
                content=content,
                metadata=metadata,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                ttl_seconds=strategy["ttl_seconds"]
            )
            
            # 添加到索引
            self.cache_index[cache_key] = cache_entry
            
            # 检查缓存大小限制
            self._enforce_cache_size_limit()
            
            # 保存索引
            self._save_cache_index()
            
            print(f"内容已缓存: {cache_key[:8]}... (TTL: {strategy['ttl_seconds']}s)")
            
            return True
            
        except Exception as e:
            print(f"存储缓存失败: {e}")
            return False
    
    def _remove_cache_entry(self, cache_key: str):
        """删除缓存条目"""
        try:
            # 删除文件
            cache_file = self._get_cache_file_path(cache_key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
            
            # 从索引中删除
            if cache_key in self.cache_index:
                del self.cache_index[cache_key]
                
        except Exception as e:
            print(f"删除缓存条目失败: {e}")
    
    def _enforce_cache_size_limit(self):
        """强制执行缓存大小限制"""
        current_size = self._calculate_cache_size()
        
        if current_size > self.max_cache_size_bytes:
            print(f"缓存超出限制 ({current_size / 1024 / 1024:.1f}MB)，清理旧条目...")
            
            # 按最后访问时间排序
            sorted_entries = sorted(
                self.cache_index.items(),
                key=lambda x: x[1].last_accessed
            )
            
            # 删除最旧的条目直到满足大小限制
            removed_count = 0
            for cache_key, entry in sorted_entries:
                self._remove_cache_entry(cache_key)
                removed_count += 1
                
                current_size = self._calculate_cache_size()
                if current_size <= self.max_cache_size_bytes * 0.8:  # 留20%余量
                    break
            
            print(f"清理了 {removed_count} 个缓存条目")
    
    def _calculate_cache_size(self) -> int:
        """计算当前缓存大小"""
        total_size = 0
        
        for cache_key in self.cache_index.keys():
            cache_file = self._get_cache_file_path(cache_key)
            if os.path.exists(cache_file):
                total_size += os.path.getsize(cache_file)
        
        return total_size
    
    def _estimate_api_cost(self, tokens: int) -> float:
        """估算API成本节省"""
        # 假设智谱GLM-4.5的价格（每1K tokens）
        input_cost_per_1k = 0.00015  # $0.00015 per 1K input tokens
        output_cost_per_1k = 0.0006  # $0.0006 per 1K output tokens
        
        # 简化计算，假设输入输出各占一半
        estimated_cost = (tokens / 1000) * (input_cost_per_1k + output_cost_per_1k) / 2
        
        return estimated_cost
    
    def cleanup_expired_cache(self):
        """清理过期缓存"""
        expired_keys = []
        
        for cache_key, entry in self.cache_index.items():
            if entry.is_expired():
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            self._remove_cache_entry(cache_key)
        
        if expired_keys:
            print(f"清理了 {len(expired_keys)} 个过期缓存条目")
            self._save_cache_index()
    
    def preload_common_content(self, common_words: List[str], 
                             grammar_topics: List[str]):
        """预加载常用内容"""
        print("开始预加载常用内容...")
        
        # 这里可以实现预加载逻辑
        # 例如为常用单词和语法主题预生成内容
        preload_count = 0
        
        for word in common_words[:10]:  # 限制预加载数量
            for topic in grammar_topics[:3]:
                # 生成缓存键（示例）
                cache_key = self._generate_cache_key(
                    f"Generate sentence for {word} with {topic}",
                    "You are an English teacher"
                )
                
                # 检查是否已缓存
                if cache_key not in self.cache_index:
                    # 这里可以调用实际的生成逻辑
                    # 暂时跳过实际生成
                    preload_count += 1
        
        print(f"预加载完成，识别出 {preload_count} 个需要预生成的内容")
    
    def get_cache_statistics(self) -> CacheStats:
        """获取缓存统计信息"""
        total_requests = self.stats["total_requests"]
        cache_hits = self.stats["cache_hits"]
        cache_misses = self.stats["cache_misses"]
        
        hit_rate = cache_hits / total_requests if total_requests > 0 else 0
        avg_response_time = (self.stats["total_response_time"] / cache_hits) if cache_hits > 0 else 0
        
        return CacheStats(
            total_entries=len(self.cache_index),
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            cache_hit_rate=hit_rate,
            total_size_bytes=self._calculate_cache_size(),
            avg_response_time_ms=avg_response_time,
            cost_saved_estimate=self.stats["cost_saved"]
        )
    
    def optimize_cache(self):
        """优化缓存"""
        print("开始缓存优化...")
        
        # 清理过期条目
        self.cleanup_expired_cache()
        
        # 识别低价值缓存条目（访问次数少且陈旧）
        low_value_keys = []
        now = datetime.now()
        
        for cache_key, entry in self.cache_index.items():
            age_hours = (now - entry.created_at).total_seconds() / 3600
            
            # 超过1天且访问次数少于3次的条目
            if age_hours > 24 and entry.access_count < 3:
                low_value_keys.append(cache_key)
        
        # 删除低价值条目
        for cache_key in low_value_keys:
            self._remove_cache_entry(cache_key)
        
        if low_value_keys:
            print(f"删除了 {len(low_value_keys)} 个低价值缓存条目")
            self._save_cache_index()
        
        # 重新计算统计信息
        current_size = self._calculate_cache_size()
        print(f"缓存优化完成，当前大小: {current_size / 1024 / 1024:.1f}MB")
    
    def export_cache_report(self, output_file: str = "cache_report.json"):
        """导出缓存报告"""
        stats = self.get_cache_statistics()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": asdict(stats),
            "cache_entries": [],
            "top_accessed_content": [],
            "content_type_distribution": {}
        }
        
        # 统计内容类型分布
        type_counts = {}
        top_entries = []
        
        for cache_key, entry in self.cache_index.items():
            content_type = entry.metadata.get("content_type", "unknown")
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
            
            top_entries.append({
                "key": cache_key[:16] + "...",
                "content_type": content_type,
                "access_count": entry.access_count,
                "created_at": entry.created_at.isoformat(),
                "last_accessed": entry.last_accessed.isoformat()
            })
        
        # 按访问次数排序
        top_entries.sort(key=lambda x: x["access_count"], reverse=True)
        
        report["content_type_distribution"] = type_counts
        report["top_accessed_content"] = top_entries[:20]  # 前20个
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"缓存报告已导出到: {output_file}")
        
        return report

# 全局缓存管理器实例
cache_manager = ContentCacheManager()

if __name__ == "__main__":
    # 测试缓存管理器
    print("=== 内容缓存管理器测试 ===")
    
    # 测试缓存存储和获取
    test_key = cache_manager._generate_cache_key(
        "Generate a sentence with 'apple'",
        "You are an English teacher",
        0.7
    )
    
    print(f"生成的缓存键: {test_key}")
    
    # 测试存储
    success = cache_manager.store_content(
        test_key,
        "I like to eat an apple every day.",
        content_type="sentences",
        metadata={"word": "apple", "grammar": "一般现在时"}
    )
    
    print(f"存储成功: {success}")
    
    # 测试获取
    cached_content = cache_manager.get_cached_content(test_key)
    print(f"缓存内容: {cached_content}")
    
    # 再次获取（测试命中）
    cached_content = cache_manager.get_cached_content(test_key)
    print(f"第二次获取: {'命中' if cached_content else '未命中'}")
    
    # 获取统计信息
    stats = cache_manager.get_cache_statistics()
    print(f"\n缓存统计:")
    print(f"  总条目数: {stats.total_entries}")
    print(f"  命中次数: {stats.cache_hits}")
    print(f"  未命中次数: {stats.cache_misses}")
    print(f"  命中率: {stats.cache_hit_rate:.2%}")
    print(f"  缓存大小: {stats.total_size_bytes / 1024:.1f}KB")
    print(f"  平均响应时间: {stats.avg_response_time_ms:.1f}ms")
    print(f"  节省成本估算: ${stats.cost_saved_estimate:.6f}")
    
    # 导出报告
    report = cache_manager.export_cache_report("test_cache_report.json")
    print(f"\n报告导出完成，内容类型分布: {report['content_type_distribution']}")

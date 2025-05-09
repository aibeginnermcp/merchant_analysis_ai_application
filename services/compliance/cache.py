"""缓存管理模块"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import aioredis
from .models import ComplianceStatus, ComplianceReport

class ComplianceCache:
    """合规缓存管理器"""
    
    def __init__(self, redis_url: str = "redis://redis:6379"):
        """初始化缓存管理器"""
        self.redis = aioredis.from_url(redis_url)
        self.default_ttl = 3600  # 默认缓存1小时
        
    async def get_merchant_status(
        self,
        merchant_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取商户状态(带缓存)"""
        cache_key = f"merchant_status:{merchant_id}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
        
    async def set_merchant_status(
        self,
        merchant_id: str,
        status: Dict[str, Any],
        ttl: int = None
    ) -> None:
        """设置商户状态缓存"""
        cache_key = f"merchant_status:{merchant_id}"
        await self.redis.set(
            cache_key,
            json.dumps(status),
            ex=ttl or self.default_ttl
        )
        
    async def get_compliance_report(
        self,
        merchant_id: str,
        report_date: str
    ) -> Optional[ComplianceReport]:
        """获取合规报告(带缓存)"""
        cache_key = f"compliance_report:{merchant_id}:{report_date}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            report_dict = json.loads(cached_data)
            return ComplianceReport(**report_dict)
        return None
        
    async def set_compliance_report(
        self,
        merchant_id: str,
        report_date: str,
        report: ComplianceReport,
        ttl: int = None
    ) -> None:
        """设置合规报告缓存"""
        cache_key = f"compliance_report:{merchant_id}:{report_date}"
        await self.redis.set(
            cache_key,
            json.dumps(report.dict()),
            ex=ttl or self.default_ttl
        )
        
    async def get_compliance_rules(
        self,
        category: str = None
    ) -> Optional[Dict[str, Any]]:
        """获取合规规则(带缓存)"""
        cache_key = f"compliance_rules:{category or 'all'}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
        
    async def set_compliance_rules(
        self,
        rules: Dict[str, Any],
        category: str = None,
        ttl: int = None
    ) -> None:
        """设置合规规则缓存"""
        cache_key = f"compliance_rules:{category or 'all'}"
        await self.redis.set(
            cache_key,
            json.dumps(rules),
            ex=ttl or self.default_ttl
        )
        
    async def invalidate_merchant_cache(self, merchant_id: str) -> None:
        """清除商户相关的所有缓存"""
        # 删除状态缓存
        await self.redis.delete(f"merchant_status:{merchant_id}")
        
        # 删除报告缓存
        pattern = f"compliance_report:{merchant_id}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
            
    async def get_cached_violations(
        self,
        merchant_id: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Optional[List[Dict[str, Any]]]:
        """获取违规记录缓存"""
        cache_key = f"violations:{merchant_id}"
        if start_date and end_date:
            cache_key += f":{start_date.date()}:{end_date.date()}"
            
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None
        
    async def set_cached_violations(
        self,
        merchant_id: str,
        violations: List[Dict[str, Any]],
        start_date: datetime = None,
        end_date: datetime = None,
        ttl: int = None
    ) -> None:
        """设置违规记录缓存"""
        cache_key = f"violations:{merchant_id}"
        if start_date and end_date:
            cache_key += f":{start_date.date()}:{end_date.date()}"
            
        await self.redis.set(
            cache_key,
            json.dumps(violations),
            ex=ttl or self.default_ttl
        )
        
    async def close(self) -> None:
        """关闭Redis连接"""
        await self.redis.close() 
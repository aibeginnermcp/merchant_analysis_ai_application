"""
缓存管理模块
"""
from typing import Optional, Any
import json
from datetime import timedelta
import aioredis
from src.shared.config import settings

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        """初始化缓存管理器"""
        self._redis: Optional[aioredis.Redis] = None
        
    async def connect(self):
        """连接Redis"""
        try:
            self._redis = await aioredis.create_redis_pool(
                settings.REDIS_URI,
                encoding='utf-8'
            )
            print("Redis连接成功")
        except Exception as e:
            print(f"Redis连接失败: {e}")
            raise
            
    async def disconnect(self):
        """断开Redis连接"""
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()
            print("Redis连接已关闭")
            
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Any: 缓存值
        """
        if not self._redis:
            raise ConnectionError("Redis未连接")
            
        value = await self._redis.get(key)
        if value:
            return json.loads(value)
        return None
        
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ):
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间(秒)
        """
        if not self._redis:
            raise ConnectionError("Redis未连接")
            
        await self._redis.set(
            key,
            json.dumps(value),
            expire=expire
        )
        
    async def delete(self, key: str):
        """删除缓存
        
        Args:
            key: 缓存键
        """
        if not self._redis:
            raise ConnectionError("Redis未连接")
            
        await self._redis.delete(key)
        
    async def clear(self):
        """清空缓存"""
        if not self._redis:
            raise ConnectionError("Redis未连接")
            
        await self._redis.flushdb()
        
    async def get_merchant_cache_key(self, merchant_id: str) -> str:
        """获取商户缓存键
        
        Args:
            merchant_id: 商户ID
            
        Returns:
            str: 缓存键
        """
        return f"merchant:{merchant_id}"
        
    async def get_analysis_cache_key(
        self,
        merchant_id: str,
        analysis_type: str
    ) -> str:
        """获取分析结果缓存键
        
        Args:
            merchant_id: 商户ID
            analysis_type: 分析类型
            
        Returns:
            str: 缓存键
        """
        return f"analysis:{merchant_id}:{analysis_type}"

# 创建全局缓存管理器实例
cache_manager = CacheManager() 
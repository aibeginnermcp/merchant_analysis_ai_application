"""
缓存管理模块
"""
import json
from typing import Optional, Any, TypeVar, Type
from datetime import datetime, timedelta
import aioredis
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_uri: str):
        """初始化缓存管理器
        
        Args:
            redis_uri: Redis连接URI
        """
        self.redis = aioredis.from_url(redis_uri)
        
    async def get(
        self,
        key: str,
        model: Type[T]
    ) -> Optional[T]:
        """获取缓存数据
        
        Args:
            key: 缓存键
            model: Pydantic模型类
            
        Returns:
            Optional[T]: 缓存的数据对象
        """
        data = await self.redis.get(key)
        if data:
            return model.parse_raw(data)
        return None
        
    async def set(
        self,
        key: str,
        value: BaseModel,
        expire: int = 3600
    ) -> None:
        """设置缓存数据
        
        Args:
            key: 缓存键
            value: 要缓存的数据对象
            expire: 过期时间(秒)
        """
        await self.redis.set(
            key,
            value.json(),
            ex=expire
        )
        
    async def delete(self, key: str) -> None:
        """删除缓存数据
        
        Args:
            key: 缓存键
        """
        await self.redis.delete(key)
        
    async def exists(self, key: str) -> bool:
        """检查键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        return await self.redis.exists(key)
        
    def get_key(
        self,
        service: str,
        resource: str,
        resource_id: str
    ) -> str:
        """生成缓存键
        
        Args:
            service: 服务名称
            resource: 资源类型
            resource_id: 资源ID
            
        Returns:
            str: 缓存键
        """
        return f"merchant_bi:{service}:{resource}:{resource_id}"
        
    async def clear_pattern(self, pattern: str) -> None:
        """清除匹配模式的所有缓存
        
        Args:
            pattern: 匹配模式
        """
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
            
    async def set_with_version(
        self,
        key: str,
        value: BaseModel,
        version: int,
        expire: int = 3600
    ) -> None:
        """设置带版本的缓存数据
        
        Args:
            key: 缓存键
            value: 要缓存的数据对象
            version: 数据版本
            expire: 过期时间(秒)
        """
        data = {
            "version": version,
            "data": value.dict()
        }
        await self.redis.set(
            key,
            json.dumps(data),
            ex=expire
        )
        
    async def get_with_version(
        self,
        key: str,
        model: Type[T],
        min_version: Optional[int] = None
    ) -> Optional[tuple[T, int]]:
        """获取带版本的缓存数据
        
        Args:
            key: 缓存键
            model: Pydantic模型类
            min_version: 最小版本要求
            
        Returns:
            Optional[tuple[T, int]]: (数据对象, 版本号)
        """
        data = await self.redis.get(key)
        if data:
            cached = json.loads(data)
            version = cached["version"]
            if min_version is None or version >= min_version:
                return model.parse_obj(cached["data"]), version
        return None 
"""
商户智能经营分析平台缓存管理模块

提供基于Redis的缓存管理功能，包括：
- 数据缓存
- 缓存失效
- 分布式锁
- 速率限制
"""

import json
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from functools import wraps

import redis
from redis.lock import Lock

# 类型变量定义
T = TypeVar('T')
CacheableData = Union[str, int, float, dict, list]

class CacheManager:
    """缓存管理器，提供Redis缓存操作封装"""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        service_name: str,
        default_ttl: int = 3600
    ):
        """
        初始化缓存管理器
        
        Args:
            redis_client: Redis客户端实例
            service_name: 服务名称
            default_ttl: 默认缓存过期时间(秒)
        """
        self.redis = redis_client
        self.service_name = service_name
        self.default_ttl = default_ttl
        
    def _build_key(self, resource: str, resource_id: str) -> str:
        """
        构建缓存键名
        
        Args:
            resource: 资源类型
            resource_id: 资源ID
            
        Returns:
            str: 格式化的缓存键名
        """
        return f'merchant_bi:{self.service_name}:{resource}:{resource_id}'
    
    def get(
        self,
        resource: str,
        resource_id: str,
        default: Any = None
    ) -> Any:
        """
        获取缓存数据
        
        Args:
            resource: 资源类型
            resource_id: 资源ID
            default: 默认值
            
        Returns:
            Any: 缓存数据或默认值
        """
        key = self._build_key(resource, resource_id)
        data = self.redis.get(key)
        
        if data is None:
            return default
            
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data.decode()
            
    def set(
        self,
        resource: str,
        resource_id: str,
        value: CacheableData,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存数据
        
        Args:
            resource: 资源类型
            resource_id: 资源ID
            value: 缓存数据
            ttl: 过期时间(秒)
            
        Returns:
            bool: 是否设置成功
        """
        key = self._build_key(resource, resource_id)
        
        try:
            data = json.dumps(value)
            return bool(
                self.redis.set(
                    key,
                    data,
                    ex=ttl or self.default_ttl
                )
            )
        except (TypeError, json.JSONEncodeError):
            return False
            
    def delete(self, resource: str, resource_id: str) -> bool:
        """
        删除缓存数据
        
        Args:
            resource: 资源类型
            resource_id: 资源ID
            
        Returns:
            bool: 是否删除成功
        """
        key = self._build_key(resource, resource_id)
        return bool(self.redis.delete(key))
        
    def exists(self, resource: str, resource_id: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            resource: 资源类型
            resource_id: 资源ID
            
        Returns:
            bool: 缓存是否存在
        """
        key = self._build_key(resource, resource_id)
        return bool(self.redis.exists(key))
        
    def acquire_lock(
        self,
        resource: str,
        resource_id: str,
        ttl: int = 30
    ) -> Lock:
        """
        获取分布式锁
        
        Args:
            resource: 资源类型
            resource_id: 资源ID
            ttl: 锁超时时间(秒)
            
        Returns:
            Lock: Redis分布式锁对象
        """
        lock_key = f'lock:{self._build_key(resource, resource_id)}'
        return self.redis.lock(
            lock_key,
            timeout=ttl,
            blocking=True,
            blocking_timeout=5
        )
        
    def cached(
        self,
        resource: str,
        key_func: Callable[..., str],
        ttl: Optional[int] = None
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        缓存装饰器
        
        Args:
            resource: 资源类型
            key_func: 缓存键生成函数
            ttl: 过期时间(秒)
            
        Returns:
            Callable: 装饰器函数
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                # 生成缓存键
                resource_id = key_func(*args, **kwargs)
                
                # 尝试获取缓存
                cached_data = self.get(resource, resource_id)
                if cached_data is not None:
                    return cached_data  # type: ignore
                    
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 设置缓存
                self.set(resource, resource_id, result, ttl)
                
                return result
                
            return wrapper
        return decorator
        
    def rate_limit(
        self,
        resource: str,
        key_func: Callable[..., str],
        limit: int,
        period: int = 60
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        速率限制装饰器
        
        Args:
            resource: 资源类型
            key_func: 限制键生成函数
            limit: 时间窗口内的最大请求数
            period: 时间窗口大小(秒)
            
        Returns:
            Callable: 装饰器函数
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> T:
                # 生成限制键
                resource_id = key_func(*args, **kwargs)
                rate_key = f'rate:{self._build_key(resource, resource_id)}'
                
                # 获取当前计数
                current = self.redis.get(rate_key)
                if current is None:
                    # 首次请求，初始化计数器
                    pipe = self.redis.pipeline()
                    pipe.set(rate_key, 1, ex=period)
                    pipe.execute()
                else:
                    # 增加计数
                    count = int(current)
                    if count >= limit:
                        raise Exception(f'Rate limit exceeded: {limit} requests per {period} seconds')
                        
                    self.redis.incr(rate_key)
                    
                return await func(*args, **kwargs)
                
            return wrapper
        return decorator 
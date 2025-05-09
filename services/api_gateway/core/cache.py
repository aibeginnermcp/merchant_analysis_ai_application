"""缓存模块"""
from typing import Any, Optional
import json
from datetime import datetime
from fastapi import FastAPI, Request, Response
from redis.asyncio import Redis

class Cache:
    """缓存管理器"""
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """设置缓存"""
        return await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        return await self.redis.delete(key) > 0

def setup_cache(app: FastAPI):
    """设置缓存"""
    redis = Redis(
        host="redis",
        port=6379,
        decode_responses=True
    )

    @app.middleware("http")
    async def cache_middleware(request: Request, call_next):
        """缓存中间件"""
        if request.method != "GET":
            return await call_next(request)

        cache = Cache(redis)
        cache_key = f"cache:{request.url.path}"

        # 尝试从缓存获取
        cached_response = await cache.get(cache_key)
        if cached_response:
            return Response(
                content=cached_response,
                media_type="application/json"
            )

        # 获取响应
        response = await call_next(request)

        # 只缓存成功的响应
        if response.status_code == 200:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # 缓存响应
            await cache.set(
                cache_key,
                response_body.decode(),
                expire=3600
            )

            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )

        return response 
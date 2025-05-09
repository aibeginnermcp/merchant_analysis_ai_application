"""限流模块"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import time
from typing import Dict, Optional
import asyncio

class RateLimiter:
    """令牌桶限流器"""
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # 令牌生成速率（每秒）
        self.capacity = capacity  # 桶容量
        self.tokens = capacity  # 当前令牌数
        self.last_update = time.time()  # 上次更新时间
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        """获取令牌"""
        async with self.lock:
            now = time.time()
            # 计算新增令牌
            time_passed = now - self.last_update
            new_tokens = time_passed * self.rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

def setup_rate_limit(app: FastAPI):
    """设置限流"""
    limiter = RateLimiter(rate=10.0, capacity=100)

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """限流中间件"""
        if not await limiter.acquire():
            return JSONResponse(
                status_code=429,
                content={"error": "请求过于频繁，请稍后重试"}
            )
        return await call_next(request) 
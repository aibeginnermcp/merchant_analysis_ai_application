"""断路器模块"""
import time
import asyncio
from typing import Optional, Dict, Any
from enum import Enum
from contextlib import asynccontextmanager

class CircuitState(Enum):
    """断路器状态"""
    CLOSED = "closed"  # 正常状态
    OPEN = "open"  # 断开状态
    HALF_OPEN = "half_open"  # 半开状态

class CircuitBreaker:
    """断路器实现"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        retry_timeout: int = 5
    ):
        """初始化断路器
        
        Args:
            failure_threshold: 失败阈值
            recovery_timeout: 恢复超时时间（秒）
            retry_timeout: 重试超时时间（秒）
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.retry_timeout = retry_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.lock = asyncio.Lock()
        
    @asynccontextmanager
    async def __call__(self):
        """使用上下文管理器包装请求
        
        Raises:
            Exception: 当断路器处于打开状态时抛出异常
        """
        await self._before_request()
        try:
            yield
            await self._on_success()
        except Exception as e:
            await self._on_failure()
            raise e
            
    async def _before_request(self):
        """请求前检查断路器状态"""
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    # 进入半开状态
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")
                    
    async def _on_success(self):
        """请求成功处理"""
        async with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
            
    async def _on_failure(self):
        """请求失败处理"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if (
                self.state == CircuitState.HALF_OPEN or
                self.failure_count >= self.failure_threshold
            ):
                self.state = CircuitState.OPEN
                
    @property
    def is_open(self) -> bool:
        """断路器是否处于打开状态"""
        return self.state == CircuitState.OPEN
        
    @property
    def is_closed(self) -> bool:
        """断路器是否处于关闭状态"""
        return self.state == CircuitState.CLOSED
        
    @property
    def is_half_open(self) -> bool:
        """断路器是否处于半开状态"""
        return self.state == CircuitState.HALF_OPEN 
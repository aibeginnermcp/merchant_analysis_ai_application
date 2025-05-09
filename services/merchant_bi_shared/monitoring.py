"""
商户智能经营分析平台监控模块

提供统一的指标收集和监控功能，包括：
- 请求计数
- 响应时间
- 错误统计
- 资源使用率
- 业务指标
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from prometheus_client import Counter, Gauge, Histogram, Summary
import psutil

from .errors import MerchantBIError

# 类型变量定义
F = TypeVar('F', bound=Callable[..., Any])

class MetricsCollector:
    """指标收集器，用于收集和导出监控指标"""
    
    def __init__(self, service_name: str):
        """
        初始化指标收集器
        
        Args:
            service_name: 服务名称
        """
        self.service_name = service_name
        
        # 请求相关指标
        self.request_counter = Counter(
            f'merchant_bi_{service_name}_requests_total',
            '请求总数',
            ['method', 'endpoint']
        )
        
        self.request_duration = Histogram(
            f'merchant_bi_{service_name}_request_duration_seconds',
            '请求处理时间',
            ['method', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.request_in_progress = Gauge(
            f'merchant_bi_{service_name}_requests_in_progress',
            '正在处理的请求数',
            ['method', 'endpoint']
        )
        
        # 错误相关指标
        self.error_counter = Counter(
            f'merchant_bi_{service_name}_errors_total',
            '错误总数',
            ['type', 'code']
        )
        
        # 资源使用指标
        self.cpu_usage = Gauge(
            f'merchant_bi_{service_name}_cpu_usage_percent',
            'CPU使用率'
        )
        
        self.memory_usage = Gauge(
            f'merchant_bi_{service_name}_memory_usage_bytes',
            '内存使用量'
        )
        
        # 业务指标
        self.business_counter = Counter(
            f'merchant_bi_{service_name}_business_operations_total',
            '业务操作计数',
            ['operation']
        )
        
        self.business_duration = Summary(
            f'merchant_bi_{service_name}_business_operation_duration_seconds',
            '业务操作耗时',
            ['operation']
        )
    
    def track_request(self, method: str, endpoint: str) -> Callable[[F], F]:
        """
        请求跟踪装饰器
        
        Args:
            method: HTTP方法
            endpoint: 请求路径
            
        Returns:
            Callable: 装饰器函数
        """
        def decorator(func: F) -> F:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # 增加请求计数
                self.request_counter.labels(
                    method=method,
                    endpoint=endpoint
                ).inc()
                
                # 记录正在处理的请求
                in_progress = self.request_in_progress.labels(
                    method=method,
                    endpoint=endpoint
                )
                in_progress.inc()
                
                try:
                    # 记录请求处理时间
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    
                    self.request_duration.labels(
                        method=method,
                        endpoint=endpoint
                    ).observe(time.time() - start_time)
                    
                    return result
                    
                except Exception as e:
                    # 记录错误
                    if isinstance(e, MerchantBIError):
                        self.error_counter.labels(
                            type=e.__class__.__name__,
                            code=str(e.code)
                        ).inc()
                    else:
                        self.error_counter.labels(
                            type='UnhandledError',
                            code='9999'
                        ).inc()
                    raise
                    
                finally:
                    # 减少正在处理的请求计数
                    in_progress.dec()
                    
            return wrapper  # type: ignore
        return decorator
    
    def track_business_operation(
        self,
        operation: str
    ) -> Callable[[F], F]:
        """
        业务操作跟踪装饰器
        
        Args:
            operation: 业务操作名称
            
        Returns:
            Callable: 装饰器函数
        """
        def decorator(func: F) -> F:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # 增加操作计数
                self.business_counter.labels(
                    operation=operation
                ).inc()
                
                # 记录操作耗时
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    self.business_duration.labels(
                        operation=operation
                    ).observe(time.time() - start_time)
                    
            return wrapper  # type: ignore
        return decorator
    
    def collect_resource_metrics(self) -> None:
        """收集资源使用指标"""
        # 收集CPU使用率
        self.cpu_usage.set(psutil.cpu_percent())
        
        # 收集内存使用量
        memory = psutil.Process().memory_info()
        self.memory_usage.set(memory.rss)  # 实际使用的物理内存
        
    def record_error(
        self,
        error: Exception,
        error_type: Optional[str] = None,
        error_code: Optional[str] = None
    ) -> None:
        """
        记录错误指标
        
        Args:
            error: 异常对象
            error_type: 错误类型
            error_code: 错误码
        """
        if isinstance(error, MerchantBIError):
            self.error_counter.labels(
                type=error.__class__.__name__,
                code=str(error.code)
            ).inc()
        else:
            self.error_counter.labels(
                type=error_type or 'UnhandledError',
                code=error_code or '9999'
            ).inc() 
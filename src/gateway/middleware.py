"""
中间件模块
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram

# 定义Prometheus指标
REQUEST_COUNT = Counter(
    'http_request_total',
    'Total HTTP Request Count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Duration',
    ['method', 'endpoint']
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Prometheus监控中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            Response: 响应对象
        """
        start_time = time.time()
        
        response = await call_next(request)
        
        # 记录请求数量
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        # 记录请求延迟
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个处理函数
            
        Returns:
            Response: 响应对象
        """
        # 记录请求开始
        print(f"开始处理请求: {request.method} {request.url}")
        start_time = time.time()
        
        response = await call_next(request)
        
        # 记录请求结束
        process_time = time.time() - start_time
        print(f"请求处理完成: {response.status_code} ({process_time:.2f}s)")
        
        return response

def setup_middleware(app):
    """设置中间件
    
    Args:
        app: FastAPI应用实例
    """
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该限制来源
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加Prometheus监控中间件
    app.add_middleware(PrometheusMiddleware)
    
    # 添加日志中间件
    app.add_middleware(LoggingMiddleware) 
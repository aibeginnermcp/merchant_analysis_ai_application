"""
中间件模块

实现以下中间件：
- 认证中间件
- 日志中间件
- 错误处理中间件
- 性能监控中间件
- 请求ID中间件
"""

import time
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from jose import JWTError, jwt
from prometheus_client import Counter, Histogram
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .models import ErrorResponse, ErrorCode, BaseResponse
from .config import settings

# Prometheus指标
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests count",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/metrics", "/health"]
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    error_code=ErrorCode.UNAUTHORIZED,
                    message="Missing authentication token"
                ).dict()
            )
            
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
                
            payload = jwt.decode(
                token,
                settings.security.SECRET_KEY,
                algorithms=[settings.security.ALGORITHM]
            )
            request.state.user = payload
            
        except (JWTError, ValueError) as e:
            return JSONResponse(
                status_code=401,
                content=ErrorResponse(
                    error_code=ErrorCode.UNAUTHORIZED,
                    message=str(e)
                ).dict()
            )
            
        return await call_next(request)

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        logger.bind(request_id=request_id)
        
        # 记录请求信息
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # 记录响应信息
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} "
            f"Completed in {process_time:.3f}s"
        )
        
        response.headers["X-Request-ID"] = request_id
        return response

class MetricsMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        path = request.url.path
        
        start_time = time.time()
        response = await call_next(request)
        
        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=method,
            endpoint=path
        ).observe(time.time() - start_time)
        
        return response

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await call_next(request)
            
        except Exception as e:
            logger.exception("Unhandled exception occurred")
            
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error_code=ErrorCode.INTERNAL_ERROR,
                    message="Internal server error",
                    error_details={"error": str(e)}
                ).dict()
            )

class TracingMiddleware:
    """链路追踪中间件"""
    
    def __init__(self, app):
        self.app = app
        self.tracer = trace.get_tracer(__name__)
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 开始追踪
        with self.tracer.start_as_current_span(
            name=f"{request.method} {request.url.path}",
            kind=trace.SpanKind.SERVER,
        ) as span:
            # 设置span属性
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.request_id", request_id)
            
            try:
                # 调用下一个中间件或路由处理器
                response = await call_next(request)
                
                # 记录响应信息
                span.set_attribute("http.status_code", response.status_code)
                span.set_status(Status(StatusCode.OK))
                
                # 更新Prometheus指标
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=request.method,
                    endpoint=request.url.path
                ).observe(time.time() - start_time)
                
                return response
                
            except Exception as e:
                # 记录异常信息
                span.set_attribute("error", True)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                span.set_status(Status(StatusCode.ERROR))
                
                # 更新Prometheus指标
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=500
                ).inc()
                
                # 重新抛出异常
                raise

class ResponseMiddleware:
    """响应处理中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 如果响应已经是BaseResponse类型，直接返回
        if isinstance(response, BaseResponse):
            return response
            
        # 包装响应数据
        if response.status_code == 200:
            return {
                "code": "0",
                "message": "success",
                "data": response.body,
                "request_id": request.state.request_id
            }
        
        return response

def create_middleware_stack(app: ASGIApp) -> list:
    """创建中间件栈"""
    return [
        ErrorHandlerMiddleware(app),
        AuthMiddleware(app),
        LoggingMiddleware(app),
        MetricsMiddleware(app)
    ] 
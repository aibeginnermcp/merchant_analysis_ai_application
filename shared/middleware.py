#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
共享中间件模块，提供各种通用中间件组件
包括认证、日志记录、性能监控、请求跟踪和异常处理等

Example:
    from shared.middleware import AuthMiddleware, LoggingMiddleware
    
    app = FastAPI()
    app.add_middleware(AuthMiddleware)
    app.add_middleware(LoggingMiddleware)
"""

import time
import json
import uuid
import logging
from typing import Dict, List, Callable, Optional, Union, Any

import jwt
from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram

from shared.exceptions import AuthError, PermissionDeniedError

# 日志配置
logger = logging.getLogger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志记录中间件，记录所有API请求的详细信息
    
    记录内容包括：请求方法、URL、状态码、请求耗时、客户端IP等
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 请求方法和路径
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # 记录请求日志
        logger.info(f"Request started: {method} {path} - ID: {request_id} - IP: {client_ip}")
        
        try:
            # 继续处理请求
            response = await call_next(request)
            
            # 计算请求处理时间
            process_time = (time.time() - start_time) * 1000
            
            # 记录响应日志
            logger.info(
                f"Request completed: {method} {path} - ID: {request_id} - "
                f"Status: {response.status_code} - Duration: {process_time:.2f}ms"
            )
            
            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            # 记录异常日志
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {method} {path} - ID: {request_id} - "
                f"Error: {str(e)} - Duration: {process_time:.2f}ms"
            )
            
            # 重新抛出异常由异常处理中间件处理
            raise


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT认证中间件，验证所有需要认证的请求
    
    验证请求头中的Authorization字段，确保JWT令牌有效
    将解析后的用户信息添加到request.state.user中
    """
    
    def __init__(
        self, 
        app: FastAPI, 
        secret_key: str = None,
        algorithm: str = "HS256",
        exclude_paths: List[str] = None
    ):
        super().__init__(app)
        # 从环境变量或配置中获取密钥
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否是需要排除的路径
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # 获取授权头
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "未提供有效的认证令牌"}
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # 验证JWT令牌
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 将用户信息添加到请求状态
            request.state.user = payload
            
            # 继续处理请求
            return await call_next(request)
            
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "认证令牌已过期"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "无效的认证令牌"}
            )


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    性能监控中间件，收集API请求的性能指标
    
    使用Prometheus收集请求计数、请求延迟等指标
    """
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        
        # 请求计数器
        self.requests_counter = Counter(
            'http_requests_total', 
            'Total HTTP Requests Count',
            ['method', 'endpoint', 'status']
        )
        
        # 请求持续时间直方图
        self.requests_latency = Histogram(
            'http_request_duration_seconds',
            'HTTP Request Duration in Seconds',
            ['method', 'endpoint']
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 请求开始时间
        start_time = time.time()
        
        method = request.method
        endpoint = request.url.path
        
        try:
            # 继续处理请求
            response = await call_next(request)
            
            # 计算请求处理时间
            duration = time.time() - start_time
            
            # 记录请求指标
            self.requests_counter.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
            self.requests_latency.labels(method=method, endpoint=endpoint).observe(duration)
            
            return response
        
        except Exception as e:
            # 记录异常请求指标
            duration = time.time() - start_time
            self.requests_counter.labels(method=method, endpoint=endpoint, status=500).inc()
            self.requests_latency.labels(method=method, endpoint=endpoint).observe(duration)
            
            # 重新抛出异常
            raise


class CORSMiddlewareConfig:
    """CORS中间件配置"""
    
    @staticmethod
    def setup(app: FastAPI, origins: List[str] = None):
        """设置CORS中间件"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins or ["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    统一异常处理中间件
    
    捕获并处理应用中的异常，返回标准格式的错误响应
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except AuthError as e:
            return JSONResponse(
                status_code=401,
                content={"detail": str(e), "code": e.code, "source": e.source}
            )
        except PermissionDeniedError as e:
            return JSONResponse(
                status_code=403,
                content={"detail": str(e), "code": e.code, "source": e.source}
            )
        except Exception as e:
            # 记录未处理的异常
            logger.exception(f"Unhandled exception: {str(e)}")
            
            # 返回500错误
            return JSONResponse(
                status_code=500,
                content={"detail": "服务器内部错误", "code": "INTERNAL_SERVER_ERROR"}
            ) 
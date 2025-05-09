"""
基础服务类定义
为所有微服务提供基础功能
"""
from typing import Optional, Dict, Any
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from .config import settings
from .middleware import auth_middleware, logging_middleware, error_handler_middleware, RateLimitMiddleware

class BaseService:
    """基础服务类"""
    
    def __init__(
        self,
        app_name: str,
        description: str,
        version: str = "1.0.0",
        enable_auth: bool = True,
        enable_rate_limit: bool = True
    ):
        """
        初始化服务
        
        Args:
            app_name: 服务名称
            description: 服务描述
            version: 服务版本
            enable_auth: 是否启用认证
            enable_rate_limit: 是否启用限流
        """
        self.app_name = app_name
        self.app = FastAPI(
            title=app_name,
            description=description,
            version=version
        )
        
        # 数据库连接
        self.mongodb: Optional[AsyncIOMotorClient] = None
        self.redis: Optional[aioredis.Redis] = None
        
        # 配置中间件
        if enable_auth:
            self.app.middleware("http")(auth_middleware)
        self.app.middleware("http")(logging_middleware)
        self.app.middleware("http")(error_handler_middleware)
        
        # 注册事件处理器
        self.app.on_event("startup")(self.startup_event)
        self.app.on_event("shutdown")(self.shutdown_event)
        
        # 注册基础路由
        self.register_base_routes()
        
    async def startup_event(self):
        """服务启动事件处理"""
        # 初始化MongoDB连接
        self.mongodb = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # 初始化Redis连接
        self.redis = await aioredis.create_redis_pool(settings.REDIS_URL)
        
        # 注册服务到服务发现
        await self.register_service()
        
    async def shutdown_event(self):
        """服务关闭事件处理"""
        # 关闭数据库连接
        if self.mongodb:
            self.mongodb.close()
            
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            
        # 从服务发现注销
        await self.deregister_service()
        
    def register_base_routes(self):
        """注册基础路由"""
        @self.app.get("/health")
        async def health_check():
            """健康检查接口"""
            return {
                "status": "healthy",
                "service": self.app_name,
                "version": self.app.version
            }
            
        @self.app.get("/metrics")
        async def metrics():
            """监控指标接口"""
            return {
                "service": self.app_name,
                "uptime": "TODO",
                "requests": "TODO",
                "errors": "TODO"
            }
            
    async def register_service(self):
        """注册服务到服务发现"""
        # TODO: 实现服务注册逻辑
        pass
        
    async def deregister_service(self):
        """从服务发现注销服务"""
        # TODO: 实现服务注销逻辑
        pass
        
    def get_db(self) -> AsyncIOMotorClient:
        """获取数据库连接"""
        if not self.mongodb:
            raise RuntimeError("数据库连接未初始化")
        return self.mongodb
        
    def get_redis(self) -> aioredis.Redis:
        """获取Redis连接"""
        if not self.redis:
            raise RuntimeError("Redis连接未初始化")
        return self.redis
        
    def get_service_url(self, service_name: str) -> str:
        """获取服务URL"""
        port = settings.SERVICE_PORTS.get(service_name)
        if not port:
            raise ValueError(f"未知的服务名称: {service_name}")
        return f"http://localhost:{port}" 
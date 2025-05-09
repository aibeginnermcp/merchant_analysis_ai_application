"""
服务管理器模块
"""
import socket
from typing import Optional
from fastapi import FastAPI
from src.shared.database import db_manager
from src.shared.cache import cache_manager
from src.shared.queue import queue_manager
from src.shared.discovery import discovery
from src.shared.config import settings

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        """初始化服务管理器"""
        self._app: Optional[FastAPI] = None
        self._host = socket.gethostname()
        self._port = settings.API_PORT
        
    async def init_app(self, app: FastAPI):
        """初始化应用
        
        Args:
            app: FastAPI应用实例
        """
        self._app = app
        
        # 注册启动事件
        app.add_event_handler("startup", self.startup)
        # 注册关闭事件
        app.add_event_handler("shutdown", self.shutdown)
        
    async def startup(self):
        """启动服务"""
        # 连接数据库
        await db_manager.connect()
        
        # 连接缓存
        await cache_manager.connect()
        
        # 连接消息队列
        await queue_manager.connect()
        
        # 连接服务发现
        discovery.connect()
        
        # 注册服务
        discovery.register_service(
            service_name="merchant-gateway",
            service_id=f"gateway-{self._host}-{self._port}",
            address=self._host,
            port=self._port,
            tags=["api", "gateway"],
            check={
                "http": f"http://{self._host}:{self._port}/health",
                "interval": "10s",
                "timeout": "5s"
            }
        )
        
        print("所有服务已启动")
        
    async def shutdown(self):
        """关闭服务"""
        # 注销服务
        discovery.deregister_service(
            f"gateway-{self._host}-{self._port}"
        )
        
        # 断开数据库连接
        await db_manager.disconnect()
        
        # 断开缓存连接
        await cache_manager.disconnect()
        
        # 断开消息队列连接
        await queue_manager.disconnect()
        
        print("所有服务已关闭")
        
    async def get_service_status(self):
        """获取服务状态
        
        Returns:
            dict: 服务状态信息
        """
        return {
            "database": bool(db_manager._client),
            "cache": bool(cache_manager._redis),
            "queue": bool(queue_manager._connection),
            "discovery": bool(discovery._consul)
        }

# 创建全局服务管理器实例
service_manager = ServiceManager() 
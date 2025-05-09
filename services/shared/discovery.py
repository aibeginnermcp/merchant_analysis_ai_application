"""
服务注册发现模块
"""
import consul
import socket
from typing import Optional, Dict, Any
from contextlib import contextmanager
from .exceptions import SystemError

class ServiceDiscovery:
    """服务发现类"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8500,
        service_name: Optional[str] = None,
        service_id: Optional[str] = None,
        service_port: Optional[int] = None,
        tags: Optional[list] = None
    ):
        """初始化服务发现
        
        Args:
            host: Consul主机
            port: Consul端口
            service_name: 服务名称
            service_id: 服务ID
            service_port: 服务端口
            tags: 服务标签
        """
        self.consul = consul.Consul(host=host, port=port)
        self.service_name = service_name
        self.service_id = service_id or f"{service_name}-{socket.gethostname()}"
        self.service_port = service_port
        self.tags = tags or []
        
    def register(self, health_check_url: str = "/health") -> None:
        """注册服务
        
        Args:
            health_check_url: 健康检查URL
        """
        try:
            self.consul.agent.service.register(
                name=self.service_name,
                service_id=self.service_id,
                port=self.service_port,
                tags=self.tags,
                check={
                    "http": f"http://localhost:{self.service_port}{health_check_url}",
                    "interval": "10s",
                    "timeout": "5s"
                }
            )
        except Exception as e:
            raise SystemError(
                code="1-0001",
                message=f"服务注册失败: {str(e)}"
            )
    
    def deregister(self) -> None:
        """注销服务"""
        try:
            self.consul.agent.service.deregister(self.service_id)
        except Exception as e:
            raise SystemError(
                code="1-0001",
                message=f"服务注销失败: {str(e)}"
            )
    
    def get_service(self, service_name: str) -> Dict[str, Any]:
        """获取服务信息
        
        Args:
            service_name: 服务名称
            
        Returns:
            服务信息字典
        """
        try:
            _, services = self.consul.health.service(service_name, passing=True)
            if not services:
                raise SystemError(
                    code="1-0002",
                    message=f"服务 {service_name} 不可用"
                )
            
            service = services[0]["Service"]
            return {
                "id": service["ID"],
                "name": service["Service"],
                "address": service["Address"] or "localhost",
                "port": service["Port"],
                "tags": service["Tags"]
            }
        except Exception as e:
            if isinstance(e, SystemError):
                raise e
            raise SystemError(
                code="1-0001",
                message=f"获取服务信息失败: {str(e)}"
            )
    
    @contextmanager
    def service_context(self):
        """服务上下文管理器"""
        try:
            self.register()
            yield
        finally:
            self.deregister()

# 服务发现单例
discovery = ServiceDiscovery() 
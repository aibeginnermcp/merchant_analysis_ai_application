"""服务发现模块"""
import consul
import random
from typing import Optional, List, Dict
from .config import settings

class ServiceDiscovery:
    """服务发现类"""
    
    def __init__(self):
        """初始化服务发现"""
        self.consul = consul.Consul(
            host=settings.CONSUL_HOST,
            port=settings.CONSUL_PORT
        )
        
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """获取服务地址
        
        Args:
            service_name: 服务名称
            
        Returns:
            Optional[str]: 服务地址，如果服务不可用则返回None
        """
        # 从Consul获取服务实例
        _, nodes = self.consul.catalog.service(service_name)
        
        if not nodes:
            return None
            
        # 随机选择一个健康的实例
        healthy_nodes = [
            node for node in nodes
            if self._check_health(node["ServiceID"])
        ]
        
        if not healthy_nodes:
            return None
            
        node = random.choice(healthy_nodes)
        return f"http://{node['ServiceAddress']}:{node['ServicePort']}"
        
    def _check_health(self, service_id: str) -> bool:
        """检查服务健康状态
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 服务是否健康
        """
        checks = self.consul.health.checks(service_id)
        return all(check["Status"] == "passing" for check in checks)
        
    async def register_service(
        self,
        service_name: str,
        service_id: str,
        address: str,
        port: int,
        tags: List[str] = None
    ) -> bool:
        """注册服务
        
        Args:
            service_name: 服务名称
            service_id: 服务ID
            address: 服务地址
            port: 服务端口
            tags: 服务标签
            
        Returns:
            bool: 注册是否成功
        """
        try:
            self.consul.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=address,
                port=port,
                tags=tags or [],
                check={
                    "http": f"http://{address}:{port}/health",
                    "interval": "10s",
                    "timeout": "5s"
                }
            )
            return True
        except Exception:
            return False
            
    async def deregister_service(self, service_id: str) -> bool:
        """注销服务
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 注销是否成功
        """
        try:
            self.consul.agent.service.deregister(service_id)
            return True
        except Exception:
            return False 
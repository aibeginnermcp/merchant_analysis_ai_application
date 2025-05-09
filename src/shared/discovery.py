"""
服务发现模块
"""
from typing import Optional, Dict, List
import consul
from src.shared.config import settings

class ServiceDiscovery:
    """服务发现管理器"""
    
    def __init__(self):
        """初始化服务发现管理器"""
        self._consul: Optional[consul.Consul] = None
        
    def connect(self):
        """连接Consul"""
        try:
            self._consul = consul.Consul(
                host=settings.CONSUL_HOST,
                port=settings.CONSUL_PORT
            )
            print("Consul连接成功")
        except Exception as e:
            print(f"Consul连接失败: {e}")
            raise
            
    def register_service(
        self,
        service_name: str,
        service_id: str,
        address: str,
        port: int,
        tags: List[str] = None,
        check: Dict = None
    ):
        """注册服务
        
        Args:
            service_name: 服务名称
            service_id: 服务ID
            address: 服务地址
            port: 服务端口
            tags: 服务标签
            check: 健康检查配置
        """
        if not self._consul:
            raise ConnectionError("Consul未连接")
            
        # 默认健康检查配置
        if check is None:
            check = {
                "http": f"http://{address}:{port}/health",
                "interval": "10s",
                "timeout": "5s"
            }
            
        self._consul.agent.service.register(
            name=service_name,
            service_id=service_id,
            address=address,
            port=port,
            tags=tags or [],
            check=check
        )
        
    def deregister_service(self, service_id: str):
        """注销服务
        
        Args:
            service_id: 服务ID
        """
        if not self._consul:
            raise ConnectionError("Consul未连接")
            
        self._consul.agent.service.deregister(service_id)
        
    def get_service(self, service_name: str) -> List[Dict]:
        """获取服务实例列表
        
        Args:
            service_name: 服务名称
            
        Returns:
            List[Dict]: 服务实例列表
        """
        if not self._consul:
            raise ConnectionError("Consul未连接")
            
        _, services = self._consul.health.service(
            service_name,
            passing=True
        )
        
        return [
            {
                "id": service["Service"]["ID"],
                "name": service["Service"]["Service"],
                "address": service["Service"]["Address"],
                "port": service["Service"]["Port"],
                "tags": service["Service"]["Tags"]
            }
            for service in services
        ]
        
    def get_service_address(self, service_name: str) -> str:
        """获取服务地址
        
        Args:
            service_name: 服务名称
            
        Returns:
            str: 服务地址
            
        Raises:
            LookupError: 服务不可用
        """
        services = self.get_service(service_name)
        if not services:
            raise LookupError(f"服务{service_name}不可用")
            
        # 这里可以实现负载均衡策略
        service = services[0]
        return f"http://{service['address']}:{service['port']}"

# 创建全局服务发现管理器实例
discovery = ServiceDiscovery() 
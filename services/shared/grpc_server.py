"""
gRPC服务器基类
"""
import grpc
from concurrent import futures
import logging
from typing import Optional

class GrpcServer:
    """gRPC服务器基类"""
    
    def __init__(
        self,
        service_name: str,
        host: str = "0.0.0.0",
        port: int = 50051,
        max_workers: int = 10
    ):
        """
        初始化gRPC服务器
        
        Args:
            service_name: 服务名称
            host: 服务器主机地址
            port: 服务器端口
            max_workers: 最大工作线程数
        """
        self.service_name = service_name
        self.host = host
        self.port = port
        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=max_workers)
        )
        self.logger = logging.getLogger(service_name)
    
    def add_service(self, service_class: object) -> None:
        """
        添加服务实现类
        
        Args:
            service_class: 服务实现类实例
        """
        # 在子类中实现具体的服务添加逻辑
        raise NotImplementedError
    
    def start(self) -> None:
        """启动服务器"""
        address = f"{self.host}:{self.port}"
        self.server.add_insecure_port(address)
        self.server.start()
        self.logger.info(f"gRPC服务器启动于 {address}")
    
    def stop(self, grace: Optional[float] = None) -> None:
        """
        停止服务器
        
        Args:
            grace: 优雅停止等待时间(秒)
        """
        self.server.stop(grace)
        self.logger.info("gRPC服务器已停止")
    
    def wait_for_termination(self) -> None:
        """等待服务器终止"""
        self.server.wait_for_termination() 
"""
gRPC客户端基类
"""
import grpc
from typing import Optional, Any
import logging
from contextlib import contextmanager

from .discovery import discovery
from .exceptions import SystemError

class GrpcClient:
    """gRPC客户端基类"""
    
    def __init__(
        self,
        service_name: str,
        stub_class: Any,
        host: Optional[str] = None,
        port: Optional[int] = None
    ):
        """
        初始化gRPC客户端
        
        Args:
            service_name: 服务名称
            stub_class: Stub类
            host: 服务器主机地址(可选)
            port: 服务器端口(可选)
        """
        self.service_name = service_name
        self.stub_class = stub_class
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.logger = logging.getLogger(service_name)
    
    def connect(self) -> None:
        """建立连接"""
        try:
            if not self.host or not self.port:
                # 从服务发现获取地址
                service_info = discovery.get_service(self.service_name)
                self.host = service_info["address"]
                self.port = service_info["port"]
            
            address = f"{self.host}:{self.port}"
            self.channel = grpc.insecure_channel(address)
            self.stub = self.stub_class(self.channel)
            self.logger.info(f"已连接到gRPC服务器: {address}")
            
        except Exception as e:
            raise SystemError(
                code="4-0001",
                message=f"gRPC连接失败: {str(e)}"
            )
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.channel:
            self.channel.close()
            self.logger.info("已断开gRPC连接")
    
    @contextmanager
    def get_stub(self):
        """获取Stub的上下文管理器"""
        try:
            if not self.stub:
                self.connect()
            yield self.stub
        finally:
            self.disconnect()
    
    def call_method(self, method_name: str, request: Any) -> Any:
        """
        调用gRPC方法
        
        Args:
            method_name: 方法名称
            request: 请求参数
            
        Returns:
            响应结果
        """
        try:
            with self.get_stub() as stub:
                method = getattr(stub, method_name)
                return method(request)
        except Exception as e:
            raise SystemError(
                code="4-0002",
                message=f"gRPC调用失败: {str(e)}"
            ) 
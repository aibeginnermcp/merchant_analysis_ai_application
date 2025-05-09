"""
基础gRPC服务类，提供通用的服务功能
"""
import grpc
from concurrent import futures
from typing import Optional
import logging
import prometheus_client as prom
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer

from shared.utils.exceptions import ServiceType, AnalysisException

class BaseGrpcService:
    """基础gRPC服务类"""
    
    def __init__(
        self,
        service_type: ServiceType,
        host: str = "0.0.0.0",
        port: int = 50051,
        max_workers: int = 10,
        enable_metrics: bool = True,
        enable_tracing: bool = True
    ):
        """
        初始化基础gRPC服务
        
        Args:
            service_type: 服务类型
            host: 服务主机地址
            port: 服务端口
            max_workers: 最大工作线程数
            enable_metrics: 是否启用指标收集
            enable_tracing: 是否启用链路追踪
        """
        self.service_type = service_type
        self.host = host
        self.port = port
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        
        # 设置日志
        self.logger = logging.getLogger(service_type.value)
        
        # 设置指标收集
        if enable_metrics:
            self._setup_metrics()
            
        # 设置链路追踪
        if enable_tracing:
            self._setup_tracing()
            
    def _setup_metrics(self):
        """设置Prometheus指标收集"""
        self.request_counter = prom.Counter(
            f"{self.service_type.value}_requests_total",
            "Total number of gRPC requests received",
            ["method", "status"]
        )
        
        self.request_latency = prom.Histogram(
            f"{self.service_type.value}_request_latency_seconds",
            "Request latency in seconds",
            ["method"]
        )
        
    def _setup_tracing(self):
        """设置OpenTelemetry链路追踪"""
        tracer = GrpcInstrumentorServer().instrument()
        
    def add_service(self, servicer_class, service_class):
        """添加gRPC服务"""
        service_class.add_to_server(servicer_class(), self.server)
        
    def start(self):
        """启动服务"""
        address = f"{self.host}:{self.port}"
        self.server.add_insecure_port(address)
        self.server.start()
        self.logger.info(f"Service {self.service_type.value} started on {address}")
        
    def stop(self, grace: Optional[float] = None):
        """停止服务"""
        self.server.stop(grace)
        self.logger.info(f"Service {self.service_type.value} stopped")
        
    def wait_for_termination(self):
        """等待服务终止"""
        self.server.wait_for_termination()
        
    def handle_exception(self, context: grpc.ServicerContext, exc: Exception):
        """处理服务异常"""
        if isinstance(exc, AnalysisException):
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(exc.message)
            self.logger.error(f"Analysis exception: {exc.to_dict()}")
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details(str(exc))
            self.logger.exception("Unexpected error occurred") 
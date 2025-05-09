"""
数据模拟服务gRPC实现
"""
import grpc
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp

from shared.grpc_server import GrpcServer
from merchant_analysis_pb2 import (
    SimulateTransactionsResponse,
    SimulateCostsResponse
)
from merchant_analysis_pb2_grpc import (
    DataSimulatorServicer,
    add_DataSimulatorServicer_to_server
)

class DataSimulatorService(DataSimulatorServicer):
    """数据模拟服务实现"""
    
    async def SimulateTransactions(
        self,
        request,
        context: grpc.aio.ServicerContext
    ) -> SimulateTransactionsResponse:
        """
        模拟交易数据
        
        Args:
            request: 请求参数
            context: gRPC上下文
            
        Returns:
            模拟的交易数据
        """
        # TODO: 实现交易数据模拟逻辑
        transaction_data = {
            "daily_transactions": "模拟的每日交易数据",
            "transaction_amount": "模拟的交易金额"
        }
        
        return SimulateTransactionsResponse(
            transaction_data=transaction_data
        )
    
    async def SimulateCosts(
        self,
        request,
        context: grpc.aio.ServicerContext
    ) -> SimulateCostsResponse:
        """
        模拟成本数据
        
        Args:
            request: 请求参数
            context: gRPC上下文
            
        Returns:
            模拟的成本数据
        """
        # TODO: 实现成本数据模拟逻辑
        cost_data = {
            "fixed_costs": "模拟的固定成本数据",
            "variable_costs": "模拟的变动成本数据"
        }
        
        return SimulateCostsResponse(
            cost_data=cost_data
        )

class DataSimulatorGrpcServer(GrpcServer):
    """数据模拟gRPC服务器"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 50051):
        super().__init__("data_simulator", host, port)
        self.add_service(DataSimulatorService())
    
    def add_service(self, service: DataSimulatorService) -> None:
        """添加服务实现"""
        add_DataSimulatorServicer_to_server(service, self.server) 
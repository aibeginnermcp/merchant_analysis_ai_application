"""
数据模拟服务gRPC客户端
"""
from typing import Dict, Any
from google.protobuf.timestamp_pb2 import Timestamp

from shared.grpc_client import GrpcClient
from merchant_analysis_pb2 import (
    Merchant,
    TimeRange,
    SimulateTransactionsRequest,
    SimulateCostsRequest
)
from merchant_analysis_pb2_grpc import DataSimulatorStub

class DataSimulatorClient(GrpcClient):
    """数据模拟服务客户端"""
    
    def __init__(self, host: str = None, port: int = None):
        super().__init__(
            service_name="data_simulator",
            stub_class=DataSimulatorStub,
            host=host,
            port=port
        )
    
    def simulate_transactions(
        self,
        merchant: Dict[str, Any],
        time_range: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        模拟交易数据
        
        Args:
            merchant: 商户信息
            time_range: 时间范围
            
        Returns:
            模拟的交易数据
        """
        # 构建请求
        merchant_proto = Merchant(
            merchant_id=merchant["merchant_id"],
            merchant_name=merchant["merchant_name"],
            business_type=merchant["business_type"]
        )
        
        time_range_proto = TimeRange(
            start_time=Timestamp().FromDatetime(time_range["start"]),
            end_time=Timestamp().FromDatetime(time_range["end"])
        )
        
        request = SimulateTransactionsRequest(
            merchant=merchant_proto,
            time_range=time_range_proto
        )
        
        # 调用gRPC方法
        response = self.call_method("SimulateTransactions", request)
        return dict(response.transaction_data)
    
    def simulate_costs(
        self,
        merchant: Dict[str, Any],
        time_range: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        模拟成本数据
        
        Args:
            merchant: 商户信息
            time_range: 时间范围
            
        Returns:
            模拟的成本数据
        """
        # 构建请求
        merchant_proto = Merchant(
            merchant_id=merchant["merchant_id"],
            merchant_name=merchant["merchant_name"],
            business_type=merchant["business_type"]
        )
        
        time_range_proto = TimeRange(
            start_time=Timestamp().FromDatetime(time_range["start"]),
            end_time=Timestamp().FromDatetime(time_range["end"])
        )
        
        request = SimulateCostsRequest(
            merchant=merchant_proto,
            time_range=time_range_proto
        )
        
        # 调用gRPC方法
        response = self.call_method("SimulateCosts", request)
        return dict(response.cost_data) 
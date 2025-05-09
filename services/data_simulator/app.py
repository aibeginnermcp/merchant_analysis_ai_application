"""
数据模拟服务主应用程序
"""
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from typing import Optional

from shared.discovery import discovery
from shared.middleware import (
    create_middleware_stack,
    TracingMiddleware,
    ResponseMiddleware
)
from shared.models import (
    BaseResponse,
    MerchantBase,
    TimeRange,
    DataResponse
)
from shared.exceptions import (
    ValidationError,
    BusinessError,
    ServiceType
)

from .grpc_server import DataSimulatorGrpcServer

# 服务配置
SERVICE_NAME = "data_simulator"
SERVICE_PORT = 8001
GRPC_PORT = 50051

# gRPC服务器实例
grpc_server: Optional[DataSimulatorGrpcServer] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    global grpc_server
    
    # 启动gRPC服务器
    grpc_server = DataSimulatorGrpcServer(port=GRPC_PORT)
    grpc_server.start()
    
    # 注册HTTP服务
    discovery.service_name = SERVICE_NAME
    discovery.service_port = SERVICE_PORT
    discovery.register()
    
    yield
    
    # 停止服务
    if grpc_server:
        grpc_server.stop()
    discovery.deregister()

app = FastAPI(
    title="商户数据模拟服务",
    description="提供商户经营数据模拟生成",
    version="1.0.0",
    lifespan=lifespan
)

# 添加中间件
for middleware in create_middleware_stack(app):
    app.add_middleware(middleware.__class__)
app.add_middleware(TracingMiddleware)
app.add_middleware(ResponseMiddleware)

@app.get("/health")
async def health_check() -> BaseResponse:
    """健康检查接口"""
    return BaseResponse(
        message="Service is healthy"
    )

@app.post("/api/v1/simulate/transaction")
async def simulate_transactions(
    merchant: MerchantBase,
    time_range: TimeRange
) -> DataResponse:
    """
    模拟生成商户交易数据
    
    Args:
        merchant: 商户基础信息
        time_range: 时间范围
        
    Returns:
        模拟的交易数据
    """
    try:
        # 调用gRPC服务
        if grpc_server:
            response = await grpc_server.service.SimulateTransactions(
                merchant=merchant.dict(),
                time_range=time_range.dict()
            )
            return DataResponse(
                data=response.transaction_data,
                message="数据模拟成功"
            )
        
        raise BusinessError(
            message="gRPC服务未启动",
            service=ServiceType.DATA_SIMULATOR
        )
    except Exception as e:
        raise BusinessError(
            message=str(e),
            service=ServiceType.DATA_SIMULATOR
        )

@app.post("/api/v1/simulate/cost")
async def simulate_costs(
    merchant: MerchantBase,
    time_range: TimeRange
) -> DataResponse:
    """
    模拟生成商户成本数据
    
    Args:
        merchant: 商户基础信息
        time_range: 时间范围
        
    Returns:
        模拟的成本数据
    """
    try:
        # 调用gRPC服务
        if grpc_server:
            response = await grpc_server.service.SimulateCosts(
                merchant=merchant.dict(),
                time_range=time_range.dict()
            )
            return DataResponse(
                data=response.cost_data,
                message="数据模拟成功"
            )
        
        raise BusinessError(
            message="gRPC服务未启动",
            service=ServiceType.DATA_SIMULATOR
        )
    except Exception as e:
        raise BusinessError(
            message=str(e),
            service=ServiceType.DATA_SIMULATOR
        )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True
    ) 
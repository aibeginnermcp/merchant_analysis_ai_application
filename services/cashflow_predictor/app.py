"""
现金流预测服务主应用程序
"""
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn

from shared.discovery import discovery
from shared.middleware import (
    create_middleware_stack,
    TracingMiddleware,
    ResponseMiddleware
)
from shared.models import (
    BaseResponse,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisType,
    AnalysisStatus
)
from shared.exceptions import (
    ValidationError,
    BusinessError,
    ServiceType
)

# 服务配置
SERVICE_NAME = "cashflow_predictor"
SERVICE_PORT = 8002

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    discovery.service_name = SERVICE_NAME
    discovery.service_port = SERVICE_PORT
    discovery.register()
    yield
    discovery.deregister()

app = FastAPI(
    title="现金流预测服务",
    description="提供商户现金流预测分析",
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

@app.post("/api/v1/predict")
async def predict_cashflow(request: AnalysisRequest) -> AnalysisResponse:
    """
    预测商户现金流
    
    Args:
        request: 分析请求参数
        
    Returns:
        现金流预测结果
    """
    try:
        if AnalysisType.CASHFLOW not in request.analysis_type:
            raise ValidationError(
                message="不支持的分析类型",
                service=ServiceType.CASH_FLOW
            )
        
        # TODO: 实现现金流预测逻辑
        prediction_results = {}
        
        return AnalysisResponse(
            request_id=request.merchant_id,
            merchant_id=request.merchant_id,
            analysis_type=AnalysisType.CASHFLOW.value,
            status=AnalysisStatus.COMPLETED.value,
            results=prediction_results,
            summary="现金流预测完成",
            recommendations=[]
        )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise BusinessError(
            message=str(e),
            service=ServiceType.CASH_FLOW
        )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True
    ) 
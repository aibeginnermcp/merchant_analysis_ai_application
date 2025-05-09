"""
成本分析服务主应用程序
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
SERVICE_NAME = "cost_analysis"
SERVICE_PORT = 8003

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    discovery.service_name = SERVICE_NAME
    discovery.service_port = SERVICE_PORT
    discovery.register()
    yield
    discovery.deregister()

app = FastAPI(
    title="成本分析服务",
    description="提供商户成本穿透分析",
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

@app.post("/api/v1/analyze")
async def analyze_cost(request: AnalysisRequest) -> AnalysisResponse:
    """
    分析商户成本结构
    
    Args:
        request: 分析请求参数
        
    Returns:
        成本分析结果
    """
    try:
        if AnalysisType.COST not in request.analysis_type:
            raise ValidationError(
                message="不支持的分析类型",
                service=ServiceType.COST_ANALYSIS
            )
        
        # TODO: 实现成本分析逻辑
        analysis_results = {}
        
        return AnalysisResponse(
            request_id=request.merchant_id,
            merchant_id=request.merchant_id,
            analysis_type=AnalysisType.COST.value,
            status=AnalysisStatus.COMPLETED.value,
            results=analysis_results,
            summary="成本分析完成",
            recommendations=[]
        )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise BusinessError(
            message=str(e),
            service=ServiceType.COST_ANALYSIS
        )

@app.post("/api/v1/optimize")
async def optimize_cost(request: AnalysisRequest) -> AnalysisResponse:
    """
    优化商户成本结构
    
    Args:
        request: 分析请求参数
        
    Returns:
        成本优化建议
    """
    try:
        if AnalysisType.COST not in request.analysis_type:
            raise ValidationError(
                message="不支持的分析类型",
                service=ServiceType.COST_ANALYSIS
            )
        
        # TODO: 实现成本优化逻辑
        optimization_results = {}
        recommendations = [
            "建议优化供应商结构",
            "建议调整库存管理策略",
            "建议优化人力资源配置"
        ]
        
        return AnalysisResponse(
            request_id=request.merchant_id,
            merchant_id=request.merchant_id,
            analysis_type=AnalysisType.COST.value,
            status=AnalysisStatus.COMPLETED.value,
            results=optimization_results,
            summary="成本优化分析完成",
            recommendations=recommendations
        )
    except Exception as e:
        if isinstance(e, ValidationError):
            raise e
        raise BusinessError(
            message=str(e),
            service=ServiceType.COST_ANALYSIS
        )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True
    ) 
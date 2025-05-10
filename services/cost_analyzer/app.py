"""
成本分析服务主应用程序
"""
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
import uvicorn
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 尝试导入shared模块，如果不存在则使用备用实现
try:
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
    SHARED_AVAILABLE = True
except ImportError:
    logger.warning("共享模块不可用，使用本地实现")
    SHARED_AVAILABLE = False
    
    # 本地实现的备用类
    class BaseResponse(BaseModel):
        message: str = ""
        status: str = "success"
    
    class AnalysisRequest(BaseModel):
        merchant_id: str
        analysis_type: List[str] = ["cost"]
        start_date: str
        end_date: str
        
    class AnalysisResponse(BaseModel):
        request_id: str
        merchant_id: str
        analysis_type: str
        status: str
        results: Dict[str, Any] = {}
        summary: str = ""
        recommendations: List[str] = []
    
    class AnalysisType:
        COST = "cost"
    
    class AnalysisStatus:
        COMPLETED = "completed"
        FAILED = "failed"
    
    class ServiceType:
        COST_ANALYSIS = "cost_analysis"
    
    class ValidationError(Exception):
        def __init__(self, message: str, service: str = None):
            self.message = message
            self.service = service
            super().__init__(self.message)
    
    class BusinessError(Exception):
        def __init__(self, message: str, service: str = None):
            self.message = message
            self.service = service
            super().__init__(self.message)
    
    # 空的服务发现
    class Discovery:
        def __init__(self):
            self.service_name = ""
            self.service_port = 0
        
        def register(self):
            logger.info(f"模拟注册服务: {self.service_name}:{self.service_port}")
        
        def deregister(self):
            logger.info(f"模拟注销服务: {self.service_name}")
    
    discovery = Discovery()

# 服务配置
SERVICE_NAME = "cost_analysis"
SERVICE_PORT = 8001  # 与主服务端口保持一致

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    logger.info("服务启动中...")
    discovery.service_name = SERVICE_NAME
    discovery.service_port = SERVICE_PORT
    
    try:
    discovery.register()
        logger.info("服务注册成功")
    except Exception as e:
        logger.error(f"服务注册失败: {str(e)}")
    
    yield
    
    try:
    discovery.deregister()
        logger.info("服务注销成功")
    except Exception as e:
        logger.error(f"服务注销失败: {str(e)}")
    
    logger.info("服务已停止")

app = FastAPI(
    title="成本分析服务",
    description="提供商户成本穿透分析",
    version="1.0.0",
    lifespan=lifespan
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"处理请求: {request.method} {request.url.path} - 耗时: {process_time:.4f}秒")
        return response
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"请求处理异常: {request.method} {request.url.path} - 耗时: {process_time:.4f}秒 - 错误: {str(e)}")
        raise

# 添加共享中间件（如果可用）
if SHARED_AVAILABLE:
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
        # 简单的分析类型检查 - 在缺少shared模块的情况下也能工作
        valid_types = ["cost", "cost_analysis"]
        if not any(t.lower() in valid_types for t in request.analysis_type):
            raise ValidationError(
                message="不支持的分析类型",
                service=ServiceType.COST_ANALYSIS
            )
        
        # 简化的成本分析结果
        analysis_results = {
            "total_cost": 12500.50,
            "cost_breakdown": {
                "fixed": 7500.25,
                "variable": 5000.25
            },
            "major_factors": [
                {"name": "人力成本", "value": 5200.00, "percentage": 41.6},
                {"name": "原材料", "value": 3750.50, "percentage": 30.0},
                {"name": "租金", "value": 2300.00, "percentage": 18.4},
                {"name": "水电", "value": 650.00, "percentage": 5.2},
                {"name": "其他", "value": 600.00, "percentage": 4.8}
            ]
        }
        
        # 优化建议
        recommendations = [
            "通过集中采购降低原材料成本",
            "优化人员配置，提高人力资源效率",
            "考虑节能设备投入，降低水电成本"
        ]
        
        return AnalysisResponse(
            request_id=f"ca-{request.merchant_id}-{int(datetime.now().timestamp())}",
            merchant_id=request.merchant_id,
            analysis_type="cost",
            status=AnalysisStatus.COMPLETED,
            results=analysis_results,
            summary="成本分析完成，已识别主要成本因素和优化空间",
            recommendations=recommendations
        )
    except ValidationError as e:
        # 将验证错误转换为HTTP 400错误
        raise HTTPException(
            status_code=400,
            detail=str(e.message)
        )
    except Exception as e:
        # 记录详细错误信息
        logger.error(f"成本分析过程中发生错误: {str(e)}", exc_info=True)
        
        # 将其他错误转换为HTTP 500错误
        if isinstance(e, BusinessError):
            raise HTTPException(
                status_code=500,
                detail=str(e.message)
            )
        raise HTTPException(
            status_code=500,
            detail=f"成本分析服务内部错误: {str(e)}"
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
        # 简单的分析类型检查 - 在缺少shared模块的情况下也能工作
        valid_types = ["cost", "cost_analysis", "optimization"]
        if not any(t.lower() in valid_types for t in request.analysis_type):
            raise ValidationError(
                message="不支持的分析类型",
                service=ServiceType.COST_ANALYSIS
            )
        
        # 简化的成本优化结果
        optimization_results = {
            "potential_savings": 2150.75,
            "optimization_areas": [
                {"area": "人力资源", "savings": 950.25, "difficulty": "中"},
                {"area": "原材料采购", "savings": 750.50, "difficulty": "低"},
                {"area": "能源使用", "savings": 450.00, "difficulty": "高"}
            ],
            "roi": {
                "short_term": "17%",
                "long_term": "32%"
            }
        }
        
        # 优化建议
        recommendations = [
            "建议优化供应商结构，集中采购降低成本",
            "建议调整人员排班，提高人力资源利用率",
            "建议采用节能设备，降低长期能源成本"
        ]
        
        return AnalysisResponse(
            request_id=f"ca-opt-{request.merchant_id}-{int(datetime.now().timestamp())}",
            merchant_id=request.merchant_id,
            analysis_type="cost_optimization",
            status=AnalysisStatus.COMPLETED,
            results=optimization_results,
            summary="成本优化分析完成，已识别潜在优化空间和实施策略",
            recommendations=recommendations
        )
    except ValidationError as e:
        # 将验证错误转换为HTTP 400错误
        raise HTTPException(
            status_code=400,
            detail=str(e.message)
        )
    except Exception as e:
        # 记录详细错误信息
        logger.error(f"成本优化分析过程中发生错误: {str(e)}", exc_info=True)
        
        # 将其他错误转换为HTTP 500错误
        if isinstance(e, BusinessError):
            raise HTTPException(
                status_code=500,
                detail=str(e.message)
            )
        raise HTTPException(
            status_code=500,
            detail=f"成本优化服务内部错误: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True
    ) 
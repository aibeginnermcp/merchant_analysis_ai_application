"""
API网关主应用程序
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from shared.discovery import ServiceDiscovery, discovery
from shared.middleware import (
    create_middleware_stack,
    TracingMiddleware,
    ResponseMiddleware
)
from shared.models import (
    AnalysisRequest,
    AnalysisResponse,
    ErrorResponse,
    BaseResponse
)

# 服务配置
SERVICE_NAME = "api_gateway"
SERVICE_PORT = 8000

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用程序生命周期管理
    """
    # 启动时注册服务
    discovery.service_name = SERVICE_NAME
    discovery.service_port = SERVICE_PORT
    discovery.register()
    
    yield
    
    # 关闭时注销服务
    discovery.deregister()

# 创建FastAPI应用
app = FastAPI(
    title="商户智能经营分析平台",
    description="提供商户经营数据分析服务",
    version="1.0.0",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
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

@app.post("/api/v1/analysis")
async def create_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """
    创建分析任务
    
    处理流程：
    1. 验证请求参数
    2. 调用数据模拟服务获取数据
    3. 根据分析类型调用相应的分析服务
    4. 整合分析结果
    5. 返回响应
    """
    # TODO: 实现分析流程
    pass

@app.get("/api/v1/analysis/{analysis_id}")
async def get_analysis(analysis_id: str) -> AnalysisResponse:
    """获取分析结果"""
    # TODO: 实现获取分析结果
    pass

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True
    ) 
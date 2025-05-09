"""
合规检查服务主入口

提供以下功能：
- 服务配置
- 服务启动
- 健康检查
- 指标暴露
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from services.shared.config import settings
from services.shared.middleware import create_middleware_stack
from .api import router as compliance_router
from .service import ComplianceService

# 创建FastAPI应用
app = FastAPI(
    title="商户合规检查服务",
    description="提供商户合规性检查功能",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 添加自定义中间件
for middleware in create_middleware_stack(app):
    app.add_middleware(middleware.__class__)

# 添加路由
app.include_router(compliance_router)

# 添加Prometheus指标端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# 创建服务实例
service = ComplianceService()

@app.on_event("startup")
async def startup():
    """服务启动时执行"""
    await service.connect()

@app.on_event("shutdown")
async def shutdown():
    """服务关闭时执行"""
    await service.disconnect()
    await service.deregister_service()

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.service.SERVICE_HOST,
        port=settings.service.SERVICE_PORT,
        reload=settings.service.DEBUG
    ) 
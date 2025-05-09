"""
API网关主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from datetime import datetime

from .routes import router
from .middleware import setup_middleware
from .services import service_manager

# 创建FastAPI应用
app = FastAPI(
    title="商户智能经营分析平台",
    description="提供商户经营数据分析、预测和优化建议的API服务",
    version="1.0.0"
)

# 设置中间件
setup_middleware(app)

# 添加路由
app.include_router(router, prefix="/api/v1")

# 添加Prometheus指标接口
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# 初始化服务管理器
@app.on_event("startup")
async def startup():
    """应用启动事件处理器"""
    await service_manager.init_app(app)

@app.get("/")
async def root():
    """根路径处理器
    
    Returns:
        dict: 欢迎信息
    """
    return {
        "message": "欢迎使用商户智能经营分析平台",
        "docs_url": "/docs",
        "metrics_url": "/metrics"
    }

@app.get("/health")
async def health_check():
    """健康检查接口
    
    Returns:
        dict: 健康状态
    """
    service_status = await service_manager.get_service_status()
    is_healthy = all(service_status.values())
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "services": service_status,
        "timestamp": datetime.utcnow().isoformat()
    } 
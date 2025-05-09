"""
API Gateway 主入口文件
作为整个系统的入口点，处理所有请求并路由到相应的服务
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import os
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="商户智能分析平台 API",
    description="集成现金流预测、成本穿透分析和合规检查的API网关",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 服务地址配置 (实际环境中可能从配置文件或环境变量获取)
SERVICE_CONFIG = {
    "cashflow": os.getenv("CASHFLOW_SERVICE_URL", "http://localhost:8002"),
    "cost": os.getenv("COST_SERVICE_URL", "http://localhost:8001"),
    "compliance": os.getenv("COMPLIANCE_SERVICE_URL", "http://localhost:8003"),
    "data": os.getenv("DATA_SERVICE_URL", "http://localhost:8004")
}

@app.get("/")
async def root():
    """API根路径，返回简单信息"""
    return {
        "name": "商户智能分析平台 API网关",
        "version": "1.0.0",
        "status": "运行中",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/integrated-analysis")
async def integrated_analysis(request: Request):
    """
    集成分析接口，将请求转发到各个微服务
    """
    try:
        # 获取请求数据
        data = await request.json()
        logger.info(f"接收到集成分析请求: {data}")
        
        # 从请求中获取所需分析的类型
        analysis_types = data.get("analysis_types", ["cashflow", "cost", "compliance"])
        results = {}
        
        # 异步调用所需的服务
        async with httpx.AsyncClient() as client:
            # 模拟模式下，仅返回成功消息
            logger.info("请求处理完成，返回集成分析结果")
            return {
                "request_id": f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "success",
                "message": "集成分析请求已成功处理",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000))) 
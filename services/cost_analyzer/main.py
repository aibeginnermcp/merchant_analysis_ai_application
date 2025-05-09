"""
成本穿透分析服务主入口文件
提供成本分析相关API
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import logging
import os
import json
import time
import uuid
import socket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="成本穿透分析服务",
    description="细分各类成本占比，发现优化空间",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求计数中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"请求处理时间: {process_time:.4f}秒 - 路径: {request.url.path}")
        return response
    except Exception as e:
        logger.error(f"请求处理异常: {str(e)}")
        process_time = time.time() - start_time
        # 返回一个错误响应
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误，请稍后再试"},
            headers={"X-Process-Time": str(process_time)}
        )

# 初始化MongoDB连接参数
def init_mongodb_connection():
    # 从环境变量获取MongoDB可用性状态
    mongodb_available = os.getenv("MONGODB_AVAILABLE", "true").lower() == "true"
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/merchant_analytics")
    
    # 尝试解析数据库主机
    try:
        if mongodb_uri and "://" in mongodb_uri:
            host = mongodb_uri.split("://")[1].split(":")[0].split("/")[0]
            logger.info(f"MongoDB主机: {host}")
            try:
                host_ip = socket.gethostbyname(host)
                logger.info(f"MongoDB主机IP: {host_ip}")
                
                # 尝试连接测试
                try:
                    import pymongo
                    from pymongo.errors import ConnectionFailure
                    client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
                    client.admin.command('ping')
                    logger.info("✅ MongoDB连接成功")
                    mongodb_available = True
                except (ConnectionFailure, Exception) as e:
                    logger.warning(f"MongoDB连接失败: {str(e)}")
                    mongodb_available = False
            except socket.gaierror:
                logger.warning(f"无法解析MongoDB主机名: {host}")
                mongodb_available = False
    except Exception as e:
        logger.error(f"解析MongoDB URI时出错: {str(e)}")
        mongodb_available = False
    
    return {
        "available": mongodb_available,
        "uri": mongodb_uri
    }

# 初始化MongoDB连接
mongodb_info = init_mongodb_connection()
MONGODB_AVAILABLE = mongodb_info["available"]
MONGODB_URI = mongodb_info["uri"]

# 数据模型
class CostAnalysisRequest(BaseModel):
    merchant_id: str = Field(..., description="商户ID")
    start_date: date = Field(..., description="分析开始日期")
    end_date: date = Field(..., description="分析结束日期")
    analysis_depth: str = Field("detailed", description="分析深度: basic, detailed, comprehensive")

class CostCategory(BaseModel):
    category: str = Field(..., description="成本类别")
    amount: float = Field(..., description="金额")
    percentage: float = Field(..., description="百分比")

class OptimizationSuggestion(BaseModel):
    area: str = Field(..., description="优化领域")
    suggestion: str = Field(..., description="建议内容")
    potential_saving: float = Field(..., description="潜在节省金额")
    difficulty: str = Field(..., description="实施难度")

class CostAnalysisResponse(BaseModel):
    request_id: str = Field(..., description="请求ID")
    merchant_id: str = Field(..., description="商户ID")
    total_cost: float = Field(..., description="总成本")
    cost_breakdown: List[CostCategory] = Field(..., description="成本明细")
    optimization_suggestions: List[Dict[str, Any]] = Field(..., description="优化建议")

@app.get("/")
async def root():
    """服务根路径，返回简单信息"""
    return {
        "name": "成本穿透分析服务",
        "version": "1.0.0",
        "status": "运行中",
        "timestamp": datetime.now().isoformat(),
        "mongodb_available": MONGODB_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    # 即使MongoDB不可用，服务也被视为健康（有降级功能）
    status = "healthy"
    
    # 检查MongoDB连接
    db_status = "connected" if MONGODB_AVAILABLE else "unavailable"
    
    return {
        "status": status, 
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/debug")
async def debug_info():
    """调试信息接口"""
    from platform import python_version
    import sys
    
    try:
        # 尝试获取MongoDB信息
        mongodb_info = {"uri": MONGODB_URI.replace(MONGODB_URI.split("@")[-1], "***") if "@" in MONGODB_URI else MONGODB_URI}
    except Exception as e:
        mongodb_info = {"error": str(e)}
    
    return {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "python_version": python_version(),
        "system": sys.platform,
        "environment_variables": {k: v for k, v in os.environ.items() if k in ["ENVIRONMENT", "PORT", "DEBUG", "MONGODB_AVAILABLE"]},
        "mongodb": {
            **mongodb_info,
            "available": MONGODB_AVAILABLE
        },
        "network": {
            "hostname": socket.gethostname(),
            "fqdn": socket.getfqdn(),
            "ip": socket.gethostbyname(socket.gethostname())
        }
    }

@app.get("/reconnect-mongodb")
async def reconnect_mongodb():
    """尝试重新连接MongoDB"""
    global MONGODB_AVAILABLE, MONGODB_URI
    
    # 重新初始化连接
    mongodb_info = init_mongodb_connection()
    MONGODB_AVAILABLE = mongodb_info["available"]
    MONGODB_URI = mongodb_info["uri"]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "mongodb_available": MONGODB_AVAILABLE,
        "message": "MongoDB重连成功" if MONGODB_AVAILABLE else "MongoDB重连失败"
    }

@app.post("/api/v1/analyze", response_model=CostAnalysisResponse)
async def analyze_cost(request: CostAnalysisRequest):
    """
    分析成本结构
    
    此API分析商户的成本结构，提供详细的成本占比和优化建议
    """
    try:
        logger.info(f"接收到成本分析请求: {request}")
        request_id = f"req_cost_{str(uuid.uuid4())[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 验证日期范围
        if request.end_date < request.start_date:
            raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
        
        # 验证分析深度参数
        valid_depths = ["basic", "detailed", "comprehensive"]
        if request.analysis_depth not in valid_depths:
            raise HTTPException(status_code=400, detail=f"无效的分析深度参数，有效值: {', '.join(valid_depths)}")
        
        # 检查MongoDB可用性
        if not MONGODB_AVAILABLE:
            logger.warning("MongoDB不可用，使用模拟数据")
        
        # 模拟成本分析结果
        total_cost = 152635.80
        
        # 模拟成本细分
        cost_breakdown = [
            CostCategory(category="labor", amount=58623.45, percentage=38.4),
            CostCategory(category="raw_material", amount=42523.75, percentage=27.9),
            CostCategory(category="utilities", amount=12458.90, percentage=8.2),
            CostCategory(category="rent", amount=24000.00, percentage=15.7),
            CostCategory(category="marketing", amount=15029.70, percentage=9.8)
        ]
        
        # 模拟优化建议
        optimization_suggestions = [
            {
                "area": "labor",
                "suggestion": "考虑优化人员排班，减少闲置时间",
                "potential_saving": 4500.00,
                "difficulty": "medium"
            },
            {
                "area": "raw_material",
                "suggestion": "与供应商重新谈判批量折扣",
                "potential_saving": 3200.00,
                "difficulty": "low"
            },
            {
                "area": "utilities",
                "suggestion": "投资节能设备减少能源消耗",
                "potential_saving": 1800.00,
                "difficulty": "high"
            }
        ]
        
        # 记录分析完成
        logger.info(f"成本分析完成，请求ID: {request_id}")
        
        # 返回分析结果
        return CostAnalysisResponse(
            request_id=request_id,
            merchant_id=request.merchant_id,
            total_cost=total_cost,
            cost_breakdown=cost_breakdown,
            optimization_suggestions=optimization_suggestions
        )
    
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"分析成本时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("成本分析服务正在启动...")
    # 记录环境信息
    logger.info(f"环境: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info(f"调试模式: {os.getenv('DEBUG', 'false')}")
    logger.info(f"MongoDB可用: {MONGODB_AVAILABLE}")
    logger.info(f"服务器主机名: {socket.gethostname()}")
    logger.info(f"PYTHONPATH: {os.getenv('PYTHONPATH', '')}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("成本分析服务正在关闭...")

if __name__ == "__main__":
    import uvicorn
    # 从环境变量获取端口，默认为8001
    port = int(os.getenv("PORT", 8001))
    
    # 配置服务器并启动
    logger.info(f"成本分析服务正在启动，端口: {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port) 
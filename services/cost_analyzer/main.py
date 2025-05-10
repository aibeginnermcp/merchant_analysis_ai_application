"""
成本穿透分析服务主入口文件
提供成本分析相关API
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Union
import logging
import os
import json
import time
import uuid
import socket
import random
from pathlib import Path

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

# 检测运行环境
CI_ENVIRONMENT = os.getenv("CI", "false").lower() == "true" or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

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
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误，请稍后再试"},
            headers={"X-Process-Time": str(process_time)}
        )

# 自定义异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常处理: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
        )

# 初始化MongoDB连接参数
def init_mongodb_connection():
    # 从环境变量获取MongoDB可用性状态
    mongodb_available = os.getenv("MONGODB_AVAILABLE", "true").lower() == "true"
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/merchant_analytics")
    
    # 如果显式设置MONGODB_AVAILABLE为false，直接返回
    if os.getenv("MONGODB_AVAILABLE", "").lower() == "false":
        logger.warning("MongoDB明确设置为不可用，跳过连接检查")
        return {
            "available": False,
            "uri": mongodb_uri
        }
    
    # 在CI环境中优先使用模拟数据，跳过连接检查
    if CI_ENVIRONMENT:
        logger.info("检测到CI环境(GitHub Actions)，强制使用模拟数据")
        return {
            "available": False,
            "uri": mongodb_uri,
            "ci_mode": True
        }
    
    # 尝试解析数据库主机并进行连接测试
    try:
        if mongodb_uri and "://" in mongodb_uri:
            host = mongodb_uri.split("://")[1].split(":")[0].split("/")[0]
            logger.info(f"MongoDB主机: {host}")
            
            # 先尝试DNS解析
            try:
                host_ip = socket.gethostbyname(host)
                logger.info(f"MongoDB主机IP: {host_ip}")
                
                # 尝试建立TCP连接
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((host_ip, 27017))
                    s.close()
                    logger.info("MongoDB端口可达")
                    
                    # 尝试MongoDB连接测试
                    try:
                        import pymongo
                        from pymongo.errors import ConnectionFailure
                        client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
                        client.admin.command('ping')
                        logger.info("✅ MongoDB连接成功")
                        mongodb_available = True
                    except (ConnectionFailure, Exception) as e:
                        logger.warning(f"MongoDB连接失败: {str(e)}")
                        mongodb_available = False
                except (socket.timeout, ConnectionRefusedError, Exception) as e:
                    logger.warning(f"无法连接到MongoDB端口: {str(e)}")
                    mongodb_available = False
            except socket.gaierror as e:
                logger.warning(f"无法解析MongoDB主机名: {host}, 错误: {str(e)}")
                mongodb_available = False
    except Exception as e:
        logger.error(f"解析MongoDB URI时出错: {str(e)}")
        mongodb_available = False
    
    return {
        "available": mongodb_available,
        "uri": mongodb_uri,
        "ci_mode": False
    }

# 初始化MongoDB连接
mongodb_info = init_mongodb_connection()
MONGODB_AVAILABLE = mongodb_info["available"]
MONGODB_URI = mongodb_info["uri"]
CI_MODE = mongodb_info.get("ci_mode", False)

# 数据模型
class CostAnalysisRequest(BaseModel):
    merchant_id: str = Field(..., description="商户ID")
    start_date: date = Field(..., description="分析开始日期")
    end_date: date = Field(..., description="分析结束日期")
    analysis_depth: str = Field("detailed", description="分析深度: basic, detailed, comprehensive")
    
    # 添加验证
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期不能早于开始日期')
        return v
    
    @validator('analysis_depth')
    def validate_analysis_depth(cls, v):
        valid_depths = ['basic', 'detailed', 'comprehensive']
        if v.lower() not in valid_depths:
            raise ValueError('无效的分析深度参数')
        return v.lower()

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
        "mongodb_available": MONGODB_AVAILABLE,
        "ci_environment": CI_ENVIRONMENT,
        "ci_mode": CI_MODE,
        "debug_mode": DEBUG_MODE
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    # 服务始终被视为健康（有降级功能）
    status = "healthy"
    
    # 检查MongoDB连接
    db_status = "connected" if MONGODB_AVAILABLE else "unavailable"
    
    # 返回更多调试信息
    return {
        "status": status, 
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "production"),
        "ci_environment": CI_ENVIRONMENT,
        "ci_mode": CI_MODE,
        "mongodb_uri": MONGODB_URI.replace(MONGODB_URI.split("@")[-1], "***") if "@" in MONGODB_URI else MONGODB_URI
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
    
    # 网络信息
    network_info = {
        "hostname": socket.gethostname(),
        "fqdn": socket.getfqdn()
    }
    
    # 尝试获取IP信息
    try:
        network_info["ip"] = socket.gethostbyname(socket.gethostname())
    except Exception as e:
        network_info["ip_error"] = str(e)
    
    # 尝试ping mongodb（非CI环境）
    if not CI_ENVIRONMENT:
        try:
            import subprocess
            ping_result = subprocess.run(["ping", "-c", "1", "mongodb"], capture_output=True, text=True, timeout=2)
            network_info["ping_mongodb"] = ping_result.returncode == 0
        except Exception as e:
            network_info["ping_error"] = str(e)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "python_version": python_version(),
        "system": sys.platform,
        "environment_variables": {k: v for k, v in os.environ.items() if k in ["ENVIRONMENT", "PORT", "DEBUG", "MONGODB_AVAILABLE", "CI", "GITHUB_ACTIONS"]},
        "mongodb": {
            **mongodb_info,
            "available": MONGODB_AVAILABLE,
            "ci_mode": CI_MODE
        },
        "network": network_info,
        "ci_environment": CI_ENVIRONMENT,
        "debug_mode": DEBUG_MODE
    }

@app.get("/reconnect-mongodb")
async def reconnect_mongodb():
    """尝试重新连接MongoDB"""
    global MONGODB_AVAILABLE, MONGODB_URI
    
    # 在CI环境中不允许重连
    if CI_ENVIRONMENT:
        return {
            "success": False,
            "message": "在CI环境中不允许重新连接数据库"
        }
    
    # 重新初始化连接
    new_info = init_mongodb_connection()
    MONGODB_AVAILABLE = new_info["available"]
    MONGODB_URI = new_info["uri"]
    
    return {
        "success": True,
        "mongodb_available": MONGODB_AVAILABLE,
        "message": "MongoDB连接状态已更新"
    }

# 模拟数据生成函数
def generate_mock_cost_data(merchant_id: str, start_date: date, end_date: date, depth: str):
    """生成模拟的成本数据"""
    # 使用商户ID作为随机种子，保证同一商户每次生成相同结果
    random.seed(hash(merchant_id) % 10000)
    
    # 计算总成本 - 根据商户ID稍微变化一下
    merchant_id_num = int(''.join([str(ord(c) % 10) for c in merchant_id[:3]]))
    base_cost = 10000 + (merchant_id_num * 100)
    variation = random.uniform(0.8, 1.2)
    total_cost = base_cost * variation
    
    # 成本分类占比 - 根据不同商户有所变化
    cost_categories = [
        {"category": "人力成本", "percentage": 0.35 + random.uniform(-0.1, 0.1)},
        {"category": "原材料", "percentage": 0.25 + random.uniform(-0.05, 0.05)},
        {"category": "租金", "percentage": 0.15 + random.uniform(-0.05, 0.05)},
        {"category": "水电费", "percentage": 0.08 + random.uniform(-0.02, 0.02)},
        {"category": "营销费用", "percentage": 0.07 + random.uniform(-0.02, 0.02)},
        {"category": "其他", "percentage": 0.10 + random.uniform(-0.03, 0.03)}
    ]
    
    # 重新归一化百分比
    total_percentage = sum(cat["percentage"] for cat in cost_categories)
    for cat in cost_categories:
        cat["percentage"] = cat["percentage"] / total_percentage
        cat["amount"] = round(total_cost * cat["percentage"], 2)
    
    # 根据深度生成不同量级的优化建议
    suggestion_count = {"basic": 2, "detailed": 4, "comprehensive": 6}
    difficulty_levels = ["低", "中", "高"]
    
    suggestions = []
    suggestion_templates = [
        {"area": "人力资源", "base": "优化排班", "saving_factor": 0.08},
        {"area": "供应链", "base": "集中采购原材料", "saving_factor": 0.1},
        {"area": "租赁", "base": "重新协商租约", "saving_factor": 0.05},
        {"area": "能源使用", "base": "采用节能设备", "saving_factor": 0.15},
        {"area": "营销策略", "base": "精准营销投放", "saving_factor": 0.12},
        {"area": "库存管理", "base": "优化库存水平", "saving_factor": 0.07},
        {"area": "定价策略", "base": "动态定价模型", "saving_factor": 0.06},
        {"area": "运营效率", "base": "流程自动化", "saving_factor": 0.09}
    ]
    
    for i in range(min(suggestion_count.get(depth, 3), len(suggestion_templates))):
        template = suggestion_templates[i]
        category = next((c for c in cost_categories if template["area"] in c["category"]), cost_categories[i % len(cost_categories)])
        
        # 计算潜在节省
        saving_factor = template["saving_factor"] * random.uniform(0.7, 1.3)
        potential_saving = round(category["amount"] * saving_factor, 2)
        
        # 确定难度
        difficulty = difficulty_levels[i % len(difficulty_levels)]
        
        suggestions.append({
            "area": template["area"],
            "suggestion": f"{template['base']}，可节省约{int(saving_factor*100)}%的{category['category']}",
            "potential_saving": potential_saving,
            "difficulty": difficulty,
            "roi": f"{int(random.uniform(10, 30))}%",
            "implementation_time": f"{int(random.uniform(1, 6))}个月"
        })
    
    return {
        "request_id": f"req-{merchant_id}-{int(datetime.now().timestamp())}",
        "merchant_id": merchant_id,
        "total_cost": round(total_cost, 2),
        "cost_breakdown": cost_categories,
        "optimization_suggestions": suggestions
    }

@app.post("/api/v1/analyze", response_model=CostAnalysisResponse)
async def analyze_cost(request: CostAnalysisRequest):
    """分析商户成本结构"""
    try:
        # 验证日期范围合理性
        if request.end_date < request.start_date:
            raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
        
        # 验证分析深度参数
        valid_depths = ['basic', 'detailed', 'comprehensive']
        if request.analysis_depth.lower() not in valid_depths:
            raise HTTPException(status_code=400, detail="无效的分析深度参数")
        
        # 记录分析请求
        logger.info(f"收到成本分析请求: 商户={request.merchant_id}, 时间范围={request.start_date}至{request.end_date}, 深度={request.analysis_depth}")
        
        # 根据MongoDB可用性决定数据来源
        if MONGODB_AVAILABLE and not CI_MODE:
            # TODO: 实现真实数据分析逻辑
            # 暂时使用模拟数据
            logger.warning("虽然MongoDB可用，但尚未实现真实数据分析，使用模拟数据")
            result = generate_mock_cost_data(
                request.merchant_id,
                request.start_date,
                request.end_date,
                request.analysis_depth
            )
        else:
            # 使用模拟数据
            logger.info("使用模拟数据进行分析")
            result = generate_mock_cost_data(
                request.merchant_id,
                request.start_date,
                request.end_date,
                request.analysis_depth
            )
        
        logger.info(f"成本分析完成: 商户={request.merchant_id}, 总成本={result['total_cost']}, 优化建议数={len(result['optimization_suggestions'])}")
        return result
    
    except HTTPException:
        # 直接抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"分析过程中出现错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"成本分析失败: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化工作"""
    logger.info("成本分析服务启动中...")
    logger.info(f"环境信息: CI={CI_ENVIRONMENT}, DEBUG={DEBUG_MODE}, MongoDB可用={MONGODB_AVAILABLE}")
    
    # 创建必要目录
    for dir_path in ["./data", "./output", "./logs"]:
        Path(dir_path).mkdir(exist_ok=True)
    
    logger.info("成本分析服务已就绪")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理工作"""
    logger.info("成本分析服务正在关闭...")
    # 执行清理工作
    logger.info("成本分析服务已关闭")

if __name__ == "__main__":
    import uvicorn
    # 从环境变量获取端口，默认为8001
    port = int(os.getenv("PORT", 8001))
    
    # 配置服务器并启动
    logger.info(f"成本分析服务正在启动，端口: {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port) 
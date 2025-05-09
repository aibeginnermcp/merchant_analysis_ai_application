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
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"请求处理时间: {process_time:.4f}秒 - 路径: {request.url.path}")
    return response

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
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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

if __name__ == "__main__":
    import uvicorn
    # 从环境变量获取端口，默认为8001
    port = int(os.getenv("PORT", 8001))
    
    # 配置服务器并启动
    logger.info(f"成本分析服务正在启动，端口: {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port) 
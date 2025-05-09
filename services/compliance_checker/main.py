"""
合规检查服务主入口文件
提供合规检查相关API
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
    title="合规检查服务",
    description="自动检查商户经营中的合规风险点",
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
class ComplianceCheckRequest(BaseModel):
    merchant_id: str = Field(..., description="商户ID")
    start_date: date = Field(..., description="检查开始日期")
    end_date: date = Field(..., description="检查结束日期")
    check_types: List[str] = Field(
        default=["tax", "accounting", "licensing", "labor"],
        description="检查类型列表"
    )

class ComplianceStatus(BaseModel):
    tax: str = Field(..., description="税务合规状态")
    accounting: str = Field(..., description="会计合规状态")
    licensing: str = Field(..., description="许可证合规状态")
    labor: str = Field(..., description="劳工合规状态")

class ComplianceCheckResponse(BaseModel):
    request_id: str = Field(..., description="请求ID")
    merchant_id: str = Field(..., description="商户ID")
    overall_status: str = Field(..., description="整体合规状态")
    type_status: ComplianceStatus = Field(..., description="各类型合规状态")
    risk_score: float = Field(..., description="风险评分")
    issues: List[Dict[str, Any]] = Field(..., description="合规问题")
    recommendations: List[str] = Field(..., description="改进建议")

@app.get("/")
async def root():
    """服务根路径，返回简单信息"""
    return {
        "name": "合规检查服务",
        "version": "1.0.0",
        "status": "运行中",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/check", response_model=ComplianceCheckResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """
    检查合规状况
    
    此API检查商户的各项合规状况，包括税务、会计、许可证和劳工合规
    """
    try:
        logger.info(f"接收到合规检查请求: {request}")
        request_id = f"req_comp_{str(uuid.uuid4())[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 验证日期范围
        if request.end_date < request.start_date:
            raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
        
        # 验证检查类型
        valid_types = ["tax", "accounting", "licensing", "labor"]
        for check_type in request.check_types:
            if check_type not in valid_types:
                raise HTTPException(status_code=400, detail=f"无效的检查类型: {check_type}")
        
        # 模拟合规检查结果
        overall_status = "needs_review"
        
        # 模拟各类型状态
        type_status = ComplianceStatus(
            tax="compliant",
            accounting="needs_review",
            licensing="non_compliant",
            labor="compliant"
        )
        
        # 模拟风险评分 (0-100，越高风险越大)
        risk_score = 42.5
        
        # 模拟合规问题
        issues = [
            {
                "area": "licensing",
                "severity": "high",
                "description": "营业执照即将过期",
                "deadline": "2023-06-30"
            },
            {
                "area": "accounting",
                "severity": "medium",
                "description": "账目记录不完整",
                "details": "3月份缺少部分交易记录"
            }
        ]
        
        # 模拟建议
        recommendations = [
            "尽快更新营业执照，避免过期带来的罚款和业务中断",
            "完善3月份的账目记录，确保财务报表准确性",
            "考虑聘请专业会计服务，规范财务流程"
        ]
        
        # 记录检查完成
        logger.info(f"合规检查完成，请求ID: {request_id}")
        
        # 返回检查结果
        return ComplianceCheckResponse(
            request_id=request_id,
            merchant_id=request.merchant_id,
            overall_status=overall_status,
            type_status=type_status,
            risk_score=risk_score,
            issues=issues,
            recommendations=recommendations
        )
    
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"检查合规时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # 从环境变量获取端口，默认为8003
    port = int(os.getenv("PORT", 8003))
    
    # 配置服务器并启动
    logger.info(f"合规检查服务正在启动，端口: {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port) 
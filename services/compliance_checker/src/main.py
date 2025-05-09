"""
财务合规检查服务的主入口
"""
import os
import logging
import sys
import asyncio
import uvicorn
import uuid
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import prometheus_client
from prometheus_client import Counter, Histogram
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from services.compliance_checker.src.models import (
    TimeRange,
    ComplianceType,
    RiskLevel,
    ComplianceStatus,
    DocumentType,
    ComplianceRule,
    ComplianceViolation,
    ComplianceDocument,
    ComplianceCheckResult,
    ComplianceCheckRequest,
    ComplianceCheckResponse
)
from services.compliance_checker.src.service import ComplianceCheckerService
from services.compliance_checker.src.storage import MongoDBStorage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("compliance_checker")

# 创建FastAPI应用
app = FastAPI(
    title="财务合规检查服务",
    description="为商户分析平台提供财务合规检查功能",
    version="1.0.0"
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 监控指标
REQUEST_COUNT = Counter(
    "compliance_checker_request_count", 
    "Number of requests received",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "compliance_checker_request_latency_seconds", 
    "Request latency in seconds",
    ["method", "endpoint"]
)

# 全局服务实例
compliance_service = ComplianceCheckerService()

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """收集请求指标的中间件"""
    start_time = time.time()
    
    # 为请求添加追踪ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        REQUEST_COUNT.labels(
            method=request.method, 
            endpoint=request.url.path, 
            status_code=status_code
        ).inc()
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        logger.exception(f"Request failed: {e}")
        status_code = 500
        return JSONResponse(
            status_code=status_code,
            content={"detail": "Internal server error", "request_id": request_id}
        )
    finally:
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(
            method=request.method, 
            endpoint=request.url.path
        ).observe(duration)

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """导出Prometheus监控指标"""
    return prometheus_client.generate_latest()

class APIRouter:
    """API路由类"""
    
    def __init__(self, app: FastAPI, service: ComplianceCheckerService):
        self.app = app
        self.service = service
        self.register_routes()
    
    def register_routes(self):
        """注册API路由"""
        
        @self.app.post("/api/v1/check", response_model=ComplianceCheckResponse)
        async def check_compliance(request: ComplianceCheckRequest):
            """执行合规检查"""
            try:
                result = await self.service.check_compliance(request)
                return ComplianceCheckResponse(
                    request_id=str(uuid.uuid4()),
                    result=result,
                    status="success"
                )
            except Exception as e:
                logger.exception(f"Compliance check failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Compliance check failed: {str(e)}"
                )
        
        @self.app.get("/api/v1/checks/{check_id}", response_model=ComplianceCheckResult)
        async def get_check_result(check_id: str):
            """获取检查结果"""
            result = await self.service.get_check_result(check_id)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Check result with ID {check_id} not found"
                )
            return result
        
        @self.app.get("/api/v1/merchants/{merchant_id}/checks", response_model=List[ComplianceCheckResult])
        async def get_merchant_checks(
            merchant_id: str,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            limit: int = 10
        ):
            """获取商户的检查历史"""
            time_range = None
            if start_date and end_date:
                time_range = TimeRange(start_date=start_date, end_date=end_date)
                
            return await self.service.get_merchant_check_results(merchant_id, time_range, limit)
        
        @self.app.post("/api/v1/documents", response_model=ComplianceDocument)
        async def create_document(
            merchant_id: str,
            type: DocumentType,
            name: str,
            issuing_authority: str,
            document_number: Optional[str] = None,
            status: str = "valid"
        ):
            """创建合规文档"""
            try:
                now = datetime.now()
                document = await self.service.create_document(
                    merchant_id=merchant_id,
                    type=type,
                    name=name,
                    issue_date=now,
                    expiry_date=now.replace(year=now.year + 1),  # 默认一年有效期
                    issuing_authority=issuing_authority,
                    document_number=document_number,
                    status=status
                )
                return document
            except Exception as e:
                logger.exception(f"Failed to create document: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create document: {str(e)}"
                )
        
        @self.app.get("/api/v1/merchants/{merchant_id}/documents", response_model=List[ComplianceDocument])
        async def get_merchant_documents(merchant_id: str):
            """获取商户的所有文档"""
            return await self.service.get_merchant_documents(merchant_id)

# 创建API路由
api_router = APIRouter(app, compliance_service)

async def startup():
    """应用启动时的初始化工作"""
    logger.info("Starting compliance checker service...")
    
async def shutdown():
    """应用关闭时的清理工作"""
    logger.info("Shutting down compliance checker service...")

@app.on_event("startup")
async def startup_event():
    await startup()

@app.on_event("shutdown")
async def shutdown_event():
    await shutdown()

def start():
    """启动应用"""
    uvicorn.run(
        "services.compliance_checker.src.main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8003)),
        reload=os.environ.get("DEBUG", "false").lower() == "true",
        log_level="info"
    )

if __name__ == "__main__":
    start() 
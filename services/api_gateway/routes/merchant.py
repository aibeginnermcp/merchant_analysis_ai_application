"""商户分析路由模块"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
import asyncio
import json

from core.auth import get_current_user
from core.clients import (
    DataSimulatorClient,
    CashFlowClient,
    CostAnalysisClient,
    ComplianceClient
)
from models.merchant import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    AnalysisType
)
from shared.errors import (
    ServiceError,
    AnalysisError,
    DataNotFoundError,
    handle_service_error
)
from core.monitoring import REQUEST_COUNT, ERROR_COUNT

router = APIRouter(prefix="/merchant", tags=["merchant"])

# 初始化服务客户端
data_simulator = DataSimulatorClient()
cashflow_client = CashFlowClient()
cost_analysis_client = CostAnalysisClient()
compliance_client = ComplianceClient()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_merchant(
    request: AnalysisRequest,
    current_user = Depends(get_current_user)
):
    """商户分析接口
    
    Args:
        request: 分析请求参数
        current_user: 当前用户信息
        
    Returns:
        AnalysisResponse: 分析结果
        
    Raises:
        HTTPException: 请求处理失败时抛出异常
    """
    try:
        # 1. 生成模拟数据
        try:
            simulated_data = await data_simulator.generate_data(
                merchant_id=request.merchant_id,
                start_date=request.time_range.start,
                end_date=request.time_range.end,
                industry=request.merchant_type
            )
        except ServiceError as e:
            raise AnalysisError(
                analysis_type="数据模拟",
                reason=e.message,
                service=e.service,
                details=e.details
            )
        
        # 2. 并行调用各个分析服务
        analysis_tasks = []
        
        if AnalysisType.CASH_FLOW in request.analysis_modules:
            analysis_tasks.append(
                cashflow_client.predict(
                    merchant_id=request.merchant_id,
                    historical_data=simulated_data["transactions"],
                    prediction_days=request.prediction_days or 30
                )
            )
            
        if AnalysisType.COST in request.analysis_modules:
            analysis_tasks.append(
                cost_analysis_client.analyze(
                    merchant_id=request.merchant_id,
                    cost_data=simulated_data["costs"],
                    industry=request.merchant_type
                )
            )
            
        if AnalysisType.COMPLIANCE in request.analysis_modules:
            analysis_tasks.append(
                compliance_client.check(
                    merchant_id=request.merchant_id,
                    profile=simulated_data["profile"],
                    compliance_records=simulated_data["compliance_records"]
                )
            )
            
        # 等待所有分析任务完成
        try:
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        except Exception as e:
            raise AnalysisError(
                analysis_type="并行分析",
                reason="部分或全部分析任务失败",
                details={"error": str(e)}
            )
            
        # 处理每个分析结果
        results = {}
        for module, result in zip(request.analysis_modules, analysis_results):
            if isinstance(result, Exception):
                error = handle_service_error(result)
                results[module] = {
                    "status": "error",
                    "error": error.to_dict()
                }
                ERROR_COUNT.labels(
                    method="POST",
                    endpoint="/merchant/analyze",
                    error_type=type(error).__name__
                ).inc()
            else:
                results[module] = {
                    "status": "success",
                    "data": result
                }
                
        REQUEST_COUNT.labels(
            method="POST",
            endpoint="/merchant/analyze",
            status=200
        ).inc()
            
        return AnalysisResponse(
            merchant_id=request.merchant_id,
            analysis_date=datetime.now(),
            results=results,
            status=AnalysisStatus.COMPLETED
        )
        
    except Exception as e:
        error = handle_service_error(e)
        ERROR_COUNT.labels(
            method="POST",
            endpoint="/merchant/analyze",
            error_type=type(error).__name__
        ).inc()
        
        raise HTTPException(
            status_code=500,
            detail=error.to_dict()
        )

@router.get("/analysis/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    current_user = Depends(get_current_user)
):
    """获取分析结果
    
    Args:
        analysis_id: 分析任务ID
        current_user: 当前用户信息
        
    Returns:
        Dict: 分析结果
        
    Raises:
        HTTPException: 获取结果失败时抛出异常
    """
    try:
        # 从Redis缓存获取结果
        cache_key = f"analysis:{analysis_id}"
        cached_result = await redis.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
            
        # 从MongoDB获取结果
        result = await db.analysis_results.find_one(
            {"analysis_id": analysis_id}
        )
        
        if not result:
            raise DataNotFoundError(
                resource="分析结果",
                resource_id=analysis_id
            )
            
        # 缓存结果
        await redis.set(
            cache_key,
            json.dumps(result),
            expire=3600  # 1小时过期
        )
        
        REQUEST_COUNT.labels(
            method="GET",
            endpoint="/merchant/analysis/{analysis_id}",
            status=200
        ).inc()
        
        return result
        
    except Exception as e:
        error = handle_service_error(e)
        ERROR_COUNT.labels(
            method="GET",
            endpoint="/merchant/analysis/{analysis_id}",
            error_type=type(error).__name__
        ).inc()
        
        if isinstance(error, DataNotFoundError):
            status_code = 404
        else:
            status_code = 500
            
        raise HTTPException(
            status_code=status_code,
            detail=error.to_dict()
        )

@router.get("/history")
async def get_analysis_history(
    merchant_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    current_user = Depends(get_current_user)
):
    """获取分析历史
    
    Args:
        merchant_id: 商户ID
        start_date: 开始日期
        end_date: 结束日期
        page: 页码
        page_size: 每页大小
        current_user: 当前用户信息
        
    Returns:
        Dict: 分页的分析历史记录
    """
    try:
        # 构建查询条件
        query = {}
        if merchant_id:
            query["merchant_id"] = merchant_id
        if start_date and end_date:
            query["analysis_date"] = {
                "$gte": start_date,
                "$lte": end_date
            }
            
        # 计算总记录数
        total = await db.analysis_results.count_documents(query)
        
        # 获取分页数据
        skip = (page - 1) * page_size
        cursor = db.analysis_results.find(query)
        cursor.skip(skip).limit(page_size)
        
        results = []
        async for doc in cursor:
            results.append(doc)
            
        REQUEST_COUNT.labels(
            method="GET",
            endpoint="/merchant/history",
            status=200
        ).inc()
            
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": results
        }
        
    except Exception as e:
        error = handle_service_error(e)
        ERROR_COUNT.labels(
            method="GET",
            endpoint="/merchant/history",
            error_type=type(error).__name__
        ).inc()
        
        raise HTTPException(
            status_code=500,
            detail=error.to_dict()
        ) 
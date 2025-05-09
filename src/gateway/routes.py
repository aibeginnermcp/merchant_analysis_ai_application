"""
路由处理模块
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .models import (
    AnalysisRequest,
    AnalysisResponse,
    MerchantInfo,
    TransactionData,
    AnalysisType
)
from .auth import (
    User,
    get_current_active_user,
    create_access_token,
    verify_password
)
from src.shared.database import db_manager
from src.shared.cache import cache_manager
from src.shared.queue import queue_manager
from src.shared.discovery import discovery

router = APIRouter()

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录
    
    Args:
        form_data: 登录表单数据
        
    Returns:
        dict: Token信息
        
    Raises:
        HTTPException: 认证失败
    """
    # 从数据库验证用户
    merchant_collection = await db_manager.get_merchant_collection()
    merchant = await merchant_collection.find_one({"username": form_data.username})
    
    if not merchant or not verify_password(form_data.password, merchant["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(merchant["_id"])},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800
    }

@router.post("/merchant/analyze", response_model=AnalysisResponse)
async def analyze_merchant(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """商户分析接口
    
    Args:
        request: 分析请求
        current_user: 当前用户
        
    Returns:
        AnalysisResponse: 分析响应
    """
    # 验证商户权限
    if current_user.merchant_id != request.merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该商户数据"
        )
    
    # 检查缓存
    cache_key = await cache_manager.get_analysis_cache_key(
        request.merchant_id,
        "full_analysis"
    )
    cached_result = await cache_manager.get(cache_key)
    if cached_result:
        return AnalysisResponse(**cached_result)
    
    # 调用各个分析服务
    results = {}
    for module in request.analysis_modules:
        try:
            # 获取服务地址
            service_name = f"merchant-analysis-{module.lower()}"
            service_url = discovery.get_service_address(service_name)
            
            # 发布分析任务
            await queue_manager.publish_analysis_task(
                request.merchant_id,
                module,
                {
                    "time_range": request.time_range.dict(),
                    "prediction_days": request.prediction_days
                }
            )
            
            # 设置初始状态
            results[module] = {
                "status": "processing",
                "data": None
            }
        except LookupError:
            results[module] = {
                "status": "error",
                "error": f"服务{service_name}不可用"
            }
    
    response = AnalysisResponse(
        merchant_id=request.merchant_id,
        analysis_date=datetime.utcnow(),
        status="PROCESSING",
        results=results
    )
    
    # 缓存结果
    await cache_manager.set(
        cache_key,
        response.dict(),
        expire=300  # 5分钟缓存
    )
    
    return response

@router.get("/merchant/{merchant_id}", response_model=MerchantInfo)
async def get_merchant_info(
    merchant_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """获取商户信息
    
    Args:
        merchant_id: 商户ID
        current_user: 当前用户
        
    Returns:
        MerchantInfo: 商户信息
        
    Raises:
        HTTPException: 无权访问或商户不存在
    """
    # 验证商户权限
    if current_user.merchant_id != merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该商户数据"
        )
    
    # 检查缓存
    cache_key = await cache_manager.get_merchant_cache_key(merchant_id)
    cached_info = await cache_manager.get(cache_key)
    if cached_info:
        return MerchantInfo(**cached_info)
    
    # 从数据库获取商户信息
    merchant_collection = await db_manager.get_merchant_collection()
    merchant = await merchant_collection.find_one({"_id": merchant_id})
    
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商户不存在"
        )
    
    merchant_info = MerchantInfo(
        merchant_id=str(merchant["_id"]),
        name=merchant["name"],
        industry=merchant["industry"],
        size=merchant["size"],
        establishment_date=merchant["establishment_date"],
        location=merchant["location"],
        business_hours=merchant["business_hours"],
        payment_methods=merchant["payment_methods"],
        rating=merchant["rating"]
    )
    
    # 缓存商户信息
    await cache_manager.set(
        cache_key,
        merchant_info.dict(),
        expire=3600  # 1小时缓存
    )
    
    return merchant_info

@router.get("/merchant/{merchant_id}/transactions", response_model=List[TransactionData])
async def get_merchant_transactions(
    merchant_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
):
    """获取商户交易数据
    
    Args:
        merchant_id: 商户ID
        start_date: 开始日期
        end_date: 结束日期
        current_user: 当前用户
        
    Returns:
        List[TransactionData]: 交易数据列表
        
    Raises:
        HTTPException: 无权访问或商户不存在
    """
    # 验证商户权限
    if current_user.merchant_id != merchant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该商户数据"
        )
    
    # 构建查询条件
    query = {"merchant_id": merchant_id}
    if start_date:
        query["date"] = {"$gte": start_date}
    if end_date:
        query["date"] = {"$lte": end_date}
    
    # 从数据库获取交易数据
    transaction_collection = await db_manager.get_transaction_collection()
    transactions = []
    async for doc in transaction_collection.find(query).sort("date", -1):
        transactions.append(TransactionData(
            date=doc["date"],
            revenue=doc["revenue"],
            transaction_count=doc["transaction_count"],
            average_transaction_value=doc["average_transaction_value"],
            peak_hours=doc["peak_hours"],
            payment_distribution=doc["payment_distribution"],
            channel_distribution=doc["channel_distribution"],
            refund_amount=doc["refund_amount"]
        ))
    
    return transactions

@router.get("/health")
async def health_check():
    """健康检查接口
    
    Returns:
        dict: 健康状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    } 
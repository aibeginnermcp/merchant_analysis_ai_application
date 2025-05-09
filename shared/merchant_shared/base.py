"""
商户智能分析平台基础共享组件
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal

class TimeRange(BaseModel):
    """时间范围模型"""
    start: datetime
    end: datetime

class BaseRequest(BaseModel):
    """基础请求模型"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    
class BaseResponse(BaseModel):
    """基础响应模型"""
    code: int = Field(0, description="响应码")
    message: str = Field("success", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    request_id: str = Field(..., description="请求ID")

class MoneyAmount(BaseModel):
    """金额模型"""
    amount: Decimal = Field(..., description="金额")
    currency: str = Field("CNY", description="币种")
    
class BusinessMetrics(BaseModel):
    """业务指标模型"""
    accuracy: float = Field(..., description="准确率")
    processing_time: float = Field(..., description="处理时间(秒)")
    error_rate: float = Field(..., description="错误率") 
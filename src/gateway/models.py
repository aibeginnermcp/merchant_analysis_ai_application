"""
API网关数据模型定义
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class AnalysisType(str, Enum):
    """分析类型枚举"""
    CASH_FLOW = "CASH_FLOW"
    COST = "COST"
    COMPLIANCE = "COMPLIANCE"

class TimeRange(BaseModel):
    """时间范围模型"""
    start: datetime = Field(..., description="开始时间")
    end: datetime = Field(..., description="结束时间")

class AnalysisRequest(BaseModel):
    """分析请求模型"""
    merchant_id: str = Field(..., description="商户ID")
    merchant_type: str = Field(..., description="商户类型")
    time_range: TimeRange = Field(..., description="分析时间范围")
    analysis_modules: List[AnalysisType] = Field(..., description="需要执行的分析模块")
    prediction_days: int = Field(30, description="预测天数", ge=1, le=365)

class AnalysisResult(BaseModel):
    """分析结果模型"""
    status: str = Field(..., description="分析状态")
    data: Optional[Dict[str, Any]] = Field(None, description="分析数据")
    error: Optional[str] = Field(None, description="错误信息")

class AnalysisResponse(BaseModel):
    """分析响应模型"""
    merchant_id: str = Field(..., description="商户ID")
    analysis_date: datetime = Field(..., description="分析时间")
    status: str = Field(..., description="总体状态")
    results: Dict[str, AnalysisResult] = Field(..., description="各模块分析结果")

class MerchantInfo(BaseModel):
    """商户信息模型"""
    merchant_id: str = Field(..., description="商户ID")
    name: str = Field(..., description="商户名称")
    industry: str = Field(..., description="行业类型")
    size: str = Field(..., description="规模大小")
    establishment_date: datetime = Field(..., description="成立日期")
    location: Dict[str, float] = Field(..., description="位置信息")
    business_hours: Dict[str, str] = Field(..., description="营业时间")
    payment_methods: List[str] = Field(..., description="支付方式")
    rating: float = Field(..., description="评分", ge=0, le=5)

class TransactionData(BaseModel):
    """交易数据模型"""
    date: datetime = Field(..., description="交易日期")
    revenue: float = Field(..., description="营业收入")
    transaction_count: int = Field(..., description="交易笔数")
    average_transaction_value: float = Field(..., description="平均客单价")
    peak_hours: List[str] = Field(..., description="高峰时段")
    payment_distribution: Dict[str, float] = Field(..., description="支付方式分布")
    channel_distribution: Dict[str, float] = Field(..., description="渠道分布")
    refund_amount: float = Field(..., description="退款金额") 
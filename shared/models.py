"""
共享数据模型定义

包含:
- 基础响应模型
- 错误响应模型
- 分页模型
- 通用查询模型
"""

from typing import TypeVar, Generic, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class ErrorCode(str, Enum):
    """错误码枚举"""
    INVALID_REQUEST = "INVALID_REQUEST"  # 无效请求
    UNAUTHORIZED = "UNAUTHORIZED"        # 未授权
    FORBIDDEN = "FORBIDDEN"             # 禁止访问
    NOT_FOUND = "NOT_FOUND"            # 资源未找到
    INTERNAL_ERROR = "INTERNAL_ERROR"   # 内部错误
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"  # 服务不可用
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 数据验证错误

class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    success: bool = Field(default=True, description="请求是否成功")
    code: str = Field(default="200", description="业务状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class ErrorResponse(BaseResponse):
    """错误响应模型"""
    success: bool = Field(default=False, description="请求失败")
    error_code: ErrorCode = Field(..., description="错误码")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")

class PaginationParams(BaseModel):
    """分页查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")

class PaginatedResponse(BaseResponse, Generic[T]):
    """分页响应模型"""
    data: List[T] = Field(default_factory=list, description="分页数据")
    total: int = Field(default=0, description="总记录数")
    total_pages: int = Field(default=0, description="总页数")
    current_page: int = Field(default=1, description="当前页码")

class QueryFilter(BaseModel):
    """通用查询过滤器"""
    field: str = Field(..., description="过滤字段")
    operator: str = Field(..., description="操作符")
    value: Any = Field(..., description="过滤值")

class SortOrder(str, Enum):
    """排序方向枚举"""
    ASC = "asc"
    DESC = "desc"

class QueryParams(BaseModel):
    """通用查询参数"""
    filters: Optional[List[QueryFilter]] = Field(default=None, description="过滤条件")
    sort_by: Optional[str] = Field(default=None, description="排序字段")
    sort_order: Optional[SortOrder] = Field(default=SortOrder.ASC, description="排序方向")
    pagination: Optional[PaginationParams] = Field(default=None, description="分页参数")

class MerchantBase(BaseModel):
    """商户基础信息"""
    merchant_id: str = Field(..., description="商户ID")
    merchant_name: str = Field(..., description="商户名称")
    business_type: str = Field(..., description="经营类型")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class AnalysisType(str, Enum):
    """分析类型枚举"""
    CASHFLOW = "CASHFLOW"
    COST = "COST"
    COMPLIANCE = "COMPLIANCE"

class AnalysisStatus(str, Enum):
    """分析状态枚举"""
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TimeRange(BaseModel):
    """时间范围模型"""
    start: datetime = Field(..., description="开始时间")
    end: datetime = Field(..., description="结束时间")

class AnalysisParameters(BaseModel):
    """分析参数模型"""
    prediction_days: Optional[int] = Field(30, description="预测天数")
    confidence_level: Optional[float] = Field(0.95, description="置信水平")

class AnalysisRequest(BaseModel):
    """分析请求模型"""
    merchant_id: str = Field(..., description="商户ID")
    analysis_type: List[AnalysisType] = Field(..., description="分析类型列表")
    time_range: TimeRange = Field(..., description="时间范围")
    parameters: Optional[AnalysisParameters] = Field(None, description="分析参数")

class AnalysisResponse(BaseModel):
    """分析响应基础模型"""
    request_id: str = Field(..., description="请求ID")
    merchant_id: str = Field(..., description="商户ID")
    analysis_type: str = Field(..., description="分析类型")
    analysis_time: datetime = Field(default_factory=datetime.now, description="分析时间")
    status: str = Field(..., description="分析状态")
    results: Dict[str, Any] = Field(..., description="分析结果")
    summary: Optional[str] = Field(None, description="分析总结")
    recommendations: Optional[List[str]] = Field(None, description="建议")

class AnalysisResult(BaseModel):
    """分析结果模型"""
    analysis_id: str = Field(..., description="分析ID")
    merchant_id: str = Field(..., description="商户ID")
    status: AnalysisStatus = Field(..., description="分析状态")
    results: Dict[AnalysisType, Any] = Field({}, description="分析结果")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class DataResponse(BaseResponse):
    """数据响应模型"""
    data: Optional[Any] = Field(None, description="响应数据")

class ListResponse(BaseResponse):
    """列表响应模型"""
    data: List[Any] = Field([], description="响应数据列表")
    total: int = Field(0, description="总数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(20, description="每页大小") 
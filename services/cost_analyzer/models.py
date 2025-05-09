"""
成本穿透分析服务的数据模型定义
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator

class TimeRange(BaseModel):
    """时间范围模型"""
    start_date: str = Field(..., description="开始日期，格式：YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期，格式：YYYY-MM-DD")
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期必须晚于开始日期')
        return v

class CostCategory(str, Enum):
    """成本类别枚举"""
    DIRECT_MATERIAL = "direct_material"  # 直接材料
    DIRECT_LABOR = "direct_labor"  # 直接人工
    MANUFACTURING_OVERHEAD = "manufacturing_overhead"  # 制造费用
    SALES_MARKETING = "sales_marketing"  # 销售和市场费用
    ADMIN_GENERAL = "admin_general"  # 管理和一般费用
    RENT = "rent"  # 租金
    UTILITIES = "utilities"  # 水电费
    LOGISTICS = "logistics"  # 物流费用
    PACKAGING = "packaging"  # 包装费用
    OTHER = "other"  # 其他费用

class CostAllocationMethod(str, Enum):
    """成本分配方法枚举"""
    DIRECT = "direct"  # 直接分配
    ACTIVITY_BASED = "activity_based"  # 基于活动分配
    PROPORTIONAL = "proportional"  # 比例分配
    WEIGHTED = "weighted"  # 加权分配

class CostItem(BaseModel):
    """成本项目模型"""
    cost_id: str = Field(..., description="成本ID")
    merchant_id: str = Field(..., description="商户ID")
    category: CostCategory = Field(..., description="成本类别")
    subcategory: Optional[str] = Field(None, description="成本子类别")
    date: str = Field(..., description="发生日期，格式：YYYY-MM-DD")
    amount: float = Field(..., description="金额", gt=0)
    description: Optional[str] = Field(None, description="描述")
    fixed_variable_ratio: float = Field(0.5, description="固定成本与变动成本比例", ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class CostData(BaseModel):
    """成本数据模型"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    items: List[CostItem] = Field(..., description="成本项目列表")
    total_amount: float = Field(..., description="总金额")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class CostDriverType(str, Enum):
    """成本驱动因素类型枚举"""
    ACTIVITY = "activity"  # 活动驱动
    RESOURCE = "resource"  # 资源驱动
    TIME = "time"  # 时间驱动
    VOLUME = "volume"  # 数量驱动

class CostDriver(BaseModel):
    """成本驱动因素模型"""
    driver_id: str = Field(..., description="驱动因素ID")
    name: str = Field(..., description="名称")
    type: CostDriverType = Field(..., description="类型")
    unit: str = Field(..., description="单位")
    description: Optional[str] = Field(None, description="描述")
    impact_weight: float = Field(1.0, description="影响权重", gt=0)
    
class CostBreakdownItem(BaseModel):
    """成本拆解项目模型"""
    category: CostCategory = Field(..., description="成本类别")
    subcategory: Optional[str] = Field(None, description="成本子类别")
    amount: float = Field(..., description="金额")
    percentage: float = Field(..., description="占比", ge=0, le=100)
    fixed_amount: float = Field(..., description="固定成本金额", ge=0)
    variable_amount: float = Field(..., description="变动成本金额", ge=0)
    drivers: Optional[List[Dict[str, Any]]] = Field(None, description="关联的驱动因素")

class CostBreakdown(BaseModel):
    """成本拆解模型"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    total_amount: float = Field(..., description="总金额")
    items: List[CostBreakdownItem] = Field(..., description="拆解项目列表")
    created_at: datetime = Field(..., description="创建时间")

class CostTrendPoint(BaseModel):
    """成本趋势点模型"""
    date: str = Field(..., description="日期，格式：YYYY-MM-DD")
    amount: float = Field(..., description="金额")
    category: Optional[CostCategory] = Field(None, description="成本类别")

class CostTrend(BaseModel):
    """成本趋势模型"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    overall_trend: List[CostTrendPoint] = Field(..., description="总体趋势")
    category_trends: Dict[CostCategory, List[CostTrendPoint]] = Field(..., description="分类趋势")
    created_at: datetime = Field(..., description="创建时间")

class CostOptimizationSuggestion(BaseModel):
    """成本优化建议模型"""
    suggestion_id: str = Field(..., description="建议ID")
    category: CostCategory = Field(..., description="成本类别")
    subcategory: Optional[str] = Field(None, description="成本子类别")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    potential_saving: float = Field(..., description="潜在节省金额")
    saving_percentage: float = Field(..., description="节省百分比", ge=0, le=100)
    difficulty: int = Field(3, description="实施难度", ge=1, le=5)
    implementation_time: str = Field(..., description="实施时间")
    priority: int = Field(2, description="优先级", ge=1, le=3)

class CostAnalysis(BaseModel):
    """成本分析模型"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    breakdown: CostBreakdown = Field(..., description="成本拆解")
    trend: Optional[CostTrend] = Field(None, description="成本趋势")
    optimization_suggestions: Optional[List[CostOptimizationSuggestion]] = Field(None, description="优化建议")
    created_at: datetime = Field(..., description="创建时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class CostAnalysisRequest(BaseModel):
    """成本分析请求模型"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    include_trend: bool = Field(True, description="是否包含趋势分析")
    include_suggestions: bool = Field(True, description="是否包含优化建议")

class CostAnalysisResponse(BaseModel):
    """成本分析响应模型"""
    request_id: str = Field(..., description="请求ID")
    analysis: CostAnalysis = Field(..., description="成本分析")
    status: str = Field("success", description="状态")
    error: Optional[str] = Field(None, description="错误信息") 
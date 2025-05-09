from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class BusinessMetrics(BaseModel):
    """
    商户经营指标模型
    """
    revenue: float = Field(..., description="营业收入")
    cost: float = Field(..., description="经营成本")
    gross_profit: float = Field(..., description="毛利润")
    operating_expenses: float = Field(..., description="运营费用")
    net_profit: float = Field(..., description="净利润")

class CashFlowMetrics(BaseModel):
    """
    现金流指标模型
    """
    operating_cash_flow: float = Field(..., description="经营现金流")
    investing_cash_flow: float = Field(..., description="投资现金流")
    financing_cash_flow: float = Field(..., description="筹资现金流")
    net_cash_flow: float = Field(..., description="净现金流")

class ComplianceStatus(BaseModel):
    """
    合规状态模型
    """
    is_compliant: bool = Field(..., description="是否合规")
    risk_level: str = Field(..., description="风险等级")
    issues: List[str] = Field(default_factory=list, description="合规问题列表")

class MerchantAnalysis(BaseModel):
    """
    商户分析报告模型
    """
    merchant_id: str = Field(..., description="商户ID")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")
    business_metrics: BusinessMetrics = Field(..., description="经营指标")
    cash_flow_metrics: CashFlowMetrics = Field(..., description="现金流指标")
    compliance_status: ComplianceStatus = Field(..., description="合规状态")
    recommendations: List[str] = Field(default_factory=list, description="优化建议")

class AnalysisRequest(BaseModel):
    """
    分析请求模型
    """
    merchant_id: str = Field(..., description="商户ID")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    analysis_types: List[str] = Field(..., description="分析类型列表")

class AnalysisResponse(BaseModel):
    """
    分析响应模型
    """
    request_id: str = Field(..., description="请求ID")
    status: str = Field(..., description="处理状态")
    data: Optional[MerchantAnalysis] = Field(None, description="分析结果")
    error: Optional[str] = Field(None, description="错误信息") 
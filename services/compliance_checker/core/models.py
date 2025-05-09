"""
合规检查服务核心数据模型定义
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MerchantInfo(BaseModel):
    """
    商户基础信息模型
    """
    merchant_id: str = Field(..., description="商户唯一标识")
    merchant_name: str = Field(..., description="商户名称")
    business_type: str = Field(..., description="经营类型")
    license_no: str = Field(..., description="营业执照号")
    registered_capital: float = Field(..., description="注册资本")
    establishment_date: datetime = Field(..., description="成立日期")
    legal_representative: str = Field(..., description="法定代表人")
    business_scope: str = Field(..., description="经营范围")
    
class RuleDefinition(BaseModel):
    """
    规则定义模型
    """
    rule_id: str = Field(..., description="规则ID")
    rule_name: str = Field(..., description="规则名称")
    rule_type: str = Field(..., description="规则类型", example="financial/qualification/risk")
    rule_description: str = Field(..., description="规则描述")
    check_method: str = Field(..., description="检查方法")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="规则参数")
    severity: str = Field(..., description="严重程度", example="high/medium/low")
    enabled: bool = Field(default=True, description="是否启用")
    
class CheckResult(BaseModel):
    """
    检查结果模型
    """
    check_id: str = Field(..., description="检查ID")
    merchant_id: str = Field(..., description="商户ID")
    rule_id: str = Field(..., description="触发规则ID")
    check_time: datetime = Field(default_factory=datetime.now, description="检查时间")
    result: bool = Field(..., description="检查结果")
    violation_details: Optional[Dict[str, Any]] = Field(None, description="违规详情")
    risk_level: str = Field(..., description="风险等级", example="high/medium/low")
    suggestions: List[str] = Field(default_factory=list, description="整改建议")

class ComplianceReport(BaseModel):
    """
    合规报告模型
    """
    report_id: str = Field(..., description="报告ID")
    merchant_id: str = Field(..., description="商户ID")
    check_time: datetime = Field(default_factory=datetime.now, description="检查时间")
    overall_status: str = Field(..., description="整体合规状态")
    risk_score: float = Field(..., description="风险评分")
    check_results: List[CheckResult] = Field(..., description="检查结果列表")
    summary: str = Field(..., description="总体评估")
    recommendations: List[str] = Field(default_factory=list, description="改进建议") 
"""
财务合规检查服务的数据模型定义
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

class ComplianceType(str, Enum):
    """合规类型枚举"""
    TAX = "tax"  # 税务合规
    ACCOUNTING = "accounting"  # 会计准则合规
    LICENSING = "licensing"  # 许可证合规
    LABOR = "labor"  # 劳动法规合规
    ENVIRONMENTAL = "environmental"  # 环保法规合规
    INDUSTRY_SPECIFIC = "industry_specific"  # 行业特定法规
    DATA_PRIVACY = "data_privacy"  # 数据隐私合规
    FINANCIAL_REPORTING = "financial_reporting"  # 财务报告合规

class RiskLevel(str, Enum):
    """风险等级枚举"""
    LOW = "low"  # 低风险
    MEDIUM = "medium"  # 中等风险
    HIGH = "high"  # 高风险
    CRITICAL = "critical"  # 严重风险

class ComplianceStatus(str, Enum):
    """合规状态枚举"""
    COMPLIANT = "compliant"  # 合规
    NON_COMPLIANT = "non_compliant"  # 不合规
    NEEDS_REVIEW = "needs_review"  # 需要审查
    EXEMPTED = "exempted"  # 获得豁免

class DocumentType(str, Enum):
    """文档类型枚举"""
    LICENSE = "license"  # 许可证
    CERTIFICATE = "certificate"  # 证书
    REPORT = "report"  # 报告
    DECLARATION = "declaration"  # 申报表
    CONTRACT = "contract"  # 合同
    RECEIPT = "receipt"  # 收据
    INVOICE = "invoice"  # 发票
    OTHER = "other"  # 其他

class ComplianceRule(BaseModel):
    """合规规则模型"""
    rule_id: str = Field(..., description="规则ID")
    type: ComplianceType = Field(..., description="合规类型")
    name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    applies_to: List[str] = Field(..., description="适用的商户类型")
    threshold: Optional[Dict[str, Any]] = Field(None, description="阈值参数")
    check_frequency: str = Field(..., description="检查频率：daily, weekly, monthly, quarterly, yearly")
    data_requirements: List[str] = Field(..., description="所需数据")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class ComplianceViolation(BaseModel):
    """合规违规模型"""
    violation_id: str = Field(..., description="违规ID")
    merchant_id: str = Field(..., description="商户ID")
    rule_id: str = Field(..., description="规则ID") 
    type: ComplianceType = Field(..., description="合规类型")
    description: str = Field(..., description="违规描述")
    detection_date: datetime = Field(..., description="检测日期")
    risk_level: RiskLevel = Field(..., description="风险等级")
    status: ComplianceStatus = Field(ComplianceStatus.NON_COMPLIANT, description="当前状态")
    resolution_deadline: Optional[datetime] = Field(None, description="解决期限")
    resolved_date: Optional[datetime] = Field(None, description="解决日期")
    evidence: Optional[Dict[str, Any]] = Field(None, description="证据数据")
    
    @validator('resolved_date')
    def resolved_date_must_be_after_detection(cls, v, values):
        if v and 'detection_date' in values and v < values['detection_date']:
            raise ValueError('解决日期必须晚于检测日期')
        return v

class ComplianceDocument(BaseModel):
    """合规文档模型"""
    document_id: str = Field(..., description="文档ID")
    merchant_id: str = Field(..., description="商户ID")
    type: DocumentType = Field(..., description="文档类型")
    name: str = Field(..., description="文档名称")
    issue_date: datetime = Field(..., description="签发日期")
    expiry_date: Optional[datetime] = Field(None, description="过期日期")
    issuing_authority: str = Field(..., description="签发机构")
    document_number: Optional[str] = Field(None, description="文档编号")
    status: str = Field(..., description="状态：valid, expired, revoked")
    file_path: Optional[str] = Field(None, description="文件路径")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    @validator('expiry_date')
    def expiry_date_must_be_after_issue(cls, v, values):
        if v and 'issue_date' in values and v < values['issue_date']:
            raise ValueError('过期日期必须晚于签发日期')
        return v

class ComplianceCheckResult(BaseModel):
    """合规检查结果模型"""
    merchant_id: str = Field(..., description="商户ID")
    check_id: str = Field(..., description="检查ID")
    check_date: datetime = Field(..., description="检查日期")
    time_range: TimeRange = Field(..., description="数据时间范围")
    overall_status: ComplianceStatus = Field(..., description="整体合规状态")
    type_status: Dict[ComplianceType, ComplianceStatus] = Field(..., description="各类型合规状态")
    violations: List[ComplianceViolation] = Field(default_factory=list, description="违规列表")
    risk_score: float = Field(..., description="风险评分", ge=0, le=100)
    documents_status: Dict[DocumentType, str] = Field(..., description="文档状态")
    next_check_date: datetime = Field(..., description="下次检查日期")
    
    @property
    def has_critical_violations(self) -> bool:
        """是否存在严重违规"""
        return any(v.risk_level == RiskLevel.CRITICAL for v in self.violations)

class ComplianceCheckRequest(BaseModel):
    """合规检查请求模型"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    check_types: Optional[List[ComplianceType]] = Field(None, description="检查类型列表，为空则检查所有类型")
    include_documents: bool = Field(True, description="是否包含文档状态")
    detailed: bool = Field(True, description="是否返回详细结果")

class ComplianceCheckResponse(BaseModel):
    """合规检查响应模型"""
    request_id: str = Field(..., description="请求ID")
    result: ComplianceCheckResult = Field(..., description="检查结果")
    status: str = Field("success", description="状态")
    error: Optional[str] = Field(None, description="错误信息") 
"""合规检查服务数据模型"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

class ComplianceRule(BaseModel):
    """合规规则"""
    rule_id: str
    category: str  # 规则类别：财务/经营/安全/许可证等
    name: str
    description: str
    severity: str  # 严重程度：高/中/低
    check_method: str  # 检查方法：阈值/模式匹配/时间序列等
    parameters: Dict[str, any]  # 规则参数

class ComplianceViolation(BaseModel):
    """合规违规"""
    rule_id: str
    timestamp: datetime
    severity: str
    description: str
    evidence: Dict[str, any]  # 违规证据
    suggested_actions: List[str]  # 建议措施

class ComplianceMetrics(BaseModel):
    """合规指标"""
    total_checks: int  # 检查总数
    passed_checks: int  # 通过检查数
    violation_count: int  # 违规数量
    high_risk_count: int  # 高风险违规数
    compliance_score: float  # 合规得分(0-100)
    trend: float  # 环比变化

class ComplianceReport(BaseModel):
    """合规报告"""
    merchant_id: str
    report_period: str
    metrics: ComplianceMetrics
    violations: List[ComplianceViolation]
    risk_assessment: str  # 风险评估：高/中/低
    improvement_suggestions: List[str]
    next_review_date: datetime

class ComplianceAlert(BaseModel):
    """合规预警"""
    alert_id: str
    merchant_id: str
    timestamp: datetime
    severity: str
    title: str
    description: str
    affected_rules: List[str]
    required_actions: List[str]
    deadline: Optional[datetime]

class ComplianceRequirement(BaseModel):
    """合规要求"""
    category: str
    name: str
    description: str
    required_documents: List[str]
    renewal_period: Optional[int]  # 更新周期(天)
    validation_rules: List[Dict[str, any]]

class ComplianceStatus(BaseModel):
    """合规状态"""
    requirement_id: str
    status: str  # 合规/待整改/违规
    last_check_date: datetime
    expiration_date: Optional[datetime]
    documents: List[Dict[str, str]]  # 文档列表
    notes: Optional[str] 
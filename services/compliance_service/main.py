"""
合规检查服务入口
"""
from typing import List, Optional
from datetime import datetime

from shared.service import BaseService
from shared.models import BaseResponse, ErrorResponse
from core.models import (
    MerchantInfo,
    RuleDefinition,
    CheckResult,
    ComplianceReport
)
from core.rule_engine import RuleEngine
from core.checker import ComplianceChecker

# 创建服务实例
service = BaseService(
    app_name="合规检查服务",
    description="提供商户经营合规性检查功能",
    version="1.0.0"
)

app = service.app

# 初始化规则引擎和检查器
rule_engine = RuleEngine()
checker = ComplianceChecker(rule_engine)

# 注册示例规则
@app.on_event("startup")
async def startup_event():
    """服务启动时注册默认规则"""
    default_rules = [
        RuleDefinition(
            rule_id="REG_CAPITAL_001",
            rule_name="最低注册资本",
            rule_type="financial",
            rule_description="检查注册资本是否满足最低要求",
            check_method="check_registered_capital",
            parameters={"min_capital": 100000},
            severity="high"
        ),
        RuleDefinition(
            rule_id="BIZ_SCOPE_001",
            rule_name="经营范围要求",
            rule_type="qualification",
            rule_description="检查经营范围是否包含必需项",
            check_method="check_business_scope",
            parameters={"required_items": ["零售", "批发"]},
            severity="medium"
        ),
        RuleDefinition(
            rule_id="EST_PERIOD_001",
            rule_name="最短成立年限",
            rule_type="risk",
            rule_description="检查企业成立时间是否满足最短要求",
            check_method="check_establishment_period",
            parameters={"min_years": 2},
            severity="low"
        )
    ]
    
    for rule in default_rules:
        rule_engine.register_rule(rule)

@app.post("/api/v1/compliance/check", response_model=BaseResponse)
async def check_merchant_compliance(
    merchant: MerchantInfo,
    rule_types: Optional[List[str]] = None
):
    """
    执行商户合规检查
    
    Args:
        merchant (MerchantInfo): 商户信息
        rule_types (Optional[List[str]], optional): 规则类型过滤
        
    Returns:
        BaseResponse: 包含合规检查报告的响应
    """
    try:
        report = checker.check_merchant(merchant, rule_types)
        return BaseResponse(
            code=200,
            message="合规检查完成",
            data=report.dict()
        )
    except Exception as e:
        return ErrorResponse(
            code=500,
            message="合规检查失败",
            details={"error": str(e)}
        )

@app.get("/api/v1/compliance/rules", response_model=BaseResponse)
async def list_compliance_rules(rule_type: Optional[str] = None):
    """
    获取所有合规检查规则
    
    Args:
        rule_type (Optional[str], optional): 规则类型过滤
        
    Returns:
        BaseResponse: 包含规则列表的响应
    """
    rules = rule_engine.list_rules(rule_type)
    return BaseResponse(
        code=200,
        message="获取规则列表成功",
        data=[rule.dict() for rule in rules]
    )

@app.post("/api/v1/compliance/rules", response_model=BaseResponse)
async def create_compliance_rule(rule: RuleDefinition):
    """
    创建新的合规检查规则
    
    Args:
        rule (RuleDefinition): 规则定义
        
    Returns:
        BaseResponse: 包含创建的规则的响应
    """
    try:
        rule_engine.register_rule(rule)
        return BaseResponse(
            code=200,
            message="创建规则成功",
            data=rule.dict()
        )
    except Exception as e:
        return ErrorResponse(
            code=400,
            message="创建规则失败",
            details={"error": str(e)}
        )

@app.get("/api/v1/compliance/rules/{rule_id}", response_model=BaseResponse)
async def get_compliance_rule(rule_id: str):
    """
    获取指定规则详情
    
    Args:
        rule_id (str): 规则ID
        
    Returns:
        BaseResponse: 包含规则详情的响应
    """
    rule = rule_engine.get_rule(rule_id)
    if not rule:
        return ErrorResponse(
            code=404,
            message="规则不存在",
            details={"rule_id": rule_id}
        )
    return BaseResponse(
        code=200,
        message="获取规则详情成功",
        data=rule.dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
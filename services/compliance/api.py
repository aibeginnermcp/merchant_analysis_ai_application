"""
合规检查服务API

提供以下接口：
- 执行合规检查
- 获取检查历史
- 获取规则列表
- 更新规则状态
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.shared.models import (
    BaseResponse,
    PaginatedResponse,
    QueryParams,
    ErrorResponse
)
from .service import ComplianceService, ComplianceRule

router = APIRouter(prefix="/api/v1/compliance", tags=["compliance"])

class CheckComplianceRequest(BaseModel):
    """合规检查请求"""
    merchant_id: str
    categories: Optional[List[str]] = None

class CheckComplianceResponse(BaseResponse):
    """合规检查响应"""
    data: dict

class RuleListResponse(BaseResponse):
    """规则列表响应"""
    data: List[ComplianceRule]

class UpdateRuleRequest(BaseModel):
    """更新规则请求"""
    enabled: bool

@router.post(
    "/check",
    response_model=CheckComplianceResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def check_compliance(
    request: CheckComplianceRequest,
    service: ComplianceService = Depends()
) -> CheckComplianceResponse:
    """
    执行商户合规检查
    
    Args:
        request: 检查请求参数
        service: 合规检查服务实例
    
    Returns:
        CheckComplianceResponse: 检查结果
    """
    try:
        result = await service.check_merchant_compliance(
            request.merchant_id,
            request.categories
        )
        return CheckComplianceResponse(data=result)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"执行合规检查时出错: {str(e)}"
        )

@router.get(
    "/history/{merchant_id}",
    response_model=PaginatedResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_compliance_history(
    merchant_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    service: ComplianceService = Depends()
) -> PaginatedResponse:
    """
    获取商户合规检查历史
    
    Args:
        merchant_id: 商户ID
        page: 页码
        page_size: 每页数量
        service: 合规检查服务实例
    
    Returns:
        PaginatedResponse: 分页的检查历史记录
    """
    try:
        query_params = QueryParams(
            pagination={
                "page": page,
                "page_size": page_size
            }
        )
        result = await service.get_compliance_history(merchant_id, query_params)
        return PaginatedResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取合规检查历史时出错: {str(e)}"
        )

@router.get(
    "/rules",
    response_model=RuleListResponse,
    responses={
        500: {"model": ErrorResponse}
    }
)
async def get_rules(
    category: Optional[str] = None,
    service: ComplianceService = Depends()
) -> RuleListResponse:
    """
    获取合规检查规则列表
    
    Args:
        category: 规则类别
        service: 合规检查服务实例
    
    Returns:
        RuleListResponse: 规则列表
    """
    try:
        rules = list(service.rules.values())
        if category:
            rules = [rule for rule in rules if rule.category == category]
        return RuleListResponse(data=rules)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取规则列表时出错: {str(e)}"
        )

@router.patch(
    "/rules/{rule_id}",
    response_model=BaseResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def update_rule(
    rule_id: str,
    request: UpdateRuleRequest,
    service: ComplianceService = Depends()
) -> BaseResponse:
    """
    更新规则状态
    
    Args:
        rule_id: 规则ID
        request: 更新请求
        service: 合规检查服务实例
    
    Returns:
        BaseResponse: 更新结果
    """
    try:
        if rule_id not in service.rules:
            raise HTTPException(
                status_code=404,
                detail=f"规则不存在: {rule_id}"
            )
        
        service.rules[rule_id].enabled = request.enabled
        return BaseResponse(
            message=f"规则 {rule_id} 已{'启用' if request.enabled else '禁用'}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新规则状态时出错: {str(e)}"
        ) 
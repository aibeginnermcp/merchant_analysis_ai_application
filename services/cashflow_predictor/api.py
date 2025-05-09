"""
现金流预测API模块

提供现金流预测相关的HTTP API接口，包括：
- 现金流预测
- 模式分析
- 场景模拟
- 风险评估
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .service import CashflowPredictor, CashflowPrediction

router = APIRouter(
    prefix="/api/v1/cashflow",
    tags=["cashflow"],
    responses={
        404: {"description": "未找到请求的资源"},
        500: {"description": "服务器内部错误"}
    }
)

class PredictionRequest(BaseModel):
    """
    预测请求模型
    
    Attributes:
        merchant_id (str): 商户ID
        start_date (datetime): 预测开始日期
        end_date (datetime): 预测结束日期
        granularity (str): 预测粒度
    """
    merchant_id: str = Field(..., description="商户ID")
    start_date: datetime = Field(..., description="预测开始日期")
    end_date: datetime = Field(..., description="预测结束日期")
    granularity: str = Field(
        "daily",
        description="预测粒度",
        enum=["daily", "weekly", "monthly"]
    )

    class Config:
        schema_extra = {
            "example": {
                "merchant_id": "MERCHANT_001",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "granularity": "daily"
            }
        }

class ScenarioConfig(BaseModel):
    """
    场景配置模型
    
    Attributes:
        name (str): 场景名称
        description (str): 场景描述
        changes (List[Dict]): 变化配置
    """
    name: str = Field(..., description="场景名称")
    description: str = Field(..., description="场景描述")
    changes: List[Dict] = Field(..., description="变化配置")

    class Config:
        schema_extra = {
            "example": {
                "name": "收入增长",
                "description": "模拟收入增长10%的情况",
                "changes": [
                    {
                        "type": "inflow",
                        "category": "sales",
                        "change_type": "percentage",
                        "value": 10
                    }
                ]
            }
        }

@router.post(
    "/predict",
    response_model=CashflowPrediction,
    summary="预测现金流",
    description="""
    对指定商户在给定时间范围内的现金流进行预测。
    
    预测内容包括：
    - 现金流入预测
    - 现金流出预测
    - 净现金流预测
    - 置信区间
    - 风险评估
    - 预警信息
    """
)
async def predict_cashflow(request: PredictionRequest):
    """
    预测现金流
    
    Args:
        request: 预测请求参数
        
    Returns:
        预测结果
    """
    try:
        predictor = CashflowPredictor()
        prediction = await predictor.predict_cashflow(
            request.merchant_id,
            request.start_date,
            request.end_date,
            request.granularity
        )
        return prediction
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"现金流预测失败: {str(e)}"
        )

@router.get(
    "/pattern/{merchant_id}",
    summary="分析现金流模式",
    description="""
    分析指定商户的现金流模式。
    
    分析内容包括：
    - 周期性模式
    - 季节性特征
    - 趋势特征
    - 异常模式
    """
)
async def analyze_pattern(
    merchant_id: str = Query(..., description="商户ID"),
    lookback_days: int = Query(365, description="回溯天数")
):
    """
    分析现金流模式
    
    Args:
        merchant_id: 商户ID
        lookback_days: 回溯天数
        
    Returns:
        模式分析结果
    """
    try:
        predictor = CashflowPredictor()
        pattern = await predictor.analyze_cashflow_pattern(
            merchant_id,
            lookback_days
        )
        return pattern
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"模式分析失败: {str(e)}"
        )

@router.post(
    "/simulate/{merchant_id}",
    summary="模拟现金流场景",
    description="""
    模拟不同场景下的现金流变化。
    
    支持的场景类型：
    - 收入变化
    - 支出变化
    - 时间变化
    - 概率变化
    
    返回每个场景的模拟结果。
    """
)
async def simulate_scenarios(
    merchant_id: str = Query(..., description="商户ID"),
    scenarios: List[ScenarioConfig] = Body(
        ...,
        description="场景配置列表"
    )
):
    """
    模拟现金流场景
    
    Args:
        merchant_id: 商户ID
        scenarios: 场景配置列表
        
    Returns:
        场景模拟结果
    """
    try:
        predictor = CashflowPredictor()
        results = await predictor.simulate_scenarios(
            merchant_id,
            [scenario.dict() for scenario in scenarios]
        )
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"场景模拟失败: {str(e)}"
        ) 
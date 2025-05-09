"""
成本穿透分析API模块

提供成本分析相关的HTTP API接口,包括:
- 成本分析请求处理
- 成本指标查询
- 成本预警和优化建议

Classes:
    TimeRange: 时间范围模型
    CostAnalysisRequest: 成本分析请求模型
    CostStructureResponse: 成本结构分析响应模型
    CostTrendResponse: 成本趋势分析响应模型
    CostAlertResponse: 成本预警分析响应模型
    CostOptimizationResponse: 成本优化建议响应模型
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .analyzers.cost_analyzer import CostAnalyzer
from .data_processor import DataProcessor
from .rule_engine import RuleEngine
from .visualizer import CostVisualizer

router = APIRouter(
    prefix="/api/v1/cost-analysis",
    tags=["cost-analysis"],
    responses={
        404: {"description": "未找到请求的资源"},
        500: {"description": "服务器内部错误"}
    }
)

class TimeRange(BaseModel):
    """
    时间范围模型
    
    Attributes:
        start_date (datetime): 分析开始日期
        end_date (datetime): 分析结束日期
    """
    start_date: datetime = Field(..., description="分析开始日期")
    end_date: datetime = Field(..., description="分析结束日期")

    class Config:
        schema_extra = {
            "example": {
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59"
            }
        }

class CostAnalysisRequest(BaseModel):
    """
    成本分析请求模型
    
    Attributes:
        merchant_id (str): 商户ID
        time_range (TimeRange): 分析时间范围
        analysis_types (List[str]): 分析类型列表
        granularity (Optional[str]): 数据粒度
    """
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="分析时间范围")
    analysis_types: List[str] = Field(
        ...,
        description="分析类型列表",
        example=["structure", "trend", "alert", "optimization"]
    )
    granularity: Optional[str] = Field(
        "monthly",
        description="数据粒度",
        example="monthly",
        enum=["daily", "weekly", "monthly", "quarterly", "yearly"]
    )

    class Config:
        schema_extra = {
            "example": {
                "merchant_id": "MERCHANT_001",
                "time_range": {
                    "start_date": "2024-01-01T00:00:00",
                    "end_date": "2024-12-31T23:59:59"
                },
                "analysis_types": ["structure", "trend"],
                "granularity": "monthly"
            }
        }

class CostStructureResponse(BaseModel):
    """
    成本结构分析响应模型
    
    Attributes:
        total_cost (float): 总成本
        cost_breakdown (dict): 成本构成明细
        major_cost_factors (List[dict]): 主要成本因素
        cost_ratios (dict): 成本占比
    """
    total_cost: float
    cost_breakdown: dict
    major_cost_factors: List[dict]
    cost_ratios: dict

class CostTrendResponse(BaseModel):
    """
    成本趋势分析响应模型
    
    Attributes:
        trend_data (List[dict]): 趋势数据
        seasonal_patterns (Optional[dict]): 季节性模式
        year_over_year (Optional[dict]): 同比数据
    """
    trend_data: List[dict]
    seasonal_patterns: Optional[dict]
    year_over_year: Optional[dict]

class CostAlertResponse(BaseModel):
    """
    成本预警分析响应模型
    
    Attributes:
        alerts (List[dict]): 预警信息列表
        risk_level (str): 风险等级
        recommendations (List[str]): 改进建议
    """
    alerts: List[dict]
    risk_level: str
    recommendations: List[str]

class CostOptimizationResponse(BaseModel):
    """
    成本优化建议响应模型
    
    Attributes:
        potential_savings (float): 潜在节省金额
        optimization_suggestions (List[dict]): 优化建议列表
        implementation_priority (List[dict]): 实施优先级
    """
    potential_savings: float
    optimization_suggestions: List[dict]
    implementation_priority: List[dict]

@router.post(
    "/analyze",
    response_model=dict,
    summary="执行成本分析",
    description="""
    对指定商户在给定时间范围内的成本数据进行全面分析。
    
    可选的分析类型包括：
    - structure: 成本结构分析
    - trend: 成本趋势分析
    - alert: 成本预警分析
    - optimization: 成本优化建议
    
    分析结果将包含所选分析类型的详细数据和可视化结果。
    """
)
async def analyze_cost(request: CostAnalysisRequest):
    """
    执行成本分析
    
    Args:
        request (CostAnalysisRequest): 包含商户ID、时间范围和分析类型的请求
        
    Returns:
        dict: 包含各类分析结果的字典
        
    Raises:
        HTTPException: 当分析过程发生错误时抛出
    """
    try:
        # 初始化分析组件
        data_processor = DataProcessor()
        cost_analyzer = CostAnalyzer()
        rule_engine = RuleEngine()
        visualizer = CostVisualizer()
        
        # 获取数据
        raw_data = await data_processor.get_merchant_data(
            request.merchant_id,
            request.time_range.start_date,
            request.time_range.end_date
        )
        
        results = {}
        
        # 根据请求的分析类型执行相应分析
        if "structure" in request.analysis_types:
            structure_analysis = cost_analyzer.analyze_structure(raw_data)
            results["structure"] = CostStructureResponse(**structure_analysis)
            
        if "trend" in request.analysis_types:
            trend_analysis = cost_analyzer.analyze_trend(
                raw_data,
                granularity=request.granularity
            )
            results["trend"] = CostTrendResponse(**trend_analysis)
            
        if "alert" in request.analysis_types:
            alert_analysis = rule_engine.check_cost_alerts(raw_data)
            results["alerts"] = CostAlertResponse(**alert_analysis)
            
        if "optimization" in request.analysis_types:
            optimization_analysis = cost_analyzer.get_optimization_suggestions(raw_data)
            results["optimization"] = CostOptimizationResponse(**optimization_analysis)
            
        # 生成可视化数据
        if results:
            visualization_data = visualizer.generate_visualizations(results)
            results["visualizations"] = visualization_data
            
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"成本分析过程中发生错误: {str(e)}"
        )

@router.get(
    "/metrics/{merchant_id}",
    summary="获取成本指标",
    description="""
    获取指定商户在给定时间范围内的关键成本指标。
    
    返回的指标包括：
    - 总成本
    - 固定成本比例
    - 变动成本比例
    - 各类成本占比
    - 成本增长率
    - 成本效率指标
    """
)
async def get_cost_metrics(
    merchant_id: str = Query(..., description="商户ID"),
    start_date: datetime = Query(..., description="开始日期"),
    end_date: datetime = Query(..., description="结束日期")
):
    """
    获取商户的关键成本指标
    
    Args:
        merchant_id: 商户ID
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        包含各项成本指标的字典
    """
    try:
        data_processor = DataProcessor()
        cost_analyzer = CostAnalyzer()
        
        raw_data = await data_processor.get_merchant_data(
            merchant_id,
            start_date,
            end_date
        )
        
        metrics = cost_analyzer.calculate_metrics(raw_data)
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取成本指标时发生错误: {str(e)}"
        )

@router.post(
    "/simulate",
    summary="模拟成本变化",
    description="""
    模拟不同成本变化场景对商户经营的影响。
    
    支持的场景类型：
    - 成本增加/减少
    - 成本结构调整
    - 固定/变动成本转换
    
    返回模拟后的各项指标变化。
    """
)
async def simulate_cost_changes(
    merchant_id: str = Query(..., description="商户ID"),
    scenarios: List[dict] = Body(
        ...,
        description="成本变化场景列表",
        example=[
            {
                "category": "人工成本",
                "change_type": "increase",
                "percentage": 10
            }
        ]
    )
):
    """
    模拟成本变化场景
    
    Args:
        merchant_id: 商户ID
        scenarios: 成本变化场景列表
        
    Returns:
        模拟分析结果
    """
    try:
        cost_analyzer = CostAnalyzer()
        simulation_results = cost_analyzer.simulate_scenarios(merchant_id, scenarios)
        return simulation_results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"成本模拟分析时发生错误: {str(e)}"
        )
""" 
"""成本分析服务数据模型"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

class CostBreakdown(BaseModel):
    """成本明细"""
    category: str
    amount: float
    percentage: float
    trend: float  # 环比变化率
    
class CostMetrics(BaseModel):
    """成本指标"""
    total_cost: float
    cost_revenue_ratio: float  # 成本收入比
    gross_margin: float  # 毛利率
    operating_margin: float  # 营业利润率
    
class CostAnalysisResult(BaseModel):
    """成本分析结果"""
    merchant_id: str
    analysis_period: str
    total_metrics: CostMetrics
    cost_breakdown: List[CostBreakdown]
    monthly_trends: Dict[str, CostMetrics]
    optimization_suggestions: List[str]
    risk_factors: List[Dict[str, str]]
    
class CostOptimizationPlan(BaseModel):
    """成本优化方案"""
    category: str
    current_cost: float
    target_cost: float
    potential_savings: float
    implementation_difficulty: str  # 容易/中等/困难
    roi_period: int  # 预计回报周期(月)
    action_items: List[str] 
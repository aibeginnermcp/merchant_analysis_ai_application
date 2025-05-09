"""成本分析器模块"""
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime
from .models import (
    CostBreakdown,
    CostMetrics,
    CostAnalysisResult,
    CostOptimizationPlan
)

class CostAnalyzer:
    """成本分析器"""
    
    def __init__(self):
        """初始化成本分析器"""
        self.cost_categories = [
            "原材料",
            "人工",
            "水电",
            "租金",
            "其他"
        ]
        
        # 行业标准成本比例
        self.industry_benchmarks = {
            "restaurant": {
                "原材料": 0.35,
                "人工": 0.25,
                "水电": 0.08,
                "租金": 0.15,
                "其他": 0.07
            },
            "retail": {
                "原材料": 0.60,
                "人工": 0.15,
                "水电": 0.05,
                "租金": 0.12,
                "其他": 0.08
            }
        }
        
    def analyze_costs(
        self,
        merchant_id: str,
        merchant_type: str,
        historical_data: Dict[str, Any]
    ) -> CostAnalysisResult:
        """分析成本结构"""
        # 计算基础指标
        total_metrics = self._calculate_total_metrics(historical_data)
        
        # 分析成本构成
        cost_breakdown = self._analyze_cost_breakdown(
            historical_data,
            self.industry_benchmarks.get(merchant_type, {})
        )
        
        # 分析月度趋势
        monthly_trends = self._analyze_monthly_trends(historical_data)
        
        # 生成优化建议
        optimization_suggestions = self._generate_optimization_suggestions(
            cost_breakdown,
            total_metrics,
            merchant_type
        )
        
        # 识别风险因素
        risk_factors = self._identify_risk_factors(
            cost_breakdown,
            total_metrics,
            monthly_trends
        )
        
        return CostAnalysisResult(
            merchant_id=merchant_id,
            analysis_period=f"{historical_data['start_date']} to {historical_data['end_date']}",
            total_metrics=total_metrics,
            cost_breakdown=cost_breakdown,
            monthly_trends=monthly_trends,
            optimization_suggestions=optimization_suggestions,
            risk_factors=risk_factors
        )
        
    def _calculate_total_metrics(self, data: Dict[str, Any]) -> CostMetrics:
        """计算总体成本指标"""
        total_revenue = sum(t["revenue"] for t in data["transactions"])
        total_cost = sum(
            sum(c.values()) for c in data["costs"]
        )
        
        return CostMetrics(
            total_cost=total_cost,
            cost_revenue_ratio=total_cost / total_revenue if total_revenue > 0 else 0,
            gross_margin=(total_revenue - total_cost) / total_revenue if total_revenue > 0 else 0,
            operating_margin=(total_revenue - total_cost * 1.1) / total_revenue if total_revenue > 0 else 0
        )
        
    def _analyze_cost_breakdown(
        self,
        data: Dict[str, Any],
        benchmarks: Dict[str, float]
    ) -> List[CostBreakdown]:
        """分析成本构成"""
        breakdowns = []
        total_cost = sum(sum(c.values()) for c in data["costs"])
        
        for category in self.cost_categories:
            category_costs = [c.get(f"{category.lower()}_cost", 0) for c in data["costs"]]
            amount = sum(category_costs)
            percentage = amount / total_cost if total_cost > 0 else 0
            
            # 计算趋势（环比变化率）
            if len(category_costs) > 1:
                trend = (category_costs[-1] - category_costs[-2]) / category_costs[-2] if category_costs[-2] > 0 else 0
            else:
                trend = 0
                
            breakdowns.append(
                CostBreakdown(
                    category=category,
                    amount=amount,
                    percentage=percentage,
                    trend=trend
                )
            )
            
        return breakdowns
        
    def _analyze_monthly_trends(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, CostMetrics]:
        """分析月度趋势"""
        monthly_data = {}
        
        for i, transaction in enumerate(data["transactions"]):
            date = datetime.fromisoformat(transaction["date"])
            month_key = date.strftime("%Y-%m")
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "revenue": 0,
                    "costs": 0
                }
                
            monthly_data[month_key]["revenue"] += transaction["revenue"]
            monthly_data[month_key]["costs"] += sum(data["costs"][i].values())
            
        monthly_trends = {}
        for month, values in monthly_data.items():
            revenue = values["revenue"]
            cost = values["costs"]
            
            monthly_trends[month] = CostMetrics(
                total_cost=cost,
                cost_revenue_ratio=cost / revenue if revenue > 0 else 0,
                gross_margin=(revenue - cost) / revenue if revenue > 0 else 0,
                operating_margin=(revenue - cost * 1.1) / revenue if revenue > 0 else 0
            )
            
        return monthly_trends
        
    def _generate_optimization_suggestions(
        self,
        cost_breakdown: List[CostBreakdown],
        metrics: CostMetrics,
        merchant_type: str
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []
        benchmarks = self.industry_benchmarks.get(merchant_type, {})
        
        # 分析成本结构偏差
        for item in cost_breakdown:
            benchmark = benchmarks.get(item.category, 0)
            if item.percentage > benchmark * 1.2:  # 超出行业标准20%
                suggestions.append(
                    f"{item.category}成本占比{item.percentage:.1%}，高于行业标准{benchmark:.1%}，"
                    f"建议优化{item.category}成本结构"
                )
                
        # 分析整体指标
        if metrics.cost_revenue_ratio > 0.8:
            suggestions.append(
                "成本收入比过高，建议全面审查成本结构，"
                "识别并消除无效支出"
            )
            
        if metrics.gross_margin < 0.2:
            suggestions.append(
                "毛利率偏低，建议：\n"
                "1. 考虑提高产品定价\n"
                "2. 寻找更具竞争力的供应商\n"
                "3. 优化产品结构，提高高毛利产品占比"
            )
            
        return suggestions
        
    def _identify_risk_factors(
        self,
        cost_breakdown: List[CostBreakdown],
        metrics: CostMetrics,
        monthly_trends: Dict[str, CostMetrics]
    ) -> List[Dict[str, str]]:
        """识别风险因素"""
        risk_factors = []
        
        # 分析成本趋势
        for item in cost_breakdown:
            if item.trend > 0.1:  # 环比增长超过10%
                risk_factors.append({
                    "category": "成本趋势",
                    "description": f"{item.category}成本环比增长{item.trend:.1%}，需要关注"
                })
                
        # 分析利润趋势
        trend_values = list(monthly_trends.values())
        if len(trend_values) >= 2:
            latest_margin = trend_values[-1].operating_margin
            prev_margin = trend_values[-2].operating_margin
            if latest_margin < prev_margin:
                risk_factors.append({
                    "category": "利润趋势",
                    "description": "营业利润率呈下降趋势，需要采取措施提升盈利能力"
                })
                
        # 分析现金流风险
        if metrics.cost_revenue_ratio > 0.9:
            risk_factors.append({
                "category": "现金流风险",
                "description": "成本收入比过高，可能面临现金流压力"
            })
            
        return risk_factors
        
    def generate_optimization_plan(
        self,
        cost_breakdown: List[CostBreakdown],
        merchant_type: str
    ) -> List[CostOptimizationPlan]:
        """生成成本优化方案"""
        plans = []
        benchmarks = self.industry_benchmarks.get(merchant_type, {})
        
        for item in cost_breakdown:
            benchmark = benchmarks.get(item.category, 0)
            if item.percentage > benchmark * 1.1:  # 超出行业标准10%
                target_cost = item.amount * (benchmark / item.percentage)
                potential_savings = item.amount - target_cost
                
                plan = CostOptimizationPlan(
                    category=item.category,
                    current_cost=item.amount,
                    target_cost=target_cost,
                    potential_savings=potential_savings,
                    implementation_difficulty=self._assess_difficulty(item.category),
                    roi_period=self._estimate_roi_period(item.category),
                    action_items=self._generate_action_items(item.category)
                )
                plans.append(plan)
                
        return plans
        
    def _assess_difficulty(self, category: str) -> str:
        """评估实施难度"""
        difficulty_map = {
            "原材料": "中等",
            "人工": "困难",
            "水电": "容易",
            "租金": "困难",
            "其他": "中等"
        }
        return difficulty_map.get(category, "中等")
        
    def _estimate_roi_period(self, category: str) -> int:
        """估计投资回报周期（月）"""
        roi_map = {
            "原材料": 3,
            "人工": 6,
            "水电": 2,
            "租金": 12,
            "其他": 4
        }
        return roi_map.get(category, 6)
        
    def _generate_action_items(self, category: str) -> List[str]:
        """生成行动建议"""
        action_items_map = {
            "原材料": [
                "建立供应商评估体系",
                "实施批量采购策略",
                "优化库存管理流程"
            ],
            "人工": [
                "优化人员配置",
                "提升人效",
                "考虑引入自动化设备"
            ],
            "水电": [
                "安装节能设备",
                "优化用能时段",
                "加强员工节能意识"
            ],
            "租金": [
                "评估店面使用效率",
                "考虑调整经营面积",
                "寻找性价比更高的位置"
            ],
            "其他": [
                "细化其他成本项目",
                "建立成本追踪机制",
                "定期评估费用必要性"
            ]
        }
        return action_items_map.get(category, []) 
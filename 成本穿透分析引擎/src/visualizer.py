"""
可视化组件模块

负责生成各类成本分析图表，包括：
- 成本结构图
- 趋势分析图
- 预警指标图
- 优化建议图
"""

from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json

class CostVisualizer:
    """
    成本可视化器
    
    生成各类成本分析图表
    """
    
    def __init__(self):
        """初始化可视化器"""
        self.color_palette = px.colors.qualitative.Set3
        self.template = "plotly_white"
        
    def generate_visualizations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成可视化图表
        
        Args:
            results: 分析结果数据
            
        Returns:
            包含各类图表的字典
        """
        visualizations = {}
        
        # 生成成本结构图表
        if "structure" in results:
            visualizations["structure"] = self._create_structure_charts(
                results["structure"]
            )
            
        # 生成趋势分析图表
        if "trend" in results:
            visualizations["trend"] = self._create_trend_charts(
                results["trend"]
            )
            
        # 生成预警指标图表
        if "alerts" in results:
            visualizations["alerts"] = self._create_alert_charts(
                results["alerts"]
            )
            
        # 生成优化建议图表
        if "optimization" in results:
            visualizations["optimization"] = self._create_optimization_charts(
                results["optimization"]
            )
            
        return visualizations
        
    def _create_structure_charts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建成本结构图表"""
        charts = {}
        
        # 成本构成饼图
        pie = go.Figure(
            data=[
                go.Pie(
                    labels=list(data["cost_ratios"].keys()),
                    values=[
                        ratio["percentage"]
                        for ratio in data["cost_ratios"].values()
                    ],
                    hole=0.3
                )
            ]
        )
        pie.update_layout(
            title="成本构成占比",
            template=self.template
        )
        charts["cost_composition"] = json.loads(pie.to_json())
        
        # 主要成本因素条形图
        bar = go.Figure(
            data=[
                go.Bar(
                    x=[factor["category"] for factor in data["major_cost_factors"]],
                    y=[factor["amount"] for factor in data["major_cost_factors"]],
                    text=[
                        f"{factor['percentage']:.1f}%"
                        for factor in data["major_cost_factors"]
                    ],
                    textposition="auto"
                )
            ]
        )
        bar.update_layout(
            title="主要成本因素",
            xaxis_title="成本类别",
            yaxis_title="金额",
            template=self.template
        )
        charts["major_factors"] = json.loads(bar.to_json())
        
        return charts
        
    def _create_trend_charts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建趋势分析图表"""
        charts = {}
        
        # 转换数据为DataFrame
        df = pd.DataFrame(data["trend_data"])
        
        # 成本趋势线图
        line = go.Figure()
        for category in df["cost_category"].unique():
            category_data = df[df["cost_category"] == category]
            line.add_trace(
                go.Scatter(
                    x=category_data["period"],
                    y=category_data["amount"],
                    name=category,
                    mode="lines+markers"
                )
            )
        line.update_layout(
            title="成本趋势分析",
            xaxis_title="时间",
            yaxis_title="金额",
            template=self.template
        )
        charts["cost_trend"] = json.loads(line.to_json())
        
        # 季节性模式图表
        if data["seasonal_patterns"]:
            seasonal = go.Figure()
            # TODO: 添加季节性图表
            charts["seasonality"] = json.loads(seasonal.to_json())
            
        # 同比分析图表
        if data["year_over_year"]:
            yoy = go.Figure()
            # TODO: 添加同比分析图表
            charts["year_over_year"] = json.loads(yoy.to_json())
            
        return charts
        
    def _create_alert_charts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建预警指标图表"""
        charts = {}
        
        # 预警指标仪表盘
        alerts_df = pd.DataFrame(data["alerts"])
        if not alerts_df.empty:
            gauge = make_subplots(
                rows=len(alerts_df),
                cols=1,
                specs=[[{"type": "indicator"}] for _ in range(len(alerts_df))]
            )
            
            for i, alert in alerts_df.iterrows():
                gauge.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=alert["triggered_value"],
                        title={
                            "text": alert["name"],
                            "font": {"size": 14}
                        },
                        gauge={
                            "axis": {"range": [0, 1]},
                            "bar": {"color": self._get_risk_color(alert["risk_level"])}
                        }
                    ),
                    row=i+1,
                    col=1
                )
                
            gauge.update_layout(
                height=200 * len(alerts_df),
                title="预警指标监控",
                template=self.template
            )
            charts["alert_gauges"] = json.loads(gauge.to_json())
            
        return charts
        
    def _create_optimization_charts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建优化建议图表"""
        charts = {}
        
        # 潜在节省金额瀑布图
        suggestions_df = pd.DataFrame(data["optimization_suggestions"])
        if not suggestions_df.empty:
            waterfall = go.Figure(
                go.Waterfall(
                    name="优化空间",
                    orientation="v",
                    measure=["relative"] * len(suggestions_df),
                    x=suggestions_df["category"],
                    y=suggestions_df["estimated_savings"],
                    connector={"line": {"color": "rgb(63, 63, 63)"}},
                    text=suggestions_df["estimated_savings"].apply(
                        lambda x: f"{x:,.0f}"
                    ),
                    textposition="outside"
                )
            )
            waterfall.update_layout(
                title="成本优化空间分析",
                xaxis_title="优化项目",
                yaxis_title="预计节省金额",
                template=self.template,
                showlegend=False
            )
            charts["optimization_waterfall"] = json.loads(waterfall.to_json())
            
        # 实施优先级矩阵图
        if data["implementation_priority"]:
            priority_df = pd.DataFrame(data["implementation_priority"])
            scatter = go.Figure(
                data=go.Scatter(
                    x=priority_df["effort"],
                    y=priority_df["impact"],
                    mode="markers+text",
                    marker=dict(
                        size=priority_df["estimated_savings"] / 1000,
                        sizemode="area",
                        sizeref=2. * max(priority_df["estimated_savings"]) / (40.**2),
                        sizemin=4
                    ),
                    text=priority_df["category"],
                    textposition="top center"
                )
            )
            scatter.update_layout(
                title="优化项目优先级矩阵",
                xaxis_title="实施难度",
                yaxis_title="预期影响",
                template=self.template
            )
            charts["priority_matrix"] = json.loads(scatter.to_json())
            
        return charts
        
    def _get_risk_color(self, risk_level: str) -> str:
        """获取风险等级对应的颜色"""
        color_map = {
            "low": "green",
            "medium": "yellow",
            "high": "orange",
            "critical": "red"
        }
        return color_map.get(risk_level, "gray") 
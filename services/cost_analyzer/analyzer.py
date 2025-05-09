"""
成本穿透分析服务的分析引擎，实现成本拆解、趋势分析和优化建议生成
"""
import uuid
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from collections import defaultdict

from services.cost_analyzer.models import (
    TimeRange,
    CostCategory,
    CostAllocationMethod,
    CostItem,
    CostData,
    CostDriverType,
    CostDriver,
    CostBreakdownItem,
    CostBreakdown,
    CostTrendPoint,
    CostTrend,
    CostOptimizationSuggestion,
    CostAnalysis
)

logger = logging.getLogger("cost_analyzer.analyzer")

class CostBreakdownAnalyzer:
    """成本拆解分析器"""
    
    def analyze_breakdown(self, cost_data: CostData) -> CostBreakdown:
        """
        分析成本拆解
        
        Args:
            cost_data: 成本数据
            
        Returns:
            成本拆解
        """
        logger.info(f"Analyzing cost breakdown for merchant {cost_data.merchant_id}")
        
        # 按类别分组
        category_data = defaultdict(list)
        subcategory_data = defaultdict(list)
        
        for item in cost_data.items:
            category_data[item.category].append(item)
            key = (item.category, item.subcategory or "未分类")
            subcategory_data[key].append(item)
        
        # 计算每个类别的总额
        category_totals = {
            category: sum(item.amount for item in items)
            for category, items in category_data.items()
        }
        
        # 计算子类别总额
        subcategory_totals = {
            key: sum(item.amount for item in items)
            for key, items in subcategory_data.items()
        }
        
        # 计算固定成本和变动成本
        total_amount = cost_data.total_amount
        
        # 创建拆解项目列表
        breakdown_items = []
        
        # 处理类别级别的拆解
        for category, amount in category_totals.items():
            percentage = (amount / total_amount) * 100 if total_amount > 0 else 0
            
            # 计算该类别下的固定和变动成本
            items = category_data[category]
            fixed_amount = sum(item.amount * item.fixed_variable_ratio for item in items)
            variable_amount = amount - fixed_amount
            
            # 创建拆解项目
            item = CostBreakdownItem(
                category=category,
                subcategory=None,
                amount=amount,
                percentage=percentage,
                fixed_amount=fixed_amount,
                variable_amount=variable_amount,
                drivers=None  # 暂不添加驱动因素
            )
            breakdown_items.append(item)
            
            # 处理子类别拆解
            for (cat, subcat), sub_amount in subcategory_totals.items():
                if cat == category and subcat != "未分类":
                    sub_percentage = (sub_amount / total_amount) * 100 if total_amount > 0 else 0
                    
                    # 计算子类别的固定和变动成本
                    sub_items = subcategory_data[(cat, subcat)]
                    sub_fixed_amount = sum(item.amount * item.fixed_variable_ratio for item in sub_items)
                    sub_variable_amount = sub_amount - sub_fixed_amount
                    
                    # 创建子类别拆解项目
                    sub_item = CostBreakdownItem(
                        category=category,
                        subcategory=subcat,
                        amount=sub_amount,
                        percentage=sub_percentage,
                        fixed_amount=sub_fixed_amount,
                        variable_amount=sub_variable_amount,
                        drivers=None  # 暂不添加驱动因素
                    )
                    breakdown_items.append(sub_item)
        
        # 创建成本拆解结果
        breakdown = CostBreakdown(
            merchant_id=cost_data.merchant_id,
            time_range=cost_data.time_range,
            total_amount=total_amount,
            items=breakdown_items,
            created_at=datetime.now()
        )
        
        return breakdown


class CostTrendAnalyzer:
    """成本趋势分析器"""
    
    def analyze_trend(self, cost_data: CostData) -> CostTrend:
        """
        分析成本趋势
        
        Args:
            cost_data: 成本数据
            
        Returns:
            成本趋势
        """
        logger.info(f"Analyzing cost trend for merchant {cost_data.merchant_id}")
        
        # 转换为 DataFrame 进行分析
        records = []
        for item in cost_data.items:
            records.append({
                "date": item.date,
                "amount": item.amount,
                "category": item.category,
                "subcategory": item.subcategory or "未分类"
            })
        
        df = pd.DataFrame(records)
        
        # 确保日期格式正确
        df["date"] = pd.to_datetime(df["date"])
        
        # 按日期排序
        df = df.sort_values("date")
        
        # 获取日期范围
        date_range = pd.date_range(start=df["date"].min(), end=df["date"].max(), freq="D")
        
        # 按日期和类别汇总
        daily_totals = df.groupby([df["date"].dt.date])["amount"].sum().reset_index()
        category_daily = df.groupby([df["date"].dt.date, "category"])["amount"].sum().reset_index()
        
        # 创建总体趋势
        overall_trend = []
        for idx, row in daily_totals.iterrows():
            point = CostTrendPoint(
                date=row["date"].strftime("%Y-%m-%d"),
                amount=float(row["amount"]),
                category=None
            )
            overall_trend.append(point)
        
        # 创建分类趋势
        category_trends = {}
        for category in CostCategory:
            cat_df = category_daily[category_daily["category"] == category]
            points = []
            
            for idx, row in cat_df.iterrows():
                point = CostTrendPoint(
                    date=row["date"].strftime("%Y-%m-%d"),
                    amount=float(row["amount"]),
                    category=category
                )
                points.append(point)
            
            if points:
                category_trends[category] = points
        
        # 创建趋势结果
        trend = CostTrend(
            merchant_id=cost_data.merchant_id,
            time_range=cost_data.time_range,
            overall_trend=overall_trend,
            category_trends=category_trends,
            created_at=datetime.now()
        )
        
        return trend


class CostOptimizationAnalyzer:
    """成本优化分析器"""
    
    def generate_suggestions(self, cost_data: CostData, breakdown: CostBreakdown) -> List[CostOptimizationSuggestion]:
        """
        生成成本优化建议
        
        Args:
            cost_data: 成本数据
            breakdown: 成本拆解
            
        Returns:
            优化建议列表
        """
        logger.info(f"Generating cost optimization suggestions for merchant {cost_data.merchant_id}")
        
        suggestions = []
        
        # 找出最大类别的成本
        category_items = [item for item in breakdown.items if item.subcategory is None]
        category_items.sort(key=lambda x: x.amount, reverse=True)
        
        # 检查顶部三个类别，生成优化建议
        for idx, item in enumerate(category_items[:3]):
            category = item.category
            amount = item.amount
            
            # 根据不同类别生成不同的优化建议
            if category == CostCategory.DIRECT_MATERIAL:
                suggestions.append(self._create_material_suggestion(item))
                
            elif category == CostCategory.DIRECT_LABOR:
                suggestions.append(self._create_labor_suggestion(item))
                
            elif category == CostCategory.MANUFACTURING_OVERHEAD:
                suggestions.append(self._create_overhead_suggestion(item))
                
            elif category == CostCategory.SALES_MARKETING:
                suggestions.append(self._create_marketing_suggestion(item))
                
            elif category == CostCategory.ADMIN_GENERAL:
                suggestions.append(self._create_admin_suggestion(item))
                
            elif category == CostCategory.RENT:
                suggestions.append(self._create_rent_suggestion(item))
                
            elif category == CostCategory.UTILITIES:
                suggestions.append(self._create_utilities_suggestion(item))
            
            elif category == CostCategory.LOGISTICS:
                suggestions.append(self._create_logistics_suggestion(item))
                
            elif category == CostCategory.PACKAGING:
                suggestions.append(self._create_packaging_suggestion(item))
        
        # 检查固定与变动成本比例
        fixed_total = sum(item.fixed_amount for item in category_items)
        variable_total = sum(item.variable_amount for item in category_items)
        total = fixed_total + variable_total
        
        fixed_ratio = fixed_total / total if total > 0 else 0
        
        # 如果固定成本占比过高，生成额外建议
        if fixed_ratio > 0.7:
            suggestions.append(self._create_high_fixed_cost_suggestion(fixed_ratio, fixed_total))
        
        return suggestions
    
    def _create_material_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建直接材料优化建议"""
        potential_saving = item.amount * 0.1  # 假设可以节省10%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="优化采购策略，降低直接材料成本",
            description="通过批量采购、寻找替代供应商、改进供应链管理，可降低直接材料成本。建议实施集中采购，与供应商建立长期战略合作关系，获取更优惠的价格。",
            potential_saving=potential_saving,
            saving_percentage=10.0,
            difficulty=3,
            implementation_time="3-6个月",
            priority=1 if item.amount > 10000 else 2
        )
    
    def _create_labor_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建直接人工优化建议"""
        potential_saving = item.amount * 0.08  # 假设可以节省8%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="提高劳动生产率，优化人力资源配置",
            description="通过优化工作流程、技能培训和适当自动化，提高员工生产效率。分析人员配置，确保人力资源与业务需求匹配，避免人力资源浪费。",
            potential_saving=potential_saving,
            saving_percentage=8.0,
            difficulty=4,
            implementation_time="6-12个月",
            priority=1 if item.amount > 15000 else 2
        )
    
    def _create_overhead_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建制造费用优化建议"""
        potential_saving = item.amount * 0.12  # 假设可以节省12%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="减少制造费用浪费，提高设备利用率",
            description="通过预防性维护降低设备故障率，提高设备利用率。实施精益生产，减少制造过程中的浪费。考虑外包非核心生产活动，降低固定成本。",
            potential_saving=potential_saving,
            saving_percentage=12.0,
            difficulty=3,
            implementation_time="3-9个月",
            priority=1 if item.amount > 8000 else 2
        )
    
    def _create_marketing_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建销售和市场费用优化建议"""
        potential_saving = item.amount * 0.15  # 假设可以节省15%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="优化营销渠道，提高营销ROI",
            description="分析各营销渠道的投资回报率，将资源集中于高效渠道。增加数字营销比例，减少传统媒体支出。建立明确的营销效果评估体系，定期评估和调整营销策略。",
            potential_saving=potential_saving,
            saving_percentage=15.0,
            difficulty=2,
            implementation_time="2-4个月",
            priority=1 if item.amount > 5000 else 2
        )
    
    def _create_admin_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建管理和一般费用优化建议"""
        potential_saving = item.amount * 0.1  # 假设可以节省10%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="简化管理流程，减少行政开支",
            description="审查并简化管理层级和审批流程，提高决策效率。推进无纸化办公，减少办公耗材支出。考虑共享服务中心模式，集中处理行政事务，实现规模效益。",
            potential_saving=potential_saving,
            saving_percentage=10.0,
            difficulty=3,
            implementation_time="4-8个月",
            priority=2
        )
    
    def _create_rent_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建租金优化建议"""
        potential_saving = item.amount * 0.08  # 假设可以节省8%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="优化空间使用，减少租赁支出",
            description="评估当前办公/经营空间利用率，考虑重新规划或缩减低效使用空间。探索灵活办公模式，如远程工作，减少对物理空间的需求。与业主协商长期租约，争取更优惠的租金条件。",
            potential_saving=potential_saving,
            saving_percentage=8.0,
            difficulty=4,
            implementation_time="6-12个月",
            priority=2
        )
    
    def _create_utilities_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建水电费优化建议"""
        potential_saving = item.amount * 0.2  # 假设可以节省20%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="提高能源使用效率，降低水电支出",
            description="安装智能照明和温控系统，根据实际需求自动调节用电。更换为节能设备和LED照明。开展节能意识培训，养成员工节约用水用电的习惯。考虑使用可再生能源，如屋顶太阳能等。",
            potential_saving=potential_saving,
            saving_percentage=20.0,
            difficulty=2,
            implementation_time="1-3个月",
            priority=3
        )
    
    def _create_logistics_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建物流费用优化建议"""
        potential_saving = item.amount * 0.12  # 假设可以节省12%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="优化物流网络，降低运输成本",
            description="重新规划配送路线，提高装载率，减少空车率。考虑整合多个订单的配送，提高配送效率。与多家物流供应商比价，选择性价比最高的合作方。优化仓储布局，减少交叉运输。",
            potential_saving=potential_saving,
            saving_percentage=12.0,
            difficulty=3,
            implementation_time="3-6个月",
            priority=2
        )
    
    def _create_packaging_suggestion(self, item: CostBreakdownItem) -> CostOptimizationSuggestion:
        """创建包装费用优化建议"""
        potential_saving = item.amount * 0.15  # 假设可以节省15%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=item.category,
            subcategory=item.subcategory,
            title="改进包装设计，降低材料成本",
            description="重新设计产品包装，减少材料使用量。使用可回收或生物可降解材料，降低环境影响。标准化包装尺寸，提高物流效率。与包装供应商协商批量采购折扣。",
            potential_saving=potential_saving,
            saving_percentage=15.0,
            difficulty=2,
            implementation_time="2-4个月",
            priority=3
        )
    
    def _create_high_fixed_cost_suggestion(self, fixed_ratio: float, fixed_amount: float) -> CostOptimizationSuggestion:
        """创建高固定成本优化建议"""
        potential_saving = fixed_amount * 0.1  # 假设可以节省10%
        
        return CostOptimizationSuggestion(
            suggestion_id=f"sugg_{uuid.uuid4().hex[:8]}",
            category=CostCategory.OTHER,
            subcategory="固定成本结构",
            title="调整成本结构，降低固定成本占比",
            description=f"当前固定成本占比为{fixed_ratio:.1%}，较高的固定成本使企业在业务量波动时缺乏灵活性。建议将部分固定成本转为变动成本，如考虑设备租赁而非购买、基于业务量的供应商付款模式、灵活用工等。",
            potential_saving=potential_saving,
            saving_percentage=10.0,
            difficulty=4,
            implementation_time="6-12个月",
            priority=1
        )


class CostAnalyzer:
    """成本分析引擎，整合各种分析功能"""
    
    def __init__(self):
        """初始化成本分析引擎"""
        self.breakdown_analyzer = CostBreakdownAnalyzer()
        self.trend_analyzer = CostTrendAnalyzer()
        self.optimization_analyzer = CostOptimizationAnalyzer()
        self.logger = logging.getLogger("cost_analyzer")
    
    def analyze_cost(
        self, 
        cost_data: CostData, 
        include_trend: bool = True,
        include_suggestions: bool = True
    ) -> CostAnalysis:
        """
        分析成本数据
        
        Args:
            cost_data: 成本数据
            include_trend: 是否包含趋势分析
            include_suggestions: 是否包含优化建议
            
        Returns:
            成本分析结果
        """
        self.logger.info(f"Analyzing cost data for merchant {cost_data.merchant_id}")
        
        # 成本拆解
        breakdown = self.breakdown_analyzer.analyze_breakdown(cost_data)
        
        # 趋势分析（可选）
        trend = None
        if include_trend:
            trend = self.trend_analyzer.analyze_trend(cost_data)
        
        # 优化建议（可选）
        optimization_suggestions = None
        if include_suggestions:
            optimization_suggestions = self.optimization_analyzer.generate_suggestions(cost_data, breakdown)
        
        # 创建分析结果
        analysis = CostAnalysis(
            merchant_id=cost_data.merchant_id,
            time_range=cost_data.time_range,
            breakdown=breakdown,
            trend=trend,
            optimization_suggestions=optimization_suggestions,
            created_at=datetime.now(),
            metadata={
                "analysis_id": f"cost_analysis_{uuid.uuid4().hex[:8]}",
                "cost_items_count": len(cost_data.items)
            }
        )
        
        return analysis 
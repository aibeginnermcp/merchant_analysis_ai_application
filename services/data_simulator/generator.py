"""数据生成器模块"""
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from .models import (
    MerchantProfile,
    DailyTransaction,
    DailyCost,
    DailyFinancial,
    ComplianceRecord,
    MarketingActivity,
    IndustryType,
    MerchantSize,
    PaymentMethod,
    ComplianceViolationType
)
from .config import SimulatorConfig

class DataGenerator:
    """数据生成器"""
    
    def __init__(self, config: Optional[SimulatorConfig] = None):
        """初始化数据生成器
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or SimulatorConfig()
        self.patterns = self.config.INDUSTRY_PATTERNS
        
    def generate_merchant_profile(self, industry: Optional[str] = None) -> MerchantProfile:
        """生成商户基础信息
        
        Args:
            industry: 指定行业类型，如果为None则随机选择
            
        Returns:
            MerchantProfile: 商户基础信息对象
        """
        if industry is None:
            industry = random.choice(list(IndustryType))
        else:
            industry = IndustryType(industry)
            
        pattern = self.patterns[industry.value]
        
        # 生成位置信息
        location = {
            "latitude": random.uniform(22.0, 45.0),  # 中国纬度范围
            "longitude": random.uniform(75.0, 135.0)  # 中国经度范围
        }
        
        # 生成营业时间
        business_hours = {
            "weekday": f"{random.randint(7,9)}:00-{random.randint(20,22)}:00",
            "weekend": f"{random.randint(8,10)}:00-{random.randint(21,23)}:00"
        }
        
        return MerchantProfile(
            merchant_id=f"M{random.randint(10000, 99999)}",
            name=f"{industry.value.title()}-{random.randint(1000, 9999)}",
            industry=industry,
            size=random.choice(list(MerchantSize)),
            establishment_date=datetime.now() - timedelta(days=random.randint(365, 3650)),
            location=location,
            business_hours=business_hours,
            payment_methods=[PaymentMethod(m) for m in pattern["payment_methods"]],
            rating=round(random.uniform(3.5, 4.8), 1)
        )

    def generate_daily_transaction(
        self,
        profile: MerchantProfile,
        date: datetime,
        marketing_activities: List[MarketingActivity] = None
    ) -> DailyTransaction:
        """生成日交易数据
        
        Args:
            profile: 商户基础信息
            date: 日期
            marketing_activities: 当日的营销活动列表
            
        Returns:
            DailyTransaction: 日交易数据对象
        """
        pattern = self.patterns[profile.industry.value]
        base_revenue = random.uniform(*pattern["revenue_range"])
        
        # 添加周末效应
        if date.weekday() >= 5:  # 周末
            base_revenue *= 1.3
            
        # 添加季节性波动
        month = date.month
        if month in [7, 8, 12, 1]:  # 旺季
            base_revenue *= 1.2
        elif month in [2, 3]:  # 淡季
            base_revenue *= 0.8
            
        # 添加营销活动效果
        if marketing_activities:
            for activity in marketing_activities:
                if activity.start_date <= date <= activity.end_date:
                    base_revenue *= random.uniform(1.1, 1.3)  # 促销效果提升10-30%
        
        # 生成支付方式分布
        payment_distribution = self._generate_payment_distribution(profile.payment_methods)
        
        # 生成渠道分布
        channel_distribution = pattern["channels"]
        
        return DailyTransaction(
            date=date,
            revenue=base_revenue,
            transaction_count=int(base_revenue / random.uniform(50, 100)),
            average_transaction_value=random.uniform(50, 200),
            peak_hours=random.sample(pattern["peak_hours"], k=3),
            payment_distribution=payment_distribution,
            channel_distribution=channel_distribution,
            refund_amount=base_revenue * random.uniform(0, 0.05)  # 0-5%的退款率
        )

    def generate_daily_cost(
        self,
        profile: MerchantProfile,
        transaction: DailyTransaction
    ) -> DailyCost:
        """生成日成本数据
        
        Args:
            profile: 商户基础信息
            transaction: 日交易数据
            
        Returns:
            DailyCost: 日成本数据对象
        """
        pattern = self.patterns[profile.industry.value]
        revenue = transaction.revenue
        
        def get_cost(ratio_range: tuple) -> float:
            return revenue * random.uniform(*ratio_range)
        
        ratios = pattern["cost_ratios"]
        return DailyCost(
            date=transaction.date,
            raw_material_cost=get_cost(ratios["raw_material"]),
            labor_cost=get_cost(ratios["labor"]),
            utility_cost=get_cost(ratios["utility"]),
            rent_cost=get_cost(ratios["rent"]),
            marketing_cost=get_cost(ratios["marketing"]),
            logistics_cost=get_cost(ratios["logistics"]),
            other_cost=revenue * random.uniform(0.05, 0.1)
        )

    def generate_daily_financial(
        self,
        transaction: DailyTransaction,
        cost: DailyCost,
        previous_financial: Optional[DailyFinancial] = None
    ) -> DailyFinancial:
        """生成日财务数据
        
        Args:
            transaction: 日交易数据
            cost: 日成本数据
            previous_financial: 前一天的财务数据
            
        Returns:
            DailyFinancial: 日财务数据对象
        """
        revenue = transaction.revenue
        total_cost = cost.total_cost
        
        # 如果有前一天的数据，基于其计算当天的数据
        if previous_financial:
            accounts_receivable = (
                previous_financial.accounts_receivable +
                revenue * random.uniform(0.1, 0.2) -  # 新增应收
                previous_financial.accounts_receivable * random.uniform(0.3, 0.5)  # 收回部分应收
            )
            accounts_payable = (
                previous_financial.accounts_payable +
                total_cost * random.uniform(0.2, 0.3) -  # 新增应付
                previous_financial.accounts_payable * random.uniform(0.4, 0.6)  # 支付部分应付
            )
            cash_balance = (
                previous_financial.cash_balance +
                revenue -  # 收入
                total_cost -  # 成本
                transaction.refund_amount  # 退款
            )
        else:
            accounts_receivable = revenue * random.uniform(0.1, 0.2)
            accounts_payable = total_cost * random.uniform(0.2, 0.3)
            cash_balance = revenue - total_cost
            
        return DailyFinancial(
            date=transaction.date,
            accounts_receivable=accounts_receivable,
            accounts_payable=accounts_payable,
            cash_balance=cash_balance,
            inventory_value=cost.raw_material_cost * random.uniform(0.5, 0.8),
            operating_expenses=total_cost * random.uniform(0.05, 0.1),
            tax_payable=revenue * random.uniform(0.05, 0.08)
        )

    def generate_compliance_record(
        self,
        profile: MerchantProfile,
        date: datetime,
        previous_record: Optional[ComplianceRecord] = None
    ) -> ComplianceRecord:
        """生成合规记录
        
        Args:
            profile: 商户基础信息
            date: 日期
            previous_record: 上一次的合规记录
            
        Returns:
            ComplianceRecord: 合规记录对象
        """
        patterns = self.config.COMPLIANCE_PATTERNS
        
        # 确定是否进行检查
        is_regular_check = (
            not previous_record or
            (date - previous_record.last_inspection_date).days >= patterns["regular_inspection"]["frequency"]
        )
        is_random_check = random.random() < patterns["random_inspection"]["probability"]
        
        if not (is_regular_check or is_random_check):
            return previous_record
            
        def get_compliance_status(base_rate: float) -> bool:
            return random.random() < base_rate
            
        # 生成违规记录
        violations = []
        for violation_type in ComplianceViolationType:
            if not get_compliance_status(0.95):  # 5%的违规概率
                violations.append(violation_type)
                
        # 确定风险等级
        if len(violations) == 0:
            risk_level = "low"
        elif len(violations) <= 2:
            risk_level = "medium"
        else:
            risk_level = "high"
            
        return ComplianceRecord(
            date=date,
            license_status=get_compliance_status(0.98),
            tax_compliance=get_compliance_status(0.96),
            health_safety_compliance=get_compliance_status(0.95),
            employee_insurance=get_compliance_status(0.93),
            environmental_compliance=get_compliance_status(0.94),
            violations=violations,
            last_inspection_date=date,
            next_inspection_date=date + timedelta(days=patterns["regular_inspection"]["frequency"]),
            risk_level=risk_level
        )

    def generate_marketing_activities(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[MarketingActivity]:
        """生成营销活动列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[MarketingActivity]: 营销活动列表
        """
        activities = []
        patterns = self.config.MARKETING_PATTERNS
        current_date = start_date
        
        while current_date <= end_date:
            # 每周生成1-2个活动
            if current_date.weekday() == 0 and random.random() < 0.8:
                activity_type = random.choices(
                    list(patterns.keys()),
                    weights=[p["probability"] for p in patterns.values()]
                )[0]
                
                duration = random.randint(3, 7)  # 活动持续3-7天
                budget = random.uniform(1000, 5000)
                expected_roi = random.uniform(1.5, 3.0)
                
                activity = MarketingActivity(
                    activity_id=f"A{random.randint(10000, 99999)}",
                    name=f"{activity_type.title()}促销活动",
                    type=activity_type,
                    start_date=current_date,
                    end_date=current_date + timedelta(days=duration),
                    budget=budget,
                    target_audience=random.sample(
                        ["新客户", "老客户", "会员", "流失客户"],
                        k=random.randint(1, 3)
                    ),
                    channels=random.sample(
                        ["线下", "微信", "支付宝", "短信", "邮件"],
                        k=random.randint(2, 4)
                    ),
                    expected_roi=expected_roi
                )
                activities.append(activity)
                
            current_date += timedelta(days=1)
            
        return activities

    async def generate_merchant_data(
        self,
        start_date: datetime,
        end_date: datetime,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成完整的商户数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            industry: 指定行业类型，如果为None则随机选择
            
        Returns:
            Dict[str, Any]: 包含所有生成数据的字典
        """
        # 生成商户基础信息
        profile = self.generate_merchant_profile(industry)
        
        # 生成营销活动
        marketing_activities = self.generate_marketing_activities(start_date, end_date)
        
        current_date = start_date
        transactions = []
        costs = []
        financials = []
        compliance_records = []
        previous_financial = None
        previous_compliance = None
        
        while current_date <= end_date:
            # 获取当日的营销活动
            current_activities = [
                activity for activity in marketing_activities
                if activity.start_date <= current_date <= activity.end_date
            ]
            
            # 生成每日数据
            transaction = self.generate_daily_transaction(
                profile,
                current_date,
                current_activities
            )
            cost = self.generate_daily_cost(profile, transaction)
            financial = self.generate_daily_financial(
                transaction,
                cost,
                previous_financial
            )
            compliance = self.generate_compliance_record(
                profile,
                current_date,
                previous_compliance
            )
            
            transactions.append(transaction)
            costs.append(cost)
            financials.append(financial)
            if compliance != previous_compliance:
                compliance_records.append(compliance)
            
            previous_financial = financial
            previous_compliance = compliance
            current_date += timedelta(days=1)
            
        return {
            "profile": profile,
            "transactions": transactions,
            "costs": costs,
            "financials": financials,
            "compliance_records": compliance_records,
            "marketing_activities": marketing_activities
        }
        
    def _generate_payment_distribution(
        self,
        available_methods: List[PaymentMethod]
    ) -> Dict[PaymentMethod, float]:
        """生成支付方式分布
        
        Args:
            available_methods: 可用的支付方式列表
            
        Returns:
            Dict[PaymentMethod, float]: 支付方式分布
        """
        weights = np.random.dirichlet(np.ones(len(available_methods)))
        return {method: weight for method, weight in zip(available_methods, weights)} 
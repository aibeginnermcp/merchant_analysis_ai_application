"""
数据模拟服务的数据模型定义
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

class IndustryType(str, Enum):
    """行业类型枚举"""
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    ECOMMERCE = "ecommerce"
    SERVICE = "service"

class MerchantSize(str, Enum):
    """商户规模枚举"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class PaymentMethod(str, Enum):
    """支付方式枚举"""
    CASH = "cash"
    CARD = "card"
    ALIPAY = "alipay"
    WECHAT = "wechat"
    OTHER = "other"

class TransactionType(str, Enum):
    """交易类型枚举"""
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出
    TRANSFER = "transfer"  # 转账
    REFUND = "refund"  # 退款

class TransactionCategory(str, Enum):
    """交易类别枚举"""
    # 收入类别
    SALES = "sales"  # 销售收入
    SERVICE = "service"  # 服务收入
    INTEREST = "interest"  # 利息收入
    INVESTMENT = "investment"  # 投资收入
    OTHER_INCOME = "other_income"  # 其他收入
    
    # 支出类别
    RENT = "rent"  # 租金
    SALARY = "salary"  # 工资
    UTILITIES = "utilities"  # 水电费
    INVENTORY = "inventory"  # 库存采购
    MARKETING = "marketing"  # 市场营销
    EQUIPMENT = "equipment"  # 设备购置
    TAX = "tax"  # 税费
    INSURANCE = "insurance"  # 保险
    MAINTENANCE = "maintenance"  # 维护费用
    OTHER_EXPENSE = "other_expense"  # 其他支出

class MerchantType(str, Enum):
    """商户类型枚举"""
    RETAIL = "retail"  # 零售
    RESTAURANT = "restaurant"  # 餐饮
    SERVICE = "service"  # 服务业
    MANUFACTURE = "manufacture"  # 制造业
    WHOLESALE = "wholesale"  # 批发
    ECOMMERCE = "ecommerce"  # 电子商务
    HEALTHCARE = "healthcare"  # 医疗保健
    EDUCATION = "education"  # 教育
    TECHNOLOGY = "technology"  # 科技
    FINANCE = "finance"  # 金融

class MerchantProfile(BaseModel):
    """商户基础信息"""
    merchant_id: str = Field(..., description="商户ID")
    name: str = Field(..., description="商户名称")
    industry: IndustryType = Field(..., description="行业类型")
    size: MerchantSize = Field(..., description="规模大小")
    establishment_date: datetime = Field(..., description="成立日期")
    location: Dict[str, float] = Field(..., description="地理位置(经纬度)")
    business_hours: Dict[str, str] = Field(..., description="营业时间")
    payment_methods: List[PaymentMethod] = Field(..., description="支持的支付方式")
    rating: float = Field(..., ge=0, le=5, description="商户评分")
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 0 <= v <= 5:
            raise ValueError('评分必须在0-5之间')
        return round(v, 1)

class DailyTransaction(BaseModel):
    """日交易数据"""
    date: datetime = Field(..., description="交易日期")
    revenue: float = Field(..., ge=0, description="营业收入")
    transaction_count: int = Field(..., ge=0, description="交易笔数")
    average_transaction_value: float = Field(..., ge=0, description="平均客单价")
    peak_hours: List[int] = Field(..., description="高峰时段")
    payment_distribution: Dict[PaymentMethod, float] = Field(..., description="支付方式分布")
    channel_distribution: Dict[str, float] = Field(..., description="渠道分布")
    refund_amount: float = Field(0, ge=0, description="退款金额")
    
    @validator('payment_distribution')
    def validate_payment_distribution(cls, v):
        if abs(sum(v.values()) - 1) > 0.01:
            raise ValueError('支付方式分布比例之和必须为1')
        return v

class DailyCost(BaseModel):
    """日成本数据"""
    date: datetime = Field(..., description="日期")
    raw_material_cost: float = Field(..., ge=0, description="原材料成本")
    labor_cost: float = Field(..., ge=0, description="人工成本")
    utility_cost: float = Field(..., ge=0, description="水电费用")
    rent_cost: float = Field(..., ge=0, description="租金成本")
    marketing_cost: float = Field(0, ge=0, description="营销成本")
    logistics_cost: float = Field(0, ge=0, description="物流成本")
    other_cost: float = Field(..., ge=0, description="其他成本")
    
    @property
    def total_cost(self) -> float:
        """计算总成本"""
        return (
            self.raw_material_cost +
            self.labor_cost +
            self.utility_cost +
            self.rent_cost +
            self.marketing_cost +
            self.logistics_cost +
            self.other_cost
        )

class DailyFinancial(BaseModel):
    """日财务数据"""
    date: datetime = Field(..., description="日期")
    accounts_receivable: float = Field(..., ge=0, description="应收账款")
    accounts_payable: float = Field(..., ge=0, description="应付账款")
    cash_balance: float = Field(..., description="现金余额")
    inventory_value: float = Field(..., ge=0, description="库存价值")
    operating_expenses: float = Field(..., ge=0, description="运营费用")
    tax_payable: float = Field(..., ge=0, description="应交税费")
    
    def calculate_working_capital(self) -> float:
        """计算营运资金"""
        return (
            self.cash_balance +
            self.accounts_receivable -
            self.accounts_payable -
            self.tax_payable
        )

class ComplianceViolationType(str, Enum):
    """违规类型枚举"""
    LICENSE_EXPIRED = "营业执照过期"
    FIRE_SAFETY = "消防设施不达标"
    HEALTH_SAFETY = "卫生条件不合格"
    TAX_DELAY = "税务申报延迟"
    LABOR_ISSUE = "劳动合规问题"
    ENVIRONMENTAL = "环保违规"

class ComplianceRecord(BaseModel):
    """合规记录"""
    date: datetime = Field(..., description="记录日期")
    license_status: bool = Field(..., description="证照状态")
    tax_compliance: bool = Field(..., description="税务合规")
    health_safety_compliance: bool = Field(..., description="卫生安全合规")
    employee_insurance: bool = Field(..., description="员工保险状态")
    environmental_compliance: bool = Field(..., description="环保合规")
    violations: List[ComplianceViolationType] = Field(default_factory=list, description="违规记录")
    last_inspection_date: datetime = Field(..., description="最近检查日期")
    next_inspection_date: datetime = Field(..., description="下次检查日期")
    risk_level: str = Field(..., description="风险等级")
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        valid_levels = ['low', 'medium', 'high']
        if v.lower() not in valid_levels:
            raise ValueError('风险等级必须为low/medium/high之一')
        return v.lower()

class MarketingActivity(BaseModel):
    """营销活动"""
    activity_id: str = Field(..., description="活动ID")
    name: str = Field(..., description="活动名称")
    type: str = Field(..., description="活动类型")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    budget: float = Field(..., ge=0, description="预算")
    target_audience: List[str] = Field(..., description="目标受众")
    channels: List[str] = Field(..., description="投放渠道")
    expected_roi: float = Field(..., description="预期ROI")
    actual_roi: Optional[float] = Field(None, description="实际ROI")
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期必须晚于开始日期')
        return v 

class TimeRange(BaseModel):
    """时间范围模型"""
    start_date: str = Field(..., description="开始日期，格式：YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期，格式：YYYY-MM-DD")

class Merchant(BaseModel):
    """商户信息模型"""
    merchant_id: str = Field(..., description="商户ID")
    merchant_name: str = Field(..., description="商户名称")
    merchant_type: MerchantType = Field(..., description="商户类型")
    business_scale: str = Field(..., description="业务规模: small, medium, large")
    established_date: str = Field(..., description="成立日期，格式：YYYY-MM-DD")
    
class Transaction(BaseModel):
    """交易记录模型"""
    transaction_id: str = Field(..., description="交易ID")
    merchant_id: str = Field(..., description="商户ID")
    timestamp: datetime = Field(..., description="交易时间")
    amount: float = Field(..., description="交易金额")
    transaction_type: TransactionType = Field(..., description="交易类型")
    category: TransactionCategory = Field(..., description="交易类别")
    description: Optional[str] = Field(None, description="交易描述")
    metadata: Optional[Dict[str, str]] = Field(None, description="元数据")

class CostItem(BaseModel):
    """成本项目模型"""
    cost_id: str = Field(..., description="成本ID")
    merchant_id: str = Field(..., description="商户ID")
    timestamp: datetime = Field(..., description="记录时间")
    amount: float = Field(..., description="成本金额")
    category: TransactionCategory = Field(..., description="成本类别")
    is_fixed: bool = Field(..., description="是否为固定成本")
    description: Optional[str] = Field(None, description="成本描述")
    recurrence: Optional[str] = Field(None, description="周期性: daily, weekly, monthly, yearly, once")

class SimulationConfig(BaseModel):
    """模拟配置模型"""
    merchant: Merchant
    time_range: TimeRange
    transaction_count: Optional[int] = Field(None, description="要生成的交易数量")
    seasonality: Optional[bool] = Field(True, description="是否包含季节性变化")
    growth_trend: Optional[float] = Field(0, description="增长趋势，如0.05表示5%的年增长率")
    volatility: Optional[float] = Field(0.1, description="波动性，值越大日常波动越大")
    weekend_effect: Optional[float] = Field(0.3, description="周末效应，正值表示周末增加，负值表示周末减少")
    
class SimulationResult(BaseModel):
    """模拟结果模型"""
    merchant_id: str
    time_range: TimeRange
    transactions: List[Transaction]
    costs: List[CostItem]
    metadata: Dict[str, Union[str, int, float]] 
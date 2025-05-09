"""
数据验证器模块

负责数据验证和错误处理，包括：
- 输入数据验证
- 业务规则验证
- 自定义异常
"""

from typing import Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from decimal import Decimal

class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, message: str, details: Dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class BusinessError(Exception):
    """业务逻辑错误异常"""
    def __init__(self, message: str, code: str, details: Dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class CashflowDataValidator(BaseModel):
    """
    现金流数据验证模型
    
    验证输入数据的格式和业务规则
    """
    id: str = Field(..., description="记录ID")
    merchant_id: str = Field(..., description="商户ID")
    date: datetime = Field(..., description="日期")
    type: str = Field(..., description="类型")
    category: str = Field(..., description="类别")
    amount: Decimal = Field(..., description="金额")
    is_recurring: bool = Field(..., description="是否经常性")
    probability: float = Field(..., description="发生概率")
    tags: List[str] = Field(default_factory=list, description="标签")

    @validator("type")
    def validate_type(cls, v):
        """验证类型"""
        if v not in ["inflow", "outflow"]:
            raise ValidationError(
                "Invalid cashflow type",
                {"type": "must be either 'inflow' or 'outflow'"}
            )
        return v

    @validator("amount")
    def validate_amount(cls, v):
        """验证金额"""
        if v <= 0:
            raise ValidationError(
                "Invalid amount",
                {"amount": "must be greater than 0"}
            )
        return v

    @validator("probability")
    def validate_probability(cls, v):
        """验证概率"""
        if not 0 <= v <= 1:
            raise ValidationError(
                "Invalid probability",
                {"probability": "must be between 0 and 1"}
            )
        return v

class PredictionRequestValidator(BaseModel):
    """
    预测请求验证模型
    
    验证预测请求参数
    """
    merchant_id: str = Field(..., description="商户ID")
    start_date: datetime = Field(..., description="预测开始日期")
    end_date: datetime = Field(..., description="预测结束日期")
    granularity: str = Field(
        "daily",
        description="预测粒度",
        enum=["daily", "weekly", "monthly"]
    )

    @validator("end_date")
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        if "start_date" in values and v <= values["start_date"]:
            raise ValidationError(
                "Invalid date range",
                {"end_date": "must be greater than start_date"}
            )
        return v

    @validator("start_date")
    def validate_start_date(cls, v):
        """验证开始日期"""
        if v < datetime.now():
            raise ValidationError(
                "Invalid start date",
                {"start_date": "must not be in the past"}
            )
        return v

class DataValidator:
    """
    数据验证器
    
    提供数据验证和错误处理方法
    """
    
    @staticmethod
    def validate_cashflow_data(data: Dict) -> None:
        """
        验证现金流数据
        
        Args:
            data: 现金流数据
            
        Raises:
            ValidationError: 数据验证错误
            BusinessError: 业务规则错误
        """
        try:
            CashflowDataValidator(**data)
        except ValidationError as e:
            raise ValidationError(
                "Invalid cashflow data",
                e.details
            )
            
    @staticmethod
    def validate_prediction_request(request: Dict) -> None:
        """
        验证预测请求
        
        Args:
            request: 预测请求参数
            
        Raises:
            ValidationError: 参数验证错误
        """
        try:
            PredictionRequestValidator(**request)
        except ValidationError as e:
            raise ValidationError(
                "Invalid prediction request",
                e.details
            )
            
    @staticmethod
    def validate_historical_data(data: List[Dict]) -> None:
        """
        验证历史数据
        
        Args:
            data: 历史数据列表
            
        Raises:
            ValidationError: 数据验证错误
            BusinessError: 业务规则错误
        """
        if not data:
            raise BusinessError(
                "Insufficient historical data",
                "INSUFFICIENT_DATA",
                {"min_required": 30}
            )
            
        # 验证每条记录
        for record in data:
            DataValidator.validate_cashflow_data(record)
            
        # 验证数据完整性
        dates = [record["date"] for record in data]
        date_range = (max(dates) - min(dates)).days
        if date_range < 30:
            raise BusinessError(
                "Insufficient historical data range",
                "INSUFFICIENT_DATE_RANGE",
                {
                    "current_range": date_range,
                    "min_required": 30
                }
            )
            
    @staticmethod
    def validate_prediction_result(result: Dict) -> None:
        """
        验证预测结果
        
        Args:
            result: 预测结果
            
        Raises:
            ValidationError: 结果验证错误
        """
        required_keys = [
            "inflow_prediction",
            "outflow_prediction",
            "net_cashflow",
            "confidence_intervals"
        ]
        
        missing_keys = [
            key for key in required_keys
            if key not in result
        ]
        
        if missing_keys:
            raise ValidationError(
                "Invalid prediction result",
                {"missing_keys": missing_keys}
            )
            
        # 验证预测值的合理性
        for key in ["inflow_prediction", "outflow_prediction"]:
            values = result[key].values()
            if any(v < 0 for v in values):
                raise ValidationError(
                    f"Invalid {key}",
                    {key: "contains negative values"}
                ) 
"""
现金流预测服务的数据模型定义
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator

class TimeRange(BaseModel):
    """时间范围模型"""
    start_date: str = Field(..., description="开始日期，格式：YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期，格式：YYYY-MM-DD")
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期必须晚于开始日期')
        return v

class TimeSeriesData(BaseModel):
    """时间序列数据"""
    date: str = Field(..., description="日期，格式：YYYY-MM-DD")
    value: float = Field(..., description="数值")
    
class CashflowData(BaseModel):
    """现金流数据"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    data: List[TimeSeriesData] = Field(..., description="时间序列数据")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class PredictionMethod(str, Enum):
    """预测方法枚举"""
    ARIMA = "arima"  # 自回归积分移动平均模型
    PROPHET = "prophet"  # Facebook Prophet模型
    LSTM = "lstm"  # 长短期记忆神经网络
    ENSEMBLE = "ensemble"  # 集成方法

class PredictionConfig(BaseModel):
    """预测配置"""
    method: PredictionMethod = Field(PredictionMethod.ARIMA, description="预测方法")
    prediction_days: int = Field(30, description="预测天数", ge=1, le=365)
    confidence_level: float = Field(0.95, description="置信水平", ge=0.5, le=0.99)
    include_holidays: bool = Field(True, description="是否考虑节假日")
    use_weekday_patterns: bool = Field(True, description="是否使用工作日模式")
    seasonality_mode: Optional[str] = Field("multiplicative", description="季节性模式: multiplicative或additive")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="模型超参数")

class ConfidenceInterval(BaseModel):
    """置信区间"""
    lower: float = Field(..., description="下界")
    upper: float = Field(..., description="上界")

class PredictionPoint(BaseModel):
    """预测点"""
    date: str = Field(..., description="日期，格式：YYYY-MM-DD")
    value: float = Field(..., description="预测值")
    confidence_interval: Optional[ConfidenceInterval] = Field(None, description="置信区间")

class PerformanceMetrics(BaseModel):
    """性能指标"""
    mape: Optional[float] = Field(None, description="平均绝对百分比误差")
    rmse: Optional[float] = Field(None, description="均方根误差")
    mae: Optional[float] = Field(None, description="平均绝对误差")
    r2: Optional[float] = Field(None, description="R方值")

class PredictionResult(BaseModel):
    """预测结果"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="原始数据时间范围")
    prediction_range: TimeRange = Field(..., description="预测时间范围")
    predictions: List[PredictionPoint] = Field(..., description="预测点列表")
    method: PredictionMethod = Field(..., description="使用的预测方法")
    created_at: datetime = Field(..., description="预测创建时间")
    metrics: Optional[PerformanceMetrics] = Field(None, description="性能指标")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
class CashflowMetrics(BaseModel):
    """现金流指标"""
    average_daily_cash: float = Field(..., description="平均日现金流")
    volatility: float = Field(..., description="波动性")
    trend_coefficient: float = Field(..., description="趋势系数，正值表示上升趋势，负值表示下降趋势")
    seasonality_strength: Optional[float] = Field(None, description="季节性强度")
    autocorrelation: Optional[float] = Field(None, description="自相关系数")
    
class CashflowAnalysis(BaseModel):
    """现金流分析"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    metrics: CashflowMetrics = Field(..., description="现金流指标")
    prediction: Optional[PredictionResult] = Field(None, description="预测结果")
    raw_data: Optional[List[TimeSeriesData]] = Field(None, description="原始数据")
    created_at: datetime = Field(..., description="分析创建时间")

class PredictionRequest(BaseModel):
    """预测请求"""
    merchant_id: str = Field(..., description="商户ID")
    time_range: TimeRange = Field(..., description="时间范围")
    config: Optional[PredictionConfig] = Field(None, description="预测配置")
    
class PredictionResponse(BaseModel):
    """预测响应"""
    request_id: str = Field(..., description="请求ID")
    prediction: PredictionResult = Field(..., description="预测结果")
    status: str = Field("success", description="状态")
    error: Optional[str] = Field(None, description="错误信息") 
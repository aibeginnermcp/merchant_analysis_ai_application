"""
现金流预测服务的服务类，提供现金流分析和预测API接口
"""
import logging
import numpy as np
import uuid
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

from services.cashflow_predictor.models import (
    TimeSeriesData,
    CashflowData,
    PredictionMethod,
    PredictionConfig,
    PredictionResult,
    PerformanceMetrics,
    TimeRange,
    CashflowMetrics,
    CashflowAnalysis,
    PredictionPoint,
    ConfidenceInterval
)
from services.cashflow_predictor.predictor import CashflowPredictor
from services.cashflow_predictor.storage import MongoDBStorage, BaseStorage

class CashflowPredictorService:
    """现金流预测服务类"""
    
    def __init__(self, storage: Optional[BaseStorage] = None):
        """
        初始化服务
        
        Args:
            storage: 数据存储实例，如果为None则创建默认的MongoDB存储
        """
        self.logger = logging.getLogger("cashflow_predictor.service")
        self.storage = storage or MongoDBStorage()
        self.predictor = CashflowPredictor()
    
    async def prepare_cashflow_data(self, merchant_id: str, time_range: TimeRange) -> CashflowData:
        """
        准备现金流数据，如果数据库没有则从数据模拟服务获取
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            现金流数据
        """
        # 先尝试从数据库获取
        cashflow_data = await self.storage.get_cashflow_data(merchant_id, time_range)
        if cashflow_data:
            self.logger.info(f"Found existing cashflow data for merchant {merchant_id}")
            return cashflow_data
        
        # 如果没有，则从数据模拟服务获取
        # TODO: 实现与数据模拟服务的集成
        # 这里暂时生成一些模拟数据
        self.logger.info(f"Generating simulated cashflow data for merchant {merchant_id}")
        
        start_date = datetime.strptime(time_range.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(time_range.end_date, "%Y-%m-%d")
        days = (end_date - start_date).days + 1
        
        # 生成模拟数据，包括趋势、季节性和噪声
        date_range = [start_date + timedelta(days=i) for i in range(days)]
        
        # 基础值和趋势
        base_value = 1000
        trend_slope = 0.5  # 每天增长0.5
        
        # 生成时间序列
        time_series_data = []
        for i, date in enumerate(date_range):
            # 趋势组件
            trend = base_value + trend_slope * i
            
            # 季节性组件 (周周期)
            weekday = date.weekday()
            season_effect = 0
            if weekday == 5 or weekday == 6:  # 周末
                season_effect = trend * 0.2  # 周末增加20%
            
            # 季节性组件 (月周期)
            month_day = date.day
            if month_day == 1:
                season_effect += trend * 0.1  # 月初增加10%
            elif month_day >= 28:
                season_effect -= trend * 0.1  # 月末减少10%
            
            # 随机噪声
            noise = np.random.normal(0, trend * 0.05)
            
            # 最终值
            value = max(0, trend + season_effect + noise)
            
            # 添加到列表
            time_series_data.append(
                TimeSeriesData(
                    date=date.strftime("%Y-%m-%d"),
                    value=round(value, 2)
                )
            )
        
        # 创建现金流数据
        cashflow_data = CashflowData(
            merchant_id=merchant_id,
            time_range=time_range,
            data=time_series_data,
            metadata={
                "source": "simulated",
                "generated_at": datetime.now().isoformat()
            }
        )
        
        # 保存到数据库
        await self.storage.save_cashflow_data(cashflow_data)
        
        return cashflow_data
    
    async def analyze_cashflow(self, merchant_id: str, time_range: TimeRange) -> CashflowAnalysis:
        """
        分析现金流数据
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            现金流分析结果
        """
        self.logger.info(f"Analyzing cashflow for merchant {merchant_id}")
        
        # 获取现金流数据
        cashflow_data = await self.prepare_cashflow_data(merchant_id, time_range)
        
        # 提取时间序列值
        values = [ts.value for ts in cashflow_data.data]
        
        # 计算基本指标
        average_daily_cash = np.mean(values)
        volatility = np.std(values) / average_daily_cash  # 变异系数
        
        # 计算趋势系数 (简单线性回归)
        days = np.arange(len(values))
        trend_coef = np.polyfit(days, values, 1)[0] / average_daily_cash
        
        # 计算季节性强度 (使用自相关)
        if len(values) >= 14:  # 至少需要两周的数据
            # 计算7天滞后的自相关
            acf_7 = np.corrcoef(values[:-7], values[7:])[0, 1]
            seasonality_strength = max(0, acf_7)
        else:
            seasonality_strength = None
            acf_7 = None
        
        # 构建指标
        metrics = CashflowMetrics(
            average_daily_cash=round(average_daily_cash, 2),
            volatility=round(volatility, 4),
            trend_coefficient=round(trend_coef, 4),
            seasonality_strength=round(seasonality_strength, 4) if seasonality_strength is not None else None,
            autocorrelation=round(acf_7, 4) if acf_7 is not None else None
        )
        
        # 构建分析结果
        analysis = CashflowAnalysis(
            merchant_id=merchant_id,
            time_range=time_range,
            metrics=metrics,
            prediction=None,  # 暂时不包含预测
            raw_data=cashflow_data.data,
            created_at=datetime.now()
        )
        
        # 保存到数据库
        await self.storage.save_cashflow_analysis(analysis)
        
        return analysis
    
    async def predict_cashflow(
        self, 
        merchant_id: str, 
        time_range: TimeRange, 
        config: Optional[PredictionConfig] = None
    ) -> PredictionResult:
        """
        预测现金流
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            config: 预测配置，如果为None则使用默认配置
            
        Returns:
            预测结果
        """
        self.logger.info(f"Predicting cashflow for merchant {merchant_id}")
        
        # 使用默认配置如果没有提供
        if config is None:
            config = PredictionConfig()
        
        # 获取现金流数据
        cashflow_data = await self.prepare_cashflow_data(merchant_id, time_range)
        
        # 进行预测
        prediction_result = self.predictor.generate_prediction(cashflow_data, config)
        
        # 保存预测结果
        prediction_id = await self.storage.save_prediction(prediction_result)
        self.logger.info(f"Saved prediction with ID: {prediction_id}")
        
        # 获取现金流分析
        analysis = await self.storage.get_cashflow_analysis(merchant_id, time_range)
        
        # 如果有分析结果，更新预测
        if analysis:
            analysis.prediction = prediction_result
            analysis.created_at = datetime.now()
            await self.storage.save_cashflow_analysis(analysis)
        
        return prediction_result
    
    async def get_prediction(self, prediction_id: str) -> Optional[PredictionResult]:
        """
        获取预测结果
        
        Args:
            prediction_id: 预测ID
            
        Returns:
            预测结果，如果不存在则返回None
        """
        return await self.storage.get_prediction(prediction_id)
    
    async def get_latest_prediction(self, merchant_id: str) -> Optional[PredictionResult]:
        """
        获取最新预测结果
        
        Args:
            merchant_id: 商户ID
            
        Returns:
            最新预测结果，如果不存在则返回None
        """
        return await self.storage.get_latest_prediction(merchant_id)
    
    async def get_cashflow_analysis(self, merchant_id: str, time_range: TimeRange) -> Optional[CashflowAnalysis]:
        """
        获取现金流分析
        
        Args:
            merchant_id: 商户ID
            time_range: 时间范围
            
        Returns:
            现金流分析，如果不存在则返回None
        """
        return await self.storage.get_cashflow_analysis(merchant_id, time_range)
    
    async def get_historical_predictions(self, merchant_id: str, limit: int = 10) -> List[PredictionResult]:
        """
        获取历史预测结果
        
        Args:
            merchant_id: 商户ID
            limit: 返回结果数量限制
            
        Returns:
            预测结果列表
        """
        return await self.storage.get_historical_predictions(merchant_id, limit)
    
    async def cleanup_old_predictions(self, merchant_id: str, keep_count: int = 10) -> int:
        """
        清理旧的预测结果
        
        Args:
            merchant_id: 商户ID
            keep_count: 保留的最新预测数量
            
        Returns:
            删除的预测数量
        """
        return await self.storage.delete_old_predictions(merchant_id, keep_count) 
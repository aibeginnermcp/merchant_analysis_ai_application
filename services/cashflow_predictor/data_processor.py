"""
数据处理器模块

负责现金流数据的获取和预处理，包括：
- 数据获取
- 数据清洗
- 特征工程
- 数据转换
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
from sklearn.preprocessing import StandardScaler
from .config import BaseConfig

class DataProcessor:
    """
    数据处理器
    
    负责从数据库获取原始数据，并进行必要的预处理
    """
    
    def __init__(self):
        """初始化数据处理器"""
        config = BaseConfig.get_config()
        self.client = AsyncIOMotorClient(config["MONGODB_URL"])
        self.db = self.client[config["MONGODB_DB"]]
        self.scaler = StandardScaler()
        
    async def get_merchant_data(
        self,
        merchant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        获取商户现金流数据
        
        Args:
            merchant_id: 商户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含现金流数据的DataFrame
        """
        # 从MongoDB获取数据
        collection = self.db.cashflow_records
        cursor = collection.find({
            "merchant_id": merchant_id,
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        
        # 转换为DataFrame
        records = await cursor.to_list(length=None)
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        
        # 基本清洗
        df = self._clean_data(df)
        
        # 特征工程
        df = self._engineer_features(df)
        
        return df
        
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        if df.empty:
            return df
            
        # 处理缺失值
        df = df.fillna({
            "amount": 0,
            "probability": 1.0,
            "is_recurring": False
        })
        
        # 处理异常值
        df = self._handle_outliers(df)
        
        # 标准化日期格式
        df["date"] = pd.to_datetime(df["date"])
        
        # 排序
        df = df.sort_values("date")
        
        return df
        
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理异常值
        
        Args:
            df: 输入DataFrame
            
        Returns:
            处理后的DataFrame
        """
        if df.empty:
            return df
            
        # 使用IQR方法处理异常值
        Q1 = df["amount"].quantile(0.25)
        Q3 = df["amount"].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 将异常值替换为边界值
        df.loc[df["amount"] < lower_bound, "amount"] = lower_bound
        df.loc[df["amount"] > upper_bound, "amount"] = upper_bound
        
        return df
        
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        特征工程
        
        Args:
            df: 输入DataFrame
            
        Returns:
            添加特征后的DataFrame
        """
        if df.empty:
            return df
            
        # 时间特征
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"] = df["date"].dt.day
        df["dayofweek"] = df["date"].dt.dayofweek
        df["quarter"] = df["date"].dt.quarter
        df["is_month_end"] = df["date"].dt.is_month_end
        df["is_month_start"] = df["date"].dt.is_month_start
        
        # 滚动统计特征
        for window in [7, 30, 90]:
            df[f"amount_mean_{window}d"] = df.groupby("type")["amount"].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df[f"amount_std_{window}d"] = df.groupby("type")["amount"].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            )
            
        # 类别编码
        df = pd.get_dummies(df, columns=["category"], prefix="category")
        
        # 概率加权金额
        df["weighted_amount"] = df["amount"] * df["probability"]
        
        return df
        
    def prepare_for_prediction(
        self,
        df: pd.DataFrame,
        features: List[str]
    ) -> np.ndarray:
        """
        准备预测数据
        
        Args:
            df: 输入DataFrame
            features: 特征列表
            
        Returns:
            预处理后的特征矩阵
        """
        if df.empty:
            return np.array([])
            
        # 选择特征
        X = df[features].copy()
        
        # 标准化
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled
        
    def aggregate_by_period(
        self,
        df: pd.DataFrame,
        period: str = "D"
    ) -> pd.DataFrame:
        """
        按周期聚合数据
        
        Args:
            df: 输入DataFrame
            period: 聚合周期
            
        Returns:
            聚合后的DataFrame
        """
        if df.empty:
            return df
            
        # 按类型和日期聚合
        agg_df = df.groupby(
            ["type", pd.Grouper(key="date", freq=period)]
        ).agg({
            "amount": "sum",
            "weighted_amount": "sum",
            "probability": "mean"
        }).reset_index()
        
        return agg_df
        
    def prepare_for_prophet(
        self,
        df: pd.DataFrame,
        value_column: str = "amount"
    ) -> pd.DataFrame:
        """
        准备Prophet模型数据
        
        Args:
            df: 输入DataFrame
            value_column: 值列名
            
        Returns:
            Prophet格式的DataFrame
        """
        if df.empty:
            return pd.DataFrame(columns=["ds", "y"])
            
        prophet_df = pd.DataFrame({
            "ds": df["date"],
            "y": df[value_column]
        })
        
        return prophet_df 
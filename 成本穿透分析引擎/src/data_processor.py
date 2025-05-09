"""
数据处理器模块

负责成本数据的获取和预处理，包括：
- 数据清洗
- 格式转换
- 数据验证
- 数据聚合
"""

from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from .config.base import BaseConfig

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
        
    async def get_merchant_data(
        self,
        merchant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        获取商户成本数据
        
        Args:
            merchant_id: 商户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含处理后数据的字典
        """
        # 构建查询条件
        query = {
            "merchant_id": merchant_id,
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        # 获取原始数据
        cursor = self.db.cost_records.find(query)
        records = []
        async for doc in cursor:
            records.append(doc)
            
        # 转换为DataFrame进行处理
        df = pd.DataFrame(records)
        
        # 数据清洗
        df = self._clean_data(df)
        
        # 数据聚合
        aggregated = self._aggregate_data(df)
        
        return {
            "raw_data": df.to_dict("records"),
            "aggregated": aggregated
        }
        
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据
        
        - 处理缺失值
        - 移除异常值
        - 标准化格式
        """
        if df.empty:
            return df
            
        # 处理缺失值
        df = df.fillna({
            "amount": 0,
            "quantity": 0,
            "unit_price": 0
        })
        
        # 移除金额为负的记录
        df = df[df["amount"] >= 0]
        
        # 确保日期格式统一
        df["date"] = pd.to_datetime(df["date"])
        
        return df
        
    def _aggregate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        聚合数据
        
        - 按类别汇总
        - 按时间维度汇总
        - 计算统计指标
        """
        if df.empty:
            return {
                "by_category": {},
                "by_time": {},
                "statistics": {}
            }
            
        # 按类别汇总
        category_summary = df.groupby("cost_category").agg({
            "amount": ["sum", "mean", "count"],
            "quantity": "sum"
        }).to_dict()
        
        # 按时间维度汇总
        time_summary = df.groupby(df["date"].dt.to_period("M")).agg({
            "amount": "sum"
        }).to_dict()
        
        # 计算统计指标
        statistics = {
            "total_amount": df["amount"].sum(),
            "average_amount": df["amount"].mean(),
            "record_count": len(df),
            "category_count": df["cost_category"].nunique()
        }
        
        return {
            "by_category": category_summary,
            "by_time": time_summary,
            "statistics": statistics
        } 
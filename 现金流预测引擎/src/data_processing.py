"""
数据处理模块，负责数据的加载、清洗和预处理。

主要功能：
1. 加载原始订单数据
2. 数据清洗和异常值处理
3. 特征工程
4. 数据格式转换
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CashFlowDataProcessor:
    """
    现金流数据处理器
    
    负责处理原始订单数据，转换为适合现金流预测的格式
    """
    
    def __init__(self, config: dict):
        """
        初始化数据处理器
        
        Args:
            config: 配置字典，包含数据处理的相关参数
        """
        self.config = config
        self.raw_data = None
        self.processed_data = None
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        加载原始数据
        
        Args:
            file_path: 数据文件路径
            
        Returns:
            加载的数据框
        """
        try:
            data = pd.read_csv(file_path, parse_dates=['date'])
            logger.info(f"成功加载数据，共 {len(data)} 条记录")
            self.raw_data = data
            return data
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            raise
            
    def detect_outliers(self, data: pd.DataFrame, column: str) -> pd.Series:
        """
        使用IQR方法检测异常值
        
        Args:
            data: 数据框
            column: 要检测的列名
            
        Returns:
            布尔序列，True表示异常值
        """
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = (data[column] < lower_bound) | (data[column] > upper_bound)
        logger.info(f"检测到 {outliers.sum()} 个异常值")
        return outliers
        
    def handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        处理缺失值
        
        Args:
            data: 输入数据框
            
        Returns:
            处理后的数据框
        """
        # 记录原始缺失值数量
        missing_before = data.isnull().sum()
        
        # 对不同类型的缺失值采用不同的处理策略
        # 数值型列使用中位数填充
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].median())
        
        # 分类型列使用众数填充
        categorical_columns = data.select_dtypes(include=['object']).columns
        data[categorical_columns] = data[categorical_columns].fillna(data[categorical_columns].mode().iloc[0])
        
        # 记录处理后的缺失值数量
        missing_after = data.isnull().sum()
        logger.info(f"缺失值处理完成，处理前：{missing_before.sum()}，处理后：{missing_after.sum()}")
        
        return data
        
    def add_time_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        添加时间特征
        
        Args:
            data: 输入数据框
            
        Returns:
            添加时间特征后的数据框
        """
        data['year'] = data['date'].dt.year
        data['month'] = data['date'].dt.month
        data['day_of_week'] = data['date'].dt.dayofweek
        data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
        data['quarter'] = data['date'].dt.quarter
        
        return data
        
    def process_data(self) -> pd.DataFrame:
        """
        执行完整的数据处理流程
        
        Returns:
            处理后的数据框
        """
        if self.raw_data is None:
            raise ValueError("请先加载数据")
            
        data = self.raw_data.copy()
        
        # 1. 处理缺失值
        data = self.handle_missing_values(data)
        
        # 2. 检测和处理异常值
        outliers = self.detect_outliers(data, 'amount')
        data.loc[outliers, 'amount'] = np.nan
        data = self.handle_missing_values(data)
        
        # 3. 添加时间特征
        data = self.add_time_features(data)
        
        # 4. 按日期排序
        data = data.sort_values('date')
        
        self.processed_data = data
        logger.info("数据处理完成")
        return data
        
    def save_processed_data(self, output_path: str):
        """
        保存处理后的数据
        
        Args:
            output_path: 输出文件路径
        """
        if self.processed_data is None:
            raise ValueError("没有处理后的数据可保存")
            
        self.processed_data.to_csv(output_path, index=False)
        logger.info(f"数据已保存至 {output_path}") 
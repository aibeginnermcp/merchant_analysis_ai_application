"""
成本数据生成器模块
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CostDataGenerator:
    """
    成本数据生成器类
    
    负责生成：
    1. SKU成本数据
    2. 物流成本数据
    3. 生产成本数据
    4. 人工成本数据
    """
    
    def __init__(self):
        """初始化成本数据生成器"""
        # 品类配置
        self.category_config = {
            '3C': {
                'weight_range': (0.1, 5.0),  # kg
                'volume_range': (0.001, 0.1),  # m³
                'bom_components': ['电芯', '外壳', '电路板'],
                'base_logistics_cost': 5.0,  # 元/kg
                'labor_cost_range': (8, 15)  # 元/件
            },
            '服饰': {
                'weight_range': (0.1, 2.0),
                'volume_range': (0.01, 0.05),
                'complexity_types': ['basic', 'custom'],
                'storage_cost': 80.0,  # 元/m³/月
                'labor_cost': {'basic': 1.0, 'custom': 5.0}
            },
            '食品': {
                'weight_range': (0.2, 10.0),
                'volume_range': (0.001, 0.02),
                'shelf_life_range': (1, 60),  # 天
                'cold_chain_cost': 0.03,  # 元/kg/km
                'spoilage_rates': {7: 0.10, 30: 0.05, 9999: 0.02}
            },
            '家居': {
                'weight_range': (1.0, 50.0),
                'volume_range': (0.1, 2.0),
                'material_types': ['wood', 'board'],
                'transport_cost': 120.0,  # 元/m³
                'material_cost': {'wood': 15.0, 'board': 8.0}
            }
        }
        
    def generate_sku_base_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        生成SKU基础数据
        
        Args:
            n_samples: 样本数量
            
        Returns:
            pd.DataFrame: SKU基础数据
        """
        data = []
        categories = list(self.category_config.keys())
        
        for i in range(n_samples):
            category = np.random.choice(categories)
            config = self.category_config[category]
            
            sku_data = {
                'SKU_ID': f'SKU{i:05d}',
                'category': category,
                'weight': np.random.uniform(*config['weight_range']),
                'volume': np.random.uniform(*config['volume_range'])
            }
            
            # 添加品类特定属性
            if category == '3C':
                sku_data['bom_components'] = ','.join(config['bom_components'])
            elif category == '服饰':
                sku_data['complexity'] = np.random.choice(config['complexity_types'])
            elif category == '食品':
                sku_data['shelf_life'] = np.random.randint(*config['shelf_life_range'])
            elif category == '家居':
                sku_data['material_type'] = np.random.choice(config['material_types'])
                
            data.append(sku_data)
            
        return pd.DataFrame(data)
        
    def generate_logistics_costs(self, sku_data: pd.DataFrame) -> pd.DataFrame:
        """
        生成物流成本数据
        
        Args:
            sku_data: SKU基础数据
            
        Returns:
            pd.DataFrame: 物流成本数据
        """
        df = sku_data.copy()
        
        # 生成运输距离
        df['transport_distance'] = np.random.uniform(50, 1000, len(df))
        
        # 计算物流成本
        for category, config in self.category_config.items():
            mask = df['category'] == category
            if category == '3C':
                df.loc[mask, 'logistics_cost'] = df.loc[mask, 'weight'] * config['base_logistics_cost']
            elif category == '服饰':
                df.loc[mask, 'logistics_cost'] = df.loc[mask, 'volume'] * config['storage_cost']
            elif category == '食品':
                df.loc[mask, 'logistics_cost'] = df.loc[mask, 'weight'] * df.loc[mask, 'transport_distance'] * config['cold_chain_cost']
            elif category == '家居':
                df.loc[mask, 'logistics_cost'] = df.loc[mask, 'volume'] * config['transport_cost']
                
        return df
        
    def generate_production_costs(self, sku_data: pd.DataFrame) -> pd.DataFrame:
        """
        生成生产成本数据
        
        Args:
            sku_data: SKU基础数据
            
        Returns:
            pd.DataFrame: 生产成本数据
        """
        df = sku_data.copy()
        
        # 计算生产成本
        for category, config in self.category_config.items():
            mask = df['category'] == category
            if category == '3C':
                # 基于BOM成本计算
                base_cost = 30  # 基础成本
                df.loc[mask, 'production_cost'] = base_cost
            elif category == '服饰':
                # 基于复杂度计算
                df.loc[mask, 'production_cost'] = df.loc[mask, 'complexity'].map(
                    {'basic': 20, 'custom': 50}
                )
            elif category == '食品':
                # 基础生产成本
                df.loc[mask, 'production_cost'] = 15
            elif category == '家居':
                # 基于材料类型计算
                df.loc[mask, 'production_cost'] = df.loc[mask, 'material_type'].map(
                    {'wood': 30, 'board': 15}
                )
                
        return df
        
    def generate_labor_costs(self, sku_data: pd.DataFrame) -> pd.DataFrame:
        """
        生成人工成本数据
        
        Args:
            sku_data: SKU基础数据
            
        Returns:
            pd.DataFrame: 人工成本数据
        """
        df = sku_data.copy()
        
        # 计算人工成本
        for category, config in self.category_config.items():
            mask = df['category'] == category
            if category == '3C':
                df.loc[mask, 'labor_cost'] = np.random.uniform(*config['labor_cost_range'])
            elif category == '服饰':
                df.loc[mask, 'labor_cost'] = df.loc[mask, 'complexity'].map(config['labor_cost'])
            elif category == '食品':
                df.loc[mask, 'labor_cost'] = 5  # 固定人工成本
            elif category == '家居':
                df.loc[mask, 'labor_cost'] = df.loc[mask, 'material_type'].map(
                    {'wood': 15, 'board': 8}
                )
                
        return df
        
    def add_cost_anomalies(self, df: pd.DataFrame, anomaly_ratio: float = 0.05) -> pd.DataFrame:
        """
        添加成本异常数据
        
        Args:
            df: 成本数据
            anomaly_ratio: 异常数据比例
            
        Returns:
            pd.DataFrame: 添加异常后的数据
        """
        df = df.copy()
        n_anomalies = int(len(df) * anomaly_ratio)
        
        # 随机选择要添加异常的记录
        anomaly_indices = np.random.choice(len(df), n_anomalies, replace=False)
        
        # 添加异常值
        for idx in anomaly_indices:
            anomaly_type = np.random.choice(['logistics', 'production', 'labor'])
            if anomaly_type == 'logistics':
                df.loc[idx, 'logistics_cost'] *= np.random.uniform(3, 5)
            elif anomaly_type == 'production':
                df.loc[idx, 'production_cost'] *= np.random.uniform(3, 5)
            else:
                df.loc[idx, 'labor_cost'] *= np.random.uniform(3, 5)
                
        return df
        
    def generate_all_cost_data(self, n_samples: int = 1000, add_anomalies: bool = True) -> pd.DataFrame:
        """
        生成所有成本数据
        
        Args:
            n_samples: 样本数量
            add_anomalies: 是否添加异常数据
            
        Returns:
            pd.DataFrame: 完整的成本数据
        """
        # 生成基础数据
        df = self.generate_sku_base_data(n_samples)
        
        # 生成各类成本
        df = self.generate_logistics_costs(df)
        df = self.generate_production_costs(df)
        df = self.generate_labor_costs(df)
        
        # 添加异常数据
        if add_anomalies:
            df = self.add_cost_anomalies(df)
            
        return df 
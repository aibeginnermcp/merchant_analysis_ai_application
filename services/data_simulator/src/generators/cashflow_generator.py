"""
现金流预测数据生成器
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CashFlowGenerator:
    """
    现金流预测数据生成器
    用于生成包含应收账款、结算周期、坏账率等信息的模拟数据
    """
    
    def __init__(self):
        """初始化生成器参数"""
        self.start_date = datetime(2023, 1, 1)
        self.end_date = datetime(2024, 3, 31)
        
        # 设置基础参数
        self.settlement_cycles = [7, 15, 30, 45]  # 结算周期（天）
        self.bad_debt_rates = [0.01, 0.02, 0.03, 0.05]  # 坏账率
        self.delay_payment_probs = [0.1, 0.2, 0.3]  # 延迟支付概率
        
        # 季节性因素
        self.seasonal_factors = {
            1: 0.8,   # 1月（淡季）
            2: 0.7,   # 2月（春节）
            3: 0.9,   # 3月
            4: 1.0,   # 4月
            5: 1.1,   # 5月（五一）
            6: 1.0,   # 6月
            7: 1.2,   # 7月（暑期）
            8: 1.2,   # 8月（暑期）
            9: 1.1,   # 9月
            10: 1.3,  # 10月（国庆）
            11: 1.2,  # 11月（双11）
            12: 1.4   # 12月（年终）
        }
        
    def generate_daily_transactions(self, n_merchants=100):
        """
        生成每日交易数据
        
        Args:
            n_merchants (int): 商户数量
            
        Returns:
            pd.DataFrame: 包含每日交易数据的DataFrame
        """
        # 生成日期范围
        date_range = pd.date_range(self.start_date, self.end_date, freq='D')
        
        # 生成商户基础信息
        merchant_ids = [f'M{i:04d}' for i in range(n_merchants)]
        merchant_types = np.random.choice(['餐饮', '零售', '服务'], size=n_merchants)
        merchant_sizes = np.random.choice(['小型', '中型', '大型'], size=n_merchants)
        
        # 为每个商户生成交易数据
        data = []
        for merchant_id, m_type, m_size in zip(merchant_ids, merchant_types, merchant_sizes):
            # 设置商户特定参数
            base_amount = np.random.uniform(
                low={'小型': 1000, '中型': 5000, '大型': 20000}[m_size],
                high={'小型': 5000, '中型': 20000, '大型': 100000}[m_size]
            )
            
            settlement_cycle = int(np.random.choice(self.settlement_cycles))  # 转换为Python int
            bad_debt_rate = float(np.random.choice(self.bad_debt_rates))  # 转换为Python float
            
            for date in date_range:
                # 应用季节性因素
                seasonal_factor = self.seasonal_factors[date.month]
                
                # 生成基础交易金额
                amount = base_amount * seasonal_factor * (1 + np.random.normal(0, 0.1))
                
                # 添加随机波动
                if np.random.random() < 0.2:  # 20%概率发生较大波动
                    amount *= np.random.uniform(0.5, 1.5)
                
                # 生成是否延迟支付
                delay_days = 0
                if np.random.random() < float(np.random.choice(self.delay_payment_probs)):  # 转换为Python float
                    delay_days = int(np.random.randint(1, 15))  # 转换为Python int
                
                # 计算预期收款日期
                expected_collection_date = date + timedelta(days=settlement_cycle)
                actual_collection_date = expected_collection_date + timedelta(days=delay_days)
                
                # 计算是否坏账
                is_bad_debt = bool(np.random.random() < bad_debt_rate)  # 转换为Python bool
                
                data.append({
                    'date': date,
                    'merchant_id': merchant_id,
                    'merchant_type': m_type,
                    'merchant_size': m_size,
                    'transaction_amount': round(float(amount), 2),  # 转换为Python float
                    'settlement_cycle': settlement_cycle,
                    'expected_collection_date': expected_collection_date,
                    'actual_collection_date': actual_collection_date,
                    'delay_days': delay_days,
                    'is_bad_debt': is_bad_debt,
                    'bad_debt_rate': bad_debt_rate
                })
        
        # 转换为DataFrame
        df = pd.DataFrame(data)
        
        # 添加实际收款金额
        df['collected_amount'] = df.apply(
            lambda x: 0 if x['is_bad_debt'] else x['transaction_amount'],
            axis=1
        )
        
        return df
    
    def generate_all_data(self, n_merchants=100):
        """
        生成所有现金流预测相关数据
        
        Args:
            n_merchants (int): 商户数量
            
        Returns:
            dict: 包含所有生成数据的字典
        """
        # 生成交易数据
        transactions_df = self.generate_daily_transactions(n_merchants)
        
        # 生成每日现金流汇总
        daily_cashflow = transactions_df.groupby('date').agg({
            'transaction_amount': 'sum',
            'collected_amount': 'sum'
        }).reset_index()
        
        daily_cashflow['cashflow_gap'] = daily_cashflow['transaction_amount'] - daily_cashflow['collected_amount']
        
        # 生成商户维度汇总
        merchant_summary = transactions_df.groupby('merchant_id').agg({
            'transaction_amount': 'sum',
            'collected_amount': 'sum',
            'delay_days': 'mean',
            'is_bad_debt': 'sum'
        }).reset_index()
        
        merchant_summary['collection_rate'] = (
            merchant_summary['collected_amount'] / merchant_summary['transaction_amount']
        )
        
        return {
            'transactions': transactions_df,
            'daily_cashflow': daily_cashflow,
            'merchant_summary': merchant_summary
        } 
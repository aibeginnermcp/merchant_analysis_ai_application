"""
数据准备脚本 - 将原始订单数据转换为现金流预测所需的格式
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class DataPreparator:
    def __init__(self, input_dir, output_dir='data'):
        """
        初始化数据准备器
        
        Args:
            input_dir (str): 原始数据目录
            output_dir (str): 输出目录
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义支付方式的结算周期（天）
        self.payment_settlement = {
            'mobile_pay': 1,      # T+1
            'wechat': 1,         # T+1
            'alipay': 1,         # T+1
            'cash': 0,           # T+0
            'other': 7,          # T+7
            'corporate': 30      # 月结
        }
        
        # 定义平台的结算周期（天）
        self.platform_settlement = {
            'meituan': 7,        # T+7
            'eleme': 7,          # T+7
            'own_platform': 1    # T+1
        }
        
    def load_and_process_orders(self):
        """
        加载并处理订单数据
        """
        # 读取外卖订单
        delivery_orders = pd.read_csv(os.path.join(self.input_dir, 'delivery_orders.csv'))
        delivery_orders['merchant_type'] = 'online'
        delivery_orders['settlement_days'] = delivery_orders['platform'].map(self.platform_settlement)
        
        # 读取堂食订单
        dine_in_orders = pd.read_csv(os.path.join(self.input_dir, 'dine_in_orders.csv'))
        dine_in_orders['merchant_type'] = 'offline'
        dine_in_orders['settlement_days'] = dine_in_orders['payment_method'].map(self.payment_settlement)
        
        # 统一字段
        delivery_cols = ['order_time', 'total_amount', 'merchant_type', 'settlement_days']
        dine_in_cols = ['order_time', 'total_amount', 'merchant_type', 'settlement_days']
        
        # 合并订单
        all_orders = pd.concat([
            delivery_orders[delivery_cols],
            dine_in_orders[dine_in_cols]
        ])
        
        # 转换日期格式
        all_orders['order_time'] = pd.to_datetime(all_orders['order_time'])
        all_orders['date'] = all_orders['order_time'].dt.date
        
        return all_orders
    
    def generate_accounts_receivable(self, orders_df):
        """
        生成应收账款数据
        
        Args:
            orders_df (pd.DataFrame): 订单数据
        """
        # 按日期和商户类型汇总订单金额
        daily_orders = orders_df.groupby(['date', 'merchant_type', 'settlement_days'])['total_amount'].sum().reset_index()
        
        # 生成应收账款记录
        receivables = []
        for _, row in daily_orders.iterrows():
            # 应收账款到期日
            due_date = pd.to_datetime(row['date']) + timedelta(days=row['settlement_days'])
            
            # 添加一些随机的坏账和延迟支付
            bad_debt_rate = np.random.uniform(0, 0.02)  # 0-2%的坏账率
            delay_days = np.random.choice([0, 7, 15, 30], p=[0.8, 0.1, 0.07, 0.03])  # 80%准时，20%延迟
            
            receivables.append({
                'date': row['date'],
                'merchant_type': row['merchant_type'],
                'amount': row['total_amount'],
                'due_date': due_date.date(),
                'actual_payment_date': (due_date + timedelta(days=delay_days)).date(),
                'bad_debt_amount': row['total_amount'] * bad_debt_rate
            })
        
        receivables_df = pd.DataFrame(receivables)
        return receivables_df
    
    def add_seasonal_factors(self, df):
        """
        添加季节性因素
        
        Args:
            df (pd.DataFrame): 应收账款数据
        """
        # 将日期转换为datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # 添加季节性波动
        df['month'] = df['date'].dt.month
        seasonal_factors = {
            1: 0.8,   # 1月（春节前）
            2: 1.2,   # 2月（春节）
            3: 0.9,   # 3月
            4: 1.0,   # 4月
            5: 1.1,   # 5月（五一）
            6: 1.0,   # 6月
            7: 1.2,   # 7月（暑假）
            8: 1.2,   # 8月（暑假）
            9: 1.0,   # 9月
            10: 1.1,  # 10月（国庆）
            11: 0.9,  # 11月
            12: 1.1   # 12月（元旦）
        }
        
        df['seasonal_factor'] = df['month'].map(seasonal_factors)
        df['amount'] = df['amount'] * df['seasonal_factor']
        
        return df.drop(['month', 'seasonal_factor'], axis=1)
    
    def prepare_data(self):
        """
        准备现金流预测所需的数据
        """
        # 加载和处理订单数据
        orders_df = self.load_and_process_orders()
        
        # 生成应收账款数据
        receivables_df = self.generate_accounts_receivable(orders_df)
        
        # 添加季节性因素
        receivables_df = self.add_seasonal_factors(receivables_df)
        
        # 保存处理后的数据
        output_file = os.path.join(self.output_dir, 'accounts_receivable.csv')
        receivables_df.to_csv(output_file, index=False)
        
        print(f"数据处理完成，已保存到：{output_file}")
        return receivables_df

if __name__ == '__main__':
    # 设置输入输出路径
    input_dir = "/Users/chris/Documents/学习/AI/cursor/智能商户经营分析报表生成器/生成行业模拟数据/output"
    output_dir = "data"
    
    # 准备数据
    preparator = DataPreparator(input_dir, output_dir)
    receivables_df = preparator.prepare_data()
    
    # 打印数据统计信息
    print("\n数据统计信息：")
    print(f"总记录数：{len(receivables_df)}")
    print("\n按商户类型统计：")
    print(receivables_df.groupby('merchant_type')['amount'].agg(['count', 'sum', 'mean'])) 
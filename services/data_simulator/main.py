"""
智能商户经营分析报表数据生成器主程序
"""

import os
import pandas as pd
from datetime import datetime
from src.generators.restaurant_generator import RestaurantGenerator
from src.generators.electronics_generator import ElectronicsGenerator
from src.generators.beauty_generator import BeautyGenerator
from src.generators.fashion_ecommerce_generator import FashionEcommerceGenerator
from src.generators.cost_data_generator import CostDataGenerator
from src.generators.cashflow_generator import CashFlowGenerator

def create_output_dirs():
    """创建输出目录"""
    dirs = ['output', 'reports']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

def save_data(data_dict: dict, industry_type: str):
    """
    保存生成的数据到CSV文件
    
    Args:
        data_dict (dict): 包含所有数据表的字典
        industry_type (str): 行业类型
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for table_name, data in data_dict.items():
        if isinstance(data, pd.DataFrame):
            # 如果是DataFrame，直接保存
            filename = f'output/{industry_type}_{table_name}_{timestamp}.csv'
            data.to_csv(filename, index=False, encoding='utf-8')
            print(f"数据已保存到: {filename}")
            generate_data_report(data, table_name, industry_type, timestamp)
        elif isinstance(data, dict):
            # 如果是字典，递归保存其中的DataFrame
            for sub_table_name, sub_data in data.items():
                if isinstance(sub_data, pd.DataFrame):
                    filename = f'output/{industry_type}_{table_name}_{sub_table_name}_{timestamp}.csv'
                    sub_data.to_csv(filename, index=False, encoding='utf-8')
                    print(f"数据已保存到: {filename}")
                    generate_data_report(sub_data, f"{table_name}_{sub_table_name}", industry_type, timestamp)

def generate_data_report(df: pd.DataFrame, table_name: str, industry_type: str, timestamp: str):
    """
    生成数据统计报告
    
    Args:
        df (pd.DataFrame): 数据表
        table_name (str): 表名
        industry_type (str): 行业类型
        timestamp (str): 时间戳
    """
    report_file = f'reports/{industry_type}_{table_name}_report_{timestamp}.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"=== {industry_type} - {table_name} 数据统计报告 ===\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 基础统计信息
        f.write("1. 基础统计信息\n")
        f.write(f"总记录数: {len(df)}\n")
        f.write(f"字段数: {len(df.columns)}\n")
        f.write(f"字段列表: {', '.join(df.columns)}\n\n")
        
        # 数值字段统计
        f.write("2. 数值字段统计\n")
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            f.write(f"\n{col}字段统计:\n")
            f.write(f"最小值: {df[col].min()}\n")
            f.write(f"最大值: {df[col].max()}\n")
            f.write(f"平均值: {df[col].mean():.2f}\n")
            f.write(f"中位数: {df[col].median()}\n")
            
        # 分类字段统计
        f.write("\n3. 分类字段统计\n")
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            f.write(f"\n{col}字段值分布:\n")
            value_counts = df[col].value_counts()
            for value, count in value_counts.items():
                f.write(f"{value}: {count} ({count/len(df)*100:.2f}%)\n")
        
        # 时间字段分析
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0:
            f.write("\n4. 时间字段分析\n")
            for col in datetime_cols:
                f.write(f"\n{col}字段统计:\n")
                f.write(f"最早时间: {df[col].min()}\n")
                f.write(f"最晚时间: {df[col].max()}\n")
                
        # 成本分析（如果存在成本字段）
        cost_cols = [col for col in df.columns if 'cost' in col.lower()]
        if cost_cols:
            f.write("\n5. 成本分析\n")
            for col in cost_cols:
                f.write(f"\n{col}统计:\n")
                f.write(f"总成本: {df[col].sum():.2f}\n")
                f.write(f"平均成本: {df[col].mean():.2f}\n")
                f.write(f"最高成本: {df[col].max():.2f}\n")
                f.write(f"最低成本: {df[col].min():.2f}\n")
                
                # 按品类统计（如果存在品类字段）
                if 'category' in df.columns:
                    f.write("\n按品类统计:\n")
                    category_stats = df.groupby('category')[col].agg(['mean', 'sum'])
                    for cat, stats in category_stats.iterrows():
                        f.write(f"{cat}:\n")
                        f.write(f"  平均成本: {stats['mean']:.2f}\n")
                        f.write(f"  总成本: {stats['sum']:.2f}\n")
                
        print(f"统计报告已生成: {report_file}")

def generate_cost_data():
    """生成成本数据"""
    print("\n开始生成成本数据...")
    cost_generator = CostDataGenerator()
    cost_data = cost_generator.generate_all_cost_data(n_samples=1000, add_anomalies=True)
    
    # 保存成本数据
    data_dict = {'cost_data': cost_data}
    save_data(data_dict, 'cost')
    
    return cost_data

def generate_cashflow_data():
    """生成现金流预测数据"""
    print("\n开始生成现金流预测数据...")
    cashflow_generator = CashFlowGenerator()
    cashflow_data = cashflow_generator.generate_all_data(n_merchants=100)
    
    # 保存现金流数据
    save_data(cashflow_data, 'cashflow')
    
    return cashflow_data

def filter_cashflow_data(cashflow_data: dict, merchant_type: str) -> dict:
    """
    根据商户类型筛选现金流数据
    
    Args:
        cashflow_data (dict): 原始现金流数据
        merchant_type (str): 商户类型
        
    Returns:
        dict: 筛选后的现金流数据
    """
    filtered_data = {}
    
    # 处理transactions数据
    if 'transactions' in cashflow_data:
        transactions = cashflow_data['transactions']
        if 'merchant_type' in transactions.columns:
            filtered_data['transactions'] = transactions[transactions['merchant_type'] == merchant_type]
    
    # 处理daily_cashflow数据
    if 'daily_cashflow' in cashflow_data:
        daily_cashflow = cashflow_data['daily_cashflow']
        merchant_transactions = filtered_data.get('transactions')
        if merchant_transactions is not None:
            # 按日期汇总筛选后的交易数据
            filtered_daily = merchant_transactions.groupby('date').agg({
                'transaction_amount': 'sum',
                'collected_amount': 'sum'
            }).reset_index()
            filtered_daily['cashflow_gap'] = filtered_daily['transaction_amount'] - filtered_daily['collected_amount']
            filtered_data['daily_cashflow'] = filtered_daily
    
    # 处理merchant_summary数据
    if 'merchant_summary' in cashflow_data:
        merchant_summary = cashflow_data['merchant_summary']
        merchant_transactions = filtered_data.get('transactions')
        if merchant_transactions is not None:
            # 按商户汇总筛选后的交易数据
            filtered_summary = merchant_transactions.groupby('merchant_id').agg({
                'transaction_amount': 'sum',
                'collected_amount': 'sum',
                'delay_days': 'mean',
                'is_bad_debt': 'sum'
            }).reset_index()
            filtered_summary['collection_rate'] = (
                filtered_summary['collected_amount'] / filtered_summary['transaction_amount']
            )
            filtered_data['merchant_summary'] = filtered_summary
    
    return filtered_data

def main():
    """主程序入口"""
    print("=== 智能商户经营分析报表数据生成器 ===")
    
    # 创建输出目录
    create_output_dirs()
    
    # 生成现金流预测数据
    cashflow_data = generate_cashflow_data()
    
    # 生成成本数据
    cost_data = generate_cost_data()
    
    # 生成餐饮行业数据
    print("\n开始生成餐饮行业数据...")
    restaurant_generator = RestaurantGenerator()
    restaurant_data = restaurant_generator.generate_all_data()
    # 添加成本数据
    restaurant_data['cost_data'] = cost_data[cost_data['category'] == '食品']
    # 添加现金流数据
    restaurant_data['cashflow_data'] = filter_cashflow_data(cashflow_data, '餐饮')
    save_data(restaurant_data, 'restaurant')
    
    # 生成3C数码行业数据
    print("\n开始生成3C数码行业数据...")
    electronics_generator = ElectronicsGenerator()
    electronics_data = electronics_generator.generate_all_data()
    # 添加成本数据
    electronics_data['cost_data'] = cost_data[cost_data['category'] == '3C']
    # 添加现金流数据
    electronics_data['cashflow_data'] = filter_cashflow_data(cashflow_data, '零售')
    save_data(electronics_data, 'electronics')
    
    # 生成美妆个护行业数据
    print("\n开始生成美妆个护行业数据...")
    beauty_generator = BeautyGenerator()
    beauty_data = beauty_generator.generate_all_data()
    # 添加现金流数据
    beauty_data['cashflow_data'] = filter_cashflow_data(cashflow_data, '零售')
    save_data(beauty_data, 'beauty')
    
    # 生成服饰电商数据
    print("\n开始生成服饰电商数据...")
    fashion_generator = FashionEcommerceGenerator()
    fashion_data = fashion_generator.generate_all_data()
    # 添加成本数据
    fashion_data['cost_data'] = cost_data[cost_data['category'] == '服饰']
    # 添加现金流数据
    fashion_data['cashflow_data'] = filter_cashflow_data(cashflow_data, '零售')
    save_data(fashion_data, 'fashion_ecommerce')
    
    print("\n所有行业数据生成完成！")

if __name__ == "__main__":
    main() 
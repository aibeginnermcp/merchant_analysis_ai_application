"""
餐饮行业数据生成示例脚本
展示如何使用RestaurantGenerator生成模拟数据并进行简单分析
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import sys

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

from src.generators.restaurant_generator import RestaurantGenerator

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def generate_data(seed=42):
    """生成餐饮行业模拟数据"""
    logger = logging.getLogger(__name__)
    logger.info("开始生成餐饮行业模拟数据...")
    
    # 初始化生成器
    generator = RestaurantGenerator(seed=seed)
    
    # 生成所有数据
    data = generator.generate_all_data()
    
    logger.info("数据生成完成")
    return data

def save_data(data, output_dir='output'):
    """保存生成的数据到CSV文件"""
    logger = logging.getLogger(__name__)
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存各个数据表
    for name, df in data.items():
        file_path = output_path / f"{name}.csv"
        df.to_csv(file_path, index=False, encoding='utf-8')
        logger.info(f"已保存{name}数据到{file_path}")

def analyze_data(data):
    """对生成的数据进行简单分析"""
    logger = logging.getLogger(__name__)
    logger.info("开始分析数据...")
    
    # 1. 分析顾客分布
    customer_df = data['customer_base']
    print("\n=== 顾客分布分析 ===")
    print("\n城市分布：")
    print(customer_df['city_tier'].value_counts(normalize=True))
    print("\n年龄分布：")
    print(customer_df['age_group'].value_counts(normalize=True))
    print("\n会员比例：")
    print(customer_df['customer_type'].value_counts(normalize=True))
    
    # 2. 分析订单数据
    dine_in_df = data['dine_in_orders']
    delivery_df = data['delivery_orders']
    
    print("\n=== 订单分析 ===")
    print("\n堂食订单数量：", len(dine_in_df))
    print("外卖订单数量：", len(delivery_df))
    print("\n堂食订单平均金额：", dine_in_df['total_amount'].mean())
    print("外卖订单平均金额：", delivery_df['total_amount'].mean())
    
    # 3. 分析服务质量
    quality_df = data['service_quality']
    print("\n=== 服务质量分析 ===")
    print("\n评分分布：")
    print(quality_df['overall_score'].value_counts(normalize=True).sort_index())
    print("\n投诉率：", (quality_df['has_complaint']==True).mean())
    
    # 4. 可视化分析
    create_visualizations(data)
    
    logger.info("数据分析完成")

def create_visualizations(data):
    """创建数据可视化图表"""
    # 设置绘图风格
    plt.style.use('default')  # 使用默认样式
    
    # 1. 顾客年龄分布
    plt.figure(figsize=(10, 6))
    sns.countplot(data=data['customer_base'], x='age_group')
    plt.title('顾客年龄分布')
    plt.savefig('output/age_distribution.png')
    plt.close()
    
    # 2. 订单金额分布
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(data=data['dine_in_orders'], x='total_amount', bins=30)
    plt.title('堂食订单金额分布')
    plt.subplot(1, 2, 2)
    sns.histplot(data=data['delivery_orders'], x='total_amount', bins=30)
    plt.title('外卖订单金额分布')
    plt.tight_layout()
    plt.savefig('output/order_amount_distribution.png')
    plt.close()
    
    # 3. 评分分布
    plt.figure(figsize=(10, 6))
    sns.countplot(data=data['service_quality'], x='overall_score')
    plt.title('服务评分分布')
    plt.savefig('output/rating_distribution.png')
    plt.close()
    
    # 4. 时间序列分析
    daily_orders = pd.concat([
        data['dine_in_orders'].groupby(data['dine_in_orders']['order_time'].dt.date).size(),
        data['delivery_orders'].groupby(data['delivery_orders']['order_time'].dt.date).size()
    ], axis=1)
    daily_orders.columns = ['堂食', '外卖']
    
    plt.figure(figsize=(15, 6))
    daily_orders.plot()
    plt.title('每日订单量趋势')
    plt.xlabel('日期')
    plt.ylabel('订单数量')
    plt.legend()
    plt.savefig('output/daily_orders_trend.png')
    plt.close()

def main():
    """主函数"""
    # 设置日志
    logger = setup_logging()
    
    try:
        # 生成数据
        data = generate_data()
        
        # 保存数据
        save_data(data)
        
        # 分析数据
        analyze_data(data)
        
        logger.info("程序执行完成")
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 
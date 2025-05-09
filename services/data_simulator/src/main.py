"""
主程序文件
用于生成各行业的示例数据
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os

from generators.restaurant_generator import RestaurantGenerator
from generators.electronics_generator import ElectronicsGenerator
from generators.beauty_generator import BeautyGenerator

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def save_sample_data(data_dict: dict, industry: str):
    """保存示例数据到CSV文件
    
    Args:
        data_dict (dict): 数据字典
        industry (str): 行业名称
    """
    # 创建输出目录
    output_dir = f'output/{industry}_samples'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存每个数据表
    for table_name, df in data_dict.items():
        # 如果数据超过100条，只取前100条
        if len(df) > 100:
            df = df.head(100)
        
        # 保存到CSV文件
        output_file = f'{output_dir}/{table_name}.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        logging.info(f'已保存{table_name}示例数据到{output_file}')

def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 设置随机种子以保证结果可重现
    seed = 42
    
    # 1. 生成餐饮行业示例数据
    logger.info('开始生成餐饮行业示例数据...')
    restaurant_gen = RestaurantGenerator(seed=seed)
    restaurant_data = restaurant_gen.generate_all_data()
    save_sample_data(restaurant_data, 'restaurant')
    
    # 2. 生成3C数码行业示例数据
    logger.info('开始生成3C数码行业示例数据...')
    electronics_gen = ElectronicsGenerator(seed=seed)
    electronics_data = electronics_gen.generate_all_data()
    save_sample_data(electronics_data, 'electronics')
    
    # 3. 生成美妆个护行业示例数据
    logger.info('开始生成美妆个护行业示例数据...')
    beauty_gen = BeautyGenerator(seed=seed)
    beauty_data = beauty_gen.generate_all_data()
    save_sample_data(beauty_data, 'beauty')
    
    logger.info('所有示例数据生成完成！')

if __name__ == '__main__':
    main() 
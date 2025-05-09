"""
现金流预测示例脚本

展示如何使用数据处理、模型训练和可视化模块进行现金流预测
"""

import sys
import os
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime, timedelta
import json
import numpy as np

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data_processing import CashFlowDataProcessor
from src.model import CashFlowPredictor
from src.visualization import CashFlowVisualizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_mock_data(start_date: str, end_date: str, output_path: str):
    """
    生成模拟数据用于测试
    
    Args:
        start_date: 起始日期
        end_date: 结束日期
        output_path: 输出文件路径
    """
    # 生成日期范围
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 生成模拟数据
    data = []
    for date in dates:
        # 基础金额
        base_amount = 10000
        
        # 添加季节性
        seasonal = np.sin(date.dayofyear * 2 * np.pi / 365) * 2000
        
        # 添加趋势
        trend = date.dayofyear * 10
        
        # 添加随机波动
        noise = np.random.normal(0, 1000)
        
        amount = base_amount + seasonal + trend + noise
        
        data.append({
            'date': date,
            'amount': max(0, amount),  # 确保金额非负
            'merchant_type': 'online'
        })
    
    # 创建DataFrame并保存
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    logger.info(f"模拟数据已保存至 {output_path}")

def main():
    """主函数"""
    try:
        # 1. 加载配置
        config = load_config('config/config.json')
        
        # 2. 创建必要的目录
        for dir_path in ['data', 'models', 'reports']:
            os.makedirs(dir_path, exist_ok=True)
        
        # 3. 生成模拟数据（如果需要）
        if not os.path.exists('data/sample_data.csv'):
            generate_mock_data(
                start_date='2023-01-01',
                end_date='2024-02-29',
                output_path='data/sample_data.csv'
            )
        
        # 4. 初始化处理器、预测器和可视化器
        data_processor = CashFlowDataProcessor(config)
        predictor = CashFlowPredictor(config)
        visualizer = CashFlowVisualizer(config)
        
        # 5. 加载和处理数据
        raw_data = data_processor.load_data('data/sample_data.csv')
        processed_data = data_processor.process_data()
        
        # 6. 划分训练集和测试集
        split_date = processed_data.index[-30]  # 使用最后30天作为测试集
        train_data = processed_data.loc[:split_date, 'amount']
        test_data = processed_data.loc[split_date:, 'amount']
        
        # 7. 训练模型
        predictor.train(train_data)
        
        # 8. 进行预测
        predictions, confidence_intervals = predictor.predict(steps=30)
        
        # 9. 评估模型
        metrics = predictor.evaluate(test_data)
        
        # 10. 生成可视化和报告
        # 生成时间序列分解图
        decomp_fig = visualizer.plot_seasonal_decompose(train_data)
        
        # 生成预测结果图
        pred_fig = visualizer.plot_prediction(
            historical_data=train_data,
            predictions=predictions,
            confidence_intervals=confidence_intervals
        )
        
        # 生成残差分析图
        residuals = test_data - predictions
        resid_fig = visualizer.plot_residuals(residuals)
        
        # 保存图表
        figures = {
            'seasonal_decomposition': decomp_fig,
            'predictions': pred_fig,
            'residuals': resid_fig
        }
        visualizer.save_plots(figures, 'reports/figures')
        
        # 生成PDF报告
        visualizer.generate_report(
            historical_data=train_data,
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            metrics=metrics,
            output_path='reports/cash_flow_prediction_report.pdf'
        )
        
        # 11. 保存模型
        predictor.save_model('models/cash_flow_model.pkl')
        
        logger.info("现金流预测完成！报告已生成在 reports 目录下。")
        
    except Exception as e:
        logger.error(f"运行过程中出现错误: {str(e)}")
        raise

if __name__ == '__main__':
    main() 
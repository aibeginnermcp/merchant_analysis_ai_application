"""
现金流预测模型模块

实现基于ARIMA的现金流预测功能，包括模型训练、预测和评估
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging
from typing import Tuple, Dict, Optional
import json
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CashFlowPredictor:
    """
    现金流预测器
    
    使用ARIMA模型进行现金流预测，支持模型训练、预测和评估
    """
    
    def __init__(self, config: dict):
        """
        初始化预测器
        
        Args:
            config: 配置字典，包含模型参数
        """
        self.config = config
        self.model = None
        self.model_params = None
        self.is_stationary = False
        self.diff_order = 0
        
    def check_stationarity(self, data: pd.Series) -> Tuple[bool, float]:
        """
        检查时间序列的平稳性
        
        Args:
            data: 时间序列数据
            
        Returns:
            是否平稳及p值
        """
        result = adfuller(data)
        p_value = result[1]
        is_stationary = p_value < 0.05
        logger.info(f"ADF检验 p值: {p_value:.4f}, {'平稳' if is_stationary else '非平稳'}")
        return is_stationary, p_value
        
    def make_stationary(self, data: pd.Series) -> Tuple[pd.Series, int]:
        """
        通过差分使时间序列平稳化
        
        Args:
            data: 原始时间序列
            
        Returns:
            平稳化后的序列和差分阶数
        """
        diff_data = data.copy()
        diff_order = 0
        
        while True:
            is_stationary, _ = self.check_stationarity(diff_data)
            if is_stationary or diff_order >= 2:  # 最多进行2阶差分
                break
            diff_data = diff_data.diff().dropna()
            diff_order += 1
            
        logger.info(f"使用 {diff_order} 阶差分实现平稳化")
        return diff_data, diff_order
        
    def select_arima_params(self, data: pd.Series) -> Dict[str, int]:
        """
        自动选择ARIMA模型参数
        
        Args:
            data: 训练数据
            
        Returns:
            最优参数组合
        """
        best_aic = float('inf')
        best_params = None
        
        # 定义参数搜索范围
        p_range = range(0, 3)
        d_range = [self.diff_order]  # 使用已确定的差分阶数
        q_range = range(0, 3)
        
        for p in p_range:
            for d in d_range:
                for q in q_range:
                    try:
                        model = ARIMA(data, order=(p, d, q))
                        results = model.fit()
                        if results.aic < best_aic:
                            best_aic = results.aic
                            best_params = (p, d, q)
                    except:
                        continue
        
        if best_params is None:
            logger.warning("参数选择失败，使用默认参数 (1,1,1)")
            best_params = (1, self.diff_order, 1)
        
        logger.info(f"选择的ARIMA参数: p={best_params[0]}, d={best_params[1]}, q={best_params[2]}")
        return {'p': best_params[0], 'd': best_params[1], 'q': best_params[2]}
        
    def train(self, data: pd.Series):
        """
        训练ARIMA模型
        
        Args:
            data: 训练数据
        """
        # 1. 检查并实现平稳性
        stationary_data, self.diff_order = self.make_stationary(data)
        self.is_stationary = True
        
        # 2. 选择模型参数
        self.model_params = self.select_arima_params(data)
        
        # 3. 训练模型
        try:
            self.model = ARIMA(
                data,
                order=(
                    self.model_params['p'],
                    self.model_params['d'],
                    self.model_params['q']
                )
            )
            self.model = self.model.fit()
            logger.info("模型训练完成")
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            raise
            
    def predict(self, steps: int = 30, return_conf_int: bool = True) -> Tuple[pd.Series, Optional[pd.DataFrame]]:
        """
        进行预测
        
        Args:
            steps: 预测步数
            return_conf_int: 是否返回置信区间
            
        Returns:
            预测结果和置信区间
        """
        if self.model is None:
            raise ValueError("请先训练模型")
            
        try:
            # 获取预测结果
            forecast = self.model.forecast(steps)
            
            if return_conf_int:
                # 获取预测置信区间
                pred_int = self.model.get_forecast(steps).conf_int()
                return forecast, pred_int
            else:
                return forecast, None
                
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            raise
            
    def evaluate(self, test_data: pd.Series) -> Dict[str, float]:
        """
        评估模型性能
        
        Args:
            test_data: 测试数据
            
        Returns:
            包含评估指标的字典
        """
        # 对测试集长度进行预测
        predictions, _ = self.predict(steps=len(test_data))
        
        # 计算评估指标
        mae = mean_absolute_error(test_data, predictions)
        rmse = np.sqrt(mean_squared_error(test_data, predictions))
        mape = np.mean(np.abs((test_data - predictions) / test_data)) * 100
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape
        }
        
        logger.info(f"模型评估结果: MAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape:.2f}%")
        return metrics
        
    def save_model(self, path: str):
        """
        保存模型
        
        Args:
            path: 保存路径
        """
        if self.model is None:
            raise ValueError("没有训练好的模型可保存")
            
        # 创建保存目录
        save_dir = Path(path).parent
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存模型
        self.model.save(path)
        
        # 保存模型参数和配置
        config_path = Path(path).with_suffix('.json')
        config = {
            'model_params': self.model_params,
            'diff_order': self.diff_order,
            'is_stationary': self.is_stationary,
            'config': self.config
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            
        logger.info(f"模型已保存至 {path}")
        
    @classmethod
    def load_model(cls, path: str) -> 'CashFlowPredictor':
        """
        加载已保存的模型
        
        Args:
            path: 模型文件路径
            
        Returns:
            加载好的预测器实例
        """
        # 加载配置
        config_path = Path(path).with_suffix('.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        # 创建预测器实例
        predictor = cls(config['config'])
        predictor.model_params = config['model_params']
        predictor.diff_order = config['diff_order']
        predictor.is_stationary = config['is_stationary']
        
        # 加载模型
        predictor.model = ARIMA.load(path)
        
        logger.info(f"模型已从 {path} 加载")
        return predictor 
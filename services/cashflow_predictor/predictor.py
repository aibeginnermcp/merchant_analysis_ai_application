"""
现金流预测服务的预测引擎，实现多种时间序列预测算法
"""
import uuid
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from abc import ABC, abstractmethod
import statsmodels.api as sm
import warnings

# 忽略statsmodels警告
warnings.filterwarnings("ignore", category=sm.tsa.statespace.initialization.Initialization)

try:
    # 尝试导入Prophet库，如果不可用则跳过
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    
try:
    # 尝试导入TensorFlow库，如果不可用则跳过
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    from sklearn.preprocessing import MinMaxScaler
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

from services.cashflow_predictor.models import (
    TimeSeriesData,
    CashflowData,
    PredictionMethod,
    PredictionConfig,
    PredictionPoint,
    ConfidenceInterval,
    PredictionResult,
    PerformanceMetrics,
    TimeRange
)

logger = logging.getLogger("cashflow_predictor.predictor")

class BasePredictor(ABC):
    """预测器基类"""
    
    def __init__(self, config: PredictionConfig):
        """
        初始化预测器
        
        Args:
            config: 预测配置
        """
        self.config = config
        self.model = None
        
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> None:
        """
        训练模型
        
        Args:
            data: 时间序列数据，包含 'ds' 和 'y' 列
        """
        pass
    
    @abstractmethod
    def predict(self, periods: int) -> pd.DataFrame:
        """
        生成预测
        
        Args:
            periods: 预测天数
            
        Returns:
            预测结果DataFrame，包含 'ds', 'yhat', 'yhat_lower', 'yhat_upper' 列
        """
        pass
    
    def calculate_metrics(self, true_values: pd.DataFrame, predictions: pd.DataFrame) -> PerformanceMetrics:
        """
        计算模型性能指标
        
        Args:
            true_values: 实际值
            predictions: 预测值
            
        Returns:
            性能指标
        """
        # 合并数据进行比较
        merged = pd.merge(true_values, predictions, on='ds')
        
        # 计算各项指标
        y_true = merged['y'].values
        y_pred = merged['yhat'].values
        
        # 平均绝对百分比误差 (MAPE)
        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(1e-10, np.abs(y_true)))) * 100
        
        # 均方根误差 (RMSE)
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        
        # 平均绝对误差 (MAE)
        mae = np.mean(np.abs(y_true - y_pred))
        
        # R方值 (R²)
        ss_total = np.sum((y_true - np.mean(y_true)) ** 2)
        ss_res = np.sum((y_true - y_pred) ** 2)
        r2 = 1 - (ss_res / (ss_total + 1e-10))
        
        return PerformanceMetrics(
            mape=float(mape),
            rmse=float(rmse),
            mae=float(mae),
            r2=float(r2)
        )


class ARIMAPredictor(BasePredictor):
    """ARIMA预测器"""
    
    def __init__(self, config: PredictionConfig):
        super().__init__(config)
        # 从配置中提取ARIMA参数，或使用默认值
        hyperparams = config.hyperparameters or {}
        self.order = hyperparams.get('order', (1, 1, 1))
        self.seasonal_order = hyperparams.get('seasonal_order', (0, 0, 0, 0))
        self.enforce_stationarity = hyperparams.get('enforce_stationarity', False)
        
    def fit(self, data: pd.DataFrame) -> None:
        """
        训练ARIMA模型
        
        Args:
            data: 时间序列数据，包含 'ds' 和 'y' 列
        """
        # 将数据转换为时间序列
        self.data = data.copy()
        self.data.set_index('ds', inplace=True)
        
        # 使用statsmodels的SARIMAX
        self.model = sm.tsa.statespace.SARIMAX(
            self.data['y'],
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=self.enforce_stationarity
        )
        
        # 拟合模型
        logger.info(f"Training ARIMA model with order={self.order}, seasonal_order={self.seasonal_order}")
        self.result = self.model.fit(disp=False)
        logger.info("ARIMA model training completed")
        
    def predict(self, periods: int) -> pd.DataFrame:
        """
        生成ARIMA预测
        
        Args:
            periods: 预测天数
            
        Returns:
            预测结果DataFrame
        """
        if self.result is None:
            raise ValueError("Model must be fit before predicting")
        
        # 进行预测
        logger.info(f"Generating ARIMA predictions for {periods} periods")
        forecast = self.result.get_forecast(steps=periods)
        pred_mean = forecast.predicted_mean
        pred_ci = forecast.conf_int(alpha=1-self.config.confidence_level)
        
        # 创建日期索引
        last_date = self.data.index[-1]
        date_range = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq='D')
        
        # 构建结果DataFrame
        predictions = pd.DataFrame({
            'ds': date_range,
            'yhat': pred_mean.values,
            'yhat_lower': pred_ci.iloc[:, 0].values,
            'yhat_upper': pred_ci.iloc[:, 1].values
        })
        
        return predictions


class ProphetPredictor(BasePredictor):
    """Facebook Prophet预测器"""
    
    def __init__(self, config: PredictionConfig):
        super().__init__(config)
        
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet库未安装，无法使用ProphetPredictor")
        
        # 从配置中提取Prophet参数，或使用默认值
        hyperparams = config.hyperparameters or {}
        self.growth = hyperparams.get('growth', 'linear')
        self.changepoints = hyperparams.get('changepoints', None)
        self.seasonality_mode = config.seasonality_mode
        self.yearly_seasonality = hyperparams.get('yearly_seasonality', 'auto')
        self.weekly_seasonality = hyperparams.get('weekly_seasonality', 'auto')
        self.daily_seasonality = hyperparams.get('daily_seasonality', 'auto')
        
    def fit(self, data: pd.DataFrame) -> None:
        """
        训练Prophet模型
        
        Args:
            data: 时间序列数据，包含 'ds' 和 'y' 列
        """
        # 创建Prophet实例
        self.model = Prophet(
            growth=self.growth,
            changepoints=self.changepoints,
            seasonality_mode=self.seasonality_mode,
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=self.weekly_seasonality,
            daily_seasonality=self.daily_seasonality
        )
        
        # 添加中国节假日如果配置指定
        if self.config.include_holidays:
            self.model.add_country_holidays(country_name='CN')
        
        # 拟合模型
        logger.info("Training Prophet model")
        self.model.fit(data)
        logger.info("Prophet model training completed")
        
    def predict(self, periods: int) -> pd.DataFrame:
        """
        生成Prophet预测
        
        Args:
            periods: 预测天数
            
        Returns:
            预测结果DataFrame
        """
        if self.model is None:
            raise ValueError("Model must be fit before predicting")
        
        # 创建未来日期DataFrame
        future = self.model.make_future_dataframe(periods=periods)
        
        # 进行预测
        logger.info(f"Generating Prophet predictions for {periods} periods")
        forecast = self.model.predict(future)
        
        # 截取预测部分
        predictions = forecast.iloc[-periods:][['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        
        return predictions


class LSTMPredictor(BasePredictor):
    """LSTM神经网络预测器"""
    
    def __init__(self, config: PredictionConfig):
        super().__init__(config)
        
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow库未安装，无法使用LSTMPredictor")
        
        # 从配置中提取LSTM参数，或使用默认值
        hyperparams = config.hyperparameters or {}
        self.n_steps = hyperparams.get('n_steps', 10)  # 时间窗口大小
        self.n_features = 1  # 特征数量
        self.n_units = hyperparams.get('n_units', 50)  # LSTM单元数
        self.dropout = hyperparams.get('dropout', 0.2)  # Dropout率
        self.epochs = hyperparams.get('epochs', 100)  # 训练轮数
        self.batch_size = hyperparams.get('batch_size', 32)  # 批次大小
        self.validation_split = hyperparams.get('validation_split', 0.2)  # 验证集比例
        
        # 用于数据缩放
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        创建LSTM训练序列
        
        Args:
            data: 归一化后的时间序列数据
            
        Returns:
            X: 特征序列
            y: 目标值
        """
        X, y = [], []
        for i in range(len(data) - self.n_steps):
            X.append(data[i:(i + self.n_steps), 0])
            y.append(data[i + self.n_steps, 0])
        return np.array(X), np.array(y)
    
    def fit(self, data: pd.DataFrame) -> None:
        """
        训练LSTM模型
        
        Args:
            data: 时间序列数据，包含 'ds' 和 'y' 列
        """
        # 存储原始数据
        self.data = data.copy()
        
        # 提取并缩放数据
        values = data['y'].values.reshape(-1, 1)
        scaled_values = self.scaler.fit_transform(values)
        
        # 创建训练序列
        X, y = self._create_sequences(scaled_values)
        X = X.reshape((X.shape[0], X.shape[1], self.n_features))
        
        # 构建LSTM模型
        self.model = Sequential()
        self.model.add(LSTM(self.n_units, return_sequences=True, input_shape=(self.n_steps, self.n_features)))
        self.model.add(Dropout(self.dropout))
        self.model.add(LSTM(self.n_units))
        self.model.add(Dropout(self.dropout))
        self.model.add(Dense(1))
        
        # 编译模型
        self.model.compile(optimizer='adam', loss='mse')
        
        # 早停策略
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # 训练模型
        logger.info("Training LSTM model")
        self.model.fit(
            X, y,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=self.validation_split,
            callbacks=[early_stopping],
            verbose=0
        )
        logger.info("LSTM model training completed")
        
    def predict(self, periods: int) -> pd.DataFrame:
        """
        生成LSTM预测
        
        Args:
            periods: 预测天数
            
        Returns:
            预测结果DataFrame
        """
        if self.model is None:
            raise ValueError("Model must be fit before predicting")
        
        # 准备初始输入序列
        values = self.data['y'].values.reshape(-1, 1)
        scaled_values = self.scaler.transform(values)
        
        # 最后n_steps天的数据作为初始输入
        input_seq = scaled_values[-self.n_steps:].reshape(1, self.n_steps, 1)
        
        # 预测未来periods天
        logger.info(f"Generating LSTM predictions for {periods} periods")
        predictions = []
        for _ in range(periods):
            # 预测下一个时间点
            next_pred = self.model.predict(input_seq, verbose=0)[0][0]
            predictions.append(next_pred)
            
            # 更新输入序列
            input_seq = np.append(input_seq[:, 1:, :], [[next_pred]], axis=1)
        
        # 反向转换预测结果
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        
        # 计算置信区间（使用前向传播多次预测+随机噪声生成多个路径）
        num_simulations = 100
        mc_predictions = []
        
        for _ in range(num_simulations):
            input_seq = scaled_values[-self.n_steps:].reshape(1, self.n_steps, 1)
            sim_predictions = []
            
            for _ in range(periods):
                # 预测下一个时间点
                next_pred = self.model.predict(input_seq, verbose=0)[0][0]
                # 添加随机噪声模拟波动
                noise_level = 0.05  # 5%噪声水平
                next_pred_noisy = next_pred * (1 + np.random.normal(0, noise_level))
                sim_predictions.append(next_pred_noisy)
                
                # 更新输入序列
                input_seq = np.append(input_seq[:, 1:, :], [[next_pred_noisy]], axis=1)
            
            mc_predictions.append(sim_predictions)
        
        # 计算置信区间
        mc_predictions = np.array(mc_predictions)
        lower_percentile = (1 - self.config.confidence_level) / 2 * 100
        upper_percentile = 100 - lower_percentile
        
        lower_bounds = np.percentile(mc_predictions, lower_percentile, axis=0).reshape(-1, 1)
        upper_bounds = np.percentile(mc_predictions, upper_percentile, axis=0).reshape(-1, 1)
        
        lower_bounds = self.scaler.inverse_transform(lower_bounds)
        upper_bounds = self.scaler.inverse_transform(upper_bounds)
        
        # 创建日期索引
        last_date = self.data['ds'].iloc[-1]
        date_range = pd.date_range(start=pd.to_datetime(last_date) + timedelta(days=1), periods=periods, freq='D')
        
        # 构建结果DataFrame
        pred_df = pd.DataFrame({
            'ds': date_range,
            'yhat': predictions.flatten(),
            'yhat_lower': lower_bounds.flatten(),
            'yhat_upper': upper_bounds.flatten()
        })
        
        return pred_df


class EnsemblePredictor(BasePredictor):
    """集成预测器"""
    
    def __init__(self, config: PredictionConfig):
        super().__init__(config)
        
        # 检查可用的模型
        self.available_models = ['arima']
        
        if PROPHET_AVAILABLE:
            self.available_models.append('prophet')
            
        if TF_AVAILABLE:
            self.available_models.append('lstm')
            
        hyperparams = config.hyperparameters or {}
        self.models_to_use = hyperparams.get('models', self.available_models)
        self.weights = hyperparams.get('weights', None)
        
        # 创建各个子模型的配置
        self.model_configs = {
            'arima': PredictionConfig(
                method=PredictionMethod.ARIMA,
                prediction_days=config.prediction_days,
                confidence_level=config.confidence_level,
                include_holidays=config.include_holidays,
                use_weekday_patterns=config.use_weekday_patterns,
                seasonality_mode=config.seasonality_mode,
                hyperparameters=hyperparams.get('arima_params', None)
            ),
            'prophet': PredictionConfig(
                method=PredictionMethod.PROPHET,
                prediction_days=config.prediction_days,
                confidence_level=config.confidence_level,
                include_holidays=config.include_holidays,
                use_weekday_patterns=config.use_weekday_patterns,
                seasonality_mode=config.seasonality_mode,
                hyperparameters=hyperparams.get('prophet_params', None)
            ),
            'lstm': PredictionConfig(
                method=PredictionMethod.LSTM,
                prediction_days=config.prediction_days,
                confidence_level=config.confidence_level,
                include_holidays=config.include_holidays,
                use_weekday_patterns=config.use_weekday_patterns,
                seasonality_mode=config.seasonality_mode,
                hyperparameters=hyperparams.get('lstm_params', None)
            )
        }
        
        # 过滤掉不可用的模型
        self.models_to_use = [m for m in self.models_to_use if m in self.available_models]
        
        if not self.models_to_use:
            raise ValueError("No valid prediction models available")
            
        # 如果没有指定权重，使用平均权重
        if self.weights is None:
            self.weights = {model: 1.0 / len(self.models_to_use) for model in self.models_to_use}
        else:
            # 确保权重归一化
            weight_sum = sum(self.weights.values())
            self.weights = {k: v / weight_sum for k, v in self.weights.items()}
            
        # 初始化预测器
        self.predictors = {}
        for model_name in self.models_to_use:
            if model_name == 'arima':
                self.predictors[model_name] = ARIMAPredictor(self.model_configs[model_name])
            elif model_name == 'prophet' and PROPHET_AVAILABLE:
                self.predictors[model_name] = ProphetPredictor(self.model_configs[model_name])
            elif model_name == 'lstm' and TF_AVAILABLE:
                self.predictors[model_name] = LSTMPredictor(self.model_configs[model_name])
                
    def fit(self, data: pd.DataFrame) -> None:
        """
        训练所有子模型
        
        Args:
            data: 时间序列数据，包含 'ds' 和 'y' 列
        """
        self.data = data.copy()
        
        for model_name, predictor in self.predictors.items():
            logger.info(f"Training {model_name} model")
            try:
                predictor.fit(data)
            except Exception as e:
                logger.error(f"Error training {model_name} model: {e}")
                # 移除失败的模型
                self.predictors.pop(model_name)
                self.models_to_use.remove(model_name)
                
        # 重新计算权重
        if self.predictors:
            weight_sum = sum(self.weights[m] for m in self.models_to_use)
            self.weights = {k: self.weights[k] / weight_sum for k in self.models_to_use}
        else:
            raise ValueError("All models failed to train")
            
    def predict(self, periods: int) -> pd.DataFrame:
        """
        生成集成预测
        
        Args:
            periods: 预测天数
            
        Returns:
            预测结果DataFrame
        """
        if not self.predictors:
            raise ValueError("No trained models available")
            
        all_predictions = {}
        valid_weights = {}
        weight_sum = 0
        
        # 获取各个模型的预测
        for model_name, predictor in self.predictors.items():
            try:
                all_predictions[model_name] = predictor.predict(periods)
                valid_weights[model_name] = self.weights[model_name]
                weight_sum += self.weights[model_name]
            except Exception as e:
                logger.error(f"Error predicting with {model_name} model: {e}")
                
        if not all_predictions:
            raise ValueError("All models failed to generate predictions")
            
        # 重新归一化权重
        valid_weights = {k: v / weight_sum for k, v in valid_weights.items()}
        
        # 获取日期列作为基准
        date_range = list(all_predictions.values())[0]['ds']
        
        # 加权平均预测
        yhat = np.zeros(periods)
        yhat_lower = np.zeros(periods)
        yhat_upper = np.zeros(periods)
        
        for model_name, preds in all_predictions.items():
            weight = valid_weights[model_name]
            yhat += weight * preds['yhat'].values
            yhat_lower += weight * preds['yhat_lower'].values
            yhat_upper += weight * preds['yhat_upper'].values
            
        # 构建结果DataFrame
        ensemble_preds = pd.DataFrame({
            'ds': date_range,
            'yhat': yhat,
            'yhat_lower': yhat_lower,
            'yhat_upper': yhat_upper
        })
        
        return ensemble_preds


class PredictorFactory:
    """预测器工厂类"""
    
    @staticmethod
    def create_predictor(config: PredictionConfig) -> BasePredictor:
        """
        创建预测器实例
        
        Args:
            config: 预测配置
            
        Returns:
            预测器实例
        """
        method = config.method
        
        if method == PredictionMethod.ARIMA:
            return ARIMAPredictor(config)
        elif method == PredictionMethod.PROPHET:
            if not PROPHET_AVAILABLE:
                logger.warning("Prophet not available, falling back to ARIMA")
                return ARIMAPredictor(config)
            return ProphetPredictor(config)
        elif method == PredictionMethod.LSTM:
            if not TF_AVAILABLE:
                logger.warning("TensorFlow not available, falling back to ARIMA")
                return ARIMAPredictor(config)
            return LSTMPredictor(config)
        elif method == PredictionMethod.ENSEMBLE:
            return EnsemblePredictor(config)
        else:
            raise ValueError(f"Unknown prediction method: {method}")


class CashflowPredictor:
    """现金流预测类，封装整个预测流程"""
    
    def __init__(self):
        """初始化现金流预测器"""
        self.logger = logging.getLogger("cashflow_predictor")
        
    def prepare_data(self, cash_data: CashflowData) -> pd.DataFrame:
        """
        准备数据用于预测
        
        Args:
            cash_data: 现金流数据
            
        Returns:
            准备好的DataFrame
        """
        # 转换为DataFrame
        df = pd.DataFrame([{'ds': d.date, 'y': d.value} for d in cash_data.data])
        
        # 转换日期列
        df['ds'] = pd.to_datetime(df['ds'])
        
        # 按日期排序
        df = df.sort_values('ds')
        
        return df
        
    def generate_prediction(self, cash_data: CashflowData, config: PredictionConfig) -> PredictionResult:
        """
        生成现金流预测
        
        Args:
            cash_data: 现金流数据
            config: 预测配置
            
        Returns:
            预测结果
        """
        self.logger.info(f"Generating prediction for merchant {cash_data.merchant_id} using {config.method.value}")
        
        # 准备数据
        df = self.prepare_data(cash_data)
        
        # 创建预测器
        predictor = PredictorFactory.create_predictor(config)
        
        # 训练模型
        predictor.fit(df)
        
        # 生成预测
        periods = config.prediction_days
        predictions_df = predictor.predict(periods)
        
        # 计算性能指标（如果有测试集）
        metrics = None
        test_size = min(30, len(df) // 5)  # 使用最后20%的数据或最多30天作为测试集
        if test_size > 0:
            train_df = df.iloc[:-test_size]
            test_df = df.iloc[-test_size:]
            
            # 使用训练集拟合
            test_predictor = PredictorFactory.create_predictor(config)
            test_predictor.fit(train_df)
            
            # 预测测试集期间
            test_predictions = test_predictor.predict(test_size)
            
            # 计算指标
            metrics = predictor.calculate_metrics(test_df, test_predictions)
        
        # 构建预测点列表
        prediction_points = []
        for _, row in predictions_df.iterrows():
            prediction_points.append(
                PredictionPoint(
                    date=row['ds'].strftime('%Y-%m-%d'),
                    value=float(row['yhat']),
                    confidence_interval=ConfidenceInterval(
                        lower=float(row['yhat_lower']),
                        upper=float(row['yhat_upper'])
                    )
                )
            )
        
        # 构建预测时间范围
        prediction_start = predictions_df['ds'].min().strftime('%Y-%m-%d')
        prediction_end = predictions_df['ds'].max().strftime('%Y-%m-%d')
        prediction_range = TimeRange(start_date=prediction_start, end_date=prediction_end)
        
        # 构建结果
        result = PredictionResult(
            merchant_id=cash_data.merchant_id,
            time_range=cash_data.time_range,
            prediction_range=prediction_range,
            predictions=prediction_points,
            method=config.method,
            created_at=datetime.now(),
            metrics=metrics,
            metadata={
                "prediction_id": f"pred_{uuid.uuid4().hex[:8]}",
                "config": config.dict()
            }
        )
        
        return result 
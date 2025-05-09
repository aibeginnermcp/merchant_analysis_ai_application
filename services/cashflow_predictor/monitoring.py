"""
监控模块

负责服务监控和日志记录，包括：
- 性能指标收集
- 业务指标监控
- 日志记录
- 告警触发
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import structlog

# 配置结构化日志
logger = structlog.get_logger()

# 定义Prometheus指标
PREDICTION_REQUEST_COUNT = Counter(
    "cashflow_prediction_requests_total",
    "Total number of cashflow prediction requests",
    ["merchant_id", "granularity"]
)

PREDICTION_LATENCY = Histogram(
    "cashflow_prediction_latency_seconds",
    "Latency of cashflow prediction requests",
    ["merchant_id", "granularity"]
)

PREDICTION_ERROR_COUNT = Counter(
    "cashflow_prediction_errors_total",
    "Total number of cashflow prediction errors",
    ["merchant_id", "error_type"]
)

MODEL_PREDICTION_ACCURACY = Gauge(
    "cashflow_model_prediction_accuracy",
    "Accuracy of cashflow prediction model",
    ["merchant_id", "model_type"]
)

DATA_PROCESSING_TIME = Histogram(
    "cashflow_data_processing_time_seconds",
    "Time taken for data processing",
    ["operation"]
)

class MetricsCollector:
    """
    指标收集器
    
    收集和记录各类性能和业务指标
    """
    
    @staticmethod
    def record_prediction_request(
        merchant_id: str,
        granularity: str
    ) -> None:
        """记录预测请求"""
        PREDICTION_REQUEST_COUNT.labels(
            merchant_id=merchant_id,
            granularity=granularity
        ).inc()
        
    @staticmethod
    def record_prediction_latency(
        merchant_id: str,
        granularity: str,
        latency: float
    ) -> None:
        """记录预测延迟"""
        PREDICTION_LATENCY.labels(
            merchant_id=merchant_id,
            granularity=granularity
        ).observe(latency)
        
    @staticmethod
    def record_prediction_error(
        merchant_id: str,
        error_type: str
    ) -> None:
        """记录预测错误"""
        PREDICTION_ERROR_COUNT.labels(
            merchant_id=merchant_id,
            error_type=error_type
        ).inc()
        
    @staticmethod
    def update_model_accuracy(
        merchant_id: str,
        model_type: str,
        accuracy: float
    ) -> None:
        """更新模型准确率"""
        MODEL_PREDICTION_ACCURACY.labels(
            merchant_id=merchant_id,
            model_type=model_type
        ).set(accuracy)
        
    @staticmethod
    def record_processing_time(
        operation: str,
        duration: float
    ) -> None:
        """记录处理时间"""
        DATA_PROCESSING_TIME.labels(
            operation=operation
        ).observe(duration)

def log_execution_time(operation: str):
    """
    执行时间装饰器
    
    Args:
        operation: 操作名称
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                MetricsCollector.record_processing_time(
                    operation,
                    duration
                )
                logger.info(
                    "operation_completed",
                    operation=operation,
                    duration=duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "operation_failed",
                    operation=operation,
                    duration=duration,
                    error=str(e)
                )
                raise
        return wrapper
    return decorator

class BusinessMetricsCollector:
    """
    业务指标收集器
    
    收集和记录业务相关的指标
    """
    
    @staticmethod
    def record_prediction_accuracy(
        merchant_id: str,
        predicted: Dict[str, float],
        actual: Dict[str, float]
    ) -> None:
        """
        记录预测准确率
        
        Args:
            merchant_id: 商户ID
            predicted: 预测值
            actual: 实际值
        """
        # 计算MAPE (Mean Absolute Percentage Error)
        total_error = 0
        count = 0
        
        for date in predicted.keys():
            if date in actual:
                pred_value = predicted[date]
                act_value = actual[date]
                if act_value != 0:
                    error = abs(pred_value - act_value) / act_value
                    total_error += error
                    count += 1
                    
        if count > 0:
            mape = total_error / count
            accuracy = 1 - mape
            
            # 更新指标
            MetricsCollector.update_model_accuracy(
                merchant_id,
                "combined",
                accuracy
            )
            
            logger.info(
                "prediction_accuracy_recorded",
                merchant_id=merchant_id,
                accuracy=accuracy,
                sample_count=count
            )
            
    @staticmethod
    def record_risk_metrics(
        merchant_id: str,
        risk_assessment: Dict[str, Any]
    ) -> None:
        """
        记录风险指标
        
        Args:
            merchant_id: 商户ID
            risk_assessment: 风险评估结果
        """
        metrics = risk_assessment.get("risk_metrics", {})
        
        # 记录关键风险指标
        logger.info(
            "risk_metrics_recorded",
            merchant_id=merchant_id,
            negative_days_ratio=metrics.get("negative_days_ratio"),
            coefficient_of_variation=metrics.get("coefficient_of_variation"),
            risk_level=risk_assessment.get("overall_risk")
        )

class AlertManager:
    """
    告警管理器
    
    处理监控告警的触发和发送
    """
    
    @staticmethod
    def check_and_alert(
        merchant_id: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        检查并触发告警
        
        Args:
            merchant_id: 商户ID
            metrics: 监控指标
        """
        # 检查预测准确率
        accuracy = metrics.get("accuracy")
        if accuracy and accuracy < 0.7:
            logger.warning(
                "low_prediction_accuracy",
                merchant_id=merchant_id,
                accuracy=accuracy,
                threshold=0.7
            )
            
        # 检查处理时间
        processing_time = metrics.get("processing_time")
        if processing_time and processing_time > 10:
            logger.warning(
                "high_processing_time",
                merchant_id=merchant_id,
                processing_time=processing_time,
                threshold=10
            )
            
        # 检查错误率
        error_rate = metrics.get("error_rate")
        if error_rate and error_rate > 0.05:
            logger.error(
                "high_error_rate",
                merchant_id=merchant_id,
                error_rate=error_rate,
                threshold=0.05
            ) 
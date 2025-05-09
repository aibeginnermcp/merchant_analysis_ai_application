"""
监控模块
"""
import time
from typing import Optional, Dict, Any
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps

class MetricsCollector:
    """指标收集器"""
    
    # 请求计数器
    request_counter = Counter(
        'merchant_bi_request_total',
        'Total number of requests',
        ['service', 'endpoint']
    )
    
    # 错误计数器
    error_counter = Counter(
        'merchant_bi_error_total',
        'Total number of errors',
        ['service', 'error_type']
    )
    
    # 请求处理时间
    request_latency = Histogram(
        'merchant_bi_request_latency_seconds',
        'Request latency in seconds',
        ['service', 'endpoint']
    )
    
    # 当前活跃请求数
    active_requests = Gauge(
        'merchant_bi_active_requests',
        'Number of active requests',
        ['service']
    )

    @classmethod
    def record_request(cls, service: str, endpoint: str) -> None:
        """记录请求"""
        cls.request_counter.labels(service=service, endpoint=endpoint).inc()
        
    @classmethod
    def record_error(cls, service: str, error_type: str) -> None:
        """记录错误"""
        cls.error_counter.labels(service=service, error_type=error_type).inc()
        
    @classmethod
    def track_request_time(cls, service: str, endpoint: str) -> None:
        """跟踪请求时间装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                cls.active_requests.labels(service=service).inc()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    cls.active_requests.labels(service=service).dec()
                    cls.request_latency.labels(
                        service=service,
                        endpoint=endpoint
                    ).observe(time.time() - start_time)
            return wrapper
        return decorator

class BusinessMetricsCollector:
    """业务指标收集器"""
    
    # 预测准确率
    prediction_accuracy = Gauge(
        'merchant_bi_prediction_accuracy',
        'Prediction accuracy',
        ['service', 'model_type']
    )
    
    # 处理时间
    processing_time = Histogram(
        'merchant_bi_processing_time_seconds',
        'Processing time in seconds',
        ['service', 'operation_type']
    )
    
    # 业务错误率
    error_rate = Gauge(
        'merchant_bi_error_rate',
        'Error rate',
        ['service', 'error_category']
    )
    
    @classmethod
    def record_accuracy(cls, service: str, model_type: str, accuracy: float) -> None:
        """记录准确率"""
        cls.prediction_accuracy.labels(
            service=service,
            model_type=model_type
        ).set(accuracy)
        
    @classmethod
    def record_processing_time(cls, service: str, operation_type: str, duration: float) -> None:
        """记录处理时间"""
        cls.processing_time.labels(
            service=service,
            operation_type=operation_type
        ).observe(duration)
        
    @classmethod
    def record_error_rate(cls, service: str, error_category: str, rate: float) -> None:
        """记录错误率"""
        cls.error_rate.labels(
            service=service,
            error_category=error_category
        ).set(rate) 
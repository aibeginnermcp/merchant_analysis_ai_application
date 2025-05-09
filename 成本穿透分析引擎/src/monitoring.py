"""
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time

# 请求计数器
REQUEST_COUNT = Counter(
    'cost_analysis_request_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

# 请求处理时间
REQUEST_LATENCY = Histogram(
    'cost_analysis_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

# 当前活跃请求数
ACTIVE_REQUESTS = Gauge(
    'cost_analysis_active_requests',
    'Number of active requests',
    ['method', 'endpoint']
)

# 成本分析结果指标
COST_METRICS = Gauge(
    'cost_analysis_metrics',
    'Cost analysis metrics',
    ['merchant_id', 'metric_name']
)

# 错误计数器
ERROR_COUNT = Counter(
    'cost_analysis_errors_total',
    'Total number of errors',
    ['error_type']
)

def track_request_metrics(endpoint: str):
    """
    请求指标跟踪装饰器
    
    Args:
        endpoint: API端点名称
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            method = "POST" if func.__name__ in ["analyze_cost", "simulate_cost_changes"] else "GET"
            
            # 增加活跃请求计数
            ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
            
            start_time = time.time()
            status = "success"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                ERROR_COUNT.labels(error_type=type(e).__name__).inc()
                raise
            finally:
                # 请求计数
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
                
                # 记录请求处理时间
                REQUEST_LATENCY.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(time.time() - start_time)
                
                # 减少活跃请求计数
                ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
        
        return wrapper
    return decorator

def record_cost_metrics(merchant_id: str, metrics: dict):
    """
    记录成本分析指标
    
    Args:
        merchant_id: 商户ID
        metrics: 成本指标字典
    """
    for metric_name, value in metrics.items():
        if isinstance(value, (int, float)):
            COST_METRICS.labels(
                merchant_id=merchant_id,
                metric_name=metric_name
            ).set(value)

def init_metrics():
    """初始化监控指标"""
    # 重置所有计数器
    for counter in [REQUEST_COUNT, ERROR_COUNT]:
        counter._metrics.clear()
    
    # 重置所有仪表盘
    for gauge in [ACTIVE_REQUESTS, COST_METRICS]:
        gauge._metrics.clear()
    
    # 重置所有直方图
    REQUEST_LATENCY._metrics.clear()
""" 
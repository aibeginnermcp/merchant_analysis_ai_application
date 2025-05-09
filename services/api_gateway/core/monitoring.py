"""监控模块"""
from fastapi import FastAPI, Request
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from typing import Dict, Any
import time

# 定义Prometheus指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors count',
    ['method', 'endpoint', 'error_type']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests',
    ['method']
)

SERVICE_UP = Gauge(
    'service_up',
    'Service availability status',
    ['service_name']
)

CACHE_HIT_COUNT = Counter(
    'cache_hits_total',
    'Total cache hits count',
    ['cache_type']
)

CACHE_MISS_COUNT = Counter(
    'cache_misses_total',
    'Total cache misses count',
    ['cache_type']
)

CIRCUIT_BREAKER_STATE = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half-open, 2=open)',
    ['service_name']
)

def setup_monitoring(app: FastAPI):
    """设置监控
    
    Args:
        app: FastAPI应用实例
    """
    # 设置OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    
    # 配置Jaeger导出器
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    # 添加BatchSpanProcessor
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    # 使用FastAPI自动检测
    FastAPIInstrumentor.instrument_app(app)
    
    @app.middleware("http")
    async def monitoring_middleware(request: Request, call_next):
        """监控中间件"""
        # 增加活跃请求计数
        ACTIVE_REQUESTS.labels(method=request.method).inc()
        
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 记录请求指标
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            # 记录请求延迟
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # 记录错误
            ERROR_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                error_type=type(e).__name__
            ).inc()
            raise
            
        finally:
            # 减少活跃请求计数
            ACTIVE_REQUESTS.labels(method=request.method).dec()
            
    @app.get("/metrics")
    async def metrics():
        """Prometheus指标接口"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
        
def record_cache_hit(cache_type: str):
    """记录缓存命中
    
    Args:
        cache_type: 缓存类型
    """
    CACHE_HIT_COUNT.labels(cache_type=cache_type).inc()
    
def record_cache_miss(cache_type: str):
    """记录缓存未命中
    
    Args:
        cache_type: 缓存类型
    """
    CACHE_MISS_COUNT.labels(cache_type=cache_type).inc()
    
def update_service_status(service_name: str, is_up: bool):
    """更新服务状态
    
    Args:
        service_name: 服务名称
        is_up: 服务是否可用
    """
    SERVICE_UP.labels(service_name=service_name).set(1 if is_up else 0)
    
def update_circuit_breaker_state(service_name: str, state: str):
    """更新断路器状态
    
    Args:
        service_name: 服务名称
        state: 断路器状态
    """
    state_value = {
        "closed": 0,
        "half-open": 1,
        "open": 2
    }.get(state, 0)
    
    CIRCUIT_BREAKER_STATE.labels(service_name=service_name).set(state_value) 
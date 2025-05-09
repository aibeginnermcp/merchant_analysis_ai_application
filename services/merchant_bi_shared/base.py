"""
商户智能经营分析平台基础服务类

提供所有微服务通用的基础功能，包括：
- 配置管理
- 日志记录
- 监控指标
- 健康检查
- 错误处理
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from prometheus_client import Counter, Histogram
import redis
import pika
from motor.motor_asyncio import AsyncIOMotorClient

class BaseService:
    """基础服务类，提供通用功能"""
    
    def __init__(self, service_name: str):
        """
        初始化基础服务
        
        Args:
            service_name: 服务名称
        """
        self.service_name = service_name
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # 初始化日志
        self._setup_logging()
        
        # 初始化监控指标
        self._setup_metrics()
        
        # 初始化数据库连接
        self._setup_database()
        
        # 初始化Redis连接
        self._setup_redis()
        
        # 初始化RabbitMQ连接
        self._setup_rabbitmq()
        
    def _setup_logging(self) -> None:
        """配置日志系统"""
        self.logger = logging.getLogger(self.service_name)
        self.logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
        
        # 添加格式化处理器
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"service": "%(name)s", "message": "%(message)s"}'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def _setup_metrics(self) -> None:
        """配置Prometheus监控指标"""
        self.request_counter = Counter(
            f'merchant_bi_{self.service_name}_requests_total',
            '请求总数'
        )
        
        self.request_duration = Histogram(
            f'merchant_bi_{self.service_name}_request_duration_seconds',
            '请求处理时间',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.error_counter = Counter(
            f'merchant_bi_{self.service_name}_errors_total',
            '错误总数',
            ['error_type']
        )
        
    def _setup_database(self) -> None:
        """配置MongoDB连接"""
        mongodb_uri = os.getenv('MONGODB_URI')
        if mongodb_uri:
            self.db_client = AsyncIOMotorClient(mongodb_uri)
            self.db = self.db_client[f'merchant_bi_{self.service_name}']
        
    def _setup_redis(self) -> None:
        """配置Redis连接"""
        redis_uri = os.getenv('REDIS_URI')
        if redis_uri:
            self.redis = redis.from_url(redis_uri)
            
    def _setup_rabbitmq(self) -> None:
        """配置RabbitMQ连接"""
        rabbitmq_uri = os.getenv('RABBITMQ_URI')
        if rabbitmq_uri:
            self.rabbitmq_connection = pika.BlockingConnection(
                pika.URLParameters(rabbitmq_uri)
            )
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            
    def get_cache_key(self, resource: str, resource_id: str) -> str:
        """
        生成缓存键名
        
        Args:
            resource: 资源类型
            resource_id: 资源ID
            
        Returns:
            str: 格式化的缓存键名
        """
        return f'merchant_bi:{self.service_name}:{resource}:{resource_id}'
    
    def publish_event(
        self,
        event_type: str,
        severity: str,
        payload: Dict[str, Any]
    ) -> None:
        """
        发布事件到消息队列
        
        Args:
            event_type: 事件类型
            severity: 事件严重程度
            payload: 事件数据
        """
        exchange = f'merchant_bi.{self.service_name}.{event_type}'
        routing_key = f'merchant_bi.{self.service_name}.{event_type}.{severity}'
        
        try:
            self.rabbitmq_channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=str(payload)
            )
        except Exception as e:
            self.logger.error(f'发布事件失败: {str(e)}')
            self.error_counter.labels(error_type='event_publish').inc()
            
    def health_check(self) -> Dict[str, Any]:
        """
        执行健康检查
        
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        status = {
            'service': self.service_name,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        # 检查数据库连接
        try:
            self.db_client.admin.command('ping')
            status['checks']['database'] = 'ok'
        except Exception as e:
            status['checks']['database'] = str(e)
            status['status'] = 'unhealthy'
            
        # 检查Redis连接
        try:
            self.redis.ping()
            status['checks']['redis'] = 'ok'
        except Exception as e:
            status['checks']['redis'] = str(e)
            status['status'] = 'unhealthy'
            
        # 检查RabbitMQ连接
        try:
            if not self.rabbitmq_connection.is_open:
                raise Exception('Connection closed')
            status['checks']['rabbitmq'] = 'ok'
        except Exception as e:
            status['checks']['rabbitmq'] = str(e)
            status['status'] = 'unhealthy'
            
        return status 
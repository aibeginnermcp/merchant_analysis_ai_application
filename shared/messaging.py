"""
商户智能经营分析平台消息队列模块

提供基于RabbitMQ的事件总线功能，包括：
- 事件发布
- 事件订阅
- 消息重试
- 死信处理
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional
from functools import wraps

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

class EventBus:
    """事件总线，提供RabbitMQ消息队列操作封装"""
    
    def __init__(
        self,
        connection: pika.BlockingConnection,
        service_name: str,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化事件总线
        
        Args:
            connection: RabbitMQ连接实例
            service_name: 服务名称
            logger: 日志记录器
        """
        self.connection = connection
        self.service_name = service_name
        self.logger = logger or logging.getLogger(__name__)
        
        # 创建通道
        self.channel = self.connection.channel()
        
        # 声明死信交换机
        self.dead_letter_exchange = f'merchant_bi.{service_name}.dlx'
        self.channel.exchange_declare(
            exchange=self.dead_letter_exchange,
            exchange_type='direct',
            durable=True
        )
        
    def _create_exchange(
        self,
        event_type: str,
        exchange_type: str = 'topic'
    ) -> str:
        """
        创建交换机
        
        Args:
            event_type: 事件类型
            exchange_type: 交换机类型
            
        Returns:
            str: 交换机名称
        """
        exchange_name = f'merchant_bi.{self.service_name}.{event_type}'
        
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        
        return exchange_name
        
    def _create_queue(
        self,
        event_type: str,
        consumer_name: str,
        max_retries: int = 3
    ) -> str:
        """
        创建队列
        
        Args:
            event_type: 事件类型
            consumer_name: 消费者名称
            max_retries: 最大重试次数
            
        Returns:
            str: 队列名称
        """
        queue_name = f'merchant_bi.{self.service_name}.{event_type}.{consumer_name}'
        
        # 声明死信队列
        dead_letter_queue = f'{queue_name}.dlq'
        self.channel.queue_declare(
            queue=dead_letter_queue,
            durable=True
        )
        
        self.channel.queue_bind(
            exchange=self.dead_letter_exchange,
            queue=dead_letter_queue,
            routing_key=queue_name
        )
        
        # 声明主队列
        arguments = {
            'x-dead-letter-exchange': self.dead_letter_exchange,
            'x-dead-letter-routing-key': queue_name,
            'x-message-ttl': 1000 * 60 * 60,  # 1小时
            'x-max-retries': max_retries
        }
        
        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments=arguments
        )
        
        return queue_name
        
    def publish(
        self,
        event_type: str,
        routing_key: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        发布事件
        
        Args:
            event_type: 事件类型
            routing_key: 路由键
            data: 事件数据
            headers: 消息头
        """
        exchange = self._create_exchange(event_type)
        
        try:
            # 准备消息属性
            properties = BasicProperties(
                content_type='application/json',
                delivery_mode=2,  # 持久化消息
                headers=headers or {}
            )
            
            # 发布消息
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(data),
                properties=properties
            )
            
            self.logger.info(
                f'Published event: {event_type}, routing_key: {routing_key}'
            )
            
        except Exception as e:
            self.logger.error(
                f'Failed to publish event: {event_type}, error: {str(e)}'
            )
            raise
            
    def subscribe(
        self,
        event_type: str,
        consumer_name: str,
        callback: Callable[[Dict[str, Any], Dict[str, Any]], None],
        routing_keys: Optional[List[str]] = None,
        max_retries: int = 3
    ) -> None:
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            consumer_name: 消费者名称
            callback: 回调函数
            routing_keys: 路由键列表
            max_retries: 最大重试次数
        """
        exchange = self._create_exchange(event_type)
        queue = self._create_queue(event_type, consumer_name, max_retries)
        
        # 绑定路由键
        if routing_keys:
            for key in routing_keys:
                self.channel.queue_bind(
                    exchange=exchange,
                    queue=queue,
                    routing_key=key
                )
        else:
            # 默认绑定所有消息
            self.channel.queue_bind(
                exchange=exchange,
                queue=queue,
                routing_key='#'
            )
            
        def message_handler(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes
        ) -> None:
            """消息处理函数"""
            try:
                # 解析消息
                data = json.loads(body)
                headers = properties.headers or {}
                
                # 获取重试次数
                retry_count = headers.get('retry_count', 0)
                
                try:
                    # 执行回调
                    callback(data, headers)
                    # 确认消息
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    self.logger.error(
                        f'Failed to process message: {str(e)}, '
                        f'retry_count: {retry_count}'
                    )
                    
                    # 检查重试次数
                    if retry_count >= max_retries:
                        # 达到最大重试次数，发送到死信队列
                        ch.basic_reject(
                            delivery_tag=method.delivery_tag,
                            requeue=False
                        )
                    else:
                        # 重新入队，增加重试次数
                        headers['retry_count'] = retry_count + 1
                        ch.basic_publish(
                            exchange=exchange,
                            routing_key=method.routing_key,
                            body=body,
                            properties=BasicProperties(
                                headers=headers
                            )
                        )
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        
            except json.JSONDecodeError as e:
                self.logger.error(f'Invalid message format: {str(e)}')
                # 无效消息直接丢弃
                ch.basic_reject(
                    delivery_tag=method.delivery_tag,
                    requeue=False
                )
                
        # 设置预取计数
        self.channel.basic_qos(prefetch_count=1)
        
        # 开始消费
        self.channel.basic_consume(
            queue=queue,
            on_message_callback=message_handler
        )
        
        self.logger.info(
            f'Started consuming from queue: {queue}, '
            f'routing_keys: {routing_keys or ["#"]}'
        )
        
    def start_consuming(self) -> None:
        """开始消费消息"""
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            
    def close(self) -> None:
        """关闭连接"""
        if self.channel and not self.channel.is_closed:
            self.channel.close()
        if self.connection and not self.connection.is_closed:
            self.connection.close() 
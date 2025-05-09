"""
消息队列模块
"""
import json
from typing import Optional, Any, Callable, Awaitable
import aiormq
from pydantic import BaseModel

class EventBus:
    """事件总线"""
    
    def __init__(self, rabbitmq_uri: str):
        """初始化事件总线
        
        Args:
            rabbitmq_uri: RabbitMQ连接URI
        """
        self.rabbitmq_uri = rabbitmq_uri
        self.connection = None
        self.channel = None
        
    async def connect(self) -> None:
        """建立连接"""
        self.connection = await aiormq.connect(self.rabbitmq_uri)
        self.channel = await self.connection.channel()
        
    async def close(self) -> None:
        """关闭连接"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
            
    async def publish(
        self,
        service: str,
        event_type: str,
        severity: str,
        payload: BaseModel
    ) -> None:
        """发布事件
        
        Args:
            service: 服务名称
            event_type: 事件类型
            severity: 严重程度
            payload: 事件数据
        """
        if not self.channel:
            await self.connect()
            
        exchange_name = f"merchant_bi.{service}.{event_type}"
        routing_key = f"merchant_bi.{service}.{event_type}.{severity}"
        
        # 确保交换机存在
        await self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='topic',
            durable=True
        )
        
        # 发布消息
        await self.channel.basic_publish(
            payload.json().encode(),
            exchange=exchange_name,
            routing_key=routing_key,
            properties={
                'delivery_mode': 2  # 持久化消息
            }
        )
        
    async def subscribe(
        self,
        service: str,
        event_type: str,
        severity: str,
        callback: Callable[[dict], Awaitable[None]]
    ) -> None:
        """订阅事件
        
        Args:
            service: 服务名称
            event_type: 事件类型
            severity: 严重程度
            callback: 回调函数
        """
        if not self.channel:
            await self.connect()
            
        exchange_name = f"merchant_bi.{service}.{event_type}"
        queue_name = f"merchant_bi.{service}.{event_type}.{severity}.queue"
        routing_key = f"merchant_bi.{service}.{event_type}.{severity}"
        
        # 声明交换机和队列
        await self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type='topic',
            durable=True
        )
        
        await self.channel.queue_declare(
            queue=queue_name,
            durable=True
        )
        
        await self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        
        # 消费消息
        async def on_message(message):
            try:
                payload = json.loads(message.body.decode())
                await callback(payload)
                await message.channel.basic_ack(message.delivery.delivery_tag)
            except Exception as e:
                # 消息处理失败，进入死信队列
                await message.channel.basic_reject(
                    message.delivery.delivery_tag,
                    requeue=False
                )
                
        await self.channel.basic_consume(
            queue=queue_name,
            consumer_callback=on_message
        )
        
    async def create_dead_letter_exchange(
        self,
        service: str,
        event_type: str
    ) -> None:
        """创建死信交换机
        
        Args:
            service: 服务名称
            event_type: 事件类型
        """
        if not self.channel:
            await self.connect()
            
        dead_letter_exchange = f"merchant_bi.{service}.{event_type}.dead"
        dead_letter_queue = f"merchant_bi.{service}.{event_type}.dead.queue"
        
        # 声明死信交换机和队列
        await self.channel.exchange_declare(
            exchange=dead_letter_exchange,
            exchange_type='direct',
            durable=True
        )
        
        await self.channel.queue_declare(
            queue=dead_letter_queue,
            durable=True
        )
        
        await self.channel.queue_bind(
            queue=dead_letter_queue,
            exchange=dead_letter_exchange,
            routing_key='dead'
        ) 
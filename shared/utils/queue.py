"""
消息队列管理模块
"""
from typing import Optional, Any, Callable
import json
import aio_pika
from src.shared.config import settings

class QueueManager:
    """消息队列管理器"""
    
    def __init__(self):
        """初始化消息队列管理器"""
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._exchange: Optional[aio_pika.Exchange] = None
        
    async def connect(self):
        """连接RabbitMQ"""
        try:
            self._connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URI
            )
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                "merchant_analysis",
                aio_pika.ExchangeType.TOPIC
            )
            print("RabbitMQ连接成功")
        except Exception as e:
            print(f"RabbitMQ连接失败: {e}")
            raise
            
    async def disconnect(self):
        """断开RabbitMQ连接"""
        if self._connection:
            await self._connection.close()
            print("RabbitMQ连接已关闭")
            
    async def publish(
        self,
        routing_key: str,
        message: Any,
        priority: int = 0
    ):
        """发布消息
        
        Args:
            routing_key: 路由键
            message: 消息内容
            priority: 优先级
        """
        if not self._exchange:
            raise ConnectionError("RabbitMQ未连接")
            
        await self._exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                priority=priority
            ),
            routing_key=routing_key
        )
        
    async def subscribe(
        self,
        queue_name: str,
        routing_key: str,
        callback: Callable
    ):
        """订阅消息
        
        Args:
            queue_name: 队列名称
            routing_key: 路由键
            callback: 回调函数
        """
        if not self._channel:
            raise ConnectionError("RabbitMQ未连接")
            
        # 声明队列
        queue = await self._channel.declare_queue(
            queue_name,
            durable=True
        )
        
        # 绑定队列到交换机
        await queue.bind(
            self._exchange,
            routing_key=routing_key
        )
        
        # 开始消费消息
        await queue.consume(callback)
        
    async def publish_analysis_task(
        self,
        merchant_id: str,
        analysis_type: str,
        data: Any
    ):
        """发布分析任务
        
        Args:
            merchant_id: 商户ID
            analysis_type: 分析类型
            data: 任务数据
        """
        routing_key = f"analysis.{analysis_type.lower()}"
        message = {
            "merchant_id": merchant_id,
            "analysis_type": analysis_type,
            "data": data
        }
        await self.publish(routing_key, message)
        
    async def publish_notification(
        self,
        merchant_id: str,
        notification_type: str,
        content: Any
    ):
        """发布通知消息
        
        Args:
            merchant_id: 商户ID
            notification_type: 通知类型
            content: 通知内容
        """
        routing_key = f"notification.{notification_type.lower()}"
        message = {
            "merchant_id": merchant_id,
            "type": notification_type,
            "content": content
        }
        await self.publish(routing_key, message)

# 创建全局消息队列管理器实例
queue_manager = QueueManager() 
"""测试配置模块"""
import pytest
import asyncio
from typing import Dict, Any, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
import mongomock
import fakeredis.aioredis
from datetime import datetime

from services.api_gateway.main import app
from services.api_gateway.core.service_discovery import ServiceDiscovery
from services.api_gateway.core.circuit_breaker import CircuitBreaker
from services.api_gateway.core.clients import (
    DataSimulatorClient,
    CashFlowClient,
    CostAnalysisClient,
    ComplianceClient
)
from src.shared.database import db_manager
from src.shared.cache import cache_manager
from src.shared.queue import queue_manager
from src.shared.discovery import discovery

@pytest.fixture
def test_client() -> Generator:
    """创建测试客户端"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_mongodb() -> Generator:
    """模拟MongoDB客户端"""
    client = AsyncMock(spec=AsyncIOMotorClient)
    yield client

@pytest.fixture
def mock_redis() -> Generator:
    """模拟Redis客户端"""
    client = AsyncMock(spec=Redis)
    yield client

@pytest.fixture
def mock_service_discovery() -> Generator:
    """模拟服务发现"""
    discovery = Mock(spec=ServiceDiscovery)
    discovery.get_service_url = AsyncMock(return_value="http://localhost:8000")
    yield discovery

@pytest.fixture
def mock_circuit_breaker() -> Generator:
    """模拟断路器"""
    breaker = Mock(spec=CircuitBreaker)
    breaker.__call__ = AsyncMock()
    yield breaker

@pytest.fixture
def mock_data_simulator() -> Generator:
    """模拟数据模拟服务客户端"""
    client = Mock(spec=DataSimulatorClient)
    client.generate_data = AsyncMock(return_value={
        "transactions": [],
        "costs": [],
        "profile": {},
        "compliance_records": []
    })
    yield client

@pytest.fixture
def mock_cashflow_client() -> Generator:
    """模拟现金流预测服务客户端"""
    client = Mock(spec=CashFlowClient)
    client.predict = AsyncMock(return_value={
        "predictions": [],
        "confidence": 0.95
    })
    yield client

@pytest.fixture
def mock_cost_analysis_client() -> Generator:
    """模拟成本分析服务客户端"""
    client = Mock(spec=CostAnalysisClient)
    client.analyze = AsyncMock(return_value={
        "cost_breakdown": {},
        "optimization_suggestions": []
    })
    yield client

@pytest.fixture
def mock_compliance_client() -> Generator:
    """模拟合规检查服务客户端"""
    client = Mock(spec=ComplianceClient)
    client.check = AsyncMock(return_value={
        "compliance_score": 0.85,
        "violations": [],
        "recommendations": []
    })
    yield client

@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_db():
    """Mock MongoDB连接"""
    client = mongomock.MongoClient()
    db = client["merchant_analysis"]
    
    # 保存原始客户端
    original_client = db_manager._client
    db_manager._client = client
    
    # 添加测试数据
    await add_test_data(db)
    
    yield db
    
    # 恢复原始客户端
    db_manager._client = original_client

@pytest.fixture
async def mock_redis():
    """Mock Redis连接"""
    redis = fakeredis.aioredis.FakeRedis()
    
    # 保存原始连接
    original_redis = cache_manager._redis
    cache_manager._redis = redis
    
    yield redis
    
    # 恢复原始连接
    cache_manager._redis = original_redis
    await redis.close()

@pytest.fixture
def mock_queue():
    """Mock RabbitMQ连接"""
    queue = AsyncMock()
    
    # 保存原始连接
    original_connection = queue_manager._connection
    queue_manager._connection = queue
    
    yield queue
    
    # 恢复原始连接
    queue_manager._connection = original_connection

@pytest.fixture
def mock_discovery():
    """Mock Consul连接"""
    consul = MagicMock()
    
    # 保存原始连接
    original_consul = discovery._consul
    discovery._consul = consul
    
    # 设置服务发现返回值
    consul.get_service_address.return_value = "http://localhost:8001"
    
    yield consul
    
    # 恢复原始连接
    discovery._consul = original_consul

async def add_test_data(db):
    """添加测试数据
    
    Args:
        db: 测试数据库实例
    """
    # 添加测试商户
    await db.merchants.insert_one({
        "_id": "test_merchant_id",
        "username": "test_merchant",
        "password": "hashed_password",
        "name": "测试商户",
        "industry": "餐饮",
        "size": "中型",
        "establishment_date": datetime(2020, 1, 1),
        "location": "北京市朝阳区",
        "business_hours": "09:00-22:00",
        "payment_methods": ["支付宝", "微信支付"],
        "rating": 4.5
    })
    
    # 添加测试交易数据
    await db.transactions.insert_many([
        {
            "merchant_id": "test_merchant_id",
            "date": datetime(2023, 1, 1),
            "revenue": 10000.0,
            "transaction_count": 100,
            "average_transaction_value": 100.0,
            "peak_hours": ["12:00", "18:00"],
            "payment_distribution": {
                "支付宝": 0.6,
                "微信支付": 0.4
            },
            "channel_distribution": {
                "堂食": 0.7,
                "外卖": 0.3
            },
            "refund_amount": 200.0
        },
        {
            "merchant_id": "test_merchant_id",
            "date": datetime(2023, 1, 2),
            "revenue": 12000.0,
            "transaction_count": 120,
            "average_transaction_value": 100.0,
            "peak_hours": ["12:00", "18:00"],
            "payment_distribution": {
                "支付宝": 0.55,
                "微信支付": 0.45
            },
            "channel_distribution": {
                "堂食": 0.65,
                "外卖": 0.35
            },
            "refund_amount": 150.0
        }
    ]) 
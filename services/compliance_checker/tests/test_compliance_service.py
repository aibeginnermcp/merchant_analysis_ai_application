"""合规检查服务测试"""
import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import aioredis
import json

from ..main import app, ComplianceService
from ..models import ComplianceRule, ComplianceViolation, ComplianceAlert
from ..rule_engine import RuleEngine
from ..cache import ComplianceCache
from ..tasks import ComplianceTaskManager

# 测试客户端
client = TestClient(app)

# 测试数据
TEST_MERCHANT_ID = "test_merchant_001"
TEST_RULE = ComplianceRule(
    rule_id="TEST001",
    category="测试",
    name="测试规则",
    description="用于测试的规则",
    severity="中",
    check_method="阈值",
    parameters={
        "min_value": 100,
        "max_value": 1000
    }
)

@pytest.fixture
async def setup_test_data():
    """准备测试数据"""
    # 连接数据库
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = mongo_client.merchant_analysis_test
    
    # 清理旧数据
    await db.compliance_rules.delete_many({})
    await db.compliance_alerts.delete_many({})
    await db.merchant_data.delete_many({})
    
    # 插入测试数据
    await db.merchant_data.insert_one({
        "merchant_id": TEST_MERCHANT_ID,
        "data": {
            "financials": {
                "cash_ratio": 0.15,
                "quick_ratio": 0.8,
                "debt_ratio": 0.75
            },
            "operations": {
                "business_hours": [
                    {"timestamp": "2024-01-01T08:00:00", "status": "open"},
                    {"timestamp": "2024-01-01T23:00:00", "status": "close"}
                ]
            },
            "safety": {
                "equipment": ["灭火器", "烟感器"],
                "last_check": "2024-01-01"
            }
        }
    })
    
    yield db
    
    # 清理数据
    await db.compliance_rules.delete_many({})
    await db.compliance_alerts.delete_many({})
    await db.merchant_data.delete_many({})
    mongo_client.close()

@pytest.mark.asyncio
async def test_rule_engine():
    """测试规则引擎"""
    print("\n1. 开始测试规则引擎...")
    
    # 创建规则引擎
    engine = RuleEngine()
    
    # 注册测试规则
    engine.register_rule(TEST_RULE)
    assert TEST_RULE.rule_id in engine.rules_registry
    print("✓ 规则注册成功")
    
    # 测试规则评估
    test_data = {"value": 50}  # 低于最小值
    violation = await engine.evaluate_rule(TEST_RULE.rule_id, test_data)
    assert violation is not None
    assert violation.rule_id == TEST_RULE.rule_id
    assert violation.severity == TEST_RULE.severity
    print("✓ 规则评估正确")
    
    # 测试批量规则评估
    violations = await engine.evaluate_rules(category="测试", data=test_data)
    assert len(violations) == 1
    print("✓ 批量规则评估正确")
    
    print("规则引擎测试完成")

@pytest.mark.asyncio
async def test_cache():
    """测试缓存功能"""
    print("\n2. 开始测试缓存功能...")
    
    # 创建缓存管理器
    cache = ComplianceCache("redis://localhost:6379")
    
    # 测试商户状态缓存
    test_status = {
        "merchant_id": TEST_MERCHANT_ID,
        "status": "active",
        "last_check": "2024-01-01"
    }
    
    await cache.set_merchant_status(TEST_MERCHANT_ID, test_status)
    cached_status = await cache.get_merchant_status(TEST_MERCHANT_ID)
    assert cached_status == test_status
    print("✓ 商户状态缓存正常")
    
    # 测试违规记录缓存
    test_violations = [
        {
            "rule_id": "TEST001",
            "description": "测试违规",
            "severity": "中"
        }
    ]
    
    await cache.set_cached_violations(
        TEST_MERCHANT_ID,
        test_violations,
        datetime.now(),
        datetime.now() + timedelta(days=1)
    )
    
    cached_violations = await cache.get_cached_violations(
        TEST_MERCHANT_ID,
        datetime.now(),
        datetime.now() + timedelta(days=1)
    )
    assert cached_violations == test_violations
    print("✓ 违规记录缓存正常")
    
    # 测试缓存清理
    await cache.invalidate_merchant_cache(TEST_MERCHANT_ID)
    assert await cache.get_merchant_status(TEST_MERCHANT_ID) is None
    print("✓ 缓存清理正常")
    
    await cache.close()
    print("缓存功能测试完成")

@pytest.mark.asyncio
async def test_task_manager():
    """测试任务管理器"""
    print("\n3. 开始测试任务管理器...")
    
    # 创建任务管理器
    task_manager = ComplianceTaskManager(
        mongo_url="mongodb://localhost:27017",
        redis_url="redis://localhost:6379"
    )
    
    # 测试任务调度
    task_id = await task_manager.schedule_check(
        TEST_MERCHANT_ID,
        check_type="full"
    )
    assert task_id is not None
    print("✓ 任务调度成功")
    
    # 测试任务状态查询
    status = await task_manager.get_task_status(task_id)
    assert status is not None
    assert status["merchant_id"] == TEST_MERCHANT_ID
    print("✓ 任务状态查询正常")
    
    # 测试任务取消
    success = await task_manager.cancel_task(task_id)
    assert success
    status = await task_manager.get_task_status(task_id)
    assert status["status"] == "cancelled"
    print("✓ 任务取消正常")
    
    await task_manager.close()
    print("任务管理器测试完成")

def test_api_endpoints():
    """测试API接口"""
    print("\n4. 开始测试API接口...")
    
    # 测试健康检查接口
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ 健康检查接口正常")
    
    # 测试合规检查接口
    check_request = {
        "request_id": "test_001",
        "merchant_id": TEST_MERCHANT_ID,
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-01-31T23:59:59",
        "analysis_type": "compliance",
        "parameters": {
            "check_types": ["financial", "operational", "safety"]
        }
    }
    
    response = client.post("/check", json=check_request)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["request_id"] == check_request["request_id"]
    print("✓ 合规检查接口正常")
    
    # 测试预警查询接口
    response = client.get(f"/alerts/{TEST_MERCHANT_ID}")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    print("✓ 预警查询接口正常")
    
    # 测试规则添加接口
    response = client.post("/rules", json=TEST_RULE.dict())
    assert response.status_code == 200
    result = response.json()
    assert result["rule_id"] == TEST_RULE.rule_id
    print("✓ 规则添加接口正常")
    
    print("API接口测试完成")

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 
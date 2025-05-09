"""
Gateway数据验证测试模块
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status
from src.gateway.models import AnalysisType

@pytest.mark.asyncio
async def test_analyze_invalid_prediction_days(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试无效预测天数
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 先登录获取token
    login_response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    token = login_response.json()["access_token"]
    
    # 测试负数天数
    response = await test_client.post(
        "/api/v1/merchant/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": "test_merchant_id",
            "analysis_modules": [AnalysisType.CASHFLOW],
            "time_range": {
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            "prediction_days": -1
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # 测试超过最大限制的天数
    response = await test_client.post(
        "/api/v1/merchant/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": "test_merchant_id",
            "analysis_modules": [AnalysisType.CASHFLOW],
            "time_range": {
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            "prediction_days": 366  # 超过一年
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_analyze_empty_modules(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试空分析模块列表
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 先登录获取token
    login_response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    token = login_response.json()["access_token"]
    
    response = await test_client.post(
        "/api/v1/merchant/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": "test_merchant_id",
            "analysis_modules": [],
            "time_range": {
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            "prediction_days": 7
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "At least one analysis module required" in response.json()["detail"]

@pytest.mark.asyncio
async def test_analyze_invalid_module(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试无效分析模块
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 先登录获取token
    login_response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    token = login_response.json()["access_token"]
    
    response = await test_client.post(
        "/api/v1/merchant/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": "test_merchant_id",
            "analysis_modules": ["INVALID_MODULE"],
            "time_range": {
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            "prediction_days": 7
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Invalid analysis module" in response.json()["detail"]

@pytest.mark.asyncio
async def test_analyze_duplicate_modules(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试重复分析模块
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 先登录获取token
    login_response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    token = login_response.json()["access_token"]
    
    response = await test_client.post(
        "/api/v1/merchant/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": "test_merchant_id",
            "analysis_modules": [
                AnalysisType.CASHFLOW,
                AnalysisType.CASHFLOW
            ],
            "time_range": {
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            "prediction_days": 7
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Duplicate analysis modules" in response.json()["detail"]

@pytest.mark.asyncio
async def test_invalid_date_format(test_client, mock_db):
    """测试无效日期格式
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
    """
    # 先登录获取token
    login_response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    token = login_response.json()["access_token"]
    
    # 获取交易数据时使用无效日期格式
    response = await test_client.get(
        "/api/v1/merchant/test_merchant_id/transactions",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "start_date": "2023/01/01",  # 错误的日期格式
            "end_date": "2023/01/31"
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Invalid date format" in response.json()["detail"]

@pytest.mark.asyncio
async def test_request_rate_limit(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试请求速率限制
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 先登录获取token
    login_response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    token = login_response.json()["access_token"]
    
    # 快速发送多个请求
    for _ in range(10):
        response = await test_client.get(
            "/api/v1/merchant/test_merchant_id",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # 最后一个请求应该被限制
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Too many requests" in response.json()["detail"] 
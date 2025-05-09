"""
Gateway边界条件测试模块
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status
from src.gateway.models import AnalysisType

# 认证相关边界条件测试
@pytest.mark.asyncio
async def test_login_empty_credentials(test_client, mock_db):
    """测试空凭证登录
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
    """
    response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "",
            "password": ""
        }
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_invalid_token_format(test_client):
    """测试无效token格式
    
    Args:
        test_client: 测试客户端
    """
    response = await test_client.get(
        "/api/v1/merchant/test_merchant_id",
        headers={"Authorization": "InvalidFormat token"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_expired_token(test_client, mock_db):
    """测试过期token
    
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
    expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0X21lcmNoYW50X2lkIiwiZXhwIjoxNTE2MjM5MDIyfQ.2H0I3Qb7cF5aS5xnbZZZ9X3X3X3X3X3X"
    
    response = await test_client.get(
        "/api/v1/merchant/test_merchant_id",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token has expired" in response.json()["detail"]

# 请求参数边界条件测试
@pytest.mark.asyncio
async def test_analyze_invalid_date_range(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试无效日期范围
    
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
    
    # 结束日期早于开始日期
    response = await test_client.post(
        "/api/v1/merchant/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": "test_merchant_id",
            "analysis_modules": [AnalysisType.CASHFLOW],
            "time_range": {
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() - timedelta(days=30)).isoformat()
            },
            "prediction_days": 7
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid date range" in response.json()["detail"]

@pytest.mark.asyncio
async def test_analyze_future_date(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试未来日期分析
    
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
    
    # 开始日期在未来
    future_date = datetime.utcnow() + timedelta(days=1)
    response = await test_client.post(
        "/api/v1/merchant/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": "test_merchant_id",
            "analysis_modules": [AnalysisType.CASHFLOW],
            "time_range": {
                "start": future_date.isoformat(),
                "end": (future_date + timedelta(days=30)).isoformat()
            },
            "prediction_days": 7
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Start date cannot be in the future" in response.json()["detail"]

# 数据访问边界条件测试
@pytest.mark.asyncio
async def test_get_nonexistent_merchant(test_client, mock_db, mock_redis):
    """测试获取不存在的商户信息
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
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
    
    response = await test_client.get(
        "/api/v1/merchant/nonexistent_id",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Merchant not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_transactions_no_data(test_client, mock_db):
    """测试获取无交易数据时间段
    
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
    
    # 查询没有数据的时间段
    response = await test_client.get(
        "/api/v1/merchant/test_merchant_id/transactions",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "start_date": datetime(2022, 1, 1).isoformat(),
            "end_date": datetime(2022, 12, 31).isoformat()
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0

# 服务状态边界条件测试
@pytest.mark.asyncio
async def test_service_unavailable(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试服务不可用
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 模拟服务发现失败
    mock_discovery.get_service_address.side_effect = LookupError("Service not found")
    
    # 先登录获取token
    login_response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    token = login_response.json()["access_token"]
    
    # 发送分析请求
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
            "prediction_days": 7
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["results"]["CASHFLOW"]["status"] == "error"
    assert "服务不可用" in data["results"]["CASHFLOW"]["error"]

@pytest.mark.asyncio
async def test_cache_failure(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试缓存失败
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
        mock_redis: Mock Redis连接
        mock_queue: Mock消息队列连接
        mock_discovery: Mock服务发现连接
    """
    # 模拟Redis连接失败
    mock_redis.get.side_effect = Exception("Redis connection failed")
    
    # 先登录获取token
    login_response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    token = login_response.json()["access_token"]
    
    # 获取商户信息
    response = await test_client.get(
        "/api/v1/merchant/test_merchant_id",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 应该仍能从数据库获取数据
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["merchant_id"] == "test_merchant_id" 
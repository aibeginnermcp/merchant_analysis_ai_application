"""
Gateway路由测试模块
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status
from src.gateway.models import AnalysisType

@pytest.mark.asyncio
async def test_login_success(test_client, mock_db):
    """测试登录成功
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
    """
    response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "test_merchant",
            "password": "test_password"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800

@pytest.mark.asyncio
async def test_login_failed(test_client, mock_db):
    """测试登录失败
    
    Args:
        test_client: 测试客户端
        mock_db: Mock数据库连接
    """
    response = await test_client.post(
        "/api/v1/token",
        data={
            "username": "wrong_user",
            "password": "wrong_password"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_analyze_merchant(
    test_client,
    mock_db,
    mock_redis,
    mock_queue,
    mock_discovery
):
    """测试商户分析
    
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
    
    # 发送分析请求
    response = await test_client.post(
        "/api/v1/merchant/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "merchant_id": "test_merchant_id",
            "analysis_modules": [
                AnalysisType.CASHFLOW,
                AnalysisType.COST
            ],
            "time_range": {
                "start": datetime.utcnow().isoformat(),
                "end": (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            "prediction_days": 7
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["merchant_id"] == "test_merchant_id"
    assert data["status"] == "PROCESSING"
    assert "CASHFLOW" in data["results"]
    assert "COST" in data["results"]

@pytest.mark.asyncio
async def test_get_merchant_info(test_client, mock_db, mock_redis):
    """测试获取商户信息
    
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
    
    # 获取商户信息
    response = await test_client.get(
        "/api/v1/merchant/test_merchant_id",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["merchant_id"] == "test_merchant_id"
    assert data["name"] == "测试商户"
    assert data["industry"] == "餐饮"

@pytest.mark.asyncio
async def test_get_merchant_transactions(test_client, mock_db):
    """测试获取商户交易数据
    
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
    
    # 获取交易数据
    response = await test_client.get(
        "/api/v1/merchant/test_merchant_id/transactions",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "start_date": datetime(2023, 1, 1).isoformat(),
            "end_date": datetime(2023, 1, 2).isoformat()
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["revenue"] == 12000.0
    assert data[1]["revenue"] == 10000.0

@pytest.mark.asyncio
async def test_health_check(test_client):
    """测试健康检查接口
    
    Args:
        test_client: 测试客户端
    """
    response = await test_client.get("/api/v1/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data 
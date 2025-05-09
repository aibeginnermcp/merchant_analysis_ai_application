"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from ..src.main import app

client = TestClient(app)

@pytest.fixture
def test_merchant_id():
    return "TEST_MERCHANT_001"

@pytest.fixture
def time_range():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }

def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_service_info():
    """测试服务信息端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "成本穿透分析服务"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"

def test_analyze_cost(test_merchant_id, time_range):
    """测试成本分析端点"""
    request_data = {
        "merchant_id": test_merchant_id,
        "time_range": time_range,
        "analysis_types": ["structure", "trend"],
        "granularity": "monthly"
    }
    
    response = client.post("/api/v1/cost-analysis/analyze", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "structure" in data
    assert "trend" in data
    
    # 验证结构分析结果
    structure = data["structure"]
    assert "total_cost" in structure
    assert "cost_breakdown" in structure
    assert "major_cost_factors" in structure
    
    # 验证趋势分析结果
    trend = data["trend"]
    assert "trend_data" in trend
    assert "seasonal_patterns" in trend

def test_get_cost_metrics(test_merchant_id, time_range):
    """测试获取成本指标端点"""
    response = client.get(
        f"/api/v1/cost-analysis/metrics/{test_merchant_id}",
        params=time_range
    )
    assert response.status_code == 200
    metrics = response.json()
    assert isinstance(metrics, dict)

def test_simulate_cost_changes(test_merchant_id):
    """测试成本模拟端点"""
    scenarios = [
        {
            "category": "人工成本",
            "change_type": "increase",
            "percentage": 10
        },
        {
            "category": "原材料成本",
            "change_type": "decrease",
            "percentage": 5
        }
    ]
    
    response = client.post(
        "/api/v1/cost-analysis/simulate",
        json={
            "merchant_id": test_merchant_id,
            "scenarios": scenarios
        }
    )
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, dict)

def test_invalid_merchant_id():
    """测试无效商户ID的错误处理"""
    invalid_id = "INVALID_ID"
    response = client.get(f"/api/v1/cost-analysis/metrics/{invalid_id}")
    assert response.status_code == 500

def test_invalid_date_range(test_merchant_id):
    """测试无效日期范围的错误处理"""
    invalid_range = {
        "start_date": "2025-01-01T00:00:00",
        "end_date": "2024-01-01T00:00:00"  # 结束日期早于开始日期
    }
    
    response = client.get(
        f"/api/v1/cost-analysis/metrics/{test_merchant_id}",
        params=invalid_range
    )
    assert response.status_code == 500

def test_missing_required_fields():
    """测试缺少必填字段的错误处理"""
    incomplete_request = {
        "merchant_id": "TEST_MERCHANT_001"
        # 缺少 time_range 和 analysis_types
    }
    
    response = client.post("/api/v1/cost-analysis/analyze", json=incomplete_request)
    assert response.status_code == 422  # FastAPI的验证错误状态码
""" 
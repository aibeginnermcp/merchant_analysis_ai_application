import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
from datetime import date, timedelta

# 将父目录添加到导入路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入应用
from main import app

# 创建测试客户端
client = TestClient(app)

def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert response.json()["name"] == "成本穿透分析服务"
    assert "version" in response.json()
    assert "status" in response.json()
    assert response.json()["status"] == "运行中"

def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"
    assert "database" in response.json()

def test_debug_endpoint():
    """测试调试端点"""
    response = client.get("/debug")
    assert response.status_code == 200
    assert "timestamp" in response.json()
    assert "mongodb" in response.json()
    assert "hostname" in response.json()
    assert "network" in response.json()

def test_invalid_analyze_date_range():
    """测试成本分析API - 无效日期范围"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    response = client.post(
        "/api/v1/analyze",
        json={
            "merchant_id": "test123",
            "start_date": str(today),
            "end_date": str(yesterday),
            "analysis_depth": "detailed"
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "结束日期不能早于开始日期" in response.json()["detail"]

def test_invalid_analysis_depth():
    """测试成本分析API - 无效分析深度"""
    today = date.today()
    next_month = today + timedelta(days=30)
    
    response = client.post(
        "/api/v1/analyze",
        json={
            "merchant_id": "test123",
            "start_date": str(today),
            "end_date": str(next_month),
            "analysis_depth": "invalid_depth"
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "无效的分析深度参数" in response.json()["detail"]

def test_analyze_cost_successful():
    """测试成本分析API - 成功场景"""
    today = date.today()
    next_month = today + timedelta(days=30)
    
    response = client.post(
        "/api/v1/analyze",
        json={
            "merchant_id": "test123",
            "start_date": str(today),
            "end_date": str(next_month),
            "analysis_depth": "detailed"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "merchant_id" in data
    assert data["merchant_id"] == "test123"
    assert "total_cost" in data
    assert "cost_breakdown" in data
    assert len(data["cost_breakdown"]) > 0
    assert "optimization_suggestions" in data
    assert len(data["optimization_suggestions"]) > 0 
"""
成本分析服务 - 主模块测试套件
测试API端点和基本功能
"""
import os
import json
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
import sys

# 添加服务目录到path以便导入main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

# 创建测试客户端
client = TestClient(app)

def test_root_endpoint():
    """测试根端点返回服务基本信息"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    # 检查必要字段
    assert "name" in data
    assert "status" in data
    assert "version" in data
    assert data["name"] == "成本穿透分析服务"
    assert data["status"] == "运行中"

def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    # 检查健康状态
    assert data["status"] == "healthy"
    assert "database" in data
    assert "timestamp" in data

def test_debug_endpoint():
    """测试调试端点返回有用的系统信息"""
    response = client.get("/debug")
    assert response.status_code == 200
    data = response.json()
    
    # 检查关键调试信息字段
    assert "timestamp" in data
    assert "hostname" in data
    assert "python_version" in data
    assert "mongodb" in data

def test_analyze_endpoint_valid_input():
    """测试分析接口处理正确的输入数据"""
    # 创建有效的请求数据
    today = date.today()
    start_date = today - timedelta(days=90)
    end_date = today
    
    request_data = {
        "merchant_id": "test123",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "analysis_depth": "detailed"
    }
    
    response = client.post(
        "/api/v1/analyze",
        json=request_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # 检查响应结构
    assert "request_id" in data
    assert "merchant_id" in data
    assert "total_cost" in data
    assert "cost_breakdown" in data
    assert "optimization_suggestions" in data
    
    # 检查响应数据
    assert data["merchant_id"] == "test123"
    assert isinstance(data["total_cost"], (int, float))
    assert len(data["cost_breakdown"]) > 0
    assert len(data["optimization_suggestions"]) > 0

def test_analyze_endpoint_invalid_date():
    """测试分析接口对无效日期范围的处理"""
    # 创建结束日期早于开始日期的无效数据
    request_data = {
        "merchant_id": "test123",
        "start_date": "2023-03-01",
        "end_date": "2023-01-01",  # 结束日期早于开始日期
        "analysis_depth": "detailed"
    }
    
    response = client.post(
        "/api/v1/analyze",
        json=request_data
    )
    
    # 应该返回400错误
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "结束日期不能早于开始日期" in data["detail"]

def test_analyze_endpoint_invalid_depth():
    """测试分析接口对无效分析深度参数的处理"""
    # 创建分析深度参数无效的请求数据
    request_data = {
        "merchant_id": "test123",
        "start_date": "2023-01-01",
        "end_date": "2023-03-01",
        "analysis_depth": "invalid_depth"  # 无效的分析深度
    }
    
    response = client.post(
        "/api/v1/analyze",
        json=request_data
    )
    
    # 应该返回400错误
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "无效的分析深度参数" in data["detail"]

def test_ci_environment():
    """测试CI环境变量检测"""
    # 在CI环境中，应该跳过MongoDB连接尝试
    response = client.get("/")
    data = response.json()
    
    # 如果是在CI环境中运行
    if os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true":
        assert data["ci_environment"] == True
    else:
        # 本地运行时可以是任何值
        assert "ci_environment" in data

def test_mongodb_connection_handling():
    """测试MongoDB连接处理逻辑"""
    response = client.get("/health")
    data = response.json()
    
    # 无论MongoDB是否可用，服务都应该是健康的
    assert data["status"] == "healthy"
    assert "database" in data 
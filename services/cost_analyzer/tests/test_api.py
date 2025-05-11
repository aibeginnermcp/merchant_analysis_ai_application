"""
成本分析服务 API 测试模块

包含对成本分析服务API接口的功能测试
"""
import os
import sys
import json
from datetime import date, datetime, timedelta
import pytest
from fastapi.testclient import TestClient

# 添加服务目录到path以便导入main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 确保测试环境变量设置
os.environ["CI"] = "true"
os.environ["MONGODB_AVAILABLE"] = "false"
os.environ["DEBUG"] = "true"

from main import app

# 创建测试客户端
client = TestClient(app)

def test_root_endpoint():
    """测试根端点能正确返回服务信息"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    # 检查必要字段
    assert "name" in data
    assert "status" in data
    assert "version" in data
    assert data["name"] == "成本穿透分析服务"
    assert data["status"] == "运行中"
    
    # 验证CI环境
    assert data["ci_environment"] == True

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
    """测试调试端点"""
    response = client.get("/debug")
    assert response.status_code == 200
    data = response.json()
    
    # 检查关键字段
    assert "timestamp" in data
    assert "hostname" in data
    assert "python_version" in data
    assert "mongodb" in data
    assert "ci_environment" in data

def test_analyze_endpoint_valid_input():
    """测试分析接口能处理有效输入"""
    # 创建合法的请求数据
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
    
    # 验证内容
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
    # 创建无效分析深度参数的请求数据
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

def test_analyze_endpoint_missing_merchant_id():
    """测试分析接口对缺少必要参数的处理"""
    # 缺少商户ID的请求数据
    request_data = {
        "start_date": "2023-01-01",
        "end_date": "2023-03-01",
        "analysis_depth": "detailed"
    }
    
    response = client.post(
        "/api/v1/analyze", 
        json=request_data
    )
    
    # 应该返回422错误(请求实体无法处理)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_analyze_endpoint_idempotency():
    """测试分析接口的幂等性 - 相同输入应产生稳定结果"""
    # 创建请求数据
    request_data = {
        "merchant_id": "stable_merchant",
        "start_date": "2023-01-01",
        "end_date": "2023-03-01",
        "analysis_depth": "detailed"
    }
    
    # 第一次请求
    response1 = client.post("/api/v1/analyze", json=request_data)
    assert response1.status_code == 200
    data1 = response1.json()
    
    # 第二次相同请求
    response2 = client.post("/api/v1/analyze", json=request_data)
    assert response2.status_code == 200
    data2 = response2.json()
    
    # 验证核心业务数据是否稳定(请求ID会不同)
    assert data1["merchant_id"] == data2["merchant_id"]
    assert data1["total_cost"] == data2["total_cost"]
    assert len(data1["cost_breakdown"]) == len(data2["cost_breakdown"])
    
    # 验证成本结构稳定性
    for i, category in enumerate(data1["cost_breakdown"]):
        assert category["category"] == data2["cost_breakdown"][i]["category"]
        assert category["amount"] == data2["cost_breakdown"][i]["amount"]

def test_ci_environment_handling():
    """测试CI环境变量处理"""
    # 访问根端点检查环境
    response = client.get("/")
    data = response.json()
    
    # 验证CI环境设置
    assert data["ci_environment"] == True
    assert data["ci_mode"] == True
    assert data["mongodb_available"] == False
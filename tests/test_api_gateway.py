"""API网关测试模块"""
import pytest
from datetime import datetime, timedelta
from fastapi import FastAPI
from httpx import AsyncClient
from typing import Dict, Any

from services.api_gateway.models.merchant import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    AnalysisType
)

pytestmark = pytest.mark.asyncio

async def test_analyze_merchant(
    test_client,
    mock_data_simulator,
    mock_cashflow_client,
    mock_cost_analysis_client,
    mock_compliance_client
):
    """测试商户分析接口"""
    # 准备测试数据
    request_data = {
        "merchant_id": "test_merchant",
        "merchant_type": "restaurant",
        "time_range": {
            "start": datetime.now() - timedelta(days=30),
            "end": datetime.now()
        },
        "analysis_modules": [
            AnalysisType.CASH_FLOW,
            AnalysisType.COST,
            AnalysisType.COMPLIANCE
        ],
        "prediction_days": 30
    }
    
    # 发送请求
    response = await test_client.post(
        "/merchant/analyze",
        json=request_data
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] == request_data["merchant_id"]
    assert data["status"] == AnalysisStatus.COMPLETED
    assert "results" in data
    
    # 验证服务调用
    mock_data_simulator.generate_data.assert_called_once()
    mock_cashflow_client.predict.assert_called_once()
    mock_cost_analysis_client.analyze.assert_called_once()
    mock_compliance_client.check.assert_called_once()

async def test_get_analysis_result(
    test_client,
    mock_redis,
    mock_mongodb
):
    """测试获取分析结果接口"""
    # 准备测试数据
    analysis_id = "test_analysis"
    analysis_result = {
        "analysis_id": analysis_id,
        "merchant_id": "test_merchant",
        "status": AnalysisStatus.COMPLETED,
        "results": {}
    }
    
    # 模拟Redis缓存未命中
    mock_redis.get.return_value = None
    
    # 模拟MongoDB查询结果
    mock_mongodb.analysis_results.find_one.return_value = analysis_result
    
    # 发送请求
    response = await test_client.get(f"/merchant/analysis/{analysis_id}")
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == analysis_id
    assert data["status"] == AnalysisStatus.COMPLETED
    
    # 验证缓存操作
    mock_redis.get.assert_called_once()
    mock_redis.set.assert_called_once()
    
    # 验证数据库查询
    mock_mongodb.analysis_results.find_one.assert_called_once()

async def test_get_analysis_history(
    test_client,
    mock_mongodb
):
    """测试获取分析历史接口"""
    # 准备测试数据
    merchant_id = "test_merchant"
    history_data = [
        {
            "analysis_id": f"analysis_{i}",
            "merchant_id": merchant_id,
            "status": AnalysisStatus.COMPLETED,
            "results": {}
        }
        for i in range(5)
    ]
    
    # 模拟MongoDB查询结果
    mock_mongodb.analysis_results.count_documents.return_value = len(history_data)
    mock_mongodb.analysis_results.find.return_value = history_data
    
    # 发送请求
    response = await test_client.get(
        "/merchant/history",
        params={
            "merchant_id": merchant_id,
            "page": 1,
            "page_size": 10
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(history_data)
    assert len(data["results"]) == len(history_data)
    assert data["page"] == 1
    assert data["page_size"] == 10
    
    # 验证数据库查询
    mock_mongodb.analysis_results.count_documents.assert_called_once()
    mock_mongodb.analysis_results.find.assert_called_once()

async def test_analyze_merchant_error_handling(
    test_client,
    mock_data_simulator
):
    """测试商户分析接口错误处理"""
    # 模拟服务调用失败
    mock_data_simulator.generate_data.side_effect = Exception("Service unavailable")
    
    # 准备测试数据
    request_data = {
        "merchant_id": "test_merchant",
        "merchant_type": "restaurant",
        "time_range": {
            "start": datetime.now() - timedelta(days=30),
            "end": datetime.now()
        },
        "analysis_modules": [AnalysisType.CASH_FLOW],
        "prediction_days": 30
    }
    
    # 发送请求
    response = await test_client.post(
        "/merchant/analyze",
        json=request_data
    )
    
    # 验证响应
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert "Service unavailable" in data["error"]
    
    # 验证服务调用
    mock_data_simulator.generate_data.assert_called_once()

async def test_get_analysis_result_not_found(
    test_client,
    mock_redis,
    mock_mongodb
):
    """测试获取不存在的分析结果"""
    # 准备测试数据
    analysis_id = "non_existent_analysis"
    
    # 模拟Redis缓存未命中
    mock_redis.get.return_value = None
    
    # 模拟MongoDB查询结果为空
    mock_mongodb.analysis_results.find_one.return_value = None
    
    # 发送请求
    response = await test_client.get(f"/merchant/analysis/{analysis_id}")
    
    # 验证响应
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert analysis_id in data["error"]
    
    # 验证缓存和数据库操作
    mock_redis.get.assert_called_once()
    mock_mongodb.analysis_results.find_one.assert_called_once() 
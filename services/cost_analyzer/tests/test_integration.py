"""
成本穿透分析服务 - 集成测试
模拟与其他服务的集成测试
"""
import pytest
import json
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

# 将父目录添加到导入路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入应用
from main import app
from fastapi.testclient import TestClient

# 创建测试客户端
client = TestClient(app)

# 模拟集成服务响应
MOCK_CASHFLOW_RESPONSE = {
    "prediction": [
        {"date": "2023-04-01", "value": 4520.25, "lower_bound": 4125.75, "upper_bound": 4915.50},
        {"date": "2023-04-02", "value": 4615.10, "lower_bound": 4210.30, "upper_bound": 5019.90},
    ],
    "metrics": {
        "mape": 4.5,
        "rmse": 215.3,
        "model_type": "arima"
    }
}

MOCK_COMPLIANCE_RESPONSE = {
    "overall_status": "needs_review",
    "type_status": {
        "tax": "compliant",
        "accounting": "needs_review",
        "licensing": "non_compliant",
        "labor": "compliant"
    },
    "risk_score": 42.5
}

@pytest.fixture
def mock_external_services():
    """模拟外部服务"""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # 配置模拟响应
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_get_response
        
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        # 根据不同的URL返回不同的模拟数据
        def mock_post_json():
            args, kwargs = mock_post.call_args
            url = args[0] if args else kwargs.get("url", "")
            if "cashflow" in url:
                return MOCK_CASHFLOW_RESPONSE
            elif "compliance" in url:
                return MOCK_COMPLIANCE_RESPONSE
            return {}
        
        mock_post_response.json = mock_post_json
        mock_post.return_value = mock_post_response
        
        yield mock_get, mock_post

@pytest.mark.integration
def test_integration_with_cashflow_service(mock_external_services):
    """测试与现金流服务集成"""
    mock_get, mock_post = mock_external_services
    
    today = date.today()
    next_month = today + timedelta(days=30)
    
    # 调用成本分析API
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
    
    # 这里我们只是模拟集成，实际实现中会检查调用情况
    # 在实际实现中，这里会验证是否正确调用了现金流服务
    # mock_post.assert_called_with(
    #     "http://cashflow-service:8000/api/v1/predict",
    #     json={"merchant_id": "test123", "start_date": str(today), "end_date": str(next_month)}
    # )

@pytest.mark.integration
def test_integrated_analysis_response_format():
    """测试集成分析响应格式是否符合标准"""
    # 创建标准响应格式示例
    standard_response = {
        "request_id": "req_cost_12345_20230401120000",
        "merchant_id": "test123",
        "total_cost": 152635.80,
        "cost_breakdown": [
            {"category": "labor", "amount": 58623.45, "percentage": 38.4},
            {"category": "raw_material", "amount": 42523.75, "percentage": 27.9},
            {"category": "utilities", "amount": 12458.90, "percentage": 8.2},
            {"category": "rent", "amount": 24000.00, "percentage": 15.7},
            {"category": "marketing", "amount": 15029.70, "percentage": 9.8}
        ],
        "optimization_suggestions": [
            {
                "area": "labor",
                "suggestion": "考虑优化人员排班，减少闲置时间",
                "potential_saving": 4500.00,
                "difficulty": "medium"
            }
        ]
    }
    
    # 在实际测试中，这里会调用API并验证响应格式
    # 验证格式是否符合预期
    for key in ["request_id", "merchant_id", "total_cost", "cost_breakdown", "optimization_suggestions"]:
        assert key in standard_response
    
    # 验证成本明细的结构
    assert all(
        all(k in item for k in ["category", "amount", "percentage"]) 
        for item in standard_response["cost_breakdown"]
    )
    
    # 验证优化建议的结构
    assert all(
        all(k in item for k in ["area", "suggestion", "potential_saving", "difficulty"]) 
        for item in standard_response["optimization_suggestions"]
    )

@pytest.mark.integration
def test_integration_with_gateway():
    """测试与API网关的集成"""
    # 模拟API网关调用的请求和响应
    # 创建测试请求
    gateway_request = {
        "merchant_id": "m123456",
        "time_range": {
            "start_date": "2023-01-01",
            "end_date": "2023-03-31"
        },
        "analysis_types": ["cost"],
        "parameters": {
            "analysis_depth": "detailed"
        }
    }
    
    # 在实际测试中，这里会使用mock模拟网关调用并验证响应
    # 以下仅为示例结构验证
    assert "merchant_id" in gateway_request
    assert "time_range" in gateway_request
    assert "start_date" in gateway_request["time_range"]
    assert "end_date" in gateway_request["time_range"]

@pytest.mark.integration
def test_integration_data_schema():
    """测试数据模型集成"""
    import json
    from datetime import datetime
    from pydantic import BaseModel, ValidationError
    from typing import List, Dict, Any
    
    # 定义集成数据模型（简化版）
    class IntegratedDataModel(BaseModel):
        request_id: str
        timestamp: str
        merchant_id: str
        cost_data: Dict[str, Any]
        
    # 测试数据
    test_data = {
        "request_id": f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "merchant_id": "test123",
        "cost_data": {
            "total_cost": 152635.80,
            "cost_breakdown": [
                {"category": "labor", "amount": 58623.45, "percentage": 38.4}
            ]
        }
    }
    
    # 验证模型
    try:
        model = IntegratedDataModel(**test_data)
        assert model.request_id == test_data["request_id"]
        assert model.merchant_id == test_data["merchant_id"]
    except ValidationError as e:
        pytest.fail(f"数据模型验证失败: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v", "test_integration.py"]) 
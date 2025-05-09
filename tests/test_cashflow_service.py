"""
现金流预测服务测试模块

包含以下测试：
- 数据验证测试
- 预测模型测试
- API接口测试
- 监控功能测试
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from services.cashflow_predictor.service import CashflowPredictor
from services.cashflow_predictor.validators import (
    DataValidator,
    ValidationError,
    BusinessError
)
from services.cashflow_predictor.monitoring import (
    MetricsCollector,
    BusinessMetricsCollector
)
from services.cashflow_predictor.main import app

# 测试客户端
client = TestClient(app)

@pytest.fixture
def sample_cashflow_data():
    """样本现金流数据"""
    return {
        "id": "CF001",
        "merchant_id": "M001",
        "date": datetime.now(),
        "type": "inflow",
        "category": "sales",
        "amount": Decimal("1000.00"),
        "is_recurring": True,
        "probability": 0.95,
        "tags": ["retail", "online"]
    }

@pytest.fixture
def sample_prediction_request():
    """样本预测请求"""
    return {
        "merchant_id": "M001",
        "start_date": datetime.now() + timedelta(days=1),
        "end_date": datetime.now() + timedelta(days=30),
        "granularity": "daily"
    }

@pytest.fixture
def sample_historical_data():
    """样本历史数据"""
    data = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(365):
        date = base_date + timedelta(days=i)
        # 添加流入记录
        data.append({
            "id": f"CF{i*2+1}",
            "merchant_id": "M001",
            "date": date,
            "type": "inflow",
            "category": "sales",
            "amount": Decimal(str(1000 + np.random.normal(0, 100))),
            "is_recurring": True,
            "probability": 0.95,
            "tags": ["retail"]
        })
        # 添加流出记录
        data.append({
            "id": f"CF{i*2+2}",
            "merchant_id": "M001",
            "date": date,
            "type": "outflow",
            "category": "expenses",
            "amount": Decimal(str(800 + np.random.normal(0, 50))),
            "is_recurring": True,
            "probability": 0.9,
            "tags": ["operational"]
        })
    return data

class TestDataValidation:
    """数据验证测试"""
    
    def test_valid_cashflow_data(self, sample_cashflow_data):
        """测试有效的现金流数据"""
        try:
            DataValidator.validate_cashflow_data(sample_cashflow_data)
        except ValidationError:
            pytest.fail("Validation failed for valid data")
            
    def test_invalid_cashflow_type(self, sample_cashflow_data):
        """测试无效的现金流类型"""
        sample_cashflow_data["type"] = "invalid"
        with pytest.raises(ValidationError):
            DataValidator.validate_cashflow_data(sample_cashflow_data)
            
    def test_negative_amount(self, sample_cashflow_data):
        """测试负金额"""
        sample_cashflow_data["amount"] = Decimal("-100.00")
        with pytest.raises(ValidationError):
            DataValidator.validate_cashflow_data(sample_cashflow_data)
            
    def test_invalid_probability(self, sample_cashflow_data):
        """测试无效的概率值"""
        sample_cashflow_data["probability"] = 1.5
        with pytest.raises(ValidationError):
            DataValidator.validate_cashflow_data(sample_cashflow_data)

class TestPredictionModel:
    """预测模型测试"""
    
    @pytest.mark.asyncio
    async def test_prediction_flow(
        self,
        sample_historical_data,
        sample_prediction_request
    ):
        """测试预测流程"""
        predictor = CashflowPredictor()
        
        # 执行预测
        prediction = await predictor.predict_cashflow(
            sample_prediction_request["merchant_id"],
            sample_prediction_request["start_date"],
            sample_prediction_request["end_date"],
            sample_prediction_request["granularity"]
        )
        
        # 验证预测结果
        assert "inflow_prediction" in prediction
        assert "outflow_prediction" in prediction
        assert "net_cashflow" in prediction
        assert "confidence_intervals" in prediction
        assert "risk_assessment" in prediction
        assert "alerts" in prediction
        
    @pytest.mark.asyncio
    async def test_prediction_accuracy(
        self,
        sample_historical_data
    ):
        """测试预测准确性"""
        predictor = CashflowPredictor()
        
        # 分割数据集
        split_date = datetime.now() - timedelta(days=30)
        train_data = [
            d for d in sample_historical_data
            if d["date"] < split_date
        ]
        test_data = [
            d for d in sample_historical_data
            if d["date"] >= split_date
        ]
        
        # 执行预测
        prediction = await predictor.predict_cashflow(
            "M001",
            split_date,
            split_date + timedelta(days=30),
            "daily"
        )
        
        # 计算准确率
        actual_inflow = {
            d["date"].strftime("%Y-%m-%d"): float(d["amount"])
            for d in test_data
            if d["type"] == "inflow"
        }
        
        BusinessMetricsCollector.record_prediction_accuracy(
            "M001",
            prediction["inflow_prediction"],
            actual_inflow
        )

class TestAPIEndpoints:
    """API接口测试"""
    
    def test_predict_endpoint(self, sample_prediction_request):
        """测试预测接口"""
        response = client.post(
            "/api/v1/cashflow/predict",
            json=sample_prediction_request
        )
        assert response.status_code == 200
        data = response.json()
        assert "inflow_prediction" in data
        
    def test_pattern_endpoint(self):
        """测试模式分析接口"""
        response = client.get(
            "/api/v1/cashflow/pattern/M001",
            params={"lookback_days": 365}
        )
        assert response.status_code == 200
        
    def test_simulate_endpoint(self):
        """测试场景模拟接口"""
        scenarios = [{
            "name": "收入增长",
            "description": "模拟收入增长10%",
            "changes": [{
                "type": "inflow",
                "category": "sales",
                "change_type": "percentage",
                "value": 10
            }]
        }]
        
        response = client.post(
            "/api/v1/cashflow/simulate/M001",
            json={"scenarios": scenarios}
        )
        assert response.status_code == 200

class TestMonitoring:
    """监控功能测试"""
    
    def test_metrics_collection(self):
        """测试指标收集"""
        # 记录请求
        MetricsCollector.record_prediction_request(
            "M001",
            "daily"
        )
        
        # 记录延迟
        MetricsCollector.record_prediction_latency(
            "M001",
            "daily",
            0.5
        )
        
        # 记录错误
        MetricsCollector.record_prediction_error(
            "M001",
            "validation_error"
        )
        
    def test_business_metrics(self):
        """测试业务指标"""
        predicted = {
            "2024-01-01": 1000.0,
            "2024-01-02": 1100.0
        }
        actual = {
            "2024-01-01": 950.0,
            "2024-01-02": 1050.0
        }
        
        BusinessMetricsCollector.record_prediction_accuracy(
            "M001",
            predicted,
            actual
        )
        
    def test_alert_triggering(self):
        """测试告警触发"""
        metrics = {
            "accuracy": 0.65,
            "processing_time": 12,
            "error_rate": 0.06
        }
        
        from services.cashflow_predictor.monitoring import AlertManager
        AlertManager.check_and_alert("M001", metrics) 
"""
集成测试模块

测试现金流预测服务与其他服务的集成：
- 数据服务集成
- 监控服务集成
- API网关集成
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import json
import asyncio
from fastapi.testclient import TestClient

from services.cashflow_predictor.service import CashflowPredictor
from services.cashflow_predictor.monitoring import (
    MetricsCollector,
    BusinessMetricsCollector
)

@pytest.mark.integration
class TestServiceIntegration:
    """服务集成测试"""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """测试环境设置"""
        # 初始化服务
        self.predictor = CashflowPredictor()
        
        # 清理测试数据
        yield
        # 测试后清理
        
    async def test_end_to_end_prediction(self):
        """端到端预测测试"""
        # 准备测试数据
        merchant_id = "TEST001"
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=30)
        
        # 记录请求指标
        MetricsCollector.record_prediction_request(
            merchant_id,
            "daily"
        )
        
        try:
            # 执行预测
            prediction = await self.predictor.predict_cashflow(
                merchant_id,
                start_date,
                end_date,
                "daily"
            )
            
            # 验证预测结果
            assert prediction.inflow_prediction
            assert prediction.outflow_prediction
            assert prediction.net_cashflow
            assert prediction.confidence_intervals
            assert prediction.risk_assessment
            assert prediction.alerts
            
            # 记录业务指标
            BusinessMetricsCollector.record_prediction_accuracy(
                merchant_id,
                prediction.inflow_prediction,
                {"2024-01-01": 1000.0}  # 模拟实际值
            )
            
        except Exception as e:
            # 记录错误
            MetricsCollector.record_prediction_error(
                merchant_id,
                str(type(e).__name__)
            )
            raise
            
    async def test_monitoring_integration(self):
        """监控集成测试"""
        merchant_id = "TEST002"
        
        # 测试指标收集
        MetricsCollector.record_prediction_request(
            merchant_id,
            "daily"
        )
        
        MetricsCollector.record_prediction_latency(
            merchant_id,
            "daily",
            0.5
        )
        
        # 测试业务指标
        predicted = {
            "2024-01-01": 1000.0,
            "2024-01-02": 1100.0
        }
        actual = {
            "2024-01-01": 950.0,
            "2024-01-02": 1050.0
        }
        
        BusinessMetricsCollector.record_prediction_accuracy(
            merchant_id,
            predicted,
            actual
        )
        
        # 测试告警触发
        metrics = {
            "accuracy": 0.65,
            "processing_time": 12,
            "error_rate": 0.06
        }
        
        from services.cashflow_predictor.monitoring import AlertManager
        AlertManager.check_and_alert(merchant_id, metrics)
        
    @pytest.mark.asyncio
    async def test_data_processing_integration(self):
        """数据处理集成测试"""
        merchant_id = "TEST003"
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        
        # 获取历史数据
        historical_data = await self.predictor._get_historical_data(
            merchant_id,
            start_date,
            end_date
        )
        
        assert not historical_data.empty
        assert "date" in historical_data.columns
        assert "amount" in historical_data.columns
        assert "type" in historical_data.columns
        
        # 测试数据预处理
        inflow_data = historical_data[historical_data["type"] == "inflow"]
        prophet_data = self.predictor._prepare_prophet_data(
            inflow_data,
            "amount"
        )
        
        assert "ds" in prophet_data.columns
        assert "y" in prophet_data.columns
        
    @pytest.mark.asyncio
    async def test_api_integration(self):
        """API集成测试"""
        from services.cashflow_predictor.main import app
        client = TestClient(app)
        
        # 测试预测接口
        prediction_request = {
            "merchant_id": "TEST004",
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "granularity": "daily"
        }
        
        response = client.post(
            "/api/v1/cashflow/predict",
            json=prediction_request
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "inflow_prediction" in data
        assert "outflow_prediction" in data
        
        # 测试模式分析接口
        response = client.get(
            "/api/v1/cashflow/pattern/TEST004",
            params={"lookback_days": 365}
        )
        
        assert response.status_code == 200
        
        # 测试场景模拟接口
        simulation_request = {
            "scenarios": [{
                "name": "收入增长",
                "description": "模拟收入增长10%",
                "changes": [{
                    "type": "inflow",
                    "category": "sales",
                    "change_type": "percentage",
                    "value": 10
                }]
            }]
        }
        
        response = client.post(
            "/api/v1/cashflow/simulate/TEST004",
            json=simulation_request
        )
        
        assert response.status_code == 200 
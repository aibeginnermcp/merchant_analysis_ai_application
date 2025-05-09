"""现金流预测器模块"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

from .models import (
    CashFlowFeatures,
    CashFlowPrediction,
    CashFlowAnalysis,
    TrainingData
)

class CashFlowPredictor:
    """现金流预测器"""
    
    def __init__(self):
        self.model_path = "models/cash_flow_model.joblib"
        self.scaler_path = "models/feature_scaler.joblib"
        self.model = None
        self.scaler = None
        self._load_or_create_model()

    def _load_or_create_model(self):
        """加载或创建新模型"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
            else:
                self.model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                self.scaler = StandardScaler()
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.scaler = StandardScaler()

    def _prepare_features(self, data: List[CashFlowFeatures]) -> np.ndarray:
        """准备特征数据"""
        features = []
        for item in data:
            feature_vector = [
                item.day_of_week,
                int(item.is_weekend),
                int(item.is_holiday),
                item.month,
                item.quarter,
                item.revenue,
                item.transaction_count,
                item.average_transaction,
                item.total_cost,
                item.raw_material_cost,
                item.labor_cost,
                item.utility_cost,
                item.rent_cost,
                item.accounts_receivable,
                item.accounts_payable,
                item.inventory_value
            ]
            features.append(feature_vector)
        return np.array(features)

    def train(self, training_data: TrainingData):
        """训练模型"""
        features = self._prepare_features(training_data.features)
        targets = np.array(training_data.target_values)

        # 数据标准化
        features_scaled = self.scaler.fit_transform(features)

        # 分割训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            features_scaled, targets, test_size=0.2, random_state=42
        )

        # 训练模型
        self.model.fit(X_train, y_train)

        # 保存模型
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

        # 计算验证集性能
        val_score = self.model.score(X_val, y_val)
        return val_score

    def predict(self, features: List[CashFlowFeatures]) -> List[CashFlowPrediction]:
        """预测现金流"""
        if not self.model or not self.scaler:
            raise ValueError("模型未初始化")

        # 准备特征数据
        feature_matrix = self._prepare_features(features)
        feature_matrix_scaled = self.scaler.transform(feature_matrix)

        # 预测现金流
        predictions = []
        for i, feature in enumerate(features):
            # 预测现金流入和流出
            cash_inflow = self.model.predict([feature_matrix_scaled[i]])[0]
            cash_outflow = feature.total_cost + feature.accounts_payable
            net_cash_flow = cash_inflow - cash_outflow

            # 计算置信度（使用预测概率的标准差作为指标）
            predictions_array = []
            for estimator in self.model.estimators_:
                predictions_array.append(estimator.predict([feature_matrix_scaled[i]])[0])
            confidence_level = 1 - np.std(predictions_array) / np.mean(predictions_array)

            # 确定风险等级
            risk_level = self._assess_risk_level(net_cash_flow, confidence_level)

            predictions.append(
                CashFlowPrediction(
                    date=feature.date,
                    predicted_cash_inflow=cash_inflow,
                    predicted_cash_outflow=cash_outflow,
                    predicted_net_cash_flow=net_cash_flow,
                    confidence_level=confidence_level,
                    risk_level=risk_level
                )
            )

        return predictions

    def analyze_cash_flow(
        self,
        merchant_id: str,
        predictions: List[CashFlowPrediction]
    ) -> CashFlowAnalysis:
        """分析现金流状况"""
        # 计算基本统计指标
        daily_cash_flows = [p.predicted_net_cash_flow for p in predictions]
        avg_daily_cash_flow = np.mean(daily_cash_flows)
        volatility = np.std(daily_cash_flows) / abs(avg_daily_cash_flow)

        # 分析季节性模式
        seasonal_patterns = self._analyze_seasonality(predictions)

        # 生成风险评估和建议
        risk_assessment, recommendations = self._generate_recommendations(
            predictions, avg_daily_cash_flow, volatility
        )

        return CashFlowAnalysis(
            merchant_id=merchant_id,
            analysis_period=f"{predictions[0].date.date()} to {predictions[-1].date.date()}",
            predictions=predictions,
            average_daily_cash_flow=avg_daily_cash_flow,
            cash_flow_volatility=volatility,
            seasonal_patterns=seasonal_patterns,
            risk_assessment=risk_assessment,
            recommendations=recommendations
        )

    def _assess_risk_level(self, net_cash_flow: float, confidence_level: float) -> str:
        """评估风险等级"""
        if confidence_level < 0.5:
            return "高风险"
        elif net_cash_flow < 0:
            return "中风险"
        elif confidence_level < 0.8:
            return "低风险"
        else:
            return "安全"

    def _analyze_seasonality(
        self,
        predictions: List[CashFlowPrediction]
    ) -> Dict[str, Any]:
        """分析季节性模式"""
        monthly_averages = {}
        for pred in predictions:
            month = pred.date.month
            if month not in monthly_averages:
                monthly_averages[month] = []
            monthly_averages[month].append(pred.predicted_net_cash_flow)

        seasonal_patterns = {
            month: np.mean(values)
            for month, values in monthly_averages.items()
        }

        return {
            "monthly_patterns": seasonal_patterns,
            "peak_month": max(seasonal_patterns, key=seasonal_patterns.get),
            "low_month": min(seasonal_patterns, key=seasonal_patterns.get)
        }

    def _generate_recommendations(
        self,
        predictions: List[CashFlowPrediction],
        avg_daily_cash_flow: float,
        volatility: float
    ) -> Tuple[str, List[str]]:
        """生成风险评估和建议"""
        risk_assessment = "正常"
        recommendations = []

        # 评估现金流状况
        if avg_daily_cash_flow < 0:
            risk_assessment = "危险"
            recommendations.extend([
                "建议立即采取措施改善现金流状况",
                "考虑缩减非必要支出",
                "加快应收账款回收"
            ])
        elif volatility > 0.5:
            risk_assessment = "波动较大"
            recommendations.extend([
                "建议建立现金储备以应对波动",
                "考虑多元化经营降低风险",
                "优化库存管理减少资金占用"
            ])

        # 分析预测趋势
        negative_days = sum(1 for p in predictions if p.predicted_net_cash_flow < 0)
        if negative_days > len(predictions) * 0.3:
            risk_assessment = "需要注意"
            recommendations.extend([
                "预计未来可能出现现金流压力",
                "建议提前做好资金储备",
                "考虑开拓新的收入来源"
            ])

        return risk_assessment, recommendations 
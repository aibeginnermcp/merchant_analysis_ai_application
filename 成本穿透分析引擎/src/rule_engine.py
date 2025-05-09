"""
规则引擎模块

负责成本预警规则的管理和执行，包括：
- 规则定义和管理
- 规则匹配和执行
- 预警生成
- 风险评估
"""

from typing import Dict, List, Any
import pandas as pd
from datetime import datetime
from enum import Enum

class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Rule:
    """
    预警规则类
    
    Attributes:
        id (str): 规则ID
        name (str): 规则名称
        description (str): 规则描述
        condition (str): 规则条件
        risk_level (RiskLevel): 风险等级
        enabled (bool): 是否启用
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        condition: str,
        risk_level: RiskLevel,
        enabled: bool = True
    ):
        self.id = id
        self.name = name
        self.description = description
        self.condition = condition
        self.risk_level = risk_level
        self.enabled = enabled

class RuleEngine:
    """
    规则引擎类
    
    负责规则的管理和执行
    """
    
    def __init__(self):
        """初始化规则引擎"""
        self.rules: List[Rule] = []
        self._load_default_rules()
        
    def _load_default_rules(self):
        """加载默认规则"""
        default_rules = [
            Rule(
                id="COST_INCREASE_RATE",
                name="成本增长率预警",
                description="月环比成本增长超过阈值",
                condition="cost_increase_rate > 0.2",  # 20%
                risk_level=RiskLevel.MEDIUM
            ),
            Rule(
                id="HIGH_COST_RATIO",
                name="高成本占比预警",
                description="成本收入比超过阈值",
                condition="cost_revenue_ratio > 0.8",  # 80%
                risk_level=RiskLevel.HIGH
            ),
            Rule(
                id="COST_CONCENTRATION",
                name="成本集中度预警",
                description="单一成本类别占比过高",
                condition="max_category_ratio > 0.5",  # 50%
                risk_level=RiskLevel.MEDIUM
            ),
            Rule(
                id="FIXED_COST_RATIO",
                name="固定成本占比预警",
                description="固定成本占比过高",
                condition="fixed_cost_ratio > 0.7",  # 70%
                risk_level=RiskLevel.MEDIUM
            ),
            Rule(
                id="NEGATIVE_MARGIN",
                name="负毛利预警",
                description="毛利率为负",
                condition="gross_margin < 0",
                risk_level=RiskLevel.CRITICAL
            )
        ]
        
        self.rules.extend(default_rules)
        
    def add_rule(self, rule: Rule):
        """
        添加规则
        
        Args:
            rule: 预警规则
        """
        self.rules.append(rule)
            
    def remove_rule(self, rule_id: str):
        """
        移除规则
        
        Args:
            rule_id: 规则ID
        """
        self.rules = [r for r in self.rules if r.id != rule_id]
        
    def enable_rule(self, rule_id: str):
        """
        启用规则
        
        Args:
            rule_id: 规则ID
        """
        for rule in self.rules:
            if rule.id == rule_id:
                rule.enabled = True
                break
                
    def disable_rule(self, rule_id: str):
        """
        禁用规则
        
        Args:
            rule_id: 规则ID
        """
        for rule in self.rules:
            if rule.id == rule_id:
                rule.enabled = False
                break
                
    def check_cost_alerts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查成本预警
        
        Args:
            data: 成本数据
            
        Returns:
            预警分析结果
        """
        df = pd.DataFrame(data["raw_data"])
        aggregated = data["aggregated"]
        
        alerts = []
        highest_risk = RiskLevel.LOW
        
        # 计算指标
        metrics = self._calculate_alert_metrics(df, aggregated)
        
        # 检查每个规则
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            # 评估规则条件
            if self._evaluate_condition(rule.condition, metrics):
                alert = {
                    "rule_id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "risk_level": rule.risk_level.value,
                    "triggered_value": self._get_triggered_value(
                        rule.condition,
                        metrics
                    ),
                    "timestamp": datetime.now().isoformat()
                }
                alerts.append(alert)
                
                # 更新最高风险等级
                if rule.risk_level.value > highest_risk.value:
                    highest_risk = rule.risk_level
                    
        # 生成改进建议
        recommendations = self._generate_recommendations(alerts, metrics)
        
        return {
            "alerts": alerts,
            "risk_level": highest_risk.value,
            "recommendations": recommendations
        }
        
    def _calculate_alert_metrics(
        self,
        df: pd.DataFrame,
        aggregated: Dict
    ) -> Dict[str, float]:
        """计算预警指标"""
        metrics = {}
        
        # 计算成本增长率
        if len(df) >= 2:
            df = df.sort_values("date")
            first_month = df.iloc[0]["amount"]
            last_month = df.iloc[-1]["amount"]
            metrics["cost_increase_rate"] = (
                (last_month - first_month) / first_month
            )
            
        # 计算成本收入比
        if "revenue" in df.columns:
            total_cost = aggregated["statistics"]["total_amount"]
            total_revenue = df["revenue"].sum()
            metrics["cost_revenue_ratio"] = total_cost / total_revenue
            
        # 计算成本集中度
        total_cost = aggregated["statistics"]["total_amount"]
        max_category_cost = max(
            stats["amount"]["sum"]
            for stats in aggregated["by_category"].values()
        )
        metrics["max_category_ratio"] = max_category_cost / total_cost
        
        # 计算固定成本占比
        if "is_fixed" in df.columns:
            fixed_cost = df[df["is_fixed"]]["amount"].sum()
            metrics["fixed_cost_ratio"] = fixed_cost / total_cost
            
        # 计算毛利率
        if "revenue" in df.columns:
            gross_profit = total_revenue - total_cost
            metrics["gross_margin"] = gross_profit / total_revenue
            
        return metrics
        
    def _evaluate_condition(
        self,
        condition: str,
        metrics: Dict[str, float]
    ) -> bool:
        """评估规则条件"""
        try:
            # 将指标注入本地命名空间
            locals().update(metrics)
            # 评估条件
            return eval(condition)
        except Exception:
            return False
            
    def _get_triggered_value(
        self,
        condition: str,
        metrics: Dict[str, float]
    ) -> float:
        """获取触发值"""
        try:
            # 从条件中提取指标名称
            metric_name = condition.split()[0]
            return metrics.get(metric_name, 0)
        except Exception:
            return 0
            
    def _generate_recommendations(
        self,
        alerts: List[Dict],
        metrics: Dict[str, float]
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for alert in alerts:
            if alert["rule_id"] == "COST_INCREASE_RATE":
                recommendations.append(
                    "建议分析成本增长的主要驱动因素，制定成本控制计划"
                )
            elif alert["rule_id"] == "HIGH_COST_RATIO":
                recommendations.append(
                    "建议优化成本结构，提高运营效率，考虑提价或开源节流"
                )
            elif alert["rule_id"] == "COST_CONCENTRATION":
                recommendations.append(
                    "建议适当分散成本结构，降低对单一成本类别的依赖"
                )
            elif alert["rule_id"] == "FIXED_COST_RATIO":
                recommendations.append(
                    "建议评估将部分固定成本转化为变动成本的可能性，提高成本弹性"
                )
            elif alert["rule_id"] == "NEGATIVE_MARGIN":
                recommendations.append(
                    "建议立即评估定价策略和成本结构，采取紧急措施扭转亏损局面"
                )
                
        return recommendations 
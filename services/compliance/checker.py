"""合规检查器模块"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import re
from .models import (
    ComplianceRule,
    ComplianceViolation,
    ComplianceMetrics,
    ComplianceReport,
    ComplianceAlert,
    ComplianceRequirement,
    ComplianceStatus
)

class ComplianceChecker:
    """合规检查器"""
    
    def __init__(self):
        """初始化合规检查器"""
        self.rules = self._init_compliance_rules()
        self.requirements = self._init_compliance_requirements()
        
    def _init_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """初始化合规规则"""
        rules = {}
        
        # 财务合规规则
        rules["FIN001"] = ComplianceRule(
            rule_id="FIN001",
            category="财务",
            name="现金流健康度",
            description="检查现金流状况是否健康",
            severity="高",
            check_method="阈值",
            parameters={
                "min_cash_ratio": 0.2,
                "min_quick_ratio": 1.0,
                "max_debt_ratio": 0.7
            }
        )
        
        rules["FIN002"] = ComplianceRule(
            rule_id="FIN002",
            category="财务",
            name="异常交易监控",
            description="检查是否存在异常交易模式",
            severity="高",
            check_method="模式匹配",
            parameters={
                "max_single_transaction": 50000,
                "suspicious_patterns": [
                    "频繁小额交易",
                    "大额现金交易",
                    "跨境异常支付"
                ]
            }
        )
        
        # 经营合规规则
        rules["OPS001"] = ComplianceRule(
            rule_id="OPS001",
            category="经营",
            name="营业时间合规",
            description="检查营业时间是否符合规定",
            severity="中",
            check_method="时间序列",
            parameters={
                "allowed_hours": {
                    "weekday": {"start": "07:00", "end": "22:00"},
                    "weekend": {"start": "08:00", "end": "23:00"}
                }
            }
        )
        
        rules["OPS002"] = ComplianceRule(
            rule_id="OPS002",
            category="经营",
            name="库存管理",
            description="检查库存管理是否规范",
            severity="中",
            check_method="阈值",
            parameters={
                "max_inventory_days": 30,
                "min_turnover_rate": 3
            }
        )
        
        # 安全合规规则
        rules["SEC001"] = ComplianceRule(
            rule_id="SEC001",
            category="安全",
            name="消防安全",
            description="检查消防设施是否符合要求",
            severity="高",
            check_method="清单",
            parameters={
                "required_equipment": [
                    "灭火器",
                    "烟感器",
                    "应急照明",
                    "安全出口标识"
                ]
            }
        )
        
        return rules
        
    def _init_compliance_requirements(self) -> List[ComplianceRequirement]:
        """初始化合规要求"""
        return [
            ComplianceRequirement(
                category="许可证",
                name="营业执照",
                description="基础营业资质",
                required_documents=["营业执照正本", "营业执照副本"],
                renewal_period=365,
                validation_rules=[
                    {"type": "expiration", "period": 365},
                    {"type": "completeness", "fields": ["注册号", "经营范围", "有效期"]}
                ]
            ),
            ComplianceRequirement(
                category="许可证",
                name="食品经营许可证",
                description="食品经营资质",
                required_documents=["许可证正本", "健康证明"],
                renewal_period=180,
                validation_rules=[
                    {"type": "expiration", "period": 180},
                    {"type": "category", "values": ["食品经营", "餐饮服务"]}
                ]
            ),
            ComplianceRequirement(
                category="安全",
                name="消防安全检查",
                description="场所消防安全检查",
                required_documents=["消防检查报告", "整改记录"],
                renewal_period=90,
                validation_rules=[
                    {"type": "expiration", "period": 90},
                    {"type": "status", "values": ["合格", "基本合格"]}
                ]
            )
        ]
        
    def check_compliance(
        self,
        merchant_id: str,
        historical_data: Dict[str, Any],
        current_status: Dict[str, Any]
    ) -> ComplianceReport:
        """执行合规检查"""
        violations = []
        total_checks = 0
        passed_checks = 0
        
        # 检查财务合规
        fin_violations = self._check_financial_compliance(
            historical_data.get("financials", []),
            historical_data.get("transactions", [])
        )
        violations.extend(fin_violations)
        total_checks += 2
        passed_checks += 2 - len(fin_violations)
        
        # 检查经营合规
        ops_violations = self._check_operational_compliance(
            historical_data.get("transactions", []),
            historical_data.get("inventory", [])
        )
        violations.extend(ops_violations)
        total_checks += 2
        passed_checks += 2 - len(ops_violations)
        
        # 检查安全合规
        safety_violations = self._check_safety_compliance(
            current_status.get("safety_equipment", []),
            current_status.get("safety_records", [])
        )
        violations.extend(safety_violations)
        total_checks += 1
        passed_checks += 1 - len(safety_violations)
        
        # 计算合规指标
        metrics = self._calculate_compliance_metrics(
            total_checks,
            passed_checks,
            violations
        )
        
        # 生成风险评估和建议
        risk_assessment, suggestions = self._generate_risk_assessment(
            metrics,
            violations
        )
        
        return ComplianceReport(
            merchant_id=merchant_id,
            report_period=f"{historical_data['start_date']} to {historical_data['end_date']}",
            metrics=metrics,
            violations=violations,
            risk_assessment=risk_assessment,
            improvement_suggestions=suggestions,
            next_review_date=datetime.now() + timedelta(days=30)
        )
        
    def _check_financial_compliance(
        self,
        financials: List[Dict[str, Any]],
        transactions: List[Dict[str, Any]]
    ) -> List[ComplianceViolation]:
        """检查财务合规"""
        violations = []
        
        # 检查现金流健康度
        if financials:
            latest = financials[-1]
            cash_ratio = latest.get("cash", 0) / latest.get("current_liabilities", 1)
            if cash_ratio < self.rules["FIN001"].parameters["min_cash_ratio"]:
                violations.append(
                    ComplianceViolation(
                        rule_id="FIN001",
                        timestamp=datetime.now(),
                        severity="高",
                        description=f"现金比率({cash_ratio:.2f})低于最低要求({self.rules['FIN001'].parameters['min_cash_ratio']})",
                        evidence={"cash_ratio": cash_ratio},
                        suggested_actions=[
                            "加强应收账款管理",
                            "优化库存周转",
                            "考虑引入外部融资"
                        ]
                    )
                )
                
        # 检查异常交易
        if transactions:
            large_transactions = [
                t for t in transactions
                if t["amount"] > self.rules["FIN002"].parameters["max_single_transaction"]
            ]
            if large_transactions:
                violations.append(
                    ComplianceViolation(
                        rule_id="FIN002",
                        timestamp=datetime.now(),
                        severity="高",
                        description=f"发现{len(large_transactions)}笔超额交易",
                        evidence={"transactions": large_transactions},
                        suggested_actions=[
                            "完善大额交易审批流程",
                            "加强交易监控",
                            "保存交易相关单据"
                        ]
                    )
                )
                
        return violations
        
    def _check_operational_compliance(
        self,
        transactions: List[Dict[str, Any]],
        inventory: List[Dict[str, Any]]
    ) -> List[ComplianceViolation]:
        """检查经营合规"""
        violations = []
        
        # 检查营业时间
        if transactions:
            for transaction in transactions:
                transaction_time = datetime.fromisoformat(transaction["timestamp"])
                allowed_hours = self.rules["OPS001"].parameters["allowed_hours"]
                
                is_weekend = transaction_time.weekday() >= 5
                hours = allowed_hours["weekend"] if is_weekend else allowed_hours["weekday"]
                
                if not self._is_within_business_hours(transaction_time, hours):
                    violations.append(
                        ComplianceViolation(
                            rule_id="OPS001",
                            timestamp=transaction_time,
                            severity="中",
                            description="营业时间不符合规定",
                            evidence={"transaction": transaction},
                            suggested_actions=[
                                "调整营业时间",
                                "设置营业时间提醒",
                                "加强员工培训"
                            ]
                        )
                    )
                    
        # 检查库存管理
        if inventory:
            inventory_days = self._calculate_inventory_days(inventory)
            if inventory_days > self.rules["OPS002"].parameters["max_inventory_days"]:
                violations.append(
                    ComplianceViolation(
                        rule_id="OPS002",
                        timestamp=datetime.now(),
                        severity="中",
                        description=f"库存周转天数({inventory_days:.1f})超过上限({self.rules['OPS002'].parameters['max_inventory_days']})",
                        evidence={"inventory_days": inventory_days},
                        suggested_actions=[
                            "优化库存管理",
                            "加强需求预测",
                            "考虑促销清理库存"
                        ]
                    )
                )
                
        return violations
        
    def _check_safety_compliance(
        self,
        equipment: List[Dict[str, Any]],
        records: List[Dict[str, Any]]
    ) -> List[ComplianceViolation]:
        """检查安全合规"""
        violations = []
        
        # 检查消防设施
        required = set(self.rules["SEC001"].parameters["required_equipment"])
        installed = set(e["name"] for e in equipment)
        missing = required - installed
        
        if missing:
            violations.append(
                ComplianceViolation(
                    rule_id="SEC001",
                    timestamp=datetime.now(),
                    severity="高",
                    description=f"缺少必要的消防设施: {', '.join(missing)}",
                    evidence={"missing_equipment": list(missing)},
                    suggested_actions=[
                        "及时补充缺失的消防设施",
                        "定期检查设施状态",
                        "建立设施维护记录"
                    ]
                )
            )
            
        return violations
        
    def _calculate_compliance_metrics(
        self,
        total_checks: int,
        passed_checks: int,
        violations: List[ComplianceViolation]
    ) -> ComplianceMetrics:
        """计算合规指标"""
        high_risk_count = sum(1 for v in violations if v.severity == "高")
        compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        return ComplianceMetrics(
            total_checks=total_checks,
            passed_checks=passed_checks,
            violation_count=len(violations),
            high_risk_count=high_risk_count,
            compliance_score=compliance_score,
            trend=0.0  # 需要历史数据计算趋势
        )
        
    def _generate_risk_assessment(
        self,
        metrics: ComplianceMetrics,
        violations: List[ComplianceViolation]
    ) -> Tuple[str, List[str]]:
        """生成风险评估和建议"""
        # 评估风险等级
        if metrics.high_risk_count > 0 or metrics.compliance_score < 60:
            risk_level = "高"
        elif metrics.violation_count > 2 or metrics.compliance_score < 80:
            risk_level = "中"
        else:
            risk_level = "低"
            
        # 生成改进建议
        suggestions = []
        if metrics.high_risk_count > 0:
            suggestions.append(
                "存在高风险违规项，需要立即整改：\n" +
                "\n".join(f"- {v.description}" for v in violations if v.severity == "高")
            )
            
        if metrics.compliance_score < 80:
            suggestions.append(
                "合规得分较低，建议：\n"
                "1. 全面梳理合规状况\n"
                "2. 制定整改计划\n"
                "3. 加强员工合规培训"
            )
            
        if metrics.violation_count > 0:
            by_category = {}
            for v in violations:
                rule = self.rules[v.rule_id]
                if rule.category not in by_category:
                    by_category[rule.category] = []
                by_category[rule.category].append(v)
                
            for category, category_violations in by_category.items():
                suggestions.append(
                    f"{category}方面存在{len(category_violations)}项违规，建议：\n" +
                    "\n".join(f"- {v.suggested_actions[0]}" for v in category_violations)
                )
                
        return risk_level, suggestions
        
    def _is_within_business_hours(
        self,
        timestamp: datetime,
        allowed_hours: Dict[str, str]
    ) -> bool:
        """检查是否在营业时间内"""
        time_str = timestamp.strftime("%H:%M")
        return allowed_hours["start"] <= time_str <= allowed_hours["end"]
        
    def _calculate_inventory_days(
        self,
        inventory: List[Dict[str, Any]]
    ) -> float:
        """计算库存周转天数"""
        if not inventory:
            return 0
            
        avg_inventory = sum(i["value"] for i in inventory) / len(inventory)
        daily_cost = sum(i["cost"] for i in inventory) / len(inventory)
        
        return avg_inventory / daily_cost if daily_cost > 0 else float('inf')
        
    def generate_alert(
        self,
        violation: ComplianceViolation,
        merchant_id: str
    ) -> ComplianceAlert:
        """生成合规预警"""
        rule = self.rules[violation.rule_id]
        
        return ComplianceAlert(
            alert_id=f"ALT-{violation.rule_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            merchant_id=merchant_id,
            timestamp=datetime.now(),
            severity=violation.severity,
            title=f"{rule.category}合规警告：{rule.name}",
            description=violation.description,
            affected_rules=[violation.rule_id],
            required_actions=violation.suggested_actions,
            deadline=datetime.now() + timedelta(days=7)  # 默认7天整改期
        ) 
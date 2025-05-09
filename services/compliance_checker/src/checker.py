"""
财务合规检查服务的检查引擎，实现各类合规检查逻辑
"""
import uuid
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
import re

from services.compliance_checker.src.models import (
    TimeRange,
    ComplianceType,
    RiskLevel,
    ComplianceStatus,
    DocumentType,
    ComplianceRule,
    ComplianceViolation,
    ComplianceDocument,
    ComplianceCheckResult
)

logger = logging.getLogger("compliance_checker.checker")

class BaseRuleChecker:
    """规则检查器基类"""
    
    def __init__(self, rule: ComplianceRule):
        """
        初始化规则检查器
        
        Args:
            rule: 合规规则
        """
        self.rule = rule
        
    def check(self, data: Dict[str, Any], merchant_type: str) -> Optional[ComplianceViolation]:
        """
        检查合规性
        
        Args:
            data: 商户数据
            merchant_type: 商户类型
            
        Returns:
            如果违规则返回违规对象，否则返回None
        """
        # 检查规则是否适用于此类商户
        if merchant_type not in self.rule.applies_to:
            return None
            
        return self._check_implementation(data)
        
    def _check_implementation(self, data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """
        实现具体的检查逻辑，由子类实现
        
        Args:
            data: 商户数据
            
        Returns:
            如果违规则返回违规对象，否则返回None
        """
        raise NotImplementedError("子类必须实现此方法")

class TaxComplianceChecker(BaseRuleChecker):
    """税务合规检查器"""
    
    def _check_implementation(self, data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """
        检查税务合规性
        
        Args:
            data: 商户数据
            
        Returns:
            如果违规则返回违规对象，否则返回None
        """
        merchant_id = data.get("merchant_id")
        transactions = data.get("transactions", [])
        tax_records = data.get("tax_records", [])
        
        # 检查是否有漏报的交易
        reported_transaction_ids = {record.get("transaction_id") for record in tax_records if record.get("transaction_id")}
        unreported_transactions = [t for t in transactions if t.get("transaction_id") not in reported_transaction_ids]
        
        if unreported_transactions:
            unreported_amount = sum(t.get("amount", 0) for t in unreported_transactions)
            threshold = self.rule.threshold.get("unreported_amount", 10000)
            
            if unreported_amount > threshold:
                # 创建违规记录
                return ComplianceViolation(
                    violation_id=f"v_{uuid.uuid4().hex[:8]}",
                    merchant_id=merchant_id,
                    rule_id=self.rule.rule_id,
                    type=ComplianceType.TAX,
                    description=f"发现未报税交易金额 {unreported_amount} 元，超过阈值 {threshold} 元",
                    detection_date=datetime.now(),
                    risk_level=RiskLevel.HIGH,
                    resolution_deadline=datetime.now() + timedelta(days=30),
                    evidence={
                        "unreported_amount": unreported_amount,
                        "threshold": threshold,
                        "unreported_transaction_count": len(unreported_transactions),
                        "unreported_transaction_ids": [t.get("transaction_id") for t in unreported_transactions[:10]]
                    }
                )
        
        # 检查税率是否正确
        incorrect_tax_records = []
        for record in tax_records:
            transaction_amount = record.get("transaction_amount", 0)
            tax_amount = record.get("tax_amount", 0)
            expected_tax_rate = self.rule.threshold.get("tax_rate", 0.13)  # 假设增值税率为13%
            actual_tax_rate = tax_amount / transaction_amount if transaction_amount else 0
            
            # 允许一定的误差
            tolerance = 0.01
            if abs(actual_tax_rate - expected_tax_rate) > tolerance:
                incorrect_tax_records.append(record)
        
        if incorrect_tax_records:
            return ComplianceViolation(
                violation_id=f"v_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant_id,
                rule_id=self.rule.rule_id,
                type=ComplianceType.TAX,
                description=f"发现 {len(incorrect_tax_records)} 条税率不正确的记录",
                detection_date=datetime.now(),
                risk_level=RiskLevel.MEDIUM,
                resolution_deadline=datetime.now() + timedelta(days=15),
                evidence={
                    "incorrect_record_count": len(incorrect_tax_records),
                    "expected_tax_rate": self.rule.threshold.get("tax_rate"),
                    "sample_records": incorrect_tax_records[:5]
                }
            )
        
        return None

class AccountingComplianceChecker(BaseRuleChecker):
    """会计准则合规检查器"""
    
    def _check_implementation(self, data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """
        检查会计准则合规性
        
        Args:
            data: 商户数据
            
        Returns:
            如果违规则返回违规对象，否则返回None
        """
        merchant_id = data.get("merchant_id")
        transactions = data.get("transactions", [])
        
        # 检查是否有大额未分类交易
        unclassified_transactions = [t for t in transactions if not t.get("category")]
        if unclassified_transactions:
            unclassified_amount = sum(t.get("amount", 0) for t in unclassified_transactions)
            threshold = self.rule.threshold.get("unclassified_amount", 5000)
            
            if unclassified_amount > threshold:
                return ComplianceViolation(
                    violation_id=f"v_{uuid.uuid4().hex[:8]}",
                    merchant_id=merchant_id,
                    rule_id=self.rule.rule_id,
                    type=ComplianceType.ACCOUNTING,
                    description=f"发现未分类交易金额 {unclassified_amount} 元，超过阈值 {threshold} 元",
                    detection_date=datetime.now(),
                    risk_level=RiskLevel.MEDIUM,
                    resolution_deadline=datetime.now() + timedelta(days=7),
                    evidence={
                        "unclassified_amount": unclassified_amount,
                        "threshold": threshold,
                        "unclassified_transaction_count": len(unclassified_transactions),
                        "unclassified_transaction_ids": [t.get("transaction_id") for t in unclassified_transactions[:10]]
                    }
                )
        
        # 检查借贷是否平衡
        debits = sum(t.get("amount", 0) for t in transactions if t.get("type") == "debit")
        credits = sum(t.get("amount", 0) for t in transactions if t.get("type") == "credit")
        imbalance = abs(debits - credits)
        balance_threshold = self.rule.threshold.get("balance_threshold", 0.01)
        
        if imbalance > balance_threshold:
            return ComplianceViolation(
                violation_id=f"v_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant_id,
                rule_id=self.rule.rule_id,
                type=ComplianceType.ACCOUNTING,
                description=f"借贷不平衡，差额为 {imbalance} 元",
                detection_date=datetime.now(),
                risk_level=RiskLevel.HIGH,
                resolution_deadline=datetime.now() + timedelta(days=3),
                evidence={
                    "debits": debits,
                    "credits": credits,
                    "imbalance": imbalance,
                    "threshold": balance_threshold
                }
            )
        
        return None

class LicensingComplianceChecker(BaseRuleChecker):
    """许可证合规检查器"""
    
    def _check_implementation(self, data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """
        检查许可证合规性
        
        Args:
            data: 商户数据
            
        Returns:
            如果违规则返回违规对象，否则返回None
        """
        merchant_id = data.get("merchant_id")
        documents = data.get("documents", [])
        required_license_types = self.rule.threshold.get("required_license_types", [])
        
        # 获取所有有效的许可证
        valid_licenses = {doc.get("type"): doc for doc in documents 
                          if doc.get("type") in required_license_types and doc.get("status") == "valid"}
        
        # 检查是否缺少必要的许可证
        missing_licenses = [license_type for license_type in required_license_types if license_type not in valid_licenses]
        
        if missing_licenses:
            return ComplianceViolation(
                violation_id=f"v_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant_id,
                rule_id=self.rule.rule_id,
                type=ComplianceType.LICENSING,
                description=f"缺少必要的许可证：{', '.join(missing_licenses)}",
                detection_date=datetime.now(),
                risk_level=RiskLevel.CRITICAL,
                resolution_deadline=datetime.now() + timedelta(days=30),
                evidence={
                    "missing_licenses": missing_licenses,
                    "required_licenses": required_license_types,
                    "existing_licenses": list(valid_licenses.keys())
                }
            )
        
        # 检查许可证是否即将过期
        now = datetime.now()
        expiring_soon = []
        
        for license_type, doc in valid_licenses.items():
            expiry_date = doc.get("expiry_date")
            if expiry_date and isinstance(expiry_date, datetime):
                days_until_expiry = (expiry_date - now).days
                warning_days = self.rule.threshold.get("expiry_warning_days", 30)
                
                if days_until_expiry <= warning_days:
                    expiring_soon.append({
                        "license_type": license_type,
                        "days_until_expiry": days_until_expiry,
                        "expiry_date": expiry_date.isoformat()
                    })
        
        if expiring_soon:
            return ComplianceViolation(
                violation_id=f"v_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant_id,
                rule_id=self.rule.rule_id,
                type=ComplianceType.LICENSING,
                description=f"有 {len(expiring_soon)} 个许可证即将过期",
                detection_date=datetime.now(),
                risk_level=RiskLevel.MEDIUM,
                resolution_deadline=datetime.now() + timedelta(days=15),
                evidence={
                    "expiring_licenses": expiring_soon,
                    "warning_days": self.rule.threshold.get("expiry_warning_days")
                }
            )
        
        return None

class DocumentValidator:
    """文档验证器"""
    
    def validate_documents(self, documents: List[ComplianceDocument]) -> Dict[DocumentType, str]:
        """
        验证文档状态
        
        Args:
            documents: 文档列表
            
        Returns:
            各类型文档的状态
        """
        now = datetime.now()
        document_status = {}
        
        # 按类型分组
        documents_by_type = {}
        for doc in documents:
            if doc.type not in documents_by_type:
                documents_by_type[doc.type] = []
            documents_by_type[doc.type].append(doc)
        
        # 检查每种类型的文档状态
        for doc_type, docs in documents_by_type.items():
            # 按状态分组
            valid_docs = [d for d in docs if d.status == "valid"]
            expired_docs = [d for d in docs if d.status == "expired"]
            revoked_docs = [d for d in docs if d.status == "revoked"]
            
            # 如果有有效文档，检查是否即将过期
            if valid_docs:
                # 获取最新的有效文档
                latest_valid = max(valid_docs, key=lambda d: d.issue_date)
                
                if latest_valid.expiry_date:
                    days_until_expiry = (latest_valid.expiry_date - now).days
                    
                    if days_until_expiry < 0:
                        document_status[doc_type] = "expired"
                    elif days_until_expiry <= 30:
                        document_status[doc_type] = "expiring_soon"
                    else:
                        document_status[doc_type] = "valid"
                else:
                    document_status[doc_type] = "valid"
            elif expired_docs:
                document_status[doc_type] = "expired"
            elif revoked_docs:
                document_status[doc_type] = "revoked"
            else:
                document_status[doc_type] = "missing"
        
        return document_status

class ComplianceChecker:
    """合规检查引擎，整合各类检查功能"""
    
    def __init__(self):
        """初始化合规检查引擎"""
        self.logger = logging.getLogger("compliance_checker")
        self.document_validator = DocumentValidator()
        self.rule_checkers = {}  # 规则ID到检查器的映射
        
    def register_rule(self, rule: ComplianceRule) -> None:
        """
        注册规则检查器
        
        Args:
            rule: 合规规则
        """
        if rule.type == ComplianceType.TAX:
            self.rule_checkers[rule.rule_id] = TaxComplianceChecker(rule)
        elif rule.type == ComplianceType.ACCOUNTING:
            self.rule_checkers[rule.rule_id] = AccountingComplianceChecker(rule)
        elif rule.type == ComplianceType.LICENSING:
            self.rule_checkers[rule.rule_id] = LicensingComplianceChecker(rule)
        else:
            self.logger.warning(f"未支持的规则类型: {rule.type}")
    
    def check_compliance(
        self, 
        merchant_id: str,
        merchant_type: str,
        time_range: TimeRange,
        data: Dict[str, Any],
        documents: List[ComplianceDocument],
        check_types: Optional[List[ComplianceType]] = None
    ) -> ComplianceCheckResult:
        """
        执行合规检查
        
        Args:
            merchant_id: 商户ID
            merchant_type: 商户类型
            time_range: 时间范围
            data: 商户数据
            documents: 文档列表
            check_types: 要检查的类型，为None则检查所有类型
            
        Returns:
            合规检查结果
        """
        self.logger.info(f"Checking compliance for merchant {merchant_id}")
        
        # 确定要检查的类型
        types_to_check = set(check_types) if check_types else set(ComplianceType)
        
        # 筛选适用的规则
        applicable_rules = [
            checker for rule_id, checker in self.rule_checkers.items()
            if checker.rule.type in types_to_check
        ]
        
        # 执行检查
        violations = []
        for checker in applicable_rules:
            try:
                violation = checker.check(data, merchant_type)
                if violation:
                    violations.append(violation)
            except Exception as e:
                self.logger.error(f"检查规则 {checker.rule.rule_id} 时出错: {e}")
        
        # 验证文档状态
        documents_status = self.document_validator.validate_documents(documents)
        
        # 计算各类型的合规状态
        type_status = {}
        for compliance_type in ComplianceType:
            if compliance_type not in types_to_check:
                continue
                
            type_violations = [v for v in violations if v.type == compliance_type]
            
            if not type_violations:
                type_status[compliance_type] = ComplianceStatus.COMPLIANT
            elif any(v.risk_level == RiskLevel.CRITICAL for v in type_violations):
                type_status[compliance_type] = ComplianceStatus.NON_COMPLIANT
            else:
                type_status[compliance_type] = ComplianceStatus.NEEDS_REVIEW
        
        # 确定整体合规状态
        if not violations:
            overall_status = ComplianceStatus.COMPLIANT
        elif any(v.risk_level == RiskLevel.CRITICAL for v in violations):
            overall_status = ComplianceStatus.NON_COMPLIANT
        else:
            overall_status = ComplianceStatus.NEEDS_REVIEW
        
        # 计算风险评分 (0-100, 越高风险越大)
        # 基础分为50分，每个违规根据严重程度加分
        risk_score = 0
        if violations:
            critical_count = sum(1 for v in violations if v.risk_level == RiskLevel.CRITICAL)
            high_count = sum(1 for v in violations if v.risk_level == RiskLevel.HIGH)
            medium_count = sum(1 for v in violations if v.risk_level == RiskLevel.MEDIUM)
            low_count = sum(1 for v in violations if v.risk_level == RiskLevel.LOW)
            
            risk_score = min(100, (
                critical_count * 30 +
                high_count * 15 +
                medium_count * 5 +
                low_count * 1
            ))
        
        # 确定下次检查日期
        next_check_date = datetime.now() + timedelta(days=30)  # 默认30天后再检查
        
        # 创建检查结果
        result = ComplianceCheckResult(
            merchant_id=merchant_id,
            check_id=f"check_{uuid.uuid4().hex[:8]}",
            check_date=datetime.now(),
            time_range=time_range,
            overall_status=overall_status,
            type_status=type_status,
            violations=violations,
            risk_score=risk_score,
            documents_status=documents_status,
            next_check_date=next_check_date
        )
        
        return result 